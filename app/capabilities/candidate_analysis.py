from __future__ import annotations

from typing import Any, Dict, Optional

from app import llm_client
from app.resume_parser import build_candidate_analysis
from app.trace_logger import TraceLogger


def run(
    resume_text: str,
    job_analysis: Optional[Dict[str, Any]] = None,
    trace_logger: TraceLogger | None = None,
) -> Dict[str, object]:
    if llm_client.llm_is_configured():
        try:
            parsed = llm_client.extract_candidate_with_llm(
                resume_text, job_analysis or {}, trace_logger=trace_logger
            )
            return {
                "candidate_analysis": parsed,
                "meta": {
                    "resume_extraction": parsed,
                    "resume_extraction_meta": {
                        "llm_used": True,
                        "llm_fallback": False,
                        "confidence_notes": ["当前为 LLM 抽取版，规则版作为 fallback。"],
                    },
                },
            }
        except Exception as exc:  # pragma: no cover - defensive fallback
            parsed = build_candidate_analysis(resume_text)
            return {
                "candidate_analysis": parsed,
                "meta": {
                    "resume_extraction": parsed,
                    "resume_extraction_meta": {
                        "llm_used": False,
                        "llm_fallback": True,
                        "fallback_reason": str(exc),
                    },
                },
            }

    parsed = build_candidate_analysis(resume_text)
    return {
        "candidate_analysis": parsed,
        "meta": {
            "resume_extraction": parsed,
        },
    }
