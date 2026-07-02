from app.risk.var import historical_var


def compute_var(returns: list[float]) -> float:
    return historical_var(returns)
