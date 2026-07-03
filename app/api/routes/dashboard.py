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
          <a class="nav-item" href="#copilot"><span>AI Copilot</span><small>Ask, explain, investigate</small></a>
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
          <h1>Autonomous Risk Command Center</h1>
          <div class="subtitle">A production-style dashboard for small hedge funds: strategy-based sample portfolios, live or demo market data, explicit risk calculations, benchmark comparison, and a completion view for the current phase.</div>
          <div class="hero-telemetry">
            <div class="telemetry-chip"><span>Signal</span>VaR / CVaR online</div>
            <div class="telemetry-chip"><span>Feed</span>yfinance ingestion + cache</div>
            <div class="telemetry-chip"><span>Desk</span>PM-ready exposure diagnostics</div>
            <div class="telemetry-chip"><span>Mode</span>Phase 1 complete</div>
          </div>
        </div>
        <div class="hero-orbit" aria-hidden="true">
          <div class="orbital-core">RISK</div>
        </div>
      </div>

      <div class="command-strip">
        <div class="command-tile"><strong>Portfolio telemetry</strong><span>Strategy selector, objective, market data mode, and refresh controls are wired to the live API.</span></div>
        <div class="command-tile"><strong>Risk engine</strong><span>NAV, returns, drawdown, VaR, CVaR, beta, tracking error, and correlations are computed server-side.</span></div>
        <div class="command-tile"><strong>Data layer</strong><span>Historical prices support demo mode and yfinance ingestion with deterministic local cache.</span></div>
        <div class="command-tile"><strong>Control status</strong><span>Phase 1 scope is continuously visible through the completion endpoint.</span></div>
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
              <div class="copilot-status" id="copilot-status">Offline-ready</div>
              <button class="copilot-icon-button" id="close-copilot-button" type="button" aria-label="Close copilot">×</button>
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
              <button class="prompt-chip" type="button">What should a PM inspect before increasing risk in this book?</button>
              <button class="prompt-chip" type="button">Write a short morning risk note for this portfolio.</button>
            </div>
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

    const money = new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
    const percentage = new Intl.NumberFormat(undefined, { style: "percent", minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const decimal = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });
    const copilotSize = { width: 560, height: window.innerHeight - 44 };

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
        pending.textContent = payload.answer || "No answer returned.";
        copilotStatus.textContent = payload.mode === "poe_live" ? "Live AI" : "Offline analyst";
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
        marker: {
          color: sorted.map(([, weight]) => weight),
          colorscale: [[0, "#1d4ed8"], [0.5, "#38bdf8"], [1, "#2dd4bf"]],
          line: { color: "rgba(238,247,255,0.20)", width: 1 },
        },
        hovertemplate: "%{y}: %{x:.2%}<extra></extra>",
      }], {
        margin: { l: 80, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { tickformat: ".0%", gridcolor: "rgba(125,211,252,0.10)", zerolinecolor: "rgba(125,211,252,0.18)" },
        yaxis: { automargin: true, gridcolor: "rgba(125,211,252,0.04)" },
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
        { x: benchmark.x, y: benchmark.y, type: "scatter", mode: "lines", name: "Benchmark", line: { color: "#2dd4bf", width: 2, dash: "dot" } },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { title: "Normalized to 100", gridcolor: "rgba(125,211,252,0.10)", zerolinecolor: "rgba(125,211,252,0.18)" },
        xaxis: { gridcolor: "rgba(125,211,252,0.08)" },
        legend: { orientation: "h", bgcolor: "rgba(3,7,18,0.30)" },
        font: { color: "#e5eefb" },
      }, { displayModeBar: false, responsive: true });

      Plotly.newPlot("drawdown-chart", [
        { x: drawdownX, y: drawdownY, type: "scatter", mode: "lines", fill: "tozeroy", name: "Drawdown", line: { color: "#fb7185", width: 2 }, fillcolor: "rgba(251,113,133,0.16)" },
      ], {
        margin: { l: 50, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        yaxis: { tickformat: ".0%", range: [Math.min(...drawdownY, 0) * 1.1, 0.02], gridcolor: "rgba(251,113,133,0.10)", zerolinecolor: "rgba(251,113,133,0.24)" },
        xaxis: { gridcolor: "rgba(125,211,252,0.08)" },
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
          [0, "#312e81"],
          [0.35, "#0f172a"],
          [0.65, "#0e7490"],
          [1, "#2dd4bf"],
        ],
        hovertemplate: "%{y} vs %{x}: %{z:.2f}<extra></extra>",
      }], {
        margin: { l: 60, r: 20, t: 20, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { gridcolor: "rgba(125,211,252,0.05)" },
        yaxis: { gridcolor: "rgba(125,211,252,0.05)" },
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
    openCopilotButton.addEventListener("click", openCopilot);
    closeCopilotButton.addEventListener("click", closeCopilot);
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

    Promise.all([loadPortfolios(), loadPhase1Status()])
      .then(loadReport)
      .catch((error) => {
        console.error(error);
        document.body.insertAdjacentHTML("afterbegin", `<div style="padding:16px; color:#fb7185;">Failed to load dashboard data.</div>`);
      });
  </script>
</body>
</html>"""