# README.md

## Project Title
**Risk Advisor Copilot**  
A production-style portfolio risk analytics platform with a clean UI, market data ingestion, portfolio construction, VaR monitoring, and an AI-powered risk copilot roadmap.

---

## Overview
This repository is intended to evolve in **three phases**:

- **Phase 1:** Build the core risk engine and UI
- **Phase 2:** Add an AI Risk Copilot
- **Phase 3:** Deploy to AWS in a simple, scalable way

The goal is to make the repo feel like a **production-grade risk application**, not just a notebook or demo script. That means clear architecture, separation of concerns, testability, observability, and a UI that supports real workflows.

---

## Product Vision
Risk Advisor Copilot helps users:
- create and manage a sample portfolio
- fetch market data using `yfinance`
- calculate and monitor portfolio risk
- track **VaR** and other meaningful risk metrics
- visualize exposures, drawdowns, and scenario behavior
- eventually interact with an AI copilot that explains risk in plain English, detects anomalies, and suggests next steps

This project is designed as a practical foundation for:
- portfolio risk monitoring
- internal risk dashboards
- analyst tooling
- AI-assisted financial workflows

---

## Phase Plan

---

# Phase 1 — Core Risk App

## Objective
Implement the core portfolio analytics workflow end-to-end:
1. define a sample portfolio
2. fetch historical market data with `yfinance`
3. compute returns and portfolio value series
4. calculate VaR and other key risk metrics
5. surface results in a polished UI
6. structure the repository like a production app

## Core Features

### 1. Sample Portfolio Builder
The app should ship with a default portfolio so a user can run the project immediately without setup friction.

Example portfolio:
- AAPL
- MSFT
- NVDA
- AMZN
- SPY
- TLT
- GLD
- CASH

Possible fields:
- ticker
- asset class
- quantity
- average cost
- market value
- weight
- currency

Support:
- fixed demo portfolio in seed data
- optional manual editing in UI
- optional CSV/JSON import later

### 2. Market Data Ingestion
Use `yfinance` as the initial market data source.

Expected capabilities:
- fetch adjusted close prices
- pull historical daily data
- refresh on demand
- handle missing values gracefully
- cache downloaded data locally or in a simple store

Notes:
- `yfinance` is fine for development and prototyping
- architecture should allow replacing the provider later with a more robust market data source

### 3. Risk Metrics Engine
The first release should include a strong set of baseline portfolio risk metrics.

#### Required Metrics
- **Daily returns**
- **Cumulative returns**
- **Volatility**
- **Annualized volatility**
- **Historical VaR**
- **Parametric VaR**
- **Expected Shortfall / CVaR**
- **Maximum drawdown**
- **Sharpe ratio**
- **Beta vs benchmark**
- **Correlation matrix**
- **Rolling volatility**
- **Rolling VaR**

#### Nice-to-have Metrics
- marginal VaR
- component VaR
- contribution to volatility
- concentration by name/sector/asset class
- tracking error vs benchmark
- stress test under simple shock scenarios

### 4. Risk Monitoring Dashboard
The UI should feel like a real internal risk dashboard.

Suggested views:
- **Portfolio Overview**
  - total value
  - daily PnL
  - cumulative return
  - top holdings
  - risk summary cards

- **Risk Dashboard**
  - VaR
  - CVaR
  - volatility
  - drawdown
  - rolling risk charts

- **Exposure Dashboard**
  - weights by asset
  - concentration chart
  - sector allocation if metadata exists
  - benchmark comparison

- **Analytics**
  - return distribution
  - correlation heatmap
  - rolling metrics
  - scenario analysis

- **Data Health**
  - latest refresh time
  - missing data flags
  - ticker fetch status
  - provider warnings

### 5. Production-Grade Repository Shape
The repo should be organized so it resembles software that could realistically be extended into a team-owned platform.

Suggested qualities:
- modular risk engine
- API layer separated from UI
- typed schemas where possible
- unit tests for risk calculations
- environment variable config
- linting and formatting
- logging
- clear error handling
- reproducible local setup
- seed/demo data

---

## Phase 1 Technical Direction

### Suggested Stack
You can adapt this, but a pragmatic setup would be:

#### Backend
- **Python**
- **FastAPI** for API services
- **pandas / numpy** for analytics
- **yfinance** for market data ingestion
- **pydantic** for models
- **scipy / statsmodels** where useful for risk calculations

#### Frontend
Choose one of the following:
- **Next.js**
- **React + Vite**

Recommended:
- **Next.js** for a polished app structure and production feel

UI suggestions:
- Tailwind CSS
- Recharts or Plotly for charts
- simple design system for cards, tables, filters, alerts, and charts

#### Storage
Start simple:
- local file cache or SQLite for metadata/cache
- later migrate to Postgres if needed

