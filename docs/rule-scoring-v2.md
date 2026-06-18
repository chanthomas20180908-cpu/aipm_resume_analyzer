# 规则评分设计 V2

## 核心假设

- 评分系统的职责不是“猜用户能不能拿 offer”，而是判断“这个岗位当前值不值得投”。
- 最终结论必须来自结构化规则，而不是 LLM 自由发挥。
- 评分必须可解释，能拆成门槛、维度、风险、结论四部分。

## 目标

定义 V2 规则层如何基于：

- `job_analysis`
- `candidate_analysis`
- `user_goal`

生成：

- `gate_check_result`
- `dimension_scores`
- `weighted_match_score`
- `confidence`
- `non_compensatory_gaps`
- `compensatory_gaps`
- `recommendation`

## 整体判断流程

建议固定成 4 步：

1. `gate check`
2. `dimension scoring`
3. `risk adjustment`
4. `recommendation mapping`

这 4 步必须串行执行，不能直接用总分拍结论。

## 一、Gate Check

### 作用

先判断是否存在明显硬门槛。

这一步是 `non-compensatory` 逻辑。  
如果不通过，后续再高的维度分也不能直接变成“冲”。

### 输入来源

- `job_analysis.job_requirements.must_have`
- `job_analysis.job_requirements.non_negotiables`
- `candidate_analysis.candidate_profile`
- `candidate_analysis.candidate_evidence`
- `candidate_analysis.missing_evidence`

### 建议 gate 项

- `experience_gate`
  - JD 明确要求年限
  - 简历年限明显不足时触发

- `ai_delivery_gate`
  - JD 明确要求 AI 产品落地经验
  - 简历完全没有 AI 落地证据时触发

- `domain_gate`
  - JD 明确要求强领域背景
  - 简历领域证据明显不匹配时触发

- `technical_gate`
  - JD 明确要求较高技术理解
  - 简历没有相关技术证据时触发

### 输出格式

```json
{
  "passed": true,
  "failed_reasons": []
}
```

### 规则原则

- `must_have` 不一定全部都是 gate
- 只有明确的、不可补偿的要求才进入 gate
- 拿不准时，降级为维度扣分，不直接 gate fail

## 二、Dimension Scoring

### 作用

对岗位和候选人做分维度匹配。

### 评分维度

建议固定为 7 个核心维度：

1. `ai_understanding`
2. `scenario_abstraction`
3. `workflow_design`
4. `delivery_execution`
5. `data_metrics`
6. `stakeholder_push`
7. `business_fit`

每个维度建议统一使用 `0-5` 分。

### 维度定义

#### 1. `ai_understanding`

看什么：

- JD 对 AI / Agent / Prompt / 工作流 / 多模态 / 模型边界的要求
- 简历是否有 AI 产品理解或落地证据

高分条件：

- 有明确 AI 产品落地经验
- 能体现对模型能力边界、Prompt、Agent、评测等理解

低分条件：

- 只有泛产品经历
- AI 仅停留在包装或概念描述

#### 2. `scenario_abstraction`

看什么：

- JD 是否强调场景理解、问题定义、任务拆解
- 简历是否体现从复杂业务里提炼通用问题

高分条件：

- 有场景抽象、流程拆解、任务建模证据

#### 3. `workflow_design`

看什么：

- JD 是否强调工作流、平台能力、任务流转、功能编排
- 简历是否体现系统化产品方案设计

高分条件：

- 做过 AI workflow、平台能力、Agent 分流、知识流转等

#### 4. `delivery_execution`

看什么：

- JD 是否强调上线、交付、落地、迭代、跨团队推进
- 简历是否体现从需求到上线的完整交付

高分条件：

- 有从 0 到 1 或持续迭代交付证据

#### 5. `data_metrics`

看什么：

- JD 是否强调指标、评测、AB test、效果评估
- 简历是否体现指标设计、数据分析、结果复盘

高分条件：

- 有清晰指标责任和优化结果

#### 6. `stakeholder_push`

看什么：

- JD 是否强调跨团队协作、项目推动、资源协调
- 简历是否体现跨团队推进和复杂协作环境

高分条件：

- 有多角色协作和推进复杂项目的证据

#### 7. `business_fit`

看什么：

- JD 所在业务领域
- 简历是否有领域经验、业务理解、结果表达

高分条件：

- 有相近业务背景或明确的业务结果表达

### 单维度评分原则

每个维度可以按以下逻辑打分：

- `0`：完全无证据
- `1`：只有弱相关词，没有实质证据
- `2`：有零散证据，但不足以支撑岗位要求
- `3`：基本匹配，可投但不占优
- `4`：较强匹配，有明确证据
- `5`：强匹配，且证据质量高

### 输出格式

```json
{
  "ai_understanding": 0,
  "scenario_abstraction": 0,
  "workflow_design": 0,
  "delivery_execution": 0,
  "data_metrics": 0,
  "stakeholder_push": 0,
  "business_fit": 0
}
```

## 三、权重与综合分

### 作用

把 7 个维度转成可比较的综合结果。

### 默认权重建议

```json
{
  "ai_understanding": 0.22,
  "scenario_abstraction": 0.14,
  "workflow_design": 0.14,
  "delivery_execution": 0.16,
  "data_metrics": 0.12,
  "stakeholder_push": 0.10,
  "business_fit": 0.12
}
```

