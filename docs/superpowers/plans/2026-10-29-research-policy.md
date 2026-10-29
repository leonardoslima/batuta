# Research Policy Implementation Plan

> **For agentic workers:** Execução inline com superpowers:executing-plans e revisão independente somente leitura.

**Goal:** Substituir escolhas fixas por pesquisa e comparação independente de modelo/esforço.

**Architecture:** Manter pesquisa com o agente principal e snapshots explícitos no runner. Neutralizar tiers e overrides de decisão dos playbooks distribuídos; preservar resolução de cadastros existentes.

**Tech Stack:** Python 3.9+, unittest, YAML e Markdown.

**Spec:** ../specs/2026-10-29-research-policy-design.md

## Restrições

- Não fazer commit ou push sem novo pedido do usuário.
- Não fixar preferência de provedor nem usar preço como medida de capacidade.
- Não iniciar chamadas pagas de modelos para validar esta mudança.
- Não atualizar a instalação pessoal ou suas preferências.

## Execução

- [x] Reproduzir defaults de esforço/modelo e ausência de distinção de pesquisa online em três testes novos.
- [x] Neutralizar tiers, overrides de modelo/esforço e provider em fases/regras.
- [x] Preservar testes de compatibilidade com fixture de configuração pessoal explícita.
- [x] Marcar snapshots de preço como não verificados na rede pelo runner.
- [x] Documentar fontes, atualização, registro local, fluxo sem rede e escolhas independentes.
- [x] Validar skill, playbooks e compatibilidade com parser YAML oficial.
- [x] Revisão independente: remover regras que alteravam tiers conforme cota de outro provedor; revisão final sem achados pendentes.

## Verificação

A suíte completa foi executada com Python 3.15; teste de equivalência PyYAML foi
também executado em ambiente efêmero Python 3.12 com dependência de validação.
Nenhum provedor foi iniciado. Dados reais de planos, preços pesquisados e
preferências pessoais não foram gravados no repositório.
