import sqlite3
from pathlib import Path

import pytest
from dotenv import load_dotenv

from clinica_alura import db

load_dotenv()

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "data" / "schema.sql"


@pytest.fixture(autouse=True, scope="session")
def test_clinic_db(tmp_path_factory):
    """Isola a suíte do `data/clinic.db` real: cria um banco de teste à parte, do mesmo schema,
    e redireciona `db.CLINIC_DB` pra ele, pra rodar a suíte nunca gravar agendamentos de teste
    no banco de demonstração que o produto ship."""
    test_db_path = tmp_path_factory.mktemp("clinic") / "clinic.db"
    con = sqlite3.connect(test_db_path)
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()
    db.CLINIC_DB = test_db_path
