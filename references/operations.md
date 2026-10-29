# Operação em lotes

Consulte esta referência ao planejar, definir orçamento, acompanhar resultados, relatar uma execução, transportar estado sujo ou limpar worktrees.

## Comandos do runner

Use Python 3.9+. No Windows, prefira `py -3` se `python` não estiver no PATH.

~~~text
python scripts/orchestrate.py probe
python scripts/orchestrate.py doctor
python scripts/orchestrate.py strategies
python scripts/orchestrate.py policy show
python scripts/orchestrate.py playbook --pick
python scripts/orchestrate.py playbook scout-then-build
python scripts/orchestrate.py usage
python scripts/orchestrate.py models
python scripts/orchestrate.py scaffold research --workers 3 --cwd .
python scripts/orchestrate.py validate <plan.json>
python scripts/orchestrate.py dry-run <plan.json>
python scripts/orchestrate.py new "Renomear auxiliar de login" --playbook scout-then-build --why "..."
python scripts/orchestrate.py run <plan.json> --in current --detach
python scripts/orchestrate.py wait --timeout 60
python scripts/orchestrate.py budget --max-calls 8 --max-reported-cost-usd 2
python scripts/orchestrate.py note "revisão: diff de três linhas" --kind skip
python scripts/orchestrate.py status
python scripts/orchestrate.py stop
python scripts/orchestrate.py mark <worker> used --why "integrado sem alterações"
python scripts/orchestrate.py report
python scripts/orchestrate.py report <pasta> --format json --write <relatorio.json>
python scripts/orchestrate.py list
python scripts/orchestrate.py use <pasta>
~~~

`doctor` verifica Python, versões e autenticação das CLIs, política salva e orçamento, YAML do usuário e cotas. `loggedIn: null` significa que não foi possível determinar; `hints` explica lacunas. `scaffold` cria plano inicial: substitua tarefas TODO, mantenha `isolate: true` de workers paralelos e informe `--provider` para `rescue` porque uma sessão pertence a uma CLI. `--write <caminho>` salva em vez de imprimir.

`dry-run` valida e mostra estratégia resolvida, provedor efetivo, concorrência, tokens estimados do prompt, orçamento e `listPriceEstimateUsd`, sem iniciar workers ou criar worktrees. Execute antes de estratégia que você não escolheu. `validate` e `dry-run` mostram `warnings` para limite de custo invisível a algumas CLIs, modelo padrão não fixado, excesso de escritores com briefings curtos, Kimi somente leitura, briefing que exige MCP desativado e escritor em checkout sujo. `dry-run` também alerta sobre provedor com pouca cota. Corrija ou justifique. Esforço fixado sozinho não fixa modelo.

## Cotas e preços

Execute `usage` antes de cada onda. Claude vem de `rate_limit_event` dos workers e pode estar antigo; Codex é lido dos arquivos de sessão da própria CLI. `usage --refresh-claude` faz uma chamada Haiku curta. `orquestrador-usage.json` ao lado da política guarda leituras e exemplos para `quotaForecast`. Cada janela tem `usedPercent`, `resetsAt`, `ageMinutes`, `low` (>= `quota.criticalThreshold`), `blocked` (>= `quota.stopAt`), `stale` (>30 minutos) e `reset`. Dados ausentes ou antigos são desconhecidos; informe isso.

`run` recusa provedor bloqueado, indicando janela, percentual e reinício; uma onda em andamento pula workers enfileirados quando o provedor cruza o limite, com `failureKind: quota_low`. Consulte o usuário antes de `--allow-low-quota`, conforme a regra de cotas da skill.

`models` mostra preços, classificação `low`/`mid`/`high`, `asOf` e marcadores `stale` (>60 dias) ou `missing`. `prices.json` usa USD por milhão de tokens com `source` oficial. `orquestrador-prices.json` substitui entradas e guarda `billing` por provedor. Para preço necessário ausente/antigo, consulte apenas a página oficial do fornecedor e registre preço, URL e data sem apagar outros dados. Não adivinhe preço não publicado. Em assinatura, consumo real é cota; em API, é preço. `listPriceEstimateUsd` é estimativa, não cobrança nem gasto informado.

## Execução atual e modo persistente

