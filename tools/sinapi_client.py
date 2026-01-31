"""
Cliente para consulta de precos SINAPI.

O SINAPI (Sistema Nacional de Pesquisa de Custos e Indices da
Construcao Civil) e mantido pela Caixa Economica Federal e IBGE.

Base de dados: https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/

NOTA: Implementacao inicial com estrutura de dados simulada.
As tabelas SINAPI sao disponibilizadas em planilhas mensais.
A integracao real requer download e parser das planilhas oficiais.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SINAPIComposicao:
    """Representa uma composicao SINAPI."""

    codigo: str
    descricao: str
    unidade: str
    preco_unitario: float
    referencia_mes: str
    estado: str
    desonerado: bool


@dataclass
class SINAPIInsumo:
    """Representa um insumo SINAPI."""

    codigo: str
    descricao: str
    unidade: str
    preco: float
    origem: str
    referencia_mes: str
    estado: str


class SINAPIClient:
    """Cliente para consultas na base SINAPI."""

    def __init__(self, estado: str = "MG"):
        self.estado = estado
        self.referencia_mes = datetime.now().strftime("%Y-%m")

    def get_composicao(
        self,
        codigo: str,
        desonerado: bool = False,
    ) -> Optional[SINAPIComposicao]:
        """
        Busca composicao por codigo SINAPI.

        Args:
            codigo: Codigo SINAPI (ex: "87529")
            desonerado: Se True, usa tabela desonerada

        Returns:
            SINAPIComposicao ou None se nao encontrado
        """
        # TODO: Implementar busca real na base SINAPI
        # Opcoes de implementacao:
        # 1. Parser de planilhas XLS/CSV baixadas do site da Caixa
        # 2. API interna se disponivel
        # 3. Base de dados local populada a partir das planilhas
        return None

    def search_composicoes(
        self,
        termo: str,
        desonerado: bool = False,
        limite: int = 10,
    ) -> list:
        """
        Busca composicoes por descricao.

        Args:
            termo: Termo de busca na descricao
            desonerado: Se True, usa tabela desonerada
            limite: Maximo de resultados

        Returns:
            Lista de SINAPIComposicao
        """
        # TODO: Implementar busca real
        return []

    def get_insumo(self, codigo: str) -> Optional[SINAPIInsumo]:
        """
        Busca insumo por codigo SINAPI.

        Args:
            codigo: Codigo do insumo SINAPI

        Returns:
            SINAPIInsumo ou None
        """
        # TODO: Implementar busca real
        return None

    def calcular_composicao_com_bdi(
        self,
        composicoes: list,
        bdi: float,
    ) -> dict:
        """
        Calcula valor total de composicoes aplicando BDI.

        Args:
            composicoes: Lista de tuplas (codigo, quantidade)
            bdi: Percentual de BDI (ex: 22.12 para 22,12%)

        Returns:
            dict com valores detalhados e total
        """
        # TODO: Implementar calculo real
        return {
            "composicoes": [],
            "subtotal": 0.0,
            "bdi_percentual": bdi,
            "bdi_valor": 0.0,
            "total": 0.0,
            "referencia": f"SINAPI {self.estado} {self.referencia_mes}",
        }
