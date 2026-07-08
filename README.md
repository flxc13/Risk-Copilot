# AI-Enhanced Risk Monitoring and Decision Support System

Production-style Python app for portfolio risk analytics, Basel-style capital monitoring, and grounded report generation.

## What This Repository Does

This project separates deterministic market-risk computation from language generation:

- Deterministic Python logic computes portfolio NAV, returns, drawdown, VaR, stressed VaR, and Basel-style capital components.
- Service and report layers package market-data outputs into dashboard payloads and markdown reporting.
- API routes stay thin and delegate business logic to services.
- The dashboard consumes the same API surface used by report generation and portfolio inspection.

## Architecture Overview

The repository is structured into clear layers:

1. API layer (`app/api`): FastAPI app and route handlers.
2. Service layer (`app/services`): endpoint workflows and request tracing.
3. Orchestration layer (`app/agents`): tool sequencing and interpretation assembly.
4. Risk engine layer (`app/risk`): deterministic numerical calculations only.
5. Tool layer (`app/tools`): typed wrappers around risk engine functions.
6. Models layer (`app/models`): request/response and domain result schemas.
7. Data layer (`app/data`): sample portfolios, market-data ingestion, cache, and historical stress calibration inputs.
8. Persistence layer (`app/db`, `app/core/logging.py`): SQLite audit logging.

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Pandas / NumPy
- yfinance
- Chroma (local vector store)
- SQLite (request audit logs)

## Repository Structure

```text
.
|-- app/
|   |-- agents/
|   |   |-- orchestrator.py
|   |   |-- prompts.py
|   |   `-- risk_interpreter.py
|   |-- api/
|   |   |-- main.py
|   |   `-- routes/
|   |       |-- chat.py
|   |       |-- dashboard.py
|   |       |-- health.py
|   |       |-- market_data.py
|   |       |-- phase1.py
|   |       |-- reports.py
|   |       `-- risk.py
|   |-- core/
|   |   |-- config.py
|   |   `-- logging.py
|   |-- data/
|   |   |-- market_data.py
|   |   |-- mock_market.py
|   |   |-- portfolio_catalog.py
|   |   `-- mock_trades.py
|   |-- db/
|   |   |-- session.py
|   |   `-- tables.py
|   |-- models/
|   |   |-- risk_models.py
|   |   `-- schemas.py
|   |-- risk/
|   |   |-- drivers.py
|   |   |-- engine.py
|   |   |-- exposure.py
|   |   |-- limits.py
|   |   `-- var.py
|   |-- services/
|   |   |-- chat_service.py
|   |   |-- phase1_service.py
|   |   |-- report_service.py
|   |   `-- risk_service.py
|   `-- tools/
|       |-- drivers_tool.py
|       |-- exposure_tool.py
|       |-- limit_tool.py
|       `-- var_tool.py
|-- scripts/
|   `-- example_payload.json
|-- tests/
|   |-- test_health.py
|   `-- test_risk_engine.py
|-- .env.example
|-- pyproject.toml
`-- README.md
```

## Module and Function Guide

### API Layer

- `app/api/main.py`
  - `app`: FastAPI application instance.
  - `create_app()`: configures logging, CORS, and the dashboard/API routers.

- `app/api/routes/health.py`
  - `health()`: returns `status`, `service`, and environment metadata.

- `app/api/routes/dashboard.py`
  - `dashboard()`: serves the interactive HTML dashboard client.

- `app/api/routes/market_data.py`
  - `historical_prices()`: returns cached or live yfinance history for requested tickers.

- `app/api/routes/phase1.py`
  - `phase1_status()`: returns implementation-status evidence for the Phase 1 slice.

- `app/api/routes/risk.py`
  - `risk_report()`: returns the portfolio analytics and Basel-style risk report payload.
  - `portfolios()`: returns the sample strategy portfolio catalog metadata.

- `app/api/routes/chat.py`
  - `chat_route()`: validates payload and delegates to `ChatService.chat()`.

- `app/api/routes/reports.py`
  - `generate_risk_report_markdown()`: generates markdown report output from the live risk payload.

### Service Layer

- `app/services/risk_service.py`
  - `list_available_portfolios()`: exposes strategy/desk metadata for the dashboard portfolio selector.
  - `_select_governed_stress_market_data()`: evaluates approved stress candidate windows and selects the conservative calibration.
  - `generate_risk_report()`: returns the full portfolio analytics payload in demo or live market-data mode.

