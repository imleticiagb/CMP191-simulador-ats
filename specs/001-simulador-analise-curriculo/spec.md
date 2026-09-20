# Feature Specification: Simulador de Análise de Currículo

**Feature Branch**: `001-simulador-analise-curriculo`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Desenvolve um Simulador de Análise de Currículo. Entradas: o utilizador pode escolher entre colar o texto do currículo ou fazer o carregamento (upload) de um ficheiro PDF. Interface: tema estilizado em tons de rosa e roxo, decorações com corações, fonte 'Tropi Land' para títulos e elementos de destaque, e fonte com serifa para as informações textuais. Lógica de análise: o sistema deve realizar uma análise semântica avançada e não apenas correspondência exata de palavras-chave (exemplo: se a vaga exige "licenciatura em curso" e o currículo apresenta "licenciatura concluída", o sistema deve validar positivamente e explicar essa dedução). Resultados: apresentar a pontuação visualmente através de uma barra de progresso horizontal com gradiente de cor (laranja a verde) e uma pontuação global em destaque (ex: 85/100), dividindo a pontuação em categorias específicas (como Design, Estrutura e Conteúdo)"

## Clarifications

### Session 2026-09-19

- Q: O resultado da análise precisa ser idêntico em outra sessão, ou basta dentro da mesma sessão? → A: Idêntico dentro da mesma sessão; entre sessões, a nota e a explicação são calculadas por regras fixas a partir dos vereditos, e a estabilidade dos vereditos é medida e informada, sem promessa de 100%.
- Q: A tela deve avisar que o texto será enviado a um serviço de IA externo antes de analisar? → A: Sim, aviso curto e visível antes do botão "Analisar", nos três idiomas, informando o envio a um serviço de IA externo e que o app não guarda o texto depois da sessão.
- Q: As bandeirinhas do seletor de idioma devem ser imagens ou emojis de bandeira? → A: Imagens das três bandeiras guardadas no projeto, sempre acompanhadas do texto PT, EN e ES, para aparecerem em qualquer computador, inclusive no Windows.
- Q: Requisitos obrigatórios devem valer mais na nota do que os desejáveis? → A: Sim, obrigatório vale o dobro do desejável (peso 2 contra 1), e a tela mostra qual é qual.
- Q: A comparação entre PDF e texto colado deve considerar só status e notas de Conteúdo e Estrutura? → A: Sim; o Design fica de fora, porque só existe no PDF.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analisar um currículo colado contra uma vaga (Priority: P1)

A pessoa candidata informa o texto de uma vaga e cola o texto do seu currículo. Ao pedir a análise, o simulador mostra uma pontuação global em destaque (por exemplo, 85/100) e, para cada requisito da vaga, se foi atendido, parcialmente atendido ou não atendido, com a justificativa em linguagem simples.

**Why this priority**: É o núcleo do produto. Sozinha, esta jornada já entrega o valor central: entender como um currículo se compara a uma vaga e por quê. Todas as demais jornadas ampliam essa.

**Independent Test**: Colar o texto de uma vaga e de um currículo, pedir a análise e verificar que aparecem a pontuação global e, para cada requisito da vaga, um status com justificativa.

**Acceptance Scenarios**:

1. **Given** uma vaga e um currículo colados nos campos de texto, **When** a pessoa pede a análise, **Then** o simulador mostra a pontuação global no formato "N/100" e a lista de requisitos da vaga, cada um com status e justificativa.
2. **Given** uma vaga que exige "licenciatura em curso" e um currículo que apresenta "licenciatura concluída", **When** a análise é feita, **Then** o requisito é marcado como atendido e a justificativa explica a dedução, por exemplo: quem já concluiu a licenciatura cumpre o que se pede a quem a está cursando.
3. **Given** um requisito da vaga sem nenhuma evidência no currículo, **When** a análise é feita, **Then** o requisito aparece como não atendido e o simulador declara explicitamente que nenhuma evidência foi encontrada.
4. **Given** uma vaga e um currículo já analisados, **When** a mesma análise é repetida com os mesmos textos na mesma sessão, **Then** a pontuação, os status e as justificativas são idênticos.
5. **Given** a tela de entrada, **When** ela é exibida em qualquer idioma, **Then** um aviso visível, antes do botão de analisar, informa que o texto será enviado a um serviço de IA externo e que o app não o guarda depois da sessão.

