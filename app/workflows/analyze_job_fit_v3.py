from __future__ import annotations

from typing import Dict

from app import llm_client
from app.capabilities import candidate_analysis_v3, jd_analysis_v3
from app.trace_logger import TraceLogger


def run(*, jd_text: str, resume_text: str) -> Dict[str, object]:
    if not llm_client.llm_is_configured():
        raise llm_client.LLMEnhancementError(
            "v3 workflow requires DASHSCOPE_API_KEY or OPENAI_API_KEY."
        )

    trace_logger = TraceLogger()
    trace_logger.add_request(jd_text=jd_text, resume_text=resume_text)

    result: Dict[str, object] | None = None
    try:
        # Step 1: JD 分析
        jd_result = jd_analysis_v3.run(jd_text, trace_logger=trace_logger)
        trace_logger.add_step(
            step="步骤 1: JD 分析",
            purpose="把原始 JD 文本转成岗位核心判断、关键要求、主要风险和业务场景。",
            input_data={"jd_text": jd_text},
            output_data=jd_result,
            key_points={
                "role_type": jd_result["job_analysis"].get("role_type"),
                "business_context": jd_result["job_analysis"].get("business_context"),
                "jd_core_judgment": jd_result["job_analysis"].get("jd_core_judgment"),
            },
        )

        # Step 2: 候选人分析
        candidate_result = candidate_analysis_v3.run(
            resume_text, job_analysis=jd_result["job_analysis"], trace_logger=trace_logger
        )
        trace_logger.add_step(
            step="步骤 2: 候选人分析",
            purpose="把简历文本转成候选人画像、匹配点、短板、角色错配判断和核心匹配判断。",
            input_data={"resume_text": resume_text},
            output_data=candidate_result,
            key_points={
                "candidate_profile": candidate_result["candidate_analysis"].get("candidate_profile"),
                "role_mismatch_flag": candidate_result["candidate_analysis"].get("role_mismatch_flag"),
                "candidate_match_summary": candidate_result["candidate_analysis"].get(
                    "candidate_match_summary"
                ),
            },
        )

        # Step 3: 终局判断（LLM 直接输出 recommendation + 文案）
        final_result = llm_client.synthesize_final_v3(
            jd_text=jd_text,
            resume_text=resume_text,
            job_analysis=jd_result["job_analysis"],
            candidate_analysis=candidate_result["candidate_analysis"],
            trace_logger=trace_logger,
        )
        trace_logger.add_step(
            step="步骤 3: 终局判断",
            purpose="基于 JD 分析和候选人分析，给出最终投递建议和可读文案。",
            input_data={
                "job_analysis": jd_result["job_analysis"],
                "candidate_analysis": candidate_result["candidate_analysis"],
            },
            output_data=final_result,
            key_points={
                "recommendation": final_result.get("recommendation"),
                "match_score": final_result.get("match_score"),
            },
        )

        job_type = jd_result["job_analysis"].get("role_type", "混合型")
        result = {
            "job_analysis": jd_result["job_analysis"],
            "candidate_analysis": candidate_result["candidate_analysis"],
            "recommendation": final_result["recommendation"],
            "match_score": final_result["match_score"],
            "job_type": job_type,
            "summary": final_result["summary"],
            "strengths": final_result["strengths"],
            "risks": final_result["risks"],
            "next_actions": final_result["next_actions"],
            "meta": {
                "version": "v3",
                "trace_id": trace_logger.trace_id,
                **jd_result["meta"],
                **candidate_result["meta"],
                "llm": {
                    "used": True,
                    "provider": "dashscope-compatible",
                    "model": llm_client.DEFAULT_MODEL,
                },
            },
        }
        trace_logger.add_final(result=result)
    except Exception as exc:
        trace_logger.add_error(
            step="流程异常",
            error=str(exc),
            details={"type": type(exc).__name__},
        )
        raise
    finally:
        log_path = trace_logger.write()
        if result is not None:
            result["meta"]["trace_log_path"] = str(log_path)

    return result
