from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from openai import OpenAI

from app.prompts import (
    LLM_RESULT_SYSTEM_PROMPT,
    V2_NARRATOR_SYSTEM_PROMPT,
    build_llm_result_user_prompt,
    build_v2_narrator_user_prompt,
)


DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-plus"


class LLMEnhancementError(RuntimeError):
    pass


def llm_is_configured() -> bool:
    return bool(os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY"))


def _build_client() -> OpenAI:
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMEnhancementError("Missing DASHSCOPE_API_KEY or OPENAI_API_KEY.")

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL),
    )


def _extract_json(content: str) -> Dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise LLMEnhancementError("LLM response did not contain a JSON object.")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMEnhancementError("Failed to parse LLM JSON response.") from exc


def _sanitize_list(values: Any, fallback: List[str]) -> List[str]:
    if not isinstance(values, list):
        return fallback
    cleaned = [str(item).strip() for item in values if str(item).strip()]
    return cleaned[:4] if cleaned else fallback


def enhance_analysis_result(
    *,
    jd_text: str,
    resume_text: str,
    user_level: str,
    goal: str,
    rule_result: Dict[str, Any],
) -> Dict[str, Any]:
    client = _build_client()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    payload = {
        "user_level": user_level,
        "goal": goal,
        "jd_text": jd_text,
        "resume_text": resume_text,
        "rule_result": {
            "recommendation": rule_result["recommendation"],
            "match_score": rule_result["match_score"],
            "job_type": rule_result["job_type"],
            "job_signals": rule_result["job_signals"],
            "candidate_signals": rule_result["candidate_signals"],
            "strengths": rule_result["strengths"],
            "risks": rule_result["risks"],
            "next_actions": rule_result["next_actions"],
            "summary": rule_result["summary"],
        },
    }

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": LLM_RESULT_SYSTEM_PROMPT},
            {"role": "user", "content": build_llm_result_user_prompt(payload)},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content or ""
    parsed = _extract_json(content)

    enhanced = dict(rule_result)
    enhanced["summary"] = str(parsed.get("summary") or rule_result["summary"]).strip()
    enhanced["strengths"] = _sanitize_list(parsed.get("strengths"), rule_result["strengths"])
    enhanced["risks"] = _sanitize_list(parsed.get("risks"), rule_result["risks"])
    enhanced["next_actions"] = _sanitize_list(parsed.get("next_actions"), rule_result["next_actions"])
    enhanced["meta"] = {
        **rule_result.get("meta", {}),
        "llm": {
            "used": True,
            "provider": "dashscope-compatible",
            "model": model,
        },
    }
    return enhanced


def enhance_v2_narration(
    *,
    jd_text: str,
    resume_text: str,
    user_level: str,
    goal: str,
    job_analysis: Dict[str, Any],
    candidate_analysis: Dict[str, Any],
    match_result: Dict[str, Any],
    recommendation_result: Dict[str, Any],
    fallback_result: Dict[str, Any],
) -> Dict[str, Any]:
    client = _build_client()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    payload = {
        "user_level": user_level,
        "goal": goal,
        "jd_text": jd_text,
        "resume_text": resume_text,
        "job_analysis": job_analysis,
        "candidate_analysis": candidate_analysis,
        "match_result": match_result,
        "recommendation_result": recommendation_result,
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": V2_NARRATOR_SYSTEM_PROMPT},
            {"role": "user", "content": build_v2_narrator_user_prompt(payload)},
        ],
        temperature=0.3,
    )
    content = response.choices[0].message.content or ""
    parsed = _extract_json(content)
    return {
        "summary": str(parsed.get("summary") or fallback_result["summary"]).strip(),
        "strengths": _sanitize_list(parsed.get("strengths"), fallback_result["strengths"]),
        "risks": _sanitize_list(parsed.get("risks"), fallback_result["risks"]),
        "next_actions": _sanitize_list(parsed.get("next_actions"), fallback_result["next_actions"]),
        "meta": {
            "llm": {
                "used": True,
                "provider": "dashscope-compatible",
                "model": model,
            }
        },
    }