---

### User Story 2 - Enviar o currículo em PDF (Priority: P2)

A pessoa candidata escolhe enviar o currículo como arquivo PDF em vez de colar o texto. O simulador lê o conteúdo do arquivo e faz a mesma análise da jornada anterior.

**Why this priority**: A maioria das pessoas tem o currículo em PDF, então esta entrada reduz o atrito. Mas o produto já funciona com texto colado, por isso vem depois.

**Independent Test**: Enviar um PDF de currículo com texto selecionável e uma vaga, pedir a análise e verificar que os status dos requisitos e as notas de Conteúdo e de Estrutura são iguais aos de colar o mesmo texto.

**Acceptance Scenarios**:

1. **Given** a tela de entrada, **When** a pessoa escolhe a opção de enviar PDF e seleciona um arquivo válido, **Then** o simulador confirma o recebimento mostrando o nome do arquivo e permite pedir a análise.
2. **Given** um PDF com texto selecionável, **When** a análise é feita, **Then** os status dos requisitos e as notas de Conteúdo e de Estrutura são iguais aos obtidos ao colar o mesmo texto.
3. **Given** um arquivo que não é PDF, **When** a pessoa tenta enviá-lo, **Then** o simulador recusa o arquivo e explica, com tom gentil, que apenas PDF é aceito.
4. **Given** um PDF sem texto legível (por exemplo, uma imagem escaneada) ou protegido por senha, **When** o envio é feito, **Then** o simulador avisa que não conseguiu ler o conteúdo e sugere colar o texto no lugar.

---

### User Story 3 - Entender a pontuação por categorias (Priority: P2)

Além da pontuação global, a pessoa candidata vê a nota dividida em categorias (Design, Estrutura e Conteúdo), cada uma com sua barra de progresso horizontal em gradiente de uma única cor de acento (tom claro para notas baixas, tom intenso para notas altas) e uma explicação do que levou àquela nota.

**Why this priority**: A divisão por categorias mostra onde melhorar. Depende da análise da jornada 1, mas é o que a torna acionável.

**Independent Test**: Concluir uma análise e verificar que existem três categorias, cada uma com nota, barra de progresso e justificativa, e que a pontuação global pode ser reconstituída a partir delas.

**Acceptance Scenarios**:

1. **Given** uma análise concluída, **When** o resultado é exibido, **Then** aparece uma barra de progresso horizontal em gradiente de uma única cor de acento, que combina com o rosa e o roxo do tema, para a pontuação global, e uma para cada categoria.
2. **Given** uma nota em uma categoria, **When** a pessoa lê o resultado, **Then** ao lado da barra estão o valor numérico e a justificativa da nota, para que a informação nunca dependa só da cor.
3. **Given** um resultado com pontuação global e por categoria, **When** a pessoa consulta como a global foi obtida, **Then** o simulador mostra o peso de cada categoria e como ele levou ao total.
4. **Given** uma nota baixa em alguma categoria, **When** o resultado é exibido, **Then** o simulador indica o que poderia ser melhorado, em tom acolhedor.

---

### User Story 4 - Ver a interface temática e acolhedora (Priority: P3)

A pessoa candidata usa um simulador visualmente coeso, com paleta em rosa e roxo, corações decorativos, títulos e destaques na fonte "Tropi Land" e textos informativos em fonte com serifa.

**Why this priority**: A identidade visual é requisito do produto (ver constituição), mas pode ser aplicada e validada separadamente da lógica de análise.

**Independent Test**: Abrir cada tela do simulador e conferir a paleta, os corações, a fonte dos títulos e a fonte dos textos.

**Acceptance Scenarios**:

