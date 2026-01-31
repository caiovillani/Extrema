# Arquitetura do Sistema de Contratacoes Publicas

## Visao Geral

Sistema de apoio a gestao de contratacoes publicas municipais,
construido sobre Claude Code CLI com arquitetura
"AI + Human on the Loop".

## Tres Camadas

### Camada de Configuracao

Define o contexto operacional do sistema.

- `CLAUDE.md`: contexto geral, regras inegociaveis, fontes normativas
- `.claude/settings.json`: permissoes, hooks, variaveis de ambiente
- `.mcp.json`: declaracao de MCP servers (ferramentas externas)

### Camada de Capacidades (Skills)

Define o que o sistema sabe fazer.

| Skill | Diretorio | Funcao |
|---|---|---|
| price-research | `.claude/skills/price-research/` | Pesquisa de precos IN 65/2021 |
| document-generation | `.claude/skills/document-generation/` | Geracao de ETP, TR, Parecer |
| bid-analysis | `.claude/skills/bid-analysis/` | Analise de editais |
| budget-analysis | `.claude/skills/budget-analysis/` | Validacao orcamentaria |
| pncp-audit | `.claude/skills/pncp-audit/` | Auditoria de publicacoes |
| normative-conflicts | `.claude/skills/normative-conflicts/` | Conflitos normativos |

### Camada de Execucao

Onde o trabalho acontece: consulta configuracao, identifica Skills,
conecta MCP servers, gera respostas com checkpoints de validacao.

## Modelo de Seguranca

### Tres Linhas de Defesa

1. **Instrucoes Declarativas**: Regras em CLAUDE.md e SKILL.md que o
   modelo segue por design
2. **Scripts de Validacao**: Codigo deterministico que verifica
   citacoes, estrutura e conformidade
3. **Hooks de Interceptacao**: Ultima linha, intercepta acoes criticas
   e exige validacao

### Checkpoints Obrigatorios

- Pesquisa de precos: apresentar fontes antes de incorporar a
  documentos
- Documentos tecnicos: apresentar rascunho completo antes de salvar
- Interpretacoes normativas: alertar sobre necessidade de validacao
  juridica

## Fluxo de Dados

```
Usuario -> Claude Code -> Skill identificado -> MCP Server (se necessario)
                                             -> Hook de validacao
                                             -> Resposta ao usuario
                                             -> Checkpoint humano
                                             -> Salvamento (se aprovado)
```

## Fontes de Dados

### Normativas (`sources/sources_log.jsonl`)

Registro de todas as fontes normativas com metadados de vigencia.
Cada entrada possui id unico, status e data de verificacao.

### Precos (`sources/price_sources_log.jsonl`)

Registro das fontes de precos autorizadas para pesquisa conforme
IN SEGES 65/2021.

### Hierarquia (`sources/normative_hierarchy.md`)

Ordem de precedencia das normas aplicaveis a contratacoes
municipais.

## Ferramentas Externas (MCP)

O MCP server `procurement-tools` expoe:

- `validate_source`: verifica vigencia de fonte
- `search_pncp`: busca contratos no PNCP
- `get_sinapi_price`: consulta SINAPI
- `get_bps_price`: consulta Banco de Precos Saude
- `check_cmed_ceiling`: verifica teto CMED
- `get_anp_price`: consulta precos ANP

Todas as ferramentas retornam dados simulados na versao atual.
Integracoes reais devem ser implementadas nos clientes
(`tools/pncp_client.py`, `tools/sinapi_client.py`,
`tools/bps_client.py`).

## Documentos Gerados

Salvos em `output/` com metadados YAML de rastreabilidade:

- `output/etp/`: Estudos Tecnicos Preliminares
- `output/tr/`: Termos de Referencia
- `output/pareceres/`: Pareceres Tecnicos
