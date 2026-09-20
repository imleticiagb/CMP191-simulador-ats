# Contrato: rubrica de pontuação (versão `rubric-1`)

Esta rubrica é o contrato entre o código de pontuação e a tela. Tudo o que está aqui **é mostrado à pessoa
candidata** (Princípio I). Implementada em `src/ats/analysis/scoring.py`, `structure.py` e `design.py`. Nenhuma
nota vem do LLM: o modelo só fornece os vereditos por requisito.

## Nota global

```text
overall = arredondar( Σ (peso_categoria × nota_categoria) / Σ peso_categoria )   # só categorias avaliadas
```

| Situação | Conteúdo | Estrutura | Design |
|---|---|---|---|
| PDF (Design avaliado) | 60 | 25 | 15 |
| Texto colado (Design "não avaliado") | 70 | 30 | não entra |

Arredondamento: meio para cima, **uma única vez** ao final de cada nota. A barra tem 20 segmentos:
`segmentos_preenchidos = arredondar(nota / 5)`. O valor numérico é sempre exibido.

## Conteúdo (0 a 100)

```text
nota = arredondar( 100 × Σ (peso_i × crédito_i) / Σ peso_i )
```

| Item | Valor |
|---|---|
| `peso_i` | `obrigatorio` = 2, `desejavel` = 1 |
| `crédito_i` | `atendido` = 1, `parcial` = 0,5, `nao_atendido` = 0 |

Requisito com `certainty = baixa` conta normalmente e é marcado como "dedução incerta" na tela (FR-011).

## Estrutura (0 a 100), regras sobre o texto inteiro

| Critério | Pontos | Regra de verificação |
|---|---|---|
| E-mail de contato | 10 | padrão de e-mail no texto |
| Telefone de contato | 10 | sequência de 8 a 13 dígitos com separadores comuns |
| Seção de experiência | 20 | título reconhecido (dicionário abaixo) |
| Seção de formação | 20 | título reconhecido |
| Seção de habilidades | 15 | título reconhecido |
| Resumo ou objetivo | 10 | título reconhecido |
| Datas nas experiências | 10 | ao menos 2 anos (19xx ou 20xx) na seção de experiência |
| Tamanho adequado | 5 | entre 250 e 1.200 palavras |

Dicionário de títulos (sem diferenciar maiúsculas e acentos):

| Seção | pt | en | es |
|---|---|---|---|
| experiência | experiência, experiência profissional, histórico profissional | experience, work experience, employment | experiencia, experiencia laboral |
| formação | formação, formação acadêmica, educação, escolaridade | education, academic background | formación, educación, estudios |
| habilidades | habilidades, competências, conhecimentos | skills, technical skills | habilidades, competencias, conocimientos |
| resumo | resumo, perfil, objetivo, sobre mim | summary, profile, objective, about | resumen, perfil, objetivo |

## Design (0 a 100), só para PDF, sobre as métricas do arquivo

| Critério | Pontos | Regra |
|---|---|---|
| Número de páginas | 25 | 1 a 2 páginas = 25; 3 = 12; mais que 3 = 0 |
| Famílias de fonte | 20 | até 3 = 20; 4 = 10; 5 ou mais = 0 |
| Tamanho do corpo do texto | 20 | mediana entre 9 e 12 pt = 20; fora disso = 0 |
| Margens | 15 | menor margem de página >= 1,0 cm = 15; senão 0 |
| Texto selecionável | 10 | nenhuma página é imagem inteira = 10 |
| Densidade do texto | 10 | área ocupada pelo texto entre 25% e 75% da página = 10 |

Cada critério mostra à pessoa a nota parcial e uma frase com o motivo (por exemplo, "Seu currículo usa 5
fontes diferentes; até 3 costuma ficar mais limpo").

## Sugestões de melhoria (FR-018)

Para categoria com nota abaixo de 70, a tela lista até 3 sugestões. Cada uma é um **modelo de texto por
chave i18n** com parâmetros (ex.: `hint.add_section` com `{secao}`, `hint.show_requirement` com o texto do
requisito não atendido). O texto vem dos arquivos de idioma e nunca é escrito pelo LLM, então tem tom gentil garantido nos três idiomas.
