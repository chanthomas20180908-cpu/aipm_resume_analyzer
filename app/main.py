from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.llm_client import llm_is_configured
from app.workflows.analyze_job_fit import run as analyze_job_fit_v2


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AI PM Job Tool MVP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeRequest(BaseModel):
    jd_text: str = Field(min_length=30)
    resume_text: str = Field(min_length=30)
    user_level: Literal["新人", "转岗PM", "有经验PM", "有AI项目经验"]
    goal: Literal["求稳", "冲高薪", "转AI", "找长期主线"]


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "llm_configured": llm_is_configured()}


@app.get("/demo")
def demo() -> dict:
    return {
        "jd_text": (
            "负责 AI Agent 产品规划与落地，围绕企业知识库、工作流自动化和智能助手场景，"
            "完成需求分析、Prompt 设计、效果评估和跨团队推进，对用户体验和业务指标负责。"
        ),
        "resume_text": (
            "3 年产品经理经验，负责 B 端协作工具产品规划与需求分析，推动研发、设计、运营协作上线。"
            "做过知识库问答和自动化工作流原型，能使用 API 和 SQL 进行基础分析，曾将流程效率提升 18%。"
        ),
        "user_level": "转岗PM",
        "goal": "转AI",
    }


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    result = analyze_job_fit_v2(
        jd_text=payload.jd_text,
        resume_text=payload.resume_text,
        user_level=payload.user_level,
        goal=payload.goal,
    )
    if "llm" not in result.get("meta", {}):
        result["meta"]["llm"] = {
            "used": False,
            "provider": "rule-fallback",
            "model": None,
        }
    if not llm_is_configured():
        result["meta"]["llm"]["used"] = False
    return result
