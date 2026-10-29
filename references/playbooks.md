# Referência do arquivo de playbooks

Leia esta referência para escolher fases ou editar playbooks. O procedimento
das fases independe do backend. Na execução nativa, consulte perfil, `pickOrder`
e resumos na cópia configurada do YAML; sem cópia, use `playbooks.yaml` da skill.
Depois leia somente o playbook escolhido, seus tiers, condições e gates.

Com o runner CLI, `python scripts/orchestrate.py playbook --pick` mostra perfil
ativo, ordem dos provedores, condições e resumos. `playbook <id>` mostra somente
o playbook escolhido, tiers resolvidos, ordem, cotas e orçamento. Ambos aceitam
`--json`. `playbook` sem ID mostra o arquivo inteiro apenas para edição ou
onboarding. `playbook --init` cria uma cópia ao lado da política; apagar essa
cópia restaura os padrões. `doctor` valida a cópia. Esses comandos não iniciam
agentes nativos. Veja [onboarding.md](onboarding.md) somente para configuração.

## Aplicação das fases em qualquer backend

Escolha por `pickOrder`, respeitando playbook ou estratégia pedidos pelo usuário;
use `complete` quando nenhum caso específico servir. `who: lead` é a sessão
principal; os demais papéis são unidades delegadas no backend escolhido.
Execute fases em ordem, pulando `if` falso. Em alternativas condicionais unidas
por `with`, escolha a primeira verdadeira. O principal verifica cada `gate`;
se falhar, execute a cadeia `after` uma vez por unidade e confira novamente,
preservando gates adicionais do projeto. `readOnly`, `workers` e `isolate`
expressam restrições e quantidade, não verbos de uma API nativa.

Resolva modelo/esforço pelo perfil ativo e primeira regra aplicável; overrides
legados de `policy.modelTiers` ainda prevalecem. Novos tiers pertencem ao YAML.
Declare as escolhas e o motivo do playbook antes da primeira rodada. Se o host
não suportar uma restrição necessária, informe a lacuna antes de delegar; não
afirme isolamento ou leitura protegida sem evidência.

## Editor

editor grava orquestrador-playbooks.html ao lado da política (ou em --out <arquivo>) e o abre; --no-open apenas grava. Cada fluxo mostra condições, fallbacks e modelos resolvidos no perfil escolhido. O cenário now usa a leitura recente de cota; demais presets e controles simulam. Mudanças na página não alteram a configuração até o usuário copiar ou baixar o YAML, salvá-lo sobre a cópia e executar doctor. A página funciona offline; [manual.md](manual.md) explica a substituição manual. Para workers de um plano específico, use [diagram.md](diagram.md).

## Campos principais

| Campo | Significado |
| --- | --- |
| setup | Data da aprovação e notas do onboarding |
| principles | Regras de economia válidas para todos os planos |
| providers | CLIs aprovados, na ordem base |
| models | IDs listados por CLI, opcionalmente com multiplicador cost |
| adapters | Adaptadores personalizados verificados |
| routes | Gateways de tráfego, como router9 |
| tiers | Modelo e esforço de cheap, standard e strong por provedor |
| quota.criticalThreshold | Percentual em que uma janela principal fica baixa |
| quota.stopAt | Percentual que impede novas rodadas e unidades pendentes; no mínimo criticalThreshold |
| quota.whenLow | switch-provider troca no mesmo tier; keep mantém |
| quota.onBothCritical | ask, run-cheapest ou block quando todos estiverem baixos |
| quota.whenSpare | spend-strong, prefer ou ignore para cota que expiraria |
| quota.spareWithinHours | Janela de tempo até reset que conta como cota a perder |
| quota.spareMinLeft | Percentual mínimo restante para cota a perder |
| quota.planEnds | Data de fim de um plano sem renovação por provedor |
| budget.warnAt, budget.whenLow | Alerta e reação a orçamento baixo |
| profile, profiles | Perfil ativo e conjuntos de overrides |
| pickOrder | Seleção de playbook, de cima para baixo |
| playbooks | Fases por ID de playbook |
| routing | Roteamento opcional por tipo/esforço, exportado pelo editor |

## Provedores e rotas

As referências a `usage`, `models`, `dry-run`, `note` e arquivos de telemetria
nesta página descrevem o runner CLI. Na execução nativa, confira as mesmas
restrições usando evidências disponíveis no host e registre decisões na sessão;
não rode esses comandos como pré-requisitos. Métricas ou previsões que o host
não expuser permanecem desconhecidas, sem afirmar limites rígidos equivalentes.

Plano contratado, capacidades e preferência de consumo ficam em `accounts` no
arquivo local de preços, conforme [accounts.md](accounts.md). Consulte `usage`,
`models` e `accounts` no `dry-run` antes de definir a rodada. Previsões usam
histórico compatível com o contexto do plano, sem inferir capacidade pelo preço.

claude, codex, agy e kimi têm adaptadores embutidos. CLIs adicionais usam provider custom e entradas em adapters:

| Campo | Significado |
| --- | --- |
| command, args | Executável e argumentos anteriores ao prompt |
| promptTransport, outputFormat | stdin/argument e text/json/jsonl |
| modelFlag, effortFlag | Flags de modelo e esforço, quando existirem |
| checked | Comando --help que confirmou o adaptador e data |

Custom não garante leitura isolada; auto não lhe atribui fase readOnly. Insira modelo/esforço por suas flags. routes.router9 registra port, running e carries. A rota leva tráfego de API, não é worker; modelos podem ser remapeados pelo gateway. Não inicie, instale ou reconfigure a rota.

## Perfis e fases

