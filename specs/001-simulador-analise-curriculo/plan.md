# Implementation Plan: Simulador de Análise de Currículo

**Branch**: `001-simulador-analise-curriculo` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-simulador-analise-curriculo/spec.md`

## Summary

Um app web em Python com Streamlit em que a pessoa candidata cola ou envia (PDF) o currículo, cola a
vaga e recebe uma pontuação global (N/100), notas por categoria (Design, Estrutura, Conteúdo) e, para
cada requisito da vaga, um status com evidência e dedução lógica explicada. O texto original está em
português do Brasil, com tradução opcional para inglês e espanhol por bandeirinhas.

Abordagem técnica (detalhes em [research.md](research.md)):

- **O LLM faz só o que exige semântica**: extrair os requisitos da vaga e julgar cada requisito contra o
  currículo (status, trechos de evidência, tipo de dedução, certeza, justificativa). Toda resposta vem
  em JSON validado por esquema.
- **Toda a pontuação é feita em código determinístico**, a partir desses vereditos e de regras
  publicadas na tela (a rubrica). Estrutura e Design também são calculados por código (detecção de
  seções e métricas do PDF), sem LLM.
- **Evidências são conferidas em código**: um trecho citado que não existe literalmente no currículo é
  descartado, e o requisito passa a "sem evidência verificada".
- **PDF**: PyMuPDF extrai texto e métricas de layout. Textos longos passam por *chunking* por seções
  com sobreposição, e os vereditos por trecho são reunidos por uma regra determinística.
- **Visual**: CSS injetado, fonte Tropi Land servida pelo Streamlit, corações em SVG e a barra
  segmentada em HTML/CSS. Escolhi HTML/CSS em vez de Altair porque dá controle total do gradiente e da
  acessibilidade (`role="progressbar"`).
- **Idiomas**: textos da interface em arquivos por idioma. As justificativas nascem sempre em português
  do Brasil e são traduzidas sob demanda por uma chamada separada, guardada na sessão, sem refazer a
  análise e sem mudar nota ou status.

## Technical Context

**Language/Version**: Python 3.11+ (a instalação foi verificada em Python 3.14.4)

**Primary Dependencies**: `streamlit` 1.64, `pymupdf` 1.28, `google-genai` 2.x (SDK oficial do Gemini), `pydantic` 2.x. Desenvolvimento: `pytest` 9

**Storage**: N/A. Nada é gravado em disco ou banco. Currículo, vaga e resultado vivem só em `st.session_state`, na memória da sessão.

**Testing**: `pytest`, `streamlit.testing.v1.AppTest` para os fluxos de tela, e um cliente de LLM falso (*fake*) com respostas gravadas para testes sem rede e sem custo

**Target Platform**: aplicação web local, aberta em navegador moderno (Linux, macOS e Windows)

**Project Type**: web app em um único projeto Streamlit (sem backend separado)

**Performance Goals**: extração de um PDF de até 10 páginas em menos de 3 s; análise completa (extração de requisitos + julgamento) em geral em menos de 60 s; troca de idioma já traduzido em menos de 1 s e, quando exige tradução nova, em menos de 15 s

**Constraints**: sem persistência dos dados da pessoa; chave de API só por variável de ambiente ou `st.secrets`, nunca no código nem no repositório; temperatura 0 e semente fixa nas chamadas ao modelo, para reduzir a variação; todo texto visível em três idiomas

**Scale/Scope**: uso individual e local, em trabalho acadêmico. Uma página com três estágios (entrada, análise, resultado), sem conta de usuário nem histórico

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constituição v1.2.0 (`.specify/memory/constitution.md`).

| Regra | Como o plano atende | Situação |
|---|---|---|
| I. Transparência Algorítmica: nada de caixa-preta, critérios e pesos visíveis | Rubrica publicada na tela (pesos das categorias, créditos por status, critérios de Estrutura e Design). Pontuação só em código, a partir de vereditos visíveis. | Atende |
| I. Reprodutibilidade em três regras (v1.2.0) | (1) Nota calculada só por código, a partir dos vereditos e da rubrica. (2) Repetir a análise na mesma sessão devolve o resultado guardado em `st.session_state`, sem nova chamada. (3) A variação dos vereditos do LLM entre sessões é medida por um teste com chave real e informada, e nada é guardado em disco. | Atende |
| II. Explicabilidade: status, trecho, dedução e "sem evidência" explícito | `Verdict` guarda status, trechos, tipo de dedução, certeza e justificativa. Trechos são verificados por código. Requisitos sem evidência aparecem como tal. | Atende |
| II. Nota agregada decomponível | `ScoreBreakdown` liga global → categorias → requisitos, e a tela mostra essa cadeia. | Atende |
| III. Paleta em rosa e roxo, cores em conjunto central de variáveis | `src/ats/ui/tokens.py` é a única fonte das cores. Um teste falha se o CSS tiver cor fora dos tokens. | Atende |
| III. Exceção 1: gradiente de uma cor de acento só na barra, com valor numérico e justificativa | Barra segmentada em turquesa (claro → intenso), só em `components/score_bar.py`, sempre com número e texto. | Atende |
| III. Exceção 2: bandeiras com cores próprias e nome acessível | Seletor com BR, US e ES, texto do idioma sempre visível e indicação de ativa que não depende de cor. | Atende |
| IV. Estética fofa, decoração que não compete com a informação | Corações em SVG de fundo e de borda (`aria-hidden`), cantos arredondados, textos gentis nas três línguas. | Atende |
| Restrições: pt-BR original, tradução opcional sem mudar o resultado | Análise sempre em pt-BR. A tradução só reescreve os textos explicativos e os trechos de evidência ficam intactos. Teste garante notas e status iguais nos três idiomas. | Atende |
| Restrições: elementos decorativos ignorados por leitores de tela; telas pequenas e grandes | `aria-hidden` nos enfeites; layout responsivo verificado em largura de celular. | Atende |
| Restrições: tipografia Tropi Land nos títulos (Demo, uso pessoal) | Fonte servida localmente, com fonte alternativa. Sem publicação. | Atende |
| Fluxo: testes de resultado **e** justificativa, incluindo requisito sem evidência | Suítes de contrato e de integração cobrem os dois, inclusive o caso sem evidência. | Atende |

**Re-check pós-design (Fase 1)**: o desenho de `data-model.md` e `contracts/` manteve todos os itens acima, sem pendências.

## Project Structure

### Documentation (this feature)

```text
specs/001-simulador-analise-curriculo/
├── plan.md              # Este arquivo (saída do /speckit-plan)
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/           # Fase 1
│   ├── llm-extract-requirements.schema.json
│   ├── llm-match-requirements.schema.json
│   ├── llm-translate.schema.json
│   ├── scoring-rubric.md
│   └── ui-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; não criado aqui)
```

### Source Code (repository root)

```text
app.py                          # ponto de entrada do Streamlit: estágios entrada → análise → resultado
pyproject.toml                  # dependências e configuração do pytest
.gitignore                      # inclui .env, .streamlit/secrets.toml e __pycache__
.streamlit/
└── config.toml                 # tema, server.enableStaticServing e [[theme.fontFaces]]
static/
├── fonts/                      # Tropi Land (extraída de font/tropi_land.zip) e serifa (OFL)
└── flags/                      # br.svg, us.svg, es.svg (bandeiras do seletor de idioma)
font/
└── tropi_land.zip              # já existe; fonte original
scripts/
└── sync_theme.py               # gera as cores do config.toml a partir de tokens.py

