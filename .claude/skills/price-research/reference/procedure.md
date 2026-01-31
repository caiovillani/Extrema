# Procedimento Operacional de Pesquisa de Precos

## Fase 1: Especificacao do Objeto

Antes de iniciar a pesquisa, defina com precisao:

- **Descricao do objeto**: O que esta sendo adquirido/contratado
- **Categoria**: Bens comuns, servicos, obras, saude, combustiveis
- **Unidade de medida**: Unidade, metro quadrado, litro, comprimido, etc.
- **Quantidade estimada**: Volume da contratacao
- **Especificacoes tecnicas**: Requisitos minimos obrigatorios

Perguntas-chave:

1. O objeto pode ser descrito por especificacoes padronizadas?
2. Ha exigencias tecnicas que limitem fornecedores?
3. O quantitativo justifica economia de escala?

## Fase 2: Selecao de Fontes

Aplique a arvore de decisao (ver `decision_tree.md`) para determinar
quais fontes consultar com base na categoria do objeto.

Regras gerais:

- SEMPRE consultar pelo menos uma fonte de precos praticados (PNCP ou
  Compras.gov)
- Para categorias com fonte setorial obrigatoria (SINAPI, CMED, ANP),
  SEMPRE inclui-la
- Minimo de 3 fontes comparaveis para o calculo final

## Fase 3: Coleta de Precos Praticados

### 3.1 Consulta ao PNCP

1. Buscar por termos descritivos do objeto
2. Filtrar por data (preferencialmente ultimos 12 meses)
3. Filtrar por regiao se relevante (mesma UF ou regiao)
4. Registrar: contrato, orgao, valor unitario, data, vigencia

### 3.2 Consulta ao Compras.gov

1. Buscar atas de SRP vigentes para o objeto
2. Verificar se ha adesao (carona) disponivel
3. Registrar: ata, orgao gerenciador, valor unitario, vigencia

### 3.3 Consulta a Contratos Similares

1. Buscar no PNCP contratos de municipios de porte similar
2. Filtrar por objetos comparaveis
3. Registrar mesmos dados dos itens anteriores

## Fase 4: Coleta de Precos Setoriais

### 4.1 Para Obras e Engenharia

1. Identificar composicoes SINAPI aplicaveis
2. Usar tabela do estado de MG, mes de referencia mais recente
3. Selecionar tabela desonerada ou nao conforme regime tributario
4. Aplicar BDI conforme Acordao TCU 2622/2013

### 4.2 Para Medicamentos

1. Consultar BPS para precos praticados
2. Consultar CMED para preco maximo (PMVG)
3. CMED e teto obrigatorio: se media exceder CMED, usar CMED

### 4.3 Para Combustiveis

1. Consultar levantamento semanal da ANP
2. Usar dados do municipio de Extrema-MG ou regiao proxima
3. Considerar media das ultimas 4 semanas

## Fase 5: Higienizacao dos Dados

### 5.1 Verificacao de Vigencia

- Descartar precos com mais de 12 meses sem justificativa
- Sinalizar precos com mais de 6 meses para atencao

### 5.2 Deteccao de Outliers

1. Calcular mediana dos precos coletados
2. Calcular desvio percentual de cada preco em relacao a mediana
3. Sinalizar valores com desvio > 30%
4. Outliers podem ser removidos se nao houver justificativa

### 5.3 Compatibilizacao

- Garantir que todos os precos estao na mesma unidade de medida
- Ajustar para mesma base temporal quando possivel
- Considerar custos de frete/logistica quando relevante

## Fase 6: Calculo do Preco Referencial

### 6.1 Metodo de Calculo

- **Mediana**: Preferivel quando ha dispersao significativa
- **Media**: Aceitavel quando precos sao homogeneos (desvio < 20%)
- **Menor preco**: Apenas se justificado e com pelo menos 3 fontes

### 6.2 Aplicacao de BDI (Obras)

Para obras e servicos de engenharia, aplicar BDI conforme faixas do
Acordao TCU 2622/2013:

| Tipo de Obra | BDI Minimo | BDI Medio | BDI Maximo |
|---|---|---|---|
| Construcao de edificios | 20,34% | 22,12% | 25,00% |
| Construcao de rodovias | 18,58% | 20,97% | 24,23% |
| Reformas de edificios | 20,34% | 22,12% | 25,00% |
| Manutencao de edificios | 20,34% | 22,12% | 25,00% |
| Fornecimento de materiais | 11,11% | 14,02% | 18,45% |

### 6.3 Formula

```
Preco Referencial = Mediana (ou Media) dos precos higienizados
Valor Total = Preco Referencial x Quantidade
Para obras: Valor Total = (Soma composicoes SINAPI) x (1 + BDI)
```

## Fase 7: Relatorio e Documentacao

O relatorio de pesquisa de precos deve conter:

1. **Identificacao do objeto**: Descricao completa
2. **Metodologia**: Fontes consultadas e criterios de selecao
3. **Dados coletados**: Tabela com todas as fontes e precos
4. **Tratamento**: Outliers removidos com justificativa
5. **Calculo**: Metodo utilizado e resultado
6. **Preco referencial**: Valor unitario e total
7. **Citacoes**: Todas as fontes no formato padrao
8. **Data da pesquisa**: Para referencia de vigencia
