# AI-Enhanced Risk Monitoring and Decision Support System

Production-style Python MVP for deterministic portfolio risk computation and AI-assisted interpretation.

## What This Repository Does

This project separates numerical risk computation from language generation:

- Deterministic Python logic computes exposure, VaR, limit checks, and risk drivers.
- Service and orchestration layers package tool outputs and generate interpretable summaries.
- API routes stay thin and delegate business logic to services.
- Every request is logged with tool outputs and latency for auditability.

## Architecture Overview

The repository is structured into clear layers:

1. API layer (`app/api`): FastAPI app and route handlers.
2. Service layer (`app/services`): endpoint workflows and request tracing.
3. Orchestration layer (`app/agents`): tool sequencing and interpretation assembly.
4. Risk engine layer (`app/risk`): deterministic numerical calculations only.
5. Tool layer (`app/tools`): typed wrappers around risk engine functions.
6. Models layer (`app/models`): request/response and domain result schemas.
7. Data layer (`app/data`): mock trades and historical return scenarios.
8. Persistence layer (`app/db`, `app/core/logging.py`): SQLite audit logging.

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Pandas / NumPy
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
|   |       |-- health.py
|   |       `-- risk.py
|   |-- core/
|   |   |-- config.py
|   |   `-- logging.py
|   |-- data/
|   |   |-- mock_market.py
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
  - `on_startup()`: initializes SQLite schema via `init_db()`.

- `app/api/routes/health.py`
  - `get_health()`: returns `status`, `service`, and UTC timestamp.

- `app/api/routes/risk.py`
  - `compute_risk_route()`: validates payload and calls service `compute_risk()`.
  - `analyze_risk_route()`: validates payload and calls service `analyze_risk()`.

- `app/api/routes/chat.py`
  - `chat_route()`: validates payload and delegates to `ChatService.chat()`.

### Service Layer

- `app/services/risk_service.py`
  - `_resolve_trades()`: uses request trades or falls back to mock trades.
  - `_resolve_limits()`: uses request limits or defaults from config.
  - `compute_risk()`: computes deterministic snapshot and logs structured trace.
  - `analyze_risk()`: computes snapshot, interprets results, and logs trace.

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

- `app/risk/exposure.py`
  - `compute_portfolio_exposure()`: computes net, gross, and per-symbol signed notional exposure.

- `app/risk/var.py`
  - `_symbol_positions()`: converts trades to signed notional positions by symbol.
  - `calculate_portfolio_var()`: historical-simulation VaR from position-weighted return PnL series.

- `app/risk/limits.py`
  - `detect_limit_breaches()`: checks gross exposure and VaR thresholds.

- `app/risk/drivers.py`
  - `identify_risk_drivers()`: finds top exposure and VaR-proxy contributors.

- `app/risk/engine.py`
  - `compute_risk_snapshot()`: composes full deterministic output (exposure, VaR, breaches, drivers).

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
  - Request/response schemas for `/risk/compute`, `/risk/analyze`, `/chat`, and `/health`.
  - Shared payload models: `TradeSchema`, `LimitConfigSchema`.

- `app/models/risk_models.py`
  - Domain output models: `ExposureResult`, `VaRResult`, `LimitBreach`, `DriversResult`,
    `RiskComputationResult`, `InterpretationResult`, `RiskAnalysisResult`.

### Data and Persistence

- `app/data/mock_trades.py`
  - `get_mock_trades()`: default portfolio used when requests omit trade lists.

- `app/data/mock_market.py`
  - `get_mock_historical_returns()`: per-symbol historical return scenarios for VaR and driver logic.

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
  - Validates deterministic risk primitives with mock inputs.

## API Endpoints

- `GET /dashboard`
- `GET /api/health`
- `GET /api/portfolios`
- `GET /api/risk/report`
- `POST /api/chat`
- `POST /api/reports/generate`

## Request Flow

1. Route validates request using Pydantic schemas.
2. Service resolves defaults (trades, limits) and starts timing.
3. Orchestrator executes deterministic tools.
4. Interpreter creates explanation text from computed outputs.
5. Service logs tools, outputs, context, model name, and latency.
6. API returns structured JSON response.

## Configuration

Environment-driven settings are defined in `app/core/config.py`:

- `APP_NAME`
- `SQLITE_DB_PATH`
- `VAR_CONFIDENCE`
- `MAX_GROSS_EXPOSURE`
- `MAX_VAR`
- `CHROMA_PATH`
- `LLM_MODEL_NAME`

Defaults are applied if environment variables are absent or unparsable.

## Features

- Deterministic risk engine:
  - Portfolio exposure aggregation
  - Historical VaR
  - Limit breach detection
  - Risk driver identification
- Typed tool wrappers around risk engine functions
- Orchestrator for tool-calling and interpretation assembly
- SQLite request logging for auditability
- Local retrieval via Chroma for policy context in chat responses
- Floating dashboard AI Copilot for grounded portfolio Q&A
- Markdown report generation for morning notes, end-of-day wraps, and weekly reviews, with styled HTML export from the dashboard
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
- http://127.0.0.1:8000/docs

## Example Requests

Health:

```bash
curl http://127.0.0.1:8000/health
```

Risk compute:

```bash
curl -X POST http://127.0.0.1:8000/risk/compute \
  -H "Content-Type: application/json" \
  -d '{
    "trades": [
      {"trade_id": "X1", "symbol": "AAPL", "side": "BUY", "quantity": 100, "price": 195},
      {"trade_id": "X2", "symbol": "MSFT", "side": "BUY", "quantity": 60, "price": 432},
      {"trade_id": "X3", "symbol": "TSLA", "side": "SELL", "quantity": 25, "price": 205}
    ],
    "confidence": 0.95,
    "limit_config": {
      "max_gross_exposure": 1000000,
      "max_var": 100000
    }
  }'
```

Risk analyze:

```bash
curl -X POST http://127.0.0.1:8000/risk/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What changed and what should we monitor?"
  }'
```

Chat:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a risk summary for this portfolio"}'
```

## Tests

```bash
pytest
```