src/ats/
├── logging_setup.py            # logs só com metadados, nunca texto de currículo ou vaga
├── config.py                   # limites (páginas, tamanho, chunking), modelo e esforço por etapa
├── domain/
│   ├── models.py               # Vaga, Requisito, Curriculo, Verdict, Result... (pydantic)
│   └── errors.py               # erros de entrada com mensagem por chave i18n
├── ingest/
│   ├── text_input.py           # normalização e validação de texto colado
│   ├── pdf_reader.py           # PyMuPDF: texto, criptografia, escaneado, métricas de layout
│   └── chunking.py             # divisão por seções com sobreposição
├── analysis/
│   ├── llm_client.py           # porta LlmClient + implementação Gemini + fake para testes
│   ├── prompts.py              # instruções das três chamadas (extrair, julgar, traduzir)
│   ├── requirements.py         # extração de requisitos da vaga
│   ├── matcher.py              # julgamento por requisito, verificação de evidência, reunião de chunks
│   ├── structure.py            # nota de Estrutura (regras sobre seções e contato)
│   ├── design.py               # nota de Design (regras sobre métricas do PDF)
│   ├── scoring.py              # rubrica, pesos, nota global e decomposição
│   ├── translate.py            # tradução sob demanda dos textos explicativos
│   └── pipeline.py             # orquestra as etapas e o cache da sessão
├── i18n/
│   ├── __init__.py             # t(chave), idioma ativo, falha se faltar chave
│   ├── pt_BR.json
│   ├── en.json
│   └── es.json
└── ui/
    ├── tokens.py               # única fonte das cores e das fontes
    ├── theme.py                # monta e injeta o CSS
    └── components/
        ├── score_bar.py        # barra segmentada (HTML/CSS)
        ├── language_picker.py  # bandeiras (imagens SVG) BR, US e ES com o texto PT, EN e ES
        ├── hearts.py           # corações decorativos em SVG
        ├── requirement_card.py # requisito com status, evidência e dedução
        └── result_view.py      # global, categorias e lista de requisitos

tests/
├── fixtures/                   # textos de exemplo e respostas gravadas do modelo
├── live/                       # testes com chave real (marcador `live`, fora da execução padrão)
├── unit/                       # chunking, scoring, structure, design, verificação de evidência, i18n
├── contract/                   # esquemas JSON dos vereditos e da tradução
├── integration/                # pipeline completa com LlmClient falso
└── ui/                         # AppTest: fluxos, troca de idioma, erros de entrada, tokens de cor
```

**Structure Decision**: um único projeto Streamlit. A camada `analysis` não importa Streamlit, então pode
ser testada sem interface. O acesso ao LLM fica atrás de uma interface (`LlmClient`), o que permite testes
sem rede e troca de provedor sem tocar na pontuação. A interface só consome objetos de `domain`.

## Complexity Tracking

Nenhuma violação da constituição v1.2.0 a justificar. A variação dos vereditos do LLM entre sessões está tratada pela emenda do Princípio I e por temperatura 0 com semente
fixa, e foi medida com o modelo real (ver [research.md](research.md), D4).
