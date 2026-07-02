from __future__ import annotations

from typing import Dict

from app import llm_client
from app.jd_parser import build_jd_analysis
from app.trace_logger import TraceLogger


def run(raw_jd_text: str, trace_logger: TraceLogger | None = None) -> Dict[str, object]:
    if llm_client.llm_is_configured():
        try:
            parsed = llm_client.extract_jd_with_llm(raw_jd_text, trace_logger=trace_logger)
            return {
                "job_analysis": parsed,
                "meta": {
                    "jd_extraction": parsed,
                    "jd_extraction_meta": {
                        "llm_used": True,
                        "llm_fallback": False,
                        "confidence_notes": ["当前为 LLM 抽取版，规则版作为 fallback。"],
                    },
                },
            }
        except Exception as exc:  # pragma: no cover - defensive fallback
            parsed = build_jd_analysis(raw_jd_text)
            return {
                "job_analysis": parsed["normalized_jd"],
                "meta": {
                    "jd_extraction": parsed["fact_extraction"],
                    "jd_extraction_meta": {
                        **parsed["extraction_meta"],
                        "llm_used": False,
                        "llm_fallback": True,
                        "fallback_reason": str(exc),
                    },
                },
            }

    parsed = build_jd_analysis(raw_jd_text)
    return {
        "job_analysis": parsed["normalized_jd"],
        "meta": {
            "jd_extraction": parsed["fact_extraction"],
            "jd_extraction_meta": parsed["extraction_meta"],
        },
    }
