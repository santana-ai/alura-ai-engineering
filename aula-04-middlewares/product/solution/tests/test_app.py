from langchain.messages import AIMessage, HumanMessage

from clinica_alura.app import format_history


def test_format_history_empty():
    assert format_history([], "short") == "Nenhuma conversa registrada ainda."


def test_format_history_short_shows_last_two_turns():
    transcript = [
        HumanMessage("pergunta 1"),
        AIMessage("resposta 1"),
        HumanMessage("pergunta 2"),
        AIMessage("resposta 2"),
        HumanMessage("pergunta 3"),
        AIMessage("resposta 3"),
    ]

    result = format_history(transcript, "short")

    assert "pergunta 3" in result
    assert "resposta 3" in result
    assert "pergunta 2" in result
    assert "resposta 2" in result
    assert "pergunta 1" not in result
    assert "resposta 1" not in result


def test_format_history_all_shows_everything():
    transcript = [
        HumanMessage("pergunta 1"),
        AIMessage("resposta 1"),
        HumanMessage("pergunta 2"),
        AIMessage("resposta 2"),
    ]

    result = format_history(transcript, "all")

    assert "pergunta 1" in result
    assert "pergunta 2" in result
