from langchain.messages import ToolMessage

from clinica_alura.config import load_config
from clinica_alura.context import ClinicContext
from clinica_alura.graph import build_graph
from clinica_alura.threads import resolve_thread_id

APP_CONFIG = load_config()


def build_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
            "assistant": APP_CONFIG["assistant"],
            "classifier": APP_CONFIG["classifier"],
        }
    }


ANON_CONTEXT = ClinicContext()
ANON_CONFIG = build_config("test-anon")


def test_parallel_intake_notes_accumulate(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Quero agendar dermatologia"}]},
        config=ANON_CONFIG,
        context=ANON_CONTEXT,
    )
    assert len(result["notes"]) == 2


def test_routes_scheduling_to_assistant(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Quero agendar dermatologia"}]},
        config=ANON_CONFIG,
        context=ANON_CONTEXT,
    )
    assert result["intent"] in {"agendamento", "informação"}
    assert "atendimento humano" not in result["messages"][-1].content.lower()


def test_routes_urgent_to_human_handoff(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Estou com uma dor forte no peito agora, o que eu faço?"}]},
        config=ANON_CONFIG,
        context=ANON_CONTEXT,
    )
    assert result["intent"] == "urgência"
    assert "atendimento humano" in result["messages"][-1].content.lower()


def test_get_patient_record_without_patient_is_not_identified(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Qual é o meu cadastro na clínica?"}]},
        config=ANON_CONFIG,
        context=ANON_CONTEXT,
    )
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert any("nenhum paciente identificado" in m.content.lower() for m in tool_messages)


def test_get_patient_record_with_patient_returns_registration(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Qual é o meu cadastro na clínica?"}]},
        config=build_config("test-patient-123-registration"),
        context=ClinicContext(patient_id="123"),
    )
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert any("ana souza" in m.content.lower() for m in tool_messages)


HOBBY_STATEMENT = "Nas horas vagas, estou aprendendo a tocar violão."
HOBBY_QUESTION = "O que eu disse que estou aprendendo nas horas vagas?"


def test_memory_within_same_graph_instance(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    context = ClinicContext(patient_id="123")
    config = build_config("test-memory-same-instance")

    graph.invoke({"messages": [{"role": "user", "content": HOBBY_STATEMENT}]}, config=config, context=context)
    result = graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]}, config=config, context=context
    )

    assert "violão" in result["messages"][-1].content.lower()


def test_memory_survives_a_new_graph_instance(tmp_path):
    checkpointer_path = tmp_path / "state.db"
    context = ClinicContext(patient_id="123")
    config = build_config("test-memory-fresh-instance")

    first_graph = build_graph(checkpointer_path=checkpointer_path)
    first_graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_STATEMENT}]}, config=config, context=context
    )

    fresh_graph = build_graph(checkpointer_path=checkpointer_path)
    result = fresh_graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]}, config=config, context=context
    )

    assert "violão" in result["messages"][-1].content.lower()


def test_isolation_between_patients(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")

    graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_STATEMENT}]},
        config=build_config("test-isolation-patient-123"),
        context=ClinicContext(patient_id="123"),
    )
    result = graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]},
        config=build_config("test-isolation-patient-456"),
        context=ClinicContext(patient_id="456"),
    )

    assert "violão" not in result["messages"][-1].content.lower()


def test_isolation_before_and_after_new(tmp_path):
    checkpointer_path = tmp_path / "state.db"
    graph = build_graph(checkpointer_path=checkpointer_path)
    context = ClinicContext(patient_id="123")

    thread_before = resolve_thread_id(checkpointer_path, "123", False)
    graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_STATEMENT}]},
        config=build_config(thread_before),
        context=context,
    )

    thread_after = resolve_thread_id(checkpointer_path, "123", True)
    result = graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]},
        config=build_config(thread_after),
        context=context,
    )

    assert "violão" not in result["messages"][-1].content.lower()


def test_anonymous_chat_uses_ephemeral_memory_not_shared_across_instances():
    graph = build_graph(checkpointer_path=None)
    config = build_config("test-anon-memory")

    graph.invoke({"messages": [{"role": "user", "content": HOBBY_STATEMENT}]}, config=config, context=ANON_CONTEXT)
    result_same_instance = graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]}, config=config, context=ANON_CONTEXT
    )
    assert "violão" in result_same_instance["messages"][-1].content.lower()

    fresh_graph = build_graph(checkpointer_path=None)
    result_fresh_instance = fresh_graph.invoke(
        {"messages": [{"role": "user", "content": HOBBY_QUESTION}]}, config=config, context=ANON_CONTEXT
    )
    assert "violão" not in result_fresh_instance["messages"][-1].content.lower()


def test_transcript_excludes_tool_messages(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    config = build_config("test-transcript-no-tools")
    graph.invoke(
        {"messages": [{"role": "user", "content": "Qual o preparo do exame de sangue?"}]},
        config=config,
        context=ClinicContext(patient_id="123"),
    )

    transcript = graph.get_state(config).values["transcript"]

    assert len(transcript) == 2
    assert all(not isinstance(message, ToolMessage) for message in transcript)


def test_transcript_accumulates_across_turns(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    config = build_config("test-transcript-accumulates")
    context = ClinicContext(patient_id="123")

    graph.invoke({"messages": [{"role": "user", "content": "Quais especialidades vocês atendem?"}]}, config=config, context=context)
    graph.invoke({"messages": [{"role": "user", "content": "Qual o horário de segunda?"}]}, config=config, context=context)

    transcript = graph.get_state(config).values["transcript"]

    assert len(transcript) == 4
    assert transcript[0].type == "human"
    assert transcript[1].type == "ai"
    assert transcript[2].type == "human"
    assert transcript[3].type == "ai"


def test_transcript_records_human_handoff_turn(tmp_path):
    graph = build_graph(checkpointer_path=tmp_path / "state.db")
    config = build_config("test-transcript-handoff")
    graph.invoke(
        {"messages": [{"role": "user", "content": "Estou com uma dor forte no peito agora, o que eu faço?"}]},
        config=config,
        context=ANON_CONTEXT,
    )

    transcript = graph.get_state(config).values["transcript"]

    assert len(transcript) == 2
    assert transcript[0].type == "human"
    assert transcript[1].type == "ai"
    assert "atendimento humano" in transcript[1].content.lower()
