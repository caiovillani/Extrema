"""
Cliente para consulta de precos de combustiveis na ANP.

A ANP (Agencia Nacional do Petroleo, Gas Natural e
Biocombustiveis) publica levantamentos semanais de precos
por municipio em formato CSV.

Dados disponiveis em:
https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/
"""

import csv
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from tools.http_utils import CachedHTTPClient, HTTPError

logger = logging.getLogger(__name__)

# Endpoint para dados abertos ANP
ANP_API_BASE = (
    "https://www.gov.br/anp/pt-br/assuntos/"
    "precos-e-defesa-da-concorrencia/precos/"
    "levantamento-de-precos/consulta-de-precos-"
    "recebidos-pelos-agentes-consumidores"
)

# Diretorio para cache local de CSVs semanais
ANP_CACHE_DIR = Path(
    os.environ.get("ANP_CACHE_DIR", "data/anp")
)


@dataclass
class ANPPreco:
    """Registro individual de preco de combustivel da ANP."""

    combustivel: str
    municipio: str
    estado: str
    preco_revenda: float
    bandeira: str
    data_coleta: str
    nome_posto: str


@dataclass
class ANPResumo:
    """Resumo estatistico de precos ANP."""

    combustivel: str
    municipio: str
    estado: str
    media: float
    minimo: float
    maximo: float
    n_postos: int
    data_coleta: str


