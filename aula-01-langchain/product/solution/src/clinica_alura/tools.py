from langchain.tools import tool

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


TOOLS = [find_available_slots, get_clinic_hours, list_specialties, estimate_consultation_price]
