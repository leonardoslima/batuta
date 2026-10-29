# Atribuição e alterações

Esta é uma adaptação de compatibilidade de **Kc1t/alethe-orchestrate-skill**, sob licença MIT.
Fonte: https://github.com/Kc1t/alethe-orchestrate-skill
Commit upstream de referência: `3268b6d115cb27d58ebf3409de6c49d55f919477` (v19, 2026-10-23).

A licença, os scripts, os 11 playbooks, o suporte a modelos e cotas, o onboarding, o editor e o relatório do projeto original foram preservados. Esta adaptação acrescenta a descoberta de capacidades do Orca e a orquestração nativa opcional, remove bloqueios artificiais de subagentes nativos nos workers Codex e Claude, atualiza o contrato dos workers e usa o nome público **Batuta**. Os nomes técnicos antigos têm migração compatível.

Esta adaptação não oferece um adaptador completo para todas as ferramentas nativas do Orca nem telemetria unificada de tokens de descendentes nativos.

O núcleo atual da Batuta é independente do host. O procedimento geral está em
[native-execution.md](references/native-execution.md); as particularidades do
Orca ficam em [orca-integration.md](references/orca-integration.md), carregadas
somente quando esse ambiente estiver em uso. O nome deste documento registra
a origem da adaptação, sem definir Orca como requisito de instalação ou execução.

A marca histórica Alethe e as marcas dos provedores pertencem aos respectivos titulares.

A identidade pública desta adaptação é **Batuta**, incluindo páginas visuais,
metadados, mensagem de modo contínuo e identificação da CLI. Nomes de arquivos
persistidos `orquestrador-*`, variáveis `ORQUESTRADOR_*`/`ALETHE_*`, caminhos de
migração e o identificador histórico do esquema permanecem por compatibilidade.
Os documentos `UPSTREAM_*` e a licença preservam a atribuição original. Os hooks
procuram a estrutura atual e `skills/batuta` antes dos caminhos legados; os
manifestos em `upstream-plugins` continuam sendo modelos de empacotamento, não
uma instalação de plugin validada por esta cópia da skill.
