"""Token tracking service for Gemini API usage per analysis."""
from typing import Dict, Any, Optional
from backend.schemas.models import TokenUsage


class TokenTracker:
    def __init__(self, analysis_id: str, model_name: str = "gemini-2.5-flash"):
        self.analysis_id = analysis_id
        self.model_name = model_name
        self.prompt_tokens = 0
        self.candidate_tokens = 0
        self.total_tokens = 0
        self.stage_breakdown: Dict[str, Dict[str, Any]] = {}
        self.estimated = False

    def record_usage(
        self,
        stage: str,
        prompt_text: str = "",
        candidate_text: str = "",
        usage_metadata: Optional[Any] = None
    ) -> None:
        """
        Record actual token usage from Gemini usage_metadata or precise character heuristics.
        """
        p_tokens = 0
        c_tokens = 0

        if usage_metadata is not None:
            # Official Google Gen AI usage_metadata object
            p_tokens = getattr(usage_metadata, "prompt_token_count", None) or \
                       getattr(usage_metadata, "prompt_tokens", 0) or 0
            c_tokens = getattr(usage_metadata, "candidates_token_count", None) or \
                       getattr(usage_metadata, "candidates_tokens", 0) or 0
            self.estimated = False
        else:
            # Fallback character-based conservative estimate (~4 chars per token)
            p_tokens = max(1, len(prompt_text) // 4) if prompt_text else 0
            c_tokens = max(1, len(candidate_text) // 4) if candidate_text else 0
            self.estimated = True

        stage_total = p_tokens + c_tokens
        self.prompt_tokens += p_tokens
        self.candidate_tokens += c_tokens
        self.total_tokens += stage_total

        self.stage_breakdown[stage] = {
            "prompt_tokens": p_tokens,
            "candidate_tokens": c_tokens,
            "total_tokens": stage_total,
            "model": self.model_name,
            "is_estimate": self.estimated
        }

    def to_schema(self) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=self.prompt_tokens,
            candidate_tokens=self.candidate_tokens,
            total_tokens=self.total_tokens,
            model_name=self.model_name,
            stage_breakdown=self.stage_breakdown,
            estimated=self.estimated
        )

