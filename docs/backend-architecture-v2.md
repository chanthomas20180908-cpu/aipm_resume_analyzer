# 后端架构实现 V2

> 2026-07-01 更新：项目已新增 v3 LLM-Native 工作流（`/analyze/v3`），对应 `app/workflows/analyze_job_fit_v3.py`。v2 工作流（`/analyze`）继续保留。本文档仍只描述 v2 架构，v3 架构见 [docs/backend-logic-current.md](docs/backend-logic-current.md)。

## 核心假设

- 当前后端已经从单文件分析器切到 `workflow + capabilities` 的 v2 架构。
- 顶层只负责流程编排，具体规则和逻辑下沉到能力层。
- 这份文档描述的是“当前已经落地的实现架构”，不是未来设计草图。

## 目标

说明当前 v2 后端的：

1. 目录结构
2. 主链路调用顺序
3. 模块职责边界
4. 兼容字段策略
5. 当前已实现和未实现部分

## 目录结构

当前 `app/` 目录已经拆成以下几层：

```text
app/
  main.py
  trace_logger.py
  jd_parser.py
  resume_parser.py
  llm_client.py
  prompts.py
  prompts_v3.py        # v3 工作流 prompt
  analyzer.py
  capabilities/
    jd_analysis.py
    candidate_analysis.py
    match_scoring.py
    recommendation.py
    narration.py
    jd_analysis_v3.py        # v3 JD 分析
    candidate_analysis_v3.py # v3 候选人分析
  workflows/
    analyze_job_fit.py
    analyze_job_fit_v3.py    # v3 三步工作流
```

说明：`prompts_v3.py`、`*_v3.py`、`analyze_job_fit_v3.py` 服务 `/analyze/v3`，v2 架构本身不依赖它们。

## 分层说明

### 1. `workflows/`

#### 作用

负责顶层流程编排。

#### 当前文件

- [analyze_job_fit.py](/Users/test/code/aipm_resume_analyzer/app/workflows/analyze_job_fit.py)

#### 职责

- 接收顶层输入
- 按顺序调用能力模块
- 汇总最终返回结构
- 处理兼容字段聚合

#### 不负责

- 具体抽取规则
- 具体评分公式
- recommendation 映射细节
- prompt 内容

### 2. `capabilities/`

#### 作用

承载业务能力模块，每个模块负责一段稳定职责。

#### 当前模块

- [jd_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/jd_analysis.py)
- [candidate_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/candidate_analysis.py)
- [match_scoring.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/match_scoring.py)
- [recommendation.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/recommendation.py)
- [narration.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/narration.py)

每个能力模块都应：

- 输入明确
- 输出明确
- 不依赖顶层页面逻辑
- 可被 workflow 编排调用

### 3. `parsers`

当前还没有单独建 `parsers/` 目录，但解析职责已经存在：

- [jd_parser.py](/Users/test/code/aipm_resume_analyzer/app/jd_parser.py)
- [resume_parser.py](/Users/test/code/aipm_resume_analyzer/app/resume_parser.py)

它们负责确定性文本抽取与归一化，是能力层的底层依赖。

### 4. `llm`

当前还没有拆独立 `llm/` 目录，但相关逻辑已经集中在：

- [llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py)
- [prompts.py](/Users/test/code/aipm_resume_analyzer/app/prompts.py)

职责是：

- 判断 LLM 是否可用
- 调用 DashScope 兼容 OpenAI 接口
- 处理 JSON 输出
- 提供 narrator 增强能力

## 主链路

当前 `/analyze` 已经切到 v2 workflow：

- [main.py](/Users/test/code/aipm_resume_analyzer/app/main.py)

v2 调用顺序如下：

```text
/analyze
  -> workflows.analyze_job_fit.run(...)
    -> capabilities.jd_analysis.run(...)
      -> llm_client.extract_jd_with_llm(...) 或 jd_parser.build_jd_analysis(...) fallback
    -> capabilities.candidate_analysis.run(...)
      -> llm_client.extract_candidate_with_llm(...) 或 resume_parser.build_candidate_analysis(...) fallback
    -> capabilities.match_scoring.run(...)
    -> capabilities.recommendation.run(...)
    -> capabilities.narration.run(...)
      -> llm_client.enhance_v2_narration(...) 或规则 fallback
  -> 返回最终结果
```

新增 `/analyze/v3` 为 LLM-Native 三步工作流：

```text
/analyze/v3
  -> workflows.analyze_job_fit_v3.run(...)
    -> capabilities.jd_analysis_v3.run(...)
      -> llm_client.extract_jd_v3(...)
    -> capabilities.candidate_analysis_v3.run(...)
      -> llm_client.extract_candidate_v3(...，带 job_analysis)
    -> llm_client.synthesize_final_v3(...)
      -> 直接输出 recommendation / match_score / summary / strengths / risks / next_actions
  -> 返回最终结果
```

前端首页默认请求 `/analyze/v3`；当环境未配置 LLM key 导致 v3 返回 503 时，自动 fallback 到 `/analyze`（v2）。因此 `/analyze` 继续作为兜底链路保留。

当前实现里，每次 `/analyze` 或 `/analyze/v3` 都会同时创建一个 `TraceLogger`，把整条链路落盘到：

- `logs/{trace_id}.md`

返回结果的 `meta` 中会带：

- `trace_id`
- `trace_log_path`

## 各模块职责

### `jd_analysis.run(raw_jd_text)`

#### 输入

- 原始 JD 文本

#### 输出

- `job_analysis`
- `meta.jd_extraction`
- `meta.jd_extraction_meta`

#### 依赖

