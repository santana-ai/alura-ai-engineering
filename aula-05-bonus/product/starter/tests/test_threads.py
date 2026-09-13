from clinica_alura.threads import resolve_thread_id


def test_resolve_thread_id_without_patient_always_new(tmp_path):
    state_db = tmp_path / "state.db"
    first = resolve_thread_id(state_db, None, False)
    second = resolve_thread_id(state_db, None, False)
    assert first != second


def test_resolve_thread_id_continues_active_thread(tmp_path):
    state_db = tmp_path / "state.db"
    first = resolve_thread_id(state_db, "123", False)
    second = resolve_thread_id(state_db, "123", False)
    assert first == second


def test_resolve_thread_id_new_moves_active_thread_forward(tmp_path):
    state_db = tmp_path / "state.db"
    original = resolve_thread_id(state_db, "123", False)

    opened = resolve_thread_id(state_db, "123", True)
    assert opened != original

    after = resolve_thread_id(state_db, "123", False)
    assert after == opened
    assert after != original
