# Instruções

Dois blocos faltam nesta versão do produto: um em `src/clinica_alura/guardrails.py`, outro em
`src/clinica_alura/graph.py`. Cada um vem com o corpo inteiro comentado (mostrando a forma completa da
função) e um `raise NotImplementedError` no final. Pra implementar: descomente o bloco, substitua cada
`...` pelo valor pedido no `# TODO` logo acima, e apague o `raise NotImplementedError`. O resto (tools,
`retry_tool`, `needs_approval`/`APPROVAL_POLICY`, o fluxo `--approve` no `app.py`, `book_appointment`) já
vem pronto.

## 1. `PatientAccessGuardrail.wrap_tool_call`: bloquear acesso a outro paciente

`PatientAccessGuardrail` é um `AgentMiddleware` customizado que intercepta toda chamada de tool
(`wrap_tool_call`). A regra: se a tool chamada for `get_patient_record` e o `patient_id` pedido nos
argumentos da tool for diferente do paciente identificado nesta conversa (`request.runtime.context`),
bloqueia e devolve uma `ToolMessage` de erro em vez de deixar a tool rodar.

Preencha:
- `requested_id`, o `patient_id` pedido: `request.tool_call["args"].get("patient_id")`;
- `current_id`, o paciente da conversa atual: `request.runtime.context.patient_id`;
- `payload`, um dicionário com `status`, `reason` e `message` descrevendo o bloqueio (veja o formato usado
  em `check_urgency_flags`/outras respostas de erro do produto pra manter o padrão de chaves).

Quando a condição não bate (tool diferente, ou mesmo paciente, ou sem `patient_id` pedido), a chamada segue
normal: `return handler(request)`.

## 2. `assistant`: montando a lista de middleware do agente

`create_agent` aceita uma lista `middleware=[...]`, aplicada nesta ordem a toda chamada do agente. Preencha
essa lista com:
- `PIIMiddleware("email", strategy="redact", apply_to_input=True)`, redigindo email antes do modelo ver;
- `PIIMiddleware("cpf", detector=detect_cpf, strategy="redact", apply_to_input=True)`, mesma ideia pra CPF,
  usando o detector customizado que já vem pronto em `guardrails.py`;
- `PatientAccessGuardrail()`, o guardrail que você acabou de implementar no bloco 1;
- `retry_tool`, o retry genérico que já vem pronto;
- `HumanInTheLoopMiddleware(interrupt_on=APPROVAL_POLICY)`, pausando a execução quando a política de
  aprovação (também já pronta) exigir.

O resto da função (`assistant_config`, `model`, `human_message`, `agent.invoke(...)`, o `return`) segue
exatamente o padrão que já apareceu pronto nesta versão do produto; só a lista de `middleware` é nova.

## Verificando

```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
sqlite3 data/clinic.db < data/schema.sql   # cria o banco (idempotente)
uv run pytest -v
```

Antes de implementar, 21 testes falham com `NotImplementedError`: os dois testes de
`PatientAccessGuardrail` em `test_guardrails.py` (chamam `wrap_tool_call` direto) e 19 testes de
`test_graph.py` que passam por `assistant` (praticamente todos, menos os dois que só passam por
`human_handoff`: `test_routes_urgent_to_human_handoff` e `test_transcript_records_human_handoff_turn`). Os
outros arquivos de teste (`test_app.py`, `test_auth.py`, `test_db.py`, `test_threads.py`, `test_tools.py`)
não dependem de nenhum dos dois blocos e já passam. Depois de implementar os dois, todos os 47 passam.

Agendar cardiologia pausa a execução (o `HumanInTheLoopMiddleware` do bloco 2); a segunda chamada, com o
mesmo `--patient`, aprova e conclui:

```bash
uv run clinica-alura chat --patient 123 --password alura123 -m "Quero agendar cardiologia dia 2026-09-10 às 09h"
uv run clinica-alura chat --patient 123 --password alura123 --approve approve
```