- `app/services/report_service.py`
  - `generate_report()`: produces markdown reports for morning notes, reviews, and Basel-style capital monitoring.
  - `_basel_simplified_report()`: emits the Basel 2.5 internal monitoring format with selected stress-window disclosure.

- `app/services/phase1_service.py`
  - `get_phase1_status()`: returns evidence-backed delivery status for the Phase 1 implementation scope.

- `app/services/chat_service.py`
  - `ChatService.__init__()`: initializes orchestrator and Chroma collection.
  - `ChatService._retrieve_context()`: retrieves top policy/methodology context chunks.
  - `ChatService.chat()`: decides whether to run risk analysis, formats response, logs trace.

### Orchestration and Interpretation Layer

- `app/agents/orchestrator.py`
  - `RiskOrchestrator.compute()`: runs exposure, VaR, limit, and driver tools.
  - `RiskOrchestrator.analyze()`: computes risk and adds interpretation text.

- `app/agents/risk_interpreter.py`
  - `interpret_risk()`: converts deterministic outputs into explanation, hypothesis, suggestion.

- `app/agents/prompts.py`
  - `RISK_INTERPRETER_SYSTEM_PROMPT`: baseline instruction text for interpretation behavior.

### Deterministic Risk Engine Layer

- `app/risk/engine.py`
  - `build_risk_report()`: composes the dashboard/report payload from holdings, prices, benchmark data, and Basel metrics.
  - `portfolio_returns_from_current_values()`: applies historical stress returns to current portfolio market values for sVaR.

- `app/risk/var.py`
  - `historical_var()`, `expected_shortfall()`, `rolling_var()`: base market-risk measures.
  - `basel_historical_var()`: 99% 10-day Basel-style VaR measure.
  - `basel_stressed_historical_var()`: fallback stressed VaR when a separate stress frame is unavailable.
  - `basel_backtesting_exceptions()`, `basel_multiplier()`: backtesting and multiplier helpers.

- `app/risk/exposure.py`
  - `exposure_by_ticker()`, `exposure_by_asset_class()`, `top_holdings()`: portfolio exposure and concentration helpers.

- `app/risk/limits.py`
  - `assess_limits()`: checks concentration and VaR-style warning thresholds.

- `app/risk/drivers.py`
  - `build_driver_summary()`: summarizes holdings-level risk contributors.

### Tool Layer (Typed Wrappers)

- `app/tools/exposure_tool.py`
  - `ExposureToolInput`, `ExposureToolOutput`, `run_exposure_tool()`.

- `app/tools/var_tool.py`
  - `VaRToolInput`, `VaRToolOutput`, `run_var_tool()`.

- `app/tools/limit_tool.py`
  - `LimitToolInput`, `LimitToolOutput`, `run_limit_tool()`.

- `app/tools/drivers_tool.py`
  - `DriversToolInput`, `DriversToolOutput`, `run_drivers_tool()`.

### Models and Schemas

- `app/models/schemas.py`
  - Response schemas for dashboard/API routes including `RiskReport` and generated-report payloads.
  - `RiskReport` includes portfolio analytics, Basel VaR/sVaR fields, selected stress-window metadata, proxies used, and governance warnings.

- `app/models/risk_models.py`
  - Domain output models: `ExposureResult`, `VaRResult`, `LimitBreach`, `DriversResult`,
    `RiskComputationResult`, `InterpretationResult`, `RiskAnalysisResult`.

### Data and Persistence

- `app/data/portfolio_catalog.py`
  - `PortfolioDefinition`: portfolio metadata including approved Basel stress-window candidates and methodology.
  - `get_portfolio()`, `list_portfolios()`: sample portfolio catalog accessors.

- `app/data/market_data.py`
  - `ingest_historical_prices()`: cached live history from yfinance.
  - `ingest_governed_stress_prices()`: prepares approved stress histories and proxy transformations for short-history instruments.

- `app/data/mock_market.py`
  - `get_demo_market_data()`: deterministic demo price paths used for fallback and testing.

- `app/data/mock_trades.py`
  - `get_demo_portfolio_by_id()`: sample holdings for each strategy portfolio.

- `app/db/session.py`
  - `get_connection()`: SQLite connection factory.

- `app/db/tables.py`
  - `ensure_tables()`: creates `request_logs` table if missing.
  - `init_db()`: initializes persistence at startup.

- `app/core/logging.py`
  - `get_logger()`: standard logger retrieval.
  - `log_request()`: structured request-level audit insertion into SQLite.

### Tests

- `tests/test_health.py`
  - Validates `/health` endpoint contract.

- `tests/test_risk_engine.py`
  - Validates deterministic analytics, Basel stress-window selection, and sVaR behavior.

