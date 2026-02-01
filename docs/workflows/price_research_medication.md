# Workflow: Pesquisa de Precos para Medicamentos

Pesquisa de precos conforme IN SEGES 65/2021 para aquisicao de
medicamentos para a Rede de Atencao Psicossocial (RAPS) de Extrema.

[Fonte: BR-FED-0015 | IN SEGES/ME 65/2021 | Art. 5 | Vigente]

## Cenario

Aquisicao de Risperidona 2mg comprimido (5.000 unidades) para o
CAPS de Extrema-MG. Necessario pesquisa com minimo de 3 fontes.

[Fonte: BR-FED-0027 | Acordao TCU 2819/2015 | - | Vigente]

## Passo 1: Consultar BPS (Precos Praticados)

```
User: Consulte precos de Risperidona 2mg no BPS.
Claude: [invoca get_bps_price(medicamento="Risperidona 2mg",
         apresentacao="comprimido")]
```

Resultado esperado: resumo estatistico com media, mediana, min/max
de compras publicas recentes.

**Fonte**: PRC-004 (Banco de Precos em Saude)

## Passo 2: Verificar Teto CMED

```
User: Verifique se o preco medio esta dentro do teto CMED.
Claude: [invoca check_cmed_ceiling(medicamento="Risperidona 2mg",
         preco_proposto=0.15)]
```

O preco proposto NAO pode exceder o teto CMED/ANVISA. Se exceder,
deve-se adotar o valor do teto como referencia maxima.

**Fonte**: PRC-005 (CMED/ANVISA)

## Passo 3: Buscar Contratos Similares no PNCP

```
User: Busque contratos de Risperidona no PNCP em MG.
Claude: [invoca search_pncp(termo="Risperidona 2mg comprimido",
         uf="MG", limite=10)]
```

Verificar contratos recentes (ultimos 12 meses) para referencia
de precos efetivamente praticados em licitacoes.

**Fonte**: PRC-001 (PNCP)

## Passo 4: Consolidar Pesquisa

Minimo 3 fontes conforme Art. 5 da IN 65/2021:

| # | Fonte | Tipo | Preco Unit. | Data |
|---|-------|------|-------------|------|
| 1 | BPS | Precos praticados | R$ 0,15 | 2026-01 |
| 2 | CMED | Teto regulatorio | R$ 0,20 | 2026-01 |
| 3 | PNCP | Contratos publicos | R$ 0,14 | 2025-12 |

## Passo 5: Tratamento de Outliers

Calcular media e desvio padrao. Excluir valores que diferem mais
de 2 desvios da media. Recalcular preco de referencia.

## Resultado Final

- Preco de referencia: media das fontes validas
- Valor total estimado: preco_referencia x 5.000 unidades
- Validade: 6 meses a partir da data da pesquisa

**Checkpoint**: Apresentar tabela consolidada ao gestor para
validacao antes de incorporar ao ETP ou TR.
