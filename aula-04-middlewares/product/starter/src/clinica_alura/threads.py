import sqlite3
import uuid
from pathlib import Path


def resolve_thread_id(state_db_path: Path, patient_id: str | None, new: bool) -> str:
    """Decide a thread da conversa: sem paciente, sempre uma nova; com paciente, continua a
    thread ativa dele, a menos que `new` peça uma thread nova (que passa a ser a ativa)."""
    if patient_id is None:
        return f"session-{uuid.uuid4()}"

    con = sqlite3.connect(state_db_path)
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS active_threads "
            "(patient_id TEXT PRIMARY KEY, thread_id TEXT NOT NULL)"
        )
        if not new:
            row = con.execute(
                "SELECT thread_id FROM active_threads WHERE patient_id = ?", (patient_id,)
            ).fetchone()
            if row:
                return row[0]

        thread_id = f"patient-{patient_id}-{uuid.uuid4()}"
        con.execute(
            "INSERT INTO active_threads (patient_id, thread_id) VALUES (?, ?) "
            "ON CONFLICT(patient_id) DO UPDATE SET thread_id = excluded.thread_id",
            (patient_id, thread_id),
        )
        con.commit()
        return thread_id
    finally:
        con.close()
