---
name: pdf-transcription
version: 1.0.0
description: >
  Extract, transcribe, and process long-format PDF documents. Use when
  the user needs to read, search, or convert PDF files from the docs/
  directory. Handles text-based and scanned PDFs with OCR fallback.
  Supports table extraction, markdown conversion, and cross-document
  search. Essential for processing normative documents, SINAPI manuals,
  SUS guides, and PNCP references.
---

# Transcricao e Processamento de PDFs

## Visao Geral

Este Skill processa documentos PDF longos do diretorio `docs/`,
extraindo texto, tabelas e metadados para uso no sistema de
contratacoes publicas. Suporta documentos de ate centenas de paginas
com multiplas estrategias de extracao.

## Ferramentas Disponiveis (MCP Server: pdf-tools)

### list_pdfs

Lista todos os PDFs disponiveis em `docs/`.

Uso: quando o usuario quer saber quais documentos estao disponiveis
ou precisa escolher um arquivo para processar.

### get_pdf_metadata

Extrai metadados (titulo, autor, paginas, hash) sem processar conteudo.

Uso: para verificar rapidamente informacoes sobre um PDF antes de
extrair seu conteudo completo.

### extract_pdf_text

Extrai texto completo de um PDF, com suporte a faixas de paginas.

Parametros:
- `filepath`: caminho do PDF (absoluto ou relativo a `docs/`)
- `page_start`: pagina inicial (1-indexado, opcional)
- `page_end`: pagina final (1-indexado, opcional)

Uso: para ler o conteudo textual de um documento. Resultados sao
cacheados automaticamente em `data/transcriptions/`.

### extract_pdf_tables

Extrai tabelas estruturadas usando pdfplumber.

Uso: para tabelas de precos SINAPI, dados orcamentarios, tabelas
de composicoes SICRO, e outros dados tabulares.

### convert_pdf_to_markdown

Converte PDF completo para Markdown estruturado com cabecalhos,
tabelas formatadas e metadados.

Uso: para criar versoes legiveis de manuais e documentos oficiais
que podem ser referenciados em ETP, TR e pareceres.

### search_pdf_content

Busca texto em um ou todos os PDFs do diretorio.

Parametros:
- `query`: texto a buscar
- `filepath`: PDF especifico (opcional, busca em todos se omitido)
- `case_sensitive`: diferenciar maiusculas/minusculas

Uso: para localizar informacoes especificas em grandes documentos
ou encontrar em qual documento uma referencia esta.

## Estrategias de Extracao

O sistema usa tres estrategias em cascata:

1. **PyMuPDF (primaria)**: Extracao nativa rapida. Funciona com a
   maioria dos PDFs baseados em texto.

2. **pdfplumber (tabelas)**: Motor secundario especializado em
   deteccao e extracao de tabelas estruturadas.

3. **Tesseract OCR (fallback)**: Para paginas escaneadas ou com
   imagens. Requer `tesseract-ocr` e pacote `por` instalados no
   sistema. Ativado automaticamente quando uma pagina tem pouco
   texto mas contem imagens.

## Cache de Transcricoes

Resultados de extracao sao salvos em `data/transcriptions/` como
JSON, indexados por hash SHA-256 do arquivo. Alteracoes no PDF
original invalidam o cache automaticamente.

## Procedimento Recomendado

### Para documentos novos:

1. Use `list_pdfs` para ver arquivos disponiveis
2. Use `get_pdf_metadata` para verificar tamanho e metadados
3. Para documentos pequenos (< 20 paginas): `extract_pdf_text`
4. Para documentos grandes: extraia em faixas de 20-30 paginas
5. Use `extract_pdf_tables` quando houver dados tabulares
6. Use `convert_pdf_to_markdown` para gerar versao referenciavel

### Para busca de informacoes:

1. Use `search_pdf_content` com o termo desejado
2. Identifique o documento e pagina relevante
3. Extraia a faixa de paginas especifica para contexto completo

## Documentos Disponiveis

Consulte `reference/document_catalog.md` para o catalogo completo
dos PDFs com descricoes e categorias.

## Limitacoes

- PDFs protegidos por senha nao sao suportados
- Paginas puramente graficas (diagramas, plantas) nao produzem texto
- Documentos muito grandes (> 100 paginas) devem ser processados em
  faixas para evitar uso excessivo de memoria
- OCR requer Tesseract instalado no sistema (opcional)
