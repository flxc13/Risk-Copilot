from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(_dashboard_html())


def _dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Risk Advisor Copilot Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #07101d;
      --panel: rgba(12, 18, 34, 0.94);
      --panel-2: rgba(15, 23, 42, 0.95);
      --panel-3: rgba(18, 28, 50, 0.96);
      --line: rgba(148, 163, 184, 0.16);
      --text: #e5eefb;
      --muted: #8ea0bb;
      --accent: #67e8f9;
      --accent-2: #f59e0b;
      --good: #34d399;
      --bad: #fb7185;
      --shadow: 0 28px 80px rgba(0, 0, 0, 0.38);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(103, 232, 249, 0.16), transparent 28%),
        radial-gradient(circle at 80% 10%, rgba(245, 158, 11, 0.10), transparent 24%),
        linear-gradient(180deg, #040814 0%, #07101d 54%, #0c172b 100%);
      color: var(--text);
      min-height: 100vh;
    }
    a { color: inherit; text-decoration: none; }
    .app-shell {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      position: sticky;
      top: 0;
      align-self: start;
      min-height: 100vh;
      padding: 24px 18px;
      border-right: 1px solid rgba(148, 163, 184, 0.12);
      background: linear-gradient(180deg, rgba(7, 12, 24, 0.94), rgba(10, 16, 32, 0.92));
      backdrop-filter: blur(16px);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }
    .brand-mark {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      background: linear-gradient(135deg, #67e8f9, #0ea5e9 55%, #22c55e);
      box-shadow: 0 0 0 1px rgba(255,255,255,0.06) inset;
    }
    .brand-copy strong {
      display: block;
      font-size: 16px;
      letter-spacing: 0.03em;
    }
    .brand-copy span {
      color: var(--muted);
      font-size: 12px;
    }
    .side-section {
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.02);
      margin-bottom: 14px;
    }
    .side-title {
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    .nav-list {
      display: grid;
      gap: 10px;
    }
    .nav-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid transparent;
      background: rgba(255,255,255,0.02);
      color: var(--text);
      transition: 140ms ease;
    }
    .nav-item:hover, .nav-item.active {
      border-color: rgba(103, 232, 249, 0.22);
      background: rgba(103, 232, 249, 0.08);
      transform: translateX(2px);
    }
    .nav-item small {
      color: var(--muted);
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(52, 211, 153, 0.12);
      color: var(--good);
      font-size: 12px;
      font-weight: 700;
    }
    .sidebar-kpi {
      display: grid;
      gap: 8px;
    }
    .sidebar-kpi .label {
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }
    .sidebar-kpi .value {
      font-size: 22px;
      font-weight: 800;
    }
    .sidebar-kpi .note {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }
    .content {
      padding: 28px;
    }
    .hero {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      margin-bottom: 22px;
    }
    .eyebrow {
      color: var(--accent);
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin: 0 0 8px;
    }
    h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.8rem);
      line-height: 0.96;
    }
    .subtitle {
      color: var(--muted);
      max-width: 860px;
      margin-top: 10px;
      font-size: 15px;
    }
    .controls, .card, .panel {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(10, 16, 32, 0.96), rgba(12, 19, 36, 0.9));
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }
    .controls {
      display: grid;
      grid-template-columns: 1.5fr 1fr 1fr auto;
      gap: 14px;
      padding: 16px;
      border-radius: 20px;
      margin-bottom: 18px;
      align-items: end;
    }
    .field label {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    select, button {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #0d1729;
      color: var(--text);
      padding: 12px 14px;
      font-size: 14px;
    }
    button {
      cursor: pointer;
      background: linear-gradient(135deg, #0ea5e9, #22c55e);
      color: #04111a;
      font-weight: 800;
      min-width: 120px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }
    .card {
      border-radius: 18px;
      padding: 16px;
      min-height: 112px;
    }
    .metric-label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .metric-value {
      font-size: clamp(1.5rem, 2.2vw, 2.4rem);
      font-weight: 800;
      margin-top: 10px;
    }
    .metric-note {
      color: var(--muted);
      margin-top: 8px;
      font-size: 13px;
      line-height: 1.45;
    }
    .layout {
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 16px;
      margin-top: 16px;
    }
    .layout.alt {
      grid-template-columns: 1fr 1fr;
    }
    .panel {
      border-radius: 22px;
      padding: 16px;
      min-height: 460px;
    }
    .panel h2 {
      margin: 0 0 12px;
      font-size: 18px;
    }
    .panel p.helper {
      margin: -2px 0 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    .chart {
      width: 100%;
      height: 360px;
    }
    .table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
      font-size: 14px;
    }
    .table th, .table td {
      border-bottom: 1px solid rgba(148, 163, 184, 0.14);
      padding: 10px 8px;
      text-align: left;
    }
    .table th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .status-list {
      display: grid;
      gap: 10px;
    }
    .status-item {
      display: flex;
      align-items: start;
      gap: 12px;
      padding: 12px;
      border: 1px solid rgba(148, 163, 184, 0.14);
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.02);
    }
    .status-pill {
      min-width: 28px;
      height: 28px;
      border-radius: 999px;
      display: grid;
      place-items: center;
      font-weight: 800;
      margin-top: 1px;
      background: rgba(52, 211, 153, 0.16);
      color: var(--good);
    }
    .status-pill.no {
      background: rgba(251, 113, 133, 0.14);
      color: var(--bad);
    }
    .status-copy strong {
      display: block;
      margin-bottom: 3px;
    }
    .warnings {
      margin-top: 10px;
      display: grid;
      gap: 8px;
    }
    .warning {
      border: 1px solid rgba(245, 158, 11, 0.25);
      background: rgba(245, 158, 11, 0.08);
      color: #fde68a;
      padding: 10px 12px;
      border-radius: 12px;
    }
    .small {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .section-gap { margin-top: 16px; }
    .content-section { scroll-margin-top: 20px; }
    .section-heading {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 12px;
      margin-bottom: 10px;
    }
    .section-heading h3 {
      margin: 0;
      font-size: 14px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.16em;
    }
    .section-heading span {
      color: var(--muted);
      font-size: 13px;
    }
    @media (max-width: 1260px) {
      .app-shell { grid-template-columns: 1fr; }
      .sidebar {
        position: relative;
        min-height: auto;
        border-right: 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
      }
    }
    @media (max-width: 1120px) {
      .controls, .summary-grid, .layout, .layout.alt {
        grid-template-columns: 1fr;
      }
      .hero {
        flex-direction: column;
        align-items: start;
      }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark"></div>
        <div class="brand-copy">
          <strong>Risk Advisor</strong>
          <span>In-house risk dashboard</span>
        </div>
      </div>

      <div class="side-section">
        <div class="side-title">Navigation</div>
        <div class="nav-list">
          <a class="nav-item active" href="#overview"><span>Overview</span><small>Core metrics</small></a>
          <a class="nav-item" href="#risk"><span>Risk</span><small>VaR, CVaR, drawdown</small></a>
          <a class="nav-item" href="#exposure"><span>Exposure</span><small>Weights and holdings</small></a>
          <a class="nav-item" href="#health"><span>Phase 1</span><small>Delivery status</small></a>
        </div>
      </div>

      <div class="side-section">
        <div class="side-title">Current view</div>
        <div class="sidebar-kpi">
          <div class="label">Selected portfolio</div>
          <div class="value" id="sidebar-portfolio-name">Loading...</div>
          <div class="note" id="sidebar-portfolio-note">Strategy objective and market mode will appear here.</div>
          <div class="status-badge" id="sidebar-data-badge">Demo data</div>
        </div>
      </div>

      <div class="side-section">
        <div class="side-title">Phase 1 check</div>
        <div class="sidebar-kpi">
          <div class="label">Implementation status</div>
          <div class="value" id="sidebar-phase-status">Checking...</div>
          <div class="note">This reflects the README scope for the phase-1 MVP slice.</div>
        </div>
      </div>
    </aside>

    <main class="content">
      <div class="hero" id="overview">
        <div>
          <p class="eyebrow">Risk Advisor Copilot</p>
          <h1>Interactive Risk Dashboard</h1>
          <div class="subtitle">A production-style dashboard for small hedge funds: strategy-based sample portfolios, live or demo market data, explicit risk calculations, benchmark comparison, and a completion view for the current phase.</div>
        </div>
      </div>

      <div class="controls">
        <div class="field">
          <label for="portfolio-select">Portfolio</label>
          <select id="portfolio-select"></select>
        </div>
        <div class="field">
          <label for="data-mode">Market data</label>
          <select id="data-mode">
            <option value="true">Demo data</option>
            <option value="false">Live yfinance data</option>
          </select>
        </div>
        <div class="field">
          <label>&nbsp;</label>
          <div class="small" id="portfolio-description">Loading portfolio catalog...</div>
        </div>
        <div class="field">
          <label>&nbsp;</label>
          <button id="refresh-button" type="button">Refresh</button>
        </div>
      </div>

      <div class="summary-grid" id="primary-metrics"></div>
      <div class="summary-grid" id="secondary-metrics"></div>

      <section class="layout content-section" id="risk">
        <div class="panel">
          <div class="section-heading">
            <h3>Portfolio vs benchmark</h3>
            <span>Normalized NAV and benchmark comparison</span>
          </div>
          <p class="helper">This view overlays portfolio NAV with the benchmark so the desk can see relative performance and drift at a glance.</p>
          <div id="value-chart" class="chart"></div>
        </div>
        <div class="panel" id="health">
          <div class="section-heading">
            <h3>Phase 1 completion</h3>
            <span>In-scope function check</span>
          </div>
          <p class="helper">This checklist reflects the README's phase-1 scope and makes the delivery status visible inside the app.</p>
          <div id="phase1-status" class="status-list"></div>
        </div>
      </section>

      <section class="layout alt content-section section-gap">
        <div class="panel">
          <div class="section-heading">
            <h3>Drawdown analytics</h3>
            <span>Current and peak-to-trough profile</span>
          </div>
          <p class="helper">Drawdown is computed directly from NAV. This helps a PM see how much risk remains after the latest high-water mark.</p>
          <div id="drawdown-chart" class="chart"></div>
        </div>
        <div class="panel">
          <div class="section-heading">
            <h3>Correlation matrix</h3>
            <span>Asset return relationships</span>
          </div>
          <p class="helper">A quick read on clustering risk, diversification, and whether the book is drifting toward one factor.</p>
          <div id="correlation-chart" class="chart"></div>
        </div>
      </section>

      <section class="layout alt content-section section-gap" id="exposure">
        <div class="panel">
          <div class="section-heading">
            <h3>Holdings and exposures</h3>
            <span>Portfolio composition</span>
          </div>
          <p class="helper">Position weights are ranked by market value so the largest names and hidden concentration stand out immediately.</p>
          <div id="holdings-chart" class="chart"></div>
        </div>
        <div class="panel">
          <div class="section-heading">
            <h3>Top holdings table</h3>
            <span>Position detail</span>
          </div>
          <p class="helper">Market value and weight table for the selected strategy basket.</p>
          <table class="table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Asset Class</th>
                <th>Market Value</th>
                <th>Weight</th>
              </tr>
            </thead>
            <tbody id="holdings-table"></tbody>
          </table>
          <div class="warnings" id="warning-list"></div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const state = {
      portfolios: [],
      currentPortfolioId: "core_long_equity",
      useDemoData: true,
      phase1Status: null,
    };

    const portfolioSelect = document.getElementById("portfolio-select");
    const dataMode = document.getElementById("data-mode");
    const refreshButton = document.getElementById("refresh-button");
    const portfolioDescription = document.getElementById("portfolio-description");
    const sidebarPortfolioName = document.getElementById("sidebar-portfolio-name");
    const sidebarPortfolioNote = document.getElementById("sidebar-portfolio-note");
    const sidebarDataBadge = document.getElementById("sidebar-data-badge");
    const sidebarPhaseStatus = document.getElementById("sidebar-phase-status");

    const money = new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
    const percentage = new Intl.NumberFormat(undefined, { style: "percent", minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const decimal = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });

    function normalizeSeries(series, keyName) {
      if (!Array.isArray(series) || series.length === 0) {
        return { x: [], y: [] };
      }
      const first = Number(series[0][keyName]);
      const x = series.map((point) => point.date);
      const y = series.map((point) => first === 0 ? Number(point[keyName]) : (Number(point[keyName]) / first) * 100);
      return { x, y };
    }

    function metricCard(label, value, note) {
      return `
        <div class="card">
          <div class="metric-label">${label}</div>
          <div class="metric-value">${value}</div>
          <div class="metric-note">${note}</div>
        </div>
      `;
    }

    function updateSidebar(report) {
      const selected = state.portfolios.find((portfolio) => portfolio.portfolio_id === report.portfolio_id);
      sidebarPortfolioName.textContent = report.portfolio_name;
      sidebarPortfolioNote.textContent = selected ? selected.objective : report.portfolio_objective || "";
      sidebarDataBadge.textContent = state.useDemoData ? "Demo data" : "Live yfinance data";
      sidebarPhaseStatus.textContent = state.phase1Status && state.phase1Status.complete ? "Complete" : "In progress";
    }

    function renderMetrics(report) {
      const primary = [
        ["Total Value", money.format(report.total_value), "Current portfolio market value."],
        ["Daily Return", percentage.format(report.daily_return), "Latest one-day return from the NAV series."],
        ["Cumulative Return", percentage.format(report.cumulative_return), "Growth since the start of the series."],
        ["Historical VaR", percentage.format(report.historical_var_95), "One-day historical VaR at the selected confidence level."],
      ];
      const secondary = [
        ["Expected Shortfall", percentage.format(report.expected_shortfall_95), "Tail loss severity beyond VaR."],
        ["Max Drawdown", percentage.format(report.maximum_drawdown), "Largest peak-to-trough loss."],
        ["Beta vs Benchmark", report.beta_vs_benchmark == null ? "n/a" : decimal.format(report.beta_vs_benchmark), "Sensitivity to the benchmark path."],
        ["Tracking Error", report.tracking_error == null ? "n/a" : percentage.format(report.tracking_error), "Volatility of active returns vs benchmark."],
      ];

      document.getElementById("primary-metrics").innerHTML = primary.map(([label, value, note]) => metricCard(label, value, note)).join("");
      document.getElementById("secondary-metrics").innerHTML = secondary.map(([label, value, note]) => metricCard(label, value, note)).join("");
    }

    function renderPhase1Status(status) {
      const container = document.getElementById("phase1-status");
      const allComplete = status.complete ? "All in-scope functions are complete." : "Some Phase 1 items remain open.";
      const summary = `<div class="card" style="margin-bottom: 8px; min-height: auto;">
        <div class="metric-label">Phase 1</div>
        <div class="metric-value" style="font-size: 1.7rem;">${status.complete ? "Complete" : "In progress"}</div>
        <div class="metric-note">${allComplete}</div>
      </div>`;
      const items = status.items.map((item) => `
        <div class="status-item">
          <div class="status-pill ${item.complete ? "" : "no"}">${item.complete ? "✓" : "!"}</div>
          <div class="status-copy">
            <strong>${item.label}</strong>
            <div class="small">${item.evidence}</div>
          </div>
        </div>
      `).join("");
      container.innerHTML = summary + items;
    }

    function renderHoldings(report) {
      const topHoldings = report.top_holdings || [];
      document.getElementById("holdings-table").innerHTML = topHoldings.map((row) => `
        <tr>
          <td>${row.ticker}</td>
          <td>${row.asset_class}</td>
          <td>${money.format(row.market_value)}</td>
          <td>${percentage.format(row.weight)}</td>
        </tr>
      `).join("");

      const weights = report.exposures_by_ticker || {};
      const sorted = Object.entries(weights).sort((a, b) => b[1] - a[1]);
      Plotly.newPlot("holdings-chart", [{
        type: "bar",
        orientation: "h",
        x: sorted.map(([, weight]) => weight),
        y: sorted.map(([ticker]) => ticker),
        marker: { color: "#67e8f9" },
        hovertemplate: "%{y}: %{x:.2%}<extra></extra>",
      }], {
        margin: { l: 80, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { tickformat: ".0%", gridcolor: "rgba(148,163,184,0.12)" },
        yaxis: { automargin: true },
        font: { color: "#e5eefb" },
      }, { displayModeBar: false, responsive: true });

      const warningList = document.getElementById("warning-list");
      warningList.innerHTML = (report.warnings || []).map((warning) => `<div class="warning">${warning}</div>`).join("");
      if ((report.warnings || []).length === 0) {
        warningList.innerHTML = `<div class="small">No current concentration or VaR threshold warnings.</div>`;
      }
    }

    function renderCharts(report) {
      const portfolio = normalizeSeries(report.portfolio_value_series || [], "value");
      const benchmark = normalizeSeries(report.benchmark_value_series || [], "value");
      const drawdown = report.drawdown_series || [];
      const drawdownX = drawdown.map((point) => point.date);
      const drawdownY = drawdown.map((point) => Number(point.drawdown));

      Plotly.newPlot("value-chart", [
        { x: portfolio.x, y: portfolio.y, type: "scatter", mode: "lines", name: report.portfolio_name, line: { color: "#67e8f9", width: 3 } },
        { x: benchmark.x, y: benchmark.y, type: "scatter", mode: "lines", name: "Benchmark", line: { color: "#f59e0b", width: 2, dash: "dot" } },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { title: "Normalized to 100", gridcolor: "rgba(148,163,184,0.12)" },
        xaxis: { gridcolor: "rgba(148,163,184,0.12)" },
        legend: { orientation: "h" },
        font: { color: "#e5eefb" },
      }, { displayModeBar: false, responsive: true });

      Plotly.newPlot("drawdown-chart", [
        { x: drawdownX, y: drawdownY, type: "scatter", mode: "lines", fill: "tozeroy", name: "Drawdown", line: { color: "#fb7185", width: 2 } },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { tickformat: ".0%", range: [Math.min(...drawdownY, 0) * 1.1, 0.02], gridcolor: "rgba(148,163,184,0.12)" },
        xaxis: { gridcolor: "rgba(148,163,184,0.12)" },
        font: { color: "#e5eefb" },
      }, { displayModeBar: false, responsive: true });

      const correlation = report.correlation_matrix || {};
      const labels = Object.keys(correlation);
      const z = labels.map((row) => labels.map((col) => correlation[row][col] ?? 0));
      Plotly.newPlot("correlation-chart", [{
        type: "heatmap",
        x: labels,
        y: labels,
        z,
        zmin: -1,
        zmax: 1,
        colorscale: [
          [0, "#1e1b4b"],
          [0.5, "#0f172a"],
          [1, "#67e8f9"],
        ],
        hovertemplate: "%{y} vs %{x}: %{z:.2f}<extra></extra>",
      }], {
        margin: { l: 60, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#e5eefb" },
      }, { displayModeBar: false, responsive: true });
    }

    async function loadPortfolios() {
      const response = await fetch("/api/portfolios");
      const payload = await response.json();
      state.portfolios = payload.portfolios || [];
      portfolioSelect.innerHTML = state.portfolios.map((portfolio) => `
        <option value="${portfolio.portfolio_id}">${portfolio.portfolio_name} - ${portfolio.strategy_style}</option>
      `).join("");
      if (state.portfolios.length > 0) {
        state.currentPortfolioId = state.portfolios[0].portfolio_id;
        portfolioSelect.value = state.currentPortfolioId;
        updateDescription();
      }
    }

    async function loadPhase1Status() {
      const response = await fetch("/api/phase1/status");
      state.phase1Status = await response.json();
      renderPhase1Status(state.phase1Status);
      sidebarPhaseStatus.textContent = state.phase1Status.complete ? "Complete" : "In progress";
    }

    function updateDescription() {
      const selected = state.portfolios.find((portfolio) => portfolio.portfolio_id === portfolioSelect.value);
      portfolioDescription.textContent = selected ? selected.objective : "";
      sidebarPortfolioNote.textContent = selected ? selected.objective : "Strategy objective and market mode will appear here.";
      sidebarPortfolioName.textContent = selected ? selected.portfolio_name : "Loading...";
    }

    async function loadReport() {
      state.currentPortfolioId = portfolioSelect.value;
      state.useDemoData = dataMode.value === "true";
      const params = new URLSearchParams({ portfolio_id: state.currentPortfolioId, use_demo_data: String(state.useDemoData) });
      const response = await fetch(`/api/risk/report?${params.toString()}`);
      const report = await response.json();
      renderMetrics(report);
      renderCharts(report);
      renderHoldings(report);
      updateDescription();
      updateSidebar(report);
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      document.querySelector('a[href="#overview"]').classList.add("active");
    }

    refreshButton.addEventListener("click", loadReport);
    portfolioSelect.addEventListener("change", loadReport);
    dataMode.addEventListener("change", loadReport);
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach((navItem) => navItem.classList.remove("active"));
        item.classList.add("active");
      });
    });

    Promise.all([loadPortfolios(), loadPhase1Status()])
      .then(loadReport)
      .catch((error) => {
        console.error(error);
        document.body.insertAdjacentHTML("afterbegin", `<div style="padding:16px; color:#fb7185;">Failed to load dashboard data.</div>`);
      });
  </script>
</body>
</html>"""