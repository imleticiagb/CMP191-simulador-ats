# Validação da implementação: Simulador de Análise de Currículo

Registro da execução de `/speckit-implement` em 2026-09-19. Cobre as tarefas T083 a T089.

## Resumo

| Item | Resultado |
|---|---|
| Testes automáticos | **209 passam**; 2 de marcador `live` (exigem chave) foram rodados à parte e passam |
| Lint (`ruff check`) | sem avisos |
| Cenários do quickstart | 14 de 15 conferidos em navegador real (Firefox, via Playwright); o 11 (idioma não suportado) está coberto por teste automático |
| Modelo de linguagem real | **exercitado com o Google Gemini** (`gemini-3.1-flash-lite`): 10/10 relações semânticas, 0 falsos positivos, 5/5 execuções idênticas (ver "Atualização: Gemini") |

## Cenários do quickstart (T086)

| # | Cenário | Como foi verificado | Resultado |
|---|---|---|---|
| 1 | Análise básica | navegador | OK: nota `N/100` e lista de requisitos |
| 2 | Dedução semântica ("concluída" cumpre "em curso") | navegador + testes | OK: `nivel_superior` com justificativa |
| 3 | Sem evidência | navegador + testes | OK: "Não encontramos nenhuma evidência no currículo." |
| 4 | Repetição na mesma sessão | navegador + testes | OK: mesma nota e sem nova chamada ao cliente |
| 4b | Aviso de privacidade e instrução embutida | navegador + testes | OK: aviso antes do botão; instrução embutida não altera a nota |
| 5 | PDF com texto | navegador + testes | OK: nome confirmado, 4 barras e pesos 60/25/15 |
| 6 | Arquivo inválido | navegador + testes | OK: `.docx` recusado; PDF protegido sugere colar o texto |
| 7 | Categorias e barras | navegador | OK: barras segmentadas com número e justificativa |
| 8 | Design não avaliado (texto colado) | navegador | OK: "não avaliada" com explicação e pesos 70/30 |
| 9 | Tema e fontes | navegador (capturas) | OK: rosa e roxo, corações, Tropi Land nos títulos, Lora nos textos |
| 10 | Idiomas | navegador + testes | OK: PT/EN/ES com resultado na tela, mesma nota |
| 11 | Idioma não suportado | testes (`test_document_language.py`) | OK: erro sem nota |
| 12 | Texto muito longo | navegador + testes | OK: análise em blocos; acima de 60.000, recusa |
| 13 | Sem chave de API | navegador (servidor sem chave) | OK: mensagem gentil, sem quebrar |
| 14 | Telas pequenas | navegador, 360 px | OK: sem rolagem horizontal |
| 15 | Nova análise | navegador + testes | OK: entradas e resultados limpos |

## Metas de desempenho (T085)

| Meta do plano | Medido |
|---|---|
| PDF de até 10 páginas em menos de 3 s | **0,07 s** (10 páginas, cerca de 35 mil caracteres) |
| Troca de idioma já traduzido em menos de 1 s | **menos de 1 ms** (vem do cache da sessão) |
| Análise completa em geral abaixo de 60 s | **medido com o Gemini**: cerca de 5 a 10 s com `gemini-3.1-flash-lite` (2 chamadas); picos de demanda do Google podem passar de 60 s por causa das novas tentativas |

## Revisão de segurança e privacidade (T083)

- Nenhum módulo grava em disco (`test_source_never_writes_files`); resultado e traduções vivem em `st.session_state`.
- Os logs guardam só metadados (etapa, duração, tamanhos, hash curto); teste confere que nenhum trecho do currículo ou da vaga aparece (`test_privacy.py`).
- A chave só vem de `GEMINI_API_KEY`, de `st.secrets` ou de `.streamlit/secrets.toml`. `.env` e `.streamlit/secrets.toml` estão no `.gitignore`, e nenhum arquivo do app contém `sk-ant-`.
- O texto da vaga e do currículo entra nos prompts como dado delimitado, com etiquetas de fechamento neutralizadas (FR-035).
- Saídas do modelo são escapadas (`html.escape`) antes de irem para o HTML.
- Erros do serviço viram mensagens gentis: recusa, indisponibilidade, chave ausente e cota diária esgotada.

## Revisão de acessibilidade (T084)

- **Teclado:** foi possível trocar de idioma com Enter e concluir a análise sem o mouse. Os links de âncora dos títulos, que só atrapalhavam o Tab, foram escondidos.
- **Bandeiras:** três imagens com `alt` no próprio idioma ("Português (Brasil)", "English", "Español"), sempre com o texto PT, EN e ES; o idioma ativo tem botão primário e "✓".
- **Corações:** todos com `aria-hidden="true"`; nenhum texto usa símbolo de coração.
- **Barras:** `role="progressbar"` com `aria-valuenow`, `aria-valuemin`, `aria-valuemax` e `aria-label`; categoria sem nota vira `role="img"`.
- **Sem cor como único sinal:** status têm ícone e rótulo; a nota tem número.
- **Layout:** sem rolagem horizontal em 360 px.
- **Limitação:** o Streamlit fixa `lang="en"` no HTML da página, o que o app não controla.

