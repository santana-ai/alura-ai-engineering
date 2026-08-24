# Clínica Alura, produto (v0.3)

O produto passa a personalizar por paciente, ler dados da clínica de um banco SQLite e guardar a memória da
conversa num arquivo, sobrevivendo ao fim do processo.

## O que esta versão entrega
- Contexto de runtime por paciente (`ClinicContext`), lido dentro das tools via `ToolRuntime` e dentro do nó
  `assistant` via `Runtime`. Identificar o paciente é opcional: a triagem geral (agendamento, dúvidas,
  urgência) continua funcionando sem saber quem está falando, exatamente como na v0.2.
- Duas tools novas, lendo do banco `data/clinic.db`: `get_patient_record` (cadastro do paciente atual) e
  `lookup_policy` (políticas da clínica por tema). As 4 tools da v0.2 seguem disponíveis.
- Memória de conversa persistida em arquivo (`SqliteSaver`, `state.db`) só quando há paciente identificado:
  uma conversa sobrevive ao fim do processo, e duas execuções separadas de `chat --patient ...` continuam a
  mesma conversa. Sem `--patient`, a memória vive só em RAM (`InMemorySaver`) durante a execução; `state.db`
  não chega a ser criado.
- Login simples antes de liberar `--patient`: sem a senha certa (`--password`), o cadastro do paciente não
  é acessível e a memória de conversa não é liberada.
- `--new`: abre uma conversa nova e isolada para o paciente, sem misturar com a conversa anterior. Por
  padrão (sem `--new`), a CLI sempre continua a conversa ativa do paciente; não existe como voltar a uma
  conversa anterior depois de abrir uma nova.
- `--history`: mostra as mensagens da conversa ativa do paciente e sai, sem entrar em modo de conversa.
  Por padrão, os últimos 2 turnos; `--history all` mostra a conversa inteira. Só a pergunta do paciente e a
  resposta final aparecem, nunca uma chamada de tool no meio do caminho. Exige `--patient` identificado.
- Modo conversa aberta (`chat` sem `-m`) não repassa mais uma lista de mensagens manual: o checkpointer
  resolve o histórico sozinho, a partir do `thread_id`.

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

Sem identificar o paciente (triagem geral, como sempre):
```bash
uv run clinica-alura chat -m "Quais especialidades vocês atendem?"
```

Com paciente identificado, cadastro e memória persistente:
```bash
uv run clinica-alura chat --patient 123 --password alura123 -m "Qual o preparo do exame de sangue?"
uv run clinica-alura chat --patient 123 --password alura123 -m "Qual é o meu cadastro na clínica?"
```

Abrindo uma conversa nova, sem misturar com a anterior:
```bash
uv run clinica-alura chat --patient 123 --password alura123 --new -m "Quero começar do zero."
```

Revendo a conversa ativa:
```bash
uv run clinica-alura chat --patient 123 --password alura123 --history
uv run clinica-alura chat --patient 123 --password alura123 --history all
```

Conversa aberta (múltiplos turnos, mesma execução):
```bash
uv run clinica-alura chat --patient 123 --password alura123
Você: Qual o preparo do exame de sangue?
Você: sair
```
