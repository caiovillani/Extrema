# Workflow: Geracao de ETP para Obras RAPS

Elaboracao de Estudo Tecnico Preliminar para obra de construcao
de unidade da Rede de Atencao Psicossocial em Extrema-MG.

[Fonte: BR-FED-0016 | IN SEGES/ME 73/2022 | Art. 7 | Vigente]

## Cenario

Construcao de CAPS I em Extrema. Necessario ETP conforme Art. 18
da Lei 14.133/2021 com orcamento baseado em SINAPI e BDI conforme
Acordao TCU 2622/2013.

[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 18 | Vigente]

## Passo 1: Definir Necessidade

Descricao da necessidade de construcao de unidade CAPS I conforme
Plano Municipal de Saude.

[Fonte: MG-EXT-0002 | Plano Municipal de Saude 2022-2025 | - | Vigente]

## Passo 2: Pesquisar Precos SINAPI

```
User: Consulte o preco SINAPI para pintura latex PVA (87529).
Claude: [invoca get_sinapi_price(codigo="87529", estado="MG")]
```

Para cada item do orcamento, consultar composicao SINAPI:

```
User: Busque composicoes SINAPI para "alvenaria".
Claude: [invoca search_sinapi(termo="alvenaria", estado="MG")]
```

**Fonte**: PRC-003 (SINAPI)

## Passo 3: Aplicar BDI

Faixas de BDI conforme Acordao TCU 2622/2013:

| Tipo | 1o Quartil | Mediana | 3o Quartil |
|------|-----------|---------|-----------|
| Edificacoes | 20,34% | 22,12% | 25,00% |
| Reforma | 18,28% | 20,60% | 23,44% |

[Fonte: BR-FED-0026 | Acordao TCU 2622/2013 | - | Vigente]

## Passo 4: Gerar ETP

O sistema gera o ETP usando o template em
`.claude/skills/document-generation/templates/etp_template.md`
preenchendo as secoes obrigatorias:

1. Descricao da Necessidade
2. Requisitos da Contratacao
3. Estimativa de Quantidades e Valor
4. Justificativa da Solucao
5. Contratacoes Correlatas
6. Impactos Ambientais

## Passo 5: Validacao Automatica

O hook `validate_document.py` verifica automaticamente:
- Presenca de todas as secoes obrigatorias
- Existencia de pelo menos uma citacao normativa
- Presenca de valores monetarios na estimativa

## Passo 6: Checkpoint Humano

**OBRIGATORIO**: O documento e apresentado ao gestor para revisao.
O sistema aguarda confirmacao explicita ("confirmo" ou "sim")
antes de salvar a versao final.

## Resultado Final

- ETP salvo em `output/etp/` com metadados YAML
- Citacoes rastreavies para todas as fundamentacoes
- Orcamento detalhado com referencia SINAPI/BDI
