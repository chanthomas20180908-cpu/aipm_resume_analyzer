# 原始 JD 抽取规范 V2

> **实现状态更新（2026-06-30）**>
> 当前 `app/capabilities/jd_analysis.py` 默认优先走 LLM 抽取（`llm_client.extract_jd_with_llm`），失败或未配置 key 时 fallback 到本文档描述的规则抽取。> 本文档现在主要描述规则 fallback 的抽取规范，并包含 LLM 抽取新增字段（`industry_domain`、`business_orientation`、`role_perspective`、`enterprise_type`）。

## 核心假设

- 真实产品输入是用户粘贴的一段原始 JD 文本。
- 在做评分和推荐之前，系统必须先把杂乱文本抽成稳定结构。
- 抽取过程必须区分“原文事实”和“系统推断”。允许谨慎推断，但不允许臆造。

## 目标

定义后端如何把一段原始 JD 文本转成内部可用的标准结构。

这份文档只回答 4 个问题：

1. 要抽什么字段
2. 哪些字段可以推断
3. 哪些字段缺失时必须留空
4. 抽取结果应该长什么样

## 抽取流程

原始 JD 处理建议拆成两步：

1. `事实抽取（fact extraction）`
2. `归一化与有界推断（normalization + bounded inference）`

### 第一步：事实抽取

从原始 JD 文本中抽取明确出现的事实。

典型内容包括：

- 岗位名称
- 公司名称
- 薪资范围
- 工作地点
- 经验要求
- 学历要求
- 岗位职责
- 任职要求
- 优先项
- AI 相关词
- 业务领域词
- 指标相关词

### 第二步：归一化与有界推断

把抽出的事实映射成后续系统统一使用的字段。

例如：

- 根据职责和业务线索推断 `job_family`
- 根据 AI 交付信号推断 `ai_maturity`
- 根据 `从0到1`、`平台化`、`持续优化`、`场景建设` 等措辞推断 `delivery_mode`
- 根据显式指标或可衡量表述推断 `success_metrics`

只有在文本证据足够时才允许推断。

## 输出结构

```json
{
  "raw_text": "",
  "fact_extraction": {
    "job_title": "",
    "company_name": "",
    "salary_text": "",
    "location": "",
    "experience_required": "",
    "education_required": "",
    "job_type_text": "",
    "responsibilities": [],
    "requirements": [],
    "preferred_items": [],
    "benefits": [],
    "keywords": {
      "ai_terms": [],
      "domain_terms": [],
      "metric_terms": [],
      "tool_terms": []
    }
  },
  "normalized_jd": {
    "job_profile": {
      "job_title": "",
      "job_family": "",
      "business_domain": "",
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
  },
  "extraction_meta": {
    "explicit_fields": [],
    "inferred_fields": [],
    "missing_fields": [],
    "confidence_notes": []
  }
}
```

## 字段规则

### 1. `job_title`

- 来源：原文中明确出现的岗位名称
- 是否必须：有则抽
- 是否允许推断：不允许
- 缺失策略：没有就返回空字符串

### 2. `company_name`

- 来源：原文中明确出现的公司名称
- 是否允许推断：不允许
- 缺失策略：没有就返回空字符串

### 3. `salary_text` / `salary_range`

- 来源：原文中明确出现的薪资表述
- 是否允许推断：不允许猜数字
- 可以做的归一化：
  - `20k-40k`
  - `2-4万`
  - `20,000-40,000 CNY/月`
- 缺失策略：没有就返回空字符串

### 4. `location`

- 来源：原文中明确出现的地点
- 是否允许推断：不允许

### 5. `experience_required`

- 来源：原文中的年限或资历表达
- 示例：
  - `3年以上`
  - `3-5年`
  - `5年及以上`
- 是否允许推断：不允许

### 6. `education_required`

- 来源：原文中的学历表达
- 是否允许推断：不允许

### 7. `responsibilities`

- 来源：原文中的岗位职责描述
- 抽取规则：
  - 每条职责尽量保持为一个独立项
  - 尽量保留原始措辞
