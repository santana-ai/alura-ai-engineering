from dataclasses import dataclass


@dataclass
class ClinicContext:
    """Contexto de runtime da conversa: quem é o paciente, quando identificado."""

    patient_id: str | None = None
