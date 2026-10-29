# Pesquisa antes das escolhas de execução

Direção aprovada pelo usuário: regras de pesquisa e avaliação devem permanecer
estáveis; seleção de modelos, esforços e comparações de custo devem vir de
evidências pertinentes e atuais. A experiência pessoal com Codex não restringe
o funcionamento da Batuta a esse provedor.

## Decisões

- O agente principal pesquisa páginas oficiais no setup/reconfiguração e diante
  de informação essencial ausente, antiga ou conflitante. O runner não navega.
- Rodadas seguintes podem reutilizar evidências pertinentes com origem/data,
  conferindo cotas e acesso recentes antes da execução.
- Playbooks distribuídos não escolhem modelo/esforço nem forçam provedor em fases
  ou regras. Tiers vazios exigem resolução pelo agente antes de delegar. A escolha
  explícita pelo padrão do CLI continua compatível e deve ser informada.
- Perfis expressam objetivos; a combinação de modelo e esforço é avaliada pela
  tarefa e recursos, sem esforço baixo obrigatório para modelos econômicos.
- A tabela local é snapshot histórico. Estimativas do runner deixam explícito que
  não consultaram a rede; não são comparações de custo total ou medições de qualidade.
- Configurações pessoais antigas continuam legíveis e não são sobrescritas.
  Exemplos antigos ficam em fixtures de teste, sem se tornarem recomendações.
- Sem rede, declarar a limitação, distinguir dados antigos e continuar somente
  decisões que não dependam da lacuna, sem inventar preços ou capacidades.

## Limites desta mudança

Não inclui rastreabilidade unificada de subagentes ou medição de custo nativo.
Não altera contas, credenciais, quotas contratadas ou configurações pessoais.
O usuário proibiu commit até novo pedido. Sem commit, push ou atualização da
instalação nesta mudança; a cópia do projeto permanece disponível para revisão.
