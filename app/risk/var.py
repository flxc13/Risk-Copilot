import numpy as np


def historical_var(returns: list[float], confidence: float = 0.95) -> float:
    if not returns:
        raise ValueError("returns cannot be empty")
    percentile = (1 - confidence) * 100
    return float(np.percentile(returns, percentile))
