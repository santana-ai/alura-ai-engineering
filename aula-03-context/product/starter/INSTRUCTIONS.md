# Instruções

Três blocos faltam nesta versão do produto, todos em `src/clinica_alura/graph.py`. Cada um vem com o corpo
inteiro comentado (mostrando a forma completa da função) e um `raise NotImplementedError` no final. Pra
implementar: descomente o bloco, substitua cada `...` pelo valor pedido no `# TODO` logo acima, e apague o
`raise NotImplementedError`. O resto (tools, contexto por paciente, login, `--new`, `--history`,
`config.yaml`) já vem pronto.

## 1. `classify` e `assistant`: configuração vinda do `RunnableConfig`

`app.py` já carrega `config.yaml` e monta o `config` que chega em todo nó via `config: RunnableConfig` — o
mesmo formato do YAML, só que dentro de `config["configurable"]`. `config.yaml` tem uma seção `assistant:` e
uma `classifier:`, cada uma com `model` (`name`/`temperature`) e `system_prompt`; pra acessá-las dentro de
um nó, comece sempre por `config["configurable"]`.

Exemplo, pra `classifier_config` dentro de `classify`:
```python
classifier_config = config["configurable"]["classifier"]
```

A partir daí, `classifier_config["model"]["name"]` e `classifier_config["model"]["temperature"]` alimentam
o `ChatOpenAI`. Em `classify`, preencha:
- `classifier_config`, como no exemplo acima;
- `model`, um `ChatOpenAI(model=..., temperature=...)` com os dois campos de `classifier_config["model"]`.

Em `assistant`, o mesmo padrão, trocando `classifier` por `assistant`:
- `assistant_config`, a partir de `config["configurable"]["assistant"]`;
- `model`, igual acima, usando `assistant_config["model"]`;
- `agent`, um `create_agent(model=model, tools=TOOLS, system_prompt=assistant_config["system_prompt"],
  context_schema=ClinicContext)`.

## 2. `build_graph`: escolha do checkpointer

Preencha `checkpointer`: `InMemorySaver()` se `checkpointer_path` for `None` (conversa sem paciente
identificado, memória só em RAM); senão `SqliteSaver(sqlite3.connect(checkpointer_path,
check_same_thread=False))` (memória em arquivo).

## Verificando

```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
sqlite3 data/clinic.db < data/schema.sql   # cria o banco (idempotente)
uv run pytest -v
```

Antes de implementar, todo `test_graph.py` falha com `NotImplementedError` (todo `graph.invoke(...)` passa
por `classify` e por um `checkpointer` montado em `build_graph`, os dois ainda sem implementação). Os
outros arquivos de teste (`test_app.py`, `test_auth.py`, `test_db.py`, `test_threads.py`, `test_tools.py`)
não dependem de nenhum dos três blocos e já passam. Depois de implementar os três, todos os testes passam.

```bash
uv run clinica-alura chat --patient 123 --password alura123 -m "Qual o preparo do exame de sangue?"
```