1. **Given** qualquer tela do simulador, **When** ela é exibida, **Then** as cores de identidade são apenas tons de rosa e roxo e há corações como elemento decorativo.
2. **Given** títulos e elementos de destaque (como a pontuação global), **When** exibidos, **Then** usam a fonte "Tropi Land".
3. **Given** textos informativos (justificativas, requisitos, trechos do currículo), **When** exibidos, **Then** usam uma fonte com serifa.
4. **Given** a fonte "Tropi Land" indisponível no dispositivo da pessoa, **When** a tela é exibida, **Then** os títulos continuam legíveis usando uma fonte alternativa.

---

### User Story 5 - Usar o simulador em português, inglês ou espanhol (Priority: P2)

A pessoa candidata usa o simulador em português do Brasil por padrão e pode trocar, a qualquer momento, para inglês ou espanhol. A troca vale para toda a interface e para as explicações da análise.

**Why this priority**: Amplia quem consegue usar o produto e, como a transparência depende de a pessoa entender as justificativas, elas precisam estar no idioma que ela domina. O produto funciona em um só idioma, por isso vem depois do núcleo.

**Independent Test**: Abrir o simulador, trocar entre os três idiomas em cada tela e verificar que todos os textos e explicações mudam, sem perder o que foi digitado nem o resultado.

**Acceptance Scenarios**:

1. **Given** a primeira abertura do simulador, **When** a tela é exibida, **Then** todos os textos estão em português do Brasil e há um seletor visível com as bandeiras do Brasil, dos Estados Unidos e da Espanha, com a do Brasil indicada como ativa.
2. **Given** qualquer tela, **When** a pessoa escolhe outro idioma, **Then** todos os textos da interface passam para o idioma da bandeira escolhida, sem recarregar o que já foi preenchido.
3. **Given** um resultado já exibido, **When** a pessoa troca o idioma, **Then** a pontuação e a estrutura do resultado permanecem iguais e as justificativas, os rótulos e as sugestões aparecem no novo idioma, sem refazer a análise.
4. **Given** um idioma escolhido, **When** a análise é feita, **Then** as justificativas e deduções são escritas nesse idioma.
5. **Given** um currículo em um idioma e uma vaga em outro (entre os três suportados), **When** a análise é feita, **Then** a análise é feita normalmente e o resultado indica que os documentos estão em idiomas diferentes.

---

### Edge Cases

- Vaga ou currículo em branco, ou com texto curto demais para ser analisado: o simulador pede a informação faltante, sem gerar pontuação.
- Texto colado que claramente não é um currículo (por exemplo, um texto aleatório): o simulador avisa que não reconheceu um currículo e não inventa uma pontuação.
- PDF muito grande, corrompido, protegido por senha ou só com imagens: mensagem gentil explicando o problema e alternativa (colar o texto).
- Pessoa cola texto e também envia PDF: o simulador deixa claro qual das duas entradas está sendo usada.
- Vaga com requisitos ambíguos ou pouquíssimos requisitos identificáveis: o simulador informa quais requisitos entendeu, para que a pessoa possa conferir.
- Currículo e vaga em idiomas diferentes (entre português, inglês e espanhol): a análise é feita e o resultado avisa que os idiomas diferem, marcando como menos certas as deduções que dependem dessa diferença.
- Currículo ou vaga em um idioma fora dos três suportados: o simulador avisa que não consegue analisar com confiança e não gera pontuação.
- Troca de idioma no meio do preenchimento ou depois do resultado: nada do que foi digitado, enviado ou calculado se perde.
- Termos que existem só em um idioma ou têm nomes diferentes por país (por exemplo, "licenciatura", "bachelor's degree", "grado"): a justificativa explica a equivalência assumida.
- Requisito atendido só por um termo relacionado (sinônimo, nível superior ao pedido, tecnologia equivalente): a justificativa diz qual foi a relação e por que ela vale, e o status pode ser "parcialmente atendido" quando a relação não é total.
- Uma dedução que o simulador não tem certeza: ela é marcada como tal, em vez de apresentada como fato.
- Pessoa quer analisar outro currículo ou outra vaga em seguida: consegue reiniciar sem resíduos da análise anterior.

## Requirements *(mandatory)*

### Functional Requirements

**Entradas**