### Suggested Repository Structure
```text
risk-advisor-copilot/
├─ README.md
├─ .env.example
├─ docker-compose.yml
├─ Makefile
├─ pyproject.toml
├─ apps/
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ routes/
│  │  ├─ services/
│  │  ├─ schemas/
│  │  └─ tests/
│  └─ web/
│     ├─ app/
│     ├─ components/
│     ├─ lib/
│     └─ public/
├─ packages/
│  ├─ risk-engine/
│  │  ├─ metrics/
│  │  ├─ portfolio/
│  │  ├─ market_data/
│  │  └─ tests/
│  └─ shared/
│     ├─ types/
│     └─ config/
├─ data/
│  ├─ seed/
│  ├─ cache/
│  └─ sample/
└─ docs/
   ├─ architecture/
   ├─ product/
   └─ api/
```

---

## Phase 1 Functional Scope

### In Scope
- sample portfolio creation
- `yfinance` integration
- historical price ingestion
- daily return calculation
- portfolio NAV/value series
- VaR and CVaR calculation
- drawdown analytics
- benchmark comparison
- interactive dashboard
- clean repo structure
- tests for core calculations

---

## Current Scaffold

The repository now includes a working Python backend scaffold for Phase 1:

- FastAPI app entrypoint at [app/api/main.py](app/api/main.py)
- health, risk, and chat routes under [app/api/routes/](app/api/routes)
- explicit portfolio risk calculations in [app/risk/](app/risk)
- demo market data and a live `yfinance` adapter in [app/data/](app/data)
- reusable request/response models in [app/models/schemas.py](app/models/schemas.py)
- API and calculation tests in [tests/](tests)

## Local Setup

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the API with `uvicorn app.api.main:app --reload`.
4. Run tests with `pytest`.

## API Endpoints

- `GET /api/health`
- `GET /api/portfolios`
- `GET /api/risk/report`
- `POST /api/chat`

## Sample Portfolios

The phase-1 scaffold now ships with strategy-based sample portfolios designed to mimic a small hedge fund's in-house risk tool:

- `core_long_equity` - Quality growth / long-only. Objective: compound capital with high-conviction large-cap equity exposure and a modest cash buffer.
- `defensive_income` - Capital preservation / income. Objective: prioritize drawdown control and steadier returns through defensive equities, bonds, gold, and cash.
- `tactical_macro` - Macro / regime rotation. Objective: rotate capital between risk assets and diversifiers when macro conditions shift.

### Out of Scope
- live trading
- broker connectivity
- real-time streaming quotes
- user auth
- multi-tenant enterprise controls
- options/derivatives pricing engine
- advanced regulatory reporting

---

## Example User Flow
1. user opens the app
2. demo portfolio is already loaded
3. app fetches historical prices for portfolio assets
4. backend computes portfolio-level returns and risk metrics
5. UI displays:
   - total portfolio value
   - allocation
   - rolling volatility
   - historical VaR
   - expected shortfall
   - drawdown chart
   - correlation heatmap
6. user edits weights or holdings
7. metrics recalculate
8. user inspects current risk posture and concentration

---

## Risk Metrics Notes

### VaR
The application should support at least:
- **Historical VaR**
- **Parametric VaR**

Recommended defaults:
- confidence levels: 95% and 99%
- horizon: 1 day initially

### Expected Shortfall
Show tail-loss severity beyond VaR to make the dashboard more meaningful than VaR alone.

### Drawdown
Track:
- current drawdown
- max drawdown
- drawdown duration if feasible

### Benchmarking
Use a simple benchmark such as:
- `SPY` for equity-heavy portfolios
- configurable benchmark later

### Scenario Testing
Even in Phase 1, a few basic scenarios would add a lot of value:
- equity market down 5%
- rates up 100 bps
- tech sector shock
- flight-to-safety scenario

These can be simple deterministic shocks at first.

---

## UI Principles
The UI should feel:
- clean
- professional
- readable
- analyst-friendly
- low-friction

Recommended layout:
- left sidebar navigation
- top summary cards
- charts in a grid
- portfolio table with sorting/filtering
- risk alerts or badges for threshold breaches

Design suggestions:
- neutral colors with meaningful use of red/amber/green
- avoid flashy retail-trading aesthetics
- prefer clarity over decoration

---

## Phase 2 — AI Risk Copilot

## Objective
Add a conversational and analytical AI layer on top of the risk engine.

The AI Risk Copilot should not just answer questions. It should help users **understand, investigate, and act on portfolio risk**.

## Proposed Capabilities

### 1. Natural Language Risk Q&A
Examples:
- “Why did portfolio VaR increase this week?”
- “Which holdings contribute most to downside risk?”
- “What changed after I added NVDA?”
- “How concentrated is this portfolio?”
- “What happens if equities fall 7%?”

### 2. Portfolio Risk Explanations
The copilot should translate quantitative outputs into plain-English summaries:
- what changed
- likely drivers
- which positions matter most
- whether the portfolio is becoming more concentrated or more diversified

### 3. Risk Change Detection
The AI can highlight:
- unusual VaR jumps
- rising correlation across holdings
- concentration creep
- volatility regime shifts
- benchmark divergence

