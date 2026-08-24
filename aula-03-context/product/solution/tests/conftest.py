import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from clinica_alura.db import CLINIC_DB

load_dotenv()

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "data" / "schema.sql"


def pytest_configure(config):
    CLINIC_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(CLINIC_DB)
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()