- **FR-001**: O sistema MUST permitir que a pessoa informe o currículo de duas formas alternativas: colando o texto ou enviando um arquivo PDF.
- **FR-002**: O sistema MUST permitir que a pessoa informe o texto da vaga, com os requisitos que serão comparados ao currículo.
- **FR-003**: O sistema MUST aceitar apenas PDF no envio de arquivo e MUST recusar outros formatos com mensagem explicativa.
- **FR-004**: O sistema MUST extrair o texto de PDFs legíveis e MUST avisar, sem gerar pontuação, quando não conseguir ler o conteúdo do arquivo.
- **FR-005**: O sistema MUST validar as entradas antes da análise e MUST orientar a pessoa quando algo faltar ou for insuficiente.

**Análise semântica e explicabilidade**

- **FR-006**: O sistema MUST comparar requisitos e currículo por significado, não só por palavras idênticas, reconhecendo sinônimos, termos relacionados e relações lógicas entre situações (por exemplo, "licenciatura concluída" cumpre "licenciatura em curso").
- **FR-007**: Para cada requisito identificado na vaga, o sistema MUST informar o status (atendido, parcialmente atendido ou não atendido) e se o requisito é obrigatório ou desejável, conforme a redação da vaga.
- **FR-008**: Para cada requisito, o sistema MUST mostrar o trecho do currículo usado como evidência, quando houver.
- **FR-009**: Para cada requisito, o sistema MUST explicar em linguagem simples a dedução lógica entre o trecho e o requisito, dizendo também quando a relação não é exata.
- **FR-010**: Quando não houver evidência para um requisito, o sistema MUST dizer isso explicitamente.
- **FR-011**: O sistema MUST sinalizar deduções de baixa certeza como tais.
- **FR-012**: Na mesma sessão, o sistema MUST devolver o mesmo resultado e as mesmas justificativas para os mesmos textos de vaga e currículo. Em qualquer sessão, a nota de cada categoria e a global MUST ser calculadas por regras fixas e publicadas a partir dos vereditos, de modo que os mesmos vereditos sempre gerem a mesma nota.
- **FR-013**: O sistema MUST mostrar os critérios, pesos e regras que influenciam a pontuação, em linguagem compreensível para a pessoa candidata.

**Resultados e pontuação**

- **FR-014**: O sistema MUST apresentar uma pontuação global de 0 a 100 em destaque, no formato "N/100".
- **FR-015**: O sistema MUST dividir a pontuação em categorias, no mínimo Design, Estrutura e Conteúdo, cada uma com sua nota e justificativa.
- **FR-016**: O sistema MUST permitir reconstituir a pontuação global a partir das notas das categorias e destas a partir das justificativas individuais. Na nota de Conteúdo, um requisito obrigatório MUST valer o dobro de um desejável (peso 2 contra 1).
- **FR-017**: O sistema MUST exibir a pontuação global e a de cada categoria em uma barra de progresso horizontal com gradiente de uma única cor de acento que combine com o rosa e o roxo do tema, variando de um tom claro (nota baixa) a um tom intenso (nota alta), em que a posição, a intensidade e o valor numérico deixem a nota clara sem depender da matiz da cor.
- **FR-018**: O sistema MUST indicar, para notas baixas, o que poderia ser melhorado, em tom acolhedor.
- **FR-019**: A justificativa e a explicação MUST fazer parte do resultado principal, sem ficarem em telas secundárias difíceis de achar.
- **FR-020**: O sistema MUST permitir iniciar uma nova análise, limpando os dados da anterior.

**Interface**

- **FR-021**: O sistema MUST usar como cores de identidade apenas tons de rosa e roxo, com as exceções da escala de pontuação (FR-017) e das bandeiras do seletor de idioma (FR-028), ver Assumptions.
- **FR-022**: O sistema MUST incluir corações como elemento decorativo recorrente, sem esconder nem competir com as informações de análise.
- **FR-023**: O sistema MUST usar a fonte "Tropi Land" nos títulos e elementos de destaque, com fonte alternativa legível se ela não estiver disponível, e MUST exibir corretamente nela os caracteres dos três idiomas suportados e o formato "N/100".
- **FR-024**: O sistema MUST usar uma fonte com serifa nos textos informativos.
- **FR-025**: Todo texto voltado à pessoa usuária MUST ter tom gentil, inclusive ao comunicar resultados desfavoráveis, em qualquer dos idiomas suportados.
- **FR-026**: A interface MUST ser utilizável em telas pequenas e grandes, e os elementos decorativos MUST ser ignorados por leitores de tela.

