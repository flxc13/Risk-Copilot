from __future__ import annotations

from collections.abc import Mapping


def assess_limits(
    historical_var_95: float,
    exposures_by_ticker: Mapping[str, float],
    max_var: float = 0.03,
    max_single_name_weight: float = 0.35,
) -> list[str]:
    warnings: list[str] = []
    if historical_var_95 > max_var:
        warnings.append(
            f"Historical VaR of {historical_var_95:.1%} is above the configured threshold of {max_var:.1%}."
        )

    overweight_names = [
        f"{ticker} ({weight:.1%})"
        for ticker, weight in exposures_by_ticker.items()
        if weight > max_single_name_weight
    ]
    if overweight_names:
        warnings.append(
            "Single-name concentration exceeds limit for " + ", ".join(overweight_names) + "."
        )

    return warnings
