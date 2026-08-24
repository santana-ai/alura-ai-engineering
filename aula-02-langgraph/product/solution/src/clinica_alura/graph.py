import operator
from typing import Annotated, Literal

from pydantic import BaseModel
from langchain.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

from clinica_alura.agent import build_agent
from clinica_alura.config import load_config

URGENCY_KEYWORDS = ["peito", "sangra", "desmai", "convuls", "falta de ar"]

CLASSIFIER_INSTRUCTION = SystemMessage(
    "Classifique a mensagem do paciente da Clínica Alura em: informação, agendamento ou urgência."
)

HUMAN_HANDOFF_TEMPLATE = "Isso parece urgente. Estou te encaminhando para atendimento humano agora.\n\n{notes}"


class TriageState(MessagesState):
    intent: str
    notes: Annotated[list[str], operator.add]


class IntentClassification(BaseModel):
    intent: Literal["informação", "agendamento", "urgência"]


def log_reception(state: TriageState) -> dict:
    return {"notes": ["Recepção: nova mensagem recebida do paciente."]}


def check_urgency_flags(state: TriageState) -> dict:
    message = state["messages"][-1].content.lower()
    flagged = any(keyword in message for keyword in URGENCY_KEYWORDS)
    note = (
        "Triagem automática: sinais de urgência detectados."
        if flagged
        else "Triagem automática: sem sinais de urgência."
    )
    return {"notes": [note]}


def classify(state: TriageState) -> dict:
    config = load_config()
    model = ChatOpenAI(model=config["model"]["name"], temperature=config["model"]["temperature"])
    classifier = model.with_structured_output(IntentClassification)
    result = classifier.invoke([CLASSIFIER_INSTRUCTION, state["messages"][-1]])
    return {"intent": result.intent}


def route_by_intent(state: TriageState) -> str:
    return state["intent"]


def assistant(state: TriageState) -> dict:
    agent = build_agent()
    result = agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}


def human_handoff(state: TriageState) -> dict:
    # ordem de escrita dos nós paralelos não é garantida, por isso a ordenação explícita
    notes = sorted(state["notes"], key=lambda note: 0 if note.startswith("Recepção") else 1)
    return {"messages": [AIMessage(HUMAN_HANDOFF_TEMPLATE.format(notes="\n".join(notes)))]}


def build_graph():
    builder = StateGraph(TriageState)
    builder.add_node("log_reception", log_reception)
    builder.add_node("check_urgency_flags", check_urgency_flags)
    builder.add_node("classify", classify)
    builder.add_node("assistant", assistant)
    builder.add_node("human_handoff", human_handoff)

    builder.add_edge(START, "log_reception")
    builder.add_edge(START, "check_urgency_flags")
    builder.add_edge("log_reception", "classify")
    builder.add_edge("check_urgency_flags", "classify")
    builder.add_conditional_edges(
        source="classify",
        path=route_by_intent,
        path_map={"informação": "assistant", "agendamento": "assistant", "urgência": "human_handoff"},
    )
    builder.add_edge("assistant", END)
    builder.add_edge("human_handoff", END)

    return builder.compile()
