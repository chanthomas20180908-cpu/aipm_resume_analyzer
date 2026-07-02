# 金标标注方案 V1

> 基于 [[testset-directions-v2]] 的 MECE 双轴分类，为 8 个 case 提供人工标准判断。
> 标注原则：先读 JD + 简历，独立打分，再对照系统规则验证一致性。

---

## 标注范围

| 字段 | 说明 | 必填 |
|------|------|------|
| `golden_recommendation` | 冲/可投/谨慎/避开 | ✅ |
| `golden_dimension_scores` | 7 维度 0-5 分 | ✅ |
| `golden_gate_check` | gate 是否通过 + 失败原因 | ✅ |
| `golden_gaps` | 可补偿缺口 + 不可补偿缺口 | ✅ |
| `golden_confidence` | 高/中/低 + 数值 | ✅ |
| `golden_job_risk_level` | 高/中/低 | ✅ |
| `annotator` | 标注人 | ✅ |
| `annotation_date` | 标注日期 | ✅ |
| `annotation_notes` | 标注过程的关键判断依据 | ✅ |

---

## 标注流程（4 步）

### Step 1：独立阅读

- 先读 JD，记录关键要求（must_have、技术深度、领域要求、指标要求）
- 再读简历，记录证据（AI 经验、交付经验、指标结果、技术理解）
- **不先看系统输出，避免被带偏**

### Step 2：逐项打分

按 7 维度逐项评分，每维 0-5：

| 分数 | 含义 |
|------|------|
| 0 | 完全无证据 |
| 1 | 只有弱相关词，无实质证据 |
| 2 | 有零散证据，不足以支撑岗位要求 |
| 3 | 基本匹配，可投但不占优 |
| 4 | 较强匹配，有明确证据 |
| 5 | 强匹配，证据质量高 |

### Step 3：综合判断

- 计算加权总分（按 rule-scoring-v2 权重）
- 判断 gate 是否通过
- 识别 gaps（可补偿 / 不可补偿）
- 判断岗位风险
- 映射 recommendation

### Step 4：一致性检查

- 总分与 recommendation 是否一致？
- gate fail 时 recommendation 是否被正确限制？
- 岗位风险高时 recommendation 是否被上限？

---

## 8 Case 金标预标注（初稿）

> 以下为人基于规则文档的初步判断，**需人工复核**。

---

### A1: case_002 — 真 AI 岗 + 强匹配

| 字段 | 金标 |
|------|------|
| **recommendation** | 冲 |
| **ai_understanding** | 5 |
| **scenario_abstraction** | 4 |
| **workflow_design** | 4 |
| **delivery_execution** | 5 |
| **data_metrics** | 4 |
| **stakeholder_push** | 4 |
| **business_fit** | 3 |
| **weighted_match_score** | ~85 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["business_fit 一般（保险 vs 通用 AI）"] |
| **confidence** | high (~85) |
| **job_risk_level** | low |

**判断依据**：
- Shivika 有完整 Agent 落地、Prompt 工程、评测体系、生成式 AI 经验
- 保险场景有明确业务抽象和指标（91% 准确率、95% ML 准确率）
- 唯一弱项是 business_fit（保险领域 vs 通用 AI），但技术深度可补偿

---

### A1-跨域: case_008 — 真 AI 岗 + 强匹配但跨行业

| 字段 | 金标 |
|------|------|
| **recommendation** | 可投 |
| **ai_understanding** | 5 |
| **scenario_abstraction** | 4 |
| **workflow_design** | 4 |
| **delivery_execution** | 4 |
| **data_metrics** | 4 |
| **stakeholder_push** | 3 |
| **business_fit** | 2 |
| **weighted_match_score** | ~78 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["business_fit 弱（无金融背景）", "stakeholder_push 证据不足（海外 vs 国内）"] |
| **confidence** | medium (~70) |
| **job_risk_level** | low |

**判断依据**：
- Jillani AI 技术极强（RAG、多智能体、LLMOps），但金融场景经验缺失
- JD 要求"金融业务知识"，简历无直接证据
- 技术深度可部分补偿行业 gap，但不足以"冲"

---

### A2: case_009 — 伪 AI 岗 + 强匹配

| 字段 | 金标 |
|------|------|
| **recommendation** | 谨慎 |
| **ai_understanding** | 5 |
| **scenario_abstraction** | 4 |
| **workflow_design** | 3 |
| **delivery_execution** | 4 |
| **data_metrics** | 4 |
| **stakeholder_push** | 4 |
| **business_fit** | 3 |
| **weighted_match_score** | ~78 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["岗位 AI 深度不足，候选人能力溢出"] |
| **confidence** | medium (~65) |
| **job_risk_level** | high |

**判断依据**：
- 候选人能力远超岗位要求（虚拟机器人 JD 实际偏传统体验产品）
- 岗位风险高（pseudo_ai_risk = high），recommendation 上限为谨慎
- 系统应提示："岗位 AI 深度不足，候选人能力溢出，建议谨慎考虑"

---

### B1: case_001 — 真 AI 岗 + 可迁移

| 字段 | 金标 |
|------|------|
| **recommendation** | 可投 |
| **ai_understanding** | 2 |
| **scenario_abstraction** | 4 |
| **workflow_design** | 3 |
| **delivery_execution** | 3 |
| **data_metrics** | 2 |
| **stakeholder_push** | 3 |
| **business_fit** | 3 |
| **weighted_match_score** | ~68 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["ai_understanding 弱（无 AI 直接经验）", "data_metrics 弱（无量化指标）"] |
| **confidence** | medium (~65) |
| **job_risk_level** | low |

