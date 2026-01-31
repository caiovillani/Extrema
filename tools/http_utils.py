"""
HTTP utilities with retry logic, caching, and credential management.

Provides a shared HTTP client used by all API clients (PNCP, SINAPI,
BPS, CMED, ANP) with:

- Exponential backoff retry (up to 4 attempts)
- In-memory TTL cache to avoid redundant requests
- Credential loading from environment variables or .env files
- Structured error handling
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, urljoin

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

_CREDENTIALS_CACHE: Optional[dict] = None


def load_credentials() -> dict:
    """
    Load API credentials from environment or .env file.

    Searches for keys prefixed with ``PROCUREMENT_`` in env vars.
    Falls back to a ``.env`` file in the project root if present.

    Returns:
        dict mapping credential names to values
    """
    global _CREDENTIALS_CACHE
    if _CREDENTIALS_CACHE is not None:
        return _CREDENTIALS_CACHE

    creds: dict = {}

    # Try loading .env file (simple key=value parser)
    env_path = Path(
        os.environ.get("CLAUDE_PROJECT_DIR", ".")
    ) / ".env"
    if env_path.exists():
        with env_path.open() as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key.startswith("PROCUREMENT_"):
                        creds[key] = value

    # Override with actual environment variables
    for key, value in os.environ.items():
        if key.startswith("PROCUREMENT_"):
            creds[key] = value

    _CREDENTIALS_CACHE = creds
    return creds


def get_credential(name: str, default: str = "") -> str:
    """Return a single credential by name."""
    creds = load_credentials()
    return creds.get(name, os.environ.get(name, default))


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class HTTPError(Exception):
    """Raised when an HTTP request fails after retries."""

    def __init__(
        self, message: str, status: Optional[int] = None,
        url: str = "",
    ):
        self.status = status
        self.url = url
        super().__init__(message)


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


class TTLCache:
    """Simple in-memory cache with per-entry TTL."""

    def __init__(self, default_ttl: int = 900):
        self._store: dict = {}
        self.default_ttl = default_ttl

    def _key(self, url: str, params: Optional[dict]) -> str:
        raw = url + (json.dumps(params, sort_keys=True) if params else "")
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, url: str, params: Optional[dict] = None):
        """Return cached value or None if missing/expired."""
        key = self._key(url, params)
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires = entry
        if time.time() > expires:
            del self._store[key]
            return None
        return value

    def set(
        self, url: str, value, params: Optional[dict] = None,
        ttl: Optional[int] = None,
    ):
        """Store a value with TTL."""
        key = self._key(url, params)
        self._store[key] = (
            value,
            time.time() + (ttl or self.default_ttl),
        )

    def clear(self):
        """Flush all entries."""
        self._store.clear()


# ---------------------------------------------------------------------------
# HTTP Client
# ---------------------------------------------------------------------------

# Retry settings
MAX_RETRIES = 4
INITIAL_BACKOFF = 2  # seconds
BACKOFF_FACTOR = 2

# Status codes that trigger a retry
RETRIABLE_STATUSES = {429, 500, 502, 503, 504}


class CachedHTTPClient:
    """Async HTTP client with retry and caching.

    Uses ``httpx`` when available; falls back to
    ``urllib.request`` in a thread executor.
    """

    def __init__(
        self,
        cache_ttl: int = 900,
        timeout: float = 30.0,
        headers: Optional[dict] = None,
    ):
        self.cache = TTLCache(default_ttl=cache_ttl)
        self.timeout = timeout
        self.default_headers = {
            "Accept": "application/json",
            "User-Agent": "ProcurementAgent/1.0",
        }
        if headers:
            self.default_headers.update(headers)
        self._httpx_client = None

    async def _ensure_httpx(self):
        """Lazily create an httpx.AsyncClient."""
        if self._httpx_client is not None:
            return
        try:
            import httpx
            self._httpx_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.default_headers,
                follow_redirects=True,
            )
        except ImportError:
            self._httpx_client = None

    async def get_json(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        cache_ttl: Optional[int] = None,
        skip_cache: bool = False,
    ) -> dict | list | None:
        """
        GET request returning parsed JSON.

        Checks cache first, retries on transient failures with
        exponential backoff.

        Args:
            url: Full URL
            params: Query parameters
            headers: Extra headers (merged with defaults)
            cache_ttl: Override default cache TTL for this request
            skip_cache: Bypass cache for this request

        Returns:
            Parsed JSON (dict or list) or None on empty body

        Raises:
            HTTPError: After all retries exhausted
        """
        if not skip_cache:
            cached = self.cache.get(url, params)
            if cached is not None:
                return cached

        await self._ensure_httpx()
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                data = await self._do_get(
                    url, params, merged_headers
                )
                self.cache.set(
                    url, data, params=params, ttl=cache_ttl
                )
                return data
            except HTTPError as exc:
                last_exc = exc
                if (
                    exc.status is not None
                    and exc.status not in RETRIABLE_STATUSES
                ):
                    raise
                wait = INITIAL_BACKOFF * (
                    BACKOFF_FACTOR ** attempt
                )
                logger.info(
                    "Retry %d/%d for %s in %.1fs",
                    attempt + 1, MAX_RETRIES, url, wait,
                )
                await asyncio.sleep(wait)
            except Exception as exc:
                last_exc = exc
                wait = INITIAL_BACKOFF * (
                    BACKOFF_FACTOR ** attempt
                )
                logger.info(
                    "Retry %d/%d for %s in %.1fs (%s)",
                    attempt + 1, MAX_RETRIES, url, wait, exc,
                )
                await asyncio.sleep(wait)

        raise HTTPError(
            f"All {MAX_RETRIES} retries exhausted for {url}: "
            f"{last_exc}",
            url=url,
        )

    async def get_bytes(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> bytes:
        """
        GET request returning raw bytes (for file downloads).

        No caching applied. Retries on transient failures.

        Args:
            url: Full URL
            params: Query parameters
            headers: Extra headers

        Returns:
            Response body as bytes

        Raises:
            HTTPError: After all retries exhausted
        """
        await self._ensure_httpx()
        merged_headers = dict(self.default_headers)
        merged_headers.pop("Accept", None)
        if headers:
            merged_headers.update(headers)

        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                return await self._do_get_bytes(
                    url, params, merged_headers
                )
            except Exception as exc:
                last_exc = exc
                wait = INITIAL_BACKOFF * (
                    BACKOFF_FACTOR ** attempt
                )
                logger.info(
                    "Retry bytes %d/%d for %s in %.1fs",
                    attempt + 1, MAX_RETRIES, url, wait,
                )
                await asyncio.sleep(wait)

        raise HTTPError(
            f"All {MAX_RETRIES} retries exhausted for {url}: "
            f"{last_exc}",
            url=url,
        )

    # ---- internal transport methods ----

    async def _do_get(
        self, url: str, params: Optional[dict],
        headers: dict,
    ) -> dict | list | None:
        """Execute a single GET and return parsed JSON."""
        if self._httpx_client is not None:
            return await self._do_get_httpx(
                url, params, headers
            )
        return await self._do_get_urllib(
            url, params, headers
        )

    async def _do_get_httpx(
        self, url: str, params: Optional[dict],
        headers: dict,
    ):
        import httpx

        resp = await self._httpx_client.get(
            url, params=params, headers=headers
        )
        if resp.status_code >= 400:
            raise HTTPError(
                f"HTTP {resp.status_code}: {resp.text[:200]}",
                status=resp.status_code,
                url=url,
            )
        if not resp.content:
            return None
        return resp.json()

    async def _do_get_urllib(
        self, url: str, params: Optional[dict],
        headers: dict,
    ):
        """Fallback using urllib in a thread executor."""
        import urllib.request
        import urllib.error

        full_url = url
        if params:
            full_url = f"{url}?{urlencode(params)}"

        req = urllib.request.Request(
            full_url, headers=headers
        )

        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=self.timeout),
            )
            body = resp.read()
            if not body:
                return None
            return json.loads(body)
        except urllib.error.HTTPError as exc:
            raise HTTPError(
                f"HTTP {exc.code}: {exc.reason}",
                status=exc.code,
                url=url,
            ) from exc
        except urllib.error.URLError as exc:
            raise HTTPError(
                f"URL error: {exc.reason}", url=url
            ) from exc

    async def _do_get_bytes(
        self, url: str, params: Optional[dict],
        headers: dict,
    ) -> bytes:
        """Download raw bytes."""
        if self._httpx_client is not None:
            import httpx

            resp = await self._httpx_client.get(
                url, params=params, headers=headers
            )
            if resp.status_code >= 400:
                raise HTTPError(
                    f"HTTP {resp.status_code}",
                    status=resp.status_code,
                    url=url,
                )
            return resp.content

        import urllib.request
        import urllib.error

        full_url = url
        if params:
            full_url = f"{url}?{urlencode(params)}"

        req = urllib.request.Request(
            full_url, headers=headers
        )
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=self.timeout),
            )
            return resp.read()
        except urllib.error.HTTPError as exc:
            raise HTTPError(
                f"HTTP {exc.code}", status=exc.code, url=url
            ) from exc

    async def close(self):
        """Close the underlying HTTP client."""
        if self._httpx_client is not None:
            await self._httpx_client.aclose()
            self._httpx_client = None
