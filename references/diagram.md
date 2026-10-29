# Diagrama da arquitetura do plano

Quando o usuário pedir a estratégia visual, renderize o dry-run resolvido, não uma configuração idealizada. Identifique agente principal, workers reais, CLI, modelo ou nível conhecido, modo de leitura/escrita, isolamento em worktree e relações entre workers. Mostre proxy como 9router somente se uma rota selecionada realmente o usar. Indique modelos ou rotas desconhecidos em vez de inventá-los.

~~~text
python scripts/orchestrate.py dry-run <plan.json> --write <preview.json>
python scripts/diagram.py <preview.json> <architecture.svg>
python scripts/diagram.py <preview.json> <architecture.svg> --via-9router <worker-id> --upstream <modelo-conhecido>
~~~

diagram.py embute marcas dos fornecedores em SVG autônomo, utilizável offline após a instalação. Passe --via-9router uma vez para cada worker confirmado nessa rota. Omita --upstream se o modelo for desconhecido. Mostre o SVG antes de iniciar o plano e informe o caminho absoluto. O SVG representa uma proposta, não uma sessão em execução.

A visualização deve distinguir delegação e retorno por setas rotuladas. Revisões sequenciais seguem a ordem real das rodadas; ramos paralelos compartilham origem. Use nós retangulares arredondados, setas levemente irregulares e traços discretos inspirados no Excalidraw. Mantenha texto legível e cores coerentes com o aplicativo hospedeiro.

Use marcas oficiais sem alterações apenas quando houver recurso com fonte oficial rastreável. Preserve proporção, respiro e cores aprovadas e registre a fonte. Se a marca não estiver disponível, escreva o nome da ferramenta; não desenhe aproximações. 9router é uma ferramenta de roteamento separada, não a marca do modelo remoto.

Fontes das marcas incluídas:

- OpenAI/Codex: https://openai.com/brand/
- Claude: https://www.anthropic.com/news
- Antigravity: https://www.antigravity.google/press
- Kimi: https://github.com/MoonshotAI/Branding-Guide
- 9router: https://github.com/decolua/9router/blob/master/public/favicon.svg

Um diagrama explica e antecipa. A presença de worker, proxy ou modelo na proposta não prova que foi iniciado. Atualize a visualização após a execução apenas com estado e resultados observados.