### 设计逻辑

- `ai_understanding` 权重最高  
  因为这是 AI PM 工具的核心区分点。

- `delivery_execution` 次高  
  因为很多 JD 真正要的是能把事情做成的人。

- `scenario_abstraction` 和 `workflow_design` 居中  
  它们决定候选人是不是“会设计 AI 产品”的人。

- `data_metrics`、`business_fit` 中等  
  它们影响岗位适配质量，但通常不是唯一决定项。

- `stakeholder_push` 权重最低  
  这是必要能力，但不能因为会协作就高估匹配度。

### 计算方式

建议：

1. 每个维度 `0-5`
2. 先归一化到 `0-100`
3. 再按权重加权

示意公式：

```text
weighted_match_score = Σ(维度分 / 5 * 100 * 权重)
```

最终得到 `0-100` 的综合匹配分。

## 四、Risk Adjustment

### 作用

把岗位风险从“岗位本身问题”里单独建模，避免只从候选人角度打分。

### 输入来源

- `job_analysis.job_risk_flags`

### 风险项

- `pseudo_ai_risk`
- `coordination_heavy_risk`
- `scope_bloat_risk`
- `unclear_metric_risk`

### 风险处理原则

- 风险不一定降低 match score
- 风险主要影响 `recommendation` 和 `job_risk_level`
- 高岗位风险时，即使匹配度高，也不一定给“冲”

### 调整建议

- 若 `pseudo_ai_risk = high`
  - recommendation 上限设为 `谨慎`

- 若 `coordination_heavy_risk = high` 且 `ai_understanding` 要求低
  - 可直接降级岗位质量判断

- 若 `scope_bloat_risk = high`
  - summary 和 risks 中要明确提示

- 若 `unclear_metric_risk = high`
  - 降低岗位可信度

## 五、Confidence

### 作用

反映这次判断有多稳。

### 置信度影响因素

- JD 信息是否完整
- 简历证据是否充分
- 是否存在大量推断字段
- 是否存在关键字段缺失

### 建议分档

- `high`
  - JD 清晰，简历证据充分，关键字段齐全

- `medium`
  - 基本可判，但部分字段依赖推断

- `low`
  - JD 模糊或简历证据严重不足

### 输出建议

在返回结构中可同时保留：

- 文本档位：`high / medium / low`
- 数值：`0-100`

## 六、Gaps 建模

### `non_compensatory_gaps`

定义：

- 无法被其他优势弥补的关键缺口

典型来源：

- gate fail 项
- 明确要求 AI 落地经验但完全没有
- 明确要求领域经验但完全不匹配

### `compensatory_gaps`

定义：

- 当前偏弱，但可通过其他强证据或补充材料弥补的缺口

典型来源：

- 技术理解一般，但交付和场景能力强
- 领域经验一般，但 AI 产品落地证据强
- 指标证据偏弱，但项目复杂度高

## 七、Recommendation Mapping

### 作用

把综合判断转成最终结论。

### 基础区间建议

- `80-100`：`冲`
- `65-79`：`可投`
- `50-64`：`谨慎`
- `<50`：`避开`

### 但不能只看总分

最终 recommendation 需要同时看：

- gate 是否通过
- 是否存在 `non_compensatory_gaps`
- 岗位风险是否过高
- confidence 是否过低

### 建议规则

#### `冲`

同时满足：

- gate 通过
- 综合分 >= 80
- 无重大不可补偿缺口
- 岗位风险不高

#### `可投`

满足：

- gate 基本通过
- 综合分 >= 65
- 有短板但可以补

#### `谨慎`

满足任一：

- 综合分 50-64
- 岗位风险偏高
- 有明显缺口但还不到完全劝退

#### `避开`

满足任一：

- gate fail 严重
- 综合分 < 50
- 岗位本身高风险且价值存疑

## 八、User Goal 调整

### 作用

让同一份匹配结果能根据用户目标做轻微偏置，但不能推翻结构化判断。

### 建议目标

- `求稳`
- `冲高薪`
- `转AI`
- `找长期主线`

### 调整方式

只允许轻量调整 recommendation 倾向，不直接重算全部评分。

例如：

- `求稳`
  - 对高岗位风险更敏感
  - 对 `scope_bloat_risk` 和 `unclear_metric_risk` 更保守

- `冲高薪`
  - 对高技术深度、高 AI 含量岗位容忍度更高

- `转AI`
  - 对可补偿缺口更宽容
  - 但对 AI gate 仍不能完全放松

- `找长期主线`
  - 更重视 `ai_maturity` 和 `delivery_mode`

## 九、推荐返回字段

### `match_result`

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
  "confidence": {
    "level": "medium",
    "score": 0
  },
  "non_compensatory_gaps": [],
  "compensatory_gaps": [],
  "match_highlights": []
}
```

### `recommendation_result`

```json
{
  "recommendation": "",
  "recommendation_reason": "",
  "job_risk_level": "",
  "candidate_readiness_level": ""
}
```

## 十、实现优先级

建议按这个顺序实现：

1. 先实现 `gate_check`
2. 再实现 7 维评分
3. 再加入岗位风险调整
4. 最后再做 `user_goal` 的轻微偏置

## 非目标

这份文档不定义：

- 具体 extractor prompt
- 具体 narrator prompt
- 前端展示方式
- 最终文案语气

这些应在独立文档中定义。
