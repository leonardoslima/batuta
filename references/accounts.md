# Contas, planos e capacidade disponível

Leia durante o onboarding e antes de escolher provedores, modelos e quantidade
de workers. O plano influencia o planejamento junto das cotas atuais e do
histórico compatível. O preço da assinatura não determina sua capacidade.

## Descoberta e confirmação

1. Consulte `usage` e `models`. Ambos apresentam `account` por provedor; `usage`
   atualiza a observação local Codex, enquanto `models` usa a leitura já salva.
2. O runner lê o plano somente quando a telemetria Codex expõe
   `rate_limits.plan_type`. Sem esse campo, não adivinha. A observação é
   armazenada no cache de uso, sem alterar preferências confirmadas.
3. Para outros provedores e capacidades, use dados locais ou respostas
   documentadas das ferramentas. Não leia credenciais nem inicie workers apenas
   para descobrir o plano. Um catálogo de modelos não comprova acesso da conta.

`models` separa origem do inventário e preço: `inventorySources` identifica
playbooks, preços, cache Codex ou cadastro confirmado; `discovered` indica
evidência no cache/cadastro. `discovery.candidates` inclui modelos visíveis do
cache e modelos do cadastro confirmado, com os esforços quando informados.
Não é garantia de acesso atual: o cache pode pertencer a outra sessão/conta.
`discovery.accountAccessVerified` permanece falso; concilie com o host e a conta.
O campo `stale` da descoberta é um aviso após 24 horas, ou sem data, não uma
regra de validade do fornecedor. Não elimine um candidato por faltar preço:
`priceMissing` e o alias legado `missing` se referem exclusivamente ao preço.
4. Pergunte apenas pelo que faltar. Plano, valor, moeda, periodicidade, modelos,
   limites e extras podem continuar desconhecidos. Não bloqueie uma tarefa
   apenas para completar campos opcionais.
5. Confirme antes de salvar preferências, seguindo o onboarding. Concilie
   conflitos com o usuário, sem sobrescrever o cadastro automaticamente.
   O runner ignora observações anteriores à data do cadastro e sinaliza
   observações antigas ou conflitantes.

Uma leitura posterior sem nome de plano preserva a última observação, com sua
origem e data reais. A ausência do campo não resolve um conflito automaticamente.

## Configuração local

Em `orquestrador-prices.json`, ao lado da política, mantenha `models` e `billing`
existentes e acrescente `accounts`. Exemplo **fictício**, sem representar planos
ou preços atuais de fornecedores:

```json
{
  "billing": {"codex": "subscription"},
  "accounts": {
    "codex": {
      "plan": "example-plan",
      "price": {"amount": 20, "currency": "USD", "period": "month"},
      "source": "user",
      "observedAt": "2026-10-29T12:00:00Z",
      "confirmed": true,
      "models": ["example-model"],
      "limits": {"window": "Limite informado pelo usuário, sem conversão em tokens"},
      "extraUsageEnabled": true,
      "extraUsageAuthorized": false,
      "consumption": "preserve"
    }
  }
}
```

- `billing`: `subscription` ou `api`, por provedor; compatível com cadastros antigos.
- `plan`: nome/variante exata quando verificada. Não invente variantes quando a
  telemetria só informar uma família genérica.
- `price`: opcional ou `null`; valor não negativo, moeda com três letras
  maiúsculas, período `month`, `year`, `week` ou `day`. Não converter mensalidade
  em preço por token.
- `source` e `observedAt`: obrigatórios em cada cadastro; origem e timestamp ISO.
  Não incluir segredos, dados de pagamento nem respostas de autenticação.
- `confirmed`: confirmação pelo usuário, não da telemetria.
- `models`: IDs com acesso verificado. Lista vazia significa desconhecido;
  ausência de um modelo gera alerta, não prova de bloqueio.
- `limits`: nomes com números não negativos ou descrições verificadas. São
  contexto para o agente; não se convertem em limites executáveis do runner.
- `extraUsageEnabled`: habilitação no provedor; ausente significa desconhecido.
- `extraUsageAuthorized`: só vale com cadastro confirmado. Habilitação não
  concede autorização; ausência equivale a não autorizado.
- `consumption`: `preserve`, `balanced` (padrão) ou `use-before-reset`.

Omita campos desconhecidos, exceto `price`, que também aceita `null`. Valide com
`python scripts/orchestrate.py models --policy <caminho-da-politica>`.
Dados da conta ficam locais, sem inclusão no repositório da skill.

## Efeito no fluxo

O agente principal continua responsável pelo roteamento. Use `accounts` e os
alertas do `dry-run` antes de preparar a rodada:

- Verifique acesso ao modelo e capacidade necessária antes de preferir um provedor.
- Com `preserve`, prefira unidades menores, menor concorrência e alternativas
  capazes com cota disponível; não reduza o nível necessário sem autorização.
- Com `use-before-reset`, aproveite cota que expiraria apenas com reset conhecido,
  leitura recente e margem dentro dos thresholds e do orçamento.
- Um plano maior permite considerar mais trabalho com evidência de capacidade
  e cota. Não multiplique workers proporcionalmente à mensalidade.
- Com API, use preços e orçamento de API; com assinatura, cotas e histórico.
  Plano ou preço desconhecido não significa acesso ou capacidade ilimitados.
- Não dependa de extras pagos sem autorização. Alertas não desabilitam cobrança
  nem substituem as configurações do provedor; não altere essas configurações.

## Previsões e troca de plano

Leituras e amostras novas guardam `accountContext`, derivado do plano, cobrança,
preço e capacidades cadastradas. Alterar só fonte, data ou preferência não troca
o contexto. Uma rodada que cruza contextos diferentes não gera amostra.

`quotaForecast` usa somente amostras do mesmo contexto. Amostras antigas sem
contexto continuam compatíveis enquanto o plano for desconhecido; ao descobrir
ou cadastrar um plano, deixam de servir. Com poucas amostras compatíveis, a
previsão fica desconhecida. Desconhecido não significa consumo zero.

Reler a mesma cota não muda seu contexto original. Previsões ficam desconhecidas
enquanto a leitura pertencer a outro contexto, houver conflito ou a evidência
descoberta do plano estiver antiga; obtenha uma leitura nova ou concilie o cadastro.

O isolamento cobre o contexto conhecido do plano, não a identidade autenticada.
Trocas de conta não detectáveis e mudanças de limite sem telemetria exigem
confirmação e avaliação pelo agente principal.
