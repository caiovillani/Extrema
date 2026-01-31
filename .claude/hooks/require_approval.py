"""
Hook para exigir aprovacao humana antes de acoes criticas.
Usado como checkpoint obrigatorio no fluxo Human on the Loop.
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Solicita aprovacao humana para acao critica"
    )
    parser.add_argument(
        "--action",
        required=True,
        help="Descricao da acao que requer aprovacao",
    )
    parser.add_argument(
        "--level",
        choices=["info", "warning", "critical"],
        default="warning",
        help="Nivel de criticidade da acao",
    )
    args = parser.parse_args()

    labels = {
        "info": "INFORMACAO",
        "warning": "ATENCAO",
        "critical": "CRITICO",
    }

    label = labels[args.level]
    print(f"[{label}] Aprovacao requerida: {args.action}")
    print("O sistema aguarda validacao humana antes de prosseguir.")
    print("---")

    if args.level == "critical":
        print(
            "Esta acao tem impacto significativo e nao pode ser "
            "desfeita facilmente."
        )
        print(
            "Recomenda-se revisao cuidadosa antes de confirmar."
        )
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
