from clinica_alura.db import query


def authenticate(patient_id: str, password: str) -> bool:
    """Confere a senha do paciente contra o cadastro. Sem cadastro ou senha errada, nega."""
    rows = query("SELECT password FROM patients WHERE id = ?", (patient_id,))
    if not rows:
        return False
    return rows[0]["password"] == password
