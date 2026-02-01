"""
MCP Server para Sistema de Contratacoes Publicas.
Expoe tools para consulta a bases de dados oficiais.

Usage:
    python -m tools.procurement_mcp_server
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from tools.http_utils import CachedHTTPClient
from tools.pncp_client import PNCPClient
from tools.sinapi_client import SINAPIClient
from tools.bps_client import BPSClient

logger = logging.getLogger(__name__)


class ProcurementTools:
    """Ferramentas para pesquisa de precos e consulta normativa."""

    def __init__(self):
        self.sources_log_path = Path(
            self._resolve_env(
                "SOURCES_LOG", "sources/sources_log.jsonl"
            )
        )
        self.price_sources_path = Path(
            self._resolve_env(
                "PRICE_SOURCES_LOG",
                "sources/price_sources_log.jsonl",
            )
        )

        # Shared HTTP client with retry + cache
        self._http = CachedHTTPClient()

        # Specialized clients
        self.pncp = PNCPClient(http=self._http)
        self.sinapi = SINAPIClient(
            estado=os.environ.get("SINAPI_ESTADO", "MG"),
            http=self._http,
        )
        self.bps = BPSClient(http=self._http)

        self._load_sources()

    @staticmethod
    def _resolve_env(key: str, default: str) -> str:
        """Read env var, falling back to default if unset or unresolved."""
        val = os.environ.get(key, default)
        if "${" in val:
            return default
        return val

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
                "error": (
                    f"Fonte {source_id} nao encontrada no log"
                ),
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
            verificado_date = datetime.fromisoformat(
                verificado_em
            )
            age = datetime.now() - verificado_date
            if age > timedelta(days=180):
                return {
                    "valid": True,
                    "warning": (
                        f"Fonte verificada ha mais de 6 meses "
                        f"({verificado_em}). Recomenda-se "
                        f"re-verificacao."
                    ),
                }

        return {"valid": True, "source": source}

    async def search_pncp(
        self,
        termo: str,
        categoria: Optional[str] = None,
        uf: Optional[str] = None,
        limite: int = 10,
    ) -> dict:
        """
        Busca contratos no Portal Nacional de Contratacoes.

        Args:
            termo: Termo de busca (descricao do objeto)
            categoria: Categoria de contratacao
            uf: Filtro por UF
            limite: Numero maximo de resultados

        Returns:
            dict com resultados da busca
        """
        pncp_source = self.price_sources.get("PRC-001")
        if (
            not pncp_source
            or pncp_source.get("status") != "vigente"
        ):
            return {
                "success": False,
                "error": (
                    "Fonte PNCP nao disponivel ou nao vigente"
                ),
            }

        result = await self.pncp.search_contratos(
            termo=termo, uf=uf, limite=limite
        )

        contratos_dicts = []
        for c in result.contratos:
            contratos_dicts.append(asdict(c))

        return {
            "success": True,
            "fonte": {
                "id": "PRC-001",
                "nome": "PNCP",
                "url": pncp_source.get("url"),
                "consultado_em": result.data_consulta,
            },
            "termo_buscado": termo,
            "categoria": categoria,
            "total_resultados": result.total_resultados,
            "resultados": contratos_dicts,
        }

    async def get_sinapi_price(
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
        if (
            not sinapi_source
            or sinapi_source.get("status") != "vigente"
        ):
            return {
                "success": False,
                "error": (
                    "Fonte SINAPI nao disponivel ou nao vigente"
                ),
            }

        # Ensure SINAPI data is loaded
        if self.sinapi.estado != estado:
            self.sinapi = SINAPIClient(
                estado=estado, http=self._http
            )
        await self.sinapi.ensure_loaded()

        comp = self.sinapi.get_composicao(
            codigo, desonerado=desonerado
        )

        regime = (
            "Desonerado" if desonerado else "Nao Desonerado"
        )
        if comp is None:
            return {
                "success": True,
                "fonte": {
                    "id": "PRC-003",
                    "nome": "SINAPI",
                    "referencia": f"SINAPI {estado} {regime}",
                    "consultado_em": (
                        datetime.now().isoformat()
                    ),
                },
                "codigo": codigo,
                "encontrado": False,
                "mensagem": (
                    f"Composicao {codigo} nao encontrada na "
                    f"base SINAPI {estado}. Verifique o codigo "
                    f"ou coloque o CSV mais recente em "
                    f"data/sinapi/{estado.lower()}/."
                ),
            }

        return {
            "success": True,
            "fonte": {
                "id": "PRC-003",
                "nome": "SINAPI",
                "referencia": f"SINAPI {estado} {regime}",
                "consultado_em": datetime.now().isoformat(),
            },
            "codigo": codigo,
            "encontrado": True,
            "composicao": asdict(comp),
        }

    async def search_sinapi(
        self,
        termo: str,
        estado: str = "MG",
        desonerado: bool = False,
        limite: int = 10,
    ) -> dict:
        """
        Busca composicoes SINAPI por descricao.

        Args:
            termo: Texto para busca na descricao
            estado: UF de referencia
            desonerado: Se True, tabela desonerada
            limite: Maximo de resultados

        Returns:
            dict com composicoes encontradas
        """
        if self.sinapi.estado != estado:
            self.sinapi = SINAPIClient(
                estado=estado, http=self._http
            )
        await self.sinapi.ensure_loaded()

        comps = self.sinapi.search_composicoes(
            termo, desonerado=desonerado, limite=limite
        )

        return {
            "success": True,
            "fonte": {
                "id": "PRC-003",
                "nome": "SINAPI",
                "consultado_em": datetime.now().isoformat(),
            },
            "termo_buscado": termo,
            "resultados": [asdict(c) for c in comps],
        }

    async def get_bps_price(
        self,
        medicamento: str,
        apresentacao: Optional[str] = None,
    ) -> dict:
        """
        Consulta preco no Banco de Precos em Saude.

        Args:
            medicamento: Nome ou codigo do medicamento
            apresentacao: Forma de apresentacao

        Returns:
            dict com preco e metadados
        """
        bps_source = self.price_sources.get("PRC-004")
        if (
            not bps_source
            or bps_source.get("status") != "vigente"
        ):
            return {
                "success": False,
                "error": (
                    "Fonte BPS nao disponivel ou nao vigente"
                ),
            }

        resumo = self.bps.search_bps(
            medicamento, apresentacao=apresentacao
        )

        if resumo is None:
            return {
                "success": True,
                "fonte": {
                    "id": "PRC-004",
                    "nome": "Banco de Precos em Saude",
                    "consultado_em": (
                        datetime.now().isoformat()
                    ),
                },
                "medicamento": medicamento,
                "apresentacao": apresentacao,
                "encontrado": False,
                "mensagem": (
                    f"Nenhum registro encontrado para "
                    f"'{medicamento}' no BPS. Exporte dados "
                    f"do portal BPS e coloque em data/bps/."
                ),
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
            "encontrado": True,
            "precos": asdict(resumo),
        }

    async def check_cmed_ceiling(
        self,
        medicamento: str,
        preco_proposto: float,
    ) -> dict:
        """
        Verifica se preco esta dentro do teto CMED.

        Args:
            medicamento: Nome ou codigo do medicamento
            preco_proposto: Preco a ser verificado

        Returns:
            dict com resultado da verificacao
        """
        cmed_source = self.price_sources.get("PRC-005")
        if (
            not cmed_source
            or cmed_source.get("status") != "vigente"
        ):
            return {
                "success": False,
                "error": (
                    "Fonte CMED nao disponivel ou nao vigente"
                ),
            }

        # Ensure CMED data is loaded
        await self.bps.ensure_cmed_loaded()

        resultado = self.bps.verificar_teto(
            medicamento, preco_proposto
        )

        return {
            "success": True,
            "fonte": {
                "id": "PRC-005",
                "nome": "CMED/ANVISA",
                "consultado_em": datetime.now().isoformat(),
            },
            "medicamento": medicamento,
            "preco_proposto": preco_proposto,
            **resultado,
        }

    async def get_anp_price(
        self,
        combustivel: str,
        municipio: str = "EXTREMA",
        estado: str = "MG",
    ) -> dict:
        """
        Consulta preco de combustivel na ANP.

        A ANP publica levantamentos semanais de precos por
        municipio. Este metodo consulta a API de dados abertos.

        Args:
            combustivel: Tipo (gasolina, diesel, etanol)
            municipio: Nome do municipio
            estado: UF

        Returns:
            dict com preco e metadados
        """
        anp_source = self.price_sources.get("PRC-007")
        if (
            not anp_source
            or anp_source.get("status") != "vigente"
        ):
            return {
                "success": False,
                "error": (
                    "Fonte ANP nao disponivel ou nao vigente"
                ),
            }

        # ANP dados abertos endpoint
        anp_api = (
            "https://www.gov.br/anp/pt-br/assuntos/"
            "precos-e-defesa-da-concorrencia/precos/"
            "levantamento-de-precos/consulta-de-precos-"
            "recebidos-pelos-agentes-consumidores"
        )

        try:
            data = await self._http.get_json(
                anp_api,
                params={
                    "combustivel": combustivel,
                    "municipio": municipio,
                    "estado": estado,
                },
                cache_ttl=3600,
            )
            if isinstance(data, dict) and data.get(
                "resultado"
            ):
                items = data["resultado"]
                precos = [
                    float(i.get("preco", 0))
                    for i in items
                    if i.get("preco")
                ]
                if precos:
                    return {
                        "success": True,
                        "fonte": {
                            "id": "PRC-007",
                            "nome": "ANP",
                            "consultado_em": (
                                datetime.now().isoformat()
                            ),
                        },
                        "combustivel": combustivel,
                        "municipio": municipio,
                        "estado": estado,
                        "preco": {
                            "media": round(
                                sum(precos) / len(precos), 3
                            ),
                            "minimo": round(min(precos), 3),
                            "maximo": round(max(precos), 3),
                            "n_postos": len(precos),
                            "data_coleta": items[0].get(
                                "data", ""
                            ),
                        },
                    }
        except Exception as exc:
            logger.warning("ANP query failed: %s", exc)

        # Fallback
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
            "encontrado": False,
            "mensagem": (
                f"Nao foi possivel obter precos ANP para "
                f"{combustivel} em {municipio}/{estado}. "
                f"Consulte o levantamento semanal em "
                f"gov.br/anp."
            ),
        }

    async def close(self):
        """Cleanup HTTP client resources."""
        await self._http.close()


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    server = FastMCP("procurement-tools")
    _tools = ProcurementTools()

    @server.tool()
    def validate_source(source_id: str) -> dict:
        """Valida se uma fonte normativa esta vigente.

        Args:
            source_id: ID da fonte (ex: BR-FED-0001)
        """
        return _tools.validate_source(source_id)

    @server.tool()
    async def search_pncp(
        termo: str,
        categoria: str = "",
        uf: str = "",
        limite: int = 10,
    ) -> dict:
        """Busca contratos no Portal Nacional de Contratacoes.

        Args:
            termo: Termo de busca (descricao do objeto)
            categoria: Categoria de contratacao
            uf: Filtro por UF
            limite: Numero maximo de resultados
        """
        return await _tools.search_pncp(
            termo,
            categoria=categoria or None,
            uf=uf or None,
            limite=limite,
        )

    @server.tool()
    async def get_sinapi_price(
        codigo: str,
        estado: str = "MG",
        desonerado: bool = False,
    ) -> dict:
        """Consulta preco de composicao SINAPI.

        Args:
            codigo: Codigo SINAPI (ex: 87529)
            estado: UF para referencia de precos
            desonerado: Se deve usar tabela desonerada
        """
        return await _tools.get_sinapi_price(
            codigo, estado=estado, desonerado=desonerado
        )

    @server.tool()
    async def search_sinapi(
        termo: str,
        estado: str = "MG",
        desonerado: bool = False,
        limite: int = 10,
    ) -> dict:
        """Busca composicoes SINAPI por descricao.

        Args:
            termo: Texto para busca
            estado: UF de referencia
            desonerado: Se True, tabela desonerada
            limite: Maximo de resultados
        """
        return await _tools.search_sinapi(
            termo,
            estado=estado,
            desonerado=desonerado,
            limite=limite,
        )

    @server.tool()
    async def get_bps_price(
        medicamento: str,
        apresentacao: str = "",
    ) -> dict:
        """Consulta preco no Banco de Precos em Saude.

        Args:
            medicamento: Nome ou codigo do medicamento
            apresentacao: Forma de apresentacao
        """
        return await _tools.get_bps_price(
            medicamento,
            apresentacao=apresentacao or None,
        )

    @server.tool()
    async def check_cmed_ceiling(
        medicamento: str,
        preco_proposto: float,
    ) -> dict:
        """Verifica se preco esta dentro do teto CMED.

        Args:
            medicamento: Nome ou codigo do medicamento
            preco_proposto: Preco a ser verificado
        """
        return await _tools.check_cmed_ceiling(
            medicamento, preco_proposto
        )

    @server.tool()
    async def get_anp_price(
        combustivel: str,
        municipio: str = "EXTREMA",
        estado: str = "MG",
    ) -> dict:
        """Consulta preco de combustivel na ANP.

        Args:
            combustivel: Tipo (gasolina, diesel, etanol)
            municipio: Nome do municipio
            estado: UF
        """
        return await _tools.get_anp_price(
            combustivel,
            municipio=municipio,
            estado=estado,
        )

    return server


def main():
    """Inicia o MCP server via stdio."""
    server = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
