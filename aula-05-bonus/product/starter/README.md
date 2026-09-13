# Clínica Alura, produto (v0.4)

O produto fica mais seguro: protege dado sensível, impede acesso ao cadastro de outro paciente e passa a
pedir aprovação humana antes de confirmar um agendamento de cardiologia.

## O que esta versão entrega
- `PIIMiddleware` redigindo email e, com um detector customizado, CPF, antes de qualquer mensagem chegar
  no modelo.
- Guardrail customizado (`PatientAccessGuardrail`) bloqueando `get_patient_record` quando alguém pede o
  cadastro de um paciente diferente do identificado na conversa.
- Retry genérico (`retry_tool`) envolvendo toda chamada de tool, incluindo a nova `book_appointment`.
- Nova tool `book_appointment`, gravando o agendamento em `data/clinic.db`.
- Human-in-the-loop: agendar cardiologia pausa a execução até alguém aprovar ou rejeitar
  (`HumanInTheLoopMiddleware`); dermatologia e clínica geral agendam direto, sem pausa.
- `--approve approve|reject`: resolve uma aprovação pendente, na mesma chamada que enviou a mensagem ou
  numa chamada separada depois. Na conversa aberta (sem `-m`), a pergunta aparece direto no terminal.

## Diferença de schema em relação aos notebooks da aula

Os notebooks usam `ClinicContext(patient_id, unit)`, porque `unit` alimenta uma demonstração de prompt de
sistema por unidade. Aqui, nenhuma tool usa `unit`, então o produto usa só `ClinicContext(patient_id)`.
Pelo mesmo motivo, `data/schema.sql` deste produto tem uma coluna `password` a mais que o `schema.sql` dos
notebooks: login é uma decisão de aplicação, não algo que os notebooks precisam ensinar.

## Como rodar
```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
sqlite3 data/clinic.db < data/schema.sql   # cria o banco (idempotente)
uv run pytest -v
```

Agendando uma especialidade sem gate (agenda direto):
```bash
uv run clinica-alura chat --patient 123 --password alura123 -m "Quero agendar dermatologia dia 2026-09-10 às 14h"
```

Agendando cardiologia, aprovação na mesma chamada:
```bash
uv run clinica-alura chat --patient 123 --password alura123 --approve approve \
  -m "Quero agendar cardiologia dia 2026-09-10 às 09h"
```

Agendando cardiologia em duas chamadas (a primeira pausa e avisa; a segunda resolve):
```bash
uv run clinica-alura chat --patient 123 --password alura123 -m "Quero agendar cardiologia dia 2026-09-11 às 09h"
uv run clinica-alura chat --patient 123 --password alura123 --approve approve
```

Esse fluxo de duas chamadas exige `--patient`: sem paciente identificado, cada chamada abre uma thread
nova e a aprovação pendente da chamada anterior não sobrevive até a próxima.

Na conversa aberta, uma pausa pergunta direto no terminal:
```bash
uv run clinica-alura chat --patient 123 --password alura123
Você: Quero agendar cardiologia dia 2026-09-12 às 09h
Aprovar ou rejeitar? [approve/reject]: approve
```

Dado sensível sai protegido da conversa:
```bash
uv run clinica-alura chat -m "Meu email é ana@example.com e meu CPF é 123.456.789-09, pode anotar?"
```
