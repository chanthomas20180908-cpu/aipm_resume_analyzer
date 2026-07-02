#!/usr/bin/env python3
"""Verify v3 workflow structure with mock LLM responses."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ["DASHSCOPE_API_KEY"] = "dummy-key-for-testing"

from app import llm_client
from app.workflows import analyze_job_fit_v3


def _load_case():
    case_path = REPO_ROOT / "data" / "test_cases_v1" / "cases" / "case_002.json"
    with open(case_path, encoding="utf-8") as f:
        case = json.load(f)
    with open(REPO_ROOT / case["jd_file"], encoding="utf-8") as f:
        jd_text = f.read()
    with open(REPO_ROOT / case["resume_file"], encoding="utf-8") as f:
        resume_text = f.read()
    return jd_text, resume_text


FAKE_JD = {
    "jd_core_judgment": "真AI落地岗，偏业务重，适合有B端AI交付经验的产品经理",
    "key_requirements": ["有AI Agent项目完整落地经验", "5年及以上toB产品经验", "保险业务场景理解"],
    "key_risks": ["协调成本高", "职责边界宽", "指标不够清晰"],
    "role_type": "产品型",
    "business_context": "保险行业客服/质检Agent落地",
}

FAKE_CANDIDATE = {
    "candidate_profile": "5年AI工程师，强技术交付，弱产品视角",
    "match_points": ["有客服生成式AI产品Prompt设计经验", "从POC到生产规模部署", "准确率91%"],
    "gaps": ["缺少保险行业具体经验", "缺少典型PM职能证据"],
    "role_mismatch_flag": True,
    "candidate_match_summary": "技术强但角色偏工程，需补充产品视角和保险领域证据",
}

FAKE_FINAL = {
    "recommendation": "可投",
    "match_score": 75,
    "summary": "AI交付能力强，但角色偏工程且缺少保险直接经验，可先投再补材料。",
    "strengths": ["有完整AI Agent落地经验", "客服场景技术扎实"],
    "risks": ["角色偏工程，PM证据不足", "无保险行业直接经验"],
    "next_actions": ["补充保险业务学习路径", "用产品语言重构项目经历"],
}


def _fake_build_client():
    responses = iter(
        [
            json.dumps(FAKE_JD, ensure_ascii=False),
            json.dumps(FAKE_CANDIDATE, ensure_ascii=False),
            json.dumps(FAKE_FINAL, ensure_ascii=False),
        ]
    )

    def create(*args, **kwargs):
        return MagicMock(choices=[MagicMock(message=MagicMock(content=next(responses)))])

    client = MagicMock()
    client.chat.completions.create = create
    return client


def main():
    jd_text, resume_text = _load_case()

    responses = iter(
        [
            json.dumps(FAKE_JD, ensure_ascii=False),
            json.dumps(FAKE_CANDIDATE, ensure_ascii=False),
            json.dumps(FAKE_FINAL, ensure_ascii=False),
        ]
    )

    def _fake_build_client():
        def create(*args, **kwargs):
            return MagicMock(choices=[MagicMock(message=MagicMock(content=next(responses)))])

        client = MagicMock()
        client.chat.completions.create = create
        return client

    llm_client._build_client = _fake_build_client

    result = analyze_job_fit_v3.run(jd_text=jd_text, resume_text=resume_text)

    # Top-level fields
    assert result.get("recommendation") == "可投"
    assert result.get("match_score") == 75
    assert isinstance(result.get("summary"), str) and result["summary"]
    assert isinstance(result.get("strengths"), list) and result["strengths"]
    assert isinstance(result.get("risks"), list) and result["risks"]
    assert isinstance(result.get("next_actions"), list) and result["next_actions"]

    # JD analysis
    jd_analysis = result["job_analysis"]
    assert jd_analysis.get("jd_core_judgment")
    assert isinstance(jd_analysis.get("key_requirements"), list) and jd_analysis["key_requirements"]
    assert isinstance(jd_analysis.get("key_risks"), list) and jd_analysis["key_risks"]
    assert jd_analysis.get("role_type") in ("产品型", "工程型", "混合型")
    assert isinstance(jd_analysis.get("business_context"), str) and jd_analysis["business_context"]

    # Candidate analysis
    candidate_analysis = result["candidate_analysis"]
    assert candidate_analysis.get("candidate_match_summary")
    assert isinstance(candidate_analysis.get("candidate_profile"), str) and candidate_analysis["candidate_profile"]
    assert isinstance(candidate_analysis.get("match_points"), list) and candidate_analysis["match_points"]
    assert isinstance(candidate_analysis.get("gaps"), list) and candidate_analysis["gaps"]
    assert candidate_analysis.get("role_mismatch_flag") is True

    # Meta
    assert result["meta"]["version"] == "v3"
    assert "trace_id" in result["meta"]
    assert "trace_log_path" in result["meta"]

    trace_path = result["meta"]["trace_log_path"]
    with open(trace_path, encoding="utf-8") as f:
        log = f.read()
    assert log.count("### LLM 调用") == 3
    assert "## 步骤 1: JD 分析" in log
    assert "## 步骤 2: 候选人分析" in log
    assert "## 步骤 3: 终局判断" in log

    print("v3 workflow structure verification passed.")
    print(f"trace_log_path: {trace_path}")
    print(f"jd_core_judgment: {jd_analysis['jd_core_judgment']}")
    print(f"candidate_match_summary: {candidate_analysis['candidate_match_summary']}")


if __name__ == "__main__":
    main()
