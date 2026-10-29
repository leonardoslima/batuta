# Onboarding and Agent Tracing Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for the isolated onboarding test task; execute tracing and integration inline with TDD, then review the full diff independently.

**Goal:** Verificar o onboarding pelos comandos públicos e reunir observações nativas/CLI sem inventar métricas.

**Architecture:** Novo módulo Python de registro validado, carregado pelo runner por caminho relativo. Uma lista normalizada de agentes é adicionada aos relatórios sem mudar os totais CLI. Um único agente principal registra snapshots nativos por comando explícito.

**Tech Stack:** Python 3.9+, biblioteca padrão, unittest, JSON e HTML offline existente.

**Spec:** ../specs/2026-10-29-onboarding-tracing-design.md (aprovada pelo usuário).

## Global Constraints

- Sem commit/push ou atualização global sem novo pedido do usuário.
- Sem chamadas pagas, contas reais ou API nativa presumida nos testes.
- Preservar configuração e totais CLI existentes; não somar consumo nativo.
- Ausência de informação não significa zero, conclusão ou falha.
- Um escritor por orquestração; workers não escrevem o registro compartilhado.

## Review Focus

- IDs repetidos entre rodadas, vínculos CLI, snapshots repetidos/antigos e tentativas distintas.
- Pais ainda não registrados, ciclos e referências externas inválidas.
- Consumo inclusivo, equivalência de API e moeda/escopo desconhecidos.
- Relatório sem ondas CLI, compatibilidade e renderização segura de campos externos.
- Fluxos de configuração simulados sem alegar validar consentimento real de conversa.

## Tarefa 1: Contrato de rastreabilidade

**Files:** scripts/agent_trace.py; upstream-tests/test_agent_trace.py.

- [x] Escrever e executar testes inicialmente falhos para identidade, snapshots, parentesco e métricas.
- [x] Implementar validação, leitura e gravação atômica do arquivo agents.json.
- [x] Expor API record(folder, observation), read(folder), cli_key(run, worker), native_key(host, id, attempt), agent_list(runs, folder).
- [x] Campos nativos: version=1, host, id, attempt (inteiro >=1, padrão 1), parent (lead ou referência host/id/attempt), provider/model/effort/task/result opcionais, status, observedAt, source, metrics opcionais, cliRef opcional (run/worker).
- [x] Métricas tokens/cost: value, scope (self/descendants/unknown); custo inclui currency e basis (reported-expense/api-equivalent/unknown).
- [x] Testar erros de fronteira, idempotência, ordem temporal e estado terminal.

## Tarefa 2: Runner e relatórios

**Files:** scripts/orchestrate.py; assets/report.html; upstream-tests/test_trace_reports.py.

- [x] Reproduzir ausência de comando e relatório nativo nos testes.
- [x] Adicionar trace record <arquivo> --in <pasta> e trace list --in <pasta>, com current como padrão.
- [x] Acrescentar agents e agentCoverage aos relatórios, mantendo runs/totals legados.
- [x] Permitir relatório somente nativo, preservar CLI e expor cobertura individual.
- [x] Renderizar tabela comum e lacunas em Markdown/HTML, sem somar métricas nativas.

## Tarefa 3: Onboarding determinístico e avaliação comportamental

**Ownership:** worker exclusivo de upstream-tests/test_onboarding_flow.py e references/onboarding-evaluation.md; não editar runner ou outros testes.

- [x] Testar doctor/models/playbook --init/policy set/validate/dry-run, com persistência/releitura simulando aprovação.
- [x] Cobrir cenários multi-provedor, modelos novos sem preço, cache antigo/ausente, sem rede e reconfiguração.
- [x] Demonstrar leituras não destrutivas, escolhas explícitas preservadas e dados opcionais desconhecidos.
- [x] Preparar roteiro offline para avaliar comportamento do agente sem afirmar que os testes Python provam obediência de LLM.

## Tarefa 4: Documentação e verificação

**Files:** SKILL.md; references/tracing.md; references/orca-integration.md; references/operations.md; README.md; .gitignore.

- [x] Documentar registro pelo principal, limitações de host, cobertura, não interferência no orçamento CLI e uso sem ondas CLI.
- [x] Executar suíte focada e completa, validadores, verificação de texto e revisão independente.
- [x] Atualizar o ledger com decisões e resultados. Não fazer commit ou instalar globalmente.

## Ledger

Desenho aprovado em 2026-10-29. Escopo local, sem publicação.

- Decisão técnica: métricas são números finitos no intervalo seguro JSON; vínculos
  CLI são imutáveis na mesma tentativa e precisam identificar rodada reconhecida.
- Revisão independente identificou limite de arquivo após escrita, vínculo para
  rodada não coletada e estouros de validação numérica/UTC. Reproduzidos em testes,
  corrigidos e conferidos pelo mesmo revisor; nenhum achado pendente.
- Suíte completa final: 165 testes, OK, 2 skips (PyYAML ausente no Python padrão
  e sinal POSIX em Windows). Teste PyYAML executado separadamente: 20 testes OK
  com dependência efêmera de validação, sem mudar dependências do runner.
- Validação da skill e de playbooks, sintaxe JavaScript, teste DOM da tabela,
  links e UTF-8 passaram. Não houve avaliação visual em navegador, chamadas pagas
  ou homologação com APIs reais de hosts nativos.
- O roteiro comportamental foi preparado; a avaliação de uma LLM por esse roteiro
  não foi executada. Os testes offline validam o contrato do runner, não o agente.
- Instalação global preservada; nenhuma alteração desta etapa foi commitada ou publicada.
