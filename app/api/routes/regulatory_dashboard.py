from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["regulatory-intelligence-page"])


@router.get("/regulatory-intelligence", response_class=HTMLResponse)
def regulatory_intelligence_dashboard() -> HTMLResponse:
    return HTMLResponse(_regulatory_html())


def _regulatory_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="view-transition" content="same-origin" />
  <title>Regulatory Intelligence | Risk Advisor Copilot</title>
  <script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.7/dist/purify.min.js"></script>
  <style>
    @view-transition { navigation: auto; }
    :root {
      --bg: #030303; --panel: #0b0c0d; --panel-2: #121416; --panel-3: #191c1e;
      --line: #292c2f; --steel: #34393d; --steel-bright: #687075;
      --text: #e8eaec; --muted: #94999d; --accent: #c7c9cc;
      --blue: #2962ff; --good: #78a783; --amber: #d7a449; --bad: #d85a5a;
      --font-ui: "IBM Plex Sans", "Segoe UI", sans-serif;
      --font-mono: "IBM Plex Mono", "Cascadia Mono", monospace;
      --font-editorial: Georgia, "Times New Roman", serif;
      --shadow: 0 12px 30px rgba(0,0,0,.36), inset 0 1px 0 rgba(255,255,255,.035);
      --inset: inset 0 1px 4px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.025);
    }
    * { box-sizing: border-box; }
    html { background: var(--bg); scroll-behavior: smooth; }
    body { margin: 0; min-height: 100vh; color: var(--text); background: radial-gradient(circle at 72% 5%, rgba(41,98,255,.08), transparent 25%), linear-gradient(180deg, #08090a, #030303 55%); font-family: var(--font-ui); }
    body::before { content: ""; position: fixed; inset: 0; pointer-events: none; background: repeating-linear-gradient(135deg, rgba(255,255,255,.018) 0 1px, transparent 1px 5px); opacity: .5; }
    a { color: inherit; text-decoration: none; }
    button, select { font: inherit; }
    button { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 38px; padding: 9px 13px; border: 1px solid #d5d7da; border-radius: 3px; color: #0b0c0d; background: linear-gradient(180deg, #f0f1f2, #a9adb2); box-shadow: var(--inset); cursor: pointer; }
    button:hover:not(:disabled) { background: linear-gradient(180deg, #fff, #c4c7ca); transform: translateY(-1px); }
    button:disabled { cursor: not-allowed; color: #73777a; border-color: #303438; background: #17191b; }
    button.secondary { color: var(--text); border-color: var(--steel); background: #111315; }
    button svg { width: 16px; height: 16px; }
    .shell { position: relative; display: grid; grid-template-columns: 286px minmax(0, 1fr); min-height: 100vh; }
    .sidebar { position: sticky; top: 0; align-self: start; min-height: 100vh; padding: 20px 16px; border-right: 1px solid var(--steel); background: linear-gradient(180deg, #101112, #080809); box-shadow: 8px 0 24px rgba(0,0,0,.26); }
    .brand { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
    .brand-mark { position: relative; width: 42px; height: 42px; border: 1px solid #50585d; border-radius: 3px; background: linear-gradient(145deg, #444b4f, #171a1c 52%, #070808); box-shadow: var(--inset); }
    .brand-mark::after { content: ""; position: absolute; inset: 10px; border: 1px solid var(--accent); background: #111314; }
    .brand strong { display: block; font-size: 16px; text-transform: uppercase; }
    .brand span { color: var(--muted); font-size: 12px; }
    .side-section { margin-bottom: 12px; padding: 14px; border: 1px solid var(--line); border-radius: 5px; background: linear-gradient(180deg, #111213, #0a0b0c); box-shadow: var(--inset); }
    .side-title { margin-bottom: 10px; color: var(--muted); font: 10px var(--font-mono); letter-spacing: .13em; text-transform: uppercase; }
    .nav-list { display: grid; gap: 4px; }
    .nav-item { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px; border: 1px solid transparent; border-radius: 3px; }
    .nav-item small { color: var(--muted); }
    .nav-item:hover, .nav-item.active { border-color: rgba(199,201,204,.22); background: linear-gradient(90deg, rgba(199,201,204,.065), transparent); transform: translateX(1px); }
    .coverage-list { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
    .coverage-list span { padding: 7px; border-left: 2px solid var(--steel-bright); color: var(--muted); background: #0d0f10; font: 11px var(--font-mono); }
    .content { min-width: 0; padding: clamp(12px, 2vw, 24px); }
    .hero { position: relative; min-height: 178px; margin-bottom: 12px; padding: 25px 27px; overflow: hidden; border: 1px solid var(--steel); border-left: 4px solid var(--accent); border-radius: 7px; background: linear-gradient(105deg, rgba(255,255,255,.025), transparent 58%), repeating-linear-gradient(135deg, rgba(255,255,255,.014) 0 1px, transparent 1px 6px), linear-gradient(180deg, #191d20, #101214); box-shadow: var(--shadow); animation: enter .35s ease both; }
    .hero::after { content: "REGULATORY INTELLIGENCE / SOURCE-GROUNDED / SAVED HISTORY"; position: absolute; right: 24px; bottom: 18px; color: #687075; font: 10px var(--font-mono); letter-spacing: .14em; }
    .eyebrow { margin: 0 0 9px; color: var(--accent); font: 11px var(--font-mono); letter-spacing: .12em; text-transform: uppercase; }
    h1 { max-width: 920px; margin: 0; font-size: clamp(30px, 4vw, 44px); line-height: 1.02; letter-spacing: 0; text-transform: uppercase; }
    .subtitle { max-width: 760px; margin-top: 12px; color: var(--muted); line-height: 1.5; }
    .toolbar { position: sticky; top: 10px; z-index: 5; display: flex; flex-wrap: wrap; align-items: end; gap: 9px; margin-bottom: 12px; padding: 12px; border: 1px solid var(--line); border-radius: 5px; background: rgba(11,12,13,.94); box-shadow: var(--shadow); }
    .field { display: grid; gap: 5px; min-width: 145px; }
    .field label { color: var(--muted); font: 10px var(--font-mono); letter-spacing: .08em; text-transform: uppercase; }
    select { min-height: 38px; padding: 8px 28px 8px 10px; color: var(--text); border: 1px solid var(--steel); border-radius: 3px; background: #0d0f10; }
    .toolbar-actions { display: flex; gap: 8px; margin-left: auto; }
    .status-line { flex-basis: 100%; min-height: 17px; color: var(--muted); font: 11px var(--font-mono); }
    .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; margin-bottom: 12px; overflow: hidden; border: 1px solid var(--line); border-radius: 5px; background: var(--line); }
    .metric { min-height: 88px; padding: 14px; background: linear-gradient(180deg, #121416, #0c0e0f); }
    .metric span { color: var(--muted); font: 10px var(--font-mono); text-transform: uppercase; }
    .metric strong { display: block; margin-top: 8px; font: 700 27px var(--font-mono); }
    .workspace { --feed-width: 65%; display: grid; grid-template-columns: minmax(360px, var(--feed-width)) 12px minmax(330px, 1fr); align-items: start; }
    .workspace-divider { position: relative; align-self: stretch; min-height: 100%; cursor: col-resize; touch-action: none; outline: none; }
    .workspace-divider::before { content: ""; position: absolute; top: 0; bottom: 0; left: 5px; width: 2px; background: var(--steel); transition: background .15s ease, box-shadow .15s ease; }
    .workspace-divider:hover::before, .workspace-divider:focus-visible::before, .workspace.resizing .workspace-divider::before { background: var(--accent); box-shadow: 0 0 8px rgba(199,201,204,.34); }
    .workspace.resizing { cursor: col-resize; user-select: none; }
    .panel { border: 1px solid var(--line); border-radius: 7px; background: linear-gradient(180deg, rgba(255,255,255,.018), transparent 32%), linear-gradient(180deg, var(--panel-2), var(--panel)); box-shadow: var(--shadow); }
    .panel-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 18px; border-bottom: 1px solid var(--line); }
    .panel-head h2 { margin: 0; font: 700 15px var(--font-mono); text-transform: uppercase; }
    .panel-head small { color: var(--muted); font: 11px var(--font-mono); }
    .feed { display: grid; }
    .update { position: relative; display: grid; grid-template-columns: 112px minmax(0, 1fr); gap: 18px; padding: 20px 18px; border-bottom: 1px solid var(--line); animation: enter .3s ease both; }
    .update:last-child { border-bottom: 0; }
    .update:hover { background: rgba(255,255,255,.018); }
    .update-meta { color: var(--muted); font: 10px/1.6 var(--font-mono); text-transform: uppercase; }
    .impact { display: inline-block; margin-top: 8px; padding: 3px 6px; border: 1px solid var(--steel); border-radius: 2px; color: var(--text); }
    .impact.Critical { color: #ffaaaa; border-color: var(--bad); }
    .impact.High { color: #f0c779; border-color: var(--amber); }
    .impact.Medium { color: #a9bfe9; border-color: #5874aa; }
    .update h3 { margin: 0 0 8px; font-size: 19px; line-height: 1.25; }
    .update p { margin: 0 0 10px; color: #b9bdc0; line-height: 1.55; }
    .portfolio-note { padding-left: 10px; border-left: 2px solid var(--good); font-size: 13px; }
    .portfolio-note.watch { border-left-color: var(--steel-bright); }
    .source { display: inline-flex; align-items: center; gap: 6px; color: #9fb9ff; font-size: 12px; }
    .source:hover { text-decoration: underline; }
    .newsletter-panel { position: sticky; top: 86px; }
    .newsletter-controls { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px; padding: 14px 18px; border-bottom: 1px solid var(--line); }
    .newsletter-controls select { width: 100%; }
    .print-button { min-height: 34px; padding: 7px 10px; }
    .paper { min-height: 420px; padding: 27px 25px; color: #1a1a19; background: #f1f0eb; }
    .paper .masthead { padding-bottom: 13px; border-bottom: 4px double #222; text-align: center; }
    .paper .masthead span { font: 10px var(--font-mono); letter-spacing: .15em; text-transform: uppercase; }
    .paper h2.issue-title { margin: 17px 0 7px; font: 700 29px/1.05 var(--font-editorial); }
    .paper .dek { margin: 0 0 17px; color: #555; font: italic 15px/1.4 var(--font-editorial); }
    .article-body { font: 15px/1.58 var(--font-editorial); }
    .article-body h2 { margin: 25px 0 8px; padding-top: 9px; border-top: 1px solid #999; font-size: 20px; }
    .article-body h3 { margin: 12px 0 4px; font-size: 17px; }
    .article-body p { margin: 6px 0 12px; }
    .article-body .kicker, .article-body .source-line { color: #555; font: 10px var(--font-mono); text-transform: uppercase; }
    .article-body a { color: #173b89; text-decoration: underline; }
    .disclaimer { padding: 12px 18px; color: var(--muted); border-top: 1px solid var(--line); font: 10px/1.5 var(--font-mono); }
    .empty { padding: 40px 18px; color: var(--muted); text-align: center; }
    @keyframes enter { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
    @media (max-width: 1180px) { .shell { grid-template-columns: 1fr; } .sidebar { position: relative; min-height: auto; } .workspace { grid-template-columns: 1fr; gap: 12px; } .workspace-divider { display: none; } .newsletter-panel { position: static; } }
    @media (max-width: 700px) { .content { padding: 10px; } .hero { padding: 20px 16px; } .hero::after { display: none; } .toolbar-actions { width: 100%; margin-left: 0; } .toolbar-actions button { flex: 1; } .metrics { grid-template-columns: 1fr 1fr; } .update { grid-template-columns: 1fr; gap: 8px; } }
    @media print {
      @page { margin: 0; }
      body { color: #1a1a19; background: #fff; }
      body::before, .shell > .sidebar, .content > :not(.workspace), .workspace > :not(.newsletter-panel), .newsletter-panel > :not(.paper) { display: none !important; }
      .content, .workspace, .newsletter-panel, .paper { display: block !important; }
      .content, .workspace { padding: 0; margin: 0; }
      .newsletter-panel { border: 0; box-shadow: none; }
      .paper { min-height: auto; padding: 16mm; background: #fff; }
    }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; } }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand"><div class="brand-mark"></div><div><strong>Risk Advisor</strong><span>In-house risk dashboard</span></div></div>
      <div class="side-section"><div class="side-title">Navigation</div><div class="nav-list">
        <a class="nav-item" href="/dashboard"><span>Risk dashboard</span><small>Portfolio analytics</small></a>
        <a class="nav-item active" href="/regulatory-intelligence"><span>Regulatory intel</span><small>Capital markets</small></a>
      </div></div>
      <div class="side-section"><div class="side-title">Launch coverage</div><div class="coverage-list"><span>HK / SFC</span><span>HK / HKMA</span><span>GLOBAL</span><span>US</span><span>UK</span><span>SG / MAS</span></div></div>
      <div class="side-section"><div class="side-title">Weekly schedule</div><div style="color:var(--muted);font-size:12px;line-height:1.5">On-demand active<br />Scheduled weekly · reserved</div></div>
    </aside>
    <main class="content">
      <section class="hero"><p class="eyebrow">Risk Advisor Copilot / Regulatory Desk</p><h1>Capital Markets Intelligence</h1><div class="subtitle">Primary-source developments distilled for risk leadership, trading desks and compliance, with portfolio relevance made explicit.</div></section>
      <section class="toolbar" aria-label="Regulatory filters and actions">
        <div class="field"><label for="jurisdiction">Jurisdiction</label><select id="jurisdiction"><option value="">All jurisdictions</option><option>HK</option><option>Global</option><option>US</option><option>UK</option><option>SG</option></select></div>
        <div class="field"><label for="topic">Topic</label><select id="topic"><option value="">All capital topics</option><option>Market risk</option><option>Basel capital</option><option>Derivatives</option><option>Counterparty credit risk</option><option>AI risk</option></select></div>
        <div class="field"><label for="impact">Impact</label><select id="impact"><option value="">All ratings</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div>
        <div class="toolbar-actions"><button class="secondary" id="refresh-button"><i data-lucide="refresh-cw"></i><span>Update intelligence</span></button><button id="generate-button"><i data-lucide="newspaper"></i><span>Generate weekly issue</span></button></div>
        <div class="status-line" id="status">Loading saved intelligence…</div>
      </section>
      <section class="metrics"><div class="metric"><span>Saved developments</span><strong id="total-count">—</strong></div><div class="metric"><span>High / critical</span><strong id="high-count">—</strong></div><div class="metric"><span>Portfolio related</span><strong id="portfolio-count">—</strong></div><div class="metric"><span>Official sources</span><strong id="official-rate">—</strong></div></section>
      <div class="workspace" id="regulatory-workspace">
        <section class="panel"><div class="panel-head"><h2>Regulatory signal feed</h2><small id="feed-count">0 records</small></div><div class="feed" id="feed"></div></section>
        <div class="workspace-divider" id="workspace-divider" role="separator" aria-label="Resize regulatory signal feed and weekly risk ledger" aria-orientation="vertical" aria-valuemin="40" aria-valuemax="70" aria-valuenow="65" tabindex="0"></div>
        <section class="panel newsletter-panel"><div class="panel-head"><h2>Weekly risk ledger</h2><small>Saved issue history</small></div><div class="newsletter-controls"><select id="issue-select" aria-label="Saved newsletter issue"><option value="">No saved issues</option></select><button class="secondary print-button" id="print-button" type="button" title="Print newsletter" aria-label="Print newsletter"><i data-lucide="printer"></i><span>Print</span></button></div><div class="paper" id="paper"><div class="masthead"><span>Risk Advisor Intelligence</span></div><h2 class="issue-title">Generate the weekly issue</h2><p class="dek">The editorial briefing will be assembled from saved, source-vetted developments.</p><div class="article-body"><p>Use the generation control to create and save an on-demand issue for CROs, trading desks and compliance.</p></div></div><div class="disclaimer" id="disclaimer">AI-generated regulatory intelligence may be incomplete or incorrect. Verify against primary sources. Not legal advice.</div></section>
      </div>
    </main>
  </div>
  <script>
    const state = { updates: [], issues: [] };
    const feed = document.getElementById("feed");
    const statusLine = document.getElementById("status");
    const workspace = document.getElementById("regulatory-workspace");
    const workspaceDivider = document.getElementById("workspace-divider");
    const clean = (value) => String(value ?? "");
    const formatDate = (value) => new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));

    function clamp(value, minimum, maximum) { return Math.min(Math.max(value, minimum), maximum); }
    function setWorkspaceSplit(percent, persist = true) {
      const workspaceWidth = workspace.getBoundingClientRect().width;
      const maximumPercent = workspaceWidth ? Math.min(70, (workspaceWidth - 342) / workspaceWidth * 100) : 70;
      const nextPercent = clamp(percent, 40, Math.max(40, maximumPercent));
      workspace.style.setProperty("--feed-width", `${nextPercent}%`);
      workspaceDivider.setAttribute("aria-valuemax", String(Math.round(maximumPercent)));
      workspaceDivider.setAttribute("aria-valuenow", String(Math.round(nextPercent)));
      if (persist) sessionStorage.setItem("regulatoryWorkspaceSplit", String(nextPercent));
    }
    function startWorkspaceResize(event) {
      if (window.innerWidth <= 1180 || event.button !== 0) return;
      event.preventDefault(); workspace.classList.add("resizing"); workspaceDivider.setPointerCapture(event.pointerId);
      function moveWorkspaceResize(moveEvent) {
        const bounds = workspace.getBoundingClientRect();
        setWorkspaceSplit((moveEvent.clientX - bounds.left) / bounds.width * 100, false);
      }
      function stopWorkspaceResize() {
        workspace.classList.remove("resizing");
        sessionStorage.setItem("regulatoryWorkspaceSplit", workspaceDivider.getAttribute("aria-valuenow"));
        workspaceDivider.removeEventListener("pointermove", moveWorkspaceResize);
        workspaceDivider.removeEventListener("pointerup", stopWorkspaceResize);
        workspaceDivider.removeEventListener("pointercancel", stopWorkspaceResize);
      }
      workspaceDivider.addEventListener("pointermove", moveWorkspaceResize);
      workspaceDivider.addEventListener("pointerup", stopWorkspaceResize);
      workspaceDivider.addEventListener("pointercancel", stopWorkspaceResize);
    }
    function resizeWorkspaceWithKeyboard(event) {
      const current = Number(workspaceDivider.getAttribute("aria-valuenow"));
      const changes = { ArrowLeft: -2, ArrowRight: 2, Home: 40 - current, End: 70 - current };
      if (!(event.key in changes)) return;
      event.preventDefault(); setWorkspaceSplit(current + changes[event.key]);
    }
    function setBusy(button, busy, text) { button.disabled = busy; button.querySelector("span").textContent = text; }
    function sourceLink(update) {
      const link = document.createElement("a"); link.className = "source"; link.href = update.source.url; link.target = "_blank"; link.rel = "noopener noreferrer";
      const icon = document.createElement("i"); icon.setAttribute("data-lucide", "external-link"); link.append(icon, document.createTextNode(`${update.source.publisher} · ${update.source.source_tier}`)); return link;
    }
    function renderUpdates() {
      const jurisdiction = document.getElementById("jurisdiction").value;
      const topic = document.getElementById("topic").value.toLowerCase();
      const impact = document.getElementById("impact").value;
      const visible = state.updates.filter((item) => (!jurisdiction || item.jurisdiction === jurisdiction) && (!topic || item.topics.some((value) => value.toLowerCase().includes(topic))) && (!impact || item.impact_rating === impact));
      feed.replaceChildren(); document.getElementById("feed-count").textContent = `${visible.length} records`;
      if (!visible.length) { const empty = document.createElement("div"); empty.className = "empty"; empty.textContent = "No saved developments match these filters."; feed.append(empty); return; }
      visible.forEach((update) => {
        const row = document.createElement("article"); row.className = "update";
        const meta = document.createElement("div"); meta.className = "update-meta";
        const impactBadge = document.createElement("span"); impactBadge.className = `impact ${update.impact_rating}`; impactBadge.textContent = update.impact_rating;
        meta.append(document.createTextNode(`${formatDate(update.published_at)}\n${update.jurisdiction} / ${update.regulator}`), document.createElement("br"), impactBadge);
        meta.style.whiteSpace = "pre-line";
        const body = document.createElement("div"); const title = document.createElement("h3"); title.textContent = update.headline;
        const summary = document.createElement("p"); summary.textContent = update.summary;
        const note = document.createElement("p"); note.className = `portfolio-note${update.portfolio_relevance ? "" : " watch"}`; note.textContent = `${update.portfolio_relevance ? "Portfolio related" : "Watch item"}: ${update.portfolio_impact}`;
        body.append(title, summary, note, sourceLink(update)); row.append(meta, body); feed.append(row);
      });
      lucide.createIcons();
    }
    function renderMetrics() {
      document.getElementById("total-count").textContent = state.updates.length;
      document.getElementById("high-count").textContent = state.updates.filter((item) => ["Critical", "High"].includes(item.impact_rating)).length;
      document.getElementById("portfolio-count").textContent = state.updates.filter((item) => item.portfolio_relevance).length;
      const official = state.updates.filter((item) => item.source.source_tier === "official").length;
      document.getElementById("official-rate").textContent = state.updates.length ? `${Math.round(official / state.updates.length * 100)}%` : "—";
    }
    async function loadUpdates() { const response = await fetch("/api/regulatory/updates"); if (!response.ok) throw new Error("Unable to load regulatory updates"); state.updates = await response.json(); renderMetrics(); renderUpdates(); statusLine.textContent = `Loaded ${state.updates.length} saved developments.`; }
    async function loadIssues(selectedId = "") { const response = await fetch("/api/regulatory/newsletters"); if (!response.ok) throw new Error("Unable to load issue history"); state.issues = await response.json(); const select = document.getElementById("issue-select"); select.replaceChildren(); if (!state.issues.length) { select.add(new Option("No saved issues", "")); return; } state.issues.forEach((issue) => select.add(new Option(`${formatDate(issue.generated_at)} · ${issue.title}`, issue.id))); select.value = selectedId || state.issues[0].id; renderIssue(select.value); }
    function renderIssue(id) { const issue = state.issues.find((item) => item.id === id); if (!issue) return; const paper = document.getElementById("paper"); paper.replaceChildren(); const masthead = document.createElement("div"); masthead.className = "masthead"; masthead.innerHTML = `<span>Risk Advisor Intelligence · ${formatDate(issue.generated_at)}</span>`; const title = document.createElement("h2"); title.className = "issue-title"; title.textContent = issue.title; const dek = document.createElement("p"); dek.className = "dek"; dek.textContent = issue.dek; const body = document.createElement("div"); body.className = "article-body"; body.innerHTML = DOMPurify.sanitize(issue.body_html, { ALLOWED_TAGS: ["p", "h2", "h3", "article", "strong", "a", "blockquote"], ALLOWED_ATTR: ["href", "target", "rel", "class"] }); paper.append(masthead, title, dek, body); document.getElementById("disclaimer").textContent = issue.disclaimer; }
    function printNewsletter() {
      const originalTitle = document.title;
      const restoreTitle = () => { document.title = originalTitle; };
      document.title = "";
      window.addEventListener("afterprint", restoreTitle, { once: true });
      window.print();
    }
    async function refresh() { const button = document.getElementById("refresh-button"); setBusy(button, true, "Searching trusted sources…"); statusLine.textContent = "Requesting official-first web search…"; try { const response = await fetch("/api/regulatory/refresh", { method: "POST" }); const result = await response.json(); if (!response.ok) throw new Error(result.detail || "Refresh failed"); state.updates = result.updates; renderMetrics(); renderUpdates(); statusLine.textContent = result.warning || `Refresh complete · ${result.updates_added} new developments saved.`; } catch (error) { statusLine.textContent = clean(error.message); } finally { setBusy(button, false, "Update intelligence"); lucide.createIcons(); } }
    async function generateIssue() { const button = document.getElementById("generate-button"); setBusy(button, true, "Writing issue…"); statusLine.textContent = "Building a grounded weekly issue from saved developments…"; try { const response = await fetch("/api/regulatory/newsletters/generate", { method: "POST" }); const issue = await response.json(); if (!response.ok) throw new Error(issue.detail || "Generation failed"); await loadIssues(issue.id); statusLine.textContent = `Issue saved · ${issue.generation_mode}.`; } catch (error) { statusLine.textContent = clean(error.message); } finally { setBusy(button, false, "Generate weekly issue"); lucide.createIcons(); } }
    ["jurisdiction", "topic", "impact"].forEach((id) => document.getElementById(id).addEventListener("change", renderUpdates));
    document.getElementById("refresh-button").addEventListener("click", refresh);
    document.getElementById("generate-button").addEventListener("click", generateIssue);
    document.getElementById("issue-select").addEventListener("change", (event) => renderIssue(event.target.value));
    document.getElementById("print-button").addEventListener("click", printNewsletter);
    workspaceDivider.addEventListener("pointerdown", startWorkspaceResize);
    workspaceDivider.addEventListener("keydown", resizeWorkspaceWithKeyboard);
    setWorkspaceSplit(Number(sessionStorage.getItem("regulatoryWorkspaceSplit")) || 65, false);
    window.addEventListener("resize", () => setWorkspaceSplit(Number(workspaceDivider.getAttribute("aria-valuenow")), false));
    Promise.all([loadUpdates(), loadIssues()]).catch((error) => { statusLine.textContent = clean(error.message); });
    lucide.createIcons();
  </script>
</body>
</html>"""