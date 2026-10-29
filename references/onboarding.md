# Configuração inicial da orquestração

Use quando o usuário pedir setup ou doctor encontrar política não configurada. O resultado é uma cópia dos playbooks que registra os provedores reais, três perfis aprovados e a forma de cobrança em orquestrador-prices.json ao lado da política. Pergunte apenas o que não puder descobrir; aproveite respostas já dadas ou salvas.

## Quando o usuário pedir para reconfigurar

Refaça descoberta e comparação antes da proposta. Use o cadastro anterior como
referência, sem limitar candidatos aos seus modelos ou apenas mudar esforços
dos mesmos modelos. Preserve restrições explícitas ainda válidas e distinga-as
de uma seleção antiga que nunca foi reavaliada. Uma configuração válida não
significa que ela continua sendo a melhor proposta para o novo setup.

Não apresente a seleção salva como uma nova comparação. Mostre o que mudou,
o que foi mantido e por quê. Não altere a configuração até aprovar a proposta.

## 1. Inventário

1. Execute doctor para Codex, Claude Code, Agy/Antigravity e Kimi Code. Um CLI com loggedIn: false entra nas notas como “fazer login primeiro”, não em providers; executá-lo falharia com auth_required.
2. Procure outros CLIs no PATH, como gemini, kiro-cli, copilot e opencode, e rotas como 9router. Execute --help antes de considerá-los disponíveis. Registre CLIs que não iniciam com a correção necessária. Pergunte se há outro CLI ou roteador a incluir; aceite nome ou caminho do executável.
3. Liste modelos pelo comando do CLI, quando houver, por exemplo agy models ou kiro-cli chat --list-models --format json. Preserve multiplicadores de custo informados. Para Codex, execute `models` e confira `discovery.candidates`, origem/data e `supportedEfforts`: o runner lê models_cache.json sem iniciar sessão. Não use apenas nomes dos playbooks ou da tabela de preços como inventário da conta. Cache ausente, antigo ou sem data não comprova o catálogo atual; procure evidência disponível no host/CLI sem inventar comandos, e informe o que não pôde conferir. O cache sozinho também não comprova acesso da assinatura a cada modelo.
4. Registre adaptador personalizado apenas quando --help confirmar modo de prompt não interativo. Anote o comando verificado; não adivinhe flags nem credenciais. Adaptadores personalizados não impõem leitura isolada, portanto recebem apenas fases de escrita. Consulte [providers.md](providers.md).
5. Execute usage. Claude usa eventos rate_limit_event de workers; Codex usa arquivos de sessão. Para outros provedores, peça uso de cota e fim do plano somente quando a política de cotas exigir. Identifique leituras antigas.
6. Descubra cobrança e plano contratado por provedor em dados locais ou respostas documentadas do CLI/host. `usage` observa `plan_type` quando exposto pela telemetria Codex; isso não revela automaticamente preço, limites ou autorização de extras. Consulte [accounts.md](accounts.md). Pergunte apenas pelos dados ausentes que influenciam a decisão, como plano, capacidades, autorização de extras e preferência de consumo. Ofereça preço como cadastro opcional, explicando em linguagem simples: quanto paga, em qual moeda e se a cobrança é mensal ou anual. Não exija que o usuário descubra limites; use cotas observadas e pergunte por limites desconhecidos somente quando a política exigir. Preserve respostas confirmadas; concilie conflitos com o usuário. Após aprovação, grave `billing` e `accounts` em orquestrador-prices.json, preservando preços existentes. Não deduza capacidade pelo preço nem salve evidência incerta como preferência confirmada.
7. Execute models para preços e níveis relativos low, mid e high. Para preço necessário ausente ou com mais de 60 dias, consulte somente o site oficial do fornecedor, informe o usuário e grave source e asOf. Nunca estime preço.
8. Para gateway como 9router, verifique instalação, execução e quais CLIs o usuário deseja rotear. Ele é um nó próprio no diagrama, não um worker. Consulte configuração ou ambiente antes de chamá-lo de ativo. Não o inicie, instale ou reconfigure.

## 2. Três perfis

Defina os perfis sobre os mesmos playbooks usando apenas modelos encontrados:

Antes de propor os perfis, apresente os candidatos descobertos por provedor,
com origem, atualidade e esforços conhecidos, e considere todos os candidatos
visíveis relevantes. Explique a escolha entre alternativas e o motivo para
descartar algum candidato relevante. Um modelo descoberto sem preço continua
candidato: `priceMissing` e o alias legado `missing` indicam preço ausente,
não indisponibilidade. `rank` mede preço relativo, não capacidade. Em assinatura,
priorize acesso verificado, adequação à tarefa, cotas e consumo observado; não
exclua um modelo apenas por faltar preço de API. Não force um modelo específico
em todos os perfis nem deduza capacidade pelo nome ou pela posição na lista.

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
2. Grave escolhas de cobrança e dados de conta aprovados ainda não salvos em orquestrador-prices.json, conforme [accounts.md](accounts.md). Execute `models` para validar o cadastro e `doctor` para validar os playbooks. Depois use policy set --provider-order com os CLIs embutidos do perfil ativo, ou policy set sem opções quando o padrão servir; isso registra o onboarding como concluído. Preferências só desta rodada não entram na política.
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
