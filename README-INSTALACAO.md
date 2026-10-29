# Instalação — Batuta

Este pacote contém a skill completa. Não é necessário baixar arquivos adicionais nem executar um instalador.

1. Extraia a pasta `batuta` para `~/.agents/skills/batuta` (no Windows: `C:\Users\<seu usuário>\.agents\skills\batuta`).
2. Guarde uma cópia da versão anterior antes de substituí-la.
3. Reinicie a sessão do Codex/Orca e diga: `Use a skill batuta e execute o setup inicial conforme references/onboarding.md.`
4. Para abrir o editor: `python scripts/orchestrate.py editor`, quando houver Python disponível.
5. Para gerar um relatório: `python scripts/orchestrate.py report --format html`.

O pacote inclui o runner original adaptado, onboarding, playbooks, páginas HTML de editor e relatório, testes, plugins e hooks. Veja [a atribuição e as alterações](ORCA_ADAPTATION.md) e a [licença](LICENSE).

A integração descobre as capacidades nativas do Orca sem fixar comandos da sua CLI. O runner também funciona sem agentes nativos do Orca. A telemetria do runner pode não incluir descendentes nativos. Os testes upstream estão em `upstream-tests` e as ferramentas auxiliares em `upstream-tools`.
