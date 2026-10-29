# Briefs e revisões

Leia ao escrever uma tarefa para worker ou instruções de revisão, validação, julgamento ou painel.

## O brief está pronto?

Um brief vago encarece todas as tentativas. Pontue antes de enviar:

| Parte | Pontuação |
| --- | --- |
| Objetivo | 0 ausente; 1 vago; 2 claro; 3 claro e testável |
| Resultado esperado | 0 ausente; 1 vago; 2 claro; 3 verificável por comando ou diff |
| Escopo | 0 ausente; 1 direção geral; 2 caminhos sob responsabilidade e caminhos proibidos |
| Restrições | 0 ausentes; 1 algumas; 2 regras e limites aplicáveis do repositório |

Abaixo de 7, leia mais ou esclareça com o usuário antes de enviar.

## Brief de escrita

Nesta ordem:

1. Uma linha sobre a posição da unidade na tarefa geral.
2. Objetivo e definição de conclusão expressos como verificações que passam ou falham.
3. Caminhos sob responsabilidade e o que deve permanecer intacto.
4. Interfaces e decisões anteriores que o worker não descobriria sozinho.
5. Resolução de ambiguidades identificadas no pedido.
6. Verificações e comandos exatos.

Descreva uma unidade, não todo o histórico da sessão. Aponte para arquivos em vez de colá-los. O runner acrescenta o contrato do worker, terminado por STATUS: e SUMMARY:. Trate BLOCKED e NEEDS_CONTEXT como pedido de contexto: altere contexto, nível ou escopo antes de reenviar a unidade. Nunca reenvie o mesmo brief ao mesmo modelo.

## Verificação do writer

- Confira o repositório, não apenas o relatório do worker. Estado e resumo são alegações.
- Leia primeiro as alterações nos testes. Um teste verde porque foi enfraquecido não vale.
- Verificações aprovadas são necessárias, porém insuficientes.
- Em checkout alterado, inspecione git diff e arquivos não rastreados antes de checkout, reset ou clean.
- Peça retrabalho descrevendo o defeito e o comportamento esperado, sem repetir toda a tarefa.
- O agente principal integra e faz commit; workers não fazem.

## Brief de revisão

Passe caminhos para a tarefa, result.md e diff.patch. Peça:

1. Conformidade com a especificação: ausências, excessos e equívocos. “Não verificável pelo diff” é resposta válida; adivinhação não.
2. Qualidade: cada achado com arquivo:linha, cenário de falha e gravidade crítica, alta, média ou baixa.
3. Apenas achados, veredito e verificações executadas.

Um achado forte supera vários fracos. Justificativas não reduzem gravidade. Use nível padrão ou superior para revisores; modelos baratos servem apenas para descartar diffs triviais.

## Revisão adversarial

Em mudanças que não podem falhar, peça razões concretas pelas quais falhariam. Investigue limites de confiança, perda de dados, retries e idempotência, concorrência e estado antigo, caminhos vazios ou nulos, timeout, divergência de schema e observabilidade ausente. Cada achado informa falha, exposição, impacto provável e correção que reduz o risco. Aprove somente sem achados substantivos pendentes.

## Veredito de validação

Um validador verifica alegações de outra sessão; nunca retome a sessão do autor. Termine com:

~~~text
VERDICT: PASS | FAIL | NOT_PROVEN
NOT CHECKED: <critérios sem evidência, ou none>
~~~

PASS exige todos os critérios demonstrados. FAIL exige falha demonstrada. NOT_PROVEN indica falta de evidência: execute a verificação faltante antes de corrigir código. O runner registra VERDICT em outcome.json e sinaliza FAIL e NOT_PROVEN no relatório.

## Nova revisão

Após correção, revise somente o diff corretivo e marque cada achado anterior ADDRESSED ou NOT ADDRESSED. Uma tentativa que deixa o defeito não o resolveu.

## Painel

Para uma decisão, entregue o mesmo brief a dois ou três provedores, cada um em sessão separada e sem ver as respostas dos demais. Um defende, outro contesta e outro é neutro. O defensor menciona ao menos uma razão real; o contestador não rejeita boa ideia apenas para discordar; o neutro relata o balanço real, não um empate artificial. Cada um termina com veredito e confiança de 0 a 10. O agente principal resume consenso, divergência, recomendação e riscos.