`new "<título>"` cria pasta sob `orchestrations/` ao lado da política; `ORQUESTRADOR_ORCHESTRATE_HOME` pode substituí-la. Salva título, playbook, motivo e agente principal em `orchestration.json`. `--lead provider:model` fixa quem planejou; sem isso, o runner pode registrar Claude Code sem modelo quando executado dentro dele. `run <plano> --in current` acrescenta ondas `<NN>-<fase>`. Comece cada onda com `--detach` e repita `wait [--timeout N]` até `done: true`; cada espera tem máximo de 540 segundos e deve respeitar o limite do shell. Se houver interrupção, veja `status` antes de recuperar.

`report`, `status`, `budget`, `note`, `stop` e `mark` usam a orquestração atual. `list` mostra as recentes e marca a atual com `*`; `use <pasta>` seleciona outra. `--run-dir <pasta-vazia>` é opção para caminho fixo; sem isso o runner usa diretório temporário exclusivo.

`mode on [--goal save|balanced|max] [--care careful] [--rule TEXT]... [--cwd DIR]` ativa modo por repositório/pasta em `modes.json`. Nova chamada altera só flags informadas; até oito regras se acumulam, e `--clear-rules` limpa. O modo por projeto expira após 12 horas sem prompt. `mode on --everywhere` define padrão global sem expiração; `mode off` no projeto cria exceção local; `mode off --everywhere` remove padrão e exceções. Modo do projeto prevalece e `mode show` indica `source`. `hook` lê JSON do agente em stdin e imprime lembrete apenas quando o diretório está coberto; nunca falha. O plugin Claude Code o executa por prompt.

`note "<texto>" [--kind change|skip|add|switch|lead]` registra mudança e motivo em `journal.jsonl`. `stop` grava arquivo de parada nas ondas: encerra árvores de processos, pula a fila com `failureKind: stopped` e preserva resultados concluídos. Sem Python, não o instale sem permissão: siga [manual.md](manual.md).

## Plano mínimo

~~~json
{
  "version": 1,
  "title": "Adicionar API de exportação",
  "playbook": "plan-big-execute-small",
  "phase": "build",
  "why": "Duas unidades independentes",
  "strategy": "balanced",
  "workers": [
    {
      "id": "api",
      "provider": "auto",
      "mode": "write",
      "cwd": "C:\\work\\project",
      "isolate": true,
      "task": "Implemente a API. Responsável por src/api e tests/api."
    }
  ]
}
~~~

Para instrução longa, use `taskFile`; `cwd` e `taskFile` relativos partem da pasta do plano. `title`, `why`, `playbook`, `phase` e `why` do worker são notas de relatório e não chegam ao worker. Limites: título 120, motivo do plano 500 e motivo do worker 300 caracteres, cada um em uma linha.

`tier: cheap|standard|strong` usa o perfil ativo; substituições legadas da política ainda vencem. Combine `tier` com `provider: auto`; modelo explícito impede isso. Codex e Claude iniciam sem MCP: use `mcp: true` quando necessário. `idleTimeoutSeconds` de 5 a 86400 encerra inatividade; deixe vazio para checagens silenciosas. `provider: auto` respeita a ordem e conservação salvas. Fixe provedor quando solicitado, ao fixar modelo/esforço exclusivo ou ao retomar sessão. `preset` legado ainda funciona; planos novos usam `strategy`. Precedência: `--strategy`, plano, política, `auto`.

## Orçamento

Campos de `budget` são opcionais; ausência significa sem limite:

~~~json
{
  "budget": {
    "maxCalls": 4,
    "maxWallSeconds": 1800,
    "maxEstimatedPromptTokens": 60000,
    "maxReportedCostUsd": 2.5,
    "maxReportedTokens": 400000
  }
}
~~~

`maxCalls` limita processos iniciados; recusados ficam `skipped`. `maxWallSeconds` limita a onda e reduz timeout efetivo de cada worker. `maxEstimatedPromptTokens` compara caracteres/4 do prompt na validação; leitura posterior do repositório não entra. `maxReportedCostUsd` barra workers posteriores pelo custo informado, disponível principalmente no Claude; se a CLI oferecer `--max-budget-usd`, o saldo é repartido entre workers Claude concorrentes. O runner não inicia Claude com menos de US$ 0,01 de saldo. `maxReportedTokens` barra workers posteriores por tokens informados, excluindo leituras de cache e incluindo gravações. Portões são conferidos ao submeter; não cancelam processos já iniciados.

