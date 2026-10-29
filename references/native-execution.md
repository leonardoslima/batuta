# Agentes nativos do host

Leia ao executar ou controlar agentes pelas ferramentas do ambiente hospedeiro,
sem depender de uma aplicação específica. Ferramentas listadas não comprovam
permissão, autenticação ou acesso aos modelos. Não presuma APIs, níveis de
esforço, isolamento ou telemetria a partir de sessões anteriores.

## Verifique somente o necessário

Confira as instruções do projeto e a preferência de backend. Descubra as
capacidades exigidas pela unidade: iniciar e acompanhar agentes, selecionar
modelo/esforço, leitura isolada, concorrência e encerramento. Não faça sondagem
com workers nem repita inventário sem mudança ou lacuna relevante.

Use recursos gerenciados pelo host quando disponíveis, autorizados e pertinentes;
respeite a propriedade de checkouts e sessões existentes. Se faltar uma capacidade
necessária, informe a limitação. Não substitua silenciosamente agentes nativos
exigidos pelo usuário por workers CLI.

## Execução

1. Escolha o playbook e as fases pelos resumos e depois somente pelo fluxo
   pertinente, conforme [playbooks.md](playbooks.md). Leia o YAML configurado,
   ou o incluído quando não houver cópia. Não execute `probe`, `scaffold`,
   `dry-run` ou `run` do runner como pré-requisitos de agentes nativos.
2. Prepare briefs conforme [briefs.md](briefs.md), com propriedade de arquivos,
   resultado esperado e verificações. Resolva conta, modelo, esforço e cotas por
   evidências disponíveis, seguindo [SKILL.md](../SKILL.md). Não afirme leitura
   protegida ou isolamento que o host não ofereça.
3. Inicie e acompanhe os agentes pelas ferramentas reais do host. Guarde os IDs
   retornados, tarefa, parentesco e estados observados. Descendentes ficam no
   escopo do pai e respeitam permissões, cotas e concorrência disponíveis.
   Workers não iniciam outra orquestração ou CLIs de agentes alheios.
4. Para cancelar, use o controle nativo e confira o estado resultante quando
   possível. `stop` do runner encerra somente seus workers CLI. Se o host não
   expuser cancelamento, declare a limitação sem afirmar que o agente parou.
5. Confira entregas e diffs, integre o trabalho revisado e valide o conjunto.
   Preserve gates do fluxo específico do projeto. Relate decisões, evidências,
   consumo conhecido e lacunas.

## Registro e limites

O runner Python não inicia nem controla agentes nativos. Não é necessário
instalar Python para esse fluxo. Para persistência local ou relatório misto,
use [tracing.md](tracing.md); sem persistência, mantenha o resumo na sessão e
declare essa condição. Não simule uma rodada CLI para representar trabalho nativo.

A coleta depende das ferramentas reais do host e não é automática. Não invente
tokens, provedor, modelo, duração ou cobertura de descendentes. Os limites rígidos
do runner não cobrem automaticamente esses agentes. Totais CLI são preservados;
métricas nativas ficam por agente, sem somar valores potencialmente inclusivos.
Um fluxo misto aplica cada procedimento somente aos agentes daquele backend.

## Particularidades do ambiente

Se o ambiente em uso for Orca, consulte também
[orca-integration.md](orca-integration.md) para seus recursos gerenciados.
Em outros hosts, use as ferramentas e instruções realmente disponíveis; não
carregue o adaptador Orca nem exija instalar outra aplicação.