O perfil ativo substitui order, quota e tiers sem alterar as fases. Provedores omitidos em order ficam por último. base geralmente não tem overrides. Confirme mudanças contínuas antes de alterar profile. Overrides legados policy.modelTiers ainda prevalecem; policy set --cheap-model é caminho antigo.

Os tiers distribuídos não predefinem modelos ou esforços. A pesquisa descrita
em [research.md](research.md) e a tarefa resolvem essas escolhas antes da rodada;
uma cópia pessoal aprovada pode registrá-las. Reavalie configurações antigas no
setup/reconfiguração sem sobrescrevê-las automaticamente. O runner continua
aceitando cópias antigas e escolhas explícitas do padrão do CLI.

Cada fase contém:

| Campo | Significado |
| --- | --- |
| id, role | Identificador único e papel mostrado |
| who | lead é a sessão atual; demais papéis são workers |
| tier | cheap, standard ou strong resolvido pelo perfil |
| provider | auto escolhe o primeiro capaz; ID fixa provedor |
| model, effort | Override da fase |
| readOnly, workers, isolate | Leitura isolada, número de unidades e worktree própria |
| runner | strategy da rodada: economy, balanced, quality, research, parallel ou rescue |
| does, returns, limit | Trabalho, resultado e limite do brief |
| gate | Verificação feita pelo agente principal |
| if | Condição para executar |
| with | Une caminhos; quando há condições, a primeira verdadeira vence; sem condições, rodam juntos |
| after | Roda após falha no gate ou fase de escalonamento |
| then | next, recheck ou done |
| rules | Escolhas de modelo em ordem; primeira condição verdadeira vence |

## Resolução do modelo e da cota

Para cada worker, parta de tier, provedor, perfil e ordem ativos. Aplique a primeira regra correspondente. Ignore regra cujo modelo pertença a outro provedor salvo quando ela também fixa esse provedor. Antes de cada rodada, execute usage; se o provedor estiver baixo e não fixado pelo usuário, escolha o próximo capaz no mesmo tier. Nunca rebaixe tier sem consultar. Quando todos estiverem baixos ou quotaForecast atingir stopAt, consulte conforme onBothCritical. Aplique whenSpare sob qualquer objetivo, perfil ou estratégia; entre cotas a perder, priorize a que expira primeiro.

O agente principal adapta o plano antes da execução; o runner não troca automaticamente por cota durante a rodada. Ele impõe stopAt e pode pular unidades pendentes como quota_low. run --allow-low-quota só com autorização explícita. Informe até uma linha de cota por rodada e registre trocas com note --kind switch. Modelo vazio usa o padrão do CLI e gera aviso em validate e dry-run.

## Janelas e previsões

| Provedor | Janelas principais | Ciclo de cota a perder |
| --- | --- | --- |
| claude | 5h, week; opus adicional | week |
| codex | 5h, week | week |
| agy | gemini, claude; gpt adicional | nenhum |
| kimi | 5h, week; month adicional | week |
| kiro | credits | créditos mensais |
| copilot | premium | solicitações mensais |
| gemini | day | nenhum |

usage lê Claude pelo rate_limit_event de workers e Codex por arquivos de sessão, sem iniciar worker. usage --refresh-claude faz uma chamada curta. Leituras ficam em orquestrador-usage.json. Cada janela informa usedPercent, resetsAt, ageMinutes, low, blocked, stale e reset. Uma leitura com mais de 30 minutos é antiga; consumo anterior ainda bloqueia até passar resetsAt. A janela opus bloqueia apenas workers Opus.

Após cada rodada, o runner guarda até 40 amostras de consumo por janela. Uso simultâneo da conta pode superestimar a amostra. dry-run calcula quotaForecast pela mediana de workers do mesmo modelo ou provedor; menos de duas amostras deixam a previsão desconhecida. Para Agy, Kimi e outros provedores, leituras podem depender do host ou do usuário. Dados ausentes/antigos não provam capacidade disponível.

Cota spare requer provedor não baixo, ao menos spareMinLeft restante e vencimento do plano antes do reset ou reset dentro de spareWithinHours. Assinatura não gera cobrança adicional por API ao gastar essa cota; cobrança por API continua usando o preço do modelo. Veja [operations.md](operations.md).

## Condições

if recebe uma condição ou lista em que todas devem ser verdadeiras. Prefixe not para negar. <provider> é ID e <window> uma janela da tabela.

| Condição | Quando vale |
| --- | --- |
| narrow | Tarefa clara e pequena, até cerca de três arquivos |
| risky | Contrato de API, schema/migration, autenticação, criptografia, segredos ou exclusão de dados; julgue pela operação |
| kind:<kind> | research, code, review, command, scrap ou docs |
| light, standard, deep | Classe de esforço da unidade |
| <provider>-low | Janela principal fresca acima de criticalThreshold, provedor conservado ou aviso do usuário |
| all-low, both-low | Todos os provedores estão baixos |
| <provider>-above:<n> | Janela principal mais ocupada acima de n% |
| <provider>-<window>-above:<n> | Janela específica acima de n% |
| <provider>-spare | Há cota que seria perdida |
| budget-low | Uso acima de budget.warnAt |
| checks-failed, checks-failed-twice | Verificação falhou uma ou duas vezes |
| report-weak, conflict, stuck | Relatório sem evidência, relatos contraditórios ou decisão pendente |
| no-pass, findings-left | Nenhuma tentativa passou ou achados confirmados restam |

Condições de Codex e Claude usam usage quando a leitura for recente. Outras cotas dependem do host ou do usuário. Dados antigos/ausentes não satisfazem above ou spare; conserveProviders e aviso explícito ainda tornam o provedor low. Spare exige horário de reset; fim de plano vem de quota.planEnds ou do usuário. Ignore data já vencida. O agente principal julga condições de tarefa e resultados com evidências; orçamento usa gasto registrado.
