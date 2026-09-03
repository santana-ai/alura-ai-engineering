from unittest.mock import MagicMock

from clinica_alura.context import ClinicContext
from clinica_alura.guardrails import PatientAccessGuardrail, detect_cpf, is_valid_cpf, needs_approval


def test_patient_access_guardrail_blocks_cross_patient_id():
    request = MagicMock()
    request.tool_call = {"name": "get_patient_record", "args": {"patient_id": "456"}, "id": "call-1"}
    request.runtime = MagicMock(context=ClinicContext(patient_id="123"))
    handler = MagicMock()

    result = PatientAccessGuardrail().wrap_tool_call(request, handler)

    handler.assert_not_called()
    assert "cross_patient_access" in result.content


def test_patient_access_guardrail_allows_own_patient_id():
    request = MagicMock()
    request.tool_call = {"name": "get_patient_record", "args": {"patient_id": "123"}, "id": "call-1"}
    request.runtime = MagicMock(context=ClinicContext(patient_id="123"))
    handler = MagicMock(return_value="ok")

    result = PatientAccessGuardrail().wrap_tool_call(request, handler)

    handler.assert_called_once_with(request)
    assert result == "ok"


def test_is_valid_cpf_accepts_valid_checksum():
    assert is_valid_cpf("12345678909")


def test_is_valid_cpf_rejects_invalid_checksum():
    assert not is_valid_cpf("12345678900")


def test_detect_cpf_finds_valid_cpf_in_text():
    matches = detect_cpf("Meu CPF é 123.456.789-09, pode confirmar?")
    assert matches[0]["text"] == "123.456.789-09"


def test_needs_approval_true_for_cardiologia():
    request = MagicMock()
    request.tool_call = {"args": {"specialty": "cardiologia"}}
    assert needs_approval(request)


def test_needs_approval_false_for_other_specialties():
    request = MagicMock()
    request.tool_call = {"args": {"specialty": "dermatologia"}}
    assert not needs_approval(request)
