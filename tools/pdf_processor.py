"""
Core PDF processing module for document extraction and transcription.

Provides multi-strategy text extraction, table detection, and
markdown conversion for long-format PDF documents.

Strategies (in order of preference):
1. PyMuPDF (fitz) -- fast native text extraction
2. pdfplumber -- table-aware extraction with layout analysis
3. pytesseract -- OCR fallback for scanned/image pages

Usage:
    from tools.pdf_processor import PDFProcessor
    processor = PDFProcessor()
    result = processor.extract_text("docs/manual.pdf")
"""

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import pymupdf

logger = logging.getLogger(__name__)

DOCS_DIR = Path(
    os.environ.get("DOCS_DIR", "docs")
)
TRANSCRIPTIONS_DIR = Path(
    os.environ.get("TRANSCRIPTIONS_DIR", "data/transcriptions")
)


@dataclass
class PageContent:
    """Extracted content from a single PDF page."""

    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)
    has_images: bool = False
    extraction_method: str = "pymupdf"


@dataclass
class PDFMetadata:
    """Metadata extracted from a PDF file."""

    filename: str
    filepath: str
    num_pages: int
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    creation_date: str = ""
    file_hash: str = ""
    file_size_bytes: int = 0


@dataclass
class ExtractionResult:
    """Complete result of PDF extraction."""

    metadata: PDFMetadata
    pages: list[PageContent]
    extraction_time_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenate all page texts."""
        parts = []
        for page in self.pages:
            parts.append(
                f"--- Pagina {page.page_number} ---\n"
                f"{page.text}"
            )
        return "\n\n".join(parts)

    @property
    def total_tables(self) -> int:
        return sum(len(p.tables) for p in self.pages)

    @property
    def total_chars(self) -> int:
        return sum(len(p.text) for p in self.pages)


class PDFProcessor:
    """Multi-strategy PDF text extractor and transcriber.

    Uses PyMuPDF as the primary extraction engine with pdfplumber
    as a secondary strategy for table extraction and OCR as a
    fallback for scanned pages.
    """

    MIN_TEXT_THRESHOLD = 50

    def __init__(
        self,
        docs_dir: Optional[Path] = None,
        transcriptions_dir: Optional[Path] = None,
        ocr_enabled: bool = True,
        ocr_language: str = "por",
    ):
        self.docs_dir = docs_dir or DOCS_DIR
        self.transcriptions_dir = (
            transcriptions_dir or TRANSCRIPTIONS_DIR
        )
        self.ocr_enabled = ocr_enabled
        self.ocr_language = ocr_language

        self.transcriptions_dir.mkdir(
            parents=True, exist_ok=True
        )

        self._ocr_available = False
        if ocr_enabled:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._ocr_available = True
            except Exception:
                logger.info(
                    "Tesseract OCR not available. "
                    "Scanned pages will have limited extraction."
                )

    def _file_hash(self, filepath: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with filepath.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]

    def _resolve_path(self, filepath: str) -> Path:
        """Resolve a filepath within docs_dir only.

        Rejects absolute paths and traversals that escape the
        docs directory to prevent unauthorized file access.
        """
        docs_root = self.docs_dir.resolve()
        candidate = (docs_root / filepath).resolve()
        if not candidate.is_relative_to(docs_root):
            raise ValueError(
                f"Path escapes docs directory: {filepath}"
            )
        if not candidate.exists():
            raise FileNotFoundError(
                f"PDF not found: {filepath} "
                f"(looked in {docs_root})"
            )
        return candidate

    def list_pdfs(self) -> list[dict]:
        """List all PDF files in the docs directory."""
        pdfs = []
        for ext in ("*.pdf", "*.PDF"):
            for p in sorted(self.docs_dir.glob(ext)):
                pdfs.append({
                    "filename": p.name,
                    "filepath": str(p),
                    "size_bytes": p.stat().st_size,
                    "size_mb": round(
                        p.stat().st_size / (1024 * 1024), 2
                    ),
                })
        return pdfs

    def get_metadata(self, filepath: str) -> PDFMetadata:
        """Extract metadata from a PDF without full text extraction."""
        path = self._resolve_path(filepath)
        doc = pymupdf.open(str(path))
        meta = doc.metadata or {}
        result = PDFMetadata(
            filename=path.name,
            filepath=str(path),
            num_pages=len(doc),
            title=meta.get("title", "") or "",
            author=meta.get("author", "") or "",
            subject=meta.get("subject", "") or "",
            creator=meta.get("creator", "") or "",
            creation_date=meta.get("creationDate", "") or "",
            file_hash=self._file_hash(path),
            file_size_bytes=path.stat().st_size,
        )
        doc.close()
        return result

    def extract_text(
        self,
        filepath: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        extract_tables: bool = True,
        use_cache: bool = True,
    ) -> ExtractionResult:
        """Extract text and tables from a PDF file.

        Args:
            filepath: Path to PDF file (absolute or relative)
            page_start: First page to extract (1-indexed, inclusive)
            page_end: Last page to extract (1-indexed, inclusive)
            extract_tables: Whether to also extract tables
            use_cache: Whether to use/update transcription cache

        Returns:
            ExtractionResult with metadata, pages, and timing
        """
        start_time = time.time()
        path = self._resolve_path(filepath)
        file_hash = self._file_hash(path)

        if use_cache:
            cached = self._load_cache(path, file_hash)
            if cached is not None:
                if page_start or page_end:
                    cached = self._filter_pages(
                        cached, page_start, page_end
                    )
                cached.extraction_time_ms = (
                    (time.time() - start_time) * 1000
                )
                return cached

        logger.info(
            "Extracting PDF: %s (%s)",
            path.name,
            file_hash,
        )

        doc = pymupdf.open(str(path))
        metadata = PDFMetadata(
            filename=path.name,
            filepath=str(path),
            num_pages=len(doc),
            title=(doc.metadata or {}).get("title", "") or "",
            author=(doc.metadata or {}).get("author", "") or "",
            subject=(
                (doc.metadata or {}).get("subject", "") or ""
            ),
            creator=(
                (doc.metadata or {}).get("creator", "") or ""
            ),
            creation_date=(
                (doc.metadata or {}).get("creationDate", "")
                or ""
            ),
            file_hash=file_hash,
            file_size_bytes=path.stat().st_size,
        )

        pages = []
        warnings = []

        start_idx = (page_start - 1) if page_start else 0
        end_idx = page_end if page_end else len(doc)
        end_idx = min(end_idx, len(doc))

        for i in range(start_idx, end_idx):
            page = doc[i]
            page_num = i + 1

            text = page.get_text("text")
            method = "pymupdf"
            has_images = len(page.get_images()) > 0

            if (
                len(text.strip()) < self.MIN_TEXT_THRESHOLD
                and has_images
            ):
                ocr_text = self._try_ocr(page, path, page_num)
                if ocr_text:
                    text = ocr_text
                    method = "ocr_tesseract"
                else:
                    warnings.append(
                        f"Pagina {page_num}: pouco texto extraido "
                        f"({len(text.strip())} chars), "
                        f"pagina pode ser imagem/escaneada"
                    )

            text = self._clean_text(text)

            tables = []
            if extract_tables:
                tables = self._extract_tables_pdfplumber(
                    path, i
                )

            pages.append(PageContent(
                page_number=page_num,
                text=text,
                tables=tables,
                has_images=has_images,
                extraction_method=method,
            ))

        doc.close()

        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            extraction_time_ms=(time.time() - start_time) * 1000,
            warnings=warnings,
        )

        if use_cache and not page_start and not page_end:
            self._save_cache(path, file_hash, result)

        logger.info(
            "Extracted %d pages, %d chars, %d tables in %.0fms",
            len(pages),
            result.total_chars,
            result.total_tables,
            result.extraction_time_ms,
        )

        return result

    def extract_to_markdown(
        self,
        filepath: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> str:
        """Extract PDF content and format as markdown.

        Args:
            filepath: Path to PDF file
            page_start: First page (1-indexed)
            page_end: Last page (1-indexed)

        Returns:
            Markdown-formatted string of the PDF content
        """
        result = self.extract_text(
            filepath,
            page_start=page_start,
            page_end=page_end,
            extract_tables=True,
        )

        lines = []
        lines.append(f"# {result.metadata.filename}\n")

        meta = result.metadata
        if meta.title:
            lines.append(f"**Titulo:** {meta.title}  ")
        if meta.author:
            lines.append(f"**Autor:** {meta.author}  ")
        lines.append(f"**Paginas:** {meta.num_pages}  ")
        lines.append(f"**Hash:** {meta.file_hash}  ")
        lines.append("")

        for page in result.pages:
            lines.append(
                f"## Pagina {page.page_number}\n"
            )
            lines.append(page.text)

            if page.tables:
                for idx, table in enumerate(page.tables, 1):
                    lines.append(
                        f"\n### Tabela {idx} "
                        f"(Pagina {page.page_number})\n"
                    )
                    lines.append(
                        self._table_to_markdown(table)
                    )

            lines.append("")

        if result.warnings:
            lines.append("## Avisos de Extracao\n")
            for w in result.warnings:
                lines.append(f"- {w}")

        return "\n".join(lines)

    def search_content(
        self,
        query: str,
        filepath: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> list[dict]:
        """Search for text across one or all PDFs.

        Args:
            query: Text to search for
            filepath: Specific PDF to search (or all if None)
            case_sensitive: Whether to match case

        Returns:
            List of matches with file, page, and context
        """
        matches = []
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(query), flags)

        if filepath:
            files = [self._resolve_path(filepath)]
        else:
            files = []
            for ext in ("*.pdf", "*.PDF"):
                files.extend(self.docs_dir.glob(ext))

        for pdf_path in sorted(files):
            try:
                result = self.extract_text(
                    str(pdf_path),
                    extract_tables=False,
                    use_cache=True,
                )
            except Exception as e:
                logger.warning(
                    "Skipping %s: %s", pdf_path.name, e
                )
                continue

            for page in result.pages:
                for m in pattern.finditer(page.text):
                    start = max(0, m.start() - 100)
                    end = min(len(page.text), m.end() + 100)
                    context = page.text[start:end].strip()

                    matches.append({
                        "filename": pdf_path.name,
                        "page": page.page_number,
                        "match": m.group(),
                        "context": f"...{context}...",
                    })

        return matches

    def _try_ocr(
        self,
        page,
        filepath: Path,
        page_num: int,
    ) -> Optional[str]:
        """Attempt OCR on a page with low text content."""
        if not self._ocr_available:
            return None

        try:
            import pytesseract
            from PIL import Image
            import io

            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            text = pytesseract.image_to_string(
                img, lang=self.ocr_language
            )

            if len(text.strip()) > self.MIN_TEXT_THRESHOLD:
                logger.info(
                    "OCR successful for page %d of %s",
                    page_num,
                    filepath.name,
                )
                return text

        except Exception as e:
            logger.warning(
                "OCR failed for page %d of %s: %s",
                page_num,
                filepath.name,
                e,
            )

        return None

    def _extract_tables_pdfplumber(
        self,
        filepath: Path,
        page_index: int,
    ) -> list[list[list[str]]]:
        """Extract tables from a specific page using pdfplumber."""
        try:
            import pdfplumber

            with pdfplumber.open(str(filepath)) as pdf:
                if page_index >= len(pdf.pages):
                    return []

                page = pdf.pages[page_index]
                raw_tables = page.extract_tables()

                tables = []
                for table in raw_tables:
                    cleaned = []
                    for row in table:
                        cleaned.append([
                            (cell or "").strip()
                            for cell in row
                        ])
                    if any(
                        any(cell for cell in row)
                        for row in cleaned
                    ):
                        tables.append(cleaned)
                return tables

        except Exception as e:
            logger.debug(
                "Table extraction failed for page %d of %s: %s",
                page_index + 1,
                filepath.name,
                e,
            )
            return []

    def _clean_text(self, text: str) -> str:
        """Clean extracted text: normalize whitespace, fix encoding."""
        text = text.replace("\x00", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        return text

    @staticmethod
    def _table_to_markdown(
        table: list[list[str]],
    ) -> str:
        """Convert a table (list of rows) to markdown format."""
        if not table:
            return ""

        lines = []
        header = table[0]
        lines.append(
            "| " + " | ".join(header) + " |"
        )
        lines.append(
            "| " + " | ".join("---" for _ in header) + " |"
        )
        for row in table[1:]:
            while len(row) < len(header):
                row.append("")
            lines.append(
                "| " + " | ".join(row[:len(header)]) + " |"
            )
        return "\n".join(lines)

    def _cache_path(
        self, filepath: Path, file_hash: str
    ) -> Path:
        """Get cache file path for a given PDF."""
        stem = filepath.stem
        safe_name = re.sub(r"[^\w\-]", "_", stem)
        return (
            self.transcriptions_dir
            / f"{safe_name}_{file_hash}.json"
        )

    def _load_cache(
        self, filepath: Path, file_hash: str
    ) -> Optional[ExtractionResult]:
        """Load cached extraction result if available."""
        cache_file = self._cache_path(filepath, file_hash)
        if not cache_file.exists():
            return None

        try:
            with cache_file.open(encoding="utf-8") as f:
                data = json.load(f)

            metadata = PDFMetadata(**data["metadata"])
            pages = [
                PageContent(**p) for p in data["pages"]
            ]
            return ExtractionResult(
                metadata=metadata,
                pages=pages,
                warnings=data.get("warnings", []),
            )
        except Exception as e:
            logger.warning(
                "Cache load failed for %s: %s",
                filepath.name,
                e,
            )
            return None

    def _save_cache(
        self,
        filepath: Path,
        file_hash: str,
        result: ExtractionResult,
    ):
        """Save extraction result to cache."""
        cache_file = self._cache_path(filepath, file_hash)
        try:
            data = {
                "metadata": asdict(result.metadata),
                "pages": [asdict(p) for p in result.pages],
                "warnings": result.warnings,
            }
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(
                    data, f, ensure_ascii=False, indent=2
                )
            logger.info(
                "Cached transcription: %s", cache_file.name
            )
        except Exception as e:
            logger.warning(
                "Cache save failed for %s: %s",
                filepath.name,
                e,
            )

    def _filter_pages(
        self,
        result: ExtractionResult,
        page_start: Optional[int],
        page_end: Optional[int],
    ) -> ExtractionResult:
        """Filter an ExtractionResult to a page range."""
        start = (page_start or 1) - 1
        end = page_end or len(result.pages)
        return ExtractionResult(
            metadata=result.metadata,
            pages=result.pages[start:end],
            warnings=result.warnings,
        )
