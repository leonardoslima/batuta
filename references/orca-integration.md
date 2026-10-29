# Particularidades do Orca

Leia somente quando o ambiente em uso for Orca. O procedimento de agentes
nativos está em [native-execution.md](native-execution.md); este arquivo
complementa esse procedimento, sem tornar Orca requisito da Batuta.

## Recursos gerenciados

- Orca é o aplicativo hospedeiro, não necessariamente o backend dos agentes.
  Sua presença não comprova disponibilidade de delegação nativa.
- Confira ferramentas e comandos realmente expostos pelo Orca e pelo runtime
  antes de usá-los. Não presuma nomes de API, verbos CLI ou modelos.
- Use workspace, worktree, terminal, navegador e agentes gerenciados pelo Orca
  quando existirem, forem permitidos e fizerem sentido. Não crie outro
  gerenciador para checkout ou sessão já pertencente ao Orca.
- Workers CLI não aparecem automaticamente no quadro nativo do Orca.
  O runner Python não inicia agentes desse quadro.

## Configuração e interação

Para setup/reconfiguração, siga [onboarding.md](onboarding.md), incluindo
contas, modelos, cotas, perfis e aprovação antes de salvar. Inclua no inventário
as ferramentas de agentes que o Orca realmente expuser. Este adaptador não
exige repetir onboarding em uma tarefa ou consulta já autorizada.

Se houver ferramenta de perguntas interativas, use-a para decisões necessárias;
caso contrário, converse normalmente. Sem ferramenta suficiente, explique o
que não pôde verificar. Preserve o editor offline e os relatórios da Batuta;
eles não dependem do quadro nativo nem comprovam que seus agentes foram coletados.

Para observações persistentes, consulte [tracing.md](tracing.md). O principal
registra somente IDs e métricas realmente expostos. A integração não oferece
coleta automática completa nem estende limites do runner a agentes nativos.
