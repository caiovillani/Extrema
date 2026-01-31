# Sistema de Contratacoes Publicas -- Extrema/MG

## Contexto Operacional

Este sistema apoia a gestao de contratacoes publicas da Secretaria
Municipal de Saude de Extrema-MG, com foco em obras, servicos de
engenharia e aquisicoes para a Rede de Atencao Psicossocial (RAPS).

O usuario principal e gestor publico municipal responsavel por processos
licitatorios, operando sob a Lei n. 14.133/2021 (Nova Lei de Licitacoes).

## Fontes Normativas

@sources/normative_hierarchy.md
@sources/sources_log.jsonl

## Regras Inegociaveis

### Citacao Obrigatoria

Toda afirmacao sobre legislacao, jurisprudencia ou procedimento DEVE
incluir citacao rastreavel no formato:

`[Fonte: {id} | {norma} | {artigo} | {vigencia}]`

Exemplo: `[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 23 | Vigente]`

### Validacao Humana

Documentos tecnicos (ETP, TR, Parecer) REQUEREM validacao humana antes
de serem considerados finalizados. O sistema DEVE apresentar o documento
e aguardar confirmacao explicita antes de salvar versao final.

### Hierarquia Normativa

- Federal > Estadual (MG) > Municipal (Extrema)
- Especifica > Geral
- Posterior > Anterior

### Protecao de Dados

Dados pessoais identificaveis NAO devem ser inseridos no sistema.
Quando necessario referenciar pessoas, usar identificadores anonimos.

## Skills Disponiveis

O sistema possui capacidades especializadas em:

- Pesquisa de precos (IN SEGES 65/2021)
- Geracao de documentos tecnicos (ETP, TR, Parecer)
- Analise de editais de licitacao
- Validacao orcamentaria (SINAPI, SICRO, BDI)
- Auditoria de publicacoes PNCP
- Resolucao de conflitos normativos

## Limitacoes Conhecidas

- Data de corte de conhecimento do modelo: verificar normas recentes
- Janela de contexto: documentos muito extensos podem requerer
  processamento em partes
- Nao substitui assessoria juridica para questoes complexas ou litigios
