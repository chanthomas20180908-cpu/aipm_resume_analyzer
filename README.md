# AI PM 岗位判断工具

一个面向 `AI 产品经理求职者` 的岗位判断工具。

当前目标很明确：

- 输入 `JD + 简历 + 用户背景`
- 输出 `岗位画像 + 匹配判断 + 风险 + 下一步动作`
- 先跑通可验证的本地 MVP，而不是完整平台

## 当前实现

- 后端：`FastAPI`
- 前端：静态 `HTML + CSS + JS`
- 主链路：
  - v2：`workflow + capabilities` 架构，规则判断主导最终 recommendation，LLM 负责 Step 1/2 结构化抽取和 Step 5 文案增强。
  - v3（新增）：三步 LLM-Native 工作流，JD 分析、候选人分析、终局判断均走 LLM，不再经过规则评分层。
- 决策方式：
  - v2：规则判断主导最终 recommendation。
  - v3：大模型直接输出 recommendation、match_score 和文案。
- LLM 作用：
  - v2：`JD/简历结构化抽取` + `文案生成`，均可在未配置或异常时 fallback 到规则版。
  - v3：JD/简历结构化抽取 + 终局判断，全链路 LLM，无 key 时返回 503。
- 调试能力：按次生成完整流程日志

## 目录结构

```text
app/
  main.py
  trace_logger.py
  jd_parser.py
  resume_parser.py
  llm_client.py
  prompts.py
  prompts_v3.py
  analyzer.py
  capabilities/
  workflows/
docs/
static/
data/
logs/
requirements.txt
main.py
AGENTS.md
```

说明：

- `app/main.py`
  FastAPI 入口，提供 `/analyze` 和 `/analyze/v3`。
- `app/workflows/`
  顶层流程编排，包含 v2 (`analyze_job_fit.py`) 和 v3 (`analyze_job_fit_v3.py`)。
- `app/capabilities/`
  JD 分析、候选人分析、评分、推荐、文案生成；v3 对应模块带 `_v3` 后缀。
- `app/prompts.py` / `app/prompts_v3.py`
  分别维护 v2 和 v3 的提示词。
- `app/trace_logger.py`
  单次分析日志生成器。
- `static/`
  前端页面与交互。
- `docs/`
  设计、架构与调研文档。
- `logs/`
  单次分析链路日志，按 `trace_id` 落盘。

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

- `DASHSCOPE_API_KEY`
  DashScope 兼容 OpenAI 接口的 API Key，优先读取。
- `OPENAI_API_KEY`
  通用兼容 Key，作为兜底。
- `OPENAI_BASE_URL`
  可选，默认：
  `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `OPENAI_MODEL`
  可选，默认：
  `qwen-plus`

## 当前接口

- `GET /`
  返回首页。
- `GET /health`
  返回服务状态与 `llm_configured`。
- `GET /demo`
  返回示例输入。
- `POST /analyze`
  核心分析接口（v2 工作流，保留旧前端兼容）。
- `POST /analyze/v3`
  新版分析接口（v3 LLM-Native 三步工作流，必须配置 LLM key）。

前端首页默认调用 `/analyze/v3`；当环境未配置 LLM key 导致 v3 返回 503 时，页面会自动 fallback 到 `/analyze`（v2）。

## 当前分析主链路

```text
/analyze
  -> workflows.analyze_job_fit.run(...)
    -> jd_analysis
      -> 优先 LLM 抽取（extract_jd_with_llm），失败 fallback 到 jd_parser
    -> candidate_analysis
      -> 优先 LLM 抽取（extract_candidate_with_llm，带 job_analysis），失败 fallback 到 resume_parser
    -> match_scoring
    -> recommendation
    -> narration
      -> 如已配置 LLM，则调用 enhance_v2_narration(...)
  -> 返回结果
```

关键点：

- 当前每次分析最多调用 3 次 LLM（Step 1、Step 2、Step 5）
- LLM 在 Step 1/2 负责结构化抽取，在 Step 5 负责文案增强
- Step 1/2 失败时自动 fallback 到规则版 parser，不影响接口可用性
- recommendation 仍由规则层决定

## v3 分析主链路

```text
/analyze/v3
  -> workflows.analyze_job_fit_v3.run(...)
    -> jd_analysis_v3
      -> llm_client.extract_jd_v3(...)
    -> candidate_analysis_v3
      -> llm_client.extract_candidate_v3(...，带 job_analysis)
    -> llm_client.synthesize_final_v3(...)
      -> 直接输出 recommendation / match_score / summary / strengths / risks / next_actions
  -> 返回结果
