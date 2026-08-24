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
    # TODO: monte um ChatOpenAI a partir do config.yaml, aplique with_structured_output(IntentClassification)
    # e classifique a última mensagem do paciente (junto com CLASSIFIER_INSTRUCTION), devolvendo {"intent": ...}
    raise NotImplementedError


def route_by_intent(state: TriageState) -> str:
    # TODO: devolva o valor de state["intent"], para o add_conditional_edges rotear por ele
    raise NotImplementedError


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
    builder.add_edge("assistant", END)
    builder.add_edge("human_handoff", END)

    # TODO: adicione a aresta condicional a partir de "classify", usando route_by_intent como função de
    # roteamento e mapeando "informação"/"agendamento" para "assistant" e "urgência" para "human_handoff"
    raise NotImplementedError

    return builder.compile()
