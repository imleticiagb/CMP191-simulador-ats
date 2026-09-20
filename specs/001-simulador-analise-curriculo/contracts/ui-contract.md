# Contrato: interface (Streamlit)

Uma página com três estágios (`input`, `analyzing`, `result`) mais um estado de erro. Todos os textos vêm de
`t("chave")`. O layout é responsivo e as decorações são `aria-hidden`.

## Telas e componentes

| Estágio | Conteúdo | Requisitos |
|---|---|---|
| Comum (topo) | Título na Tropi Land, corações, seletor de idioma (bandeiras BR, US, ES) | FR-022, FR-023, FR-027, FR-028 |
| `input` | Campo da vaga; escolha **colar** ou **enviar PDF** para o currículo; aviso de privacidade; botão "Analisar" | FR-001 a FR-005, FR-020 |
| `analyzing` | Indicador de progresso gentil com a etapa atual (lendo, entendendo a vaga, comparando) | FR-025 |
| `result` | Nota global em destaque com barra segmentada; três categorias com barra, número e justificativa; rubrica ("como calculamos"); lista de requisitos; sugestões; botão "Nova análise" | FR-006 a FR-020 |
| `error` | Mensagem gentil por causa (arquivo inválido, PDF sem texto, texto curto, idioma não suportado, recusa, sem chave de API, falha de rede) e ação para voltar | FR-003, FR-004, FR-005, FR-032 |

### Aviso de privacidade

Antes de "Analisar", a tela informa que o texto da vaga e do currículo é enviado a um serviço de IA externo
para a análise, e que o app não guarda os dados depois da sessão (FR-034).

## Seletor de idioma

| Item | Regra |
|---|---|
| Opções | três bandeiras em imagens SVG (`static/flags/`): Brasil, Estados Unidos e Espanha, cada uma com o texto PT, EN ou ES ao lado; a imagem leva `alt` com o nome do idioma |
| Padrão | PT (português do Brasil) |
| Acessibilidade | nome do idioma no `alt` e no texto de ajuda; o idioma ativo usa o botão primário e `aria-pressed`, não só a cor |
| Efeito | atualiza a interface e as explicações; não altera entradas, notas nem status (FR-029, FR-030) |
| Tradução | se ainda não houver `TranslationBundle` para `(result_id, idioma)`, chama a tradução uma vez e mostra o texto em pt-BR com aviso enquanto isso |

## Barra de progresso segmentada

Função pura `render_score_bar(value: int, label: str) -> str` que devolve HTML:

- 20 elementos de segmento; os `round(value/5)` primeiros preenchidos, com a cor de acento em gradiente do tom claro (primeiro segmento) ao intenso (último);
- contêiner com `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"` e `aria-label`;
- o número (`N/100`) na Tropi Land ao lado e a justificativa logo abaixo; a informação nunca depende só da cor;
- categoria não avaliada: barra vazia em tom neutro com o texto "não avaliada" e a explicação.

## Cartão de requisito

Mostra: texto do requisito, status (ícone + rótulo), trecho de evidência entre aspas (em destaque suave), tipo
de dedução em palavras ("sinônimo", "nível superior ao pedido"...), selo de "dedução incerta" quando aplicável, e a justificativa.
Para `sem_evidencia`, mostra a frase fixa "Não encontramos nenhuma evidência no currículo".

## Tema e tokens

Fonte única em `src/ats/ui/tokens.py`. Nenhuma cor hexadecimal fora dele (teste automático).

| Token | Uso |
|---|---|
| `pink_50`, `pink_100`, `pink_300`, `pink_500`, `pink_700` | fundos, bordas e destaques em rosa |
| `purple_50`, `purple_100`, `purple_300`, `purple_500`, `purple_700`, `purple_900` | fundos, texto e destaques em roxo |
| `ink` | texto principal (roxo muito escuro, contraste mínimo 4,5:1 sobre o fundo) |
| `accent_light`, `accent_deep` | **apenas** o gradiente da barra (turquesa/verde-água, matiz final definida no design) |

Fontes: `font_display` = "Tropi Land" com alternativa; `font_body` = serifa com alternativa.

## Estado e chaves de texto

- Estado em `st.session_state` conforme [data-model.md](../data-model.md) (UiState).
- Chaves de texto por área: `input.*`, `result.*`, `rubric.*`, `error.*`, `hint.*`, `lang.*`, `status.*`, `deduction.*`.
- Teste de contrato: o conjunto de chaves de `pt_BR.json`, `en.json` e `es.json` é idêntico, e nenhuma chave usada no código falta em nenhum dos três (FR-033).