### 4. Scenario Narration
Given a stress scenario, the copilot can explain:
- expected portfolio impact
- most sensitive names
- offsetting exposures
- interpretation of results

### 5. Guided What-If Analysis
Examples:
- “Reduce tech exposure by 10%”
- “Increase bonds to lower drawdown risk”
- “Show a more diversified version of this portfolio”
- “How can I lower VaR without materially changing expected exposure?”

### 6. Document and Report Generation
The copilot could generate:
- daily risk summaries
- weekly PM notes
- investment committee snapshots
- plain-English portfolio diagnostics

### 7. Alert Triage
If thresholds are breached, AI can answer:
- what happened
- why it matters
- what to review next
- whether this looks like a data issue or a real market move

---

## Phase 2 Architecture Ideas
Possible implementation path:
- LLM-powered chat interface
- retrieval over portfolio state, risk metrics, and scenario outputs
- tool-calling functions for:
  - fetching latest portfolio stats
  - recalculating risk
  - comparing two portfolio versions
  - running predefined stress tests
  - summarizing alerts

### Guardrails
The AI copilot should:
- avoid giving trading advice framed as certainty
- distinguish facts from interpretation
- reference computed metrics, not invented numbers
- clearly label assumptions in scenario analysis

### Nice Future Features
- voice-enabled risk briefings
- anomaly summaries each morning
- AI-generated board-ready charts and commentary
- portfolio optimization suggestions under constraints
- policy and threshold recommendation assistant
- risk memo generation in markdown/PDF

---

## Phase 3 — AWS Deployment

## Objective
Deploy the app to AWS in a simple, clean, later-stage setup.

This phase should be intentionally lightweight at first. Keep it practical and easy to operate.

## Guiding Principles
- keep AWS setup simple
- avoid over-engineering early
- optimize for maintainability
- support future scaling

## Suggested Later-Stage AWS Plan
A simple path could be:

- **Frontend**
  - deploy web app on **AWS Amplify** or **S3 + CloudFront**

- **Backend API**
  - deploy FastAPI using:
    - **App Runner**, or
    - **ECS Fargate**

- **Database**
  - start with **RDS Postgres** if persistent storage is needed
  - or keep SQLite/local storage during earlier stages

- **Secrets and Config**
  - AWS Secrets Manager
  - SSM Parameter Store

- **Monitoring**
  - CloudWatch logs and alarms

- **CI/CD**
  - GitHub Actions
  - deploy on main branch or tagged releases

## Keep for Later
The AWS phase is intentionally deferred until the core app and copilot are stable.

---

## Engineering Principles
This repository should aim to reflect production-minded engineering:

- clean separation of UI, API, and analytics engine
- explicit schemas and contracts
- deterministic calculations
- test coverage for key risk logic
- observable services with logs and health endpoints
- graceful fallback for bad market data
- easy local onboarding
- documented architecture and roadmap

---

## MVP Definition
The Phase 1 MVP is complete when a user can:

- run the project locally
- load a sample portfolio
- fetch historical data from `yfinance`
- compute portfolio returns
- view VaR, CVaR, volatility, and drawdown
- inspect portfolio allocation and correlations
- use a decent UI that feels like a real application

---

## Suggested Milestones

### Milestone 1 — Repo Foundation
- initialize monorepo/app structure
- set up backend and frontend
- add config, linting, formatting, and test scaffolding

### Milestone 2 — Market Data + Portfolio Model
- sample portfolio seed data
- `yfinance` ingestion service
- normalized portfolio schema
- local caching

### Milestone 3 — Risk Engine
- returns pipeline
- portfolio aggregation
- VaR
- CVaR
- volatility
- drawdown
- benchmark comparison

### Milestone 4 — Dashboard UI
- overview page
- holdings table
- risk charts
- heatmaps
- alerts and badges

### Milestone 5 — AI Copilot Design
- define tools and prompts
- create risk explanation workflows
- build chat entry point
- connect to analytics outputs

### Milestone 6 — AWS Deployment
- choose simple AWS topology
- containerize services
- configure deployment
- add monitoring and CI/CD

---

## Local Development Goals
The local developer experience should be easy:
- one command to install backend dependencies
- one command to run API
- one command to run UI
- seeded portfolio available by default
- sample screenshots and example outputs in `/docs`

---

## Future Enhancements
Potential extensions after the first three phases:
- user authentication
- multiple portfolios
- portfolio upload workflow
- factor risk models
- options and derivatives support
- intraday data providers
- alert subscriptions
- PDF export
- scheduled risk reports
- optimization engine
- role-based access control
- audit logs

---

## Proposed Tagline
**A production-style portfolio risk dashboard with an AI copilot for monitoring, explaining, and exploring risk.**

---

## Next Step
Start with **Phase 1** and build the core system first:
- sample portfolio
- market data fetch
- risk engine
- polished UI
- production-style repo structure

Once that foundation is stable, layer on the **AI Risk Copilot**, then move to a simple **AWS deployment**.

---
```  
