# 后端 Schema V2

> 2026-07-01 更新：项目已新增 v3 工作流（`/analyze/v3`），使用不同的 schema 设计：英文 key + 中文枚举值，Step 3 由 LLM 直接输出 recommendation 和文案，不经过规则评分层。v2 schema 仍服务 `/analyze`。本文档主体描述 v2 schema，v3 差异见文末补充。

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
    "industry_domain": "",
    "company_stage": "",
    "company_size": "",
    "ai_maturity": "",
    "delivery_mode": "",
    "business_orientation": "",
    "role_perspective": "",
    "enterprise_type": "",
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
- `industry_domain`：垂直行业，例如保险、金融、医疗、教育、零售、电商等。
- `ai_maturity`：AI 成熟度，反映岗位到底是概念包装、应用落地还是深度交付。
- `delivery_mode`：交付模式，例如 `0_to_1`、`1_to_10`、平台型、场景型。
- `business_orientation`：岗位偏业务还是偏技术：`business-heavy`、`tech-heavy`、`hybrid`。
- `role_perspective`：JD 招的是 PM 还是工程师视角：`pm`、`engineer`、`hybrid`。
- `enterprise_type`：企业类型：`traditional_enterprise`、`ai_native`、`hybrid`。

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
    "product_background": "",
    "candidate_role_orientation": ""
  },
  "candidate_evidence": {
    "project_evidence": [],
    "delivery_evidence": [],
    "metrics_evidence": [],
    "technical_evidence": [],
    "collaboration_evidence": [],
    "product_evidence": [],
    "business_evidence": []
  },
  "missing_evidence": {
    "ai_landing_gap": [],
    "metric_gap": [],
    "domain_gap": [],
    "technical_gap": [],
    "product_gap": [],
    "business_gap": []
  },
  "role_mismatch_flag": false
}
```

#### 字段说明

- `candidate_profile`：候选人的背景信息。
- `candidate_role_orientation`：候选人本质是 PM、工程师、研究员还是无法判断：`pm`、`engineer`、`researcher`、`ambiguous`。
- `candidate_evidence`：简历中真正能支撑判断的证据，如项目、交付、指标、技术协作、跨团队推动。
  - `product_evidence`：产品经理视角证据（需求分析、roadmap、用户研究等）。
  - `business_evidence`：业务/商业视角证据（商业化、ROI、定价、市场调研等）。
- `missing_evidence`：当前证据缺口，强调的是“缺证明”而不是武断地说“没有能力”。
- `role_mismatch_flag`：当 JD 明确要求 PM 角色，而候选人明显是 engineer/researcher 时为 `true`。

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

LLM 默认负责 Step 1/2 结构化抽取，失败时 fallback 到规则版：

- `job_analysis`：由 `extract_jd_with_llm` 生成
- `candidate_analysis`：由 `extract_candidate_with_llm` 生成

LLM 在 Step 5 负责文案增强：

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

## v3 Schema 差异补充

2026-07-01 新增的 `/analyze/v3` 与 v2 schema 有以下差异：

1. **枚举值使用中文**
   - 例如 `business_orientation` 取值为 `"业务重"`、`"技术重"`、`"混合"`，而非 v2 的 `"business-heavy"` 等。
   - `core_competencies` 使用 `"AI理解"`、`"场景抽象"` 等中文标签。

2. **新增专家判断字段**
   - `job_requirements.implied_requirements`：JD 原文要求的潜台词解读。
   - `jd_core_judgment`：对岗位本质的一句话判断。
   - `candidate_match_summary`：对候选人匹配情况的一句话判断。

3. **删除对用户价值较低的字段**
   - v3 的 `job_profile` 不再包含 `job_title`、`company_stage`、`company_size`、`location`、`salary_range`。
   - v3 的 `job_requirements` 不再包含 `preferred`。

4. **终局输出结构不同**
   - v3 不再返回 `match_result` 和 `recommendation_result`。
   - v3 直接返回顶层字段：`recommendation`、`match_score`、`summary`、`strengths`、`risks`、`next_actions`。
   - v3 的 `recommendation` 和 `match_score` 由 Step 3 LLM 直接生成，不经过规则层。

## 非目标

这份文档不定义：

- 具体 prompt 文案
- 具体打分公式
- 前端页面布局
- 数据库存储结构

这些应分别在独立文档中定义。
