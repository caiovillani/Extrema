---
name: budget-analysis
version: 1.0.0
description: >
  Validate construction budgets against SINAPI and SICRO references,
  check BDI compliance with TCU guidelines, detect overpricing and
  "jogo de planilha". Use when reviewing budget proposals for
  construction works or engineering services.
---

# Analise Orcamentaria

## Visao Geral

Este Skill analisa orcamentos de obras e servicos de engenharia,
verificando conformidade com referencias oficiais (SINAPI, SICRO) e
diretrizes do TCU para BDI. Detecta sobrepreco, jogo de planilha e
inconsistencias.

## Procedimento de Analise

### Fase 1: Verificacao de Composicoes

1. Identificar cada item/composicao do orcamento
2. Localizar composicao SINAPI ou SICRO correspondente
3. Comparar preco unitario do orcamento com referencia oficial
4. Calcular desvio percentual por item

Criterios de desvio:

- Ate 10% acima da referencia: Aceitavel
- De 10% a 30% acima: Requer justificativa tecnica
- Acima de 30%: Indicio de sobrepreco

### Fase 2: Verificacao de BDI

Conferir BDI conforme faixas do Acordao TCU 2622/2013:

| Tipo de Obra | 1o Quartil | Medio | 3o Quartil |
|---|---|---|---|
| Construcao de edificios | 20,34% | 22,12% | 25,00% |
| Construcao de rodovias | 18,58% | 20,97% | 24,23% |
| Reformas de edificios | 20,34% | 22,12% | 25,00% |
| Construcao de redes | 18,36% | 21,27% | 24,18% |
| Fornecimento de materiais | 11,11% | 14,02% | 18,45% |
| Fornecimento de equipamentos | 11,11% | 14,02% | 18,45% |

`[Fonte: BR-FED-0026 | Acordao TCU 2622/2013 | - | Vigente]`

Componentes do BDI a verificar:

- Administracao central
- Seguros e garantias
- Riscos
- Despesas financeiras
- Lucro
- Tributos (PIS, COFINS, ISS)

### Fase 3: Deteccao de Jogo de Planilha

Verificar se ha manipulacao de quantitativos para favorecer itens com
sobrepreco:

1. Comparar quantitativos do orcamento com memorial de calculo
2. Verificar se itens com preco acima da referencia tem quantitativos
   inflados
3. Verificar se itens com preco abaixo da referencia tem quantitativos
   reduzidos
4. Calcular impacto financeiro do remanejamento

Indicadores de alerta:

- Itens com desvio > 30% E quantitativo significativo
- Inversao sistematica: itens caros com mais quantidade, baratos com
  menos
- Diferenca significativa entre valor global do orcamento e soma
  SINAPI

### Fase 4: Verificacao de Encargos Sociais

- Conferir percentual de encargos sociais aplicado
- Verificar se e compativel com o regime de desoneracão adotado
- Comparar com tabela de encargos SINAPI do estado

### Fase 5: Analise Global

1. Calcular valor global pela referencia SINAPI/SICRO + BDI
2. Comparar com valor global do orcamento analisado
3. Calcular sobrepreco/subpreco global
4. Emitir parecer

## Formato de Relatorio

```markdown
## Relatorio de Analise Orcamentaria

**Obra**: {descricao}
**Orcamento analisado**: {referencia}
**Base de referencia**: SINAPI {estado} {mes/ano}
**BDI adotado**: {percentual}

### Resumo
- Valor do orcamento: R$ {valor}
- Valor referencial: R$ {valor}
- Diferenca: R$ {valor} ({percentual}%)
- Parecer: {CONFORME / SOBREPRECO / SUBPRECO}

### Itens com Desvio Significativo
| Item | Orcamento | Referencia | Desvio |
|---|---|---|---|

### BDI
- BDI adotado: {valor}%
- BDI referencia TCU: {faixa}%
- Situacao: {CONFORME / ACIMA / ABAIXO}

### Conclusao
{Parecer sobre o orcamento}
```

## Ferramentas MCP

- Use `procurement-tools:get_sinapi_price` para consultar composicoes
- Use `procurement-tools:validate_source` para verificar vigencia

## Checkpoint de Validacao

Ao concluir a analise:

1. Apresentar relatorio completo
2. Destacar itens com sobrepreco
3. "Analise orcamentaria concluida. Revise os apontamentos. Para
   decisoes sobre aprovacao ou reprovacao do orcamento, recomenda-se
   validacao por engenheiro responsavel."
