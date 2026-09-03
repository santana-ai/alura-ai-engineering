import click
from dotenv import load_dotenv
from langchain.messages import AnyMessage, HumanMessage
from langgraph.types import Command

from clinica_alura.auth import authenticate
from clinica_alura.config import load_config
from clinica_alura.context import ClinicContext
from clinica_alura.graph import build_graph
from clinica_alura.paths import PROJECT_ROOT
from clinica_alura.threads import resolve_thread_id
from clinica_alura.utils import Spinner

load_dotenv()

DEFAULT_STATE_DB = PROJECT_ROOT / "state.db"
DEFAULT_HISTORY_TURNS = 2


def format_history(transcript: list[AnyMessage], mode: str) -> str:
    """Formata as mensagens de uma conversa pra exibição, 'short' (últimos turnos) ou 'all' (tudo)."""
    if not transcript:
        return "Nenhuma conversa registrada ainda."
    messages = transcript if mode == "all" else transcript[-(DEFAULT_HISTORY_TURNS * 2) :]
    return "\n".join(
        f"{'Você' if message.type == 'human' else 'Assistente'}: {message.content}" for message in messages
    )


def describe_pending_approval(result: dict) -> str:
    """Descrição da ação pendente de aprovação num resultado que pausou (`__interrupt__` presente)."""
    action = result["__interrupt__"][0].value["action_requests"][0]
    return action["description"]


@click.group()
def app():
    """CLI do Assistente da Clínica Alura."""


@app.command()
@click.option("-m", "--message", default=None, help="Mensagem única, sem manter a conversa aberta.")
@click.option("--patient", default=None, help="Identificação do paciente.")
@click.option("--password", default=None, help="Senha do paciente.")
@click.option("--new", is_flag=True, help="Abre uma conversa nova, isolada da conversa atual do paciente.")
@click.option(
    "--history",
    "history_mode",
    is_flag=False,
    flag_value="short",
    default=None,
    type=click.Choice(["short", "all"]),
    help="Mostra as últimas mensagens da conversa e sai. 'all' mostra a conversa inteira.",
)
@click.option(
    "--approve",
    default=None,
    type=click.Choice(["approve", "reject"]),
    help="Resolve uma aprovação pendente (ex.: agendamento que exige aprovação humana).",
)
def chat(message, patient, password, new, history_mode, approve):
    """Conversa com o assistente da Clínica Alura."""
    if history_mode is not None and message is not None:
        raise click.UsageError("--history não pode ser usado com -m.")
    if history_mode is not None and patient is None:
        raise click.UsageError("--history exige --patient.")

    if patient is not None and not authenticate(patient, password or ""):
        click.echo("Paciente ou senha inválidos.")
        return

    app_config = load_config()
    context = ClinicContext(patient_id=patient)
    thread_id = resolve_thread_id(DEFAULT_STATE_DB, patient, new)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "assistant": app_config["assistant"],
            "classifier": app_config["classifier"],
        }
    }
    checkpointer_path = DEFAULT_STATE_DB if patient is not None else None
    graph = build_graph(checkpointer_path=checkpointer_path)

    if history_mode is not None:
        state = graph.get_state(config)
        click.echo(format_history(state.values.get("transcript", []), history_mode))
        return

    if approve is not None and message is None:
        if not graph.get_state(config).next:
            click.echo("Não há nenhuma aprovação pendente nesta conversa.")
            return
        with Spinner("Pensando"):
            result = graph.invoke(Command(resume={"decisions": [{"type": approve}]}), config=config, context=context)
        click.echo(result["messages"][-1].content)
        return

    if message is not None:
        with Spinner("Pensando"):
            result = graph.invoke({"messages": [HumanMessage(message)]}, config=config, context=context)
        if result.get("__interrupt__"):
            if approve is None:
                click.echo(describe_pending_approval(result))
                click.echo("Rode de novo com --approve approve|reject pra continuar.")
                return
            with Spinner("Pensando"):
                result = graph.invoke(
                    Command(resume={"decisions": [{"type": approve}]}), config=config, context=context
                )
        click.echo(result["messages"][-1].content)
        return

    click.echo("Conversa aberta. Digite 'sair' para encerrar.")
    while True:
        try:
            message = input("Você: ")
        except (EOFError, KeyboardInterrupt):
            break
        if message.strip().lower() in {"sair", "exit"}:
            break
        with Spinner("Pensando"):
            result = graph.invoke({"messages": [HumanMessage(message)]}, config=config, context=context)
        if result.get("__interrupt__"):
            click.echo(describe_pending_approval(result))
            decision = input("Aprovar ou rejeitar? [approve/reject]: ").strip().lower()
            while decision not in {"approve", "reject"}:
                decision = input("Resposta inválida. Digite 'approve' ou 'reject': ").strip().lower()
            with Spinner("Pensando"):
                result = graph.invoke(
                    Command(resume={"decisions": [{"type": decision}]}), config=config, context=context
                )
        click.echo(result["messages"][-1].content)
