# Account Plans Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task in the current workspace.

**Goal:** Incorporar o plano contratado ao cadastro, às consultas e à previsão de cotas.

**Architecture:** Estender a configuração local de preços com accounts por provedor, preservando billing. Observar o plano exposto pela telemetria Codex e separar amostras por contexto; o agente usa capacidades e preferências verificadas no planejamento.

**Tech Stack:** Python 3.9+, biblioteca padrão, unittest, Markdown.

**Spec:** ../specs/2026-10-29-account-plans-design.md (aprovada pelo usuário).

## Global Constraints

- Não deduzir capacidade pelo valor mensal nem habilitar gasto adicional.
- Preservar billing legado, thresholds e permissões existentes.
- Dados da conta são locais; nenhum dado real deve entrar no repositório.
- Executar neste workspace designado pelo usuário, sem commit/push nesta mudança.

## Review Focus

- Configuração ausente ou antiga continua funcionando.
- Plano observado em conflito com cadastro confirmado fica explícito.
- Troca de plano invalida previsões incompatíveis e rodadas que cruzam a troca.
- Metadados inválidos falham com mensagem útil; valores ausentes ficam desconhecidos.
- Preço, preferência e habilitação de extras nunca concedem autorização implícita.

## Tarefas

- [x] Adicionar testes de contas, telemetria, conflitos e separação de histórico; observar as falhas.
- [x] Implementar validação e exposição do contexto em usage, models e dry-run; separar amostras.
- [x] Atualizar onboarding, instruções de roteamento e README com contrato e exemplo fictício.
- [x] Executar testes focados, suíte herdada, verificação de playbooks e revisão final.

## Decisões de execução

- A descoberta inicial usará apenas o campo plan_type efetivamente observado na telemetria local Codex. Outros hosts/CLIs podem fornecer evidência ao onboarding, sem inferir flags ou formatos.
- O armazenamento continua no arquivo local orquestrador-prices.json, ao lado da política; não haverá tabela fixa de planos comerciais.
- A escolha dos agentes continua com o agente principal, como no runner atual; o dry-run apresentará contexto e alertas, sem introduzir um roteador automático paralelo.

## Verificação e revisão

- 12 testes novos de contas passaram, após falhas iniciais reproduzidas.
- Suíte completa: 137 testes, OK, 2 skips dependentes do ambiente.
- quick_validate.py: skill válida; check_playbooks.py: 2 provedores, 3 perfis,
  11 playbooks, 49 fases. Validadores rodados com Python 3.12 em UTF-8 e PyYAML
  via ambiente efêmero do uv, sem alterar dependências do runner.
- Revisão independente somente leitura apontou reclassificação de leitura antiga
  e perda de evidência de plano. Ambos foram reproduzidos em testes, corrigidos
  e conferidos novamente pelo mesmo revisor, sem achados remanescentes.
- Dados pessoais e contas reais não foram salvos no repositório. Nenhum worker
  de provedor externo foi executado; testes usam fixtures locais. A descoberta
  não foi homologada com todos os CLIs/provedores.
