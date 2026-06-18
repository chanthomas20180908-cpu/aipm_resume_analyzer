from __future__ import annotations

from typing import Dict

from app.capabilities import candidate_analysis, jd_analysis, match_scoring, narration, recommendation


def run(*, jd_text: str, resume_text: str, user_level: str, goal: str) -> Dict[str, object]:
    jd_result = jd_analysis.run(jd_text)
    candidate_result = candidate_analysis.run(resume_text)
    match_result = match_scoring.run(
        job_analysis=jd_result["job_analysis"],
        candidate_analysis=candidate_result["candidate_analysis"],
        user_goal=goal,
    )
    recommendation_result = recommendation.run(
        match_result=match_result,
        job_analysis=jd_result["job_analysis"],
        user_goal=goal,
    )
    narration_result = narration.run(
        jd_text=jd_text,
        resume_text=resume_text,
        user_level=user_level,
        goal=goal,
        job_analysis=jd_result["job_analysis"],
        candidate_analysis=candidate_result["candidate_analysis"],
        match_result=match_result,
        recommendation_result=recommendation_result,
    )
    meta = {
        "version": "v2",
        "user_level": user_level,
        "goal": goal,
        **jd_result["meta"],
        **candidate_result["meta"],
        **narration_result["meta"],
    }
    return {
        "job_analysis": jd_result["job_analysis"],
        "candidate_analysis": candidate_result["candidate_analysis"],
        "match_result": match_result,
        "recommendation_result": {
            **recommendation_result,
            "summary": narration_result["summary"],
            "strengths": narration_result["strengths"],
            "risks": narration_result["risks"],
            "next_actions": narration_result["next_actions"],
        },
        "recommendation": recommendation_result["recommendation"],
        "match_score": match_result["weighted_match_score"],
        "job_type": jd_result["job_analysis"]["job_profile"].get("job_family", "general_ai_pm"),
        "summary": narration_result["summary"],
        "strengths": narration_result["strengths"],
        "risks": narration_result["risks"],
        "next_actions": narration_result["next_actions"],
        "meta": meta,
    }
