from app.risk.engine import compute_var


def test_compute_var_returns_float() -> None:
    value = compute_var([0.01, -0.02, 0.005, -0.01, 0.003])
    assert isinstance(value, float)