```

关键点：

- 三步均调用 LLM，无 LLM key 时返回 503。
- Step 1/2 输出英文 key + 中文枚举值/内容，可直接阅读。
- Step 1 增加 `implied_requirements` 和 `jd_core_judgment`。
- Step 2 增加 `candidate_match_summary`。
- 终局判断由 LLM 直接完成，不经过规则评分层。

## 日志

每次 `/analyze` 或 `/analyze/v3` 都会生成一份流程日志：

- 目录：`logs/`
- 文件名：`{trace_id}.md`

v2 日志内容包括：

- 请求输入
- `步骤 1: JD 分析`
- `步骤 2: 候选人分析`
- `步骤 3: 匹配评分`
- `步骤 4: 推荐结论`
- `步骤 5: 文案生成`
- 如走 LLM，会在对应步骤下记录 `LLM 调用`
- 最终输出摘要

v3 日志内容包括：

- 请求输入
- `步骤 1: JD 分析`（含 LLM 调用）
- `步骤 2: 候选人分析`（含 LLM 调用）
- `步骤 3: 终局判断`（含 LLM 调用）
- 最终输出摘要

接口返回的 `meta` 中包含：

- `trace_id`
- `trace_log_path`

## 测试集

测试集用于验证系统判断准确性，采用 MECE 双轴分类：

- 横轴：岗位质量（真 AI 岗 / 伪 AI 岗）
- 纵轴：匹配类型（强匹配 / 可迁移 / 有短板 / 硬伤）

当前 8 个 case 覆盖 6 个主格子 + 1 个跨域变体：

| Case | 方向 | 预期结论 |
|------|------|----------|
| 002 | 真 AI + 强匹配 | 冲 |
| 008 | 真 AI + 强匹配（跨域） | 可投 |
| 001 | 真 AI + 可迁移 | 可投 |
| 005 | 真 AI + 有短板 | 谨慎 |
| 003 | 真 AI + 硬伤 | 避开 |
| 009 | 伪 AI + 强匹配 | 谨慎 |
| 010 | 伪 AI + 可迁移 | 避开 |
| 004 | 伪 AI + 有短板 | 避开 |

测试集文档：

- [`data/test_cases_v1/README.md`](data/test_cases_v1/README.md) — 测试集目录索引（按 A1-D2 矩阵组织）
- [docs/testset-directions-v2.md](docs/testset-directions-v2.md) — 分类体系设计
- [docs/golden-label-schema-v1.md](docs/golden-label-schema-v1.md) — 金标标注方案
- `data/test_cases_v1/golden/` — 8 个 case 的金标数据
- [docs/testset-case-mapping-v2.md](docs/testset-case-mapping-v2.md) — 历史归档：V2 矩阵设计过程

### A1 离线逻辑测试

标准 `A1` 样本 `case_002` 提供了一个离线逻辑评测入口，不经过 `/analyze`，因此不会在仓库 `logs/` 下生成 trace：

```bash
python3 scripts/run_a1_logic_test.py
```

默认输出：

- `/tmp/a1_case_002_actual.json`
- `/tmp/a1_case_002_eval.md`

详细说明见 [docs/a1-logic-test.md](docs/a1-logic-test.md)。

## 主要文档

- [AGENTS.md](/Users/test/code/aipm_resume_analyzer/AGENTS.md)
- [docs/backend-architecture-v2.md](/Users/test/code/aipm_resume_analyzer/docs/backend-architecture-v2.md)
- [docs/backend-schema-v2.md](/Users/test/code/aipm_resume_analyzer/docs/backend-schema-v2.md)
- [docs/raw-jd-extraction-v2.md](/Users/test/code/aipm_resume_analyzer/docs/raw-jd-extraction-v2.md)
- [docs/rule-scoring-v2.md](/Users/test/code/aipm_resume_analyzer/docs/rule-scoring-v2.md)
- [docs/prompt-redesign-v2.md](/Users/test/code/aipm_resume_analyzer/docs/prompt-redesign-v2.md)
- [docs/backend-logic-current.md](/Users/test/code/aipm_resume_analyzer/docs/backend-logic-current.md)
- [docs/prompt-design-current.md](/Users/test/code/aipm_resume_analyzer/docs/prompt-design-current.md)
