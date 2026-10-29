# Integração com Orca

Esta skill mantém o comportamento do Orquestrador v19 e acrescenta uma adaptação pequena ao Orca. Leia [onboarding.md](onboarding.md) para as perguntas originais do primeiro setup. Preserve playbooks, editor, relatório, cotas, orçamentos, provedores e salvaguardas, salvo exceção explícita abaixo.

## Descubra o ambiente antes de executar

- Orca é o aplicativo hospedeiro, não necessariamente o backend de execução dos agentes.
- No início de cada tarefa, descubra as ferramentas e capacidades reais expostas pelo Orca e pelo runtime do agente. Não presuma nomes de API, verbos CLI, modelos, níveis de esforço nem comandos de shell por documentação ou sessões anteriores.
- Use workspace, worktree, terminal, navegador e agentes gerenciados pelo Orca quando existirem, forem permitidos e fizerem sentido. Não crie outro gerenciador para checkout ou sessão já pertencente ao Orca.
- Se a delegação nativa estiver realmente disponível, o agente principal pode usá-la diretamente com os playbooks, limites de escopo e verificações desta skill. O runner Python não inicia agentes nativos do Orca; não o apresente como se fizesse isso.
- O runner CLI original continua disponível para workers externos e não desativa artificialmente subagentes nativos dentro deles.
- Prefira delegação nativa quando o fluxo exigir subagentes nativos. Nos demais casos, escolha conforme tarefa, preferência do usuário, suporte, isolamento e recursos. Não substitua silenciosamente agentes nativos exigidos por workers CLI.
- Um worker pode usar subagentes aninhados apenas dentro de seu escopo. Ele responde por todos os descendentes. Não execute novamente o Orquestrador dentro de um worker nem inicie outro CLI de agente alheio. Evite responsabilidades de escrita sobrepostas e respeite permissões, cotas e concorrência do host.
- A telemetria de cota e custo do runner original pode não incluir descendentes nativos. Declare essa lacuna e não afirme que os limites rígidos os cobrem.

## Setup e perguntas originais

Ao receber $batuta setup ou /orchestrator setup, leia [onboarding.md](onboarding.md) por completo:

1. Inspecione ferramentas de agentes do Orca, CLIs locais, autenticação, modelos, capacidades, cotas disponíveis e gateways configurados.
2. Pergunte por CLIs adicionais somente quando a descoberta não os encontrar; confira como são usados.
3. Para cada provedor sem resposta salva, pergunte se a cobrança é por assinatura ou API.
4. Proponha base, savings e aggressive com modelos e níveis de esforço encontrados; mostre a tabela concreta de rotas e modelos e peça aprovação antes de gravar.
5. Pergunte se o modo deve valer globalmente e ofereça a prévia visual original.
6. Preserve o editor offline de playbooks e o relatório HTML.

Se o Orca oferecer ferramenta de perguntas interativas, use-a; caso contrário, converse normalmente. Sem ferramenta suficiente, explique precisamente o que não pôde verificar. Não invente modelos descobertos nem declare setup concluído.

## Sessões nativas e relatórios

O relatório CLI cobre apenas rodadas CLI. Para sessões nativas, forneça resumo separado com evidências ou use o relatório do host. Não invente tokens, provedores nem duração e não rotule sessões nativas como rodadas CLI. Preserve o editor e o relatório HTML originais para rodadas CLI; a unificação com sessões nativas não é garantida.

## Relação com fluxos do projeto

Um fluxo específico, como muvit-autonomous, controla seleção de tarefas, planejamento, ambiente, QA, PR e ciclo de revisão. Respeite seus gates mesmo quando um playbook genérico sugerir uma política de retry menor.
