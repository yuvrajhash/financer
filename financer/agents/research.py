from __future__ import annotations

import json
from dataclasses import asdict

try:
    from openai import OpenAI
except ImportError:  # Optional until AI review is enabled
    OpenAI = None  # type: ignore

from financer.config import Settings
from financer.models import TradeCandidate


SYSTEM = """You are the skeptic reviewer inside a paper-trading research system.
You do not place trades. Review the supplied setup for contradictions, event risk,
data-quality risk, regime mismatch and reasons to reject it. Be concise. Never invent
prices or events. If current-news web search is enabled, cite only facts returned by the tool.
Return a short critique and finish with one of: ACCEPT_RESEARCH, CAUTION, REJECT_RESEARCH.
"""


class AIResearchReviewer:
    def __init__(self, settings: Settings):
        self.s = settings
        self.client = OpenAI(api_key=settings.openai_api_key) if (OpenAI and settings.openai_api_key) else None

    def review(self, candidate: TradeCandidate, extra_context: dict | None = None) -> str | None:
        if not self.s.enable_ai_review or not self.client:
            return None
        if candidate.score.final < self.s.ai_review_min_score:
            return None

        payload = {
            "strategy": candidate.signal.strategy,
            "version": candidate.signal.strategy_version,
            "side": candidate.signal.side,
            "entry": candidate.signal.entry,
            "stop": candidate.signal.stop,
            "target": candidate.signal.target,
            "rr": candidate.signal.rr,
            "regime": candidate.regime,
            "score": asdict(candidate.score),
            "reasons": candidate.signal.reasons,
            "extra_context": extra_context or {},
        }
        kwargs = {
            "model": self.s.openai_model,
            "instructions": SYSTEM,
            "input": json.dumps(payload, default=str),
        }
        if self.s.enable_ai_web_search:
            kwargs["tools"] = [{"type": "web_search"}]
        response = self.client.responses.create(**kwargs)
        return response.output_text
