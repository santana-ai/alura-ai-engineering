# Instruções

Este produto não tem nenhum bloco faltando: é o mesmo Assistente da Clínica Alura da Aula 4 (guardrails,
PII, human-in-the-loop), rodando e testado, sem `raise NotImplementedError` nenhum. `uv sync && sqlite3
data/clinic.db < data/schema.sql && uv run pytest -v` já passa antes de você tocar em qualquer coisa.

O que muda nesta aula é o convite: três peças que você viu nos notebooks (`02_evals.ipynb`,
`03_monitoring.ipynb`, `04_tracing.ipynb`) e que ainda não existem aqui. São independentes, você escolhe
quantas quer implementar, e não tem uma única combinação "certa": cada uma abaixo vem com uma dica de
caminho, não com o código pronto.

## 1. Evals: uma suíte contra regressão

**Objetivo:** um pequeno golden dataset de mensagens de paciente com a resposta certa esperada, rodado
contra o `graph` de verdade, pra pegar se uma mudança futura piorou alguma coisa que já funcionava.

**Dica:** o padrão de `02_evals.ipynb` é o classificador de intenção (`IntentClassification`,
`with_structured_output`) contra um dicionário de cenários com `expected_intent`, comparado por igualdade
exata; o notebook também tem `run_scenarios`/`success_rate`/`find_regressions` prontos pra reaproveitar a
ideia (uma regressão é um cenário que passava antes e passou a falhar, não só a taxa geral caindo). Aqui,
o alvo natural é o `classify` de `graph.py`, que já produz esse `IntentClassification`. Um bom lugar pra
esse código é `tests/test_evals.py`, rodando junto do resto de `uv run pytest`.

## 2. Monitoring: um relatório agregado de execuções

**Objetivo:** cada `uv run clinica-alura chat ...` vira um registro (sucesso, latência, tokens, tools
chamadas); depois de várias execuções, um relatório agregado aponta se algo saiu do padrão.

**Dica:** `03_monitoring.ipynb` tem o formato pronto pra adaptar: um `RunRecord` (dataclass), um
`UsageMetadataCallbackHandler` anexado no `config={"callbacks": [...]}` pra pegar tokens de verdade, e um
`build_report` que compara a execução mais lenta contra a média. Aqui, `chat()` em `app.py` é onde cada
`graph.invoke(...)` acontece; grave um registro por chamada numa tabela nova em `clinic.db` (`db.py` já tem
o padrão de acesso ao banco), e um segundo comando de CLI (`clinica-alura report`, por exemplo) pra ler
essa tabela e imprimir o agregado.

## 3. Tracing: instrumentando com Langfuse

**Objetivo:** cada execução do produto vira um trace navegável no Langfuse, com o caminho completo (chamada
ao modelo, chamada de tool, na ordem em que aconteceram).

**Dica:** `04_tracing.ipynb` é praticamente o código inteiro: `from langfuse.langchain import
CallbackHandler`, `handler = CallbackHandler()` (lê `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/
`LANGFUSE_HOST` do `.env`), anexado no mesmo `config={"callbacks": [...]}` de `graph.invoke(...)`, com
`get_client().flush()` antes da CLI sair (senão os spans não chegam a tempo). A diferença de produção pro
notebook é rodar sem quebrar quando as chaves não estão configuradas: uma função tipo `build_tracer(cfg)`
que devolve `None` nesse caso, pra `chat()` sempre funcionar, com ou sem tracing ligado. Vai precisar
adicionar `langfuse` às dependências (`uv add langfuse`): não vem pré-instalado, já que é opcional.

## Verificando

```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY (e LANGFUSE_* se for pro desafio 3)
sqlite3 data/clinic.db < data/schema.sql   # cria o banco (idempotente)
uv run pytest -v
```

Os testes herdados da Aula 4 já passam antes de qualquer mudança. Se você implementar o desafio 1, seus
testes novos de evals entram na mesma suíte.
