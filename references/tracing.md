# Rastreabilidade de agentes nativos e CLI

O registro reúne **agentes observados**, não garante descobrir todos os agentes
do host. O runner não consulta APIs nativas automaticamente. O principal usa as
ferramentas disponíveis para observar a execução e registrar snapshots. Dados
ausentes continuam desconhecidos; não invente modelo, esforço, custo ou conclusão.

## Fluxo do agente principal

1. Para persistir observações no runner e gerar relatórios mistos, crie uma
   orquestração com `new` e guarde a pasta retornada. Isso cria o registro local,
   não inicia agentes. A persistência via Python é opcional para uma execução
   puramente nativa: sem ela, mantenha IDs, tarefas, estados e resultados na
   sessão e relate a ausência de registro persistente. Não instale Python nem
   crie uma rodada CLI apenas para representar agentes nativos.
2. Ao delegar nativamente, registre o ID real retornado, host, tarefa, estado e
   horário da observação. Informe modelo/provedor/esforço somente se conhecidos.
3. Após consultas de estado e entrega do resultado, registre novos snapshots da
   mesma tentativa. Descendentes podem ser registrados com referência ao pai.
4. O principal é o único escritor. Workers entregam IDs/evidências para ele;
   não devem escrever no registro compartilhado ou iniciar outro orquestrador.
5. Consulte `trace list` ou `report`. `stop` e orçamentos do runner continuam
   cobrindo somente workers CLI. Para parar um agente nativo, use a ferramenta
   real do host, quando disponível e autorizada; registrar não encerra processos.

## Comandos

```sh
python scripts/orchestrate.py new "Investigação de exemplo"
python scripts/orchestrate.py trace record observacao.json --in current
python scripts/orchestrate.py trace list --in current
python scripts/orchestrate.py report --format json
python scripts/orchestrate.py report --format html --no-open
```

`--in` aceita uma pasta de orquestração ou `current`; quando omitido, usa a atual.
O arquivo JSON de entrada é dado, não código; caminhos e textos nele não são
executados. Guarde entradas e relatórios fora do checkout ou em área ignorada.

Exemplo **fictício** de observação sem medição:

```json
{
  "version": 1,
  "host": "example-host",
  "id": "agent-123",
  "attempt": 1,
  "parent": "lead",
  "task": "Investigar uma falha delimitada",
  "status": "running",
  "observedAt": "2026-10-29T12:00:00Z",
  "source": "resposta da ferramenta de estado do host"
}
```

Estados aceitos: `pending`, `running`, `completed`, `failed`, `cancelled`,
`unknown`. Traduza o estado do host somente quando sua semântica for conhecida.
`completed` registra a entrega observada; não comprova correção ou aceitação.

Campos opcionais: `provider`, `model`, `effort`, `result`, `parent`, `metrics`,
`cliRef`. `parent` pode ser `lead` (referência lógica ao principal, sem ID nativo
inventado) ou `{"host":"example-host","id":"parent-123","attempt":1}`.

## Identidade e atualização

- A identidade nativa combina host, ID e tentativa dentro da orquestração.
  Uma nova tentativa usa outro número ou outro ID.
- Cada entrada é um snapshot completo. Campos opcionais ausentes ficam
  desconhecidos no novo snapshot, sem misturar evidências de horários diferentes.
- Snapshots iguais não duplicam agentes ou consumo. Um snapshot mais antigo não
  substitui o atual. No mesmo horário, conteúdo conflitante é rejeitado.
- Uma tentativa terminal não reabre com outro estado. Correções de resultado ou
  métricas com o mesmo estado precisam de horário posterior.
- Pais ainda não recebidos são referências não resolvidas; ciclos e referências
  externas à estrutura da orquestração são rejeitados.
- Após 30 minutos, o relatório marca a observação como antiga, sem alterar seu
  estado para sucesso ou falha. Esse aviso é operacional, não regra do fornecedor.
- Dados ficam em `agents.json`, com gravação atômica. Limites: 64 KiB por entrada
  no comando, 5000 tentativas e 16 MiB no arquivo; nomes até 200 caracteres,
  tarefa/resultado até 2000 e fonte até 1000. Não incluir transcrições ou segredos.

## Métricas, natureza e cobertura

Só informe valores que a fonte realmente expôs. Exemplo fictício:

```json
{
  "tokens": {"value": 1200, "scope": "self"},
  "cost": {"value": 0.02, "scope": "descendants", "currency": "USD", "basis": "api-equivalent"}
}
```

Esse objeto vai em `metrics`. Valores são cumulativos da tentativa naquele
instante; snapshots não são somados. Tokens são inteiros não negativos, custo é
numérico não negativo, ambos finitos e no intervalo seguro para consumidores JSON.
Zero precisa ser informado explicitamente; omitir uma métrica significa desconhecido.

`scope`: `self` (só o agente), `descendants` (inclui descendentes) ou `unknown`.
`basis` monetária: `reported-expense` (despesa informada), `api-equivalent`
(equivalência em preços de API) ou `unknown`; moeda deve ter três letras maiúsculas.
Não converter equivalência de API em gasto marginal de uma assinatura.

Relatórios JSON, Markdown e HTML mostram uma lista comum e cobertura por agente.
Uma medição de um provedor não encobre outro agente do mesmo provedor sem dados.
Métricas nativas são apresentadas **por agente**, sem total nativo ou total geral
CLI+nativo; pai e filho podem ter consumo sobreposto. Os totais CLI existentes
permanecem separados. Escopo de consumo CLI é desconhecido quando não informado.

## Referências a workers CLI

Workers CLI são coletados dos relatórios existentes, sem registro manual.
Se uma observação do host se referir comprovadamente ao mesmo worker, acrescente
`"cliRef": {"run":"nome-da-rodada","worker":"worker-id"}`. `run` é relativo à
pasta da orquestração e deve identificar uma rodada existente com esse worker.
Referências externas, inexistentes ou conflitantes são rejeitadas.

Uma vez informado, `cliRef` precisa ser repetido nos próximos snapshots dessa
tentativa e não pode apontar para outra execução. Para outra execução, registre
uma nova tentativa. A rodada deve pertencer às rodadas reconhecidas pelo relatório
da orquestração; um diretório aninhado arbitrário não é aceito.

O vínculo anexa a evidência à execução CLI, sem criar outro agente ou somar suas
métricas novamente. Identidades CLI incluem rodada e worker, pois IDs podem se
repetir entre rodadas. No relatório unificado, a execução e suas métricas CLI
continuam sendo a fonte dessa linha; a observação vinculada preserva sua origem.

## Limites de garantia

O registro não autentica o host, verifica acesso a modelos, acompanha processos,
descobre descendentes sozinho ou impõe orçamento nativo. Se o host não fornecer
dados, declare a lacuna. Quando não houver Python, use o relatório do host ou um
registro manual com as mesmas distinções, sem afirmar que ele foi importado pelo runner.
