"""
Validates price sources against the sources log.
Checks that all referenced sources exist, are current, and meet
minimum requirements for procurement price research.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_sources(log_path: str) -> dict:
    """Load sources from a JSONL log file into a dict keyed by id."""
    sources = {}
    path = Path(log_path)
    if not path.exists():
        return sources
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                source = json.loads(line)
                sources[source["id"]] = source
    return sources


def validate_source_status(source: dict) -> list:
    """Check that a source is active and recently verified."""
    warnings = []

    if source.get("status") != "vigente":
        warnings.append(
            f"Fonte {source['id']} nao esta vigente. "
            f"Status: {source.get('status')}"
        )

    verificado = source.get("verificado_em")
    if verificado:
        ver_date = datetime.fromisoformat(verificado)
        age = datetime.now() - ver_date
        if age > timedelta(days=180):
            warnings.append(
                f"Fonte {source['id']} verificada ha mais de 6 meses "
                f"({verificado}). Recomenda-se re-verificacao."
            )
    else:
        warnings.append(
            f"Fonte {source['id']} sem data de verificacao registrada."
        )

    return warnings


def validate_minimum_sources(source_ids: list, sources: dict) -> list:
    """Check that at least 3 valid sources are available."""
    errors = []
    valid = [
        sid for sid in source_ids
        if sid in sources and sources[sid].get("status") == "vigente"
    ]
    if len(valid) < 3:
        errors.append(
            f"Apenas {len(valid)} fontes vigentes encontradas "
            f"(minimo recomendado: 3). Fontes: {valid}"
        )
    return errors


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate price research sources"
    )
    parser.add_argument(
        "--sources-log",
        default="sources/price_sources_log.jsonl",
        help="Path to the price sources log",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        help="Source IDs to validate (validates all if omitted)",
    )
    args = parser.parse_args()

    sources = load_sources(args.sources_log)

    if not sources:
        print("ERRO: Nenhuma fonte encontrada no log.")
        sys.exit(1)

    ids_to_check = args.ids if args.ids else list(sources.keys())
    all_warnings = []
    all_errors = []

    for sid in ids_to_check:
        if sid not in sources:
            all_errors.append(f"Fonte {sid} nao encontrada no log.")
            continue
        warnings = validate_source_status(sources[sid])
        all_warnings.extend(warnings)

    min_errors = validate_minimum_sources(ids_to_check, sources)
    all_errors.extend(min_errors)

    if all_errors:
        print("ERROS:")
        for e in all_errors:
            print(f"  {e}")

    if all_warnings:
        print("AVISOS:")
        for w in all_warnings:
            print(f"  {w}")

    if not all_errors and not all_warnings:
        print("Todas as fontes validadas com sucesso.")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
