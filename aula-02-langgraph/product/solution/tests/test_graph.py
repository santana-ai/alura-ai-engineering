from clinica_alura.graph import build_graph


def test_parallel_intake_notes_accumulate():
    graph = build_graph()
    result = graph.invoke({"messages": [{"role": "user", "content": "Quero agendar dermatologia"}]})
    assert len(result["notes"]) == 2


def test_routes_scheduling_to_assistant():
    graph = build_graph()
    result = graph.invoke({"messages": [{"role": "user", "content": "Quero agendar dermatologia"}]})
    assert result["intent"] in {"agendamento", "informação"}
    assert "atendimento humano" not in result["messages"][-1].content.lower()


def test_routes_urgent_to_human_handoff():
    graph = build_graph()
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Estou com uma dor forte no peito agora, o que eu faço?"}]}
    )
    assert result["intent"] == "urgência"
    assert "atendimento humano" in result["messages"][-1].content.lower()


def test_conversation_history_carries_forward():
    graph = build_graph()
    first = graph.invoke({"messages": [{"role": "user", "content": "Quero agendar dermatologia"}]})

    second = graph.invoke(
        {"messages": first["messages"] + [{"role": "user", "content": "E pode ser amanhã?"}]}
    )

    assert len(second["messages"]) > len(first["messages"]) + 1
    assert second["messages"][: len(first["messages"])] == first["messages"]
