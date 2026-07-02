from app.risk.engine import compute_var


def run_risk_snapshot(returns: list[float]) -> float:
    return compute_var(returns)
