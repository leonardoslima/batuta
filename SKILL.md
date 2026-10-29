---
name: batuta
description: Orquestra agentes Codex, Claude Code, Antigravity, Kimi ou CLIs personalizados em tarefas delimitadas, com controle de cotas, modelos, custos e revisão. Use quando o usuário pedir orquestração, delegação, comparação de agentes, economia de uso, recuperação de workers, relatórios ou configuração do Batuta.
metadata:
  version: "19"
---

# Batuta — orquestração de agentes no Orca ou por CLI

Leia primeiro [references/orca-integration.md](references/orca-integration.md) para execução nativa no Orca. Para a configuração inicial, leia [references/onboarding.md](references/onboarding.md) e preserve todas as perguntas do onboarding original.

Conclua o trabalho com o menor contexto possível no agente principal e com os workers capazes de menor custo, ou com modelos mais fortes quando o usuário pedir. Planeje unidades delimitadas, delegue somente quando compensar e integre resultados com evidências.

- **Playbook:** fases, papéis e verificações.
- **Perfil:** modelos de cada nível em base, savings e aggressive.
- **Objetivo:** intensidade da delegação enquanto um modo está ligado: save, balanced ou max.
- **Estratégia de execução:** composição de uma rodada: economy, balanced, quality, research, parallel ou rescue.

## Escolha da execução

Um pedido explícito pela skill local ou sem MCP prevalece. Nos demais casos, consulte scripts/orchestrate.py policy show: backend skill usa este runner; mcp usa ferramentas compatíveis quando disponíveis; auto as prefere quando existirem. Não presuma que o runner Python inicia agentes nativos do Orca. Consulte a integração para escolher entre delegação nativa e workers CLI.

Python 3.9 ou mais recente é opcional. Se python, python3 e py estiverem ausentes ou abaixo dessa versão, ou se o usuário pedir, siga [references/manual.md](references/manual.md). As demais regras continuam valendo pelas alternativas manuais.

O runner local aceita workers concorrentes delimitados, isolamento opcional em worktrees e sessões retomáveis. Seus workers CLI não aparecem automaticamente no quadro nativo do Orca.

## Primeira execução e configuração

Execute scripts/orchestrate.py doctor se o ambiente puder não estar preparado ou se o usuário perguntar pelo setup. O diagnóstico confere Python, provedores, política, playbooks e leituras de cota.

Se não houver política configurada ou o usuário pedir setup, siga [references/onboarding.md](references/onboarding.md): inventarie CLIs, modelos e rotas; proponha os perfis base, savings e aggressive; obtenha aprovação antes de salvar. Grave somente preferências confirmadas. Um proxy como 9router transporta tráfego e não é worker.

A ausência de setup não bloqueia uma tarefa em andamento: rode doctor, use os CLIs autenticados com os playbooks incluídos, informe isso em uma linha e continue. Ofereça o onboarding depois; não grave preferências antes do aceite.

Interprete pedidos de configuração assim:

| Pedido | Ação |
| --- | --- |
| Economizar um provedor continuamente | Confirme e use policy set --conserve-providers |
| Modelo barato para tarefas pequenas | Confirme provedor e modelo; altere tiers na cópia dos playbooks |
| Limite contínuo de workers, tempo ou custo | Confirme e use as opções max-calls, max-wall-seconds e max-reported-cost-usd da política |
| Limite só desta rodada | Use budget no plano ou --strategy; não altere a política |
| Limite da tarefa inteira | Defina budget antes da primeira rodada |
| Retomar após compactação | Consulte status antes de continuar |
| Voltar aos padrões | Confirme e use policy reset |
| Mudar fases e papéis | Inicialize a cópia com playbook --init e edite-a |
| Trocar o perfil continuamente | Confirme e altere profile na cópia |
| Ver trabalho e gasto | Execute report |

## Comandos curtos

Use $batuta nos ambientes com suporte a skills, ou palavras após “batuta” nos demais ambientes. A integração existente do Claude Code mantém /orchestrator <argumentos>. Esses pedidos correspondem a uma ação. Os apelidos legados “orquestrador” e “alethe” continuam aceitos para compatibilidade. Comandos de rodada sem pasta usam a orquestração atual, criada por new, escolhida por use ou usada pelo último run.

