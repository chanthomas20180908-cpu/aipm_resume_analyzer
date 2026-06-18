# Prompt 重构设计 V2

## 核心假设

- V2 prompt 的目标不是“让模型更聪明”，而是让模型在明确边界内稳定工作。
- 规则层负责判断，LLM 负责抽取和解释。
- prompt 必须和 `raw-jd-extraction-v2`、`backend-schema-v2`、`rule-scoring-v2` 对齐，不能自成一套逻辑。

## 目标

把当前较单一的提示词重构为 3 类 prompt：

1. `JD extractor`
2. `resume extractor`
3. `narrator`

这 3 类 prompt 分别服务：

- 原始 JD 抽取
- 简历证据抽取
- 用户结果解释

## 总体职责划分

### 规则层负责

- 岗位分析最终结构
- 匹配评分
- 风险判断
- recommendation

### LLM 负责

- 从原始文本抽事实
- 把文本映射成结构化证据
- 基于规则结果生成用户可读解释

### LLM 不负责

- 决定 recommendation
- 自行修改分数
- 自行创造不存在的经历或岗位事实
- 用主观常识替代原文证据

## 一、JD Extractor Prompt

### 作用

从用户粘贴的一段原始 JD 文本里抽出：

- 明确事实
- 可用于归一化的基础线索

它的职责是“抽事实”，不是“下判断”。

### 输入

- `raw_jd_text`

### 输出

对应 `raw-jd-extraction-v2` 中的 `fact_extraction`：

```json
{
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
}
```

### 允许做的事

- 识别 JD 中显式出现的信息
- 把长句拆成职责项或要求项
- 识别优先项、加分项
- 提取 AI / 领域 / 指标 / 工具关键词

### 不允许做的事

- 推断 `job_family`
- 推断 `ai_maturity`
- 推断 `technical_depth`
- 推断岗位风险
- 编造公司阶段、薪资、领域

### 设计原则

- 只抽“看得见”的东西
- 允许缺失
- 宁可少抽，不乱猜

### 输出约束

- 必须输出 JSON
- 字段必须完整
- 缺失字段返回空字符串、空数组或空对象
- 不输出解释文字

## 二、Resume Extractor Prompt

### 作用

从简历文本中抽出候选人证据，用于后续匹配。

它的职责是“抽证据”，不是“做推荐”。

### 输入

- `resume_text`

### 输出

对应 `candidate_analysis` 的抽取基础：

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

### 允许做的事

- 提取工作年限和背景
- 提取项目经历中的 AI 证据
- 提取交付、指标、技术协作、跨团队推进证据
- 识别哪些证据缺失或不够明确

### 不允许做的事

- 直接说候选人“适合/不适合”
- 推断不存在的项目经历
- 把模糊描述升级为强证据
- 根据行业常识补全简历没有写的内容

### 设计原则

- 抽“证据”，不是抽“自我评价”
- 能映射到项目、结果、职责的内容优先
- 模糊措辞只能作为弱证据

### 输出约束

- 必须输出 JSON
- 不输出 recommendation
- 不输出结论型语句

## 三、Narrator Prompt

### 作用

把规则层已经算出的结果，转成用户能读懂的中文结果。

它的职责是“解释”，不是“裁决”。

### 输入

- `job_analysis`
- `candidate_analysis`
- `match_result`
- `recommendation_result` 中规则层已决定的字段

### 输出

只生成以下字段：

```json
{
  "summary": "",
  "strengths": [],
  "risks": [],
  "next_actions": []
}
```

### 允许做的事

- 用更自然的语言总结规则结果
- 优先引用 JD 和简历中的真实线索
- 把结构化缺口翻译成可执行建议

### 不允许做的事

- 修改 `recommendation`
- 修改 `weighted_match_score`
- 修改 `job_risk_level`
- 添加规则层没有支持的判断
- 写成空泛鸡汤或求职模板话术

### 设计原则

- 解释必须跟着规则走
- 风险描述必须对应具体缺口
- 建议必须是可执行动作

### 输出约束

- `summary` 一句话
- `strengths` 2-4 条
- `risks` 2-4 条
- `next_actions` 2-4 条
- 必须输出 JSON

## 四、Prompt 间的关系

### 调用顺序

建议固定为：

1. `JD extractor`
2. `resume extractor`
3. 规则层归一化与评分
4. `narrator`

### 数据流

```text
raw_jd_text
  -> JD extractor
  -> fact_extraction
  -> normalization
  -> job_analysis

resume_text
  -> resume extractor
  -> candidate_analysis

job_analysis + candidate_analysis + user_goal
  -> rule scoring
  -> match_result + recommendation_result

rule outputs
  -> narrator
  -> summary / strengths / risks / next_actions
```

### 设计意义

这样拆开之后，系统可以明确区分：

- 抽取错了
- 归一化错了
- 评分错了
- 解释写偏了

否则所有错误都会混在一个 prompt 里，无法调试。

## 五、提示词约束原则

所有 prompt 都建议遵守以下原则：

### 1. JSON First

- 输出必须是结构化 JSON
- 禁止 markdown
- 禁止额外解释

### 2. Evidence First

- 优先基于原文证据
- 不允许用常识填补事实缺口

### 3. Bounded Inference

- 允许有限推断
- 但必须在定义好的字段边界内进行

### 4. Empty Allowed

- 信息缺失时允许返回空值
- 不要为了“完整”硬填内容

### 5. Role Separation

- extractor 不下结论
- narrator 不改规则结果

## 六、三类 Prompt 的失败模式

### `JD extractor` 常见失败

- 把偏好项抽成硬要求
- 把职责和要求混在一起
- 遇到长文本时漏掉关键职责
- 过度推断公司或岗位背景

### `resume extractor` 常见失败

- 把自我评价当成强证据
- 把模糊经历包装成 AI 落地经验
- 忽略结果和指标
- 抽不出领域背景

### `narrator` 常见失败

- 写成很泛的建议
- 不引用真实线索
- 夸大风险或夸大优势
- 偷改 recommendation 语气

## 七、推荐的 Prompt 文件组织

建议在代码中按职责拆成独立模板：

- `build_jd_extractor_system_prompt()`
- `build_jd_extractor_user_prompt(raw_jd_text)`
- `build_resume_extractor_system_prompt()`
- `build_resume_extractor_user_prompt(resume_text)`
- `build_narrator_system_prompt()`
- `build_narrator_user_prompt(payload)`

如果暂时不拆多个文件，至少在 `app/prompts.py` 中按功能分组。

## 八、实现优先级

建议按这个顺序推进：

1. 先新增 `JD extractor`
2. 再新增 `resume extractor`
3. 最后重写 `narrator`

原因：

- 抽取层先稳定，规则才能稳定
- narrator 是最后一层，依赖前面结果结构

## 非目标

这份文档不定义：

- 具体 prompt 文案最终版本
- 模型参数
- 代码实现细节
- 前端展示策略

这些内容应在实现阶段单独收敛。