`budget [pasta]` define `--max-calls`, `--max-reported-cost-usd` e `--max-reported-tokens` para todas as ondas em `budget.json`. Sem flags, mostra consumo e saldo; `--clear` remove limites. Execute uma onda de cada vez, pois a contabilização ocorre após conclusão. Padrões da política podem ser substituídos por plano campo a campo. As preferências da interface de orquestração podem controlar backend, estratégia, provedores e concorrência; níveis novos pertencem ao YAML. `state.json` registra orçamento efetivo e `budgetUsage`; métrica não informada fica `null`.

## Arquivos e resultados

~~~text
<pasta>/
|-- budget.json
`-- <NN>-<fase>/
    |-- state.json
    |-- plan.json
    `-- workers/<id>/
        |-- prompt.txt
        |-- stdout.log
        |-- stderr.log
        |-- result.md
        |-- outcome.json
        |-- status.txt
        |-- diff.patch
        `-- mark.json
~~~

`state.json` resume a onda e mostra `outputBytes` e `idleSeconds` durante execução. Sucesso exige conclusão no prazo, saída estruturada válida e resultado final não vazio. Logs brutos são diagnósticos. `outcome.json` inclui `workerStatus`, `workerSummary`, `verdict` (`PASS`, `FAIL`, `NOT_PROVEN`), `failureKind`, `resetHint`, `permissionDenials`, `billedModels`, `readOnlyViolation`, `touchedFiles`, `dirtyBefore`, `costCapUsd`, `diffError` e `sharedCheckoutWith`. `readOnlyViolation: null` indica impossibilidade de determinar, por exemplo em checkout compartilhado. `strategy` e `requestedStrategy` divergem quando `auto` resolve; `requestedProvider` mostra roteamento automático. Status geral: `done`, `partial`, `failed`, `stopped`, `cancelled` ou `interrupted`. `plan.json` não inclui a tarefa; ela fica em `prompt.txt`.

## Relatório e aproveitamento

`report` lê pasta de onda ou orquestração, usando a atual por padrão. Markdown é padrão; `--format json` e `--write` permitem automação. O relatório mostra decisões, tempo, tokens e custo que a CLI informou, pendências e contexto do agente principal. Não estima gasto. Claude pode informar custo equivalente à API mesmo sob assinatura; Codex informa tokens e outras CLIs variam. `--format html` cria página local com totais, mapa de rotas, decisões, tabela de workers e pendências; `--no-open` só grava.

`mark [pasta] <worker> used|partial|discarded [--why TEXT]` registra aproveitamento. Depois da primeira marcação, a linha Valor divide custo e tokens informados entre usados, parciais e descartados e lista os sem marca. Leituras de cache ficam separadas; custo não é recalculado. `status` mostra ondas, orçamento, mudanças, cotas, worktrees abertas, resultados sem marca e pendências. Use-o primeiro após compactação.

## Worktrees, falhas e recuperação

`isolate: true` cria worktree destacada em `.orquestrador/worktrees/` só para escritor. Ela não é removida automaticamente. O runner usa `.git/info/exclude` local, não versionado. Worktrees partem de `HEAD`; `seedPaths` leva apenas caminhos relativos explicitamente listados, aplicando diffs rastreados e copiando arquivos não rastreados. Symlinks são rejeitados. O runner não faz stash nem commit do checkout principal. Inspecione `status.txt` e `diff.patch`, integre mudanças revisadas, valide o conjunto e só então remova a worktree.

Saída não zero, timeout, JSON inválido, erro ou resposta vazia são falhas. Leia `error`, `failureKind` e o fim de `stderr.log`. Tente novamente uma vez apenas após corrigir causa específica: `rate_limited`/`quota_low` pedem espera ou outro provedor; `auth_required`/`not_installed` exigem ação no ambiente; `timed_out`/`stalled` podem usar `rescue` ou escopo menor; `budget`/`budget_exceeded` só elevam limite com autorização. Diff parcial é não confiável até revisão. Não apague mudanças do checkout principal após falha de escritor não isolado sem verificar autoria.
# Registro nativo e relatórios mistos

Consulte [tracing.md](tracing.md) para registrar observações nativas e consultar
orquestrações sem rodadas CLI. Registro é responsabilidade do principal; não
lança nem encerra agentes. Consumo completo pode ser desconhecido e orçamentos
do runner permanecem limitados aos workers CLI gerenciados.
