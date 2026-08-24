# Clínica Alura, produto (v0.2)

O agente da v0.1 vira um nó dentro de um `StateGraph`, com um fluxo de atendimento explícito ao redor dele.

## O que esta versão entrega
- Dois nós de entrada em paralelo (`log_reception`, `check_urgency_flags`) escrevendo num campo do estado com
  reducer (`notes: Annotated[list[str], operator.add]`).
- Um nó classificador (`classify`) que decide a intenção do paciente: informação, agendamento ou urgência.
- Um roteador (`route_by_intent` + `add_conditional_edges`) que aciona o agente da Aula 1 (nó `assistant`)
  para informação/agendamento, ou encaminha direto para atendimento humano (nó `human_handoff`) em caso de
  urgência, sem chamar o modelo de novo.
- `clinica-alura chat` sem `-m` abre uma conversa: o histórico de mensagens é repassado a cada novo turno,
  então o agente usa o contexto da conversa. Essa memória vive só enquanto o processo está rodando; feche a
  conversa e a próxima começa do zero. `chat -m "..."` continua disponível para uma pergunta isolada.
- As 4 tools da v0.1 (`find_available_slots`, `get_clinic_hours`, `list_specialties`,
  `estimate_consultation_price`) seguem disponíveis, agora por dentro do nó `assistant`.

## Como rodar
```bash
uv sync
cp .env.example .env   # preencha OPENAI_API_KEY
uv run pytest -v
```

Mensagem única:
```bash
uv run clinica-alura chat -m "Quero agendar dermatologia"
uv run clinica-alura chat -m "Estou com uma dor forte no peito agora"
```

Conversa aberta (mesma execução, contexto mantido entre turnos):
```bash
uv run clinica-alura chat
Você: Quero agendar dermatologia
Você: Pode ser amanhã?
Você: sair
```
