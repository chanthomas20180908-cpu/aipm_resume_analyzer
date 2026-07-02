from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def _json_block(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


class TraceLogger:
    def __init__(self, trace_id: str | None = None) -> None:
        self.trace_id = trace_id or datetime.now().strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8]
        self.created_at = datetime.now().isoformat(timespec="seconds")
        self._sections: List[str] = []
        self._pending_llm_block: str | None = None

    def add_request(self, *, jd_text: str, resume_text: str) -> None:
        payload = {
            "jd_text": jd_text,
            "resume_text": resume_text,
        }
        self._sections.append(
            "\n".join(
                [
                    "## 请求输入",
                    "",
                    "```json",
                    _json_block(payload),
                    "```",
                ]
            )
        )

    def add_step(
        self,
        *,
        step: str,
        purpose: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        key_points: Dict[str, Any] | None = None,
    ) -> None:
        blocks = [f"## {step}", "", f"- 目的：{purpose}"]
        if key_points:
            blocks.append("- 关键信息：")
            for key, value in key_points.items():
                blocks.append(f"  - {key}: {value}")
        blocks.extend(
            [
                "",
                "### 输入",
                "```json",
                _json_block(input_data),
                "```",
                "",
                "### 输出",
                "```json",
                _json_block(output_data),
                "```",
            ]
        )
        if self._pending_llm_block:
            blocks.extend(["", self._pending_llm_block])
            self._pending_llm_block = None
        self._sections.append("\n".join(blocks))

    def add_llm(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        raw_response: str,
        parsed_response: Dict[str, Any] | None,
    ) -> None:
        payload = {
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "raw_response": raw_response,
            "parsed_response": parsed_response,
        }
        self._pending_llm_block = "\n".join(
            [
                "### LLM 调用",
                "```json",
                _json_block(payload),
                "```",
            ]
        )

    def add_final(self, *, result: Dict[str, Any]) -> None:
        summary = {
            "recommendation": result.get("recommendation"),
            "match_score": result.get("match_score"),
            "job_type": result.get("job_type"),
            "summary": result.get("summary"),
            "meta": result.get("meta"),
        }
        self._sections.append(
            "\n".join(
                [
                    "## 最终输出摘要",
                    "",
                    "```json",
                    _json_block(summary),
                    "```",
                ]
            )
        )

    def add_error(
        self,
        *,
        step: str,
        error: str,
        details: Dict[str, Any] | None = None,
    ) -> None:
        blocks = [f"## {step}", "", f"- 错误：{error}"]
        if details:
            blocks.extend(
                [
                    "",
                    "### 错误详情",
                    "```json",
                    _json_block(details),
                    "```",
                ]
            )
        if self._pending_llm_block:
            blocks.extend(["", self._pending_llm_block])
            self._pending_llm_block = None
        self._sections.append("\n".join(blocks))

    def write(self) -> Path:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = LOG_DIR / f"{self.trace_id}.md"
        content = "\n\n".join(
            [
                f"# Analyze Trace: {self.trace_id}",
                "",
                f"- 创建时间：{self.created_at}",
                *self._sections,
            ]
        ).strip() + "\n"
        path.write_text(content, encoding="utf-8")
        return path
