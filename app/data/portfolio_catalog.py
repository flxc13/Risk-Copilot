from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PortfolioDefinition:
    portfolio_id: str
    portfolio_name: str
    strategy_style: str
    objective: str
    benchmark_ticker: str
    basel_stress_window_id: str
    basel_stress_window_ids: tuple[str, ...]
    basel_stress_methodology: str
    risk_budget: str
    target_net_exposure: str
    target_gross_exposure: str
    pm_desk: str
    holdings: tuple[dict[str, float | str], ...]


PORTFOLIO_CATALOG: dict[str, PortfolioDefinition] = {
    "core_long_equity": PortfolioDefinition(
        portfolio_id="core_long_equity",
        portfolio_name="TMT Long/Short Alpha",
        strategy_style="Equity long/short / technology, media, telecom",
        objective="Run a liquid TMT alpha book with concentrated compounder longs, index hedges, and controlled beta to growth equities.",
        benchmark_ticker="QQQ",
        basel_stress_window_id="growth_2022",
        basel_stress_window_ids=("growth_2022", "covid_2020_12m", "rates_2022"),
        basel_stress_methodology="Approved equity-growth candidate stress set; current positions are revalued on each approved regime and the conservative calibration window is selected for sVaR.",
        risk_budget="1.25% daily VaR target, 8% max drawdown soft stop",
        target_net_exposure="55% to 70% net long",
        target_gross_exposure="130% to 170% gross using listed ETFs for hedges",
        pm_desk="Equity L/S - TMT",
        holdings=(
            {"ticker": "MSFT", "quantity": 72, "average_cost": 330.0, "asset_class": "Single Name Equity", "sector": "Software", "region": "US", "position_type": "Core long", "liquidity_bucket": "T+1", "risk_bucket": "Quality growth", "thesis": "Durable cloud and AI infrastructure compounder."},
            {"ticker": "GOOGL", "quantity": 58, "average_cost": 138.0, "asset_class": "Single Name Equity", "sector": "Internet", "region": "US", "position_type": "Core long", "liquidity_bucket": "T+1", "risk_bucket": "Advertising / AI", "thesis": "Search cash flows plus optionality in AI products."},
            {"ticker": "META", "quantity": 38, "average_cost": 360.0, "asset_class": "Single Name Equity", "sector": "Internet", "region": "US", "position_type": "Core long", "liquidity_bucket": "T+1", "risk_bucket": "Digital advertising", "thesis": "Operating leverage and capital return support upside."},
            {"ticker": "NVDA", "quantity": 26, "average_cost": 420.0, "asset_class": "Single Name Equity", "sector": "Semiconductors", "region": "US", "position_type": "Tactical long", "liquidity_bucket": "T+1", "risk_bucket": "AI beta", "thesis": "Data-center demand, sized tightly for volatility."},
            {"ticker": "AVGO", "quantity": 12, "average_cost": 860.0, "asset_class": "Single Name Equity", "sector": "Semiconductors", "region": "US", "position_type": "Core long", "liquidity_bucket": "T+1", "risk_bucket": "Infrastructure semis", "thesis": "Diversified semiconductor and software cash flows."},
            {"ticker": "QQQ", "quantity": 30, "average_cost": 390.0, "asset_class": "Index ETF", "sector": "Growth benchmark", "region": "US", "position_type": "Beta sleeve", "liquidity_bucket": "T+0", "risk_bucket": "Nasdaq beta", "thesis": "Liquid beta expression for tactical scaling."},
            {"ticker": "PSQ", "quantity": 210, "average_cost": 11.0, "asset_class": "Inverse ETF", "sector": "Index hedge", "region": "US", "position_type": "Short hedge proxy", "liquidity_bucket": "T+0", "risk_bucket": "Nasdaq hedge", "thesis": "Listed ETF hedge proxy for growth drawdown protection."},
            {"ticker": "SH", "quantity": 160, "average_cost": 13.0, "asset_class": "Inverse ETF", "sector": "Index hedge", "region": "US", "position_type": "Short hedge proxy", "liquidity_bucket": "T+0", "risk_bucket": "S&P hedge", "thesis": "Broad equity market hedge overlay."},
            {"ticker": "CASH", "quantity": 85000.0, "average_cost": 1.0, "asset_class": "Cash", "sector": "Liquidity", "region": "US", "position_type": "Cash buffer", "liquidity_bucket": "Same day", "risk_bucket": "Liquidity", "thesis": "Dry powder and variation margin buffer."},
        ),
    ),
    "defensive_income": PortfolioDefinition(
        portfolio_id="defensive_income",
        portfolio_name="Multi-Asset Defensive Carry",
        strategy_style="Cross-asset income / defensive carry",
        objective="Generate lower-volatility carry using bonds, credit, healthcare, gold, and explicit equity hedges for drawdown control.",
        benchmark_ticker="TLT",
        basel_stress_window_id="rates_2022",
        basel_stress_window_ids=("rates_2022", "covid_2020_12m"),
        basel_stress_methodology="Approved rates and liquidity candidate stress set for duration, credit-spread, defensive equity, and real-asset carry exposures.",
        risk_budget="0.75% daily VaR target, 5% drawdown review level",
        target_net_exposure="20% to 40% net risk exposure",
        target_gross_exposure="90% to 125% gross across rates, credit, equity defensives, and hedges",
        pm_desk="Macro Credit - Defensive Carry",
        holdings=(
            {"ticker": "TLT", "quantity": 420, "average_cost": 92.0, "asset_class": "Rates ETF", "sector": "Treasuries", "region": "US", "position_type": "Duration long", "liquidity_bucket": "T+0", "risk_bucket": "Rates duration", "thesis": "Convexity and recession hedge."},
            {"ticker": "LQD", "quantity": 240, "average_cost": 108.0, "asset_class": "Credit ETF", "sector": "Investment grade credit", "region": "US", "position_type": "Carry long", "liquidity_bucket": "T+0", "risk_bucket": "Credit spread", "thesis": "Higher-quality income sleeve."},
            {"ticker": "HYG", "quantity": 130, "average_cost": 76.0, "asset_class": "Credit ETF", "sector": "High yield credit", "region": "US", "position_type": "Carry long", "liquidity_bucket": "T+0", "risk_bucket": "Credit spread", "thesis": "Limited high-yield allocation for carry."},
            {"ticker": "GLD", "quantity": 145, "average_cost": 185.0, "asset_class": "Commodity ETF", "sector": "Gold", "region": "Global", "position_type": "Diversifier", "liquidity_bucket": "T+0", "risk_bucket": "Real asset", "thesis": "Inflation and policy uncertainty hedge."},
            {"ticker": "XLV", "quantity": 115, "average_cost": 132.0, "asset_class": "Sector ETF", "sector": "Healthcare", "region": "US", "position_type": "Defensive equity", "liquidity_bucket": "T+0", "risk_bucket": "Low beta equity", "thesis": "Stable earnings and defensive equity factor."},
            {"ticker": "SH", "quantity": 260, "average_cost": 13.0, "asset_class": "Inverse ETF", "sector": "Index hedge", "region": "US", "position_type": "Short hedge proxy", "liquidity_bucket": "T+0", "risk_bucket": "Equity hedge", "thesis": "Broad equity drawdown dampener."},
            {"ticker": "CASH", "quantity": 105000.0, "average_cost": 1.0, "asset_class": "Cash", "sector": "Liquidity", "region": "US", "position_type": "Cash buffer", "liquidity_bucket": "Same day", "risk_bucket": "Liquidity", "thesis": "Liquidity reserve for redemptions and margin."},
        ),
    ),
    "tactical_macro": PortfolioDefinition(
        portfolio_id="tactical_macro",
        portfolio_name="Global Macro Regime Rotation",
        strategy_style="Discretionary macro / ETF implementation",
        objective="Express liquid macro views across equity beta, rates duration, energy, USD, gold, and drawdown hedges.",
        benchmark_ticker="SPY",
        basel_stress_window_id="rates_2022",
        basel_stress_window_ids=("rates_2022", "covid_2020_12m", "growth_2022"),
        basel_stress_methodology="Approved macro candidate stress set covering rates repricing, liquidity shock, growth drawdown, dollar, commodity, and beta sleeves.",
        risk_budget="1.00% daily VaR target, 6% drawdown review level",
        target_net_exposure="Flexible, -10% to 65% directional risk",
        target_gross_exposure="100% to 150% gross across liquid ETF sleeves",
        pm_desk="Global Macro - Tactical",
        holdings=(
            {"ticker": "SPY", "quantity": 90, "average_cost": 460.0, "asset_class": "Index ETF", "sector": "US large-cap equity", "region": "US", "position_type": "Risk-on sleeve", "liquidity_bucket": "T+0", "risk_bucket": "Equity beta", "thesis": "Base risk asset exposure when growth remains resilient."},
            {"ticker": "IWM", "quantity": 85, "average_cost": 205.0, "asset_class": "Index ETF", "sector": "US small-cap equity", "region": "US", "position_type": "Cyclical sleeve", "liquidity_bucket": "T+0", "risk_bucket": "Small-cap beta", "thesis": "Cyclical rebound exposure, sized for volatility."},
            {"ticker": "XLE", "quantity": 180, "average_cost": 86.0, "asset_class": "Sector ETF", "sector": "Energy", "region": "US", "position_type": "Inflation hedge", "liquidity_bucket": "T+0", "risk_bucket": "Commodity beta", "thesis": "Energy cash-flow and inflation sensitivity."},
            {"ticker": "TLT", "quantity": 260, "average_cost": 92.0, "asset_class": "Rates ETF", "sector": "Treasuries", "region": "US", "position_type": "Duration hedge", "liquidity_bucket": "T+0", "risk_bucket": "Rates duration", "thesis": "Rates rally hedge against growth shock."},
            {"ticker": "GLD", "quantity": 95, "average_cost": 185.0, "asset_class": "Commodity ETF", "sector": "Gold", "region": "Global", "position_type": "Policy hedge", "liquidity_bucket": "T+0", "risk_bucket": "Real asset", "thesis": "Hedge against real-rate and policy uncertainty."},
            {"ticker": "UUP", "quantity": 430, "average_cost": 28.0, "asset_class": "Currency ETF", "sector": "US dollar", "region": "US", "position_type": "FX long", "liquidity_bucket": "T+0", "risk_bucket": "Dollar factor", "thesis": "Dollar strength during risk-off and rate repricing."},
            {"ticker": "SH", "quantity": 180, "average_cost": 13.0, "asset_class": "Inverse ETF", "sector": "Index hedge", "region": "US", "position_type": "Short hedge proxy", "liquidity_bucket": "T+0", "risk_bucket": "Equity hedge", "thesis": "Liquid hedge overlay for macro shock scenarios."},
            {"ticker": "CASH", "quantity": 70000.0, "average_cost": 1.0, "asset_class": "Cash", "sector": "Liquidity", "region": "US", "position_type": "Cash buffer", "liquidity_bucket": "Same day", "risk_bucket": "Liquidity", "thesis": "Liquidity for tactical redeployment."},
        ),
    ),
    "event_driven_special_sits": PortfolioDefinition(
        portfolio_id="event_driven_special_sits",
        portfolio_name="Event-Driven Special Situations",
        strategy_style="Event-driven / catalyst equity",
        objective="Hold liquid catalyst names around capital return, restructuring, M&A probability, and regulatory event paths with index hedges.",
        benchmark_ticker="SPY",
        basel_stress_window_id="covid_2020_12m",
        basel_stress_window_ids=("covid_2020_12m", "growth_2022", "rates_2022"),
        basel_stress_methodology="Approved catalyst-equity candidate stress set; current holdings are stressed on observed equity-crisis and factor-rotation regimes.",
        risk_budget="1.10% daily VaR target, catalyst gap-risk reviewed weekly",
        target_net_exposure="45% to 60% net long",
        target_gross_exposure="115% to 145% gross using ETF hedge overlays",
        pm_desk="Event Driven - Special Sits",
        holdings=(
            {"ticker": "JPM", "quantity": 95, "average_cost": 172.0, "asset_class": "Single Name Equity", "sector": "Financials", "region": "US", "position_type": "Core long", "liquidity_bucket": "T+1", "risk_bucket": "Capital return", "thesis": "Quality bank compounder with capital return support."},
            {"ticker": "XOM", "quantity": 120, "average_cost": 102.0, "asset_class": "Single Name Equity", "sector": "Energy", "region": "US", "position_type": "Catalyst long", "liquidity_bucket": "T+1", "risk_bucket": "Commodity linked", "thesis": "Free cash flow and shareholder return catalyst."},
            {"ticker": "LLY", "quantity": 22, "average_cost": 560.0, "asset_class": "Single Name Equity", "sector": "Healthcare", "region": "US", "position_type": "Catalyst long", "liquidity_bucket": "T+1", "risk_bucket": "Drug pipeline", "thesis": "Pipeline and obesity franchise momentum."},
            {"ticker": "AMZN", "quantity": 72, "average_cost": 145.0, "asset_class": "Single Name Equity", "sector": "Consumer internet", "region": "US", "position_type": "Restructuring long", "liquidity_bucket": "T+1", "risk_bucket": "Margin expansion", "thesis": "Retail margin recovery and cloud stabilization."},
            {"ticker": "XLF", "quantity": 260, "average_cost": 38.0, "asset_class": "Sector ETF", "sector": "Financials", "region": "US", "position_type": "Sector hedge / beta", "liquidity_bucket": "T+0", "risk_bucket": "Financial beta", "thesis": "Liquid sleeve to manage financial factor exposure."},
            {"ticker": "SH", "quantity": 220, "average_cost": 13.0, "asset_class": "Inverse ETF", "sector": "Index hedge", "region": "US", "position_type": "Short hedge proxy", "liquidity_bucket": "T+0", "risk_bucket": "Market hedge", "thesis": "Market hedge to isolate catalyst idiosyncratic exposure."},
            {"ticker": "CASH", "quantity": 90000.0, "average_cost": 1.0, "asset_class": "Cash", "sector": "Liquidity", "region": "US", "position_type": "Cash buffer", "liquidity_bucket": "Same day", "risk_bucket": "Liquidity", "thesis": "Cash for event slippage, borrow, and redeployment."},
        ),
    ),
    "high_octane_trading": PortfolioDefinition(
        portfolio_id="high_octane_trading",
        portfolio_name="High-Octane Levered Trading Book",
        strategy_style="Concentrated levered beta / crypto / volatility trading",
        objective="Demonstrate a stressed internal-model capital case with concentrated levered ETFs, crypto beta, and volatility exposure.",
        benchmark_ticker="QQQ",
        basel_stress_window_id="growth_2022",
        basel_stress_window_ids=("growth_2022", "covid_2020_12m", "rates_2022"),
        basel_stress_methodology="Approved high-beta equity, crypto-proxy, and volatility candidate stress set; short-history and levered instruments use governed proxy transformations from observed market histories.",
        risk_budget="Breach-demo profile: VaR, drawdown, concentration, and capital intensity intentionally elevated",
        target_net_exposure="Aggressive directional risk, 90%+ net long equivalent",
        target_gross_exposure="250%+ gross economic beta through levered ETFs and high-volatility assets",
        pm_desk="Demo Desk - High Risk Capital Case",
        holdings=(
            {"ticker": "TQQQ", "quantity": 1900, "average_cost": 62.0, "asset_class": "Levered ETF", "sector": "Nasdaq 100 3x", "region": "US", "position_type": "Levered long", "liquidity_bucket": "T+0", "risk_bucket": "Levered growth beta", "thesis": "High-convexity growth beta sleeve for capital charge demonstration."},
            {"ticker": "SOXL", "quantity": 1700, "average_cost": 41.0, "asset_class": "Levered ETF", "sector": "Semiconductors 3x", "region": "US", "position_type": "Levered long", "liquidity_bucket": "T+0", "risk_bucket": "Levered semiconductor beta", "thesis": "Concentrated high-volatility semiconductor exposure."},
            {"ticker": "COIN", "quantity": 430, "average_cost": 225.0, "asset_class": "Single Name Equity", "sector": "Crypto infrastructure", "region": "US", "position_type": "High beta long", "liquidity_bucket": "T+1", "risk_bucket": "Crypto equity beta", "thesis": "Crypto-linked equity exposure with large gap-risk potential."},
            {"ticker": "BITO", "quantity": 2300, "average_cost": 28.0, "asset_class": "Crypto ETF", "sector": "Bitcoin futures", "region": "US", "position_type": "Crypto beta long", "liquidity_bucket": "T+0", "risk_bucket": "Digital asset beta", "thesis": "Liquid listed crypto futures beta for stress demonstration."},
            {"ticker": "ARKK", "quantity": 1200, "average_cost": 48.0, "asset_class": "Thematic ETF", "sector": "Disruptive growth", "region": "US", "position_type": "Speculative growth long", "liquidity_bucket": "T+0", "risk_bucket": "Unprofitable growth beta", "thesis": "Long-duration growth factor exposure."},
            {"ticker": "UVXY", "quantity": 900, "average_cost": 24.0, "asset_class": "Volatility ETF", "sector": "VIX futures", "region": "US", "position_type": "Volatility overlay", "liquidity_bucket": "T+0", "risk_bucket": "Volatility convexity", "thesis": "Volatility-linked instrument that increases portfolio path instability."},
            {"ticker": "CASH", "quantity": 15000.0, "average_cost": 1.0, "asset_class": "Cash", "sector": "Liquidity", "region": "US", "position_type": "Minimal cash buffer", "liquidity_bucket": "Same day", "risk_bucket": "Liquidity", "thesis": "Small cash buffer to keep the stress case capital intensive."},
        ),
    ),
}


def list_portfolios() -> list[PortfolioDefinition]:
    return list(PORTFOLIO_CATALOG.values())


def get_portfolio(portfolio_id: str | None = None) -> PortfolioDefinition:
    if portfolio_id and portfolio_id in PORTFOLIO_CATALOG:
        return PORTFOLIO_CATALOG[portfolio_id]
    return PORTFOLIO_CATALOG["core_long_equity"]
