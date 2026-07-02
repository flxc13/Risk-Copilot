from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.risk.exposure import top_holdings


def build_driver_summary(
    holdings: Sequence[Mapping[str, float | str]],
    latest_prices: Mapping[str, float],
    limit: int = 5,
) -> list[str]:
    summary = []
    for row in top_holdings(holdings, latest_prices, limit=limit):
        weight = float(row["weight"])
        summary.append(
            f"{row['ticker']} contributes {weight:.1%} of portfolio value across {row['asset_class']}."
        )
    return summary
