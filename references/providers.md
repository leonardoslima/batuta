# Adaptadores de provedores

Leia ao escolher provedor, retomar worker ou definir adaptador personalizado. O runner usa arrays de argumentos. Um shim .cmd ilegível passa por cmd.exe somente sob as restrições da seção Windows.

## Adaptadores embutidos

| Provedor | Executável | Leitura isolada | Escrita | Retomada | Resultado estruturado |
| --- | --- | --- | --- | --- | --- |
| Codex | codex | sandbox read-only | sandbox workspace-write | codex exec resume | eventos JSONL e mensagem final |
| Claude Code | claude | permission mode plan | acceptEdits | --resume | stream JSON |
| Agy / Antigravity | agy | mode plan | accept-edits | --conversation | resultado JSON |
| Kimi Code | kimi | nenhum; veja abaixo | prompt mode | --session | stream JSON |

antigravity é alias aceito para agy nos planos.

Use provider: auto para worker novo sem modelo, esforço ou sessão específicos de provedor. O runner escolhe o primeiro provedor instalado na providerOrder salva que não esteja em conserveProviders e consiga executar a fase. Kimi não recebe leitura isolada. Um provedor explícito só muda automaticamente com providerSwitch: automatic; nos demais casos, é respeitado ou a validação solicita decisão.

O runner consulta --help local para flags opcionais. Como CLIs mudam, confira stderr.log e outcome.json; código de saída isolado não prova sucesso.

Formatos equivalentes para uma nova sessão:

~~~text
codex exec --sandbox read-only|workspace-write --json --output-last-message <result> --cd <cwd> --config mcp_servers={} -
claude --print --output-format stream-json --verbose --permission-mode plan|acceptEdits --strict-mcp-config [--max-budget-usd <cap>]
agy --output-format json --mode plan|accept-edits --print-timeout <seconds>s --add-dir <cwd> --print=<task>
kimi --output-format stream-json --prompt=<task>
~~~

Codex e Claude recebem a tarefa por entrada padrão. Agy e Kimi exigem prompt na flag; --print do Agy pode absorver a flag seguinte se o valor não estiver anexado. Como o prompt vira argumento nesses provedores, a validação recusa tarefas acima de cerca de 30.000 caracteres no Windows ou 100.000 nos demais sistemas. Mantenha stdout e stderr separados e limite externamente o tempo mesmo quando o CLI oferecer timeout.

## O que o runner restringe

- Subagentes: a adaptação Orca não desativa artificialmente subagentes nativos em Codex ou Claude. Workers permanecem limitados ao escopo recebido. ORQUESTRADOR_ORCHESTRATE_WORKER=1 impede segunda orquestração; o nome legado da variável continua aceito. Descendentes podem ultrapassar a contabilidade de cota do pai.
- Servidores MCP: Codex recebe mcp_servers vazio e Claude --strict-mcp-config. Isso evita custo de inicialização e definições de ferramentas desnecessárias. Defina mcp: true quando um brief precisar de servidor.
- Gasto: se o Claude instalado aceitar --max-budget-usd, o worker recebe o orçamento relatado restante por essa flag. Sem a flag, o limite de custo relatado só impede workers posteriores.

acceptEdits do Claude não autoriza todos os comandos de shell. O runner pede permissões não interativas quando houver suporte. Negativas aparecem em permissionDenials no outcome.json; o relatório alerta que verificações podem não ter rodado.

Kimi em prompt mode usa permissão automática e rejeita --plan, --yolo e --auto combinados com --prompt. Sua leitura isolada depende do contrato e do monitoramento posterior; writer Kimi exige worktree isolada. validate alerta sobre ambos.

Se um worker Agy em modo de leitura não retornar nada, o modo plan pode ter parado num comando que depende de aprovação humana; encaminhe essa leitura a Codex ou Claude.

## Windows

Instalações npm podem expor codex, claude, kimi ou gemini como shims .cmd. cmd.exe reinterpreta argumentos de batch: corta no primeiro newline e pode executar texto após aspas desequilibradas. O runner lê o shim npm e chama seu alvo real diretamente, como node <script> ou executável nativo; probe mostra o launch resolvido. Um batch ilegível só passa por cmd.exe quando nenhum argumento contém newline, aspas, &, |, <, >, ^, % ou !. Caso contrário, é recusado; aponte ao executável real.

## Retomada

Copie sessionId de worker bem-sucedido para resume em worker posterior do mesmo provedor. Codex retoma com sandbox e esforço do novo worker; Claude, Agy e Kimi preservam as opções da sessão original. Claude transmite eventos, então um timeout ainda pode deixar sessionId para estratégia rescue.

Retome apenas acompanhamento relacionado. Sem sessionId, crie novo worker com handoff breve.

## CLIs personalizados

Use provider: custom com command (nome ou caminho), args (array; placeholders {cwd} e {result} sem expansão de shell), promptTransport (stdin ou argument) e outputFormat (text, json ou jsonl).

Adaptadores personalizados não herdam garantias de leitura isolada, retomada, tokens ou cota. Aplique restrições do provedor nos argumentos e isole a worktree se puder escrever. O onboarding registra o adaptador verificado em adapters; construa o worker a partir dessa entrada.

Dê a permissão mínima para escrita, por exemplo --trust-tools=fs_read,fs_write no Kiro ou --allow-tool write no Copilot. Flags que autorizam todas as ferramentas, como --trust-all-tools, --allow-all-tools e --yolo, exigem allowUnsafe: true e autorização explícita do usuário para perder isolamento.

## Recursos MCP ausentes no runner CLI

Workers CLI comuns não aparecem no quadro nativo de orquestração e não oferecem direcionamento no meio do turno nem diálogos de aprovação. Cotas de Codex e Claude podem ser lidas com usage; outras dependem do host ou do usuário, conforme [playbooks.md](playbooks.md). Use ferramentas MCP compatíveis quando quadro ou direcionamento ao vivo forem necessários.
