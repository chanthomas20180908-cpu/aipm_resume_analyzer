from __future__ import annotations

from typing import Dict

from app import llm_client
from app.trace_logger import TraceLogger


def run(raw_jd_text: str, trace_logger: TraceLogger | None = None) -> Dict[str, object]:
    parsed = llm_client.extract_jd_v3(raw_jd_text, trace_logger=trace_logger)
    return {
        "job_analysis": parsed,
        "meta": {
            "jd_extraction": parsed,
            "jd_extraction_meta": {
                "llm_used": True,
                "llm_fallback": False,
                "jd_core_judgment": parsed.get("jd_core_judgment", ""),
            },
        },
    }
