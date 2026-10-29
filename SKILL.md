---
name: batuta
description: Use quando o usuário pedir orquestração ou delegação de tarefas entre agentes de código, comparação de modelos para esse trabalho, controle de cotas da execução, recuperação de workers ou configuração e relatórios do Batuta.
metadata:
  version: "19"
---

# Batuta — orquestração de agentes de código

Coordene tarefas delimitadas com o menor contexto e custo total que atendam à
qualidade necessária. Delegue quando compensar; mantenha tarefas pequenas,
ambíguas ou muito acopladas com o agente principal. Não fixe fornecedor, modelo
ou esforço a partir de uma experiência anterior.

## Comece pelo pedido

Leia somente as referências pertinentes à ação atual. Não percorra setup,
pesquisa de preços ou descoberta de agentes para apenas consultar um resultado.
Relatórios genéricos, configuração de aplicações e trabalho individual de código
não acionam a Batuta por si sós.

| Pedido | Leia e faça |
| --- | --- |
| Configurar ou reconfigurar a Batuta | [onboarding.md](references/onboarding.md); preserve perguntas relevantes, respostas anteriores e aprovação antes de salvar. Leia [accounts.md](references/accounts.md) e [research.md](references/research.md) ao comparar conta, modelos, esforço e custo. |
| Executar ou delegar uma tarefa | Escolha o backend abaixo; depois leia somente o procedimento correspondente. |
| Status, resultados, orçamento ou recuperação de uma execução CLI | [operations.md](references/operations.md), na seção da ação; consulte `status` antes de retomar após compactação. |
| Consultar ou registrar agentes nativos | [tracing.md](references/tracing.md); use as ferramentas do host para estado e controle dos agentes. |
| Relatório HTML ou editor de playbooks | [operations.md](references/operations.md) para relatório; [playbooks.md](references/playbooks.md), seção Editor, para editor. Se o pedido for apenas abrir arquivo existente, abra-o sem regenerar ou reconfigurar. |
| Ativar/desativar modo contínuo, comandos curtos ou preferências persistentes | [cli-workflow.md](references/cli-workflow.md), seções Comandos curtos, Modo contínuo e configuração. |
| Sem argumentos | Consulte o estado existente; sem execução atual, apresente os comandos principais de [cli-workflow.md](references/cli-workflow.md). Não inicie setup ou workers. |

`$batuta` é a invocação onde houver suporte. A integração Claude Code mantém
`/orchestrator`; os apelidos legados continuam compatíveis. Nenhum desses nomes
autoriza ativar modo contínuo ou gravar preferências sem pedido aplicável.

## Escolha o backend antes de executar

Respeite a escolha explícita do usuário e as permissões reais do ambiente.
Caso contrário, considere política já disponível, suporte, isolamento, cotas e
recursos; descubra apenas as capacidades necessárias para a tarefa. Instalação,
catálogo ou ferramenta listada não comprovam autenticação nem acesso.

- **Agentes nativos do host:** leia [native-execution.md](references/native-execution.md).
  Use as ferramentas realmente expostas para iniciar, acompanhar e encerrar.
  Não execute `probe`, `scaffold`, `dry-run` ou `run` do runner para lançar esses
  agentes. O runner pode servir ao registro opcional e aos relatórios mistos,
  conforme [tracing.md](references/tracing.md), mas não controla a execução nativa.
- **Workers em CLIs externos:** leia [cli-workflow.md](references/cli-workflow.md).
  O runner Python valida planos e administra seus processos, limites e resultados.
  Seus workers não aparecem automaticamente como agentes nativos do host.
- **Sem Python para workers CLI:** leia [manual.md](references/manual.md).
  A ausência de Python não impede usar ferramentas nativas disponíveis. Não
  substitua o backend exigido pelo usuário silenciosamente.

Sem ferramenta suficiente, informe a lacuna e continue o que não depender dela.
Ausência de setup não obriga interromper uma tarefa: use capacidades verificadas,
limites já autorizados e playbooks incluídos, sem salvar preferências; ofereça
configuração depois. Não invente defaults de modelo/esforço para preencher tiers.

## Regras comuns de planejamento e consumo

- Continue do plano, conversa e diff existentes. Preserve gates do projeto;
  Batuta organiza delegação, sem substituir o fluxo específico de entrega.
- **Playbook** define fases, papéis e verificações; **perfil** (`base`, `savings`,
  `aggressive`) orienta escolhas de modelo/esforço; **estratégia** compõe uma
  rodada; **objetivo** (`save`, `balanced`, `max`) orienta um modo contínuo.
  Leia [playbooks.md](references/playbooks.md) ao escolher fases; os comandos
  dessa referência pertencem ao runner, não são pré-requisitos da execução nativa.
- Antes de escolher agentes, confira conta, acesso, cotas, atualidade das leituras
  e autorização de extras em [accounts.md](references/accounts.md). Mensalidade
  não determina capacidade; preço de API não representa consumo da assinatura.
- Para escolher ou revisar modelos e esforços, siga [research.md](references/research.md).
  Setup/reconfiguração exige fontes oficiais; nas rodadas seguintes, reaproveite
  evidências pertinentes e pesquise lacunas ou mudanças. Tabela local é snapshot.
  Modelo econômico não implica esforço baixo. Declare escolhas e incertezas.
- Antes de cada rodada, confira cotas disponíveis e limites aplicáveis. Dados
  ausentes/antigos são desconhecidos. Se todos os provedores estiverem baixos,
  uma troca exigir reduzir capacidade ou a previsão ultrapassar o limite salvo,
  peça decisão antes de iniciar. Respeite provedor fixado e extras autorizados.
  Limites rígidos do runner não cobrem automaticamente agentes nativos.

## Delegação e entrega

Prepare briefs conforme [briefs.md](references/briefs.md): objetivo, conclusão
esperada, caminhos sob responsabilidade, contexto necessário, verificações e
mudanças proibidas. Aponte para arquivos em vez de copiar transcrições.

Separe responsabilidades de escrita e isole writers concorrentes. Um writer
único pode usar o checkout atual preservando alterações existentes. Workers não
iniciam outra orquestração nem CLIs de agentes alheios; descendentes nativos só
dentro do escopo, permissões e concorrência disponíveis, sob responsabilidade
do worker pai. Nunca coloque segredos em tarefas, planos, argumentos ou logs.
Flags que removem isolamento exigem pedido explícito.

Acompanhe pelo backend escolhido, confira resultado e diff mesmo após declaração
de sucesso, integre alterações revisadas e valide o conjunto. Faça uma tentativa
adicional somente com causa concreta e corrigível, respeitando gates do projeto.
Registre mudanças de estratégia e aproveitamento no mecanismo disponível.

Para agentes nativos, registre IDs, parentesco, estado e resultado observados;
o principal serializa a persistência conforme [tracing.md](references/tracing.md).
Declare lacunas de cobertura. Não invente métricas nem some custos/tokens nativos
potencialmente inclusivos aos totais CLI. Encerre com trabalho entregue,
verificações, consumo conhecido e pendências, sem exigir runner para relatar
uma execução puramente nativa.

Não faça commit, push, tag, release nem abra PR sem pedido explícito do usuário.
