from __future__ import annotations

from typing import Any, Dict, Optional

from app import llm_client
from app.trace_logger import TraceLogger


def run(
    resume_text: str,
    job_analysis: Optional[Dict[str, Any]] = None,
    trace_logger: TraceLogger | None = None,
) -> Dict[str, object]:
    parsed = llm_client.extract_candidate_v3(
        resume_text, job_analysis or {}, trace_logger=trace_logger
    )
    return {
        "candidate_analysis": parsed,
        "meta": {
            "resume_extraction": parsed,
            "resume_extraction_meta": {
                "llm_used": True,
                "llm_fallback": False,
                "candidate_match_summary": parsed.get("candidate_match_summary", ""),
            },
        },
    }