## Conferência dos Princípios III e IV (T088)

| Ponto | Resultado |
|---|---|
| Só rosa e roxo como cores de identidade | Sim. `tokens.py` é a única fonte; nenhum hexadecimal fora dele (`test_no_hex_colors_in_source_outside_tokens`) |
| Exceção 1: gradiente de acento só na barra | Sim, em turquesa (`#CDF3EC` → `#0B6B62`), só em `score_bar.py`, sempre com número |
| Exceção 2: bandeiras com cores próprias | Sim, como imagens SVG com nome acessível |
| Contraste mínimo de 4,5:1 | Sim: 5,5:1 a 16,3:1 nos pares usados (menor: rosa 700 sobre rosa 50) |
| Corações recorrentes | Sim: cabeçalho de todas as telas, cartão da nota geral e canto de cada cartão |
| Decoração não compete com a informação | Sim, verificado nas capturas de tela |
| Tom gentil, inclusive em resultados ruins | Sim: mensagens de erro, sugestões e "não avaliada" foram escritas nos três idiomas com tom acolhedor |
| Tropi Land nos títulos, serifa nos textos | Sim (navegador); fonte alternativa definida para os dois |

## Reavaliação da checklist `qualidade-requisitos.md` (T089)

As checklists são do revisor, então **nenhuma marcação foi alterada**. Estado, item a item, contra a spec atualizada:

| Situação | Itens |
|---|---|
| Resolvidos pela clarificação e pela spec | CHK004, CHK007, CHK009, CHK010 (parte), CHK012, CHK015, CHK018, CHK019, CHK021, CHK023, CHK024, CHK028, CHK029, CHK030, CHK033 |
| Atendidos na implementação, mas ainda sem texto na spec | CHK014 (contraste 4,5:1), CHK016 (360 px), CHK017 (teclado), CHK020 (carregamento), CHK025 (falha de rede), CHK026, CHK027 |
| Ainda abertos | CHK001, CHK002, CHK003, CHK005, CHK006, CHK008, CHK011, CHK013, CHK022, CHK031, CHK032 |

## Diferenças em relação ao plano

- **Erros na tela de entrada:** os erros aparecem na própria tela de entrada, e não em um estágio `error` separado, para a pessoa não perder o que digitou.
- **Modo de entrada:** o modo (colar ou PDF) usa dois botões em vez de `st.radio`, pois o `st.radio` com `format_func` não funciona com o `AppTest` quando o rótulo muda de idioma. O comportamento real estava correto.
- **Bandeiras:** o seletor mostra a imagem por HTML (`<img alt>`), pois `st.image` não aceita texto alternativo.
- **Idioma "other":** vaga ou currículo em outro idioma geram erro sem nota; idiomas diferentes entre si geram um aviso.

## Atualização: troca do provedor para o Google Gemini

O provedor foi trocado da Anthropic para o Google Gemini (`google-genai`), a pedido. O que foi medido com o modelo real:

| Medida | Resultado |
|---|---|
| Análise completa (exemplo "licenciatura") | nota de Conteúdo 86, todos os status como esperado; "concluída" cumpre "em curso" com dedução `nivel_superior` |
| Relações semânticas reconhecidas (SC-003) | **10 de 10 (100%)**, meta de 90% atingida |
| Falsos positivos (requisito sem relação dado como atendido) | **0** |
| Acerto geral em 22 casos | 18 de 22 (82%); as 4 divergências são "parcial" versus "não atendido" |
| Estabilidade entre execuções independentes | **5 de 5 idênticas** (temperatura 0 e semente fixa) |
| Latência típica (`gemini-3.1-flash-lite`) | 2 a 3 s por chamada; o `gemini-3.6-flash` chegou a 20 s e a 503 por alta demanda |
| Cota gratuita | `gemini-3.6-flash`: 20 requisições por dia (esgotada nos testes); `gemini-3.1-flash-lite`: sem limite atingido em mais de 60 chamadas |

Decisões: o modelo padrão é o `gemini-3.1-flash-lite`; picos de demanda são repetidos com espera; cota diária esgotada mostra mensagem própria. O modelo `gemini-2.5-flash` já não está disponível para contas novas.

## Como validar com o modelo real

```bash
export GEMINI_API_KEY="..."     # ou .streamlit/secrets.toml
uv run pytest -m live -s        # precisão semântica (SC-003) e estabilidade entre execuções (Princípio I)
uv run streamlit run app.py
```
