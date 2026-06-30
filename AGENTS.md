# AGENTS.md

## 项目概览

这是一个面向 `AI 产品经理求职者` 的岗位判断工具。

当前实现形态：

- 后端：`FastAPI`
- 前端：静态 `HTML + CSS + JS`
- 判断主链路：`workflow + capabilities` 的 v2 架构
- 文案增强：真实 LLM，可选启用
- 调试方式：按次落盘的 Markdown 流程日志

当前产品目标不是做完整求职平台，而是先跑通：

`JD + 简历 + 用户背景 -> 岗位判断 -> 风险与建议`

## 目录结构

- `app/main.py`
  FastAPI 入口，提供页面和 API。

- `app/workflows/`
  顶层流程编排，当前 `/analyze` 主链路从这里进入。

- `app/capabilities/`
  业务能力层，包含 JD 分析、候选人分析、评分、推荐、文案生成。

- `app/trace_logger.py`
  单次分析流程日志生成器。

- `app/analyzer.py`
  旧版规则分析器，当前主接口已不再直接依赖它。

- `app/llm_client.py`
  LLM 调用层，负责模型调用、JSON 解析、结果合并、fallback。

- `app/prompts.py`
  提示词统一维护位置。

- `static/`
  前端静态页面、样式和交互脚本。

- `docs/`
  项目文档，包括调研、MVP、后端逻辑、prompt 设计说明。

- `logs/`
  单次分析日志目录，按 `trace_id` 生成 Markdown 文件。

- `requirements.txt`
  Python 依赖。

- `main.py`
  本地启动提示入口，不承载业务逻辑。

## 当前接口

- `GET /`
  返回首页。

- `GET /health`
  返回服务状态和 `llm_configured`。

- `GET /demo`
  返回一组示例输入。

- `POST /analyze`
  核心分析接口。

## 运行方式

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

启动服务：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

访问地址：

```text
http://127.0.0.1:8000
```

## 环境变量

当前真实支持的环境变量：

- `DASHSCOPE_API_KEY`
  DashScope 兼容 OpenAI 接口的 API Key。优先使用。

- `OPENAI_API_KEY`
  通用兼容 Key。没有 `DASHSCOPE_API_KEY` 时读取。

- `OPENAI_BASE_URL`
  可选，默认是：
  `https://dashscope.aliyuncs.com/compatible-mode/v1`

- `OPENAI_MODEL`
  可选，默认是：
  `qwen-plus`

## 当前架构约定

- 规则层负责最终判断：
  - `recommendation`
  - `match_score`
  - `job_type`

- LLM 当前只在 `步骤 5: 文案生成` 调用一次，负责结果增强：
  - `summary`
  - `strengths`
  - `risks`
  - `next_actions`

- 如果 LLM 不可用或返回异常：
  - 自动 fallback 到纯规则结果

- 提示词不得散落在调用代码里：
  - 统一维护在 `app/prompts.py`

- 每次 `/analyze` 都会生成一份流程日志：
  - 文件位于 `logs/{trace_id}.md`
  - 返回里会带 `meta.trace_id` 和 `meta.trace_log_path`

## 文档入口

当前主要文档：

- `docs/ai-pm-job-tool-plan.md`
  最初产品方案草案。

- `docs/ai-pm-job-pain-research-report-2026-06-17.md`
  AI PM 求职痛点网络调研报告。

- `docs/ai-pm-job-tool-mvp.md`
  MVP 定义文档。

- `docs/backend-logic-current.md`
  当前后端真实实现说明。

- `docs/backend-architecture-v2.md`
  当前 v2 后端架构实现说明。

- `docs/prompt-design-current.md`
  当前 prompt 设计说明。

## 测试集约定

- 测试集位于 `data/test_cases_v1/`，采用 MECE 双轴分类（真 AI/伪 AI × 强匹配/可迁移/有短板/硬伤）。
- 当前 8 个 case：001-005, 008-010（006/007 已删除，009/010 为新建）。
- 金标数据独立存储在 `data/test_cases_v1/golden/`（与输入分离）。
- 测试集相关文档：
  - `data/test_cases_v1/README.md` — 测试集目录索引（按 A1-D2 矩阵组织，含文件路径总览）
  - `docs/testset-directions-v2.md` — 分类体系
  - `docs/golden-label-schema-v1.md` — 金标方案
  - `docs/testset-case-mapping-v2.md` — 已归档，仅作历史参考
- 旧版 `docs/testset-sourcing-directions-v1.md` 已归档，仅作历史参考。

## 协作约束

- 禁止任何 Git 操作。

- 写操作或外部效果动作之前：
  先给三行预告，再执行。

- 优先小步修改，不做无关重构。

- 修改代码后，同步更新相关文档，避免代码和文档漂移。

- 讨论和实现都以当前真实代码为准，不依赖历史假设。
