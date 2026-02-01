# Data Sources -- Setup Guide

This document describes how to populate the `data/` directories so the
procurement tools can operate with real price data.

## Directory Structure

```
data/
  sinapi/
    mg/          # SINAPI tables for Minas Gerais
  bps/           # BPS exported CSVs
  cmed/          # CMED price ceiling tables
```

## SINAPI (Construction Costs)

Download monthly tables from
[Caixa Economica Federal](https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/).

1. Select the desired state (default: MG) and month.
2. Download the CSV or XLS file for "Precos de Composicoes".
3. Place the file in `data/sinapi/mg/` (or the appropriate state directory).

The system auto-detects the most recent file by filename sort order.

Expected CSV format (semicolon-delimited, latin-1 encoding):

```
CODIGO;DESCRICAO;UNIDADE;PRECO UNITARIO
87529;PINTURA LATEX PVA;M2;12,50
```

## BPS (Health Procurement Prices)

Export data from the [BPS portal](https://bps.saude.gov.br/).

1. Search for the desired medication or supply.
2. Export results as CSV.
3. Place the file in `data/bps/`.

Expected CSV format (semicolon-delimited, UTF-8):

```
MEDICAMENTO;APRESENTACAO;PRINCIPIO_ATIVO;PRECO_UNITARIO;ORGAO;UF;DATA_COMPRA;QUANTIDADE;MODALIDADE
```

## CMED (ANVISA Price Ceilings)

Download the CMED table from
[ANVISA](https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos).

1. Download the latest published XLS or CSV.
2. Place in `data/cmed/`.

Expected CSV columns: `SUBSTANCIA`, `PRODUTO`, `APRESENTACAO`,
`LABORATORIO`, `PF_SEM_IMPOSTOS`, `PMVG_SEM_IMPOSTOS`,
`PMVG_COM_IMPOSTOS`, `LISTA_CONCESSAO`.

## Notes

- Files in `data/` are git-ignored (except `.gitkeep` placeholders).
- The system loads the most recent file in each directory automatically.
- For SINAPI XLS files, `openpyxl` must be installed (`pip install -r requirements.txt`).