**Idiomas**

- **FR-027**: O sistema MUST oferecer a interface em português do Brasil, inglês e espanhol, com português do Brasil como idioma original e padrão, e inglês e espanhol como traduções opcionais.
- **FR-028**: O sistema MUST mostrar, em todas as telas, um seletor de idioma visível e acessível sem sair do fluxo, com três bandeirinhas: Brasil (português), Estados Unidos (inglês) e Espanha (espanhol). As bandeiras MUST ser imagens guardadas com o projeto, e não emojis do sistema, para aparecerem em qualquer computador, e MUST vir acompanhadas do texto PT, EN e ES. Cada bandeira MUST ter também um nome de idioma acessível para leitores de tela e indicar qual está ativa, sem depender só da cor.
- **FR-029**: A troca de idioma MUST atualizar imediatamente todos os textos da interface, incluindo mensagens de erro, rótulos, nomes de categorias e sugestões, sem perder o que a pessoa preencheu, enviou ou já recebeu como resultado.
- **FR-030**: As justificativas, deduções e sugestões de melhoria MUST ser escritas no idioma escolhido pela pessoa, e a troca de idioma MUST NOT alterar a pontuação nem os status dos requisitos.
- **FR-031**: O sistema MUST aceitar vaga e currículo em português, inglês ou espanhol, inclusive em idiomas diferentes entre si, e MUST sinalizar no resultado quando os idiomas diferirem.
- **FR-032**: O sistema MUST avisar, sem gerar pontuação, quando o texto estiver em um idioma fora dos três suportados.
- **FR-033**: Nenhum texto voltado à pessoa usuária pode faltar em algum dos três idiomas; um texto sem tradução MUST ser tratado como defeito.

**Privacidade e segurança**

- **FR-034**: Antes de a pessoa iniciar a análise, o sistema MUST exibir um aviso visível, nos três idiomas, de que o texto da vaga e do currículo será enviado a um serviço de inteligência artificial externo e de que o app não o guarda depois da sessão.
- **FR-035**: O sistema MUST tratar o texto da vaga e do currículo apenas como dados a analisar, e MUST ignorar instruções embutidas nesses textos (por exemplo, pedidos para dar nota máxima), de modo que elas não alterem a nota nem os status.

### Key Entities *(include if feature involves data)*

