"""
Hook de validacao para documentos tecnicos.
Executado antes de salvar ETPs, TRs e Pareceres.
"""

import argparse
import re
import sys
from pathlib import Path


def validate_etp(content: str) -> dict:
    """Valida estrutura e conteudo de um ETP."""
    errors = []
    warnings = []

    required_sections = [
        ("Descricao da Necessidade", r"##?\s*\d*\.?\s*Descri"),
        ("Requisitos da Contratacao", r"##?\s*\d*\.?\s*Requisitos"),
        ("Estimativa de Quantidades", r"##?\s*\d*\.?\s*Estimativa.*Quant"),
        ("Estimativa de Valor", r"##?\s*\d*\.?\s*Estimativa.*Valor"),
        ("Justificativa da Solucao", r"##?\s*\d*\.?\s*Justificativa"),
    ]

    for section_name, pattern in required_sections:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Secao obrigatoria ausente: {section_name}")

    citations = re.findall(r"\[Fonte:\s*[^\]]+\]", content)
    if not citations:
        warnings.append("Nenhuma citacao de fonte encontrada no documento")

    money_pattern = r"R\$\s*[\d.,]+"
    money_values = re.findall(money_pattern, content)
    if not money_values:
        warnings.append(
            "Nenhum valor monetario encontrado - verificar estimativa"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "citations_count": len(citations),
        "money_values_count": len(money_values),
    }


def validate_tr(content: str) -> dict:
    """Valida estrutura e conteudo de um TR."""
    errors = []
    warnings = []

    required_sections = [
        ("Objeto", r"##?\s*\d*\.?\s*Objeto"),
        ("Fundamentacao Legal", r"##?\s*\d*\.?\s*Fundamenta"),
        ("Descricao da Solucao", r"##?\s*\d*\.?\s*Descri.*Solu"),
        ("Requisitos Tecnicos", r"##?\s*\d*\.?\s*Requisitos"),
        ("Modelo de Execucao", r"##?\s*\d*\.?\s*Modelo.*Execu"),
        ("Estimativa de Precos", r"##?\s*\d*\.?\s*Estimativa.*Pre"),
    ]

    for section_name, pattern in required_sections:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Secao obrigatoria ausente: {section_name}")

    citations = re.findall(r"\[Fonte:\s*[^\]]+\]", content)
    if not citations:
        warnings.append("Nenhuma citacao de fonte encontrada")

    if "14.133" not in content and "14133" not in content:
        warnings.append("Nao ha referencia explicita a Lei 14.133/2021")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "citations_count": len(citations),
    }


def validate_parecer(content: str) -> dict:
    """Valida estrutura e conteudo de um Parecer."""
    errors = []
    warnings = []

    required_sections = [
        ("Identificacao", r"##?\s*\d*\.?\s*Identifica"),
        ("Questao Analisada", r"##?\s*\d*\.?\s*Quest"),
        ("Fundamentacao", r"##?\s*\d*\.?\s*Fundamenta"),
        ("Conclusao", r"##?\s*\d*\.?\s*Conclus"),
    ]

    for section_name, pattern in required_sections:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Secao obrigatoria ausente: {section_name}")

    citations = re.findall(r"\[Fonte:\s*[^\]]+\]", content)
    if not citations:
        warnings.append("Nenhuma citacao de fonte encontrada")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "citations_count": len(citations),
    }


def _detect_doc_type(file_path: str) -> str:
    """Detect document type from file path."""
    fp = file_path.lower()
    if ".etp." in fp or "/etp" in fp:
        return "etp"
    elif ".tr." in fp or "/tr" in fp:
        return "tr"
    elif ".parecer." in fp or "/parecer" in fp:
        return "parecer"
    return ""


def _run_validation(doc_type: str, content: str):
    """Run validation and print results. Exits with appropriate code."""
    validators = {
        "etp": validate_etp,
        "tr": validate_tr,
        "parecer": validate_parecer,
    }

    if doc_type not in validators:
        # Not a document we validate -- pass through
        sys.exit(0)

    result = validators[doc_type](content)

    if result["errors"]:
        print("VALIDACAO FALHOU")
        for error in result["errors"]:
            print(f"  ERRO: {error}")

    if result.get("warnings"):
        print("AVISOS:")
        for warning in result["warnings"]:
            print(f"  AVISO: {warning}")

    if result["valid"]:
        print("Documento valido para salvamento")
        sys.exit(0)
    else:
        sys.exit(1)


def main():
    import json as _json

    parser = argparse.ArgumentParser(
        description="Valida documentos tecnicos"
    )
    parser.add_argument(
        "--type",
        required=False,
        choices=["etp", "tr", "parecer"],
    )
    parser.add_argument(
        "--file",
        required=False,
        help="Caminho do arquivo a validar",
    )
    parser.add_argument(
        "--stdin-check",
        action="store_true",
        help="Read Claude Code hook JSON from stdin",
    )
    args = parser.parse_args()

    if args.stdin_check:
        # Claude Code hook mode: read JSON with tool_input from stdin
        raw = sys.stdin.read().strip()
        if not raw:
            sys.exit(0)
        try:
            hook_data = _json.loads(raw)
        except _json.JSONDecodeError:
            sys.exit(0)

        tool_input = hook_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        if not file_path or not content:
            sys.exit(0)

        # Only validate output documents
        if "output/" not in file_path:
            sys.exit(0)

        doc_type = _detect_doc_type(file_path)
        if not doc_type:
            sys.exit(0)

        _run_validation(doc_type, content)
    else:
        # Legacy CLI mode
        if not args.type:
            print("--type is required in CLI mode")
            sys.exit(1)

        if args.file:
            content = Path(args.file).read_text(encoding="utf-8")
        else:
            content = sys.stdin.read()

        _run_validation(args.type, content)


if __name__ == "__main__":
    main()