class ANPClient:
    """Cliente para consultas de precos ANP.

    Fluxo:
    1. Tenta carregar CSV semanal do cache local (data/anp/)
    2. Caso nao exista, consulta API de dados abertos
    3. Indexa em memoria para consultas por combustivel/municipio
    """

    def __init__(
        self,
        municipio: str = "EXTREMA",
        estado: str = "MG",
        http: Optional[CachedHTTPClient] = None,
    ):
        self.municipio = municipio.upper()
        self.estado = estado.upper()
        self.http = http or CachedHTTPClient()
        self._registros: list[ANPPreco] = []
        self._loaded = False

    def load_from_csv(self, csv_path: str | Path):
        """
        Carrega registros a partir de CSV local da ANP.

        O CSV deve ter colunas separadas por ponto-e-virgula:
        COMBUSTIVEL, MUNICIPIO, ESTADO, PRECO_REVENDA,
        BANDEIRA, DATA_COLETA, NOME_POSTO.

        Args:
            csv_path: Caminho para o arquivo CSV
        """
        path = Path(csv_path)
        if not path.exists():
            logger.warning("CSV not found: %s", path)
            return

        self._registros = []
        with path.open(encoding="latin-1") as fh:
            reader = csv.DictReader(fh, delimiter=";")
            for row in reader:
                combustivel = (
                    row.get("COMBUSTIVEL", "")
                    or row.get("PRODUTO", "")
                ).strip()
                if not combustivel:
                    continue

                municipio = (
                    row.get("MUNICIPIO", "")
                    or row.get("MUNICÍPIO", "")
                ).strip().upper()

                estado = (
                    row.get("ESTADO", "")
                    or row.get("UF", "")
                ).strip().upper()

                preco_str = (
                    row.get("PRECO_REVENDA", "")
                    or row.get("PRECO REVENDA", "")
                    or row.get("VALOR DE VENDA", "")
                ).strip()
                preco_str = (
                    preco_str.replace(".", "").replace(",", ".")
                )
                try:
                    preco = float(preco_str) if preco_str else 0.0
                except ValueError:
                    preco = 0.0

                bandeira = (
                    row.get("BANDEIRA", "")
                ).strip()

                data_coleta = (
                    row.get("DATA_COLETA", "")
                    or row.get("DATA COLETA", "")
                    or row.get("DATA DA COLETA", "")
                ).strip()

                nome_posto = (
                    row.get("NOME_POSTO", "")
                    or row.get("REVENDA", "")
                    or row.get("NOME POSTO", "")
                ).strip()

                self._registros.append(ANPPreco(
                    combustivel=combustivel,
                    municipio=municipio,
                    estado=estado,
                    preco_revenda=preco,
                    bandeira=bandeira,
                    data_coleta=data_coleta,
                    nome_posto=nome_posto,
                ))

        self._loaded = True
        logger.info(
            "Loaded %d ANP records from %s",
            len(self._registros), path,
        )

    async def ensure_loaded(self):
        """
        Ensure data is loaded. Tries local cache first,
        then attempts API query.
        """
        if self._loaded:
            return

        # Try local cache directory
        cache_dir = ANP_CACHE_DIR
        if cache_dir.exists():
            csvs = sorted(cache_dir.glob("*.csv"), reverse=True)
            if csvs:
                self.load_from_csv(csvs[0])
                return

        # Try downloading via API
        await self._query_api(
            self.municipio, self.estado
        )

    async def _query_api(
        self,
        municipio: str,
        estado: str,
    ):
        """
        Query ANP dados abertos API.

        Args:
            municipio: Nome do municipio
            estado: UF
        """
        try:
            data = await self.http.get_json(
                ANP_API_BASE,
                params={
                    "municipio": municipio,
                    "estado": estado,
                },
                cache_ttl=3600,
            )
            if isinstance(data, dict) and data.get(
                "resultado"
            ):
                for item in data["resultado"]:
                    try:
                        preco = float(
                            item.get("preco", 0)
                        )
                    except (ValueError, TypeError):
                        preco = 0.0
                    self._registros.append(ANPPreco(
                        combustivel=item.get(
                            "combustivel", ""
                        ),
                        municipio=municipio.upper(),
                        estado=estado.upper(),
                        preco_revenda=preco,
                        bandeira=item.get("bandeira", ""),
                        data_coleta=item.get("data", ""),
                        nome_posto=item.get("posto", ""),
                    ))
                self._loaded = True
        except Exception as exc:
            logger.warning("ANP API query failed: %s", exc)

    def search_postos(
        self,
        combustivel: str,
        municipio: Optional[str] = None,
        limite: int = 10,
    ) -> list[ANPPreco]:
        """
        Busca registros individuais de postos.

        Args:
            combustivel: Tipo de combustivel
            municipio: Filtrar por municipio
            limite: Maximo de resultados

        Returns:
            Lista de ANPPreco
        """
        pattern = re.compile(
            re.escape(combustivel), re.IGNORECASE
        )
        mun = municipio.upper() if municipio else None
        results: list[ANPPreco] = []
        for reg in self._registros:
            if not pattern.search(reg.combustivel):
                continue
            if mun and reg.municipio != mun:
                continue
            results.append(reg)
            if len(results) >= limite:
                break
        return results

    def get_precos(
        self,
        combustivel: str,
        municipio: Optional[str] = None,
    ) -> Optional[ANPResumo]:
        """
        Calcula resumo estatistico para combustivel/municipio.

        Args:
            combustivel: Tipo de combustivel
            municipio: Filtrar por municipio

        Returns:
            ANPResumo ou None se sem dados
        """
        pattern = re.compile(
            re.escape(combustivel), re.IGNORECASE
        )
        mun = municipio.upper() if municipio else None
        precos: list[float] = []
        data_coleta = ""
        for reg in self._registros:
            if not pattern.search(reg.combustivel):
                continue
            if mun and reg.municipio != mun:
                continue
            if reg.preco_revenda > 0:
                precos.append(reg.preco_revenda)
                if not data_coleta and reg.data_coleta:
                    data_coleta = reg.data_coleta

        if not precos:
            return None

        return ANPResumo(
            combustivel=combustivel,
            municipio=mun or self.municipio,
            estado=self.estado,
            media=round(sum(precos) / len(precos), 3),
            minimo=round(min(precos), 3),
            maximo=round(max(precos), 3),
            n_postos=len(precos),
            data_coleta=data_coleta,
        )