- **Vaga**: o texto informado pela pessoa, do qual são extraídos os requisitos.
- **Requisito**: uma exigência identificada na vaga (formação, experiência, habilidade, idioma etc.). Tem uma importância (obrigatório ou desejável), um status de atendimento, uma evidência opcional e uma justificativa.
- **Currículo**: o conteúdo do currículo da pessoa, vindo de texto colado ou de PDF, tratado como texto para análise.
- **Evidência**: o trecho do currículo que sustenta a conclusão sobre um requisito.
- **Dedução**: a relação lógica explicada entre a evidência e o requisito (correspondência exata, sinônimo, termo relacionado, nível superior ao pedido etc.), com indicação de certeza.
- **Categoria de Pontuação**: um grupo de avaliação (Design, Estrutura, Conteúdo) com nota, peso e justificativa.
- **Resultado da Análise**: a pontuação global, as notas por categoria e a lista de requisitos com suas deduções.
- **Idioma da Interface**: a escolha da pessoa entre português do Brasil (padrão), inglês e espanhol. Define o idioma de todos os textos e explicações, e vale durante a sessão.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A pessoa consegue ir da tela inicial ao resultado completo em menos de 3 minutos, incluindo o preenchimento das entradas.
- **SC-002**: 100% dos requisitos apresentados no resultado têm status e justificativa, e 100% dos requisitos sem evidência dizem isso explicitamente.
- **SC-003**: Em um conjunto de pelo menos 20 casos de teste com relações semânticas conhecidas (sinônimos, níveis equivalentes, situação concluída versus em curso), o simulador reconhece corretamente ao menos 90% delas e explica cada uma.
- **SC-004**: Repetir a análise com os mesmos textos na mesma sessão produz pontuação e justificativas idênticas em 100% das tentativas. Entre sessões diferentes, a taxa de vereditos idênticos é medida em um teste com o modelo real e registrada, sem meta de 100%.
- **SC-005**: Em testes de compreensão, ao menos 90% das pessoas conseguem explicar com as próprias palavras por que receberam a nota global e onde poderiam melhorar, olhando só a tela de resultado.
- **SC-006**: Um PDF com texto selecionável gera os mesmos status de requisitos e as mesmas notas de Conteúdo e de Estrutura que o mesmo texto colado, em 100% dos casos. O Design fica de fora da comparação, porque só existe no PDF.
- **SC-007**: Em revisão visual de todas as telas, 100% das cores de identidade são tons de rosa e roxo (fora a escala da barra de progresso e as bandeiras), e cada tela tem ao menos um coração decorativo.
- **SC-008**: Em revisão visual, 100% dos títulos e destaques usam "Tropi Land" e 100% dos textos informativos usam fonte com serifa.
- **SC-009**: Nenhuma pontuação é exibida sem o valor numérico e a justificativa correspondentes, e nenhuma informação da análise depende só da cor.
- **SC-010**: 100% dos textos da interface existem em português do Brasil e têm tradução para inglês e espanhol, e nenhuma tela exibe texto em idioma diferente do escolhido.
- **SC-011**: A troca de idioma é feita em uma única ação a partir de qualquer tela e, em 100% dos casos, preserva o texto digitado, o arquivo enviado e o resultado exibido.
- **SC-012**: Para o mesmo par de textos, a pontuação e os status dos requisitos são idênticos nos três idiomas da interface.
- **SC-013**: Em 100% das telas, nos três idiomas, todos os caracteres dos títulos em "Tropi Land" (incluindo acentos, "ñ" e sinais de pontuação) aparecem corretamente, sem caracteres faltando ou trocados.

## Assumptions

