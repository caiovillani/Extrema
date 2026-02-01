"""
Hook de verificacao de citacoes.
Executado apos salvar documentos para garantir rastreabilidade.
"""

import json
import os
import re
import sys
from pathlib import Path


def load_valid_sources(sources_log: str, price_log: str) -> set:
    """Load all valid source IDs from both log files."""
    valid = set()
    for log_path in [sources_log, price_log]:
        path = Path(log_path)
        if not path.exists():
            continue
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    source = json.loads(line)
                    if source.get("status") == "vigente":
                        valid.add(source["id"])
    return valid


def check_citations(content: str, valid_sources: set) -> dict:
    """Verify all citations in a document are valid."""
    # Find all citations in the format [Fonte: ID | ...]
    pattern = r"\[Fonte:\s*(\S+)\s*\|"
    citations = re.findall(pattern, content)

    invalid = []
    for citation_id in citations:
        if citation_id not in valid_sources:
            invalid.append(citation_id)

    # Check for normative statements without citations
    normative_patterns = [
        r"conforme\s+(?:o\s+)?(?:art\.?|artigo)",
        r"nos\s+termos\s+d[ao]",
        r"de\s+acordo\s+com\s+a\s+Lei",
        r"previsto\s+n[ao]",
    ]

    uncited = []
    for norm_pattern in normative_patterns:
        matches = re.finditer(norm_pattern, content, re.IGNORECASE)
        for match in matches:
            context = content[match.start():match.start() + 200]
            if "[Fonte:" not in context:
                line_num = content[:match.start()].count("\n") + 1
                uncited.append(
                    f"Linha ~{line_num}: '{match.group()}...'"
                )

    return {
        "valid": len(invalid) == 0 and len(uncited) == 0,
        "total_citations": len(citations),
        "invalid_citations": invalid,
        "uncited_statements": uncited,
    }


def _run_check(content: str, file_path_str: str):
    """Run citation check and print results."""
    # Only check markdown files
    if not file_path_str.endswith((".md", ".markdown")):
        sys.exit(0)

    sources_log = os.environ.get(
        "SOURCES_LOG", "sources/sources_log.jsonl"
    )
    price_log = os.environ.get(
        "PRICE_SOURCES_LOG", "sources/price_sources_log.jsonl"
    )

    valid_sources = load_valid_sources(sources_log, price_log)
    result = check_citations(content, valid_sources)

    if not result["valid"]:
        print("VERIFICACAO DE CITACOES:")
        if result["invalid_citations"]:
            print(
                f"  Citacoes invalidas: {result['invalid_citations']}"
            )
        if result["uncited_statements"]:
            print("  Afirmacoes normativas sem citacao:")
            for stmt in result["uncited_statements"][:5]:
                print(f"    {stmt}")
            if len(result["uncited_statements"]) > 5:
                remaining = len(result["uncited_statements"]) - 5
                print(f"    ... e mais {remaining}")
    else:
        print(
            f"Citacoes verificadas: {result['total_citations']} "
            f"citacao(oes) valida(s)"
        )

    # Citation check is advisory, does not block
    sys.exit(0)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Verifica citacoes em documentos"
    )
    parser.add_argument(
        "--file",
        required=False,
        help="Caminho do arquivo a verificar",
    )
    parser.add_argument(
        "--stdin-check",
        action="store_true",
        help="Read Claude Code hook JSON from stdin",
    )
    args = parser.parse_args()

    if args.stdin_check:
        # Claude Code hook mode: read JSON with tool_input
        raw = sys.stdin.read().strip()
        if not raw:
            sys.exit(0)
        try:
            hook_data = json.loads(raw)
        except json.JSONDecodeError:
            sys.exit(0)

        tool_input = hook_data.get("tool_input", {})
        file_path_str = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        if not file_path_str or not content:
            sys.exit(0)

        _run_check(content, file_path_str)
    else:
        # Legacy CLI mode
        if not args.file:
            print("--file is required in CLI mode")
            sys.exit(1)

        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Arquivo nao encontrado: {args.file}")
            sys.exit(1)

        content = file_path.read_text(encoding="utf-8")
        _run_check(content, str(file_path))


if __name__ == "__main__":
    main()
