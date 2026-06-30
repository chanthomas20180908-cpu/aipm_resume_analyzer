# AI PM 岗位判断工具

一个面向 `AI 产品经理求职者` 的岗位判断工具。

当前目标很明确：

- 输入 `JD + 简历 + 用户背景`
- 输出 `岗位画像 + 匹配判断 + 风险 + 下一步动作`
- 先跑通可验证的本地 MVP，而不是完整平台

## 当前实现

- 后端：`FastAPI`
- 前端：静态 `HTML + CSS + JS`
- 主链路：`workflow + capabilities` 的 v2 架构
- 决策方式：规则判断主导
- LLM 作用：只参与 `文案生成`，不直接改最终 recommendation
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
  FastAPI 入口。
- `app/workflows/`
  顶层流程编排。
- `app/capabilities/`
  JD 分析、候选人分析、评分、推荐、文案生成。
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
  核心分析接口。

## 当前分析主链路

```text
/analyze
  -> workflows.analyze_job_fit.run(...)
    -> jd_analysis
    -> candidate_analysis
    -> match_scoring
    -> recommendation
    -> narration
      -> 如已配置 LLM，则调用一次 enhance_v2_narration(...)
  -> 返回结果
```

关键点：

- 当前每次分析最多只调用一次 LLM
- LLM 只在 `步骤 5: 文案生成` 参与
- recommendation 仍由规则层决定

## 日志

每次 `/analyze` 都会生成一份流程日志：

- 目录：`logs/`
- 文件名：`{trace_id}.md`

日志内容包括：

- 请求输入
- `步骤 1: JD 分析`
- `步骤 2: 候选人分析`
- `步骤 3: 匹配评分`
- `步骤 4: 推荐结论`
- `步骤 5: 文案生成`
- 如走 LLM，会在 `步骤 5` 下记录 `LLM 调用`
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