- **Vaga como entrada:** a descrição menciona requisitos da vaga sem dizer como ela é informada. Assume-se que a pessoa cola o texto da vaga em um campo próprio. Enviar a vaga em PDF está fora do escopo desta versão.
- **Design fora do texto colado:** a nota de Design depende do visual do documento, que só existe em PDF. Assume-se que, para currículo colado como texto, a categoria Design é apresentada como "não avaliada" com uma explicação, e a pontuação global é calculada só com as categorias avaliadas. Para PDF, o Design é avaliado pelo aspecto visual do documento enviado.
- **Categorias:** Design, Estrutura e Conteúdo são o mínimo exigido. Assume-se que estas três são as categorias desta versão, com pesos definidos e exibidos ao usuário (FR-013). Categorias adicionais ficam para versões futuras.
- **Exceção à paleta:** a constituição (Princípio III, v1.2.0) restringe as cores de identidade a rosa e roxo e admite duas exceções enumeradas: a escala de dados da barra de progresso e as bandeiras do seletor de idioma. A barra usa o gradiente de **uma única cor de acento** que combine com rosa e roxo, do tom claro (nota baixa) ao intenso (nota alta). Como padrão, assume-se um tom de turquesa ou verde-água, e a matiz exata é definida no design da interface. O gradiente por intensidade também funciona para pessoas com daltonismo.
- **Fonte "Tropi Land":** o arquivo foi fornecido em `font/tropi_land.zip` e contém um único arquivo TrueType, "Tropi Land - (Demo) hanscostudio.com.ttf". Foi verificado que ele cobre as letras acentuadas do português e do espanhol, "ñ", "¿", "¡", dígitos e a pontuação usada em "85/100". Se estiver indisponível, usa-se uma alternativa legível (FR-023).
- **Licença da fonte:** o arquivo é uma versão "Demo" da HansCo Studio (© 2023, todos os direitos reservados), cuja licença é de uso pessoal. Como o simulador é um trabalho acadêmico e não será publicado nem comercializado, a licença de uso pessoal é suficiente. Caso o projeto venha a ser publicado, será preciso adquirir a licença adequada.
- **Corações fora da fonte:** a fonte não tem os símbolos de coração, então os corações decorativos não podem depender dela.
- **Idiomas da interface:** o texto original e padrão é o português do Brasil, com tradução opcional para inglês e espanhol, escolhida pelas bandeiras do Brasil, dos Estados Unidos e da Espanha. Assume-se que as bandeiras servem só para identificar o idioma, sem exigir variantes regionais rigorosas. A troca vale durante a sessão e não muda como a análise é calculada.
- **Idiomas dos documentos:** vaga e currículo podem estar em português, inglês ou espanhol, inclusive um em cada idioma. Outros idiomas estão fora do escopo desta versão. Entre idiomas diferentes, a confiança das deduções pode ser menor e isso é sinalizado (FR-031).
- **Bandeiras e a paleta:** as bandeiras têm cores próprias (verde, amarelo, vermelho, azul etc.) e são símbolos informativos de idioma, e não cores de identidade. Isso está previsto na exceção 2 do Princípio III da constituição.
- **Constituição sobre o idioma:** o português do Brasil é o idioma original e padrão, e a tradução opcional para inglês e espanhol (FR-027 a FR-033) está prevista nas Restrições de Interface e Conteúdo da constituição v1.2.0.
- **Privacidade:** currículos são dados pessoais. Assume-se que o app usa o conteúdo enviado apenas para a análise da sessão atual e não o guarda depois que a pessoa inicia uma nova análise ou encerra a sessão. O texto é enviado a um serviço de IA externo para a análise, o que a pessoa é avisada antes de analisar (FR-034). A retenção de dados pelo serviço externo está fora do controle do app.
- **Repetibilidade entre sessões:** o modelo de linguagem pode variar levemente os vereditos entre sessões, e nenhum resultado é guardado em disco para evitar isso (Privacidade). Isso está registrado nas Clarifications e previsto no Princípio I da constituição v1.2.0: a nota é determinística a partir dos vereditos, a repetição é garantida dentro da sessão e a variação entre sessões é medida e informada.
- **Sem conta de usuário:** não há cadastro, login nem histórico de análises nesta versão.
- **Natureza do resultado:** a pontuação é uma simulação educativa e não representa o resultado de nenhum sistema de recrutamento real. O simulador deixa isso claro à pessoa.
- **Limites de entrada:** o PDF aceita até 10 páginas e 5 MB. O texto do currículo tem de 200 a 60.000 caracteres (acima de 20.000 é analisado em blocos), e o texto da vaga tem de 100 a 20.000 caracteres. Fora desses limites, a mensagem é clara e gentil e nenhuma nota é gerada.

## Conformidade com a Constituição

Constituição v1.2.0 (`.specify/memory/constitution.md`).

- **Princípio I, Transparência Algorítmica:** atendido pelos FR-012 e FR-013 (nota calculada por regras fixas e publicadas, regras e pesos visíveis), FR-016 (a nota global pode ser reconstituída) e FR-034 (aviso de envio a serviço externo). A reprodutibilidade segue as três regras do princípio: nota determinística a partir dos vereditos, repetição idêntica na mesma sessão (FR-012, SC-004) e variação entre sessões medida e informada (SC-004).
- **Princípio II, Explicabilidade por Dedução Lógica:** atendido pelos FR-006 a FR-011 (status, evidência, dedução, ausência de evidência e certeza por requisito), FR-016 (decomposição da nota) e SC-002 (100% dos requisitos com status e justificativa).
- **Princípio III, Paleta em Rosa e Roxo:** atendido pelo FR-021 e pelas duas exceções enumeradas (barra de progresso no FR-017; bandeiras no FR-028), com verificação em SC-007.
- **Princípio IV, Estética Fofa e Acolhedora:** atendido pelos FR-022 e FR-025, sem esconder informação de análise.
