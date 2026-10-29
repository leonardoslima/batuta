# Plano contratado nas decisões da Batuta

## Objetivo

Descobrir o plano da conta quando houver evidência verificável, perguntar pelos
dados ausentes e usar esse contexto para planejar o trabalho e prever cotas.
O usuário aprovou a descoberta automática com perguntas apenas quando necessário.

## Abordagens

1. Registrar o plano apenas no onboarding: informa o agente, mas não corrige
   previsões que misturam históricos de planos diferentes.
2. Integrar cadastro, previsões e instruções de roteamento: recomendada, pois o
   plano influencia o fluxo e mantém os limites observados como base da execução.
3. Fixar tabelas de capacidade por faixa de preço: descartada, pois o preço
   mensal não determina capacidade nem garante acesso a modelos.

## Proposta para aprovação

- Registrar por provedor o tipo de cobrança, nome do plano, valor, moeda e
  periodicidade quando disponíveis, fonte e data da observação.
- Registrar capacidades verificadas: modelos disponíveis, limites conhecidos e
  situação do uso adicional pago, separando habilitação de autorização de uso.
- Descobrir por dados locais ou respostas documentadas do CLI/host. Não ler
  credenciais nem disparar workers só para descobrir o plano. Quando a descoberta
  não for suficiente, perguntar; valores desconhecidos continuam desconhecidos.
- Preservar configurações antigas de billing e não sobrescrever uma preferência
  confirmada diante de evidência conflitante: pedir conciliação nesse caso.
- Mostrar plano, origem e lacunas nos comandos de consulta e na prévia da rodada.
- Orientar o agente a ajustar provedor, modelo, quantidade de workers e tamanho
  das rodadas conforme capacidades verificadas, cota recente, histórico compatível
  e preferência de consumo do usuário. Um plano mais caro não autoriza aumentar
  gasto nem reduzir o nível de capacidade exigido pela tarefa.
- Separar as amostras de previsão pelo contexto do plano. Após mudança, não usar
  amostras de outro plano; com dados insuficientes, marcar a previsão desconhecida.
- Preservar thresholds de parada, escolhas explícitas e permissões existentes.
  API continua usando preços de API; mensalidade não vira custo por token.

## Escopo e verificação

Alterar runner, onboarding, referências e README; adicionar testes para cadastro,
compatibilidade, descoberta sem evidência, mudanças de plano e previsão isolada.
Não alterar contas, assinaturas, autenticação nem contratar uso adicional.
Não instalar esta versão sobre a skill ativa. Commit e publicação desta mudança
dependem de pedido do usuário; a autorização anterior cobriu a publicação inicial.

## Estado

Desenho aprovado pelo usuário em 2026-10-29. Não contém tabelas de planos ou preços presumidos.
