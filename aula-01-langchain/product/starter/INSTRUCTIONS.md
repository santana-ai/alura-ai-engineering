# Instruções, Clínica Alura (v0.1)

O produto já está pronto: CLI (`app.py`), montagem do agente (`agent.py`) e config (`config.yaml` +
`config.py`) funcionam. Os dados da clínica (`SCHEDULE`, `HOURS`, `SPECIALTIES`, `PRICES`) também já
estão em `src/clinica_alura/tools.py`. Falta implementar 3 das 4 tools que leem esses dados. A quarta,
`find_available_slots`, já está pronta como referência do padrão a seguir.

## TODOs

1. **`get_clinic_hours(day_of_week)`**: leia `HOURS` e devolva o horário do dia da semana informado
   (compare em minúsculas, como a `find_available_slots` já faz com `specialty`).
2. **`list_specialties()`**: monte a lista de especialidades a partir de `SPECIALTIES`.
3. **`estimate_consultation_price(specialty)`**: leia `PRICES` e devolva o preço da especialidade
   informada.

Não mude as assinaturas nem as docstrings: são o contrato que o modelo usa para decidir quando chamar
cada tool.

## Como verificar

```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
uv run pytest -v       # 2 passam, 5 falham até você implementar as 3 tools
```

Quando as 3 tools estiverem implementadas, `uv run pytest -v` passa por inteiro.

Em seguida, faça uma pergunta, por exemplo:
```bash
uv run clinica-alura chat -m "Quais especialidades vocês atendem?"
```