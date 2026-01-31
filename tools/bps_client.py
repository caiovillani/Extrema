"""
Cliente para o Banco de Precos em Saude (BPS).

O BPS e mantido pelo Ministerio da Saude e registra precos praticados
em compras publicas de medicamentos e insumos de saude.

Base de dados: https://bps.saude.gov.br/

NOTA: Implementacao inicial com estrutura de dados simulada.
A integracao real requer acesso ao portal BPS.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BPSPreco:
    """Representa um registro de preco no BPS."""

    medicamento: str
    apresentacao: str
    principio_ativo: str
    preco_unitario: float
    orgao_comprador: str
    uf: str
    data_compra: str
    quantidade: int
    modalidade: str


@dataclass
class BPSResumo:
    """Resumo estatistico de precos no BPS."""

    medicamento: str
    apresentacao: str
    media: float
    mediana: float
    minimo: float
    maximo: float
    desvio_padrao: float
    n_registros: int
    periodo: str


@dataclass
class CMEDPreco:
    """Preco maximo de medicamento conforme CMED/ANVISA."""

    medicamento: str
    apresentacao: str
    laboratorio: str
    pf_sem_impostos: float
    pmvg_sem_impostos: float
    pmvg_com_impostos: float
    lista_concessao: str
    data_publicacao: str


class BPSClient:
    """Cliente para consultas no BPS e CMED."""

    def __init__(self):
        self.bps_url = "https://bps.saude.gov.br/"
        self.cmed_url = (
            "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed"
        )

    def search_bps(
        self,
        medicamento: str,
        apresentacao: Optional[str] = None,
        uf: Optional[str] = None,
        periodo_meses: int = 12,
    ) -> Optional[BPSResumo]:
        """
        Busca precos de medicamento no BPS.

        Args:
            medicamento: Nome ou principio ativo
            apresentacao: Forma farmaceutica e concentracao
            uf: Filtro por UF
            periodo_meses: Periodo de busca em meses

        Returns:
            BPSResumo com estatisticas de precos ou None
        """
        # TODO: Implementar consulta real ao BPS
        return None

    def get_registros_bps(
        self,
        medicamento: str,
        apresentacao: Optional[str] = None,
        limite: int = 20,
    ) -> list:
        """
        Busca registros individuais de compra no BPS.

        Args:
            medicamento: Nome ou principio ativo
            apresentacao: Forma farmaceutica
            limite: Maximo de registros

        Returns:
            Lista de BPSPreco
        """
        # TODO: Implementar consulta real
        return []

    def get_cmed_teto(
        self,
        medicamento: str,
        apresentacao: Optional[str] = None,
    ) -> Optional[CMEDPreco]:
        """
        Busca preco maximo CMED para medicamento.

        O PMVG (Preco Maximo de Venda ao Governo) e o teto
        obrigatorio para compras publicas de medicamentos.

        Args:
            medicamento: Nome ou principio ativo
            apresentacao: Forma farmaceutica

        Returns:
            CMEDPreco com teto ou None
        """
        # TODO: Implementar consulta real a tabela CMED
        # A tabela CMED e publicada em XLS pela ANVISA
        return None

    def verificar_teto(
        self,
        medicamento: str,
        preco_proposto: float,
        apresentacao: Optional[str] = None,
    ) -> dict:
        """
        Verifica se preco proposto esta dentro do teto CMED.

        Args:
            medicamento: Nome do medicamento
            preco_proposto: Preco a verificar
            apresentacao: Forma farmaceutica

        Returns:
            dict com resultado da verificacao
        """
        teto = self.get_cmed_teto(medicamento, apresentacao)
        if teto is None:
            return {
                "verificado": False,
                "erro": "Teto CMED nao encontrado para este medicamento",
            }

        dentro = preco_proposto <= teto.pmvg_sem_impostos
        return {
            "verificado": True,
            "dentro_do_teto": dentro,
            "preco_proposto": preco_proposto,
            "teto_pmvg": teto.pmvg_sem_impostos,
            "diferenca": preco_proposto - teto.pmvg_sem_impostos,
            "data_referencia": teto.data_publicacao,
        }
