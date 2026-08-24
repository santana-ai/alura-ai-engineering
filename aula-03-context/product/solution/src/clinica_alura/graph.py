import operator
import sqlite3
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime

from clinica_alura.context import ClinicContext
from clinica_alura.tools import TOOLS


class TriageState(MessagesState):
    intent: str
    notes: Annotated[list[str], operator.add]
    transcript: Annotated[list[AnyMessage], operator.add]


def log_reception(state: TriageState) -> dict:
    return {"notes": ["Recepção: nova mensagem recebida do paciente."]}


def check_urgency_flags(state: TriageState, config: RunnableConfig) -> dict:
    message = state["messages"][-1].content.lower()
    keywords = config["configurable"]["classifier"]["urgency_keywords"]
    flagged = any(keyword in message for keyword in keywords)
    note = (
        "Triagem automática: sinais de urgência detectados."
        if flagged
        else "Triagem automática: sem sinais de urgência."
    )
    return {"notes": [note]}


class IntentClassification(BaseModel):
    intent: Literal["informação", "agendamento", "urgência"]


def classify(state: TriageState, config: RunnableConfig) -> dict:
    classifier_config = config["configurable"]["classifier"]
    model = ChatOpenAI(
        model=classifier_config["model"]["name"],
        temperature=classifier_config["model"]["temperature"],
    )
    classifier = model.with_structured_output(IntentClassification)
    system_message = SystemMessage(classifier_config["system_prompt"])
    result = classifier.invoke([system_message, state["messages"][-1]])
    return {"intent": result.intent}


def route_by_intent(state: TriageState) -> str:
    return state["intent"]


def assistant(state: TriageState, config: RunnableConfig, runtime: Runtime[ClinicContext]) -> dict:
    assistant_config = config["configurable"]["assistant"]
    model = ChatOpenAI(
        model=assistant_config["model"]["name"],
        temperature=assistant_config["model"]["temperature"],
    )
    agent = create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=assistant_config["system_prompt"],
        context_schema=ClinicContext,
    )
    human_message = state["messages"][-1]
    result = agent.invoke({"messages": state["messages"]}, context=runtime.context)
    # o loop do agente só termina numa AIMessage sem tool_calls, então isto é sempre a resposta final
    final_answer = result["messages"][-1]
    return {"messages": result["messages"], "transcript": [human_message, final_answer]}


def human_handoff(state: TriageState) -> dict:
    # ordem de escrita dos nós paralelos não é garantida, por isso a ordenação explícita
    notes = sorted(state["notes"], key=lambda note: 0 if note.startswith("Recepção") else 1)
    human_message = state["messages"][-1]
    template = PromptTemplate.from_template(
        "Isso parece urgente. Estou te encaminhando para atendimento humano agora.\n\n{notes}"
    )
    reply = AIMessage(template.format(notes="\n".join(notes)))
    return {"messages": [reply], "transcript": [human_message, reply]}


def build_graph(checkpointer_path: Path | None = None):
    builder = StateGraph(TriageState, context_schema=ClinicContext)
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

    if checkpointer_path is None:
        checkpointer = InMemorySaver()
    else:
        checkpointer = SqliteSaver(sqlite3.connect(checkpointer_path, check_same_thread=False))
    return builder.compile(checkpointer=checkpointer)
