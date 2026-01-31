---
name: document-generation
version: 1.0.0
description: >
  Generate technical documents for public procurement processes
  including Preliminary Technical Study (ETP), Terms of Reference (TR),
  and technical opinions. Use when the user needs to create or draft
  bidding documents following Law 14.133/2021 requirements.
---

# Geracao de Documentos Tecnicos

## Visao Geral

Este Skill gera documentos tecnicos padronizados para processos
licitatorios conforme Lei n. 14.133/2021. Os documentos sao gerados
como rascunhos que REQUEREM validacao humana antes de serem considerados
finalizados.

## Documentos Suportados

**Estudo Tecnico Preliminar (ETP)**: Documento que fundamenta a
necessidade da contratacao e define requisitos. Obrigatorio conforme
Art. 18 da Lei 14.133/2021. Template em `templates/etp_template.md`.

**Termo de Referencia (TR)**: Documento que especifica o objeto da
contratacao. Conforme Art. 6, XXIII da Lei 14.133/2021. Template em
`templates/tr_template.md`.

**Parecer Tecnico**: Manifestacao tecnica sobre situacoes especificas
(aditivos, impugnacoes, recursos). Template em
`templates/parecer_template.md`.

## Fluxo de Geracao

1. **Identificar Tipo**: Determinar qual documento e necessario
2. **Coletar Insumos**: Obter dados necessarios (precos via Skill
   price-research)
3. **Selecionar Template**: Carregar template apropriado
4. **Preencher Campos**: Inserir dados nos campos do template
5. **Adicionar Fundamentacao**: Incluir base legal e citacoes
6. **Revisar Completude**: Verificar todos os campos obrigatorios
7. **Apresentar para Validacao**: Mostrar documento e aguardar aprovacao

## Integracao com Outros Skills

Para dados de precos, invocar o Skill `price-research`:
"Antes de preencher a secao de estimativa de custos, preciso realizar
pesquisa de precos."

Para verificar hierarquia normativa, consultar Skill
`normative-conflicts`:
"Verificando qual norma se aplica a este caso."

## Campos Obrigatorios por Documento

### ETP deve conter

- Descricao da necessidade
- Requisitos da contratacao
- Estimativa de quantidades
- Estimativa de valor (com fontes)
- Justificativa da solucao escolhida
- Analise de riscos

### TR deve conter

- Objeto da contratacao (descricao detalhada)
- Fundamentacao legal
- Descricao da solucao
- Requisitos tecnicos
- Modelo de execucao
- Criterios de medicao e pagamento
- Estimativa de precos (com metodologia)

### Parecer deve conter

- Identificacao do processo
- Questao analisada
- Fundamentacao tecnica e legal
- Conclusao e recomendacao

## Formato de Saida

Documentos sao salvos em Markdown no diretorio `output/`:

- ETPs: `output/etp/ETP_{objeto}_{data}.etp.md`
- TRs: `output/tr/TR_{objeto}_{data}.tr.md`
- Pareceres: `output/pareceres/PAR_{assunto}_{data}.md`

## Metadados de Rastreabilidade

Todo documento gerado deve incluir header YAML com metadados:

```yaml
---
documento: ETP
objeto: Descricao do objeto
data_geracao: 2026-01-31T14:30:00-03:00
versao: rascunho-v1
gerado_por: Sistema de Contratacoes + Validacao Humana
skill_utilizado: document-generation
fontes_consultadas:
  - PRC-001 (PNCP)
checkpoints_validacao:
  - pesquisa_precos: confirmado em YYYY-MM-DDTHH:MM:SS
  - documento_final: pendente
---
```

## Checkpoint de Validacao OBRIGATORIO

Antes de salvar qualquer documento finalizado:

1. Apresentar o documento completo ao usuario
2. Destacar campos que requerem atencao especial
3. Listar todas as fontes citadas
4. Usar a frase: "Documento rascunhado. Por favor, revise o conteudo.
   Confirma salvamento da versao final?"
5. AGUARDAR confirmacao explicita ("sim", "confirmo", "pode salvar")
6. Somente apos confirmacao, salvar o arquivo

NUNCA salvar documento finalizado sem confirmacao explicita do usuario.
