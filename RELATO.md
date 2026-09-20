# Relato (Simulador de ATS)

**Contexto.** O Simulador de ATS recebe vaga e currículo (texto ou PDF) e devolve nota, notas por categoria e por requisito, o trecho do currículo, a dedução lógica e a explicação. A interface foi feita em tons de rosa e roxo (preferência pessoal) e existe a possibilidade de usá-la em três idiomas: PT/EN/ES. Usei o framework de Spec-Driven Development **Spec-Kit do GutHub**: constituição, spec, clarificação, plano, tarefas, análise e só então código, que foi a saída dessas decisões. Comecei com o Copilot no VS Code, mas ele não fazia o que eu queria; apaguei tudo e recomecei do zero com o Claude. Tudo, contando o projeto do Copilot, levou das **9h30 às cerca de 21h30 de 19 de setembro**.

## Registro de mudanças

| O que apareceu | O que mudei |
|---|---|
| Barra laranja–verde contradizia a constituição ("só rosa e roxo") | Gradiente de uma cor (turquesa); FR-017 e constituição v1.1.0 |
| PT/EN/ES pedido depois; emoji de bandeira falha no Windows | US5, FR-027 a 033; bandeiras em SVG (FR-028) |
| "Sempre o mesmo resultado" não vale para um LLM | FR-012, SC-004, constituição v1.2.0: nota determinística, repetição idêntica na sessão, variação medida |
| "Avaliar o Design" é subjetivo e só existe em PDF | Seis critérios mensuráveis; "não avaliada" em texto colado; SC-006 reescrito |
| PDF e chunking sem limites claros | Limites na spec (10 páginas, 5 MB, 20 mil e 60 mil caracteres); PDF ilegível cai em "cole o texto"; evidência tem de ser trecho literal |
| `/speckit-checklist` e `/speckit-analyze` acharam lacunas | FR-034 (aviso de envio a serviço externo), FR-035 (instruções embutidas), conformidade; tarefas de 84 para 89 |
| Sem chave da Anthropic, usei o Gemini; o modelo maior tem cota de 20/dia | Plano e pesquisa D4 reescritos; modelo padrão trocado; meta do SC-003 só para relações positivas (decisão minha) |
| A Tropi Land não aparecia, embora os testes passassem | Só o navegador mostrou (CSS genérico sobrescrevia os títulos). Corrigi o CSS e registrei em `validation.md`; plano e data-model ainda citam `st.radio` e estágio `error` |

## Reflexão crítica

Não escrever o código mudou meu papel: passei a decidir e conferir. O `/speckit-clarify` me fez decidir cinco pontos que eu não tinha visto, e o `/speckit-analyze` achou conflitos entre constituição e spec antes de haver código. Mesmo com 209 testes (executados em parte por mim, em parte pelo Claude), passaram erros: a fonte errada, o cabeçalho cortando as bandeiras, um título duplicado na constituição. Só vi ao comparar com o navegador e com a API real. "A IA fez" não basta; o que garante é a verificação.

Sobre transparência, sistemas de seleção costumam ter problemas de opacidade. Travar as regras na especificação permitiu explicar a nota: a rubrica aparece na tela, a nota sai de código e não do modelo, o modelo só devolve veredito em opções fechadas, todo trecho citado é conferido contra o currículo e a falta de evidência é dita. A pessoa vê por que perdeu pontos e o que melhorar.

Os limites ficam registrados: o veredito depende de um modelo (5 de 5 execuções idênticas e 10 de 10 relações reconhecidas, sem garantia; 18 de 22 no geral, com dúvida entre "parcial" e "não atendido"); o currículo vai para um serviço externo; e o Design mede legibilidade do arquivo, não o valor de quem se candidata.
