# Pesquisa para decidir modelos, esforço e custo

Leia antes de propor perfis no setup/reconfiguração e quando uma decisão depender
de informação ausente, conflitante ou desatualizada. A pesquisa é executada pelo
agente principal com as ferramentas de consulta disponíveis. O runner Python
não navega na internet nem transforma o catálogo local em pesquisa atual.

## Fontes e perguntas distintas

| Pergunta | Evidência adequada |
| --- | --- |
| Quais modelos existem e o que suportam? | Documentação oficial do fornecedor |
| Quais estão expostos nesta instalação? | Inventário do host/CLI e cache com origem/data |
| A conta tem acesso e cota? | Estado autenticado, telemetria e confirmação do usuário |
| Quanto custa a modalidade usada? | Preços e condições oficiais da API/assinatura/rota correspondente |
| Qual combinação atende à tarefa? | Capacidades documentadas, contexto da tarefa e resultados observados |

Documentação pública não comprova acesso da conta. Um catálogo local não prova
que um preço continua válido. Preço e posição no catálogo não medem qualidade.
Separe observações, alegações do fornecedor e conclusões próprias.

## Pesquisa no setup e na reconfiguração

1. Descubra os provedores e rotas disponíveis e respeite os que o usuário deseja
   considerar. Pesquise os candidatos relevantes, sem limitar a análise aos nomes
   dos playbooks, ao preço cadastrado ou aos modelos de um setup antigo.
2. Busque e abra as páginas oficiais de modelos, preços e condições pertinentes.
   Não use apenas snippet, agregador de preços ou nome de um link como evidência.
   Descubra as fontes do fornecedor/rota em questão, sem exigir um provedor fixo.
3. Confirme IDs/variantes, recursos necessários, esforços ou budgets suportados,
   restrições e situação de preview/depreciação quando afetarem a decisão.
   Não copie o conjunto de esforços de um modelo para outro ou entre provedores.
4. Compare preços na mesma modalidade e unidade. Distinga entrada, saída, cache,
   contexto, ferramentas e descontos/modos quando relevantes. Registre moeda,
   unidade e condições. Um preço de API não representa gasto marginal da assinatura.
5. Consulte acesso, cotas e reset da conta. A internet não substitui essa leitura.
   Sem evidência, marque desconhecido; não estime capacidade pelo valor mensal.
6. Compare combinações de modelo **e** esforço conforme a tarefa. Um modelo
   econômico não recebe automaticamente esforço baixo. Um modelo mais caro não
   recebe automaticamente esforço alto. Não trate `low`, `high` ou budgets de
   provedores distintos como quantidades equivalentes de raciocínio.
7. Apresente alternativas consideradas, evidências, incertezas e justificativa
   dos perfis. Recomendações de capacidade não são resultados medidos no projeto.
   Se uma comparação prática for necessária, proponha unidades equivalentes e
   verificações; não inicie testes pagos ou workers fora da autorização existente.

Perfis são objetivos, não tabelas universais de modelos: `savings` prioriza custo
total por resultado aceito, `base` equilibra qualidade, tempo e recursos, e
`aggressive` prioriza margem de capacidade dentro dos limites aprovados. Eles
podem escolher o mesmo modelo com esforços diferentes ou modelos distintos.
Não imponha essas diferenças quando as evidências não as justificarem.

## Quando repetir

- Faça pesquisa oficial no setup/reconfiguração; uma consulta já realizada na
  mesma sessão pode ser reutilizada, identificando data, fonte e condições.
- Antes de cada rodada, confira acesso/cotas recentes, tarefa, limites e a
  compatibilidade do cadastro. Não refaça toda a pesquisa para cada tarefa pequena.
- Pesquise novamente quando surgir modelo, rota, modalidade ou necessidade nova;
  houver mudança anunciada, conflito, fonte inacessível ou informação essencial
  ausente/antiga. A aprovação de um perfil não autoriza substituir preferências
  persistentes automaticamente; proponha a revisão quando necessário.
- Ter menos de 60 dias na tabela não comprova atualidade. O aviso de 60 dias do
  runner é um indicador histórico, não permissão para omitir a pesquisa necessária.

## Registro local

Use `orquestrador-research.md` ao lado da política para registrar de forma curta:

- Escopo, provedores considerados e restrições confirmadas.
- URLs efetivamente abertas, data/hora da consulta e informação verificada.
- Modelo/variante, modalidade de cobrança, unidade e condições relevantes.
- Combinações consideradas, escolha e motivo, alternativas descartadas e lacunas.
- O que foi observado na conta e o que ainda depende de confirmação, sem segredos.

O registro é evidência reaproveitável, não uma instrução permanente nem prova de
atualidade futura. Não salve páginas completas, credenciais ou dados de pagamento.
Preços verificados podem atualizar `models` em `orquestrador-prices.json`, com
`source` e `asOf`, preservando `billing` e `accounts`. Preferências e perfis só
são gravados após a aprovação prevista no onboarding.

`prices.json` incluído no pacote é um snapshot histórico de compatibilidade.
`models` sinaliza `pricingEvidence.networkChecked: false`; o `dry-run` usa esse
snapshot para uma estimativa de entrada, sem checagem de rede. Não apresente
esses números como uma pesquisa feita pelo runner ou como gasto efetivo.

## Sem internet ou sem fonte conclusiva

Declare a limitação. Mostre a origem/data do que pôde reutilizar e mantenha preço,
capacidade ou comparação como desconhecidos quando necessário. Não fabrique uma
atualização nem repita consultas sem progresso. Continue unidades que não dependem
da lacuna; peça decisão somente quando ela afetar custo autorizado, acesso ou a
capacidade necessária. Não bloqueie trabalho pequeno apenas para completar preço
opcional de assinatura.

## Pontos de partida, sem preferência de fornecedor

URLs devem ser reconferidas na pesquisa; não são um catálogo fechado:

- [Preços da OpenAI API](https://developers.openai.com/api/docs/pricing)
- [Preços da Claude API](https://platform.claude.com/docs/en/about-claude/pricing)
- [Preços da Gemini API](https://ai.google.dev/gemini-api/docs/pricing)

Outros provedores, assinaturas, marketplaces e gateways exigem suas próprias
fontes oficiais e condições. Uma experiência de teste só com Codex não restringe
as regras da Batuta a Codex.
