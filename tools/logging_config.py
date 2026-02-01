"""
Structured logging configuration for procurement tools.

Provides:
- JSON formatter for machine-readable logs
- Configurable handlers (console, file, audit)
- audit_log() function for structured audit entries
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


AUDIT_LOG_PATH = Path(
    os.environ.get("AUDIT_LOG", "logs/audit.jsonl")
)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": (
                datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            entry["exception"] = self.formatException(
                record.exc_info
            )
        for key in ("tool", "params", "duration_ms"):
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        return json.dumps(
            entry, ensure_ascii=False, default=str
        )


def configure_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None,
):
    """Configure structured logging for all procurement tools.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, etc.)
        json_format: If True, use JSON formatter
        log_file: Optional path for file handler
    """
    root = logging.getLogger()
    root.setLevel(
        getattr(logging, level.upper(), logging.INFO)
    )

    # Clear existing handlers
    root.handlers.clear()

    # Console handler
    console = logging.StreamHandler()
    if json_format:
        console.setFormatter(JSONFormatter())
    else:
        console.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(
            parents=True, exist_ok=True
        )
        fh = logging.FileHandler(
            log_file, encoding="utf-8"
        )
        fh.setFormatter(JSONFormatter())
        root.addHandler(fh)


def audit_log(
    tool: str,
    params: dict,
    result: Any,
    duration_ms: float,
    success: bool = True,
):
    """Write a structured audit entry to the audit log file.

    Args:
        tool: Name of the tool invoked
        params: Parameters passed to the tool
        result: Result returned by the tool
        duration_ms: Execution time in milliseconds
        success: Whether the call succeeded
    """
    entry = {
        "timestamp": (
            datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "tool": tool,
        "params": params,
        "success": success,
        "duration_ms": round(duration_ms, 2),
        "result_summary": _summarize(result),
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                entry, ensure_ascii=False, default=str
            )
            + "\n"
        )


def _summarize(result: Any) -> str:
    """Create a brief summary of tool result for audit."""
    if isinstance(result, dict):
        if "success" in result:
            return f"success={result['success']}"
        if "valid" in result:
            return f"valid={result['valid']}"
        return f"keys={list(result.keys())[:5]}"
    return str(result)[:100]
