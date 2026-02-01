"""
Cliente para a API do Portal Nacional de Contratacoes Publicas (PNCP).

API Base: https://pncp.gov.br/api/consulta/v1/
Documentacao: https://pncp.gov.br/api/consulta/swagger-ui/

Este modulo implementa a interface com a API publica do PNCP para
consulta de contratos, atas de registro de precos e avisos de licitacao.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from tools.http_utils import CachedHTTPClient, HTTPError

logger = logging.getLogger(__name__)

PNCP_BASE = "https://pncp.gov.br/api/consulta/v1"


@dataclass
class PNCPContrato:
    """Representa um contrato retornado pela API do PNCP."""

    contrato_id: str
    objeto: str
    valor_total: float
    valor_unitario: Optional[float]
    orgao: str
    cnpj_orgao: str
    data_assinatura: str
    data_vigencia_fim: str
    fornecedor: str
    cnpj_fornecedor: str
    url_pncp: str


@dataclass
class PNCPSearchResult:
    """Resultado de uma busca no PNCP."""

    termo: str
    total_resultados: int
    contratos: list
    data_consulta: str


class PNCPClient:
    """Cliente para consultas na API do PNCP."""

    def __init__(self, http: Optional[CachedHTTPClient] = None):
        self.http = http or CachedHTTPClient()

    async def search_contratos(
        self,
        termo: str,
        uf: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        pagina: int = 1,
        limite: int = 10,
    ) -> PNCPSearchResult:
        """
        Busca contratos no PNCP.

        Endpoint: GET /contratos

        Args:
            termo: Termo de busca
            uf: Filtro por UF (ex: "MG")
            data_inicio: Data minima (YYYYMMDD)
            data_fim: Data maxima (YYYYMMDD)
            pagina: Pagina de resultados
            limite: Resultados por pagina (max 500)

        Returns:
            PNCPSearchResult com contratos encontrados
        """
        params = {
            "q": termo,
            "pagina": str(pagina),
            "tamanhoPagina": str(min(limite, 500)),
        }
        if uf:
            params["uf"] = uf
        if data_inicio:
            params["dataInicial"] = data_inicio
        if data_fim:
            params["dataFinal"] = data_fim

        contratos = []
        total = 0
        try:
            data = await self.http.get_json(
                f"{PNCP_BASE}/contratos", params=params
            )
            if isinstance(data, dict):
                total = data.get("totalRegistros", 0)
                for item in data.get("data", []):
                    contratos.append(self._parse_contrato(item))
            elif isinstance(data, list):
                total = len(data)
                for item in data:
                    contratos.append(self._parse_contrato(item))
        except HTTPError as exc:
            logger.warning("PNCP search_contratos failed: %s", exc)

        return PNCPSearchResult(
            termo=termo,
            total_resultados=total,
            contratos=contratos,
            data_consulta=datetime.now().isoformat(),
        )

    async def get_contrato(
        self, cnpj: str, ano: str, sequencial: str
    ) -> Optional[PNCPContrato]:
        """
        Busca um contrato especifico por chave composta.

        Endpoint: GET /contratos/{cnpj}/{ano}/{sequencial}

        Args:
            cnpj: CNPJ do orgao
            ano: Ano do contrato
            sequencial: Sequencial do contrato

        Returns:
            PNCPContrato ou None se nao encontrado
        """
        url = (
            f"{PNCP_BASE}/contratos/{cnpj}/{ano}/{sequencial}"
        )
        try:
            data = await self.http.get_json(url)
            if data:
                return self._parse_contrato(data)
        except HTTPError as exc:
            logger.warning("PNCP get_contrato failed: %s", exc)
        return None

    async def search_atas_srp(
        self,
        termo: str,
        uf: Optional[str] = None,
        vigente: bool = True,
        pagina: int = 1,
        limite: int = 10,
    ) -> list:
        """
        Busca atas de registro de precos.

        Endpoint: GET /atas

        Args:
            termo: Termo de busca
            uf: Filtro por UF
            vigente: Se True, filtra atas dentro da vigencia
            pagina: Pagina de resultados
            limite: Resultados por pagina

        Returns:
            Lista de dicts com dados de atas
        """
        params = {
            "q": termo,
            "pagina": str(pagina),
            "tamanhoPagina": str(min(limite, 500)),
        }
        if uf:
            params["uf"] = uf

        results = []
        try:
            data = await self.http.get_json(
                f"{PNCP_BASE}/atas", params=params
            )
            if isinstance(data, dict):
                items = data.get("data", [])
            elif isinstance(data, list):
                items = data
            else:
                items = []
            for item in items:
                if vigente:
                    fim = item.get("dataVigenciaFim", "")
                    if fim:
                        try:
                            dt = datetime.strptime(
                                fim[:10], "%Y-%m-%d"
                            )
                            if dt < datetime.now():
                                continue
                        except ValueError:
                            pass
                results.append(item)
        except HTTPError as exc:
            logger.warning("PNCP search_atas failed: %s", exc)
        return results

    async def search_avisos(
        self,
        orgao_cnpj: Optional[str] = None,
        modalidade: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        pagina: int = 1,
        limite: int = 10,
    ) -> list:
        """
        Busca avisos de licitacao publicados.

        Endpoint: GET /compras

        Args:
            orgao_cnpj: CNPJ do orgao para filtrar
            modalidade: Filtro por modalidade licitatoria
            data_inicio: Data minima (YYYYMMDD)
            data_fim: Data maxima (YYYYMMDD)
            pagina: Pagina de resultados
            limite: Resultados por pagina

        Returns:
            Lista de avisos encontrados
        """
        params = {
            "pagina": str(pagina),
            "tamanhoPagina": str(min(limite, 500)),
        }
        if orgao_cnpj:
            params["cnpj"] = orgao_cnpj
        if modalidade:
            params["codigoModalidadeContratacao"] = modalidade
        if data_inicio:
            params["dataInicial"] = data_inicio
        if data_fim:
            params["dataFinal"] = data_fim

        results = []
        try:
            data = await self.http.get_json(
                f"{PNCP_BASE}/compras", params=params
            )
            if isinstance(data, dict):
                items = data.get("data", [])
            elif isinstance(data, list):
                items = data
            else:
                items = []
            results.extend(items)
        except HTTPError as exc:
            logger.warning("PNCP search_avisos failed: %s", exc)
        return results

    def _parse_contrato(self, raw: dict) -> PNCPContrato:
        """Parse raw PNCP API response into PNCPContrato."""
        orgao = raw.get("orgaoEntidade", {})
        fornecedor = raw.get("fornecedor", {})
        cnpj = orgao.get("cnpj", "")
        ano = raw.get("anoContrato", "")
        seq = raw.get("sequencialContrato", "")
        return PNCPContrato(
            contrato_id=raw.get("id", f"{cnpj}-{ano}-{seq}"),
            objeto=raw.get(
                "objetoContrato", raw.get("objeto", "")
            ),
            valor_total=float(raw.get("valorInicial", 0)),
            valor_unitario=None,
            orgao=orgao.get(
                "razaoSocial", raw.get("nomeOrgao", "")
            ),
            cnpj_orgao=cnpj,
            data_assinatura=raw.get("dataAssinatura", ""),
            data_vigencia_fim=raw.get("dataVigenciaFim", ""),
            fornecedor=fornecedor.get(
                "razaoSocial", raw.get("nomeFornecedor", "")
            ),
            cnpj_fornecedor=fornecedor.get("cnpj", ""),
            url_pncp=raw.get(
                "linkUrl",
                f"https://pncp.gov.br/app/contratos/"
                f"{cnpj}/{ano}/{seq}",
            ),
        )
