from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


ImpactRating = Literal["Critical", "High", "Medium", "Low"]


class RegulatorySource(BaseModel):
    title: str
    publisher: str
    url: HttpUrl
    source_tier: Literal["official", "major_media"]


class RegulatoryUpdate(BaseModel):
    id: str
    headline: str
    jurisdiction: Literal["HK", "Global", "US", "UK", "SG"]
    regulator: str
    topics: list[str]
    published_at: datetime
    summary: str
    impact_rating: ImpactRating
    portfolio_relevance: bool
    portfolio_impact: str
    source: RegulatorySource
    fetched_at: datetime
    is_seed: bool = False


class RegulatoryRefreshResult(BaseModel):
    mode: str
    fetched_at: datetime
    updates_added: int
    updates: list[RegulatoryUpdate]
    warning: str | None = None


class NewsletterIssue(BaseModel):
    id: str
    title: str
    dek: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    audience: list[str] = Field(default_factory=list)
    body_html: str
    source_update_ids: list[str]
    generation_mode: str
    disclaimer: str
