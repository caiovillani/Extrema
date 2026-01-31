---
name: bid-analysis
version: 1.0.0
description: >
  Analyze bidding documents (editais) for compliance with Law
  14.133/2021 and identify potential red flags such as restrictive
  specifications, unreasonable deadlines, or disproportionate
  requirements. Use when reviewing or auditing procurement notices.
---

# Analise de Editais

## Visao Geral

Este Skill analisa editais de licitacao quanto a conformidade com a Lei
14.133/2021, identifica red flags e verifica elementos obrigatorios.
A analise e orientativa e NAO substitui parecer juridico formal.

## Procedimento de Analise

### Fase 1: Verificacao de Elementos Obrigatorios

Verificar presenca de todos os elementos exigidos pelo Art. 25 da Lei
14.133/2021:

- Objeto da licitacao (descricao clara e precisa)
- Modalidade e criterio de julgamento
- Requisitos de habilitacao
- Criterios de aceitabilidade de precos
- Prazos e condicoes
- Sancoes administrativas
- Condicoes de pagamento

`[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 25 | Vigente]`

### Fase 2: Analise de Restricoes Indevidas

Verificar conformidade com Sumula TCU 247 (descricao objetiva sem
restricoes indevidas):

- Especificacoes direcionam para marca ou fornecedor especifico?
- Requisitos de habilitacao sao proporcionais ao objeto?
- Prazos sao exequiveis?
- Ha exigencia de amostras ou visita tecnica desnecessarias?
- Atestados de capacidade tecnica sao proporcionais?

`[Fonte: BR-FED-0025 | Sumula TCU 247 | - | Vigente]`

### Fase 3: Verificacao de Precos

- Valor estimado esta coerente com pesquisa de precos?
- Ha sigilo do orcamento quando exigido?
- Criterio de aceitabilidade de precos e razoavel?

### Fase 4: Verificacao de Publicacoes

- Publicacao no PNCP conforme prazos legais?
- Prazo minimo entre publicacao e abertura respeitado?
- Aviso publicado nos meios obrigatorios?

### Fase 5: Emissao de Parecer

Consulte `checklists/conformidade_14133.md` para checklist detalhado.

## Red Flags Comuns

1. **Especificacao direcionada**: Descricao que so pode ser atendida
   por um fornecedor
2. **Prazo inexequivel**: Prazo de entrega ou execucao incompativel com
   o mercado
3. **Atestado desproporcional**: Exigencia de atestado superior a 50%
   do quantitativo
4. **Habilitacao excessiva**: Requisitos financeiros ou tecnicos
   desproporcionais ao objeto
5. **Agrupamento inadequado**: Lotes agrupados de forma a restringir
   competicao
6. **Valor incompativel**: Orcamento significativamente acima ou abaixo
   do mercado
7. **Ausencia de parcelamento**: Nao justificativa para nao
   parcelamento do objeto
8. **Clausulas restritivas**: Condicoes que limitam indevidamente a
   participacao

## Formato de Relatorio

```markdown
## Relatorio de Analise de Edital

**Processo**: {numero}
**Orgao**: {orgao}
**Objeto**: {objeto}
**Modalidade**: {modalidade}
**Data da Analise**: {data}

### Conformidade
- [x] ou [ ] para cada item do checklist

### Red Flags Identificadas
- {Descricao de cada red flag com fundamentacao}

### Recomendacoes
- {Acoes sugeridas}

### Conclusao
{Parecer resumido sobre o edital}
```

## Checkpoint de Validacao

Ao concluir a analise:

1. Apresentar relatorio completo ao usuario
2. Destacar red flags identificadas
3. "Analise de edital concluida. Revise as observacoes antes de tomar
   qualquer providencia. Em caso de duvida juridica, consulte a
   assessoria competente."
