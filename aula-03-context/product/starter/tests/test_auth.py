from clinica_alura.auth import authenticate


def test_authenticate_correct_password():
    assert authenticate("123", "alura123") is True


def test_authenticate_wrong_password():
    assert authenticate("123", "senha-errada") is False


def test_authenticate_unknown_patient():
    assert authenticate("000", "qualquer") is False
