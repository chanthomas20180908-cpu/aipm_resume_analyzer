# 后端 Schema V2

## 核心假设

- V2 schema 同时服务 3 层：规则引擎、LLM 增强层、前端结果页。
- 最终投递建议必须由规则层决定。LLM 可以参与抽取和解释，但不能决定结论。
- 方法论必须显性体现在返回结构里，不能只藏在代码逻辑中。

## 目标

把当前较扁平的返回结果升级为 4 层结构：

1. `job_analysis`
2. `candidate_analysis`
3. `match_result`
4. `recommendation_result`

这 4 层对应完整判断链路，也方便后续调试、扩展和前端展示。

## 流程结构

### 1. `job_analysis`

#### 干什么

把原始 JD 文本转成结构化的岗位画像和能力要求。

#### 输入

- `raw_jd_text`

#### 输出

```json
{
  "job_profile": {
    "job_title": "",
    "job_family": "",
    "business_domain": "",
    "company_stage": "",
    "company_size": "",
    "ai_maturity": "",
    "delivery_mode": "",
    "location": "",
    "salary_range": ""
  },
  "job_requirements": {
    "must_have": [],
    "preferred": [],
    "core_competencies": [],
    "technical_depth": "",
    "success_metrics": [],
    "non_negotiables": []
  },
  "job_risk_flags": {
    "pseudo_ai_risk": "",
    "coordination_heavy_risk": "",
    "scope_bloat_risk": "",
    "unclear_metric_risk": ""
  }
}
```

#### 字段说明

- `job_family`：岗位类型，例如内部平台、企业协作、AI 工作流、机器人交互、增长型 AI PM 等。
- `business_domain`：业务领域，例如营销、协作、教育、机器人、知识管理等。
- `ai_maturity`：AI 成熟度，反映岗位到底是概念包装、应用落地还是深度交付。
- `delivery_mode`：交付模式，例如 `0_to_1`、`1_to_10`、平台型、场景型。
- `must_have`：JD 中明确表达的必要条件。
- `preferred`：JD 中表达为优先、加分项、方向性优势的条件。
- `core_competencies`：从 JD 中归一化出来的核心能力维度。
- `success_metrics`：岗位成功标准，可能来自显式指标，也可能来自高置信度推断。
- `non_negotiables`：后续匹配中视为不可补偿的硬要求。

#### 为什么需要这一层

这一层对应 `岗位分析（job analysis）`。系统必须先理解“这个岗位到底要什么人”，才能判断候选人是否匹配。

### 2. `candidate_analysis`

#### 干什么

把简历文本转成证据，而不是只看表面措辞。

#### 输入

- `resume_text`

#### 输出

```json
{
  "candidate_profile": {
    "experience_years": "",
    "domain_experience": [],
    "ai_experience_level": "",
    "product_background": ""
  },
  "candidate_evidence": {
    "project_evidence": [],
    "delivery_evidence": [],
    "metrics_evidence": [],
    "technical_evidence": [],
    "collaboration_evidence": []
  },
  "missing_evidence": {
    "ai_landing_gap": [],
    "metric_gap": [],
    "domain_gap": [],
    "technical_gap": []
  }
}
```

#### 字段说明

- `candidate_profile`：候选人的背景信息。
- `candidate_evidence`：简历中真正能支撑判断的证据，如项目、交付、指标、技术协作、跨团队推动。
- `missing_evidence`：当前证据缺口，强调的是“缺证明”而不是武断地说“没有能力”。

#### 为什么需要这一层

这层让系统基于证据判断候选人，而不是基于关键词或语言包装做表面匹配。

### 3. `match_result`

#### 干什么

把岗位要求和候选人证据做结构化比对，并生成可解释的匹配结果。

#### 输入

- `job_analysis`
- `candidate_analysis`
- `user_goal`

#### 输出

```json
{
  "gate_check_result": {
    "passed": true,
    "failed_reasons": []
  },
  "dimension_scores": {
    "ai_understanding": 0,
    "scenario_abstraction": 0,
    "workflow_design": 0,
    "delivery_execution": 0,
    "data_metrics": 0,
    "stakeholder_push": 0,
    "business_fit": 0
  },
  "weighted_match_score": 0,
  "confidence": 0,
  "non_compensatory_gaps": [],
  "compensatory_gaps": [],
  "match_highlights": []
}
```

