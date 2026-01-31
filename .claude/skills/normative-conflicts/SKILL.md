---
name: normative-conflicts
version: 1.0.0
description: >
  Resolve conflicts between multiple applicable norms in public
  procurement. Use when there is ambiguity about which law, decree, or
  regulation applies, or when norms seem to contradict each other.
  Establishes normative hierarchy and resolution rules.
---

# Resolucao de Conflitos Normativos

## Visao Geral

Este Skill estabelece regras para determinar qual norma se aplica
quando multiplas normas parecem aplicaveis ou quando ha conflito
aparente entre normas. A correta aplicacao da hierarquia normativa e
fundamental para a seguranca juridica das contratacoes.

## Hierarquia Normativa

Consulte `reference/hierarchy.md` para a hierarquia detalhada.

A hierarquia de normas para contratacoes publicas municipais segue
esta ordem (da mais forte para a mais fraca):

1. Constituicao Federal (CF/1988)
2. Leis Federais (Lei 14.133/2021, Lei 8.429/1992)
3. Decretos Federais (Dec. 11.246/2022, Dec. 11.317/2022)
4. Instrucoes Normativas Federais (INs SEGES)
5. Jurisprudencia TCU (Sumulas, Acordaos paradigmaticos)
6. Leis Estaduais MG
7. Decretos Estaduais MG
8. Jurisprudencia TCE-MG
9. Leis Municipais Extrema
10. Decretos Municipais Extrema

## Regras de Resolucao

**Regra 1: Hierarquia Vertical**
Norma de nivel superior prevalece sobre norma de nivel inferior.
Exemplo: Lei Federal prevalece sobre Decreto Municipal.

**Regra 2: Especialidade**
Norma especifica prevalece sobre norma geral, mesmo que de nivel
inferior (desde que nao contrarie norma superior expressa).
Exemplo: IN SEGES sobre pesquisa de precos prevalece sobre disposicao
geral do Decreto regulamentador.

**Regra 3: Temporalidade**
Norma posterior revoga ou modifica norma anterior de mesmo nivel.
Exemplo: Lei 14.133/2021 revogou Lei 8.666/1993 (observada a
transicao).

**Regra 4: Competencia**
Materia de competencia privativa da Uniao nao pode ser regulada por
estado ou municipio de forma divergente.
Exemplo: Modalidades de licitacao sao competencia da Uniao.

## Casos Especiais

### Lei 14.133/2021 vs. Lei 8.666/1993

A Lei 8.666/1993 foi integralmente revogada em 30/12/2023. Processos
iniciados sob o regime anterior seguem aquele regime ate sua conclusao.
Novos processos devem seguir exclusivamente a Lei 14.133/2021.

### Conflito IN SEGES vs. Manual de Orientacao

Instrucoes Normativas tem forca normativa; manuais sao orientativos.
Em caso de conflito, prevalece a IN.

### Jurisprudencia TCU

Sumulas tem efeito vinculante para a Administracao Federal e servem de
orientacao para estados e municipios. Acordaos paradigmaticos devem ser
observados como interpretacao autorizada.

### Decretos Municipais Desatualizados

Decretos municipais que estabelecam valores ou procedimentos
incompativeis com a legislacao federal vigente devem ser interpretados
a luz da norma superior. Na duvida, aplicar a norma federal.

## Procedimento de Analise

Quando houver duvida sobre qual norma aplicar:

1. **Identificar normas candidatas**: Listar todas as normas
   potencialmente aplicaveis
2. **Classificar por nivel**: Ordenar conforme hierarquia
3. **Verificar especialidade**: Identificar se alguma e especifica
   para o caso
4. **Verificar temporalidade**: Confirmar vigencia e data de publicacao
5. **Verificar competencia**: Confirmar que a norma foi editada por
   ente competente
6. **Resolver conflito**: Aplicar regras de resolucao
7. **Fundamentar**: Explicitar o raciocinio no documento

## Formato de Parecer de Conflito

```markdown
## Analise de Conflito Normativo

**Situacao**: {Descrever a situacao que gera duvida}

**Normas em Conflito**:
- Norma A: {Identificacao completa}
- Norma B: {Identificacao completa}

**Analise**:
{Aplicar regras de resolucao, explicando o raciocinio}

**Conclusao**:
Aplica-se a Norma {X} pelos seguintes fundamentos: {justificativa}

**Citacao**: [Fonte: {id} | {norma} | {artigo} | {vigencia}]
```

## Checkpoint de Validacao

Para interpretacoes normativas que possam gerar controversia:

1. Apresentar analise completa ao usuario
2. Explicitar o raciocinio aplicado
3. Alertar: "Esta interpretacao normativa deve ser validada. Em casos
   complexos ou de alto risco, recomenda-se consulta a assessoria
   juridica."
4. Aguardar confirmacao antes de incorporar a conclusao a documentos
   oficiais
