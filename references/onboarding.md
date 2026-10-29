# Configuração inicial da orquestração

Use quando o usuário pedir setup ou doctor encontrar política não configurada. O resultado é uma cópia dos playbooks que registra os provedores reais, três perfis aprovados e a forma de cobrança em orquestrador-prices.json ao lado da política. Pergunte apenas o que não puder descobrir; aproveite respostas já dadas ou salvas.

## 1. Inventário

1. Execute doctor para Codex, Claude Code, Agy/Antigravity e Kimi Code. Um CLI com loggedIn: false entra nas notas como “fazer login primeiro”, não em providers; executá-lo falharia com auth_required.
2. Procure outros CLIs no PATH, como gemini, kiro-cli, copilot e opencode, e rotas como 9router. Execute --help antes de considerá-los disponíveis. Registre CLIs que não iniciam com a correção necessária. Pergunte se há outro CLI ou roteador a incluir; aceite nome ou caminho do executável.
3. Liste modelos pelo comando do CLI, quando houver, por exemplo agy models ou kiro-cli chat --list-models --format json. Preserve multiplicadores de custo informados. Leia models_cache.json no diretório do Codex, em vez de iniciar uma sessão só para descobrir modelos.
4. Registre adaptador personalizado apenas quando --help confirmar modo de prompt não interativo. Anote o comando verificado; não adivinhe flags nem credenciais. Adaptadores personalizados não impõem leitura isolada, portanto recebem apenas fases de escrita. Consulte [providers.md](providers.md).
5. Execute usage. Claude usa eventos rate_limit_event de workers; Codex usa arquivos de sessão. Para outros provedores, peça uso de cota e fim do plano somente quando a política de cotas exigir. Identifique leituras antigas.
6. Pergunte uma vez por provedor se a cobrança é assinatura ou API. Após aprovação, grave billing com subscription ou api em orquestrador-prices.json, preservando preços existentes. Em assinatura, acompanhe o percentual da cota; em API, o preço do modelo. Não pergunte novamente por escolhas já salvas.
7. Execute models para preços e níveis relativos low, mid e high. Para preço necessário ausente ou com mais de 60 dias, consulte somente o site oficial do fornecedor, informe o usuário e grave source e asOf. Nunca estime preço.
8. Para gateway como 9router, verifique instalação, execução e quais CLIs o usuário deseja rotear. Ele é um nó próprio no diagrama, não um worker. Consulte configuração ou ambiente antes de chamá-lo de ativo. Não o inicie, instale ou reconfigure.

## 2. Três perfis

Defina os perfis sobre os mesmos playbooks usando apenas modelos encontrados:

| Perfil | Níveis | Ordem | Cota baixa | Parada |
| --- | --- | --- | --- | --- |
| base | Modelo usual por nível | CLIs principais do usuário primeiro | 80% | 95% |
| savings | Um passo mais econômico por nível; baixo multiplicador e cotas separadas para volume | CLI capaz mais econômico primeiro, assinatura escassa por último | 70% | 90% |
| aggressive | Um passo mais forte por nível; xhigh só em escalonamento | CLIs mais fortes primeiro | 95% | 98% |

Prefira modelos explícitos. Se o usuário escolher o padrão do CLI, deixe model vazio e explique o alerta de validate/dry-run, mesmo com effort definido. Só atribua leitura isolada a CLI que a implemente. Grave tiers na cópia dos playbooks, nunca em policy.modelTiers ou pelo caminho legado policy set --cheap-model; overrides legados já existentes ainda prevalecem.

## 3. Aprovação

Resuma provedores encontrados, excluídos com motivo e rotas. Mostre uma tabela com os três perfis e modelo de cada nível em cada CLI. Recomende um e pergunte qual perfil deve ficar ativo. Aplique mudanças e mostre a tabela novamente. Não salve nem inicie workers antes da aprovação.

## 4. Gravação

1. Execute playbook --init; use --force somente após aprovação para substituir cópia existente. Edite setup (data e notas), providers, models, adapters, routes, tiers, profiles e profile conforme [playbooks.md](playbooks.md).
2. Grave escolhas de cobrança aprovadas ainda não salvas em orquestrador-prices.json. Execute doctor para validar os playbooks. Depois use policy set --provider-order com os CLIs embutidos do perfil ativo, ou policy set sem opções quando o padrão servir; isso registra o onboarding como concluído. Preferências só desta rodada não entram na política.
3. Pergunte uma vez se a orquestração deve ficar ligada em todos os projetos. Com resposta positiva, execute mode on --everywhere. Sugira objetivo save com savings, max com aggressive e balanced com base. O objetivo controla intensidade da delegação, independentemente dos modelos. É possível desligá-lo por projeto.
4. Ofereça a prévia visual do perfil ativo.

Mais tarde, a troca contínua para savings ou aggressive exige confirmação; uma troca só desta rodada não altera a cópia.

## Estratégias iniciais

São pontos de partida, não promessas de disponibilidade ou menor preço. Rode probe antes de escolher um worker; o CLI local e o pedido do usuário prevalecem.

| Finalidade | Estratégia sugerida | Provedor típico |
| --- | --- | --- |
| Economizar uso | Uma leitura ou escrita delimitada, economy, nível barato | Primeiro CLI preferido disponível |
| Trabalho cotidiano | Duas unidades independentes, balanced | Dois CLIs, ou duas unidades isoladas no mesmo CLI |
| Revisão independente | Escrita, revisão e correção se necessário, quality | Outro CLI disponível para revisão, quando possível |
| Comparar conclusões | Duas ou mais leituras independentes, research | CLIs disponíveis com visões distintas |
| Alterar módulos independentes | Writers com arquivos distintos e worktrees isoladas, parallel | CLIs capazes de escrever |
| Recuperar sessão | Um worker retomado, rescue | Mesmo CLI da sessionId |

9router transporta o tráfego de API do agente e pode aparecer entre CLI e modelo remoto. Não substitui o adaptador nem identifica necessariamente qual modelo remoto atendeu uma chamada.
