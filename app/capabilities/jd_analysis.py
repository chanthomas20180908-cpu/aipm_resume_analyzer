from __future__ import annotations

from typing import Dict

from app.jd_parser import build_jd_analysis


def run(raw_jd_text: str) -> Dict[str, object]:
    parsed = build_jd_analysis(raw_jd_text)
    return {
        "job_analysis": parsed["normalized_jd"],
        "meta": {
            "jd_extraction": parsed["fact_extraction"],
            "jd_extraction_meta": parsed["extraction_meta"],
        },
    }