**判断依据**：
- Mackenzie 无 AI 经验，但有 UX/用户研究/产品路线图能力
- 电商 AI PM 偏应用型，可迁移能力可覆盖部分要求
- AI 理解是明显短板，但非不可补偿（可学习）

---

### B2: case_010 — 伪 AI 岗 + 可迁移

| 字段 | 金标 |
|------|------|
| **recommendation** | 避开 |
| **ai_understanding** | 2 |
| **scenario_abstraction** | 3 |
| **workflow_design** | 2 |
| **delivery_execution** | 3 |
| **data_metrics** | 2 |
| **stakeholder_push** | 3 |
| **business_fit** | 2 |
| **weighted_match_score** | ~55 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["综合短板多，岗位本身无价值"] |
| **confidence** | medium (~60) |
| **job_risk_level** | high |

**判断依据**：
- 双向一般：岗位伪 AI，候选人可迁移但非强匹配
- 岗位风险高 + 候选人无亮点 = 不值得投入时间
- 系统应给出"避开"，而非因"岗位要求低"而误判为"可投"

---

### C1: case_005 — 真 AI 岗 + 有短板（技术理解不足）

| 字段 | 金标 |
|------|------|
| **recommendation** | 谨慎 |
| **ai_understanding** | 2 |
| **scenario_abstraction** | 3 |
| **workflow_design** | 3 |
| **delivery_execution** | 4 |
| **data_metrics** | 2 |
| **stakeholder_push** | 4 |
| **business_fit** | 3 |
| **weighted_match_score** | ~62 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["ai_understanding 弱（无模型/Prompt/评测证据）", "data_metrics 弱（无量化结果）"] |
| **confidence** | medium (~60) |
| **job_risk_level** | low |

**判断依据**：
- 5 年 PM 经验，强交付/推进，但无 AI 技术深度证据
- JD 要求 Agent/评测/模型理解，简历只有流程管理/需求对接
- 交付能力可补偿部分 gap，但技术短板明显，不足以"可投"

---

### C2: case_004 — 伪 AI 岗 + 有短板

| 字段 | 金标 |
|------|------|
| **recommendation** | 避开 |
| **ai_understanding** | 1 |
| **scenario_abstraction** | 2 |
| **workflow_design** | 2 |
| **delivery_execution** | 3 |
| **data_metrics** | 1 |
| **stakeholder_push** | 3 |
| **business_fit** | 2 |
| **weighted_match_score** | ~48 |
| **gate_check** | passed |
| **non_compensatory_gaps** | [] |
| **compensatory_gaps** | ["综合短板多，岗位本身无价值"] |
| **confidence** | medium (~55) |
| **job_risk_level** | high |

**判断依据**：
- 岗位伪 AI（实际偏体验设计/验收测试），候选人普通 PM
- 双向不行：岗位无成长价值，候选人无亮点
- 系统应同时识别岗位风险和候选人短板

---

### D1: case_003 — 真 AI 岗 + 硬伤

| 字段 | 金标 |
|------|------|
| **recommendation** | 避开 |
| **ai_understanding** | 1 |
| **scenario_abstraction** | 2 |
| **workflow_design** | 2 |
| **delivery_execution** | 3 |
| **data_metrics** | 1 |
| **stakeholder_push** | 3 |
| **business_fit** | 2 |
| **weighted_match_score** | ~45 |
| **gate_check** | failed |
| **failed_reasons** | ["ai_delivery_gate: JD 要求 AI 落地经验，简历无 AI 项目证据", "technical_gate: JD 要求模型/Agent/评测理解，简历无技术证据"] |
| **non_compensatory_gaps** | ["无 AI 产品落地经验", "无模型/Agent/评测技术理解"] |
| **compensatory_gaps** | ["交付能力尚可，但不足以补偿 AI 硬门槛"] |
| **confidence** | medium (~55) |
| **job_risk_level** | low |

**判断依据**：
- 传统 PM 背景，无 AI 项目、无模型理解、无 Prompt/评测经验
- JD 明确要求 AI 统一能力平台/Agent 编排/工作流自动化
- 硬门槛缺失，不可补偿，应直接避开

---

## 金标数据结构（建议写入 case JSON）

```json
{
  "id": "case_xxx",
  "direction": "...",
  "cell": "A1",
  "golden_label": {
    "recommendation": "冲",
    "dimension_scores": {
      "ai_understanding": 5,
      "scenario_abstraction": 4,
      "workflow_design": 4,
      "delivery_execution": 5,
      "data_metrics": 4,
      "stakeholder_push": 4,
      "business_fit": 3
    },
    "weighted_match_score": 85,
    "gate_check_result": {
      "passed": true,
      "failed_reasons": []
    },
    "non_compensatory_gaps": [],
    "compensatory_gaps": ["business_fit 一般"],
    "confidence": {
      "level": "high",
      "score": 85
    },
    "job_risk_level": "low"
  },
  "annotation": {
    "annotator": "human",
    "date": "2026-06-30",
    "notes": "核心判断依据..."
  }
}
```

---

## 标注质量检查清单

- [ ] 每个 case 的 recommendation 与总分区间一致
- [ ] gate fail 时 recommendation 不为"冲"或"可投"
- [ ] pseudo_ai_risk = high 时 recommendation 上限为"谨慎"
- [ ] 同一 JD 不同简历（002 vs 005），结论单调变化
- [ ] 同一简历不同 JD（001 vs 010），结论单调变化
- [ ] 所有"避开"都有明确原因（gate fail 或总分<50 或岗位高风险）

---

## 下一步

1. **人工复核**：逐 case 确认上述预标注是否合理
2. **写入 case JSON**：将 golden_label 和 annotation 字段追加到每个 case 文件
3. **交叉验证**：两人独立标注，对比差异，讨论达成一致
4. **冻结金标**：标注完成后锁定，作为系统评测基准
