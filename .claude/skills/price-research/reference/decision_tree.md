# Arvore de Decisao -- Selecao de Fontes por Categoria

## Fluxo de Decisao

```
OBJETO DA CONTRATACAO
|
+-- E medicamento ou insumo farmaceutico?
|   |
|   +-- SIM --> BPS (PRC-004) + CMED teto (PRC-005) + PNCP (PRC-001)
|   |           Nota: CMED e teto obrigatorio
|   |
|   +-- NAO --> Proximo
|
+-- E obra ou servico de engenharia?
|   |
|   +-- SIM --> SINAPI (PRC-003) + BDI TCU
|   |   |
|   |   +-- E infraestrutura rodoviaria?
|   |   |   +-- SIM --> Adicionar SICRO (PRC-006)
|   |   |   +-- NAO --> Apenas SINAPI
|   |   |
|   |   +-- Complementar com PNCP (PRC-001) para contratos similares
|   |
|   +-- NAO --> Proximo
|
+-- E combustivel?
|   |
|   +-- SIM --> ANP (PRC-007) + PNCP (PRC-001)
|   |           Nota: Usar dados do municipio de Extrema ou regiao
|   |
|   +-- NAO --> Proximo
|
+-- E insumo de saude (nao medicamento)?
|   |
|   +-- SIM --> BPS (PRC-004) + PNCP (PRC-001) + Compras.gov (PRC-002)
|   |
|   +-- NAO --> Proximo
|
+-- E bem comum ou servico geral?
    |
    +-- PNCP (PRC-001) + Compras.gov (PRC-002)
    +-- Complementar com Painel de Precos (PRC-010)
    +-- Se insuficiente: Cotacao Direta (PRC-009) com min. 3 orcamentos
```

## Regras de Complementacao

### Quando 3 fontes nao sao alcancadas

Se as fontes primarias da categoria nao gerarem 3 resultados
comparaveis:

1. Expandir busca no PNCP para contratos de outros estados
2. Consultar Portal de Compras MG (PRC-008)
3. Buscar contratos de municipios de porte similar (PRC-011)
4. Em ultimo caso: Cotacao Direta com fornecedores (PRC-009)

### Quando nenhuma fonte retorna resultado

1. Verificar se a descricao do objeto esta muito especifica
2. Tentar termos alternativos ou mais genericos
3. Documentar a impossibilidade e justificar uso de fontes
   alternativas
4. Alertar o usuario sobre a limitacao

## Prioridade de Fontes por Confiabilidade

1. Tabelas oficiais (SINAPI, SICRO, CMED, ANP) -- maxima
   confiabilidade
2. PNCP e Compras.gov -- alta confiabilidade (precos efetivos)
3. BPS e Painel de Precos -- alta confiabilidade (agregadores oficiais)
4. Portal de Compras MG -- media confiabilidade (estadual)
5. Contratos similares -- media confiabilidade (requer validacao)
6. Cotacao direta -- confiabilidade variavel (requer triangulacao)
