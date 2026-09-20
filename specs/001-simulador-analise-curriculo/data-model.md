# Data Model: Simulador de Análise de Currículo

Nada é persistido. Todas as entidades vivem na memória da sessão (`st.session_state`) e somem ao iniciar
uma nova análise ou encerrar a sessão (FR-020). Os nomes seguem [spec.md](spec.md) (Key Entities), e
os tipos são modelos `pydantic` em `src/ats/domain/models.py`.

## Entidades

### JobPosting (Vaga)

| Campo | Tipo | Regra |
|---|---|---|
| `text` | str | obrigatório; 100 a 20.000 caracteres depois de normalizar |
| `language` | `pt` \| `en` \| `es` \| `other` | preenchido pela extração de requisitos |

### Requirement (Requisito)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | str | `R1`, `R2`, ... únicos na análise |
| `text` | str | o requisito reescrito de forma curta, em pt-BR |
| `kind` | enum | `formacao`, `experiencia`, `habilidade_tecnica`, `habilidade_comportamental`, `idioma`, `certificacao`, `outro` |
| `importance` | enum | `obrigatorio` (peso 2) ou `desejavel` (peso 1) |
| `source_excerpt` | str | trecho da vaga de onde veio, para a pessoa conferir |

Uma vaga com nenhum requisito identificado interrompe a análise com aviso (edge case da spec).

### Resume (Currículo)

| Campo | Tipo | Regra |
|---|---|---|
| `source` | `pasted` \| `pdf` | de onde veio |
| `text` | str | 200 a 60.000 caracteres depois de normalizar (espaços e hifenização) |
| `language` | `pt` \| `en` \| `es` \| `other` | preenchido pelo julgamento |
| `pdf_meta` | `PdfMeta` \| null | só quando `source = pdf` |

**PdfMeta**: `file_name`, `pages` (≤ 10), `size_bytes` (≤ 5 MB), `font_families` (int), `body_font_size_range`
(min e max em pt), `min_margin_cm`, `text_density`, `has_full_page_image` (bool), `column_count`.

Se ambos os modos de entrada estiverem preenchidos, o estado guarda `active_input` e a tela mostra qual está em uso.

### Chunk

| Campo | Tipo | Regra |
|---|---|---|
| `index` | int | ordem no currículo |
| `text` | str | até 8.000 caracteres, com 500 de sobreposição com o anterior |

Só existe quando o currículo passa de 20.000 caracteres.

### Verdict (Veredito por requisito)

| Campo | Tipo | Regra |
|---|---|---|
| `requirement_id` | str | referência a `Requirement.id` |
| `status` | `atendido` \| `parcial` \| `nao_atendido` | enumeração fechada |
| `evidence` | list[str], 0 a 3 | trechos **literais** do currículo; verificados em código |
| `deduction_type` | enum | `correspondencia_exata`, `sinonimo`, `termo_relacionado`, `nivel_superior`, `equivalencia_contextual`, `sem_evidencia` |
| `certainty` | `alta` \| `media` \| `baixa` | `baixa` é exibida como "dedução incerta" (FR-011) |
| `justification` | str | pt-BR, para a pessoa candidata (Princípio II) |

**Regras de validação em código** (depois do esquema do LLM):

1. Cada item de `evidence` precisa ser substring do texto do currículo depois da mesma normalização. Item que
   falha é removido e a evidência verificada passa a vazia.
2. Se `evidence` ficar vazia, `status` vira `nao_atendido`, `deduction_type` vira `sem_evidencia` e a
   justificativa informa que nenhuma evidência foi encontrada (FR-010).
3. Todo `Requirement` tem exatamente um `Verdict`; faltando, gera-se `nao_atendido` com `sem_evidencia`.

### CategoryScore (Categoria de Pontuação)

| Campo | Tipo | Regra |
|---|---|---|
| `category` | `conteudo` \| `estrutura` \| `design` | |
| `evaluated` | bool | `design` é `false` para texto colado |
| `score` | int 0 a 100 | inteiro, arredondado uma única vez, em `scoring.py` |
| `weight` | float | conforme a rubrica (depende de `design` estar avaliado) |
| `criteria` | list[CriterionResult] | cada critério com `passed`, pontos, e `explanation_key` para o texto |

**CriterionResult**: `id`, `points_earned`, `points_max`, `explanation_key`, `explanation_params`. Os textos vêm dos arquivos de idioma,
não do LLM.

### ScoreBreakdown e AnalysisResult

| Campo | Tipo | Regra |
|---|---|---|
| `result_id` | str | `sha256(vaga + currículo + versão do prompt + modelo)`; chave do cache da sessão |
| `requirements` | list[Requirement] | |
| `verdicts` | list[Verdict] | um por requisito |
| `categories` | list[CategoryScore] | |
| `overall` | int 0 a 100 | soma ponderada das categorias avaliadas (ver rubrica), única fórmula em `scoring.py` |
| `language_notes` | list[str] | ex.: vaga e currículo em idiomas diferentes (FR-031) |
| `improvement_hints` | list[Hint] | sugestões para notas baixas (FR-018); cada uma é uma chave de modelo i18n com parâmetros, como em [contracts/scoring-rubric.md](contracts/scoring-rubric.md) |
| `rubric_version`, `prompt_version`, `model` | str | reprodutibilidade |

**Invariante (Princípio II)**: `overall` e cada `score` podem ser recalculados só a partir de `verdicts`,
`Requirement.importance`, `criteria` e da rubrica, sem consultar o LLM.

### TranslationBundle

| Campo | Tipo | Regra |
|---|---|---|
| `result_id` | str | resultado ao qual pertence |
| `language` | `en` \| `es` | pt-BR não tem bundle: é o original |
| `items` | dict[str, str] | chave (ex. `R2.justification`, `R2.text`) → texto traduzido; só textos escritos pelo LLM entram aqui |

Evidência, número, status e nome de arquivo nunca entram no bundle. Se a chave faltar no bundle, a
tela mostra o texto em pt-BR e um aviso discreto, sem quebrar.

### UiState (`st.session_state`)

| Campo | Tipo | Regra |
|---|---|---|
| `ui_language` | `pt_BR` \| `en` \| `es` | padrão `pt_BR`; vale na sessão |
| `stage` | `input` \| `analyzing` \| `result` \| `error` | ver transições |
| `active_input` | `pasted` \| `pdf` | |
| `job_text`, `resume_text` | str | preservados na troca de idioma |
| `results` | dict[result_id, AnalysisResult] | cache da sessão |
| `translations` | dict[(result_id, language), TranslationBundle] | cache da sessão |
| `last_error` | chave i18n \| null | erro exibido com tom gentil |

## Transições de estado

```text
input --(validar OK, pedir análise)--> analyzing --(sucesso)--> result
  ^                                        |                        |
  |                                        +--(falha/recusa)--> error --(voltar)--> input
  +------------------(nova análise: limpa results e translations)---+
```

- `input → analyzing` só se vaga e currículo passam na validação (FR-005); senão permanece em `input` com o erro.
- `result` permanece ao trocar de idioma: só `ui_language` e, se preciso, `translations` mudam.
- Análise repetida com o mesmo `result_id` volta direto para `result`, sem chamar o LLM.