#### 字段说明

- `gate_check_result`：先判定硬门槛是否通过。
- `dimension_scores`：分维度匹配得分，用于解释最终结论。
- `weighted_match_score`：归一化后的综合分数。
- `confidence`：当前判断的置信度，受证据完整性和文本清晰度影响。
- `non_compensatory_gaps`：不可补偿缺口，其他优势不能抵消。
- `compensatory_gaps`：可补偿缺口，可以靠强项目、强结果或相邻能力补回来。
- `match_highlights`：最关键的匹配理由。

#### 为什么需要这一层

这一层是专业判断核心。它把“匹不匹配”拆成：

- 是否卡在硬门槛
- 哪些维度匹配
- 哪些缺口严重
- 哪些缺口可补

没有这层，系统就会退化成不透明打分器。

### 4. `recommendation_result`

#### 干什么

把结构化匹配结果转成用户可以直接使用的投递建议和行动建议。

#### 输入

- `match_result`
- `job_analysis`
- `candidate_analysis`

#### 输出

```json
{
  "recommendation": "",
  "recommendation_reason": "",
  "job_risk_level": "",
  "candidate_readiness_level": "",
  "summary": "",
  "strengths": [],
  "risks": [],
  "next_actions": []
}
```

#### 字段说明

- `recommendation`：`冲 / 可投 / 谨慎 / 避开`
- `recommendation_reason`：结论原因，必须能追溯到规则结果。
- `job_risk_level`：岗位风险高低。
- `candidate_readiness_level`：候选人当前准备度，如 ready / near-ready / stretch / not-ready。
- `summary`：一句话结论。
- `strengths`、`risks`、`next_actions`：用户可直接理解和行动的结果层。

#### 为什么需要这一层

这层负责把专业判断转成产品输出。用户不需要看到内部流程，但必须拿到明确结论和下一步动作。

## 职责边界

### 规则层负责的字段

以下字段必须由规则层决定：

- `job_analysis`
- `match_result`
- `recommendation_result.recommendation`
- `recommendation_result.recommendation_reason`
- `recommendation_result.job_risk_level`
- `recommendation_result.candidate_readiness_level`

### LLM 可参与的字段

LLM 只能在受约束范围内参与：

- `candidate_analysis` 的抽取辅助
- `recommendation_result.summary`
- `recommendation_result.strengths`
- `recommendation_result.risks`
- `recommendation_result.next_actions`

### 严格约束

LLM 不得：

- 修改 `recommendation`
- 编造简历证据
- 把 `preferred` 写成硬门槛
- 在没有来源的情况下补充事实

## 顶层最小返回结构

```json
{
  "job_analysis": {},
  "candidate_analysis": {},
  "match_result": {},
  "recommendation_result": {},
  "meta": {
    "version": "v2",
    "llm_used": false
  }
}
```

## 与当前 V1 的映射关系

当前 V1 字段大致可以映射为：

- `job_type` -> `job_analysis.job_profile.job_family`
- `match_score` -> `match_result.weighted_match_score`
- `recommendation` -> `recommendation_result.recommendation`
- `summary` -> `recommendation_result.summary`
- `strengths` -> `recommendation_result.strengths`
- `risks` -> `recommendation_result.risks`
- `next_actions` -> `recommendation_result.next_actions`

V2 相比 V1，新增了中间层：

- 岗位分析
- 候选人证据分析
- 缺口建模
- 置信度

## 推荐实现顺序

建议按这个顺序落地：

1. 增加 `job_analysis` 和 JD 归一化层
2. 增加 `candidate_analysis` 证据抽取层
3. 用 `match_result` 替代当前较扁平的打分逻辑
4. 把现有结果页输出迁移到 `recommendation_result`
5. 按新的职责边界重构 prompt

## 非目标

这份文档不定义：

- 具体 prompt 文案
- 具体打分公式
- 前端页面布局
- 数据库存储结构

这些应分别在独立文档中定义。