- 拆分规则：
  - 如果一句话里包含多个明确不同的职责，可以拆开
  - 如果只是同一职责的补充说明，不拆

### 8. `requirements`

- 来源：原文中的任职要求
- 抽取规则：
  - 先不区分硬要求和软要求
  - 统一进入原始要求列表
  - 后续在归一化阶段再区分

### 9. `preferred_items`

- 来源：
  - `优先`
  - `加分项`
  - `bonus`
  - `plus`
- 允许推断的情况：
  - JD 清楚表达为可选优势项
- 不允许：
  - 仅凭语气猜测为优先项

### 10. `keywords`

#### `ai_terms`

例如：

- AI
- Agent
- Prompt
- LLM
- 大模型
- 多模态
- 知识库
- RAG
- 工作流
- Skill

#### `domain_terms`

例如：

- 智能营销
- 研发效能
- 企业协作
- 教育
- 机器人
- 知识管理

#### `metric_terms`

例如：

- 命中率
- 完成率
- 渗透率
- 转化率
- 用户体验
- 成本
- ROI

#### `tool_terms`

例如：

- SQL
- Python
- API
- SDK
- GPT-4V
- Gemini

这些词主要服务抽取，不直接等于最终评分结果。

## 归一化规则

### A. `job_family`

#### 作用

把岗位归到稳定的产品类别里。

#### 允许值

- `internal_ai_platform`
- `enterprise_collaboration`
- `ai_workflow_tool`
- `growth_ai_product`
- `marketing_ai_product`
- `robotics_ai_product`
- `multimodal_ai_product`
- `general_ai_pm`

#### 推断依据

- 岗位职责
- 业务领域词
- 产品场景上下文

如果证据太弱，回退为 `general_ai_pm`。

### B. `business_domain`

#### 作用

识别岗位落在哪个业务语境里。

#### 允许值

- `marketing`
- `collaboration`
- `efficiency`
- `knowledge_management`
- `education`
- `robotics`
- `consumer_content`
- `general`

证据不足时使用 `general`。

### B1. `industry_domain`

#### 作用

识别岗位所在的垂直行业。

#### 允许值

- `insurance`
- `finance`
- `healthcare`
- `education`
- `retail`
- `e_commerce`
- `manufacturing`
- `logistics`
- `automotive`
- `real_estate`
- `enterprise_service`
- `general`

证据不足时使用 `general`。

### B2. `business_orientation`

#### 作用

判断岗位偏业务还是偏技术。

#### 允许值

- `business-heavy`
- `tech-heavy`
- `hybrid`

### B3. `role_perspective`

#### 作用

判断 JD 招的是 PM 视角还是工程师视角。

#### 允许值

- `pm`
- `engineer`
- `hybrid`

### B4. `enterprise_type`

#### 作用

判断企业类型是传统行业还是 AI 原生。

#### 允许值

- `traditional_enterprise`
- `ai_native`
- `hybrid`

### C. `ai_maturity`

#### 作用

判断这个岗位的 AI 成熟度到底有多高。

#### 允许值

- `concept_heavy`
- `application_driven`
- `deep_delivery`

#### 推断原则

- `concept_heavy`：AI 词很多，但交付细节少
- `application_driven`：有明确场景和产品能力设计
- `deep_delivery`：提到系统设计、评测、工作流、指标、迭代、能力边界、生产优化等

### D. `delivery_mode`

#### 作用

识别这个岗位的交付模式。

#### 允许值

- `0_to_1`
- `1_to_10`
- `platform`
- `scenario_driven`
- `mixed`

#### 推断原则

- `0_to_1`：从零搭建、新方向探索、首次上线
- `1_to_10`：持续优化、迭代放大
- `platform`：平台能力、基础设施、生态层
- `scenario_driven`：多个业务场景设计、交互路径设计为主

### E. `must_have`

#### 作用

表示 JD 中明确或近似明确的必要条件。

#### 仅在以下情况纳入

- 明确要求的工作年限
- 明确要求的行业背景
- 明确要求的 AI 产品经验
- 明确要求的技术理解

不要把软素质塞进这个字段。

