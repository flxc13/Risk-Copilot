def gross_exposure(weights: list[float]) -> float:
    return float(sum(abs(w) for w in weights))
