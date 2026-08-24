# Instruções, Clínica Alura (v0.2)

O produto já está pronto: o agente da v0.1 (`agent.py`, `tools.py`, `config.py`, `config.yaml`) não muda, e o
grafo em `src/clinica_alura/graph.py` já tem o estado (`TriageState`), os dois nós de entrada em paralelo
(`log_reception`, `check_urgency_flags`), o nó que chama o agente (`assistant`) e o nó de encaminhamento
(`human_handoff`) prontos. A CLI (`app.py`), com o modo de mensagem única e o modo de conversa aberta, também
já está pronta. Falta implementar o nó classificador e o roteamento condicional que decide para onde a
mensagem vai.

## TODOs

1. **`classify(state)`**: monte um `ChatOpenAI` a partir do `config.yaml` (mesmo padrão de `agent.py`),
   aplique `with_structured_output(IntentClassification)` e classifique a última mensagem do paciente
   (junto com `CLASSIFIER_INSTRUCTION`), devolvendo `{"intent": ...}`.
2. **`route_by_intent(state)`**: devolva `state["intent"]`, o valor que o `add_conditional_edges` vai usar
   para decidir o próximo nó.
3. **Aresta condicional em `build_graph()`**: adicione a chamada de `add_conditional_edges` a partir de
   `"classify"`, usando `route_by_intent` como função de roteamento e mapeando `"informação"` e
   `"agendamento"` para `"assistant"`, e `"urgência"` para `"human_handoff"`.

Não mude as assinaturas das funções nem o nome dos nós: os testes e o restante do grafo dependem deles.

## Como verificar

```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
uv run pytest -v       # os testes de tools passam, os de graph falham até você implementar os 3 TODOs
```

Quando os 3 TODOs estiverem implementados, `uv run pytest -v` passa por inteiro.

Em seguida, teste o fluxo completo:
```bash
uv run clinica-alura chat -m "Quero agendar dermatologia"
uv run clinica-alura chat -m "Estou com uma dor forte no peito agora"
```

E a conversa aberta, sem `-m` (o histórico se mantém entre os turnos, dentro dessa mesma execução):
```bash
uv run clinica-alura chat
Você: Quero agendar dermatologia
Você: Pode ser amanhã?
Você: sair
```