- 优先：`llm_client.extract_jd_with_llm`
- Fallback：`jd_parser.build_jd_analysis`

### `candidate_analysis.run(resume_text, job_analysis=None)`

#### 输入

- 原始简历文本
- （可选）`job_analysis`，用于判断角色错配

#### 输出

- `candidate_analysis`
- `meta.resume_extraction`
- `meta.resume_extraction_meta`

#### 依赖

- 优先：`llm_client.extract_candidate_with_llm`
- Fallback：`resume_parser.build_candidate_analysis`

### `match_scoring.run(job_analysis, candidate_analysis, user_goal)`

#### 输入

- `job_analysis`
- `candidate_analysis`
- `user_goal`

#### 输出

- `gate_check_result`
- `dimension_scores`
- `weighted_match_score`
- `confidence`
- `non_compensatory_gaps`
- `compensatory_gaps`
- `match_highlights`
- `job_risk_level`

#### 当前实现说明

已实现：

- gate check
- 7 维评分
- 权重计算
- confidence
- job risk 汇总

当前仍属于 v2 第一版，后续仍需要调规则细节。

### `recommendation.run(match_result, job_analysis, user_goal)`

#### 输入

- `match_result`
- `job_analysis`
- `user_goal`

#### 输出

- `recommendation`
- `recommendation_reason`
- `job_risk_level`
- `candidate_readiness_level`

#### 当前实现说明

recommendation 基于：

- gate 是否通过
- 综合分区间
- 岗位风险
- 不可补偿缺口
- user goal 的轻量偏置

### `narration.run(...)`

#### 输入

- 原始 JD / 简历
- `job_analysis`
- `candidate_analysis`
- `match_result`
- `recommendation_result`

#### 输出

- `summary`
- `strengths`
- `risks`
- `next_actions`
- `meta.llm`

#### 当前实现说明

这一层支持两条分支：

- `LLM 可用`：调用 `enhance_v2_narration`
- `LLM 不可用`：使用规则 fallback 文案

注意：

- 当前 Step 1/2 默认也调用 LLM 做结构化抽取
- Step 5 仍只调用一次 LLM 做文案增强
- LLM 调用信息会作为 `步骤 5` 的子块写入 trace 日志
- Step 1/2 的 LLM 调用状态记录在对应 capability 返回的 `meta` 中

## Trace 日志

当前 v2 架构已经内置轻量流程日志。

### 目标

- 看清一次分析从输入到输出的完整链路
- 快速定位某一步的输入、输出和关键结论
- 保留 LLM request / response 供 prompt 调试使用

### 记录内容

每次分析的 trace 文件包含：

1. `请求输入`
2. `步骤 1: JD 分析`
3. `步骤 2: 候选人分析`
4. `步骤 3: 匹配评分`
5. `步骤 4: 推荐结论`
6. `步骤 5: 文案生成`
7. 如调用 LLM，则在 `步骤 5` 下追加 `LLM 调用`
8. `最终输出摘要`

## 返回结构

当前返回分两层：

### 1. v2 主结构

```json
{
  "job_analysis": {},
  "candidate_analysis": {},
  "match_result": {},
  "recommendation_result": {},
  "meta": {}
}
```

### 2. 兼容字段

为了不立即打坏前端，当前还保留：

- `recommendation`
- `match_score`
- `job_type`
- `summary`
- `strengths`
- `risks`
- `next_actions`

这些字段本质上是从 v2 结构中映射出来的兼容层。

## 兼容策略

当前系统采用的是：

- `v2 主链路`
- `v1 风格兼容输出`

也就是：

- 内部逻辑按 v2 跑
- 对外结果暂时保留旧字段，方便前端继续使用

这是一种过渡兼容，不建议长期维持。

## 当前已实现部分

### 已完成

- workflow 顶层编排
- JD 结构化抽取
- 简历结构化抽取
- v2 评分主链路
- recommendation 模块
- narrator 模块
- LLM narrator 分支
- 旧前端兼容字段输出

### 尚未完成

- v2 字段驱动的前端展示重构
- v2 LLM 抽取质量持续校准
- 更完整的 v2 规则校准
- 真实评测集驱动的 v2 阈值调优

说明：`job_family`、`business_domain` 等内部枚举的中文映射已在 v3 工作流中通过“英文 key + 中文枚举值”方式解决，v2 不再扩展。

## 当前限制

### 1. Parser 默认由 LLM 抽取，规则版作为 fallback

当前 `app/jd_parser.py` 和 `app/resume_parser.py` 仍保留，但不再优先调用：

- 环境配置了 LLM key 时，优先走 `llm_client.extract_jd_with_llm` / `extract_candidate_with_llm`
- LLM 未配置、超时或返回异常时，自动回退到规则 parser
- 规则 parser 继续作为兜底，保证服务不中断

### 2. narrator 已切 v2，但文案仍偏保守

LLM narrator 目前已经接在 v2 结构后，但结果语气和细节仍需要调优。

### 3. 内部枚举直接暴露给前端

当前 `job_type` 返回的是类似：

- `enterprise_collaboration`
- `ai_workflow_tool`

这对产品结果页不够友好，后续需要做映射层。

## 推荐下一步

当前最值得做的不是继续扩文档，而是继续收口输出层：

1. 给 `job_family / business_domain / readiness / risk level` 做中文映射
2. 用 v2 字段驱动前端结果页
3. 再开始调 narrator 和评分细节

## 非目标

这份文档不定义：

- 产品需求
- prompt 细节
- 精确打分公式推导
- 未来数据库设计

这些内容已经在其他文档中定义，或应在后续文档中继续补充。
