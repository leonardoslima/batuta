# Batuta

**Uma skill para reger agentes de código, com escopo, orçamento e revisão.**

Batuta ajuda o agente principal a distribuir tarefas entre Codex, Claude Code,
Antigravity, Kimi e CLIs personalizados. Escolhe playbooks, prepara briefs,
acompanha resultados e exige revisão antes de integrar o trabalho dos workers.

O ponto de entrada é o [SKILL.md](SKILL.md). Este repositório contém a skill
completa, o runner Python e os recursos de apoio.

## Quando usar

- Dividir uma tarefa em unidades independentes com responsabilidades claras.
- Coordenar implementação, pesquisa, revisão e validação.
- Escolher agentes conforme capacidade, cotas e preferências de custo.
- Retomar workers e consultar resultados, uso e pendências.

Tarefas pequenas ou muito acopladas podem permanecer com o agente principal.
Delegar tem custo; Batuta orienta o agente a avaliar quando compensa.

## Instalação

Clone este repositório na pasta de skills do seu ambiente, com o nome `batuta`.
Se essa pasta já existir, preserve sua cópia antes de instalar.

### Windows · PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/leonardoslima/batuta.git "$HOME/.agents/skills/batuta"
```

### macOS e Linux

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/leonardoslima/batuta.git ~/.agents/skills/batuta
```

Reabra a sessão do agente para que ele descubra a skill. Em ambientes com outra
pasta de skills, use o diretório correspondente. A instalação precisa manter
`SKILL.md`, `references/`, `scripts/` e os demais recursos juntos.

Os arquivos em `upstream-plugins/` e `upstream-hooks/` são recursos herdados;
os comandos acima instalam a **skill**, sem registrar um plugin ou hook.

## Primeiro uso

Em um ambiente com invocação de skills:

```text
$batuta setup
```

Ou peça em linguagem natural:

```text
Use a skill batuta e execute o setup inicial.
```

O onboarding inspeciona as capacidades disponíveis, CLIs e modelos, pergunta
pelas preferências necessárias e propõe os perfis `base`, `savings` e
`aggressive`. Preferências só são salvas após aprovação.

Também considera o plano contratado: descobre o que estiver exposto pelas
ferramentas e pergunta pelos dados ausentes. Nome do plano, preço, capacidades,
extras e preferência de consumo ajudam a dimensionar as rodadas. O runner já
lê o nome do plano quando a telemetria Codex o informa; outros provedores
dependem das evidências disponíveis ao agente ou da resposta do usuário.
Previsões separam históricos de planos diferentes. Veja [contas e planos](references/accounts.md).

Depois, descreva uma tarefa e suas restrições:

```text
$batuta revise o diff atual, sem editar arquivos, e apresente os achados.
```

```text
$batuta implemente a tarefa descrita em docs/plano.md, com orçamento
de até dois workers e revisão dos diffs antes de integrar.
```

Esses exemplos são pedidos ao agente hospedeiro, não comandos de terminal.

## Comandos da skill

Use depois de `$batuta`, conforme o suporte do seu ambiente.

| Comando | Finalidade |
| --- | --- |
| `setup` | Diagnóstico e onboarding |
| `<tarefa>` | Coordenar uma tarefa delimitada |
| `status` | Consultar o estado atual |
| `usage` | Consultar cotas, resets e atualidade das leituras |
| `models` | Consultar modelos, preços e fontes |
| `report` | Mostrar resultados e uso relatado |
| `report html` | Gerar e abrir o relatório HTML |
| `editor` | Abrir o editor offline de playbooks |
| `stop` | Interromper a rodada atual |
| `on` / `off` | Ligar ou desligar o modo contínuo no projeto |
| `help` | Consultar os comandos disponíveis |

O modo contínuo é opcional e depende de pedido explícito. Consulte o
[contrato completo](SKILL.md) para objetivos, estratégias e orçamentos.

## Execução e requisitos

- **Skill:** requer um agente hospedeiro que leia `SKILL.md` e seus recursos.
- **Runner CLI:** requer Python 3.9+ e os CLIs dos provedores escolhidos,
  instalados e autenticados. O runner usa a biblioteca padrão do Python.
- **Sem Python:** existe um [fluxo manual](references/manual.md).
- **Orca:** a integração depende das capacidades realmente expostas pelo host.
  O runner Python não inicia agentes nativos do Orca.

Para diagnosticar o runner, execute na pasta da skill:

```sh
python scripts/orchestrate.py doctor
```

## Como funciona

1. O agente lê a tarefa e escolhe um playbook adequado.
2. Define responsabilidades, verificações e limites de cada worker.
3. Confere capacidades, cotas e a prévia da execução.
4. Executa unidades delimitadas, isolando writers concorrentes quando necessário.
5. Inspeciona resultados e diffs, valida a integração e registra o aproveitamento.
6. Apresenta resultados, uso relatado e pendências.

O pacote inclui playbooks, perfis de modelos, orçamentos por rodada ou tarefa,
sessões retomáveis, editor offline e relatório HTML. A disponibilidade de cada
recurso depende do backend e dos provedores configurados.

## Limites e permissões

Batuta orienta o agente a não fazer commit, push, tag, release ou PR sem pedido
explícito. Workers entregam resultados para inspeção pelo agente principal.

Cotas, tokens e custos dependem do que cada provedor informa. Leituras antigas
são incertas; o relatório CLI pode não incluir agentes nativos ou seus
descendentes. Estimativas de preço não equivalem a gasto efetivamente relatado.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| [SKILL.md](SKILL.md) | Instruções e contrato da skill |
| [agents/openai.yaml](agents/openai.yaml) | Nome e prompt de apresentação |
| [references/](references/) | Onboarding, execução, provedores e operações |
| [scripts/](scripts/) | Runner e geração de diagramas |
| [playbooks.yaml](playbooks.yaml) | Playbooks e perfis incluídos |
| [schemas/](schemas/) | Esquema dos planos de execução |
| [assets/](assets/) | Editor, relatório e recursos visuais |
| [upstream-tests/](upstream-tests/) | Testes herdados do projeto original |
| [ORCA_ADAPTATION.md](ORCA_ADAPTATION.md) | Origem e alterações da adaptação |

## Créditos e licença

Batuta é uma adaptação de
[Kc1t/alethe-orchestrate-skill](https://github.com/Kc1t/alethe-orchestrate-skill),
de Kauã Miguel, baseada no upstream v19. O commit de referência está em
[UPSTREAM_COMMIT.txt](UPSTREAM_COMMIT.txt), e os documentos históricos foram
preservados nos arquivos `UPSTREAM_*`.

Distribuído sob a [licença MIT](LICENSE), com a atribuição original preservada.
