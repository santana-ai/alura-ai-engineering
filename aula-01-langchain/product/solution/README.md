# Clínica Alura, produto (v0.1)

CLI do Assistente da Clínica Alura no seu primeiro estágio: um agente que conversa e consulta a agenda.

## O que esta versão entrega
- Um agente (ReAct) com 4 tools: `find_available_slots`, `get_clinic_hours`, `list_specialties` e
  `estimate_consultation_price`.
- Comando de conversa: `clinica-alura chat`, com um spinner enquanto o agente processa.
- Dados da clínica direto nas tools (dicts em `tools.py`, ainda sem DB). O `config.yaml` guarda só o
  modelo e o `system_prompt`.

## Como rodar
```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
uv run pytest -v
```

Em seguida, faça uma pergunta. Por exemplo:
```bash
uv run clinica-alura chat -m "Tem cardiologia dia 2026-07-20?"
```
