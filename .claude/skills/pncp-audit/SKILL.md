---
name: pncp-audit
version: 1.0.0
description: >
  Audit publications on the National Public Procurement Portal (PNCP),
  verify mandatory publications, check deadline compliance, and monitor
  contracting status. Use when verifying procurement transparency or
  auditing municipal publications.
---

# Auditoria PNCP

## Visao Geral

Este Skill verifica publicacoes no Portal Nacional de Contratacoes
Publicas (PNCP), confere cumprimento de prazos legais e monitora
transparencia das contratacoes do municipio de Extrema-MG.

`[Fonte: BR-FED-0012 | Decreto 11.430/2023 | - | Vigente]`

## Publicacoes Obrigatorias

Conforme Lei 14.133/2021 e Decreto 11.430/2023, o municipio deve
publicar no PNCP:

### Fase de Planejamento

- Plano de Contratacoes Anual (PCA)
- Estudos Tecnicos Preliminares (quando exigido)

### Fase de Selecao

- Edital e seus anexos
- Aviso de licitacao
- Atas de sessao publica
- Resultado de habilitacao
- Resultado de julgamento
- Resultado de recurso
- Homologacao

### Fase Contratual

- Extrato do contrato
- Aditivos contratuais
- Rescisoes
- Atas de registro de precos

### Dispensas e Inexigibilidades

- Aviso de contratacao direta
- Extrato do contrato resultante

## Prazos Legais de Publicacao

| Ato | Prazo para Publicacao |
|---|---|
| Edital | Antes da abertura |
| Extrato de contrato | Ate 20 dias uteis da assinatura |
| Aditivo | Ate 20 dias uteis da assinatura |
| Ata de RP | Ate 20 dias uteis da assinatura |
| Resultado de licitacao | Ate 20 dias uteis da homologacao |

`[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 174 | Vigente]`

## Procedimento de Auditoria

### 1. Consulta ao PNCP

Usar ferramenta MCP `procurement-tools:search_pncp` para buscar
publicacoes do municipio de Extrema-MG.

### 2. Verificacao de Completude

Para cada processo licitatorio:

- Todas as publicacoes obrigatorias foram feitas?
- Ha lacunas na sequencia de publicacoes?
- Documentos anexos estao acessiveis?

### 3. Verificacao de Prazos

Para cada publicacao:

- Foi realizada dentro do prazo legal?
- Prazo minimo entre publicacao do edital e abertura foi respeitado?
- Prazos entre fases foram observados?

### 4. Verificacao de Consistencia

- Valores publicados sao consistentes entre documentos?
- Dados do contrato correspondem ao edital?
- Aditivos estao dentro dos limites legais (25% / 50%)?

### 5. Relatorio

```markdown
## Relatorio de Auditoria PNCP

**Orgao**: Municipio de Extrema-MG
**Periodo**: {data_inicio} a {data_fim}
**Data da Auditoria**: {data}

### Resumo
- Total de processos verificados: {n}
- Processos conformes: {n}
- Processos com pendencias: {n}
- Publicacoes em atraso: {n}

### Pendencias Identificadas
| Processo | Pendencia | Prazo | Status |
|---|---|---|---|

### Recomendacoes
- {Acoes sugeridas para regularizacao}
```

## Ferramentas MCP

- Use `procurement-tools:search_pncp` para consultar publicacoes

## Checkpoint de Validacao

Ao concluir a auditoria:

1. Apresentar relatorio completo
2. Destacar pendencias criticas
3. "Auditoria de publicacoes concluida. Revise as pendencias
   identificadas. Pendencias de publicacao devem ser regularizadas o
   mais breve possivel para evitar apontamentos de orgaos de controle."
