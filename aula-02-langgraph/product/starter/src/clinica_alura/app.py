import click
from dotenv import load_dotenv
from langchain.messages import HumanMessage

from clinica_alura.graph import build_graph
from clinica_alura.utils import Spinner

load_dotenv()


@click.group()
def app():
    """CLI do Assistente da Clínica Alura."""


@app.command()
@click.option("-m", "--message", default=None, help="Mensagem única, sem manter a conversa aberta.")
def chat(message):
    """Conversa com o assistente da Clínica Alura."""
    graph = build_graph()

    if message is not None:
        with Spinner("Pensando"):
            result = graph.invoke({"messages": [HumanMessage(message)]})
        click.echo(result["messages"][-1].content)
        return

    click.echo("Conversa aberta. Digite 'sair' para encerrar.")
    history = []
    while True:
        try:
            message = input("Você: ")
        except (EOFError, KeyboardInterrupt):
            break
        if message.strip().lower() in {"sair", "exit"}:
            break
        with Spinner("Pensando"):
            result = graph.invoke({"messages": history + [HumanMessage(message)]})
        click.echo(result["messages"][-1].content)
        history = result["messages"]
