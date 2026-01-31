---
name: price-research
version: 1.0.0
description: >
  Research prices for public procurement using official Brazilian
  sources (PNCP, Compras.gov, BPS, CMED, SINAPI, SICRO, ANP). Use when
  estimating costs for bidding documents (ETP, TR), validating budget
  proposals, or answering questions about market prices. Follows IN SEGES
  65/2021 methodology.
---

# Pesquisa de Precos -- IN SEGES 65/2021

## Visao Geral

Este Skill implementa o procedimento de pesquisa de precos para
contratacoes publicas conforme Instrucao Normativa SEGES/ME n. 65/2021.
O objetivo e obter precos referenciais defensaveis que atendam aos
requisitos de auditoria.

## Fontes Autorizadas

Consulte `reference/sources.md` para a lista completa de 11 fontes
validadas.

As fontes sao classificadas em duas categorias conforme Art. 5 da IN
65/2021:

**Precos Praticados (Art. 5, I)**: Contratos e atas do PNCP,
Compras.gov, Portal de Compras MG. Representam precos efetivamente
pagos pelo setor publico.

**Precos Setoriais (Art. 5, II)**: SINAPI, SICRO, BPS, CMED, ANP. Sao
referenciais oficiais para categorias especificas (obras, saude,
combustiveis).

## Procedimento de 7 Fases

Consulte `reference/procedure.md` para o procedimento operacional
detalhado.

Resumo das fases:

1. **Especificacao**: Identificar objeto, categoria, unidade de medida
2. **Selecao de Fontes**: Aplicar arvore de decisao por categoria
3. **Coleta Praticados**: PNCP, Compras.gov, contratos similares
4. **Coleta Setoriais**: Fonte especifica por categoria
5. **Higienizacao**: Remover outliers, verificar vigencia
6. **Calculo**: Media ou mediana, aplicar BDI se obras
7. **Relatorio**: Gerar documentacao rastreavel

## Arvore de Decisao

Consulte `reference/decision_tree.md` para a arvore visual completa.

Logica simplificada:

- Medicamentos -> BPS + CMED (teto obrigatorio)
- Obras/Engenharia -> SINAPI + SICRO + BDI
- Combustiveis -> ANP
- Bens comuns -> PNCP + Compras.gov
- Saude (insumos) -> BPS + PNCP

## Guardrails Obrigatorios

**Minimo de Fontes**: Apresentar pelo menos 3 fontes comparaveis. Se
nao for possivel obter 3 fontes, justificar e alertar o usuario.

**Teto CMED**: Para medicamentos, o preco CMED e teto obrigatorio. Se o
preco de mercado exceder o CMED, usar o CMED.

**Tratamento de Outliers**: Valores com desvio superior a 30% da
mediana devem ser sinalizados e, se nao justificaveis, removidos do
calculo.

**BDI**: Para obras e servicos de engenharia, aplicar BDI conforme
faixas do Acordao TCU 2622/2013.

**Vigencia**: Precos com mais de 12 meses de referencia devem ser
sinalizados como potencialmente desatualizados.

## Formato de Citacao

Toda fonte utilizada deve ser citada no formato:

`[Fonte: {id} | {nome} | {url} | Verificado: {data}]`

Exemplo:

`[Fonte: PRC-001 | PNCP | https://pncp.gov.br/... | Verificado: 2026-01-31]`

## Checkpoint de Validacao

ANTES de incorporar os precos pesquisados a qualquer documento (ETP,
TR):

1. Apresentar tabela resumo com todas as fontes consultadas
2. Mostrar calculo da media/mediana
3. Listar outliers removidos (se houver) com justificativa
4. Solicitar confirmacao explicita do usuario

Frase de checkpoint: "Pesquisa de precos concluida. Apresento o resumo
para sua validacao antes de prosseguir."

## Uso de Ferramentas MCP

Para consultas as bases de dados:

- Use `procurement-tools:search_pncp` para buscar no PNCP
- Use `procurement-tools:get_sinapi_price` para consultar SINAPI
- Use `procurement-tools:get_bps_price` para consultar Banco de Precos
  Saude
- Use `procurement-tools:check_cmed_ceiling` para verificar teto CMED
- Use `procurement-tools:validate_source` para verificar vigencia de
  fonte
