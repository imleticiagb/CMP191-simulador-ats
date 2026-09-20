<!--
Sync Impact Report
- Version change: 1.1.0 → 1.2.0
- Bump rationale: MINOR. O Princípio I troca uma garantia inatingível ("sempre o mesmo
  resultado") por obrigações precisas e testáveis, e acrescenta a de medir e informar a
  variação. Nenhum princípio foi removido, e o que já cumpria a regra antiga continua cumprindo.
- Modified principles:
  - I. Transparência Algorítmica (título mantido): determinismo delimitado à nota calculada a
    partir dos vereditos e à repetição dentro da mesma sessão; variação dos vereditos do modelo
    entre sessões passa a ser medida e informada; proibido guardar resultado em disco para
    forçar a repetição.
- Added principles: nenhum
- Added sections: nenhuma
- Removed sections: nenhuma
- Templates/artefatos a revisar: spec.md (FR-012, SC-004) já reflete esta emenda; plan.md
  (Constitution Check e Complexity Tracking) deixa de registrar desvio; tasks.md T021(c) e T078.
- Deferred / TODOs: nenhum.
- Correção de forma: removido o título H1 duplicado deixado pela emenda 1.1.0.
-->

# Simulador de ATS Constitution

## Core Principles

### I. Transparência Algorítmica

O produto existe para tornar visível o que um ATS faz. Nenhuma etapa da análise pode ser uma
"caixa-preta": todo critério, peso e regra que influencia o resultado MUST ser exibido à pessoa
candidata em linguagem compreensível. Nenhum resultado MAY ser apresentado sem que a pessoa
consiga ver como ele foi obtido.

Reprodutibilidade, em três regras:

1. A nota de cada categoria e a nota global MUST ser calculadas por regras fixas e publicadas a
   partir dos vereditos, de modo que os mesmos vereditos sempre gerem a mesma nota.
2. Dentro da mesma sessão, repetir a análise com os mesmos textos de vaga e currículo MUST
   devolver exatamente o mesmo resultado e as mesmas justificativas.
3. Os vereditos gerados por modelo de linguagem MAY variar entre sessões. Essa variação MUST ser
   medida e informada, e nunca escondida. Nenhum resultado MAY ser guardado em disco para forçar
   a repetição.

Racional: a proposta do simulador é dar à pessoa candidata poder de compreensão. Um resultado
sem visibilidade das regras contradiz o propósito do projeto. Os modelos de linguagem atuais não
permitem fixar a amostragem, e guardar resultados contraria a privacidade; por isso o
determinismo é exigido onde é possível garantir (regras de nota e repetição na sessão), e a
incerteza restante é declarada em vez de prometer o que não se cumpre.

### II. Explicabilidade por Dedução Lógica

Toda análise de correspondência entre os requisitos da vaga e o currículo MUST ser explicável.
Para cada requisito da vaga, o simulador MUST informar: (a) se foi considerado atendido,
parcialmente atendido ou não atendido; (b) qual trecho do currículo sustentou essa conclusão,
quando houver; e (c) qual dedução lógica ligou o trecho ao requisito (por exemplo, correspondência
exata, sinônimo ou termo relacionado). Quando nenhuma evidência for encontrada, o simulador MUST
dizer isso explicitamente, em vez de omitir o requisito. Pontuações agregadas MUST poder ser
decompostas até essas justificativas individuais. Os textos de justificativa MUST ser escritos
para a pessoa candidata, sem jargão técnico não explicado.

Racional: uma nota sem justificativa não ajuda ninguém a melhorar o currículo. A dedução
explícita é o que transforma a análise em aprendizado.

### III. Paleta Estrita em Rosa e Roxo

A interface MUST usar exclusivamente tons de rosa e roxo como cores de identidade, incluindo
fundos, textos, bordas, botões, gráficos e ilustrações. Neutros de apoio (branco, e tons
rosados ou arroxeados muito claros ou muito escuros) são permitidos. Nenhuma outra matiz MAY ser
usada como cor de identidade. Estados de sucesso, aviso e erro MUST ser diferenciados por ícone,
rótulo e variação de tom dentro da paleta, e nunca só pela cor. As cores MUST ser definidas em um
único conjunto central de variáveis, para que nenhum componente use valores avulsos. Combinações
de texto e fundo MUST manter contraste legível.

Exceções (as únicas permitidas; qualquer outra cor fora de rosa e roxo continua proibida e só
pode ser admitida por emenda desta constituição):

1. **Escala de dados da barra de progresso.** A barra de progresso da pontuação MAY usar o
   gradiente de uma única cor de acento que combine com rosa e roxo, do tom claro (nota baixa)
   ao intenso (nota alta). O padrão é turquesa ou verde-água, e a matiz exata é definida no
   design. Essa cor é uma escala de dados, não uma cor de identidade, e MUST NOT ser usada em
   nenhum outro elemento. A barra MUST vir sempre acompanhada do valor numérico e da
   justificativa, e a informação MUST NOT depender só da cor.
2. **Bandeiras do seletor de idioma.** As bandeiras do Brasil, dos Estados Unidos e da Espanha
   MAY manter suas cores próprias, como símbolos informativos. Cada bandeira MUST ter nome de
   idioma acessível e indicação de qual está ativa que não dependa só da cor.

Racional: a identidade visual é um requisito do produto, não um detalhe. Centralizar as cores
torna a regra verificável, e a legibilidade impede que a estética prejudique o uso. As exceções
são enumeradas e limitadas porque uma escala de dados e bandeiras só cumprem sua função com
cores que não são de identidade, e listá-las evita que a paleta se dilua.

### IV. Estética Fofa e Acolhedora

A interface MUST ter elementos decorativos que reforcem uma estética fofa, incluindo corações
como motivo recorrente, cantos arredondados e um tom de voz gentil nos textos. A decoração MUST
ser puramente visual e MUST NOT esconder, distorcer ou competir com as informações de análise e
justificativa. O tom acolhedor MUST se manter também ao comunicar resultados desfavoráveis ou
requisitos não atendidos, tratando-os como oportunidades de melhoria e nunca como julgamento
sobre a pessoa.

Racional: o processo seletivo costuma gerar ansiedade. A estética e o tom reduzem a intimidação
sem tirar o rigor da explicação.

## Restrições de Interface e Conteúdo

- O português do Brasil é o idioma original e padrão de todo texto voltado à pessoa usuária, e
  todo texto MUST existir em português do Brasil.
- Traduções opcionais para inglês e espanhol são permitidas, escolhidas por bandeirinhas (Brasil,
  Estados Unidos e Espanha). A tradução MUST NOT alterar a pontuação, o status dos requisitos
  nem o resultado da análise.
- A tipografia dos títulos e elementos de destaque MAY usar a fonte "Tropi Land" (versão Demo,
  de uso pessoal). Isso vale enquanto o projeto for um trabalho acadêmico não publicado. Se for
  publicado, a licença da fonte MUST ser revista.
- Elementos decorativos MUST ter texto alternativo vazio ou ser marcados como decorativos, para
  não poluir leitores de tela; as informações de análise MUST ser acessíveis por texto.
- A interface MUST ser utilizável em telas pequenas e grandes.
- Explicações e justificativas MUST fazer parte do resultado principal, sem ficarem escondidas
  em telas secundárias difíceis de encontrar.

## Fluxo de Desenvolvimento e Verificação

- Toda especificação de funcionalidade (`spec.md`) MUST declarar como atende aos Princípios I e
  II, ou justificar por que não se aplica.
- Toda mudança de interface MUST ser conferida contra os Princípios III e IV antes de ser
  considerada concluída.
- Regras de correspondência MUST ter testes que verifiquem tanto o resultado quanto a
  justificativa gerada, incluindo o caso de requisito sem evidência.
- O plano de implementação (`plan.md`) MUST incluir uma verificação de conformidade com esta
  constituição, e violações MUST ser registradas e justificadas.

## Governance

Esta constituição prevalece sobre outras práticas do projeto. Emendas MUST ser feitas por
alteração deste arquivo, com registro do motivo, atualização da versão e da data de emenda, e
revisão dos artefatos dependentes (especificações, planos e tarefas) para manter a coerência.

Política de versionamento (semântico):
- MAJOR: remoção ou redefinição incompatível de princípio ou regra de governança.
- MINOR: novo princípio ou seção, ou ampliação relevante de uma orientação existente.
- PATCH: esclarecimentos, ajustes de redação e correções sem mudança de significado.

Revisão de conformidade: toda revisão de especificação, plano e implementação MUST verificar a
aderência aos princípios acima. Complexidade ou desvios MUST ser justificados por escrito.

**Version**: 1.2.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-09-19
