# Orquestração sem Python

Use este procedimento para workers CLI quando Python 3.9+ não estiver disponível
ou o usuário dispensar essa dependência. Para agentes nativos disponíveis, siga
[native-execution.md](native-execution.md) sem exigir Python. As regras comuns
de [SKILL.md](../SKILL.md) e o contrato de workers CLI em
[cli-workflow.md](cli-workflow.md), seção Contrato dos workers, continuam válidos.

## 1. Detectar

Confira versões de Python e dos CLIs pertinentes, autenticação por estado local
ou comando documentado que não inicie worker, raiz e estado do Git e roteadores
configurados. Instalação não comprova autenticação. Uma tarefa curta de prova
só cabe dentro da autorização de execução existente; não a inicie apenas para
descobrir a conta. Não inicie nem altere roteadores para sondá-los. No Windows,
a cópia do usuário fica em `%APPDATA%\Orquestrador\orquestrador-playbooks.yaml`;
em outros sistemas, em `~/.config/orquestrador/orquestrador-playbooks.yaml`.
Sem cópia, leia `playbooks.yaml` da skill.

Leia primeiro perfil, provedores, `pickOrder` e resumos. Depois, somente o playbook escolhido, níveis efetivos e cotas. Leia todo o YAML para edição ou onboarding. Substituições legadas em `policy.modelTiers` ainda prevalecem; grave níveis novos somente na cópia do YAML. Sem configuração salva, siga [onboarding.md](onboarding.md) antes de gravar.

## Cotas e preços

Antes de cada onda, leia o `rate_limit_event` mais recente de cada worker Claude e os dados de cota nos arquivos de sessão do Codex. Codex pode ser lido diretamente; Claude depende do último evento. Mantenha por janela `usedPercent`, `resetsAt`, `ageMinutes`, `low` (>= `quota.criticalThreshold`), `blocked` (>= `quota.stopAt`), `stale` (>30 minutos) e `reset` em `orquestrador-usage.json`. Ausência ou leitura antiga significa desconhecido. Para atualizar Claude, uma chamada Haiku de uma linha com `--output-format stream-json --verbose` pode produzir um novo evento. Peça leitura de provedores sem fonte local confiável ao usuário.

Aplique `quota.whenLow` no mesmo nível e `quota.whenSpare` quando uma janela for reiniciar. Não inicie worker bloqueado; confira cada worker da fila. Informe no máximo uma linha de cotas por onda e registre troca e motivo em `state.md`. Use consumo de ondas anteriores para estimar a próxima. Consulte o usuário nas decisões de limite descritas pela skill.

Leia `prices.json` com as substituições de `orquestrador-prices.json`. Preços são em USD por milhão de tokens, com URL oficial e `asOf`. Marque preço ausente ou antigo (>60 dias); pesquise apenas na página oficial do fornecedor antes de atualizar a cópia. Não invente preço não publicado. No onboarding, pergunte cobrança `subscription` ou `api` uma vez por provedor e preserve respostas. Prévia em USD é estimativa de tabela; relatório usa apenas métricas informadas pelas CLIs.

## 2. Escolher o fluxo

Antes da primeira onda, apresente duas a quatro opções concretas baseadas em `pickOrder` e no ambiente: execução direta, leitura paralela, escrita em worktrees ou runner Python. Diga quem faz cada parte e o motivo. Se o usuário já escolheu playbook, estratégia ou provedor, prossiga com a escolha.

## 3. Preparar a execução

Crie `<pasta>/<NN>-<fase>/<worker-id>/` fora do repositório. Em cada pasta, grave
`task.md` com o briefing de [briefs.md](briefs.md), as regras comuns de
[SKILL.md](../SKILL.md) e o contrato de [cli-workflow.md](cli-workflow.md),
seção Contrato dos workers, incluindo `STATUS:` e `SUMMARY:`. Para escritores
concorrentes, crie uma worktree por worker sob `.orquestrador/worktrees/` e,
se preciso, inclua `/.orquestrador/worktrees/` em `.git/info/exclude`.
Inspecione o estado sujo antes.

## 4. Iniciar workers

Inicie processos em segundo plano com `ORQUESTRADOR_ORCHESTRATE_WORKER=1`; leia o prompt de `task.md`, envie stdout a `out.jsonl` e stderr a `err.log`. Fixe modelo e esforço; execute até quatro workers por onda e defina prazo por processo. Use os comandos e permissões de [providers.md](providers.md). Confira `--help` para flags incertas. Não use bypass de permissões sem pedido do usuário.

## 5. Conferir resultados

Claude: último evento `result`, `usage`, `total_cost_usd`, `modelUsage` e `session_id`. Codex: `result.md`, `usage` de `turn.completed` e `thread_id` de `thread.started`. Agy: `result` e, se houver, métricas e `conversation`. Kimi: última mensagem e métricas/sessão quando houver. Leia apenas o necessário, nunca o stream inteiro.

Separe leituras de cache: no Codex, subtraia `cached_input_tokens` de `input_tokens` para a parcela sem cache; Claude informa `cache_read_input_tokens` separadamente. Gravações de cache continuam no total. Exclua leituras de cache de `maxReportedTokens` e da divisão de valor, sem recalcular custo informado.

Confira `STATUS:`, diff e checagens próprias. O estado declarado pelo worker não prova correção. Escrita de worker somente leitura é falha. Erro 429 ou limite de uso move a unidade para o próximo provedor capaz no mesmo nível, conforme `quota.whenLow`.

## 6. Integrar e relatar

Aplique diffs aceitos, execute checagens no checkout combinado e só então remova worktrees e branches cujas mudanças foram tratadas. Registre `report.md` com worker, CLI/modelo, motivo, estado, tempo, tokens, cache, custo informado e aproveitamento. Separe resultados usados, parciais e descartados. Custo ausente continua ausente; prévia não vira gasto medido.

Para página manual, grave `report.json` com os dados observados e substitua `__REPORT_JSON__` em `assets/report.html`; escape `</` como `<\/` e use `null` para dados não informados. Para editor, substitua `__PLAYBOOKS_YAML__` em `assets/editor.html` pelo YAML efetivo e escape `</script` como `<\/script`. Abra a página e confira erros de YAML.

Sem runner, conte chamadas e orçamento em `state.md` após cada onda; estime tokens do prompt como caracteres/4 apenas na prévia. Para `report`, `status`, `usage`, `models`, `list`, `use`, `stop`, `budget`, `note` e `mark`, mantenha os resultados e decisões no estado manual. Para `on`/`off`, preserve o modo na conversa e confirme depois de compactação. `setup` inicia pela detecção e segue o onboarding.