| Comando | Ação |
| --- | --- |
| tarefa em linguagem natural | Orquestre conforme esta skill |
| sem argumentos | status; sem rodada atual, liste os comandos principais |
| on ou instrução contínua | Ligue o modo no projeto |
| always ou on everywhere | mode on --everywhere |
| off | mode off no projeto |
| off everywhere | mode off --everywhere |
| save, balanced ou max | mode on --goal com o valor pedido |
| careful | mode on --care careful |
| report [pasta] | Mostre a saída de report sem reescrevê-la |
| report html | Gere e abra o relatório HTML |
| status | Mostre a saída de status sem reescrevê-la |
| usage | Mostre janelas, resets e atualidade; para Claude desatualizado, usage --refresh-claude |
| models | Mostre preços, níveis e atualidade das fontes |
| editor ou “mostrar playbooks” | Gere e abra o editor visual offline |
| list | Liste rodadas; use <pasta> a torna atual |
| stop | Pare e consulte status após o encerramento |
| budget <limite> | Defina max-calls, max-reported-cost-usd ou max-reported-tokens |
| skip, switch, freeform ou add | Ajuste as fases entre rodadas |
| note <texto> | Registre uma nota |
| mark <worker> used/partial/discarded | Marque o aproveitamento |
| setup | Rode doctor e faça o onboarding se necessário |
| help | Liste brevemente os comandos |

## Modo contínuo

Use-o de forma proativa quando houver unidades independentes delimitadas; mantenha tarefas pequenas ou muito acopladas com o agente principal. mode on --everywhere vale para todos os projetos até ser desligado; mode off cria exceção local. mode on vale para o projeto atual até mode off ou 12 horas sem solicitação. A regra local prevalece sobre a global.

--goal save economiza ao máximo; balanced delega quando compensa; max usa mais capacidade disponível. --care careful exige leitura antes da escrita, isolamento de writers, revisão de cada diff e consulta antes de algo difícil de reverter. --rule guarda até oito instruções do usuário; --clear-rules as remove.

Ligue o modo apenas quando o usuário pedir $batuta on, /orchestrator on ou uma instrução contínua. Traduza a preferência para objetivo e cuidado quando couber; preserve também as palavras do usuário. Confirme o estado em uma linha e retome a tarefa. O hook do Claude Code pode lembrar o modo; sem ele, consulte mode show no começo da sessão e após compactação.

## Entrada em tarefa já iniciada

Continue do estado existente. Use conversa, especificação, plano, lista e diff como plano; aponte workers para arquivos em vez de copiar conteúdos. Preserve fases e verificações do fluxo em andamento. Crie new somente para trabalho delegado; mantenha trabalho pequeno, acoplado ou ambíguo com o agente principal e explique em uma linha.

## Escolha e execução dos playbooks

Antes de planejar, rode scripts/orchestrate.py playbook --pick para ver perfil, ordem, condições e resumos. Depois rode playbook <id> para ver fases, níveis resolvidos, cotas e orçamento. Ambos aceitam --json. O comando playbook sem ID mostra o arquivo completo apenas para edição ou onboarding. Consulte [references/playbooks.md](references/playbooks.md).

Escolha pelo pickOrder. O playbook ou a estratégia nomeados pelo usuário prevalecem. Use complete quando nenhum caso específico servir. Execute fases em ordem: who: lead significa esta sessão; as outras fases formam rodadas de workers. runner define strategy, workers define quantidade, readOnly aplica mode: read-only e isolate separa writers em worktrees.

Pule fases cujo if falhe. Entre alternativas unidas por with, execute a primeira verdadeira. Confira cada gate pessoalmente; se falhar, execute a cadeia after uma vez por unidade e confira novamente. Resolva modelo e esforço pelo perfil ativo e pela primeira regra aplicável. Overrides antigos em policy.modelTiers ainda prevalecem; grave novos tiers somente nos playbooks. Declare modelo e esforço de cada worker e use provedor capaz para leitura isolada. Antes da primeira rodada, diga qual playbook escolheu e por quê.

## Cotas

Antes de cada rodada, consulte usage. Codex usa dados das sessões; Claude usa rate_limit_event dos workers. Se Claude for usado e a leitura estiver ausente ou com mais de 30 minutos, usage --refresh-claude faz uma chamada curta ao Haiku.

Leia quotaForecast em dry-run. Com menos de duas amostras adequadas, trate a previsão como desconhecida. Se o provedor alcançar quota.criticalThreshold, passe a tarefa ao próximo capaz no mesmo nível e informe percentuais e reset em uma linha. Aplique quota.whenSpare quando uma cota de assinatura expiraria sem uso.

Peça decisão antes de iniciar se todos os provedores estiverem baixos, se a alternativa exigir reduzir o nível necessário ou se a previsão ultrapassar quota.stopAt. Informe necessidade, saldo e reset; ofereça esperar, trocar provedor, usar nível menor apenas em unidades seguras, executar somente unidades que caibam ou conectar outro CLI. run --allow-low-quota exige autorização explícita. run recusa provedores no limite e marca unidades pendentes como quota_low; rate_limited indica limite atingido pelo worker.

Um provedor fixado pelo usuário e sua resposta prevalecem. Leituras antigas são incertas, não números atuais. Registre trocas com note "<motivo e leituras>" --kind switch. Consulte [references/playbooks.md](references/playbooks.md) para janelas e previsões.

## Ajustes entre rodadas

