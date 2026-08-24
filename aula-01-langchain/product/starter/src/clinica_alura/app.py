import click
from dotenv import load_dotenv
from langchain.messages import HumanMessage

from clinica_alura.agent import build_agent
from clinica_alura.utils import Spinner

load_dotenv()


@click.group()
def app():
    """CLI do Assistente da Clínica Alura."""


@app.command()
@click.option("-m", "--message", required=True, help="Mensagem do paciente.")
def chat(message):
    """Conversa com o assistente da Clínica Alura."""
    agent = build_agent()
    with Spinner("Pensando"):
        response = agent.invoke({"messages": [HumanMessage(message)]})
    click.echo(response["messages"][-1].content)
