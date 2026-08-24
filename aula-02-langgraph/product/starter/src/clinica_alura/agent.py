from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from clinica_alura.config import load_config
from clinica_alura.tools import TOOLS


def build_agent():
    config = load_config()
    model = ChatOpenAI(model=config["model"]["name"], temperature=config["model"]["temperature"])
    return create_agent(model=model, tools=TOOLS, system_prompt=config["agent"]["system_prompt"])
