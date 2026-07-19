from __future__ import annotations

from datetime import UTC, datetime

from app.models.regulatory import RegulatoryUpdate


def initial_regulatory_updates() -> list[RegulatoryUpdate]:
    fetched_at = datetime.now(UTC)
    return [
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-hk-sfc-frr",
                "headline": "SFC financial resources rules remain a priority watch item",
                "jurisdiction": "HK",
                "regulator": "SFC",
                "topics": ["Market risk", "Capital", "Derivatives"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Track SFC consultations and conclusions affecting the Financial Resources Rules, including capital treatment, liquid capital and reporting expectations for licensed corporations.",
                "impact_rating": "High",
                "portfolio_relevance": True,
                "portfolio_impact": "Potentially relevant to broker-dealer capital, derivatives activity and the operating constraints of Hong Kong trading entities.",
                "source": {
                    "title": "SFC consultations and conclusions",
                    "publisher": "Hong Kong Securities and Futures Commission",
                    "url": "https://apps.sfc.hk/edistributionWeb/gateway/EN/consultation/",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-hkma-basel-iii",
                "headline": "HKMA Basel III implementation remains central to capital planning",
                "jurisdiction": "HK",
                "regulator": "HKMA",
                "topics": ["Basel capital", "Counterparty credit risk"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Monitor HKMA implementation materials for Basel III standards that affect risk-weighted assets, market risk and counterparty credit risk capital calculations.",
                "impact_rating": "High",
                "portfolio_relevance": True,
                "portfolio_impact": "Relevant where financing, derivatives counterparties or legal entities are subject to Hong Kong banking capital requirements.",
                "source": {
                    "title": "Implementation of international standards",
                    "publisher": "Hong Kong Monetary Authority",
                    "url": "https://www.hkma.gov.hk/eng/key-functions/banking/banking-regulatory-and-supervisory-regime/implementation-of-international-standards/",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-basel-counterparty-credit",
                "headline": "Basel market and counterparty credit standards shape global implementation",
                "jurisdiction": "Global",
                "regulator": "BCBS",
                "topics": ["Basel capital", "Market risk", "Counterparty credit risk"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "The Basel Framework remains the primary reference for market-risk capital and counterparty credit risk requirements as national regulators complete local implementation.",
                "impact_rating": "High",
                "portfolio_relevance": True,
                "portfolio_impact": "Relevant to capital consumption, pricing and capacity across bank counterparties and regulated trading entities.",
                "source": {
                    "title": "The Basel Framework",
                    "publisher": "Bank for International Settlements",
                    "url": "https://www.bis.org/basel_framework/",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-ai-risk-capital-markets",
                "headline": "AI model governance is moving into capital-markets risk agendas",
                "jurisdiction": "Global",
                "regulator": "FSB",
                "topics": ["AI risk", "Operational risk", "Capital markets"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Financial authorities are assessing how AI adoption can amplify model, third-party, cyber and concentration risks across financial services.",
                "impact_rating": "Medium",
                "portfolio_relevance": False,
                "portfolio_impact": "Primarily relevant to model governance and operating controls rather than current portfolio exposures; reassess as AI-supported trading workflows expand.",
                "source": {
                    "title": "Artificial intelligence in financial services",
                    "publisher": "Financial Stability Board",
                    "url": "https://www.fsb.org/work-of-the-fsb/financial-innovation-and-structural-change/artificial-intelligence-in-financial-services/",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-us-capital-markets",
                "headline": "US market-structure rulemaking remains a trading-risk watch item",
                "jurisdiction": "US",
                "regulator": "SEC",
                "topics": ["Market risk", "Capital markets"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Monitor SEC rules and proposals for changes that affect market structure, execution, clearing and regulated trading activity.",
                "impact_rating": "Medium",
                "portfolio_relevance": True,
                "portfolio_impact": "Potentially relevant to execution controls, liquidity assumptions, transaction costs and US market access.",
                "source": {
                    "title": "SEC rules and regulations",
                    "publisher": "U.S. Securities and Exchange Commission",
                    "url": "https://www.sec.gov/rules-regulations",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-uk-wholesale-markets",
                "headline": "UK wholesale-market supervision remains in active transition",
                "jurisdiction": "UK",
                "regulator": "FCA",
                "topics": ["Market risk", "Derivatives", "Capital markets"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Track FCA market-policy publications for changes affecting wholesale markets, trading venues, transparency and derivatives activity.",
                "impact_rating": "Medium",
                "portfolio_relevance": True,
                "portfolio_impact": "Potentially relevant to UK execution, venue selection, reporting obligations and derivatives workflows.",
                "source": {
                    "title": "FCA markets",
                    "publisher": "Financial Conduct Authority",
                    "url": "https://www.fca.org.uk/markets",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
        RegulatoryUpdate.model_validate(
            {
                "id": "seed-sg-capital-markets",
                "headline": "MAS capital-markets requirements anchor Singapore monitoring",
                "jurisdiction": "SG",
                "regulator": "MAS",
                "topics": ["Market risk", "Capital", "Derivatives"],
                "published_at": "2025-01-01T00:00:00Z",
                "summary": "Monitor MAS regulatory materials for requirements affecting capital-markets intermediaries, derivatives and risk management.",
                "impact_rating": "Medium",
                "portfolio_relevance": True,
                "portfolio_impact": "Potentially relevant to Singapore counterparties, regulated entities, derivatives controls and regional trading operations.",
                "source": {
                    "title": "MAS regulation",
                    "publisher": "Monetary Authority of Singapore",
                    "url": "https://www.mas.gov.sg/regulation",
                    "source_tier": "official",
                },
                "fetched_at": fetched_at,
                "is_seed": True,
            }
        ),
    ]
