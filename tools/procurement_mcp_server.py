"""
MCP Server para Sistema de Contratacoes Publicas.
Expoe tools para consulta a bases de dados oficiais.

Usage:
    python -m tools.procurement_mcp_server
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ProcurementTools:
    """Ferramentas para pesquisa de precos e consulta normativa."""

    def __init__(self):
        self.sources_log_path = Path(
            os.environ.get("SOURCES_LOG", "sources/sources_log.jsonl")
        )
        self.price_sources_path = Path(
            os.environ.get(
                "PRICE_SOURCES_LOG",
                "sources/price_sources_log.jsonl",
            )
        )
        self._load_sources()

    def _load_sources(self):
        """Carrega fontes validas do log."""
        self.sources = {}
        if self.sources_log_path.exists():
            with self.sources_log_path.open() as f:
                for line in f:
                    line = line.strip()
                    if line:
                        source = json.loads(line)
                        self.sources[source["id"]] = source

        self.price_sources = {}
        if self.price_sources_path.exists():
            with self.price_sources_path.open() as f:
                for line in f:
                    line = line.strip()
                    if line:
                        source = json.loads(line)
                        self.price_sources[source["id"]] = source

    def validate_source(self, source_id: str) -> dict:
        """
        Valida se uma fonte esta vigente e acessivel.

        Args:
            source_id: ID da fonte no formato XX-XXX-NNNN

        Returns:
            dict com status da validacao
        """
        source = self.sources.get(source_id)
        if source is None:
            source = self.price_sources.get(source_id)

        if source is None:
            return {
                "valid": False,
                "error": f"Fonte {source_id} nao encontrada no log",
            }

        if source.get("status") != "vigente":
            return {
                "valid": False,
                "error": (
                    f"Fonte {source_id} nao esta vigente. "
                    f"Status: {source.get('status')}"
                ),
            }

        verificado_em = source.get("verificado_em")
        if verificado_em:
            verificado_date = datetime.fromisoformat(verificado_em)
            if datetime.now() - verificado_date > timedelta(days=180):
                return {
                    "valid": True,
                    "warning": (
                        f"Fonte verificada ha mais de 6 meses "
                        f"({verificado_em}). Recomenda-se "
                        f"re-verificacao."
                    ),
                }

        return {"valid": True, "source": source}

    def search_pncp(
        self,
        termo: str,
        categoria: Optional[str] = None,
        limite: int = 10,
    ) -> dict:
        """
        Busca contratos no Portal Nacional de Contratacoes Publicas.

        Args:
            termo: Termo de busca (descricao do objeto)
            categoria: Categoria de contratacao (bens, servicos, obras)
            limite: Numero maximo de resultados

        Returns:
            dict com resultados da busca
        """
        pncp_source = self.price_sources.get("PRC-001")
        if not pncp_source or pncp_source.get("status") != "vigente":
            return {
                "success": False,
                "error": "Fonte PNCP nao disponivel ou nao vigente",
            }

        return {
            "success": True,
            "fonte": {
                "id": "PRC-001",
                "nome": "PNCP",
                "url": pncp_source.get("url"),
                "consultado_em": datetime.now().isoformat(),
            },
            "termo_buscado": termo,
            "categoria": categoria,
            "limite": limite,
            "resultados": [],
            "aviso": (
                "Dados simulados - implementar integracao real com "
                "API PNCP em https://pncp.gov.br/api/consulta/v1/"
            ),
        }

    def get_sinapi_price(
        self,
        codigo: str,
        estado: str = "MG",
        desonerado: bool = False,
    ) -> dict:
        """
        Consulta preco de composicao no SINAPI.

        Args:
            codigo: Codigo SINAPI da composicao
            estado: UF para referencia de precos
            desonerado: Se deve usar tabela desonerada

        Returns:
            dict com preco e metadados
        """
        sinapi_source = self.price_sources.get("PRC-003")
        if not sinapi_source or sinapi_source.get("status") != "vigente":
            return {
                "success": False,
                "error": "Fonte SINAPI nao disponivel ou nao vigente",
            }

        regime = "Desonerado" if desonerado else "Nao Desonerado"
        return {
            "success": True,
            "fonte": {
                "id": "PRC-003",
                "nome": "SINAPI",
                "referencia": f"SINAPI {estado} {regime}",
                "consultado_em": datetime.now().isoformat(),
            },
            "codigo": codigo,
            "estado": estado,
            "preco": {
                "valor": 0.0,
                "unidade": "UN",
                "referencia_mes": datetime.now().strftime("%Y-%m"),
            },
            "aviso": (
                "Dados simulados - implementar integracao real com "
                "base SINAPI da Caixa"
            ),
        }

    def get_bps_price(
        self,
        medicamento: str,
        apresentacao: Optional[str] = None,
    ) -> dict:
        """
        Consulta preco no Banco de Precos em Saude.

        Args:
            medicamento: Nome ou codigo do medicamento
            apresentacao: Forma de apresentacao (opcional)

        Returns:
            dict com preco e metadados
        """
        bps_source = self.price_sources.get("PRC-004")
        if not bps_source or bps_source.get("status") != "vigente":
            return {
                "success": False,
                "error": "Fonte BPS nao disponivel ou nao vigente",
            }

        return {
            "success": True,
            "fonte": {
                "id": "PRC-004",
                "nome": "Banco de Precos em Saude",
                "consultado_em": datetime.now().isoformat(),
            },
            "medicamento": medicamento,
            "apresentacao": apresentacao,
            "precos": {
                "media": 0.0,
                "mediana": 0.0,
                "minimo": 0.0,
                "maximo": 0.0,
                "n_registros": 0,
            },
            "aviso": (
                "Dados simulados - implementar integracao real com "
                "BPS em https://bps.saude.gov.br/"
            ),
        }

    def check_cmed_ceiling(
        self,
        medicamento: str,
        preco_proposto: float,
    ) -> dict:
        """
        Verifica se preco proposto esta dentro do teto CMED.

        Args:
            medicamento: Nome ou codigo do medicamento
            preco_proposto: Preco a ser verificado

        Returns:
            dict com resultado da verificacao
        """
        cmed_source = self.price_sources.get("PRC-005")
        if not cmed_source or cmed_source.get("status") != "vigente":
            return {
                "success": False,
                "error": "Fonte CMED nao disponivel ou nao vigente",
            }

        teto_cmed = 0.0  # Buscar valor real da tabela CMED

        return {
            "success": True,
            "fonte": {
                "id": "PRC-005",
                "nome": "CMED/ANVISA",
                "consultado_em": datetime.now().isoformat(),
            },
            "medicamento": medicamento,
            "preco_proposto": preco_proposto,
            "teto_cmed": teto_cmed,
            "dentro_do_teto": (
                preco_proposto <= teto_cmed if teto_cmed > 0 else None
            ),
            "aviso": (
                "Dados simulados - implementar integracao real com "
                "tabela CMED/ANVISA"
            ),
        }

    def get_anp_price(
        self,
        combustivel: str,
        municipio: str = "EXTREMA",
        estado: str = "MG",
    ) -> dict:
        """
        Consulta preco de combustivel na ANP.

        Args:
            combustivel: Tipo de combustivel (gasolina, diesel, etanol)
            municipio: Nome do municipio
            estado: UF

        Returns:
            dict com preco e metadados
        """
        anp_source = self.price_sources.get("PRC-007")
        if not anp_source or anp_source.get("status") != "vigente":
            return {
                "success": False,
                "error": "Fonte ANP nao disponivel ou nao vigente",
            }

        return {
            "success": True,
            "fonte": {
                "id": "PRC-007",
                "nome": "ANP",
                "consultado_em": datetime.now().isoformat(),
            },
            "combustivel": combustivel,
            "municipio": municipio,
            "estado": estado,
            "preco": {
                "media": 0.0,
                "minimo": 0.0,
                "maximo": 0.0,
                "data_coleta": None,
            },
            "aviso": (
                "Dados simulados - implementar integracao real com "
                "levantamento de precos ANP"
            ),
        }


def main():
    """Inicia o MCP server."""
    tools = ProcurementTools()

    print("MCP Server procurement-tools iniciado")
    print(f"Sources log: {tools.sources_log_path}")
    print(f"Price sources log: {tools.price_sources_path}")
    print(f"Fontes normativas carregadas: {len(tools.sources)}")
    print(f"Fontes de precos carregadas: {len(tools.price_sources)}")
    print()
    print("Tools disponiveis:")
    print("  - validate_source(source_id)")
    print("  - search_pncp(termo, categoria, limite)")
    print("  - get_sinapi_price(codigo, estado, desonerado)")
    print("  - get_bps_price(medicamento, apresentacao)")
    print("  - check_cmed_ceiling(medicamento, preco_proposto)")
    print("  - get_anp_price(combustivel, municipio, estado)")
    print()
    print(
        "NOTA: Todas as ferramentas retornam dados simulados. "
        "Implementar integracoes reais com as APIs oficiais para "
        "uso em producao."
    )


if __name__ == "__main__":
    main()
