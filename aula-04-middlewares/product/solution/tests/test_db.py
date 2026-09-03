from clinica_alura.db import query


def test_query_patient_by_id():
    rows = query("SELECT name FROM patients WHERE id = ?", ("123",))
    assert rows[0]["name"] == "Ana Souza"


def test_query_unknown_patient():
    rows = query("SELECT name FROM patients WHERE id = ?", ("000",))
    assert rows == []


def test_query_policy_by_topic():
    rows = query("SELECT text FROM policies WHERE topic LIKE ?", ("%exame de sangue%",))
    assert "jejum" in rows[0]["text"]
