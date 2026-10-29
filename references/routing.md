# Roteamento e política de tokens

Leia ao decidir se vale delegar, escolher estratégia de execução ou atribuir provedores.

## Delegue independência útil

Delegue quando pelo menos duas unidades puderem avançar sem ler resultados inacabados uma da outra. Boas fronteiras: serviço, pacote, área funcional, investigação independente ou revisão de diff já produzido. Mantenha com o agente principal operações de um comando, transformações uniformes em lote, mudanças locais pequenas e cadeias totalmente sequenciais.

## Estratégias de execução

| Estratégia | Workers | Concorrência | Uso |
| --- | ---: | ---: | --- |
| auto | inferidos | inferida | Menor estratégia adequada ao plano |
| economy | 1 | 1 | Uma delegação curta com menor uso |
| balanced | até 4 | 2 | Implementação ou investigação independente comum |
| quality | 1 por rodada | 1 | Writer, revisor e correção em rodadas sequenciais |
| research | até 8 | 4 | Leituras isoladas e comparações com evidências |
| parallel | até 8 | 4 | Escrita em áreas distintas; cada writer isolado |
| rescue | 1 | 1 | Retomada de uma sessão interrompida ou falha |

O runner impõe os limites; o plano pode reduzi-los, nunca superar estratégia ou política. performance ainda é alias legado de parallel. auto escolhe rescue para retomada única, economy para worker novo único, research para lote só de leitura, parallel para dois ou mais writers isolados e balanced nos demais casos. Não escolhe quality sozinho, pois a revisão extra custa mais.

## Política salva

O runner mantém preferências portáveis sem depender de MCP. Consulte policy show. Exemplos:

~~~text
python scripts/orchestrate.py policy set economy
python scripts/orchestrate.py policy set --backend skill --provider-switch automatic
python scripts/orchestrate.py policy set --provider-order codex kimi agy claude
python scripts/orchestrate.py policy set --conserve-providers claude --max-workers 1
python scripts/orchestrate.py policy reset
~~~

ORQUESTRADOR_ORCHESTRATE_POLICY ou --policy <arquivo> seleciona outra política; ALETHE_ORCHESTRATE_POLICY permanece como alias legado. No Windows, o padrão novo fica em %APPDATA%\Orquestrador; instalações antigas em %APPDATA%\Alethe são migradas sem apagar a origem.

backend skill usa o runner local, mcp usa ferramentas compatíveis disponíveis e auto prefere MCP com fallback local. Pedido explícito do usuário prevalece. providerSwitch define como lidar com provedor conservado: never mantém, ask pede escolha e automatic tenta o próximo instalado na providerOrder. A troca automática é recusada quando modelo, esforço ou sessão retomada fixam um provedor.

budget da política define maxCalls, maxWallSeconds, maxEstimatedPromptTokens, maxReportedTokens e maxReportedCostUsd. O plano substitui cada campo individualmente. Quando houver integração externa que controle preferências de orquestração, preserve orçamento e overrides de modelos que ela não controla.

## Níveis de modelo

cheap, standard e strong vêm de tiers dos playbooks e dos overrides do perfil ativo. playbook <id> mostra modelo e esforço resolvidos. Entradas antigas policy.modelTiers prevalecem quando existirem; grave decisões novas na cópia dos playbooks.

Um worker pode usar tier em vez de modelo. O tier é resolvido após a escolha do provedor e combina com provider: auto. model ou effort explícitos podem fixar semântica de provedor; não combine tier diferente de standard com esses campos. Modelo vazio usa o padrão do CLI e provoca alerta em validate e dry-run, mesmo com esforço informado. economy atribui cheap ao worker único quando nenhum tier ou modelo foi fixado.

Confira preços e níveis relativos com models. Para preço necessário ausente ou com mais de 60 dias, use fonte oficial e grave source e asOf em orquestrador-prices.json. O runner não verifica nomes de modelos; erro de digitação aparece como falha do worker em outcome.json.

## Escolha por requisitos

1. Respeite provedor/modelo solicitado pelo usuário, salvo autorização de troca automática.
2. Identifique leitura isolada, escrita, saída estruturada, retomada e ecossistema exigido.
3. Exclua CLIs indisponíveis ou incapazes.
4. Prefira modelos baratos configurados para leituras delimitadas e tarefas mecânicas.
5. Reserve decisões arquiteturais e ambiguidade para o agente principal ou modelo forte.
6. Se a qualidade exigir visão independente, revise após a implementação com outro provedor ou modelo.

Antes de cada rodada, execute usage. Se o provedor escolhido estiver baixo e não tiver sido fixado pelo usuário, mova a tarefa ao próximo capaz no mesmo tier e resolva modelo/esforço novamente. Aplique quota.whenSpare quando houver cota a perder. Nunca rebaixe tier só para fugir da cota nem ultrapasse quota.stopAt sem consultar o usuário. Informe no máximo uma linha de cota por rodada, identifique leituras antigas e registre a troca com note --kind switch. Não deduza cota disponível só porque o CLI está instalado.

## Handoffs curtos e rodadas

Peça a pesquisadores achados com arquivo:linha ou fonte, não transcrições. Peça a writers caminhos alterados, verificações, falhas e riscos. Leia o diff; não peça que colem o código. Reuse sessionId apenas para acompanhamento relacionado; tarefa nova merece sessão nova.

- Rodada paralela: leitores independentes ou writers com arquivos distintos.
- Integração: o agente principal revisa e combina.
- Revisão: worker separado revisa o diff integrado.
- Correção: no máximo uma tentativa focada para defeito demonstrado.

Inicie cada rodada com run <plano> --in current --detach; chame wait --timeout N, até 540 segundos por chamada, até done. Claude Code pode usar execução em background. Nunca deixe uma rodada em primeiro plano sob timeout curto, nem inicie revisor em paralelo com o código que deve revisar.
