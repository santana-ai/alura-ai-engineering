from langchain.tools import ToolRuntime, tool

from clinica_alura.context import ClinicContext
from clinica_alura.db import execute, query

SCHEDULE = {"cardiologia": ["09:00", "10:30"], "dermatologia": ["14:00"]}
HOURS = {
    "segunda": "08:00 às 18:00",
    "terça": "08:00 às 18:00",
    "quarta": "08:00 às 18:00",
    "quinta": "08:00 às 18:00",
    "sexta": "08:00 às 17:00",
    "sábado": "08:00 às 12:00",
    "domingo": "fechado",
}
SPECIALTIES = ["cardiologia", "dermatologia", "clínica geral"]
PRICES = {"cardiologia": 350, "dermatologia": 280, "clínica geral": 200}


@tool
def find_available_slots(specialty: str, date: str) -> str:
    """Horários livres na agenda da Clínica Alura para a especialidade e data (YYYY-MM-DD)."""
    slots = SCHEDULE.get(specialty.lower(), [])
    return f"Horários para {specialty} em {date}: {', '.join(slots) or 'nenhum'}"


@tool
def get_clinic_hours(day_of_week: str) -> str:
    """Horário de atendimento da Clínica Alura no dia da semana informado, em português (ex.: 'segunda')."""
    return f"Atendimento às {day_of_week}: {HOURS.get(day_of_week.lower(), 'dia não reconhecido')}"


@tool
def list_specialties() -> str:
    """Lista as especialidades médicas atendidas pela Clínica Alura."""
    return f"Especialidades atendidas: {', '.join(SPECIALTIES)}"


@tool
def estimate_consultation_price(specialty: str) -> str:
    """Preço estimado da consulta particular por especialidade na Clínica Alura."""
    price = PRICES.get(specialty.lower())
    return f"Consulta de {specialty}: R$ {price}" if price else f"Sem preço cadastrado para {specialty}."


@tool
def get_patient_record(patient_id: str | None = None, *, runtime: ToolRuntime[ClinicContext]) -> str:
    """Consulta o cadastro de um paciente. Sem patient_id, usa o paciente da conversa atual."""
    target_id = patient_id or runtime.context.patient_id
    if target_id is None:
        return "Nenhum paciente identificado nesta conversa."
    rows = query("SELECT name, insurance FROM patients WHERE id = ?", (target_id,))
    if not rows:
        return "Paciente não encontrado."
    return f"{rows[0]['name']}, convênio: {rows[0]['insurance']}."


@tool
def lookup_policy(topic: str) -> str:
    """Consulta as políticas da Clínica Alura por tema (ex.: 'convênio', 'exame de sangue')."""
    rows = query("SELECT text FROM policies WHERE topic LIKE ?", (f"%{topic}%",))
    return "\n".join(row["text"] for row in rows) or "Nenhuma política encontrada para esse tema."


@tool
def book_appointment(specialty: str, date: str, time: str, runtime: ToolRuntime[ClinicContext]) -> str:
    """Confirma o agendamento de uma consulta na Clínica Alura para uma especialidade, data e horário."""
    execute(
        "INSERT INTO appointments (patient_id, specialty, date, time) VALUES (?, ?, ?, ?)",
        (runtime.context.patient_id, specialty, date, time),
    )
    return f"Consulta de {specialty} agendada para {date} às {time}."


TOOLS = [
    find_available_slots,
    get_clinic_hours,
    list_specialties,
    estimate_consultation_price,
    get_patient_record,
    lookup_policy,
    book_appointment,
]
