from __future__ import annotations

from typing import Dict

from app.resume_parser import build_candidate_analysis


def run(resume_text: str) -> Dict[str, object]:
    candidate_analysis = build_candidate_analysis(resume_text)
    return {
        "candidate_analysis": candidate_analysis,
        "meta": {
            "resume_extraction": candidate_analysis,
        },
    }
