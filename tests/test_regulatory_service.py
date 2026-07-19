from pathlib import Path

from app.services.regulatory_service import RegulatoryService, _is_trusted_source


def test_regulatory_updates_seed_and_filter(tmp_path: Path) -> None:
    service = RegulatoryService(tmp_path / "regulatory.db")

    updates = service.list_updates()
    hk_updates = service.list_updates(jurisdiction="HK")
    basel_updates = service.list_updates(topic="Basel")

    assert len(updates) >= 7
    assert {"HK", "Global", "US", "UK", "SG"}.issubset(
        {update.jurisdiction for update in updates}
    )
    assert all(update.source.source_tier == "official" for update in updates)
    assert all(update.jurisdiction == "HK" for update in hk_updates)
    assert basel_updates
    assert all(update.is_seed for update in updates)


def test_trusted_source_policy() -> None:
    assert _is_trusted_source("https://www.hkma.gov.hk/example", "official")
    assert _is_trusted_source("https://www.wsj.com/articles/example", "major_media")
    assert not _is_trusted_source("https://example.com/regulation", "official")