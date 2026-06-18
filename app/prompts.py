from __future__ import annotations

import json
from typing import Any, Dict


LLM_RESULT_SYSTEM_PROMPT = (
    "你是一个谨慎的 AI PM 求职判断助手。"
    "你只能根据用户提供的 JD、简历和规则结果生成解释。"
    "不能修改 recommendation、match_score、job_type。"
    "不能编造不存在的项目经历。"
    "输出必须是 JSON，不要输出 markdown，不要解释。"
)


def build_llm_result_user_prompt(payload: Dict[str, Any]) -> str:
    return (
        "请基于下面的信息，生成更自然、更具体、但仍然克制的结果文案。"
        "返回 JSON，字段必须只有：summary, strengths, risks, next_actions。"
        "约束：summary 是一句中文结论；strengths、risks、next_actions 都是 2-4 条中文短句数组；"
        "要尽量引用 JD 或简历里的真实线索；不要改 recommendation；不要输出空字段。\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
