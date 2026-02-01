# Workflow: Validacao Orcamentaria SINAPI/SICRO

Analise e validacao de proposta orcamentaria para obras publicas
comparando com referenciais SINAPI e SICRO.

[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 23 | Vigente]

## Cenario

Recebimento de proposta orcamentaria para obra de infraestrutura
viaria vinculada ao CAPS de Extrema. Necessario validar cada item
contra SINAPI (edificacoes) e SICRO (infraestrutura de transportes).

## Passo 1: Verificar Composicoes SINAPI

Para cada item de edificacao no orcamento:

```
User: Consulte SINAPI para composicao 87529.
Claude: [invoca get_sinapi_price(codigo="87529", estado="MG")]
```

Comparar preco proposto vs. preco SINAPI. Criterios de desvio:

| Desvio | Classificacao | Acao |
|--------|---------------|------|
| <= 10% | Aceitavel | Aprovado |
| 10-30% | Atencao | Requer justificativa |
| > 30% | Red flag | Requer parecer tecnico |

## Passo 2: Verificar Composicoes SICRO

Para itens de infraestrutura rodoviaria:

```
User: Busque SICRO para "escavacao mecanica".
Claude: [invoca search_sicro(termo="escavacao mecanica",
         estado="MG")]
```

```
User: Consulte SICRO para composicao 5914242.
Claude: [invoca get_sicro_price(codigo="5914242", estado="MG")]
```

**Fonte**: PRC-006 (SICRO/DNIT)

## Passo 3: Verificar BDI

Comparar BDI proposto com faixas do Acordao TCU 2622/2013:

```
User: O BDI proposto e 28%. Esta dentro das faixas TCU?
Claude: Verifica contra faixas de referencia.
        Para edificacoes, o 3o quartil e 25,00%.
        BDI de 28% EXCEDE o limite superior.
```

[Fonte: BR-FED-0026 | Acordao TCU 2622/2013 | - | Vigente]

## Passo 4: Detectar Jogo de Planilha

Verificar se ha itens com quantidades subdimensionadas e precos
unitarios elevados (ou vice-versa). Indicadores:

- Item com preco > 30% acima do SINAPI e quantidade relevante
- Item com preco < 30% abaixo do SINAPI e quantidade pequena
- Inversao sistematica: itens iniciais caros, finais baratos

## Passo 5: Gerar Relatorio

Resultado consolidado com:

| Item | Codigo | Proposto | SINAPI/SICRO | Desvio | Status |
|------|--------|----------|-------------|--------|--------|
| Pintura | 87529 | R$ 14,00 | R$ 12,50 | +12% | Atencao |
| Escavacao | 5914242 | R$ 8,00 | R$ 8,45 | -5% | OK |

## Resultado Final

- Parecer com classificacao: Aprovado / Aprovado com ressalvas / Reprovado
- Lista de itens com desvio > 10% para justificativa
- Recomendacao de ajuste se BDI fora das faixas TCU