Adapte fases, provedores, modelos, estratégias e orçamento ao resultado ou ao pedido do usuário. Registre a alteração antes da próxima rodada para que o relatório a explique: note --kind skip, add, switch ou lead conforme a mudança; use note sem tipo para as demais. Em rodada livre, omita playbook do plano e nomeie phase pelo trabalho. stop interrompe uma rodada inútil sem apagar resultados já produzidos.

## Orquestração

1. Delegue apenas quando compensar. economy e rescue também aceitam um worker. Leia [references/routing.md](references/routing.md) para as estratégias; uma estratégia explícita do usuário vence a preferência salva.
2. Execute scripts/orchestrate.py probe e escolha provedores disponíveis. Leia [references/providers.md](references/providers.md) para Agy, Kimi, retomada de sessão ou CLI personalizado.
3. Atribua arquivos distintos aos writers. Isole writers concorrentes em worktrees; um writer único pode usar o checkout atual preservando alterações existentes.
4. Crie um plano JSON versão 1 fora do repositório. scaffold <strategy> --workers N gera um esqueleto válido. Use provider: auto somente quando a troca aprovada de provedor puder decidir. Coloque limites da rodada em budget; para todas as rodadas, use o comando budget. Inclua title, playbook, phase e why no plano e um why curto em cada worker. Prepare os briefs conforme [references/briefs.md](references/briefs.md). Codex e Claude iniciam sem servidores MCP; mcp: true só quando o brief precisar. Valide pelo esquema ou por validate.
5. Execute models. Para preço necessário ausente ou com mais de 60 dias, consulte apenas a página oficial do fornecedor e registre source e asOf em orquestrador-prices.json; não estime. Confira dry-run: estratégia, provedores, concorrência, tokens, orçamento, listPriceEstimateUsd e quotaForecast. Resolva ou explique alertas. Se o usuário pedir a arquitetura, salve dry-run --write, gere SVG com scripts/diagram.py e mostre antes de iniciar workers; use somente rotas de proxy confirmadas.
6. Crie a rodada uma vez com new "<título>" --playbook <nome> --why "<motivo>" --lead <CLI>:<modelo>. Inicie cada fase com run <plano> --in current --detach e espere com wait --timeout N (até 540 segundos) até done ser true. Nunca use execução em primeiro plano com timeout curto. stop encerra processos remanescentes; o runner limita concorrência e orçamento e mantém worktrees para revisão.
7. Inspecione state.json e cada outcome.json (workerStatus, failureKind e readOnlyViolation primeiro), depois result.md e diff.patch. Logs brutos só para diagnóstico.
8. Integre alterações revisadas, valide o checkout combinado, marque cada resultado como used, partial ou discarded e remova somente dados temporários e worktrees cujo conteúdo útil foi tratado.
9. Encerre com report e mostre trabalho, motivos, mudanças, gasto relatado e pendências. Para exemplos e limpeza, consulte [references/operations.md](references/operations.md).

## Contrato dos workers

Cada brief contém objetivo, definição de conclusão, caminhos sob responsabilidade, regras do repositório, verificações, mudanças proibidas e forma de entrega. O runner exige que o worker não inicie outro Orquestrador ou CLI externo alheio, não faça commit, push, tag, release nem PR, e devolva resumo, evidências, arquivos, verificações, falhas e riscos. A última resposta termina com STATUS: (DONE, DONE_WITH_CONCERNS, BLOCKED ou NEEDS_CONTEXT) e SUMMARY:.

Subagentes nativos podem ser usados dentro do escopo atribuído, sem sobreposição de escrita. ORQUESTRADOR_ORCHESTRATE_WORKER=1 impede uma segunda orquestração; o alias legado continua aceito. Confira o diff mesmo se o worker declarar sucesso. Briefs de revisão, validação e julgamento seguem [references/briefs.md](references/briefs.md).

Nunca coloque segredos em planos, tarefas, argumentos ou logs. Flags que removem isolamento exigem pedido explícito; workers personalizados precisam de allowUnsafe: true para flags sabidamente inseguras.

## Economia de tokens

- “Poucos tokens”, “economize cota” e similares significam strategy economy nesta rodada. policy set economy persiste só quando o usuário pedir.
- budget limita chamadas, tempo, tokens estimados de prompt, tokens relatados e custo relatado. Confira dry-run antes de executar. Apenas Claude relata custo; maxReportedTokens limita os demais. Leituras de cache são contabilizadas à parte.
- Mais workers gastam mais cota total. auto escolhe execução direta quando delegar custaria mais; se o usuário pediu orquestração, escolha a menor estratégia válida.
- Aponte para arquivos em vez de copiar conteúdos. Leia resultados curtos e diffs, não transcrições. Reuse sessionId apenas em acompanhamentos focados.
- Faça uma única tentativa adicional para um worker que falhou somente se houver causa concreta e corrigível.

Não faça commit, push, tag, release nem abra PR sem pedido explícito do usuário.