### F. `preferred`

#### 作用

表示方向性加分项或可选优势项。

#### 典型信号

- `优先`
- `加分项`
- `有...经验优先`

### G. `core_competencies`

#### 作用

把 JD 里的表述映射成统一能力维度。

#### 建议能力词表

- `ai_understanding`
- `scenario_abstraction`
- `workflow_design`
- `product_design`
- `technical_collaboration`
- `delivery_execution`
- `data_metrics`
- `stakeholder_push`
- `business_judgment`
- `user_insight`

这里使用的是归一化标签，不直接保留 JD 原句。

### H. `technical_depth`

#### 作用

表达岗位对技术理解的强度要求。

#### 允许值

- `low`
- `medium`
- `high`

#### 推断原则

- `low`：提到 AI，但岗位仍以协调或包装为主
- `medium`：要求把 AI 能力产品化，并理解能力边界
- `high`：要求 Prompt 架构、多 Agent 设计、评测体系、模型/工具理解、深度技术协作

### I. `success_metrics`

#### 作用

抽出岗位可能会被如何衡量成功。

#### 可以来自

- 明确写出的指标
- 高置信度的运营表述

例如：

- 任务完成率
- 渗透率
- 命中率
- 响应质量
- 用户体验
- 交付效率
- 成本优化

没有证据时不要编 KPI。

### J. `non_negotiables`

#### 作用

为后续匹配层定义不可补偿项。

#### 只在以下情况填充

- 明确的经验门槛
- 明确要求 AI 落地经验
- 明确要求业务领域匹配
- 明确要求技术熟悉度

这个字段比 `must_have` 更严格。拿不准时宁可留空。

### K. `job_risk_flags`

#### 作用

描述岗位本身的风险，不是候选人的风险。

#### `pseudo_ai_risk`

高风险条件：

- 有大量 AI 词
- 但职责主要是泛协调或泛产品工作
- 几乎没有 AI 产品设计或交付细节

#### `coordination_heavy_risk`

高风险条件：

- 职责大量强调协调、推进、对齐
- 但很少提产品判断、AI 能力设计、指标或交付深度

#### `scope_bloat_risk`

高风险条件：

- JD 同时要求策略、设计、技术、数据、交付、业务全包
- 但没有清晰重点

#### `unclear_metric_risk`

高风险条件：

- JD 要求优化、增长、提效
- 但没有表达清楚评价逻辑

风险等级统一用：`low / medium / high`

## 推断边界

### 允许推断

- 根据职责模式归类岗位类型
- 根据 AI 词密度和交付信号判断 AI 成熟度
- 根据明确运营表述推断 success metrics
- 把 JD 原句映射成统一能力标签

### 不允许推断

- 公司阶段原文没有，就不能编
- 薪资没有，就不能猜
- 领域不明确，就不能硬判
- 偏好项不能升级成硬门槛
- 看到 AI 关键词，不等于深度 AI 岗

## 空值策略

当证据缺失时：

- 字符串字段：`""`
- 数组字段：`[]`
- 对象字段：保留结构，用空值填充

除非本文明确允许回退，否则不能用猜测值填充。

允许的安全回退包括：

- `job_family = general_ai_pm`
- `business_domain = general`

## `extraction_meta`

`extraction_meta` 用于调试和建立信任。

### `explicit_fields`

直接从原文抽出的字段。

### `inferred_fields`

通过归一化或推断生成的字段。

### `missing_fields`

schema 预期存在，但当前 JD 无法支持的字段。

### `confidence_notes`

短说明，例如：

- `job_family 基于内部工作流职责推断`
- `success_metrics 基于完成率相关措辞推断`
- `company_stage 原文缺失`

## 推荐实现顺序

建议按这个顺序落地：

1. 先写事实抽取 prompt
2. 再写确定性的归一化层
3. 用真实 JD 样本校验
4. 最后再接入评分逻辑

## 非目标

这份文档不定义：

- 候选人抽取
- 评分逻辑
- recommendation 阈值
- 最终结果文案风格

这些内容应在后续文档中单独定义。
