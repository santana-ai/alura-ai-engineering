from clinica_alura.tools import (
    estimate_consultation_price,
    find_available_slots,
    get_clinic_hours,
    list_specialties,
)


def test_find_available_slots():
    result = find_available_slots.invoke({"specialty": "cardiologia", "date": "2026-07-20"})
    assert "09:00" in result
    assert "10:30" in result


def test_find_available_slots_unknown_specialty():
    result = find_available_slots.invoke({"specialty": "neurologia", "date": "2026-07-20"})
    assert "nenhum" in result


def test_get_clinic_hours():
    result = get_clinic_hours.invoke({"day_of_week": "segunda"})
    assert "08:00 às 18:00" in result


def test_get_clinic_hours_unknown_day():
    result = get_clinic_hours.invoke({"day_of_week": "feriado"})
    assert "dia não reconhecido" in result


def test_list_specialties():
    result = list_specialties.invoke({})
    assert "cardiologia" in result
    assert "dermatologia" in result


def test_estimate_consultation_price():
    result = estimate_consultation_price.invoke({"specialty": "dermatologia"})
    assert "280" in result


def test_estimate_consultation_price_unknown_specialty():
    result = estimate_consultation_price.invoke({"specialty": "neurologia"})
    assert "Sem preço cadastrado" in result
