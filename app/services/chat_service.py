"""Chat orchestration service combining retrieval context, risk analysis, and audit logging."""

import time
import uuid

import chromadb

from app.agents.orchestrator import RiskOrchestrator
from app.core.config import settings
from app.core.logging import log_request
from app.data.mock_market import get_mock_historical_returns
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    LimitConfigSchema,
    RiskAnalyzeRequest,
)
from app.services.risk_service import _resolve_trades


class ChatService:
    def __init__(self) -> None:
        self.orchestrator = RiskOrchestrator(get_mock_historical_returns())
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection("risk_knowledge")
        if self.collection.count() == 0:
            self.collection.add(
                ids=["limit_policy", "var_definition", "driver_definition"],
                documents=[
                    "Desk limits define maximum gross exposure and maximum VaR thresholds.",
                    "Historical VaR estimates tail losses from historical return scenarios.",
                    "Risk drivers are the largest contributors to exposure or volatility impact.",
                ],
                metadatas=[
                    {"source": "internal_policy"},
                    {"source": "risk_methodology"},
                    {"source": "risk_framework"},
                ],
            )

    def _retrieve_context(self, query: str) -> list[str]:
        result = self.collection.query(query_texts=[query], n_results=2)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        context_lines: list[str] = []
        for doc, meta in zip(docs, metas):
            source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
            context_lines.append(f"{source}: {doc}")
        return context_lines

    def chat(self, request: ChatRequest) -> ChatResponse:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        message_lower = request.message.lower()
        risk_keywords = ["risk", "exposure", "var", "limit", "driver", "portfolio"]
        should_analyze = bool(request.trades) or any(keyword in message_lower for keyword in risk_keywords)

        retrieved_context = self._retrieve_context(request.message)
        tools_used: list[str] = []
        tool_outputs: dict[str, dict] = {}
        analysis = None

        if should_analyze:
            trades = _resolve_trades(request.trades)
            limit_config = LimitConfigSchema(
                max_gross_exposure=settings.max_gross_exposure,
                max_var=settings.max_var,
            )
            analysis, tool_outputs = self.orchestrator.analyze(
                trades=trades,
                confidence=settings.var_confidence,
                limit_config=limit_config,
                question=request.message,
            )
            tools_used = [
                "compute_portfolio_exposure",
                "calculate_var",
                "detect_limit_breach",
                "identify_risk_drivers",
                "retrieve_policy_context",
            ]
            message = (
                f"Explanation: {analysis.interpretation.explanation}\n"
                f"Hypothesis: {analysis.interpretation.hypothesis}\n"
                f"Suggestion: {analysis.interpretation.suggestion}"
            )
            response_type = "chat_risk_analysis"
        else:
            message = (
                "I can help with portfolio risk analysis. Ask about exposure, VaR, limits, "
                "or provide a trade list for computation."
            )
            response_type = "chat_general"

        latency_ms = int((time.perf_counter() - start) * 1000)
        log_request(
            request_id=request_id,
            request_type="chat",
            input_query=request.message,
            tools_used=tools_used,
            tool_outputs=tool_outputs,
            retrieved_context=retrieved_context,
            model_used=settings.llm_model_name,
            latency_ms=latency_ms,
            response_type=response_type,
        )

        return ChatResponse(
            request_id=request_id,
            response_type=response_type,
            message=message,
            analysis=analysis,
            citations=retrieved_context,
        )
