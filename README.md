# AI-Enhanced Risk Monitoring and Decision Support System

Production-style Python MVP for deterministic portfolio risk computation and AI-assisted interpretation.

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Pandas / NumPy
- Chroma (local vector store)
- SQLite (request audit logs)

## Project Structure

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

## Features

- Deterministic risk engine:
  - Portfolio exposure aggregation
  - Historical VaR
  - Limit breach detection
  - Risk driver identification
- Tool wrappers with typed I/O (Pydantic)
- Orchestrator for tool-calling and interpretation
- API endpoints:
  - `POST /risk/compute`
  - `POST /risk/analyze`
  - `POST /chat`
  - `GET /health`
- SQLite request logging (auditability)
- Local vector retrieval via Chroma for policy context in chat

## Implementation Checklist

Status reflects current code in this repository.

- [x] FastAPI app scaffold with mounted routes (`/health`, `/risk/compute`, `/risk/analyze`, `/chat`)
- [x] Deterministic risk engine modules (exposure, historical VaR, limit checks, risk drivers)
- [x] Typed tool wrappers and orchestrator wiring
- [x] Service-layer request logging into SQLite (`request_logs`)
- [x] Local policy-context retrieval in chat flow (Chroma)
- [x] Basic automated tests for health endpoint and risk engine primitives
- [ ] API integration tests for `/risk/compute`, `/risk/analyze`, and `/chat`
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

## Example curl requests

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

## Run tests

```bash
pytest
```
