# Simulador de ATS 💗

Simulador de análise de currículo com **transparência algorítmica**. A pessoa cola (ou envia em PDF) o
currículo, cola a vaga e recebe:

- uma **nota geral** (`N/100`) em destaque, com barra de progresso segmentada;
- notas por **categoria** (Conteúdo, Estrutura e Design), cada uma com justificativa;
- para **cada requisito da vaga**: status, trecho do currículo que o sustenta, a dedução lógica entre os dois e
  uma explicação em linguagem simples. Exemplo: "licenciatura concluída" cumpre "licenciatura em curso".

A interface é em rosa e roxo, com corações e a fonte Tropi Land nos títulos. O texto original é em português do
Brasil, com tradução opcional para inglês e espanhol pelas bandeirinhas (BR, US e ES).

> Isto é uma simulação educativa. Não representa o resultado de nenhum sistema de recrutamento real.

## Passo a passo para rodar

### 1. Pré-requisitos

- **Python 3.11 ou mais novo** (`python3 --version`).
- **uv**, o gerenciador de pacotes: <https://docs.astral.sh/uv/getting-started/installation/>
  (Linux e macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`; Windows: `winget install astral-sh.uv`).

### 2. Abrir a pasta do projeto

```bash
cd simulador-ats
```

### 3. Instalar as dependências

```bash
uv venv
uv pip install -e ".[dev]"
```

### 4. Configurar a chave do Gemini

Crie uma chave gratuita em <https://aistudio.google.com/apikey> e guarde-a **em um destes lugares** (o primeiro
que existir vale):

| Opção | Como |
|---|---|
| Arquivo local (recomendado) | crie `.streamlit/secrets.toml` com `GEMINI_API_KEY = "sua-chave"` |
| Variável de ambiente (Linux/macOS) | `export GEMINI_API_KEY="sua-chave"` |
| Variável de ambiente (Windows PowerShell) | `$env:GEMINI_API_KEY = "sua-chave"` |

O arquivo `.streamlit/secrets.toml` já está no `.gitignore`. **Nunca coloque a chave no código nem envie o arquivo
ao repositório.** Sem chave, o app abre e mostra uma mensagem explicando o que falta.

### 5. Iniciar o app

```bash
uv run streamlit run app.py
```

O navegador abre em <http://localhost:8501>. Para parar, use `Ctrl+C` no terminal.

### 6. Usar

1. Cole o **texto da vaga** (com os requisitos).
2. Escolha **Colar o texto** ou **Enviar um PDF** para o currículo (até 10 páginas e 5 MB, com texto selecionável).
3. Leia o aviso de privacidade e clique em **Analisar**.
4. Veja a nota geral, as categorias e, em cada requisito, o trecho do currículo e a explicação.
5. Troque o idioma pelas bandeirinhas PT, EN e ES no topo. A nota não muda, só os textos.
6. Use **Nova análise** para começar de novo.

### Sem chave (demonstração)

```bash
ATS_LLM=fake uv run streamlit run app.py        # Windows PowerShell: $env:ATS_LLM="fake"; uv run streamlit run app.py
```

Usa um avaliador simples por palavras, só para conhecer a interface. Ele **não** faz a análise semântica real.

### Problemas comuns

| Mensagem no app | O que fazer |
|---|---|
| "A chave de acesso ao serviço de IA não está configurada" | refaça o passo 4 e reinicie o app |
| "O serviço de análise está indisponível no momento" | é um pico de demanda do Google; o app já tenta de novo algumas vezes, aguarde e clique em Analisar |
| "O limite gratuito de uso da API foi atingido por hoje" | espere o dia seguinte ou troque de modelo (veja abaixo) |
| PDF "sem texto legível" | o PDF é uma imagem escaneada ou tem senha; cole o texto do currículo |

## Escolher o modelo

O padrão é o `gemini-3.1-flash-lite`: rápido (2 a 3 s por chamada) e com cota gratuita maior. Para outro modelo:

```bash
export ATS_MODEL="gemini-3.6-flash"      # mais capaz, mas com cota gratuita de só 20 requisições por dia
```

## Como funciona (resumo)

| Etapa | Quem faz | Observação |
|---|---|---|
| Ler o PDF | PyMuPDF | texto em ordem de leitura e métricas de layout |
| Entender a vaga e julgar cada requisito | Google Gemini | resposta em JSON validado por esquema; evidência conferida em código |
| Todas as notas | Código Python | rubrica publicada na tela (`specs/.../contracts/scoring-rubric.md`) |
| Traduzir as explicações | Google Gemini | só sob demanda; nota, status e evidência não mudam |

A nota é sempre calculada por regras fixas a partir dos vereditos. As chamadas ao modelo usam temperatura 0 e
semente fixa; em 5 execuções independentes do mesmo par de textos, os vereditos foram idênticos. Ainda assim o modelo
pode variar levemente entre sessões, e dentro da mesma sessão repetir a análise devolve exatamente o mesmo resultado.
Veja o Princípio I em `.specify/memory/constitution.md`.

## Testes

```bash
uv run pytest                                   # unitários, contrato, integração (cliente falso) e telas
uv run pytest -m live -s                        # com o Gemini real: precisão semântica e estabilidade (usa a cota)
uv run ruff check . && uv run ruff format .
```

## Privacidade

O texto da vaga e do currículo é enviado ao **Google Gemini** para a análise, e a tela avisa isso antes de
"Analisar". O app não grava nada em disco: currículo, vaga e resultado vivem só na memória da sessão, e os logs guardam
apenas metadados (tamanhos e durações). No plano gratuito, o Google pode usar os dados enviados para melhorar seus
produtos; para currículos reais, prefira um plano pago.

## Estrutura

```text
app.py                    # ponto de entrada do Streamlit
src/ats/domain/           # modelos (pydantic) e erros
src/ats/ingest/           # texto colado, PDF e chunking
src/ats/analysis/         # LLM (Gemini), requisitos, julgamento, notas (rubrica), tradução, pipeline
src/ats/i18n/             # textos em pt_BR, en e es
src/ats/ui/               # tema (tokens de cor), barra de progresso, corações, seletor de idioma, telas
static/                   # fontes (Tropi Land, Lora) e bandeiras em SVG
specs/                    # especificação, plano, tarefas e contratos (Spec Kit)
```

## Licenças e créditos

- **Tropi Land** (`font/tropi_land.zip`): versão *Demo* da HansCo Studio, com licença de uso pessoal. Serve para
  este trabalho acadêmico não publicado. Se o projeto for publicado, adquira a licença adequada.
- **PyMuPDF**: AGPL-3.0. Adequado a um trabalho acadêmico não publicado. Para publicar, troque por `pdfplumber` (MIT).
- **Lora**: SIL Open Font License (`static/fonts/Lora-OFL.txt`).
- Bandeiras em SVG desenhadas para este projeto.
