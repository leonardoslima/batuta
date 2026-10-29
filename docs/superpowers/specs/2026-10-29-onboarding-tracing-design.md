# Onboarding verificável e rastreabilidade de agentes

## Objetivo e escopo

O usuário autorizou continuar pelas duas melhorias prioritárias: testes do
onboarding completo e rastreabilidade nativa/CLI. Manter independência de
provedor e transparência sobre lacunas de medição. Não fazer commit ou push
até pedido explícito. Esta proposta detalha o comportamento antes de implementar.

## Abordagens

1. **Registro local comum e relatórios existentes — recomendada.** Normalizar os
   workers CLI já coletados e registrar observações dos agentes nativos com
   origem explícita. Funciona com hosts diferentes, mas a coleta nativa exige
   ferramentas do host ou atualizações pelo agente principal.
2. **Adaptador exclusivo de um host.** Facilita automação naquele aplicativo,
   mas limita portabilidade e depende de APIs ainda não verificadas. Fica para
   uma integração posterior, sem presumir capacidades do Orca ou outro host.

## Onboarding completo

- Testar o percurso pelos comandos públicos em diretório temporário: diagnóstico,
  descoberta, proposta representada por configuração, validação e prévia de rodada.
- Usar CLIs falsos, catálogos e fontes oficiais simuladas; sem contas reais,
  navegação externa ou chamadas pagas durante a suíte determinística.
- Incluir o passo explícito de persistência e sua releitura: playbooks, preços/
  contas e política. Simular a aprovação no roteiro do teste, sem afirmar que o
  runner interpreta consentimento de uma conversa. Leituras anteriores não
  sobrescrevem arquivos; escolhas persistidas devem chegar à prévia da rodada.
- Cobrir provedores alternativos, catálogo novo sem preço, cache antigo/ausente,
  dados opcionais desconhecidos, ausência de rede e reconfiguração de cadastro
  antigo com restrições explícitas preservadas.
- Verificar efeitos observáveis: novos candidatos permanecem disponíveis, as
  escolhas explícitas chegam à prévia, modelos/esforços não são herdados dos
  defaults vazios, o cadastro não é sobrescrito sem o passo autorizado e preços
  simulados não são apresentados como pesquisa real da rede.
- Esses testes verificam o percurso do runner e seus contratos. A pesquisa, a
  comparação e as perguntas realizadas pelo agente exigem cenários comportamentais
  separados; não afirmar que uma suíte Python prova obediência de qualquer LLM.
- Incluir roteiro de avaliação comportamental offline com resultados esperados
  observáveis, para execução isolada quando houver ferramenta de agente autorizada.

## Registro de agentes nativos

- Registrar observações em arquivo local da orquestração. Acrescentar comando
  explícito para importar uma observação JSON validada, sem lançar agentes nem
  executar caminhos ou comandos contidos no arquivo.
- Campos: ID estável, ID do pai quando conhecido, backend nativo/CLI, host,
  provedor, modelo, esforço, tarefa/resumo, estado observado, fonte e horário.
  Informações não expostas ficam ausentes/desconhecidas.
- Repetir a mesma observação não duplica o agente nem seu consumo. Uma nova
  tentativa tem identidade própria ou tentativa explícita; observação antiga
  não pode reverter o estado mais recente.
- Identidade CLI inclui rodada e worker, pois nomes podem se repetir entre
  rodadas. Identidade nativa inclui host, ID externo e tentativa. Um vínculo
  explícito com um worker CLI existente representa a mesma execução, sem criar
  outro agente ou adicionar novamente suas métricas; vínculo inválido é rejeitado.
- Cada observação é um snapshot completo, com valores opcionais desconhecidos
  quando ausentes. Métricas são cumulativas da tentativa naquele instante, nunca
  deltas somados entre snapshots. Observações iguais são idempotentes; no mesmo
  horário, snapshots conflitantes são rejeitados. Observações antigas não alteram
  o estado vigente; uma nova tentativa não reutiliza identidade já concluída.
- Preservar origem e horário reais. Fonte indisponível ou observação antiga não
  é evidência de conclusão ou falha; mostrar a incerteza.
- Distinguir agentes de diferentes orquestrações e validar relações de parentesco,
  inclusive ciclos. Um agente principal identificado pode ser pai dos registrados.
- A chave completa pertence à orquestração. Reservar `lead` como referência lógica
  ao principal, sem inventar um ID real do host ou suas métricas. Filhos recebidos
  antes do pai guardam referência não resolvida dentro da mesma orquestração;
  relatório informa essa lacuna. Rejeitar referência externa e ciclos, sem criar
  pais fictícios para completar a árvore.
- Começar com um escritor responsável: o agente principal serializa os registros;
  não permitir que workers atualizem o relatório compartilhado concorrendo entre si.

## Relatórios e cobertura

- Unificar a lista de agentes nativos e workers CLI, distinguindo origem/backend,
  estado, resultado e relações. Manter relatórios Markdown, JSON e HTML coerentes.
- Permitir consultar uma orquestração com registros nativos mesmo sem rodadas CLI.
- Preservar os totais CLI existentes. Métricas nativas permanecem identificadas e
  na primeira versão são mostradas somente por agente, sem soma entre pai/filhos,
  tentativas ou registros que representem o mesmo worker CLI. Não criar total
  monetário ou de tokens geral CLI+nativo nesta etapa.
- Campos de medição incluem escopo: apenas o agente, incluindo descendentes ou
  desconhecido, por métrica. Valores ausentes ficam desconhecidos; zero exige
  relato explícito, e valores negativos ou não finitos são inválidos. Valor
  monetário inclui moeda e natureza: despesa informada ou equivalência de tabela,
  sem tratar equivalência de API como gasto de assinatura.
- Quando faltar cobertura, mostrar métricas conhecidas e informar que o total
  completo é desconhecido. Não substituir desconhecido por zero.
- Expor cobertura por agente, inclusive nos workers CLI: um agente com consumo
  informado não pode ocultar outro sem medição só porque têm o mesmo provedor.
- Orçamentos rígidos do runner continuam cobrindo somente workers CLI gerenciados.
  Registros nativos observam execução; não controlam processos ou despesas do host.
- Renderizar nomes/tarefas/fontes como texto seguro no HTML e limitar tamanho
  das entradas. Não importar transcrições, credenciais ou dados pessoais desnecessários.

## Compatibilidade e limites

Configurações e relatórios antigos continuam funcionando sem arquivo nativo.
Não alterar credenciais, conta, preferências pessoais nem APIs de hosts nesta etapa.
Avaliação por resultado aceito e identificação de versão instalada são melhorias
posteriores; não entram nesta implementação. Atualização global fica para pedido
explícito após a validação da mudança local.

## Verificação

Testes de contrato e integração para onboarding, deduplicação, observações fora
de ordem, parentesco inválido, métricas desconhecidas/inclusivas, relatórios só
nativos e mistos, renderização segura e compatibilidade CLI. Revisão independente
somente leitura antes de concluir. A suíte usa fixtures sem provedores externos.

## Estado

Revisão independente do desenho sem decisão adicional de preferência do usuário.
Definições de identidade, snapshots e medição registradas acima são escolhas
técnicas propostas, não preferências atribuídas ao usuário.
Desenho aprovado pelo usuário em 2026-10-29; implementação autorizada na cópia local.
