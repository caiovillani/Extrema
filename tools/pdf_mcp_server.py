"""
MCP Server for PDF extraction and transcription.

Exposes tools for extracting text, tables, and metadata from
PDF documents in the docs/ directory.

Usage:
    python -m tools.pdf_mcp_server
"""

import json
import logging
import time
from typing import Optional

from mcp.server.fastmcp import FastMCP

from tools.pdf_processor import PDFProcessor
from tools.logging_config import audit_log

logger = logging.getLogger(__name__)


def create_pdf_mcp_server() -> FastMCP:
    """Create and configure the PDF processing MCP server."""

    server = FastMCP("pdf-tools")

    processor = PDFProcessor()

    @server.tool()
    async def list_pdfs() -> dict:
        """Lista todos os PDFs disponiveis no diretorio docs/.

        Returns:
            Lista de PDFs com nome, caminho e tamanho.
        """
        start = time.time()
        pdfs = processor.list_pdfs()
        result = {
            "success": True,
            "total": len(pdfs),
            "pdfs": pdfs,
        }
        audit_log(
            "list_pdfs",
            {},
            result,
            (time.time() - start) * 1000,
        )
        return result

    @server.tool()
    async def get_pdf_metadata(filepath: str) -> dict:
        """Extrai metadados de um PDF sem processar o conteudo.

        Args:
            filepath: Caminho para o arquivo PDF
                (absoluto ou relativo ao docs/)

        Returns:
            Metadados: titulo, autor, paginas, hash, tamanho.
        """
        start = time.time()
        try:
            from dataclasses import asdict
            meta = processor.get_metadata(filepath)
            result = {
                "success": True,
                "metadata": asdict(meta),
            }
        except FileNotFoundError as e:
            result = {
                "success": False,
                "error": str(e),
            }
        audit_log(
            "get_pdf_metadata",
            {"filepath": filepath},
            result,
            (time.time() - start) * 1000,
        )
        return result

    @server.tool()
    async def extract_pdf_text(
        filepath: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> dict:
        """Extrai texto completo de um PDF.

        Usa PyMuPDF como motor principal com fallback OCR
        para paginas escaneadas. Resultados sao cacheados
        para consultas futuras.

        Args:
            filepath: Caminho para o PDF
                (absoluto ou relativo ao docs/)
            page_start: Pagina inicial (1-indexado, inclusive)
            page_end: Pagina final (1-indexado, inclusive)

        Returns:
            Texto extraido com metadados e estatisticas.
        """
        start = time.time()
        try:
            result_data = processor.extract_text(
                filepath,
                page_start=page_start,
                page_end=page_end,
                extract_tables=False,
            )
            pages_out = []
            for p in result_data.pages:
                pages_out.append({
                    "page_number": p.page_number,
                    "text": p.text,
                    "extraction_method": p.extraction_method,
                    "has_images": p.has_images,
                    "char_count": len(p.text),
                })
            result = {
                "success": True,
                "filename": result_data.metadata.filename,
                "num_pages": result_data.metadata.num_pages,
                "pages_extracted": len(pages_out),
                "total_chars": result_data.total_chars,
                "extraction_time_ms": round(
                    result_data.extraction_time_ms, 1
                ),
                "pages": pages_out,
                "warnings": result_data.warnings,
            }
        except FileNotFoundError as e:
            result = {
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.exception("PDF extraction failed")
            result = {
                "success": False,
                "error": f"Extraction failed: {e}",
            }
        audit_log(
            "extract_pdf_text",
            {
                "filepath": filepath,
                "page_start": page_start,
                "page_end": page_end,
            },
            result,
            (time.time() - start) * 1000,
        )
        return result

    @server.tool()
    async def extract_pdf_tables(
        filepath: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> dict:
        """Extrai tabelas estruturadas de um PDF usando pdfplumber.

        Ideal para tabelas de precos SINAPI, orcamentos,
        e dados tabulares em documentos oficiais.

        Args:
            filepath: Caminho para o PDF
            page_start: Pagina inicial (1-indexado)
            page_end: Pagina final (1-indexado)

        Returns:
            Tabelas extraidas organizadas por pagina.
        """
        start = time.time()
        try:
            result_data = processor.extract_text(
                filepath,
                page_start=page_start,
                page_end=page_end,
                extract_tables=True,
            )
            tables_out = []
            for p in result_data.pages:
                if p.tables:
                    for idx, table in enumerate(p.tables):
                        tables_out.append({
                            "page": p.page_number,
                            "table_index": idx + 1,
                            "rows": len(table),
                            "cols": (
                                len(table[0]) if table else 0
                            ),
                            "data": table,
                        })
            result = {
                "success": True,
                "filename": result_data.metadata.filename,
                "total_tables": len(tables_out),
                "tables": tables_out,
            }
        except FileNotFoundError as e:
            result = {
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.exception("Table extraction failed")
            result = {
                "success": False,
                "error": f"Table extraction failed: {e}",
            }
        audit_log(
            "extract_pdf_tables",
            {
                "filepath": filepath,
                "page_start": page_start,
                "page_end": page_end,
            },
            result,
            (time.time() - start) * 1000,
        )
        return result

    @server.tool()
    async def convert_pdf_to_markdown(
        filepath: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> dict:
        """Converte um PDF para formato Markdown estruturado.

        Inclui texto, tabelas formatadas, e metadados.
        Ideal para criar versoes legiveis de documentos
        oficiais e manuais tecnicos.

        Args:
            filepath: Caminho para o PDF
            page_start: Pagina inicial (1-indexado)
            page_end: Pagina final (1-indexado)

        Returns:
            Conteudo em Markdown com metadados.
        """
        start = time.time()
        try:
            markdown = processor.extract_to_markdown(
                filepath,
                page_start=page_start,
                page_end=page_end,
            )
            result = {
                "success": True,
                "markdown": markdown,
                "char_count": len(markdown),
            }
        except FileNotFoundError as e:
            result = {
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.exception("Markdown conversion failed")
            result = {
                "success": False,
                "error": f"Conversion failed: {e}",
            }
        audit_log(
            "convert_pdf_to_markdown",
            {
                "filepath": filepath,
                "page_start": page_start,
                "page_end": page_end,
            },
            result,
            (time.time() - start) * 1000,
        )
        return result

    @server.tool()
    async def search_pdf_content(
        query: str,
        filepath: Optional[str] = None,
        case_sensitive: bool = False,
    ) -> dict:
        """Busca texto em um ou todos os PDFs do diretorio.

        Busca o termo em todos os PDFs ou em um arquivo
        especifico, retornando trechos com contexto.

        Args:
            query: Texto a buscar
            filepath: PDF especifico (ou todos se None)
            case_sensitive: Diferenciar maiusculas/minusculas

        Returns:
            Lista de ocorrencias com arquivo, pagina e contexto.
        """
        start = time.time()
        try:
            matches = processor.search_content(
                query,
                filepath=filepath,
                case_sensitive=case_sensitive,
            )
            result = {
                "success": True,
                "query": query,
                "total_matches": len(matches),
                "matches": matches[:50],
            }
            if len(matches) > 50:
                result["truncated"] = True
                result["total_available"] = len(matches)
        except Exception as e:
            logger.exception("Search failed")
            result = {
                "success": False,
                "error": f"Search failed: {e}",
            }
        audit_log(
            "search_pdf_content",
            {
                "query": query,
                "filepath": filepath,
            },
            result,
            (time.time() - start) * 1000,
        )
        return result

    return server


def main():
    """Start the PDF MCP server via stdio."""
    from tools.logging_config import configure_logging
    configure_logging(
        log_file="logs/pdf_mcp_server.jsonl",
    )
    server = create_pdf_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
