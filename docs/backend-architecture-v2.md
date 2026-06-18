# 后端架构实现 V2

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
  jd_parser.py
  resume_parser.py
  llm_client.py
  prompts.py
  analyzer.py
  capabilities/
    jd_analysis.py
    candidate_analysis.py
    match_scoring.py
    recommendation.py
    narration.py
  workflows/
    analyze_job_fit.py
```

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

调用顺序如下：

```text
/analyze
  -> workflows.analyze_job_fit.run(...)
    -> capabilities.jd_analysis.run(...)
      -> jd_parser.build_jd_analysis(...)
    -> capabilities.candidate_analysis.run(...)
      -> resume_parser.build_candidate_analysis(...)
    -> capabilities.match_scoring.run(...)
    -> capabilities.recommendation.run(...)
    -> capabilities.narration.run(...)
      -> llm_client.enhance_v2_narration(...) 或规则 fallback
  -> 返回最终结果
```

## 各模块职责

### `jd_analysis.run(raw_jd_text)`

#### 输入

- 原始 JD 文本

#### 输出

- `job_analysis`
- `meta.jd_extraction`
- `meta.jd_extraction_meta`

#### 依赖

- `jd_parser.build_jd_analysis`

### `candidate_analysis.run(resume_text)`

#### 输入

- 原始简历文本

#### 输出

- `candidate_analysis`
- `meta.resume_extraction`

#### 依赖

- `resume_parser.build_candidate_analysis`

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

- `job_family`、`business_domain` 等内部枚举的中文映射
- v2 字段驱动的前端展示重构
- JD extractor / resume extractor 的 LLM 版本
- 更完整的规则校准
- 真实评测集驱动的阈值调优

## 当前限制

### 1. Parser 仍是规则版

当前 JD / 简历解析仍是启发式规则抽取，不是 LLM 抽取版。

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
