from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from openai import OpenAI

from app.prompts import (
    CANDIDATE_EXTRACTION_SYSTEM_PROMPT,
    JD_EXTRACTION_SYSTEM_PROMPT,
    LLM_RESULT_SYSTEM_PROMPT,
    V2_NARRATOR_SYSTEM_PROMPT,
    build_candidate_extraction_user_prompt,
    build_jd_extraction_user_prompt,
    build_llm_result_user_prompt,
    build_v2_narrator_user_prompt,
)
from app.prompts_v3 import (
    CANDIDATE_V3_SYSTEM_PROMPT,
    FINAL_V3_SYSTEM_PROMPT,
    JD_V3_SYSTEM_PROMPT,
    build_candidate_v3_user_prompt,
    build_final_v3_user_prompt,
    build_jd_v3_user_prompt,
)
from app.trace_logger import TraceLogger


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
    job_analysis: Dict[str, Any],
    candidate_analysis: Dict[str, Any],
    match_result: Dict[str, Any],
    recommendation_result: Dict[str, Any],
    fallback_result: Dict[str, Any],
    trace_logger: TraceLogger | None = None,
) -> Dict[str, Any]:
    client = _build_client()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    payload = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "job_analysis": job_analysis,
        "candidate_analysis": candidate_analysis,
        "match_result": match_result,
        "recommendation_result": recommendation_result,
    }
    user_prompt = build_v2_narrator_user_prompt(payload)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": V2_NARRATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    content = response.choices[0].message.content or ""
    parsed = _extract_json(content)
    if trace_logger:
        trace_logger.add_llm(
            model=model,
            system_prompt=V2_NARRATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            parsed_response=parsed,
        )
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


def _call_llm_json(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    trace_logger: TraceLogger | None = None,
) -> Dict[str, Any]:
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    raw_response = ""
    try:
        client = _build_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        raw_response = response.choices[0].message.content or ""
        parsed = _extract_json(raw_response)
        if trace_logger:
            trace_logger.add_llm(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response,
                parsed_response=parsed,
            )
        return parsed
    except Exception as exc:
        if trace_logger:
            trace_logger.add_llm(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response or str(exc),
                parsed_response=None,
            )
        raise


def extract_jd_with_llm(
    jd_text: str, trace_logger: TraceLogger | None = None
) -> Dict[str, Any]:
    """Use LLM to extract structured JD analysis."""
    user_prompt = build_jd_extraction_user_prompt(jd_text)
    parsed = _call_llm_json(
        system_prompt=JD_EXTRACTION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        trace_logger=trace_logger,
    )
    # Basic validation: ensure top-level keys exist
    required_keys = {"job_profile", "job_requirements", "job_risk_flags"}
    missing = required_keys - set(parsed.keys())
    if missing:
        raise LLMEnhancementError(f"JD extraction missing keys: {missing}")
    return parsed


def extract_candidate_with_llm(
    resume_text: str, job_analysis: Dict[str, Any], trace_logger: TraceLogger | None = None
) -> Dict[str, Any]:
    """Use LLM to extract structured candidate analysis."""
    user_prompt = build_candidate_extraction_user_prompt(resume_text, job_analysis)
    parsed = _call_llm_json(
        system_prompt=CANDIDATE_EXTRACTION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        trace_logger=trace_logger,
    )
    required_keys = {"candidate_profile", "candidate_evidence", "missing_evidence"}
    missing = required_keys - set(parsed.keys())
    if missing:
        raise LLMEnhancementError(f"Candidate extraction missing keys: {missing}")
    # Ensure role_mismatch_flag exists and is bool
    if "role_mismatch_flag" not in parsed:
        parsed["role_mismatch_flag"] = False
    return parsed


def extract_jd_v3(
    jd_text: str, trace_logger: TraceLogger | None = None
) -> Dict[str, Any]:
    """Use LLM to extract structured JD analysis for v3 workflow."""
    user_prompt = build_jd_v3_user_prompt(jd_text)
    parsed = _call_llm_json(
        system_prompt=JD_V3_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        trace_logger=trace_logger,
    )
    return parsed


def extract_candidate_v3(
    resume_text: str,
    job_analysis: Dict[str, Any],
    trace_logger: TraceLogger | None = None,
) -> Dict[str, Any]:
    """Use LLM to extract structured candidate analysis for v3 workflow."""
    user_prompt = build_candidate_v3_user_prompt(resume_text, job_analysis)
    parsed = _call_llm_json(
        system_prompt=CANDIDATE_V3_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        trace_logger=trace_logger,
    )
    if not isinstance(parsed.get("role_mismatch_flag"), bool):
        parsed["role_mismatch_flag"] = bool(parsed.get("role_mismatch_flag"))
    return parsed


def synthesize_final_v3(
    *,
    jd_text: str,
    resume_text: str,
    job_analysis: Dict[str, Any],
    candidate_analysis: Dict[str, Any],
    trace_logger: TraceLogger | None = None,
) -> Dict[str, Any]:
    """Use LLM to produce final recommendation and narration for v3 workflow."""
    user_prompt = build_final_v3_user_prompt(
        jd_text=jd_text,
        resume_text=resume_text,
        job_analysis=job_analysis,
        candidate_analysis=candidate_analysis,
    )
    parsed = _call_llm_json(
        system_prompt=FINAL_V3_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        trace_logger=trace_logger,
    )
    required_keys = {"recommendation", "match_score", "summary", "strengths", "risks", "next_actions"}
    missing = required_keys - set(parsed.keys())
    if missing:
        raise LLMEnhancementError(f"Final v3 synthesis missing keys: {missing}")
    return parsed
