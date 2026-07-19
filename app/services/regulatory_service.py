from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
from html import escape
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlparse
from uuid import uuid4

from app.core.config import get_settings
from app.data.regulatory_seed import initial_regulatory_updates
from app.models.regulatory import NewsletterIssue, RegulatoryRefreshResult, RegulatoryUpdate


TRUSTED_OFFICIAL_DOMAINS = {
    "bis.org", "cftc.gov", "fca.org.uk", "federalreserve.gov", "finra.org",
    "fsb.org", "gov.uk", "hkma.gov.hk", "mas.gov.sg", "sec.gov", "sfc.hk",
}
TRUSTED_MEDIA_DOMAINS = {"bloomberg.com", "ft.com", "reuters.com", "wsj.com"}


class RegulatoryService:
    def __init__(self, database_path: Path | str = "risk_advisor.db") -> None:
        self.database_path = Path(database_path)
        self._ensure_tables()
        self._seed_initial_records()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_tables(self) -> None:
        with self._connect() as connection:
            columns = {
                str(row[1])
                for row in connection.execute("PRAGMA table_info(regulatory_updates)").fetchall()
            }
            if columns and "payload_json" not in columns:
                archived_name = f"regulatory_updates_legacy_{datetime.now(UTC):%Y%m%d%H%M%S%f}"
                connection.execute(
                    f"ALTER TABLE regulatory_updates RENAME TO {archived_name}"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS regulatory_updates (
                    id TEXT PRIMARY KEY,
                    published_at TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    jurisdiction TEXT NOT NULL,
                    regulator TEXT NOT NULL,
                    impact_rating TEXT NOT NULL,
                    portfolio_relevance INTEGER NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            newsletter_columns = {
                str(row[1])
                for row in connection.execute("PRAGMA table_info(regulatory_newsletters)").fetchall()
            }
            if newsletter_columns and "payload_json" not in newsletter_columns:
                archived_name = f"regulatory_newsletters_legacy_{datetime.now(UTC):%Y%m%d%H%M%S%f}"
                connection.execute(
                    f"ALTER TABLE regulatory_newsletters RENAME TO {archived_name}"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS regulatory_newsletters (
                    id TEXT PRIMARY KEY,
                    generated_at TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def _seed_initial_records(self) -> None:
        self.save_updates(initial_regulatory_updates())

    def save_updates(self, updates: list[RegulatoryUpdate]) -> int:
        added = 0
        with self._connect() as connection:
            for update in updates:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO regulatory_updates
                    (id, published_at, fetched_at, jurisdiction, regulator, impact_rating,
                     portfolio_relevance, payload_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        update.id,
                        update.published_at.isoformat(),
                        update.fetched_at.isoformat(),
                        update.jurisdiction,
                        update.regulator,
                        update.impact_rating,
                        int(update.portfolio_relevance),
                        update.model_dump_json(),
                    ),
                )
                added += cursor.rowcount
        return added

    def list_updates(
        self,
        jurisdiction: str | None = None,
        topic: str | None = None,
        limit: int = 100,
    ) -> list[RegulatoryUpdate]:
        query = "SELECT payload_json FROM regulatory_updates"
        parameters: list[object] = []
        if jurisdiction:
            query += " WHERE jurisdiction = ?"
            parameters.append(jurisdiction)
        query += " ORDER BY published_at DESC, fetched_at DESC LIMIT ?"
        parameters.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        updates = [RegulatoryUpdate.model_validate_json(row["payload_json"]) for row in rows]
        if topic:
            normalized = topic.casefold()
            updates = [
                update for update in updates
                if any(normalized in value.casefold() for value in update.topics)
            ]
        return updates

    def refresh(self) -> RegulatoryRefreshResult:
        fetched_at = datetime.now(UTC)
        settings = get_settings()
        if not settings.poe_api_key:
            return RegulatoryRefreshResult(
                mode="seed_fallback",
                fetched_at=fetched_at,
                updates_added=0,
                updates=self.list_updates(),
                warning="POE_API_KEY is not configured. Showing saved official-source watch items.",
            )

        try:
            updates = self._fetch_with_ai(fetched_at)
            added = self.save_updates(updates)
            return RegulatoryRefreshResult(
                mode="ai_web_search",
                fetched_at=fetched_at,
                updates_added=added,
                updates=self.list_updates(),
            )
        except Exception as exc:  # pragma: no cover - live provider path
            return RegulatoryRefreshResult(
                mode="provider_error_fallback",
                fetched_at=fetched_at,
                updates_added=0,
                updates=self.list_updates(),
                warning=f"Live regulatory search failed; showing saved records. {exc}",
            )

    def list_newsletters(self, limit: int = 20) -> list[NewsletterIssue]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM regulatory_newsletters "
                "ORDER BY generated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [NewsletterIssue.model_validate_json(row["payload_json"]) for row in rows]

    def generate_newsletter(self) -> NewsletterIssue:
        updates = self.list_updates(limit=30)
        if not updates:
            raise ValueError("No regulatory updates are available for newsletter generation")
        now = datetime.now(UTC)
        settings = get_settings()
        mode = "editorial_fallback"
        title = "The Risk Ledger: Capital Rules in Motion"
        dek = "A weekly briefing on market-risk supervision, capital and counterparty exposure."
        body_html = self._fallback_newsletter_html(updates)
        if settings.poe_api_key:
            try:
                title, dek, body_html = self._generate_newsletter_with_ai(updates)
                mode = "ai_grounded"
            except Exception:  # pragma: no cover - live provider path
                mode = "provider_error_fallback"

        issue = NewsletterIssue(
            id=f"issue-{uuid4().hex[:12]}",
            title=title,
            dek=dek,
            generated_at=now,
            period_start=now - timedelta(days=7),
            period_end=now,
            audience=["CRO and risk leadership", "Trading desks", "Compliance"],
            body_html=body_html,
            source_update_ids=[update.id for update in updates],
            generation_mode=mode,
            disclaimer=(
                "AI-generated regulatory intelligence may be incomplete or incorrect. "
                "Verify all conclusions against linked primary sources; this is not legal advice."
            ),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO regulatory_newsletters
                (id, generated_at, period_start, period_end, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    issue.id,
                    issue.generated_at.isoformat(),
                    issue.period_start.isoformat(),
                    issue.period_end.isoformat(),
                    issue.model_dump_json(),
                ),
            )
        return issue

    def _fallback_newsletter_html(self, updates: list[RegulatoryUpdate]) -> str:
        ranked = sorted(
            updates,
            key=lambda update: ({"Critical": 4, "High": 3, "Medium": 2, "Low": 1}[update.impact_rating], update.published_at),
            reverse=True,
        )
        sections: list[str] = [
            "<p class=\"dropcap\">Capital-markets risk teams enter the week with implementation detail, counterparty exposure and model governance competing for attention. The clearest signal is to keep primary regulatory texts close and translate each development into an owned control or capital question.</p>",
            "<h2>The week in risk</h2>",
        ]
        for update in ranked[:6]:
            relevance = "Direct portfolio read-through" if update.portfolio_relevance else "Enterprise watch item"
            sections.extend(
                [
                    f"<article><p class=\"kicker\">{escape(update.jurisdiction)} · {escape(update.regulator)} · {escape(update.impact_rating)}</p>",
                    f"<h3>{escape(update.headline)}</h3>",
                    f"<p>{escape(update.summary)}</p>",
                    f"<p><strong>{relevance}:</strong> {escape(update.portfolio_impact)}</p>",
                    f"<p class=\"source-line\"><a href=\"{escape(str(update.source.url))}\" target=\"_blank\" rel=\"noopener noreferrer\">Read the source: {escape(update.source.publisher)}</a></p></article>",
                ]
            )
        sections.append(
            "<h2>Desk agenda</h2><p>Confirm implementation owners, test whether capital assumptions remain current, and escalate any change that alters derivatives capacity, counterparty limits or market-risk reporting.</p>"
        )
        return "".join(sections)

    def _generate_newsletter_with_ai(
        self, updates: list[RegulatoryUpdate]
    ) -> tuple[str, str, str]:
        import openai

        settings = get_settings()
        context = [update.model_dump(mode="json") for update in updates]
        prompt = f"""
Write a concise weekly capital-markets risk newsletter for CROs, trading desks and compliance.
Use a restrained financial-newspaper style, but do not imitate any publication or invent facts.
Use ONLY the supplied saved updates. Return a JSON object with title, dek and body_html. body_html
may use p, h2, h3, article, strong, a and blockquote tags. Preserve exact source URLs, attribute
any quotation, and include portfolio read-through. Do not give legal advice.

Saved updates:
{json.dumps(context)}
""".strip()
        client = openai.OpenAI(api_key=settings.poe_api_key, base_url=settings.poe_base_url)
        response = client.responses.create(model=settings.poe_model, input=prompt)
        raw = str(response.output_text).strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            if raw.startswith("json"):
                raw = raw[4:].lstrip()
        result = json.loads(raw)
        return str(result["title"]), str(result["dek"]), str(result["body_html"])

    def _fetch_with_ai(self, fetched_at: datetime) -> list[RegulatoryUpdate]:
        import openai

        settings = get_settings()
        client = openai.OpenAI(api_key=settings.poe_api_key, base_url=settings.poe_base_url)
        cutoff = (fetched_at - timedelta(days=14)).date().isoformat()
        prompt = f"""
Search the web for material capital-markets regulatory developments published since {cutoff}.
Cover Hong Kong (SFC and HKMA), global Basel/BCBS, United States, United Kingdom, and Singapore.
Focus on market risk, Basel capital, derivatives, counterparty credit risk, and material AI risk.
Use official regulator publications first. Use Bloomberg, WSJ, Reuters, or FT only for meaningful
secondary context. Return ONLY a JSON array with: headline, jurisdiction (HK, Global, US, UK, SG),
regulator, topics (array), published_at (ISO timestamp), summary, impact_rating (Critical, High,
Medium, Low), portfolio_relevance (boolean), portfolio_impact, source_title, source_publisher,
source_url, source_tier (official or major_media). Never invent a URL, date, quotation, or event.
""".strip()
        response = client.responses.create(
            model=settings.poe_model,
            input=prompt,
            tools=[{"type": "web_search_preview"}],
        )
        raw = str(response.output_text).strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            if raw.startswith("json"):
                raw = raw[4:].lstrip()
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("Web search response was not a JSON array")

        updates: list[RegulatoryUpdate] = []
        for item in payload:
            url = str(item["source_url"])
            source_tier = str(item["source_tier"])
            if not _is_trusted_source(url, source_tier):
                continue
            identifier = hashlib.sha256(
                f"{item['headline']}|{url}|{item['published_at']}".encode("utf-8")
            ).hexdigest()[:20]
            updates.append(
                RegulatoryUpdate.model_validate(
                    {
                        "id": f"web-{identifier}",
                        **{key: value for key, value in item.items() if not key.startswith("source_")},
                        "source": {
                            "title": item["source_title"],
                            "publisher": item["source_publisher"],
                            "url": url,
                            "source_tier": source_tier,
                        },
                        "fetched_at": fetched_at,
                    }
                )
            )
        return updates


def _is_trusted_source(url: str, source_tier: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    allowed = TRUSTED_OFFICIAL_DOMAINS if source_tier == "official" else TRUSTED_MEDIA_DOMAINS
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowed)
