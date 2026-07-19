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
  <script src="https://cdn.jsdelivr.net/npm/marked@14.1.2/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.7/dist/purify.min.js"></script>
  <style>
    :root {
      --bg: #030712;
      --panel: rgba(6, 11, 24, 0.76);
      --panel-2: rgba(11, 18, 38, 0.84);
      --panel-3: rgba(15, 23, 42, 0.92);
      --line: rgba(125, 211, 252, 0.18);
      --line-hot: rgba(45, 212, 191, 0.44);
      --text: #eef7ff;
      --muted: #95a9c6;
      --accent: #38bdf8;
      --accent-2: #2dd4bf;
      --accent-3: #f59e0b;
      --good: #34d399;
      --bad: #fb7185;
      --violet: #a78bfa;
      --shadow: 0 32px 90px rgba(0, 0, 0, 0.48);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.18), transparent 28%),
        radial-gradient(circle at 80% 8%, rgba(45, 212, 191, 0.14), transparent 28%),
        radial-gradient(circle at 62% 84%, rgba(167, 139, 250, 0.11), transparent 30%),
        linear-gradient(180deg, #020617 0%, #030712 44%, #07111f 100%);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }
    body::before, body::after {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 0;
    }
    body::before {
      background:
        linear-gradient(rgba(125, 211, 252, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125, 211, 252, 0.035) 1px, transparent 1px);
      background-size: 44px 44px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.95), transparent 86%);
      animation: gridDrift 16s linear infinite;
    }
    body::after {
      background: linear-gradient(180deg, transparent, rgba(56, 189, 248, 0.05), transparent);
      mix-blend-mode: screen;
      animation: scanline 9s ease-in-out infinite;
    }
    @keyframes gridDrift {
      from { background-position: 0 0, 0 0; }
      to { background-position: 44px 44px, 44px 44px; }
    }
    @keyframes scanline {
      0%, 100% { transform: translateY(-55%); opacity: 0.18; }
      50% { transform: translateY(55%); opacity: 0.38; }
    }
    @keyframes pulseRing {
      0%, 100% { transform: scale(0.92); opacity: 0.35; }
      50% { transform: scale(1.04); opacity: 0.78; }
    }
    @keyframes floatIn {
      from { opacity: 0; transform: translateY(14px); }
      to { opacity: 1; transform: translateY(0); }
    }
    a { color: inherit; text-decoration: none; }
    .app-shell {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      min-height: 100vh;
      position: relative;
      z-index: 1;
    }
    .sidebar {
      position: sticky;
      top: 0;
      align-self: start;
      min-height: 100vh;
      padding: 24px 18px;
      border-right: 1px solid rgba(125, 211, 252, 0.16);
      background:
        linear-gradient(180deg, rgba(2, 6, 23, 0.86), rgba(8, 13, 29, 0.78)),
        linear-gradient(90deg, rgba(56, 189, 248, 0.08), transparent 42%);
      backdrop-filter: blur(22px);
      box-shadow: 22px 0 90px rgba(0, 0, 0, 0.34);
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
      border-radius: 16px;
      position: relative;
      background:
        linear-gradient(135deg, rgba(255,255,255,0.86), rgba(255,255,255,0.08)),
        conic-gradient(from 160deg, #38bdf8, #2dd4bf, #a78bfa, #38bdf8);
      box-shadow: 0 0 34px rgba(56, 189, 248, 0.34), 0 0 0 1px rgba(255,255,255,0.12) inset;
    }
    .brand-mark::after {
      content: "";
      position: absolute;
      inset: 10px;
      border-radius: 10px;
      border: 1px solid rgba(3, 7, 18, 0.72);
      background: rgba(3, 7, 18, 0.68);
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
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.62), rgba(2, 6, 23, 0.42));
      margin-bottom: 14px;
      box-shadow: 0 18px 38px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255,255,255,0.04);
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
      background: rgba(125, 211, 252, 0.025);
      color: var(--text);
      transition: 180ms ease;
    }
    .nav-item:hover, .nav-item.active {
      border-color: rgba(103, 232, 249, 0.22);
      background: linear-gradient(90deg, rgba(56, 189, 248, 0.16), rgba(45, 212, 191, 0.06));
      transform: translateX(2px);
      box-shadow: 0 0 24px rgba(56, 189, 248, 0.14);
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
      border: 1px solid rgba(52, 211, 153, 0.28);
      background: rgba(52, 211, 153, 0.10);
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
      padding: 30px;
    }
    .hero {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: center;
      margin-bottom: 22px;
      min-height: 260px;
      position: relative;
      overflow: hidden;
      padding: 34px;
      border: 1px solid rgba(125, 211, 252, 0.16);
      border-radius: 30px;
      background:
        linear-gradient(100deg, rgba(8, 13, 29, 0.82), rgba(8, 47, 73, 0.22) 62%, rgba(20, 184, 166, 0.10)),
        radial-gradient(circle at 76% 46%, rgba(56, 189, 248, 0.16), transparent 30%);
      box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .hero::before {
      content: "";
      position: absolute;
      width: 390px;
      height: 390px;
      right: -90px;
      top: -78px;
      border-radius: 999px;
      border: 1px solid rgba(125, 211, 252, 0.18);
      background:
        repeating-radial-gradient(circle, rgba(125, 211, 252, 0.13) 0 1px, transparent 1px 24px),
        conic-gradient(from 0deg, rgba(56, 189, 248, 0.0), rgba(56, 189, 248, 0.26), rgba(45, 212, 191, 0.0));
      filter: drop-shadow(0 0 46px rgba(56, 189, 248, 0.22));
      animation: pulseRing 5s ease-in-out infinite;
    }
    .hero::after {
      content: "RISK OPS / LIVE ANALYTICS / PHASE ONE";
      position: absolute;
      right: 28px;
      bottom: 22px;
      color: rgba(226, 246, 255, 0.28);
      font-size: 11px;
      letter-spacing: 0.28em;
      text-transform: uppercase;
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
      max-width: 840px;
      font-size: clamp(2.4rem, 5.2vw, 5.8rem);
      line-height: 0.96;
      letter-spacing: -0.04em;
      text-shadow: 0 0 34px rgba(56, 189, 248, 0.16);
    }
    .subtitle {
      color: var(--muted);
      max-width: 860px;
      margin-top: 10px;
      font-size: 15px;
      line-height: 1.65;
    }
    .hero-telemetry {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 22px;
      max-width: 860px;
    }
    .telemetry-chip {
      border: 1px solid rgba(125, 211, 252, 0.20);
      border-radius: 999px;
      padding: 9px 12px;
      background: rgba(3, 7, 18, 0.44);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 0 22px rgba(56, 189, 248, 0.06);
      color: #dff7ff;
      font-size: 12px;
    }
    .telemetry-chip span {
      color: var(--accent-2);
      font-weight: 800;
      margin-right: 6px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .hero-orbit {
      width: min(30vw, 360px);
      min-width: 260px;
      aspect-ratio: 1;
      position: relative;
      border-radius: 999px;
      display: grid;
      place-items: center;
      isolation: isolate;
    }
    .hero-orbit::before,
    .hero-orbit::after {
      content: "";
      position: absolute;
      inset: 16%;
      border-radius: 999px;
      border: 1px solid rgba(125, 211, 252, 0.22);
      box-shadow: 0 0 40px rgba(56, 189, 248, 0.14), inset 0 0 34px rgba(45, 212, 191, 0.06);
    }
    .hero-orbit::after {
      inset: 28%;
      border-style: dashed;
      animation: pulseRing 3.8s ease-in-out infinite;
    }
    .orbital-core {
      width: 46%;
      aspect-ratio: 1;
      border-radius: 999px;
      display: grid;
      place-items: center;
      background:
        radial-gradient(circle, rgba(238, 247, 255, 0.86), rgba(56, 189, 248, 0.24) 28%, rgba(3, 7, 18, 0.18) 62%),
        conic-gradient(from 120deg, #38bdf8, #2dd4bf, #a78bfa, #38bdf8);
      color: #020617;
      font-weight: 900;
      letter-spacing: 0.08em;
      box-shadow: 0 0 70px rgba(56, 189, 248, 0.38);
      z-index: 1;
    }
    .command-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .command-tile {
      border: 1px solid rgba(125, 211, 252, 0.15);
      border-radius: 18px;
      padding: 14px;
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.62), rgba(2, 6, 23, 0.46));
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 16px 34px rgba(0,0,0,0.20);
    }
    .command-tile strong {
      display: block;
      font-size: 12px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 6px;
    }
    .command-tile span {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .controls, .card, .panel {
      border: 1px solid var(--line);
      background:
        linear-gradient(180deg, rgba(8, 13, 29, 0.86), rgba(2, 6, 23, 0.70)),
        linear-gradient(135deg, rgba(56, 189, 248, 0.06), transparent 42%, rgba(45, 212, 191, 0.05));
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }
    .controls {
      display: grid;
      grid-template-columns: 1.5fr 1fr 1fr auto;
      gap: 14px;
      padding: 16px;
      border-radius: 20px;
      margin-bottom: 18px;
      align-items: end;
      position: sticky;
      top: 18px;
      z-index: 4;
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
      background: rgba(3, 7, 18, 0.62);
      color: var(--text);
      padding: 12px 14px;
      font-size: 14px;
    }
    button {
      cursor: pointer;
      background: linear-gradient(135deg, #38bdf8, #2dd4bf 54%, #bef264);
      color: #04111a;
      font-weight: 800;
      min-width: 120px;
      box-shadow: 0 0 34px rgba(45, 212, 191, 0.22);
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
      position: relative;
      overflow: hidden;
      animation: floatIn 420ms ease both;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(120deg, rgba(125, 211, 252, 0.16), transparent 28%, transparent 70%, rgba(45, 212, 191, 0.12));
      opacity: 0.5;
      pointer-events: none;
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
      position: relative;
      z-index: 1;
    }
    .metric-note {
      color: var(--muted);
      margin-top: 8px;
      font-size: 13px;
      line-height: 1.45;
      position: relative;
      z-index: 1;
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
      position: relative;
      overflow: hidden;
    }
    .panel::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: linear-gradient(90deg, rgba(56, 189, 248, 0.11), transparent 18%, transparent 82%, rgba(45, 212, 191, 0.09));
      pointer-events: none;
    }
    .panel > * { position: relative; z-index: 1; }
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
    .floating-copilot {
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 20;
      display: grid;
      justify-items: end;
      gap: 14px;
      pointer-events: none;
    }
    .copilot-launcher {
      pointer-events: auto;
      width: 72px;
      height: 72px;
      border: 1px solid rgba(103, 232, 249, 0.42);
      border-radius: 24px;
      display: grid;
      place-items: center;
      color: var(--text);
      background:
        radial-gradient(circle at 28% 18%, rgba(255, 255, 255, 0.28), transparent 30%),
        linear-gradient(135deg, rgba(56, 189, 248, 0.94), rgba(45, 212, 191, 0.82) 48%, rgba(167, 139, 250, 0.86));
      box-shadow: 0 20px 55px rgba(56, 189, 248, 0.30), 0 0 0 10px rgba(56, 189, 248, 0.07);
      cursor: pointer;
      transition: transform 180ms ease, box-shadow 180ms ease;
    }
    .copilot-launcher:hover {
      transform: translateY(-3px) scale(1.03);
      box-shadow: 0 26px 70px rgba(45, 212, 191, 0.34), 0 0 0 12px rgba(45, 212, 191, 0.08);
    }
    .copilot-launcher strong {
      font-size: 19px;
      letter-spacing: 0.08em;
      text-shadow: 0 1px 12px rgba(3, 7, 18, 0.44);
    }
    .copilot-pulse {
      position: absolute;
      right: 2px;
      top: 2px;
      width: 14px;
      height: 14px;
      border-radius: 999px;
      background: var(--good);
      box-shadow: 0 0 18px rgba(52, 211, 153, 0.9);
    }
    .copilot-window {
      pointer-events: auto;
      width: min(560px, calc(100vw - 44px));
      height: calc(100vh - 44px);
      max-height: calc(100vh - 44px);
      display: none;
      position: relative;
      grid-template-rows: auto minmax(180px, 1fr) auto auto;
      gap: 12px;
      border: 1px solid rgba(125, 211, 252, 0.24);
      border-radius: 24px;
      padding: 16px;
      background:
        linear-gradient(180deg, rgba(8, 13, 29, 0.96), rgba(2, 6, 23, 0.94)),
        radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.20), transparent 38%);
      box-shadow: 0 34px 100px rgba(0, 0, 0, 0.58), inset 0 1px 0 rgba(255,255,255,0.05);
      backdrop-filter: blur(24px);
      animation: floatIn 180ms ease both;
    }
    .copilot-window.resizing {
      user-select: none;
      transition: none;
    }
    .copilot-resize-handle {
      position: absolute;
      top: 8px;
      left: 8px;
      width: 20px;
      height: 20px;
      border-left: 2px solid rgba(125, 211, 252, 0.46);
      border-top: 2px solid rgba(125, 211, 252, 0.46);
      border-radius: 6px 0 0 0;
      cursor: nwse-resize;
      opacity: 0.72;
    }
    .copilot-resize-handle:hover {
      border-color: rgba(45, 212, 191, 0.82);
      opacity: 1;
    }
    .floating-copilot.open .copilot-window {
      display: grid;
    }
    .floating-copilot.open .copilot-launcher {
      display: none;
    }
    .copilot-header {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
    }
    .copilot-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .copilot-icon-button {
      width: 34px;
      height: 34px;
      border-radius: 12px;
      border: 1px solid rgba(125, 211, 252, 0.16);
      background: rgba(125, 211, 252, 0.05);
      color: var(--text);
      cursor: pointer;
      font-size: 18px;
      line-height: 1;
    }
    .copilot-minimize-button {
      display: grid;
      place-items: center;
      padding: 0 0 9px;
      font-size: 22px;
      font-weight: 800;
      color: var(--accent-2);
    }
    .copilot-icon-button:hover {
      border-color: rgba(45, 212, 191, 0.34);
      background: rgba(45, 212, 191, 0.10);
    }
    .copilot-status {
      border: 1px solid rgba(45, 212, 191, 0.24);
      border-radius: 999px;
      padding: 8px 11px;
      color: var(--accent-2);
      background: rgba(45, 212, 191, 0.08);
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    .chat-log {
      border: 1px solid rgba(125, 211, 252, 0.12);
      border-radius: 18px;
      background: rgba(3, 7, 18, 0.38);
      padding: 14px;
      overflow-y: auto;
      display: grid;
      align-content: start;
      gap: 12px;
      min-height: 260px;
    }
    .message {
      border-radius: 16px;
      padding: 13px 14px;
      max-width: 86%;
      line-height: 1.55;
      font-size: 14px;
      white-space: pre-wrap;
    }
    .message.markdown {
      white-space: normal;
    }
    .message.markdown p {
      margin: 0 0 10px;
    }
    .message.markdown p:last-child {
      margin-bottom: 0;
    }
    .message.markdown ul, .message.markdown ol {
      margin: 8px 0 10px 20px;
      padding: 0;
    }
    .message.markdown li {
      margin: 5px 0;
    }
    .message.markdown strong {
      color: #f8fbff;
    }
    .message.markdown code {
      border: 1px solid rgba(125, 211, 252, 0.16);
      border-radius: 8px;
      padding: 2px 5px;
      background: rgba(3, 7, 18, 0.54);
      color: #bae6fd;
      font-size: 0.92em;
    }
    .message.markdown pre {
      overflow-x: auto;
      border: 1px solid rgba(125, 211, 252, 0.16);
      border-radius: 12px;
      padding: 10px;
      background: rgba(3, 7, 18, 0.62);
    }
    .message.markdown pre code {
      border: 0;
      padding: 0;
      background: transparent;
    }
    .message.markdown blockquote {
      margin: 10px 0;
      padding-left: 12px;
      border-left: 3px solid rgba(45, 212, 191, 0.42);
      color: var(--muted);
    }
    .message.user {
      justify-self: end;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.20), rgba(45, 212, 191, 0.12));
      border: 1px solid rgba(125, 211, 252, 0.24);
    }
    .message.ai {
      justify-self: start;
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(2, 6, 23, 0.54));
      border: 1px solid rgba(167, 139, 250, 0.18);
      box-shadow: 0 0 34px rgba(167, 139, 250, 0.08);
    }
    .composer {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 12px;
      align-items: end;
    }
    textarea {
      width: 100%;
      min-height: 86px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(3, 7, 18, 0.62);
      color: var(--text);
      padding: 13px 14px;
      font: inherit;
      line-height: 1.5;
    }
    .prompt-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }
    .prompt-panel {
      display: grid;
      gap: 10px;
    }
    .prompt-panel.collapsed .prompt-grid {
      display: none;
    }
    .prompt-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .prompt-panel-title {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }
    .prompt-toggle {
      border: 1px solid rgba(125, 211, 252, 0.16);
      border-radius: 999px;
      padding: 7px 10px;
      background: rgba(125, 211, 252, 0.05);
      color: var(--text);
      cursor: pointer;
      font-size: 12px;
      font-weight: 800;
    }
    .prompt-toggle:hover {
      border-color: rgba(45, 212, 191, 0.34);
      background: rgba(45, 212, 191, 0.10);
    }
    .prompt-chip {
      text-align: left;
      border: 1px solid rgba(125, 211, 252, 0.14);
      border-radius: 16px;
      padding: 12px;
      background: rgba(125, 211, 252, 0.04);
      color: var(--text);
      cursor: pointer;
      font-size: 13px;
      line-height: 1.45;
    }
    .prompt-chip:hover {
      border-color: rgba(45, 212, 191, 0.34);
      background: rgba(45, 212, 191, 0.08);
    }
    .report-panel {
      display: grid;
      gap: 10px;
      border: 1px solid rgba(125, 211, 252, 0.12);
      border-radius: 16px;
      padding: 12px;
      background: rgba(125, 211, 252, 0.035);
    }
    .report-controls {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 0.8fr);
      gap: 8px;
    }
    .report-actions {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
    }
    .report-panel select, .report-panel input {
      width: 100%;
      border: 1px solid rgba(125, 211, 252, 0.14);
      border-radius: 12px;
      padding: 10px 11px;
      background: rgba(3, 7, 18, 0.62);
      color: var(--text);
      font: inherit;
      font-size: 13px;
    }
    .report-output {
      display: none;
      max-height: 220px;
      overflow-y: auto;
      border: 1px solid rgba(125, 211, 252, 0.12);
      border-radius: 14px;
      padding: 12px;
      background: rgba(3, 7, 18, 0.44);
      color: var(--text);
      font-size: 13px;
      line-height: 1.5;
    }
    .report-output.visible {
      display: block;
    }
    .report-output h1, .report-output h2, .report-output h3 {
      margin: 10px 0 6px;
      font-size: 14px;
    }
    .report-output ul, .report-output ol {
      margin: 8px 0 8px 18px;
      padding: 0;
    }
    .copilot-meta {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 12px;
    }
    .meta-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid rgba(125, 211, 252, 0.10);
      padding-bottom: 9px;
      color: var(--muted);
      font-size: 13px;
    }
    .meta-row strong {
      color: var(--text);
      text-align: right;
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
    .section-heading h3::before {
      content: "";
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 999px;
      margin-right: 8px;
      background: var(--accent-2);
      box-shadow: 0 0 18px rgba(45, 212, 191, 0.8);
      vertical-align: 1px;
    }
    .basel-report-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 100;
      overflow-y: auto;
      background: linear-gradient(180deg, rgba(255,255,255,0.015), transparent 180px), var(--bg);
      color: var(--text);
    }
    .basel-report-overlay.visible { display: block; }
    .basel-report-toolbar {
      position: sticky;
      top: 0;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 58px;
      padding: 10px 28px;
      color: var(--text);
      background: linear-gradient(90deg, #1b1f21, #111315);
      border-bottom: 3px solid var(--accent);
      box-shadow: var(--shadow-inset);
    }
    .basel-report-toolbar strong { font: 14px var(--font-mono); letter-spacing: 0; }
    .basel-toolbar-actions { display: flex; gap: 8px; }
    .basel-toolbar-actions button {
      min-height: 36px;
      padding: 8px 12px;
      border: 1px solid var(--steel-bright);
      border-radius: var(--radius-sm);
      color: var(--text);
      background: #0d0f10;
      cursor: pointer;
    }
    .basel-report-canvas {
      width: min(1420px, calc(100% - 40px));
      margin: 24px auto 48px;
    }
    .basel-report-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 24px;
      align-items: end;
      padding: 24px 28px;
      color: var(--text);
      background: repeating-linear-gradient(135deg, rgba(255,255,255,0.014) 0 1px, transparent 1px 6px), linear-gradient(180deg, #1b1f21, #111315);
      border-left: 6px solid var(--accent);
      box-shadow: var(--shadow);
    }
    .basel-report-kicker {
      margin-bottom: 8px;
      color: var(--accent);
      font-size: 11px;
      font: 800 11px var(--font-mono);
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }
    .basel-report-head h2 { margin: 0; font-size: 28px; letter-spacing: 0; }
    .basel-report-head p { margin: 8px 0 0; color: var(--muted); font-size: 13px; }
    .basel-scope-badge {
      max-width: 300px;
      padding: 10px 12px;
      border: 1px solid var(--steel-bright);
      border-radius: var(--radius-sm);
      color: var(--text);
      background: rgba(0,0,0,0.2);
      font-size: 11px;
      line-height: 1.45;
      text-align: right;
    }
    .basel-kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      border: 1px solid var(--steel);
      border-top: 0;
      background: linear-gradient(180deg, var(--panel-2), var(--panel));
      box-shadow: var(--shadow-inset);
    }
    .basel-kpi {
      min-width: 0;
      padding: 20px 22px;
      border-right: 1px solid var(--steel);
    }
    .basel-kpi:last-child { border-right: 0; }
    .basel-kpi span { display: block; color: var(--muted); font: 800 11px var(--font-mono); text-transform: uppercase; }
    .basel-kpi strong { display: block; margin-top: 7px; color: var(--text); font: 800 25px var(--font-mono); letter-spacing: 0; }
    .basel-dashboard-grid {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
      margin-top: 18px;
    }
    .basel-dashboard-section {
      min-width: 0;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      background: linear-gradient(180deg, rgba(255,255,255,0.018), transparent 32%), linear-gradient(180deg, var(--panel-2), var(--panel));
      box-shadow: var(--shadow);
    }
    .basel-dashboard-section.wide { grid-column: 1 / -1; }
    .basel-section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--accent);
    }
    .basel-section-title h3 { margin: 0; color: var(--text); font: 15px var(--font-mono); letter-spacing: 0; }
    .basel-section-title span { color: var(--muted); font-size: 11px; }
    .basel-stack-row {
      display: grid;
      grid-template-columns: 170px minmax(120px, 1fr) 110px;
      gap: 12px;
      align-items: center;
      margin: 13px 0;
      font-size: 12px;
    }
    .basel-stack-track { height: 12px; overflow: hidden; background: #0d0f10; box-shadow: var(--shadow-inset); }
    .basel-stack-fill { height: 100%; min-width: 2px; background: var(--accent); }
    .basel-stack-fill.placeholder { background: var(--steel-bright); }
    .basel-stack-value { font-weight: 800; text-align: right; }
    .basel-status-tag {
      display: inline-block;
      margin-left: 6px;
      padding: 2px 5px;
      border-radius: var(--radius-xs);
      color: #f1f2f3;
      background: rgba(199,201,204,0.13);
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .basel-metric-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .basel-metric-table th, .basel-metric-table td { padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: left; }
    .basel-metric-table th { color: var(--muted); font: 10px var(--font-mono); text-transform: uppercase; }
    .basel-metric-table td:nth-child(2) { font-weight: 800; text-align: right; }
    .basel-metric-table td:last-child { color: var(--muted); text-align: right; }
    .basel-classification {
      padding: 16px;
      border-left: 5px solid var(--accent);
      background: rgba(199,201,204,0.08);
    }
    .basel-classification.green { border-left-color: var(--good); background: rgba(120,167,131,0.1); }
    .basel-classification.yellow { border-left-color: var(--accent); }
    .basel-classification.red { border-left-color: var(--bad); background: rgba(216,90,90,0.1); }
    .basel-classification strong { display: block; margin-bottom: 5px; color: var(--text); }
    .basel-classification span { color: var(--muted); font-size: 12px; line-height: 1.5; }
    .basel-evidence-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .basel-evidence {
      padding: 14px;
      border: 1px solid var(--line);
      background: #0f1112;
      box-shadow: var(--shadow-inset);
    }
    .basel-evidence strong { display: block; color: var(--text); font: 12px var(--font-mono); }
    .basel-evidence code { display: block; margin: 7px 0; color: var(--muted); font-size: 11px; white-space: normal; }
    .basel-evidence b { color: var(--text); font: 800 18px var(--font-mono); }
    .basel-detail-list { margin: 0; padding-left: 18px; color: var(--muted); font-size: 12px; line-height: 1.6; }
    .basel-detail-list li { margin: 6px 0; color: var(--muted); }
    .basel-governance-meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
    .basel-governance-meta div { padding: 11px; background: #0d0f10; box-shadow: var(--shadow-inset); }
    .basel-governance-meta span { display: block; color: var(--muted); font: 800 9px var(--font-mono); text-transform: uppercase; }
    .basel-governance-meta strong { display: block; margin-top: 5px; color: var(--text); font-size: 12px; }
    .basel-report-footer { margin-top: 16px; color: var(--muted); font: 10px/1.5 var(--font-mono); }
    .stress-workbench {
      margin-top: 18px;
      padding: 24px;
      border-top: 3px solid var(--accent-3);
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(3, 7, 18, 0.72));
    }
    .stress-controls {
      display: grid;
      grid-template-columns: minmax(240px, 1fr) auto auto;
      gap: 10px;
      align-items: end;
      margin-top: 16px;
    }
    .stress-controls select {
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 11px;
      color: var(--text);
      background: rgba(3, 7, 18, 0.72);
    }
    .stress-status { color: var(--muted); font-size: 12px; }
    .stress-results { display: none; margin-top: 20px; }
    .stress-results.visible { display: block; }
    .stress-result-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
      padding: 16px 0;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }
    .stress-result-head h4 { margin: 0 0 6px; font-size: 18px; }
    .stress-result-head p { margin: 0; color: var(--muted); font-size: 12px; }
    .stress-run-badge {
      padding: 7px 9px;
      border: 1px solid rgba(245, 158, 11, 0.36);
      border-radius: 4px;
      color: #fbbf24;
      background: rgba(245, 158, 11, 0.08);
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .stress-run-badge[data-source="live"] { border-color: rgba(120,167,131,0.42); color: #a9c9b0; background: rgba(120,167,131,0.10); }
    .stress-run-badge[data-source="fallback"] { border-color: rgba(199,201,204,0.56); color: #f1f2f3; background: rgba(199,201,204,0.14); }
    .stress-kpis {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      border-bottom: 1px solid var(--line);
    }
    .stress-kpi { padding: 18px; border-right: 1px solid var(--line); }
    .stress-kpi:last-child { border-right: 0; }
    .stress-kpi span { display: block; color: var(--muted); font-size: 10px; font-weight: 800; text-transform: uppercase; }
    .stress-kpi strong { display: block; margin-top: 6px; font-size: 22px; }
    .stress-kpi.loss strong { color: var(--bad); }
    .stress-analysis-grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; margin-top: 16px; }
    .stress-subsection { min-width: 0; padding: 16px; border: 1px solid var(--line); background: rgba(3, 7, 18, 0.38); }
    .stress-subsection h4 { margin: 0 0 12px; font-size: 13px; text-transform: uppercase; }
    .stress-driver-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .stress-driver-table th, .stress-driver-table td { padding: 9px 7px; border-bottom: 1px solid var(--line); text-align: left; }
    .stress-driver-table th { color: var(--muted); font-size: 9px; text-transform: uppercase; }
    .stress-driver-table td:nth-child(n+3) { text-align: right; }
    .stress-negative { color: var(--bad); }
    .stress-positive { color: var(--good); }
    .stress-governance-list { margin: 0; padding-left: 17px; color: var(--muted); font-size: 12px; line-height: 1.55; }
    .stress-governance-list li { margin: 6px 0; }
    @media print {
      body > .app-shell, body > .basel-report-overlay:not(.visible) { display: none !important; }
      .basel-report-overlay.visible { position: static; display: block; overflow: visible; }
      .basel-report-toolbar { display: none; }
      .basel-report-canvas { width: 100%; margin: 0; }
      .basel-dashboard-section { break-inside: avoid; }
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
      .controls, .summary-grid, .layout, .layout.alt, .command-strip {
        grid-template-columns: 1fr;
      }
      .hero {
        flex-direction: column;
        align-items: start;
      }
      .hero-orbit { display: none; }
      .basel-kpi-grid { grid-template-columns: 1fr 1fr; }
      .basel-kpi:nth-child(2) { border-right: 0; }
      .basel-kpi:nth-child(-n+2) { border-bottom: 1px solid #dce3e8; }
      .basel-dashboard-grid { grid-template-columns: 1fr; }
      .basel-dashboard-section.wide { grid-column: auto; }
      .stress-analysis-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .floating-copilot {
        right: 14px;
        bottom: 14px;
      }
      .copilot-window {
        width: calc(100vw - 28px);
        height: calc(100vh - 28px);
        max-height: calc(100vh - 28px);
        border-radius: 22px;
      }
      .copilot-resize-handle {
        display: none;
      }
      .copilot-header {
        display: grid;
      }
      .copilot-meta {
        grid-template-columns: 1fr;
      }
      .basel-report-toolbar { padding: 10px 14px; }
      .basel-report-canvas { width: calc(100% - 20px); margin-top: 10px; }
      .basel-report-head { grid-template-columns: 1fr; padding: 20px; }
      .basel-scope-badge { max-width: none; text-align: left; }
      .basel-kpi-grid { grid-template-columns: 1fr; }
      .basel-kpi { border-right: 0; border-bottom: 1px solid #dce3e8; }
      .basel-stack-row { grid-template-columns: 1fr 80px; }
      .basel-stack-track { grid-column: 1 / -1; grid-row: 2; }
      .basel-evidence-grid, .basel-governance-meta { grid-template-columns: 1fr; }
      .stress-controls, .stress-kpis { grid-template-columns: 1fr; }
      .stress-kpi { border-right: 0; border-bottom: 1px solid var(--line); }
      .stress-result-head { display: grid; }
    }

    /* Industrial operations-console visual system */
    :root {
      --bg: #030303;
      --panel: #0b0b0b;
      --panel-2: #141414;
      --panel-3: #1b1b1b;
      --line: rgba(199, 201, 204, 0.22);
      --line-hot: rgba(240, 241, 242, 0.68);
      --text: #f3f4f5;
      --muted: #a7aaae;
      --accent: #c7c9cc;
      --accent-2: #f0f1f2;
      --accent-3: #8f9398;
      --good: #78a783;
      --bad: #d85a5a;
      --violet: #a0a7ab;
      --steel: #35373a;
      --steel-bright: #595c60;
      --radius-xs: 2px;
      --radius-sm: 4px;
      --radius-md: 6px;
      --radius-lg: 8px;
      --shadow: 0 12px 28px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.035);
      --shadow-inset: inset 0 1px 0 rgba(255, 255, 255, 0.04), inset 0 -1px 0 rgba(0, 0, 0, 0.72);
      --font-ui: Bahnschrift, "Segoe UI Variable", "Segoe UI", sans-serif;
      --font-mono: "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
    }
    body {
      font-family: var(--font-ui);
      background: linear-gradient(180deg, rgba(255,255,255,0.015), transparent 180px), var(--bg);
    }
    body::before {
      background:
        repeating-linear-gradient(135deg, rgba(255,255,255,0.018) 0 1px, transparent 1px 5px),
        repeating-linear-gradient(45deg, rgba(0,0,0,0.18) 0 1px, transparent 1px 5px);
      background-size: 8px 8px;
      mask-image: none;
      opacity: 0.52;
      animation: none;
    }
    body::after {
      display: block;
      background:
        radial-gradient(circle, rgba(199,201,204,0.22) 0 1px, transparent 1.5px) 0 0 / 137px 127px,
        radial-gradient(circle, rgba(199,201,204,0.16) 0 1px, transparent 1.5px) 47px 63px / 181px 163px,
        radial-gradient(circle, rgba(255,255,255,0.12) 0 1px, transparent 1.5px) 101px 23px / 227px 199px;
      z-index: 2;
      opacity: 0.46;
      animation: particleDrift 28s linear infinite;
    }
    .app-shell { grid-template-columns: 286px minmax(0, 1fr); }
    .sidebar {
      padding: 20px 16px;
      border-right: 1px solid var(--steel);
      background: linear-gradient(90deg, rgba(255,255,255,0.008), transparent 42%), linear-gradient(180deg, #101112, #080809);
      backdrop-filter: none;
      box-shadow: 8px 0 24px rgba(0,0,0,0.26), inset -1px 0 0 rgba(255,255,255,0.025);
    }
    .brand-mark {
      border: 1px solid #50585d;
      border-radius: var(--radius-sm);
      background: linear-gradient(145deg, #444b4f, #171a1c 52%, #070808);
      box-shadow: var(--shadow-inset), 0 6px 14px rgba(0,0,0,0.32);
    }
    .brand-mark::after {
      border: 1px solid var(--accent);
      border-radius: 1px;
      background: #111314;
      box-shadow: 0 0 0 3px rgba(199,201,204,0.08);
      animation: brandCorePulse 3.6s ease-in-out infinite;
    }
    .brand-copy strong { letter-spacing: 0; text-transform: uppercase; }
    .side-section {
      padding: 14px;
      margin-bottom: 12px;
      border-radius: var(--radius-md);
      background: linear-gradient(180deg, #111213, #0a0b0c);
      box-shadow: var(--shadow-inset);
    }
    .side-title, .sidebar-kpi .label { font-family: var(--font-mono); }
    .nav-list { gap: 4px; }
    .nav-item {
      padding: 10px;
      border-radius: var(--radius-sm);
      background: transparent;
      transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
    }
    .nav-item:hover, .nav-item.active {
      border-color: rgba(199,201,204,0.22);
      background: linear-gradient(90deg, rgba(199,201,204,0.065), rgba(199,201,204,0.012));
      box-shadow: none;
      transform: translateX(1px);
    }
    .status-badge { border-radius: var(--radius-xs); font-family: var(--font-mono); animation: statusBeacon 3.8s ease-in-out infinite; }
    .content {
      width: 100%;
      min-width: 0;
      padding: clamp(12px, 1.7vw, 22px) clamp(12px, 1.9vw, 24px) clamp(28px, 3.3vw, 42px);
    }
    .hero {
      min-height: 176px;
      margin-bottom: 12px;
      padding: 24px 26px;
      border: 1px solid var(--steel);
      border-left: 4px solid var(--accent);
      border-radius: var(--radius-lg);
      background: linear-gradient(105deg, rgba(255,255,255,0.025), transparent 58%), repeating-linear-gradient(135deg, rgba(255,255,255,0.014) 0 1px, transparent 1px 6px), linear-gradient(180deg, #191d20, #101214);
      box-shadow: var(--shadow);
      animation: heroFloat 7s ease-in-out infinite;
    }
    .hero::before {
      content: "SYS // RISK-OPS-01";
      width: auto;
      height: auto;
      right: 24px;
      top: 22px;
      border: 0;
      border-radius: 0;
      background: none;
      filter: none;
      color: #687075;
      font: 11px var(--font-mono);
      letter-spacing: 0.12em;
      animation: none;
    }
    .hero::after { content: "MARKET RISK / STRESS / CAPITAL / AI TOOLING"; color: #687075; }
    .eyebrow { font: 11px var(--font-mono); }
    h1 {
      max-width: 920px;
      font-size: 42px;
      line-height: 1.05;
      letter-spacing: 0;
      text-transform: uppercase;
      text-shadow: none;
    }
    .subtitle { max-width: 760px; line-height: 1.5; }
    .hero-telemetry { margin-top: 16px; }
    .telemetry-chip {
      padding: 7px 9px;
      border-radius: var(--radius-xs);
      background: #0d0f10;
      box-shadow: var(--shadow-inset);
      color: var(--text);
      font: 11px var(--font-mono);
      animation: telemetryBreathe 4.8s ease-in-out infinite;
    }
    .telemetry-chip span { color: var(--accent); }
    .telemetry-chip:nth-child(2) { animation-delay: 0.8s; }
    .telemetry-chip:nth-child(3) { animation-delay: 1.6s; }
    .telemetry-chip:nth-child(4) { animation-delay: 2.4s; }
    .hero-orbit { display: none; }
    .command-strip {
      gap: 1px;
      margin-bottom: 12px;
      border: 1px solid #2b2d30;
      border-radius: var(--radius-md);
      overflow: hidden;
      background: #252628;
    }
    .command-tile {
      position: relative;
      padding: 11px 12px;
      border: 0;
      border-radius: 0;
      background: #0d0e0f;
      box-shadow: var(--shadow-inset);
    }
    .command-tile strong { margin-bottom: 3px; color: var(--muted); font-family: var(--font-mono); }
    .command-tile span { color: var(--text); font: 12px/1.35 var(--font-mono); }
    .controls, .card, .panel {
      border-color: var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,0.018), transparent 32%), linear-gradient(180deg, var(--panel-2), var(--panel));
      box-shadow: var(--shadow);
      backdrop-filter: none;
    }
    .controls { top: 10px; margin-bottom: 12px; border-radius: var(--radius-md); }
    .field label { font-family: var(--font-mono); }
    select, button, textarea, .report-panel input {
      border-radius: var(--radius-sm);
      background: #0d0f10;
      font-family: var(--font-ui);
      transition: border-color 160ms ease, background 160ms ease, transform 160ms ease, color 160ms ease;
    }
    button {
      position: relative;
      overflow: hidden;
      border-color: #d5d7da;
      background: linear-gradient(180deg, #f0f1f2, #a9adb2);
      color: #0b0c0d;
      box-shadow: var(--shadow-inset), 0 4px 10px rgba(0,0,0,0.26);
    }
    button:hover:not(:disabled) { border-color: #ffffff; background: linear-gradient(180deg, #ffffff, #c4c7ca); transform: translateY(-1px); }
    button:active:not(:disabled) { transform: translateY(1px); box-shadow: inset 0 2px 5px rgba(0,0,0,0.42); }
    button:disabled { cursor: not-allowed; color: #72787b; border-color: #30363a; background: #181b1d; box-shadow: var(--shadow-inset); opacity: 0.72; }
    button:disabled::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent, rgba(199,201,204,0.12), transparent);
      transform: translateX(-100%);
      animation: processSweep 1.4s linear infinite;
    }
    select:focus-visible, button:focus-visible, textarea:focus-visible, input:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    .summary-grid { gap: 10px; margin-bottom: 10px; }
    .summary-grid:empty::before {
      content: "INITIALIZING RISK TELEMETRY...";
      grid-column: 1 / -1;
      padding: 16px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: var(--panel);
      font: 11px var(--font-mono);
      letter-spacing: 0.1em;
    }
    .card { min-height: 104px; border-radius: var(--radius-md); animation: panelEnter 260ms ease both; }
    .card::before { inset: 0; height: 2px; background: linear-gradient(90deg, var(--accent), transparent 54%); opacity: 0.52; }
    .metric-label { font: 10px var(--font-mono); }
    .metric-value { font: 800 29px var(--font-mono); }
    .panel { border-radius: var(--radius-lg); }
    .panel::before { background: linear-gradient(90deg, rgba(199,201,204,0.07), transparent 16%, transparent 84%, rgba(255,255,255,0.018)); }
    .section-heading h3, .table th { font-family: var(--font-mono); }
    .section-heading h3::before { border-radius: 1px; background: var(--accent); box-shadow: none; animation: sectionSignal 3.4s ease-in-out infinite; }
    .table { font-variant-numeric: tabular-nums; }
    .table-shell { width: 100%; overflow-x: auto; scrollbar-color: var(--steel-bright) #090a0b; }
    .status-item { border-radius: var(--radius-sm); background: #111416; }
    .status-pill { border-radius: var(--radius-xs); font-family: var(--font-mono); }
    .warning { border-radius: var(--radius-sm); }
    .stress-workbench { border-top-color: var(--accent); background: linear-gradient(180deg, #1b1f21, #111315); }
    .stress-status { min-height: 30px; margin-top: 10px; padding: 8px 10px; border-left: 2px solid var(--steel-bright); background: #0d0f10; font-family: var(--font-mono); }
    .stress-status[data-state="processing"] { border-left-color: var(--accent); color: var(--text); }
    .stress-status[data-state="error"] { border-left-color: var(--bad); color: #f0a1a1; }
    .stress-status[data-state="success"] { border-left-color: var(--good); color: #a9c9b0; }
    .stress-subsection { border-radius: var(--radius-sm); background: #0f1112; box-shadow: var(--shadow-inset); }
    .system-alert {
      position: relative;
      z-index: 50;
      margin: 12px;
      padding: 12px 14px;
      border: 1px solid rgba(216,90,90,0.55);
      border-left: 4px solid var(--bad);
      border-radius: var(--radius-sm);
      color: #f2b0b0;
      background: #241416;
      font: 12px var(--font-mono);
    }
    .copilot-launcher {
      border: 1px solid var(--accent);
      border-radius: var(--radius-lg);
      background: linear-gradient(145deg, #343a3e, #141719 58%, #090a0b);
      box-shadow: 0 10px 24px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 4px rgba(199,201,204,0.07);
      animation: launcherFloat 5.6s ease-in-out infinite;
    }
    .copilot-launcher:hover { border-color: #ffffff; box-shadow: 0 12px 28px rgba(0,0,0,0.44), 0 0 0 5px rgba(199,201,204,0.10); }
    .copilot-pulse { box-shadow: 0 0 0 3px rgba(120,167,131,0.16); animation: statusPulse 2.4s ease-in-out infinite; }
    .copilot-window {
      border-color: var(--steel-bright);
      border-radius: var(--radius-lg);
      background: repeating-linear-gradient(135deg, rgba(255,255,255,0.012) 0 1px, transparent 1px 6px), linear-gradient(180deg, #1b1f22, #0d0f10);
      box-shadow: 0 18px 46px rgba(0,0,0,0.58), var(--shadow-inset);
      backdrop-filter: none;
      animation: panelEnter 180ms ease both;
    }
    .copilot-icon-button, .copilot-status, .chat-log, .message, .prompt-toggle, .prompt-chip, .report-panel, .report-output { border-radius: var(--radius-sm); }
    .copilot-status { color: var(--good); background: rgba(120,167,131,0.08); font: 10px var(--font-mono); }
    .chat-log { background: #0c0e0f; }
    .message.user { background: rgba(199,201,204,0.12); border-color: rgba(199,201,204,0.32); }
    .message.ai { background: linear-gradient(180deg, #1a1e20, #121416); border-color: var(--line); box-shadow: none; }
    @keyframes panelEnter { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes brandCorePulse { 0%, 100% { box-shadow: 0 0 0 3px rgba(199,201,204,0.08), 0 0 0 rgba(199,201,204,0); } 50% { box-shadow: 0 0 0 4px rgba(199,201,204,0.14), 0 0 14px rgba(199,201,204,0.24); } }
    @keyframes statusBeacon { 0%, 100% { box-shadow: none; } 50% { box-shadow: 0 0 12px rgba(120,167,131,0.18); } }
    @keyframes heroFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
    @keyframes telemetryBreathe { 0%, 100% { border-color: rgba(199,201,204,0.22); box-shadow: var(--shadow-inset); } 50% { border-color: rgba(240,241,242,0.42); box-shadow: var(--shadow-inset), 0 0 12px rgba(199,201,204,0.10); } }
    @keyframes particleDrift { from { background-position: 0 0, 61px 83px, 131px 29px; } to { background-position: 173px -157px, -168px 280px, 414px -212px; } }
    @keyframes sectionSignal { 0%, 100% { opacity: 0.62; } 50% { opacity: 1; box-shadow: 0 0 8px rgba(199,201,204,0.32); } }
    @keyframes launcherFloat { 0%, 100% { transform: translateY(0); box-shadow: 0 10px 24px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 4px rgba(199,201,204,0.07); } 50% { transform: translateY(-4px); box-shadow: 0 14px 28px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 5px rgba(199,201,204,0.10); } }
    @keyframes statusPulse { 0%, 100% { opacity: 0.62; } 50% { opacity: 1; } }
    @keyframes processSweep { to { transform: translateX(100%); } }
    @media (max-width: 1260px) { .app-shell { grid-template-columns: 1fr; } }
    @media (max-width: 1120px) {
      .controls, .summary-grid, .command-strip { grid-template-columns: 1fr 1fr; }
      .layout, .layout.alt { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .content { padding: 12px; }
      .hero { min-height: 220px; padding: 20px 16px; }
      .hero::before { display: none; }
      .hero::after { left: 16px; right: auto; bottom: 14px; letter-spacing: 0.1em; }
      h1 { font-size: 30px; }
      .controls, .summary-grid, .command-strip { grid-template-columns: 1fr; }
      .copilot-window { border-radius: var(--radius-lg); }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important; transition-duration: 1ms !important; }
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
          <a class="nav-item" href="#stress-testing"><span>Stress testing</span><small>Historical replay</small></a>
          <a class="nav-item" href="#exposure"><span>Exposure</span><small>Weights and holdings</small></a>
          <a class="nav-item" href="#copilot"><span>AI Copilot</span><small>Ask, explain, investigate</small></a>
          <a class="nav-item" href="/regulatory-intelligence"><span>Regulatory intel</span><small>Capital markets</small></a>
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

    </aside>

    <main class="content">
      <div class="hero" id="overview">
        <div>
          <p class="eyebrow">Risk Advisor Copilot</p>
          <h1>AI-Enhanced Risk Command Center</h1>
          <div class="subtitle">Portfolio telemetry, governed historical stress, capital evidence, and tool-enabled AI analysis in one operational surface.</div>
          <div class="hero-telemetry">
            <div class="telemetry-chip"><span>Signal</span>VaR / CVaR online</div>
            <div class="telemetry-chip"><span>Feed</span>yfinance ingestion + cache</div>
            <div class="telemetry-chip"><span>Desk</span>PM-ready exposure diagnostics</div>
            <div class="telemetry-chip"><span>Mode</span>Phase 2 copilot online</div>
          </div>
        </div>
        <div class="hero-orbit" aria-hidden="true">
          <div class="orbital-core">RISK</div>
        </div>
      </div>

      <div class="command-strip">
        <div class="command-tile"><strong>Analytics core</strong><span>ONLINE / DETERMINISTIC</span></div>
        <div class="command-tile"><strong>Market data bus</strong><span>YFINANCE / LOCAL CACHE</span></div>
        <div class="command-tile"><strong>Stress engine</strong><span>GOVERNED / RECONCILED</span></div>
        <div class="command-tile"><strong>AI tool bus</strong><span>GPT-5.4 / ARMED</span></div>
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

      <section class="panel stress-workbench content-section" id="stress-testing">
        <div class="section-heading">
          <h3>Historical stress testing</h3>
          <span>Approved scenario replay on current positions</span>
        </div>
        <p class="helper">Run the same governed tool available to the AI Copilot. Historical returns are replayed on current marked positions with position-level P&amp;L reconciliation.</p>
        <div class="stress-controls">
          <div class="field">
            <label for="stress-scenario-select">Approved scenario</label>
            <select id="stress-scenario-select"></select>
          </div>
          <button id="run-stress-button" type="button">Run stress test</button>
          <button id="download-stress-button" type="button" disabled>Download report</button>
        </div>
        <div class="stress-status" id="stress-status" role="status" aria-live="polite">Select an approved scenario or ask the Copilot to run one.</div>
        <div class="stress-results" id="stress-results">
          <div class="stress-result-head">
            <div><h4 id="stress-result-title"></h4><p id="stress-result-subtitle"></p></div>
            <div class="stress-run-badge" id="stress-data-source" role="status">Deterministic replay</div>
          </div>
          <div class="stress-kpis" id="stress-kpis"></div>
          <div class="stress-analysis-grid">
            <div class="stress-subsection"><h4>Portfolio P&amp;L path</h4><div id="stress-path-chart" class="chart"></div></div>
            <div class="stress-subsection"><h4>Largest loss contributors</h4><div class="table-shell"><table class="stress-driver-table"><thead><tr><th>Ticker</th><th>Risk bucket</th><th>P&amp;L</th><th>Return</th></tr></thead><tbody id="stress-driver-rows"></tbody></table></div></div>
            <div class="stress-subsection"><h4>Scenario governance</h4><ul class="stress-governance-list" id="stress-governance"></ul></div>
            <div class="stress-subsection"><h4>Interpretation boundary</h4><ul class="stress-governance-list" id="stress-limitations"></ul></div>
          </div>
        </div>
      </section>

      <section class="layout content-section" id="risk">
        <div class="panel">
          <div class="section-heading">
            <h3>Portfolio vs benchmark</h3>
            <span>Normalized NAV and benchmark comparison</span>
          </div>
          <p class="helper">This view overlays portfolio NAV with the benchmark so the desk can see relative performance and drift at a glance.</p>
          <div id="value-chart" class="chart"></div>
        </div>
        <div class="panel">
          <div class="section-heading">
            <h3>Risk pulse</h3>
            <span>Current risk readout</span>
          </div>
          <p class="helper">A compact summary of headline risk metrics and active warnings for the selected book.</p>
          <div id="risk-pulse" class="status-list"></div>
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
          <div class="table-shell"><table class="table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Asset Class</th>
                <th>Market Value</th>
                <th>Weight</th>
              </tr>
            </thead>
            <tbody id="holdings-table"></tbody>
          </table></div>
          <div class="warnings" id="warning-list"></div>
        </div>
      </section>

      <section class="floating-copilot" id="copilot" aria-label="AI Risk Copilot">
        <div class="copilot-window" id="copilot-window" role="dialog" aria-label="AI Risk Copilot chat" aria-hidden="true">
          <div class="copilot-resize-handle" id="copilot-resize-handle" title="Drag to resize" aria-hidden="true"></div>
          <div class="copilot-header">
            <div>
              <div class="section-heading" style="margin-bottom: 6px;">
                <h3>AI Risk Copilot</h3>
                <span>Grounded portfolio Q&A</span>
              </div>
            </div>
            <div class="copilot-actions">
              <div class="copilot-status" id="copilot-status" role="status" aria-live="polite">Offline-ready</div>
              <button class="copilot-icon-button copilot-minimize-button" id="close-copilot-button" type="button" aria-label="Minimize copilot">_</button>
            </div>
          </div>
          <div class="chat-log" id="chat-log">
            <div class="message ai">Ask me why VaR moved, which exposures dominate downside risk, or what a PM should inspect before changing the book.</div>
          </div>
          <div class="composer">
            <textarea id="copilot-question" placeholder="Example: Explain the main downside risk in this portfolio and what I should inspect next."></textarea>
            <button id="ask-copilot-button" type="button">Ask Copilot</button>
          </div>
          <div class="prompt-panel" id="prompt-panel">
            <div class="prompt-panel-header">
              <div class="prompt-panel-title">Suggested questions</div>
              <button class="prompt-toggle" id="toggle-prompts-button" type="button" aria-expanded="true">Hide</button>
            </div>
            <div class="prompt-grid" id="prompt-grid">
              <button class="prompt-chip" type="button">Explain the current VaR and expected shortfall in plain English.</button>
              <button class="prompt-chip" type="button">Which holdings or asset classes are driving the most concentration risk?</button>
              <button class="prompt-chip" type="button">Compare this portfolio to its benchmark and highlight active risk.</button>
              <button class="prompt-chip" type="button">Run the approved historical stress test and give me the report.</button>
              <button class="prompt-chip" type="button">What should a PM inspect before increasing risk in this book?</button>
              <button class="prompt-chip" type="button">Write a short morning risk note for this portfolio.</button>
            </div>
          </div>
          <div class="report-panel">
            <div class="prompt-panel-header">
              <div class="prompt-panel-title">Report generation</div>
              <div class="small" id="report-status" role="status" aria-live="polite">Ready</div>
            </div>
            <div class="report-controls">
              <select id="report-type" aria-label="Report type">
                <option value="morning_note">Morning note</option>
                <option value="eod_wrap">End-of-day wrap</option>
                <option value="weekly_review">Weekly review</option>
                <option value="basel_simplified_capital">Basel-style capital charge</option>
              </select>
              <input id="report-audience" type="text" value="PM" aria-label="Report audience" />
            </div>
            <div class="report-actions">
              <button id="generate-report-button" type="button">Generate</button>
              <button id="copy-report-button" type="button" disabled>Copy</button>
              <button id="download-report-button" type="button" disabled>Download</button>
            </div>
            <div id="report-output" class="report-output"></div>
          </div>
          <div class="copilot-meta">
            <div class="meta-row"><span>Provider</span><strong>Poe OpenAI-compatible API</strong></div>
            <div class="meta-row"><span>Model</span><strong id="copilot-model">gpt-5.4</strong></div>
            <div class="meta-row"><span>Mode</span><strong id="copilot-mode">Waiting</strong></div>
            <div class="meta-row"><span>Grounding</span><strong>Risk report + catalog</strong></div>
          </div>
        </div>
        <button class="copilot-launcher" id="open-copilot-button" type="button" aria-label="Open AI Risk Copilot">
          <span class="copilot-pulse" aria-hidden="true"></span>
          <strong>AI</strong>
        </button>
      </section>
    </main>
  </div>

  <section class="basel-report-overlay" id="basel-report-overlay" aria-label="Basel capital dashboard" aria-hidden="true">
    <div class="basel-report-toolbar">
      <strong>Basel Capital Monitoring Dashboard</strong>
      <div class="basel-toolbar-actions">
        <button id="print-basel-report-button" type="button">Print / PDF</button>
        <button id="close-basel-report-button" type="button" aria-label="Close Basel dashboard">Close</button>
      </div>
    </div>
    <div class="basel-report-canvas" id="basel-report-canvas"></div>
  </section>

  <script>
    const state = {
      portfolios: [],
      currentPortfolioId: "core_long_equity",
      useDemoData: true,
      generatedReport: "",
      generatedReportTitle: "risk-report",
      generatedDashboard: null,
      stressResult: null,
    };

    const portfolioSelect = document.getElementById("portfolio-select");
    const dataMode = document.getElementById("data-mode");
    const refreshButton = document.getElementById("refresh-button");
    const portfolioDescription = document.getElementById("portfolio-description");
    const sidebarPortfolioName = document.getElementById("sidebar-portfolio-name");
    const sidebarPortfolioNote = document.getElementById("sidebar-portfolio-note");
    const sidebarDataBadge = document.getElementById("sidebar-data-badge");
    const chatLog = document.getElementById("chat-log");
    const copilotQuestion = document.getElementById("copilot-question");
    const askCopilotButton = document.getElementById("ask-copilot-button");
    const copilot = document.getElementById("copilot");
    const copilotWindow = document.getElementById("copilot-window");
    const copilotResizeHandle = document.getElementById("copilot-resize-handle");
    const openCopilotButton = document.getElementById("open-copilot-button");
    const closeCopilotButton = document.getElementById("close-copilot-button");
    const promptPanel = document.getElementById("prompt-panel");
    const togglePromptsButton = document.getElementById("toggle-prompts-button");
    const copilotStatus = document.getElementById("copilot-status");
    const copilotModel = document.getElementById("copilot-model");
    const copilotMode = document.getElementById("copilot-mode");
    const reportType = document.getElementById("report-type");
    const reportAudience = document.getElementById("report-audience");
    const reportStatus = document.getElementById("report-status");
    const reportOutput = document.getElementById("report-output");
    const generateReportButton = document.getElementById("generate-report-button");
    const copyReportButton = document.getElementById("copy-report-button");
    const downloadReportButton = document.getElementById("download-report-button");
    const baselReportOverlay = document.getElementById("basel-report-overlay");
    const baselReportCanvas = document.getElementById("basel-report-canvas");
    const closeBaselReportButton = document.getElementById("close-basel-report-button");
    const printBaselReportButton = document.getElementById("print-basel-report-button");
    const stressScenarioSelect = document.getElementById("stress-scenario-select");
    const runStressButton = document.getElementById("run-stress-button");
    const downloadStressButton = document.getElementById("download-stress-button");
    const stressStatus = document.getElementById("stress-status");
    const stressResults = document.getElementById("stress-results");

    const money = new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
    const percentage = new Intl.NumberFormat(undefined, { style: "percent", minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const decimal = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });
    const copilotSize = { width: 560, height: window.innerHeight - 44 };
    const chartTheme = {
      portfolio: "#2962ff",
      benchmark: "#ff9800",
      positive: "#26a69a",
      loss: "#ef5350",
      grid: "rgba(203, 208, 214, 0.14)",
      axis: "#e4e7eb",
    };

    function clamp(value, min, max) {
      return Math.min(Math.max(value, min), max);
    }

    function applyCopilotSize(width, height) {
      const maxWidth = Math.max(360, window.innerWidth - 44);
      const maxHeight = Math.max(520, window.innerHeight - 44);
      copilotSize.width = clamp(width, 380, maxWidth);
      copilotSize.height = clamp(height, 520, maxHeight);
      if (window.innerWidth > 640) {
        copilotWindow.style.width = `${copilotSize.width}px`;
        copilotWindow.style.height = `${copilotSize.height}px`;
      } else {
        copilotWindow.style.removeProperty("width");
        copilotWindow.style.removeProperty("height");
      }
    }

    function setPromptCollapsed(collapsed) {
      promptPanel.classList.toggle("collapsed", collapsed);
      togglePromptsButton.textContent = collapsed ? "Show" : "Hide";
      togglePromptsButton.setAttribute("aria-expanded", String(!collapsed));
      sessionStorage.setItem("copilotPromptsCollapsed", String(collapsed));
    }

    function startCopilotResize(event) {
      if (window.innerWidth <= 640) {
        return;
      }
      event.preventDefault();
      const startX = event.clientX;
      const startY = event.clientY;
      const startWidth = copilotWindow.offsetWidth;
      const startHeight = copilotWindow.offsetHeight;
      copilotWindow.classList.add("resizing");
      copilotResizeHandle.setPointerCapture(event.pointerId);

      function moveCopilotResize(moveEvent) {
        const nextWidth = startWidth + (startX - moveEvent.clientX);
        const nextHeight = startHeight + (startY - moveEvent.clientY);
        applyCopilotSize(nextWidth, nextHeight);
      }

      function stopCopilotResize() {
        copilotWindow.classList.remove("resizing");
        copilotResizeHandle.removeEventListener("pointermove", moveCopilotResize);
        copilotResizeHandle.removeEventListener("pointerup", stopCopilotResize);
        copilotResizeHandle.removeEventListener("pointercancel", stopCopilotResize);
      }

      copilotResizeHandle.addEventListener("pointermove", moveCopilotResize);
      copilotResizeHandle.addEventListener("pointerup", stopCopilotResize);
      copilotResizeHandle.addEventListener("pointercancel", stopCopilotResize);
    }

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

    function appendMessage(role, text) {
      const element = document.createElement("div");
      element.className = `message ${role}`;
      element.textContent = text;
      chatLog.appendChild(element);
      chatLog.scrollTop = chatLog.scrollHeight;
      return element;
    }

    function setMarkdownMessage(element, text) {
      if (window.marked && window.DOMPurify) {
        element.classList.add("markdown");
        const html = window.marked.parse(text || "", { breaks: true, gfm: true });
        element.innerHTML = window.DOMPurify.sanitize(html);
      } else {
        element.classList.remove("markdown");
        element.textContent = text || "";
      }
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    function openCopilot() {
      copilot.classList.add("open");
      copilotWindow.setAttribute("aria-hidden", "false");
      setTimeout(() => copilotQuestion.focus(), 60);
    }

    function closeCopilot() {
      copilot.classList.remove("open");
      copilotWindow.setAttribute("aria-hidden", "true");
      openCopilotButton.focus();
    }

    function renderReportPreview(markdown) {
      reportOutput.classList.add("visible");
      if (window.marked && window.DOMPurify) {
        const html = window.marked.parse(markdown || "", { breaks: true, gfm: true });
        reportOutput.innerHTML = window.DOMPurify.sanitize(html);
      } else {
        reportOutput.textContent = markdown || "";
      }
    }

    function escapeHtml(value) {
      const wrapper = document.createElement("div");
      wrapper.textContent = value == null ? "" : String(value);
      return wrapper.innerHTML;
    }

    function formatBaselValue(item) {
      const value = Number(item.value || 0);
      if (item.format === "money") return money.format(value);
      if (item.format === "percent") return percentage.format(value);
      if (item.format === "multiple") return `${decimal.format(value)}x`;
      if (item.format === "integer") return Math.round(value).toLocaleString();
      return decimal.format(value);
    }

    function baselList(items, emptyText) {
      const values = Array.isArray(items) ? items.filter(Boolean) : [];
      if (values.length === 0) return `<li>${escapeHtml(emptyText)}</li>`;
      return values.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    }

    function buildBaselDashboardMarkup(dashboard) {
      const headlineMetrics = dashboard.headline_metrics || [];
      const capitalStack = dashboard.capital_stack || [];
      const modelMetrics = dashboard.model_metrics || [];
      const evidence = dashboard.calculation_evidence || [];
      const stress = dashboard.stress_governance || {};
      const status = dashboard.status || {};
      const maxCapital = Math.max(...capitalStack.map((item) => Number(item.value || 0)), 1);
      const candidates = Array.isArray(stress.candidate_windows) && stress.candidate_windows.length > 0
        ? stress.candidate_windows.join(", ")
        : stress.selected_window_id || "Not supplied";
      const proxyCount = Array.isArray(stress.proxies) ? stress.proxies.length : 0;

      return `
        <header class="basel-report-head">
          <div>
            <div class="basel-report-kicker">${escapeHtml(status.label || "Internal monitoring")}</div>
            <h2>${escapeHtml(dashboard.portfolio_name)} · Basel Capital View</h2>
            <p>${escapeHtml(dashboard.desk)} · ${escapeHtml(dashboard.generated_at)} · Audience: ${escapeHtml(dashboard.audience)}</p>
          </div>
          <div class="basel-scope-badge">${escapeHtml(dashboard.framework)}</div>
        </header>

        <div class="basel-kpi-grid">
          ${headlineMetrics.map((item) => `
            <div class="basel-kpi">
              <span>${escapeHtml(item.label)}</span>
              <strong>${escapeHtml(formatBaselValue(item))}</strong>
            </div>
          `).join("")}
        </div>

        <div class="basel-dashboard-grid">
          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Capital stack</h3><span>Illustrative charge by component</span></div>
            ${capitalStack.map((item) => {
              const isPlaceholder = item.status !== "calculated";
              const width = isPlaceholder ? 0 : Math.max((Number(item.value || 0) / maxCapital) * 100, 1);
              return `
                <div class="basel-stack-row">
                  <div>${escapeHtml(item.label)}${isPlaceholder ? '<span class="basel-status-tag">Not implemented</span>' : ""}</div>
                  <div class="basel-stack-track"><div class="basel-stack-fill ${isPlaceholder ? "placeholder" : ""}" style="width:${width}%"></div></div>
                  <div class="basel-stack-value">${escapeHtml(money.format(Number(item.value || 0)))}</div>
                </div>
              `;
            }).join("")}
          </section>

          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Backtesting control</h3><span>Forecast vs realized P&amp;L</span></div>
            <div class="basel-classification ${escapeHtml(status.traffic_light || "insufficient")}">
              <strong>${escapeHtml(status.traffic_light_label || "NOT CLASSIFIED")}</strong>
              <span>${escapeHtml(status.traffic_light_reason || "Classification evidence unavailable.")}</span>
            </div>
            <table class="basel-metric-table">
              <thead><tr><th>Metric</th><th>Result</th><th>Basis</th></tr></thead>
              <tbody>
                ${modelMetrics.slice(-2).map((item) => `<tr><td>${escapeHtml(item.label)}</td><td>${escapeHtml(formatBaselValue(item))}</td><td>${escapeHtml(item.basis)}</td></tr>`).join("")}
              </tbody>
            </table>
          </section>

          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Model evidence</h3><span>99% confidence · 10-day horizon</span></div>
            <table class="basel-metric-table">
              <thead><tr><th>Measure</th><th>Result</th><th>Evidence</th></tr></thead>
              <tbody>
                ${modelMetrics.slice(0, 4).map((item) => `<tr><td>${escapeHtml(item.label)}</td><td>${escapeHtml(formatBaselValue(item))}</td><td>${escapeHtml(item.basis)}</td></tr>`).join("")}
              </tbody>
            </table>
          </section>

          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Calculation trace</h3><span>Binding capital logic</span></div>
            <div class="basel-evidence-grid">
              ${evidence.map((item) => `
                <div class="basel-evidence">
                  <strong>${escapeHtml(item.label)}</strong>
                  <code>${escapeHtml(item.formula)}</code>
                  <b>${escapeHtml(money.format(Number(item.value || 0)))}</b>
                </div>
              `).join("")}
            </div>
          </section>

          <section class="basel-dashboard-section wide">
            <div class="basel-section-title"><h3>Stressed VaR governance</h3><span>Window selection and coverage</span></div>
            <div class="basel-governance-meta">
              <div><span>Selected window</span><strong>${escapeHtml(stress.selected_window_id)}</strong></div>
              <div><span>Data mode</span><strong>${escapeHtml(stress.data_mode)}</strong></div>
              <div><span>Approved proxies used</span><strong>${proxyCount}</strong></div>
            </div>
            <p class="small"><strong>${escapeHtml(stress.selected_window)}</strong></p>
            <p class="small">Candidate set: ${escapeHtml(candidates)}</p>
            <p class="small">${escapeHtml(stress.methodology)}</p>
            <ul class="basel-detail-list">${baselList(stress.warnings, "No stress-window governance warnings raised.")}</ul>
          </section>

          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Methodology basis</h3><span>Implemented approach</span></div>
            <ul class="basel-detail-list">${baselList(dashboard.methodology, "Methodology disclosure unavailable.")}</ul>
          </section>

          <section class="basel-dashboard-section">
            <div class="basel-section-title"><h3>Scope and limitations</h3><span>Do not infer beyond these controls</span></div>
            <ul class="basel-detail-list">${baselList(dashboard.limitations, "No limitations supplied.")}</ul>
          </section>
        </div>
        <div class="basel-report-footer">Internal monitoring demo. Not a regulatory filing, supervisory approval, or claim of IMA model approval. RWA equivalent is the illustrative capital charge multiplied by 12.5.</div>
      `;
    }

    function openBaselDashboard(dashboard) {
      baselReportCanvas.innerHTML = buildBaselDashboardMarkup(dashboard);
      baselReportOverlay.classList.add("visible");
      baselReportOverlay.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      baselReportOverlay.scrollTop = 0;
    }

    function closeBaselDashboard() {
      baselReportOverlay.classList.remove("visible");
      baselReportOverlay.setAttribute("aria-hidden", "true");
      document.body.style.removeProperty("overflow");
    }

    function buildBaselStandaloneHtml(title, dashboard) {
      const styles = Array.from(document.querySelectorAll("style")).map((style) => style.textContent).join("\\n");
      return `<!doctype html><html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>${escapeHtml(title)}</title><style>${styles}</style></head><body><section class="basel-report-overlay visible"><div class="basel-report-canvas">${buildBaselDashboardMarkup(dashboard)}</div></section></body></html>`;
    }

    function stressDataSourceLabel(dataMode) {
      const sourceLabels = {
        live_current_marks_with_governed_historical_scenario: "Live/cache market data",
        demo_current_marks_with_governed_historical_scenario: "Demo marks + governed history",
        fallback_demo_current_marks_with_governed_historical_scenario: "Fallback demo marks + governed history",
        fallback_demo_current_marks_with_demo_scenario: "Fallback demo data",
      };
      return sourceLabels[dataMode] || `Data mode: ${String(dataMode || "unknown").replaceAll("_", " ")}`;
    }

    function renderStressResult(result, shouldScroll = false) {
      state.stressResult = result;
      stressResults.classList.add("visible");
      downloadStressButton.disabled = false;
      document.getElementById("stress-result-title").textContent = result.scenario_label;
      document.getElementById("stress-result-subtitle").textContent = `${result.portfolio_name} · ${result.scenario_start_date} to ${result.scenario_end_date} · worst point ${result.worst_date}`;
      const stressDataSource = document.getElementById("stress-data-source");
      stressDataSource.textContent = `Deterministic replay · ${stressDataSourceLabel(result.data_mode)}`;
      stressDataSource.dataset.source = result.data_mode === "live_current_marks_with_governed_historical_scenario"
        ? "live"
        : result.data_mode && result.data_mode.startsWith("fallback_")
          ? "fallback"
          : "demo";
      document.getElementById("stress-kpis").innerHTML = [
        ["Current value", money.format(result.current_value), ""],
        ["Worst loss", money.format(result.worst_loss), "loss"],
        ["Worst return", percentage.format(result.worst_return), "loss"],
        ["Stressed value", money.format(result.worst_stressed_value), ""],
      ].map(([label, value, tone]) => `<div class="stress-kpi ${tone}"><span>${label}</span><strong>${value}</strong></div>`).join("");

      const impacts = (result.position_impacts || []).slice(0, 7);
      document.getElementById("stress-driver-rows").innerHTML = impacts.map((row) => `
        <tr>
          <td>${escapeHtml(row.ticker)}</td>
          <td>${escapeHtml(row.risk_bucket)}</td>
          <td class="${row.pnl < 0 ? "stress-negative" : "stress-positive"}">${money.format(row.pnl)}</td>
          <td class="${row.return < 0 ? "stress-negative" : "stress-positive"}">${percentage.format(row.return)}</td>
        </tr>
      `).join("");

      const proxyText = (result.proxies_used || []).length > 0
        ? `${result.proxies_used.length} approved proxy mapping(s) applied and disclosed in the API result.`
        : "No approved proxy mapping was required.";
      const coverage = result.coverage_warnings || [];
      document.getElementById("stress-governance").innerHTML = [
        `Scenario ID: ${result.scenario_id}`,
        `Data mode: ${result.data_mode}`,
        `Attribution reconciled: ${result.attribution_reconciled}`,
        proxyText,
        ...coverage,
      ].map((item) => `<li>${escapeHtml(item)}</li>`).join("");
      document.getElementById("stress-limitations").innerHTML = (result.limitations || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");

      const path = result.path || [];
      Plotly.newPlot("stress-path-chart", [{
        x: path.map((point) => point.date),
        y: path.map((point) => point.pnl),
        type: "scatter",
        mode: "lines",
        fill: "tozeroy",
        line: { color: chartTheme.loss, width: 2 },
        fillcolor: "rgba(239,83,80,0.18)",
        hovertemplate: "%{x}<br>P&L %{y:$,.0f}<extra></extra>",
      }], {
        margin: { l: 62, r: 18, t: 12, b: 38 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { gridcolor: chartTheme.grid },
        yaxis: { tickprefix: "$", gridcolor: "rgba(239,83,80,0.18)", zerolinecolor: "rgba(228,231,235,0.34)" },
        font: { color: chartTheme.axis, family: "Cascadia Mono, Consolas, monospace" },
      }, { displayModeBar: false, responsive: true });
      stressStatus.textContent = `Completed ${result.scenario_id}; worst loss ${money.format(result.worst_loss)} on ${result.worst_date}.`;
      stressStatus.dataset.state = "success";
      if (shouldScroll) document.getElementById("stress-testing").scrollIntoView({ behavior: "smooth", block: "start" });
    }

    async function loadStressScenarios() {
      const response = await fetch(`/api/stress/scenarios?portfolio_id=${encodeURIComponent(portfolioSelect.value)}`);
      if (!response.ok) throw new Error(`Scenario catalog request failed (${response.status})`);
      const payload = await response.json();
      const approved = (payload.scenarios || []).filter((scenario) => scenario.approved_for_portfolio);
      stressScenarioSelect.innerHTML = approved.map((scenario) => `<option value="${escapeHtml(scenario.scenario_id)}">${escapeHtml(scenario.label)}</option>`).join("");
      stressResults.classList.remove("visible");
      state.stressResult = null;
      downloadStressButton.disabled = true;
      stressStatus.textContent = approved.length > 0 ? `${approved.length} approved scenario(s) available for this portfolio.` : "No approved scenarios available.";
      stressStatus.dataset.state = "idle";
    }

    async function runSelectedStressTest() {
      if (!stressScenarioSelect.value) return;
      runStressButton.disabled = true;
      stressStatus.dataset.state = "processing";
      stressStatus.textContent = "Running governed historical replay...";
      try {
        const response = await fetch("/api/stress/runs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            portfolio_id: portfolioSelect.value,
            scenario_id: stressScenarioSelect.value,
            use_demo_data: dataMode.value === "true",
          }),
        });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.detail || `Stress run failed (${response.status})`);
        renderStressResult(payload, true);
      } catch (error) {
        stressStatus.dataset.state = "error";
        stressStatus.textContent = `Stress run failed: ${error}`;
      } finally {
        runStressButton.disabled = false;
      }
    }

    function downloadStressReport() {
      if (!state.stressResult) return;
      const styles = Array.from(document.querySelectorAll("style")).map((style) => style.textContent).join("\\n");
      const title = `${state.stressResult.portfolio_name} - ${state.stressResult.scenario_label}`;
      const content = document.getElementById("stress-testing").outerHTML;
      const html = `<!doctype html><html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>${escapeHtml(title)}</title><style>${styles}body{padding:24px}.stress-workbench{max-width:1200px;margin:0 auto}.stress-controls{display:none}</style></head><body>${content}</body></html>`;
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${state.stressResult.portfolio_id}-${state.stressResult.scenario_id}-stress-report.html`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }

    function reportMarkdownToHtml(markdown) {
      if (window.marked && window.DOMPurify) {
        const html = window.marked.parse(markdown || "", { breaks: true, gfm: true });
        return window.DOMPurify.sanitize(html);
      }
      return `<pre>${escapeHtml(markdown || "")}</pre>`;
    }

    function buildStyledReportHtml(title, markdown) {
      const safeTitle = escapeHtml(title || "Risk Report");
      const generatedAt = new Date().toLocaleString();
      const reportBody = reportMarkdownToHtml(markdown);
      return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${safeTitle}</title>
  <style>
    :root {
      --bg: #030712;
      --panel: rgba(8, 13, 29, 0.94);
      --line: rgba(125, 211, 252, 0.18);
      --text: #eef7ff;
      --muted: #95a9c6;
      --accent: #38bdf8;
      --accent-2: #2dd4bf;
      --bad: #fb7185;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 14% 8%, rgba(56, 189, 248, 0.18), transparent 28%),
        radial-gradient(circle at 85% 10%, rgba(45, 212, 191, 0.14), transparent 26%),
        linear-gradient(180deg, #020617 0%, #030712 44%, #07111f 100%);
      color: var(--text);
      padding: 42px;
    }
    .shell {
      max-width: 1040px;
      margin: 0 auto;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(180deg, var(--panel), rgba(2, 6, 23, 0.92));
      box-shadow: 0 34px 100px rgba(0, 0, 0, 0.42), inset 0 1px 0 rgba(255,255,255,0.05);
      overflow: hidden;
    }
    .masthead {
      display: flex;
      justify-content: space-between;
      gap: 24px;
      padding: 30px 34px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(90deg, rgba(56, 189, 248, 0.12), rgba(45, 212, 191, 0.06), transparent);
    }
    .eyebrow {
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    h1 { margin: 0; font-size: 30px; letter-spacing: 0; }
    .stamp { color: var(--muted); font-size: 13px; text-align: right; line-height: 1.6; }
    .content { padding: 32px 34px 38px; }
    h1, h2, h3 { color: var(--text); }
    h2 {
      margin: 28px 0 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(125, 211, 252, 0.14);
      font-size: 18px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    p, li { color: #dce9f8; line-height: 1.65; }
    ul, ol { padding-left: 22px; }
    strong { color: #f8fbff; }
    code {
      border: 1px solid rgba(125, 211, 252, 0.16);
      border-radius: 8px;
      padding: 2px 5px;
      background: rgba(3, 7, 18, 0.54);
      color: #bae6fd;
    }
    blockquote {
      margin: 18px 0;
      padding: 12px 16px;
      border-left: 3px solid var(--accent-2);
      background: rgba(45, 212, 191, 0.07);
      color: var(--muted);
    }
    @media print {
      body { background: white; color: #111827; padding: 0; }
      .shell { box-shadow: none; border: 0; }
      .masthead { background: #f8fafc; }
      p, li, h1, h2, h3, strong { color: #111827; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="masthead">
      <div>
        <div class="eyebrow">Risk Advisor Copilot</div>
        <h1>${safeTitle}</h1>
      </div>
      <div class="stamp">Generated report<br />${escapeHtml(generatedAt)}</div>
    </header>
    <article class="content">${reportBody}</article>
  </main>
</body>
</html>`;
    }

    async function generateRiskReportDraft() {
      openCopilot();
      reportStatus.textContent = "Generating";
      generateReportButton.disabled = true;
      copyReportButton.disabled = true;
      downloadReportButton.disabled = true;

      try {
        const response = await fetch("/api/reports/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            portfolio_id: portfolioSelect.value,
            use_demo_data: dataMode.value === "true",
            report_type: reportType.value,
            audience: reportAudience.value || "PM",
          }),
        });
        const payload = await response.json();
        state.generatedReport = payload.report || "No report returned.";
        state.generatedReportTitle = payload.title || "risk-report";
        state.generatedDashboard = payload.dashboard || null;
        renderReportPreview(state.generatedReport);
        if (state.generatedDashboard) {
          closeCopilot();
          openBaselDashboard(state.generatedDashboard);
        }
        reportStatus.textContent = payload.mode === "poe_live_report" ? "Live AI report" : "Fallback report";
        copyReportButton.disabled = false;
        downloadReportButton.disabled = false;
      } catch (error) {
        state.generatedReport = "";
        reportOutput.classList.add("visible");
        reportOutput.textContent = `Report generation failed: ${error}`;
        reportStatus.textContent = "Error";
      } finally {
        generateReportButton.disabled = false;
      }
    }

    async function copyGeneratedReport() {
      if (!state.generatedReport) {
        return;
      }
      await navigator.clipboard.writeText(state.generatedReport);
      reportStatus.textContent = "Copied";
    }

    function downloadGeneratedReport() {
      if (!state.generatedReport) {
        return;
      }
      const slug = state.generatedReportTitle.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "risk-report";
      const html = state.generatedDashboard
        ? buildBaselStandaloneHtml(state.generatedReportTitle, state.generatedDashboard)
        : buildStyledReportHtml(state.generatedReportTitle, state.generatedReport);
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${slug}.html`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      reportStatus.textContent = "Downloaded HTML";
    }

    async function askCopilot(question) {
      const trimmed = question.trim();
      if (!trimmed) {
        return;
      }
      openCopilot();
      appendMessage("user", trimmed);
      copilotQuestion.value = "";
      copilotStatus.textContent = "Thinking";
      askCopilotButton.disabled = true;
      const pending = appendMessage("ai", "Analyzing current portfolio risk context...");

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: trimmed,
            portfolio_id: portfolioSelect.value,
            use_demo_data: dataMode.value === "true",
          }),
        });
        const payload = await response.json();
        setMarkdownMessage(pending, payload.answer || "No answer returned.");
        if (payload.stress_result) {
          renderStressResult(payload.stress_result, true);
          copilotStatus.textContent = "Stress tool complete";
        } else {
          copilotStatus.textContent = payload.mode === "poe_live" ? "Live AI" : "Offline analyst";
        }
        copilotModel.textContent = payload.model || "unknown";
        copilotMode.textContent = payload.mode || "unknown";
      } catch (error) {
        pending.textContent = `Copilot request failed: ${error}`;
        copilotStatus.textContent = "Error";
      } finally {
        askCopilotButton.disabled = false;
      }
    }

    function updateSidebar(report) {
      const selected = state.portfolios.find((portfolio) => portfolio.portfolio_id === report.portfolio_id);
      sidebarPortfolioName.textContent = report.portfolio_name;
      sidebarPortfolioNote.textContent = selected ? selected.objective : report.portfolio_objective || "";
      sidebarDataBadge.textContent = state.useDemoData ? "Demo data" : "Live yfinance data";
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

    function renderRiskPulse(report) {
      const warnings = report.warnings || [];
      const warningState = warnings.length > 0
        ? `${warnings.length} risk warning${warnings.length > 1 ? "s" : ""}`
        : "No active warnings";
      const warningDetail = warnings.length > 0
        ? warnings.slice(0, 2).join(" | ")
        : "Portfolio risk checks are currently within configured thresholds.";

      const rows = [
        ["Volatility + Drawdown", `${percentage.format(report.annualized_volatility)} | ${percentage.format(report.maximum_drawdown)}`, "Annualized volatility and max drawdown."],
        ["VaR + CVaR", `${percentage.format(report.historical_var_95)} | ${percentage.format(report.expected_shortfall_95)}`, "Historical VaR and expected shortfall at 95%."],
        ["Benchmark Link", `${report.beta_vs_benchmark == null ? "n/a" : decimal.format(report.beta_vs_benchmark)} beta | ${report.tracking_error == null ? "n/a" : percentage.format(report.tracking_error)} TE`, "Directional sensitivity and active risk vs benchmark."],
        ["Warning Monitor", warningState, warningDetail],
      ];

      document.getElementById("risk-pulse").innerHTML = rows.map(([label, value, note], index) => `
        <div class="status-item">
          <div class="status-pill ${index === 3 && warnings.length > 0 ? "no" : ""}">${index === 3 && warnings.length > 0 ? "!" : "✓"}</div>
          <div class="status-copy">
            <strong>${label}</strong>
            <div class="small">${value}</div>
            <div class="small">${note}</div>
          </div>
        </div>
      `).join("");
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
        marker: {
          color: sorted.map(([, weight]) => weight),
          colorscale: [[0, "#173e65"], [0.5, "#00bcd4"], [1, "#26a69a"]],
          line: { color: "rgba(228,231,235,0.28)", width: 1 },
        },
        hovertemplate: "%{y}: %{x:.2%}<extra></extra>",
      }], {
        margin: { l: 80, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { tickformat: ".0%", gridcolor: chartTheme.grid, zerolinecolor: "rgba(228,231,235,0.30)" },
        yaxis: { automargin: true, gridcolor: "rgba(203,208,214,0.06)" },
        font: { color: chartTheme.axis },
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
        { x: portfolio.x, y: portfolio.y, type: "scatter", mode: "lines", name: report.portfolio_name, line: { color: chartTheme.portfolio, width: 3 } },
        { x: benchmark.x, y: benchmark.y, type: "scatter", mode: "lines", name: "Benchmark", line: { color: chartTheme.benchmark, width: 2, dash: "dot" } },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { title: "Normalized to 100", gridcolor: chartTheme.grid, zerolinecolor: "rgba(228,231,235,0.30)" },
        xaxis: { gridcolor: "rgba(203,208,214,0.10)" },
        legend: { orientation: "h", bgcolor: "rgba(5,5,5,0.64)" },
        font: { color: chartTheme.axis },
      }, { displayModeBar: false, responsive: true });

      Plotly.newPlot("drawdown-chart", [
        { x: drawdownX, y: drawdownY, type: "scatter", mode: "lines", fill: "tozeroy", name: "Drawdown", line: { color: chartTheme.loss, width: 2 }, fillcolor: "rgba(239,83,80,0.18)" },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { tickformat: ".0%", range: [Math.min(...drawdownY, 0) * 1.1, 0.02], gridcolor: "rgba(239,83,80,0.18)", zerolinecolor: "rgba(239,83,80,0.32)" },
        xaxis: { gridcolor: "rgba(203,208,214,0.10)" },
        font: { color: chartTheme.axis },
      }, { displayModeBar: false, responsive: true });

      const correlation = report.correlation_matrix || {};
      const labels = Object.keys(correlation);
      const z = labels.map((row) => labels.map((col) => correlation[row][col] == null ? 0 : correlation[row][col]));
      Plotly.newPlot("correlation-chart", [{
        type: "heatmap",
        x: labels,
        y: labels,
        z,
        zmin: -1,
        zmax: 1,
        colorscale: [
          [0, "#ef5350"],
          [0.35, "#784447"],
          [0.5, "#37474f"],
          [0.65, "#26736e"],
          [1, "#26a69a"],
        ],
        hovertemplate: "%{y} vs %{x}: %{z:.2f}<extra></extra>",
      }], {
        margin: { l: 60, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { gridcolor: "rgba(203,208,214,0.08)" },
        yaxis: { gridcolor: "rgba(203,208,214,0.08)" },
        font: { color: chartTheme.axis },
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
      renderRiskPulse(report);
      renderCharts(report);
      renderHoldings(report);
      updateDescription();
      updateSidebar(report);
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      document.querySelector('a[href="#overview"]').classList.add("active");
    }

    refreshButton.addEventListener("click", loadReport);
    portfolioSelect.addEventListener("change", async () => {
      await Promise.all([loadReport(), loadStressScenarios()]);
    });
    dataMode.addEventListener("change", loadReport);
    openCopilotButton.addEventListener("click", openCopilot);
    closeCopilotButton.addEventListener("click", closeCopilot);
    generateReportButton.addEventListener("click", generateRiskReportDraft);
    copyReportButton.addEventListener("click", copyGeneratedReport);
    downloadReportButton.addEventListener("click", downloadGeneratedReport);
    closeBaselReportButton.addEventListener("click", closeBaselDashboard);
    printBaselReportButton.addEventListener("click", () => window.print());
    runStressButton.addEventListener("click", runSelectedStressTest);
    downloadStressButton.addEventListener("click", downloadStressReport);
    copilotResizeHandle.addEventListener("pointerdown", startCopilotResize);
    togglePromptsButton.addEventListener("click", () => {
      setPromptCollapsed(!promptPanel.classList.contains("collapsed"));
    });
    window.addEventListener("resize", () => applyCopilotSize(copilotSize.width, copilotSize.height));
    askCopilotButton.addEventListener("click", () => askCopilot(copilotQuestion.value));
    copilotQuestion.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        askCopilot(copilotQuestion.value);
      }
    });
    document.querySelectorAll(".prompt-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        copilotQuestion.value = chip.textContent.trim();
        askCopilot(copilotQuestion.value);
      });
    });
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach((navItem) => navItem.classList.remove("active"));
        item.classList.add("active");
      });
    });

    applyCopilotSize(copilotSize.width, copilotSize.height);
    setPromptCollapsed(sessionStorage.getItem("copilotPromptsCollapsed") === "true");

    loadPortfolios()
      .then(() => Promise.all([loadReport(), loadStressScenarios()]))
      .catch((error) => {
        console.error(error);
        document.body.insertAdjacentHTML("afterbegin", `<div class="system-alert" role="alert">DASHBOARD INITIALIZATION FAILED // CHECK API CONNECTIVITY</div>`);
      });
  </script>
</body>
</html>"""