- `tests/test_market_data.py`
  - Validates cache behavior, named stress windows, and approved proxy mapping.

- `tests/test_reports.py`
  - Validates markdown report generation including the Basel monitoring format.

## API Endpoints

- `GET /dashboard`
- `GET /api/health`
- `GET /api/market-data/history`
- `GET /api/portfolios`
- `GET /api/phase1/status`
- `GET /api/risk/report`
- `POST /api/chat`
- `POST /api/reports/generate`

## Request Flow

1. The dashboard or client selects a sample portfolio and demo/live market-data mode.
2. The risk service fetches recent market history plus approved candidate stress windows.
3. The service evaluates stressed VaR across the approved candidate set and selects the conservative calibration window.
4. The risk engine computes NAV series, returns, VaR, sVaR, drawdown, benchmark statistics, exposures, and Basel-style capital measures.
5. The report service converts the risk payload into markdown when the reporting route is used.
6. The API returns JSON for dashboard/report consumers, with fallback demo mode if live market data is unavailable.

## Configuration

Environment-driven settings are defined in `app/core/config.py`:

- `APP_NAME`
- `SQLITE_DB_PATH`
- `API_PREFIX`
- `ENVIRONMENT`
- `VAR_CONFIDENCE`
- `MAX_GROSS_EXPOSURE`
- `MAX_VAR`
- `CHROMA_PATH`
- `LLM_MODEL_NAME`
- `BENCHMARK_TICKER`
- `DEMO_LOOKBACK_DAYS`
- `POE_API_KEY`

Defaults are applied if environment variables are absent or unparsable.

## Features

- Deterministic risk engine:
  - Portfolio NAV and return-series construction
  - Historical VaR and expected shortfall
  - Basel 2.5-style VaR, stressed VaR, backtesting, and capital legs
  - Exposure, concentration, benchmark, and drawdown analytics
- Typed tool wrappers around risk engine functions
- Orchestrator for tool-calling and interpretation assembly
- SQLite request logging for auditability
- Local retrieval via Chroma for policy context in chat responses
- Floating dashboard AI Copilot for grounded portfolio Q&A
- Markdown report generation for morning notes, end-of-day wraps, and weekly reviews, with styled HTML export from the dashboard
- Basel 2.5-style capital monitoring with governed candidate stress windows, conservative stress-window selection, yfinance stress histories, proxy mappings for short-history instruments, and governance warnings when stress calibration needs review
- Deterministic sample-data report fallback when the AI provider is unavailable

## Implementation Checklist

Status reflects current code in this repository.

- [x] FastAPI app scaffold with mounted dashboard, risk, chat, and report routes
- [x] Deterministic risk engine modules (exposure, historical VaR, limit checks, risk drivers)
- [x] Typed tool wrappers and orchestrator wiring
- [x] Service-layer request logging into SQLite (`request_logs`)
- [x] Local policy-context retrieval in chat flow (Chroma)
- [x] Basic automated tests for health endpoint and risk engine primitives
- [x] API tests for chat fallback, report fallback, dashboard rendering, market data, and risk output
- [x] Basel 2.5-style VaR/sVaR capital monitoring with governed stress-window assignment and proxy disclosure
- [ ] CI workflow for automated test/lint on push/PR
- [ ] Machine-readable progress tracker (for example `progress.json`)

Checklist update rule:

- If implementation status changes, update this checklist in the same change set.

## Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows PowerShell

pip install -U pip
pip install -e .
```

Optional dev dependencies:

```bash
pip install -e .[dev]
```

## Run

```bash
uvicorn app.api.main:app --reload
```

API docs:

- [OpenAPI docs](http://127.0.0.1:8000/docs)

## Example Requests

Health:

```bash
curl http://127.0.0.1:8000/api/health
```

Available portfolios:

```bash
curl http://127.0.0.1:8000/api/portfolios
```

Risk report payload:

```bash
curl "http://127.0.0.1:8000/api/risk/report?portfolio_id=core_long_equity&use_demo_data=false"
```

Historical market data:

```bash
curl "http://127.0.0.1:8000/api/market-data/history?tickers=AAPL&tickers=MSFT&tickers=SPY&period=1y"
```

Generated Basel-style capital report:

```bash
curl -X POST http://127.0.0.1:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": "high_octane_trading",
    "use_demo_data": false,
    "report_type": "basel_simplified_capital",
    "audience": "Risk Control"
  }'
```

Chat:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a risk summary for this portfolio"}'
```

## Run Tests

```bash
pytest
```
