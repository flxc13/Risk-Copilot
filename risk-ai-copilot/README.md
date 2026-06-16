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
risk-ai-copilot/
?œâ? app/
?? ?œâ? api/
?? ?? ?œâ? main.py
?? ?? ?œâ? routes/
?? ?? ?? ?œâ? chat.py
?? ?? ?? ?œâ? risk.py
?? ?? ?? ?”â? health.py
?? ?œâ? core/
?? ?? ?œâ? config.py
?? ?? ?”â? logging.py
?? ?œâ? agents/
?? ?? ?œâ? orchestrator.py
?? ?? ?œâ? risk_interpreter.py
?? ?? ?”â? prompts.py
?? ?œâ? risk/
?? ?? ?œâ? engine.py
?? ?? ?œâ? exposure.py
?? ?? ?œâ? var.py
?? ?? ?œâ? limits.py
?? ?? ?”â? drivers.py
?? ?œâ? tools/
?? ?? ?œâ? exposure_tool.py
?? ?? ?œâ? var_tool.py
?? ?? ?œâ? limit_tool.py
?? ?? ?”â? drivers_tool.py
?? ?œâ? services/
?? ?? ?œâ? chat_service.py
?? ?? ?”â? risk_service.py
?? ?œâ? models/
?? ?? ?œâ? schemas.py
?? ?? ?”â? risk_models.py
?? ?œâ? data/
?? ?? ?œâ? mock_trades.py
?? ?? ?”â? mock_market.py
?? ?”â? db/
??    ?œâ? session.py
??    ?”â? tables.py
?œâ? tests/
?œâ? scripts/
?œâ? .env.example
?œâ? pyproject.toml
?œâ? README.md
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

From the `risk-ai-copilot` directory:

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
