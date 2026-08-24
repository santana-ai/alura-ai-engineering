import sqlite3

from clinica_alura.paths import PROJECT_ROOT

CLINIC_DB = PROJECT_ROOT / "data" / "clinic.db"


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Consulta o banco da clínica e devolve as linhas como dicionários."""
    con = sqlite3.connect(CLINIC_DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(sql, params).fetchall()]
    finally:
        con.close()
