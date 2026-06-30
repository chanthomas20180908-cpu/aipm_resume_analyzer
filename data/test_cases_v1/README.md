# 测试集 V1 目录

本目录是 AI PM 岗位判断工具的测试集，采用 MECE 双轴分类：

- **横轴：岗位质量** — 真 AI 岗 / 伪 AI 岗
- **纵轴：匹配类型** — 强匹配 / 可迁移 / 有短板 / 硬伤

当前 8 个有效 case 覆盖 6 个主格子 + 1 个跨域变体。每个 case 包含 JD、简历、case 定义和金标数据。

---

## 矩阵总览

```text
              真 AI 岗                              |        伪 AI 岗
           ───────────────────────────────────────┼───────────────────────────────────────
强匹配  │  A1: 002 Shivika (保险Agent)           │  A2: 009 Shivika + 图灵机器人 JD
           │      冲                              │      谨慎
           │      [✓]                              │      [✓]
           ───────────────────────────────────────┼───────────────────────────────────────
可迁移  │  B1: 001 Mackenzie (电商AI, UX背景)    │  B2: 010 Mackenzie + 图灵机器人 JD
           │      可投                            │      避开
           │      [✓]                              │      [✓]
           ───────────────────────────────────────┼───────────────────────────────────────
有短板  │  C1: 005 强交付弱技术 (case_002 JD)      │  C2: 004 伪AI+普通PM
           │      谨慎                            │      避开
           │      [✓]                              │      [✓]
           ───────────────────────────────────────┼───────────────────────────────────────
硬伤   │  D1: 003 传统PM无AI证据                 │  D2: 不建（价值低）
           │      避开                            │
           │      [✓]                              │
           ───────────────────────────────────────┼───────────────────────────────────────

附加: A1-跨域: 008 Jillani (金融AI, 强匹配但跨行业) → 测试 business_fit，可投
```

---

## A1: 真 AI 岗 + 强匹配 → 冲

| 字段 | 内容 |
|------|------|
| **Cell** | A1 |
| **Case** | `case_002` |
| **方向** | 真 AI 落地岗，候选人明显匹配 |
| **JD** | [`jd/case_002_jd.md`](jd/case_002_jd.md) — 保险 Agent 落地（脉脉） |
| **Resume** | [`resume/case_002_resume.md`](resume/case_002_resume.md) — Shivika 公开 PDF |
| **Golden** | [`golden/case_002_golden.json`](golden/case_002_golden.json) |
| **候选人类型** | 技术型 AI 产品，AI 应用落地能力强 |
| **核心测试点** | 系统是否对强匹配过度保守？是否漏判 match_highlights？ |
| **预期 Recommendation** | 冲 |
| **预期 Match Score** | 85 |
| **关键维度** | ai_understanding ↑, delivery_execution ↑, data_metrics ↑ |

---

## A1-跨域: 真 AI 岗 + 强匹配但跨行业 → 可投

| 字段 | 内容 |
|------|------|
| **Cell** | A1-跨域 |
| **Case** | `case_008` |
| **方向** | 行业/场景高度相关岗，候选人强匹配但跨域 |
| **JD** | [`jd/case_008_jd.md`](jd/case_008_jd.md) — 同花顺海外 AI PM（金融方向，脉脉） |
| **Resume** | [`resume/case_008_resume.md`](resume/case_008_resume.md) — Jillani 公开 PDF |
| **Golden** | [`golden/case_008_golden.json`](golden/case_008_golden.json) |
| **候选人类型** | AI 技术和落地能力强，但行业/场景不贴合（金融 vs 通用 AI） |
| **核心测试点** | 系统对 business_fit 和 technical_depth 的复合判断 |
| **预期 Recommendation** | 可投 |
| **预期 Match Score** | 78 |
| **关键维度** | ai_understanding ↑, business_fit ↓, technical_evidence ↑ |

---

## A2: 伪 AI 岗 + 强匹配 → 谨慎

| 字段 | 内容 |
|------|------|
| **Cell** | A2 |
| **Case** | `case_009` |
| **方向** | 伪 AI 岗 + 强匹配候选人 |
| **JD** | [`jd/case_004_jd.md`](jd/case_004_jd.md) — 图灵机器人虚拟机器人（脉脉，复用） |
| **Resume** | [`resume/case_002_resume.md`](resume/case_002_resume.md) — Shivika 公开 PDF（复用） |
| **Golden** | [`golden/case_009_golden.json`](golden/case_009_golden.json) |
| **候选人类型** | 强 AI 候选人，能力远超岗位要求 |
| **核心测试点** | 系统是否优先识别岗位风险？是否被候选人质量带偏？ |
| **预期 Recommendation** | 谨慎 |
| **预期 Match Score** | 78 |
| **关键维度** | pseudo_ai_risk → 上限 recommendation |

---

## B1: 真 AI 岗 + 可迁移 → 可投

| 字段 | 内容 |
|------|------|
| **Cell** | B1 |
| **Case** | `case_001` |
| **方向** | 可迁移型案例 |
| **JD** | [`jd/case_001_jd.md`](jd/case_001_jd.md) — 电商 AI PM（售前售后质检营销，BOSS） |
| **Resume** | [`resume/case_001_resume.md`](resume/case_001_resume.md) — Mackenzie Clark 公开简历 |
| **Golden** | [`golden/case_001_golden.json`](golden/case_001_golden.json) |
| **候选人类型** | 真实产品经理，偏 UX/用户研究/路线图，可迁移 |
| **核心测试点** | 系统是否识别可迁移能力？是否给出"可投"而非"避开"？ |
| **预期 Recommendation** | 可投 |
| **预期 Match Score** | 68 |
| **关键维度** | scenario_abstraction ↑, business_fit ↑, ai_understanding 弱但有潜力 |

---

## B2: 伪 AI 岗 + 可迁移 → 避开

| 字段 | 内容 |
|------|------|
| **Cell** | B2 |
| **Case** | `case_010` |
| **方向** | 伪 AI 岗 + 可迁移候选人 |
| **JD** | [`jd/case_004_jd.md`](jd/case_004_jd.md) — 图灵机器人虚拟机器人（脉脉，复用） |
| **Resume** | [`resume/case_001_resume.md`](resume/case_001_resume.md) — Mackenzie Clark 公开简历（复用） |
| **Golden** | [`golden/case_010_golden.json`](golden/case_010_golden.json) |
| **候选人类型** | 可迁移背景，但非强匹配，能力一般 |
| **核心测试点** | 系统是否识别"双向一般"？是否给出"避开"？ |
| **预期 Recommendation** | 避开 |
| **预期 Match Score** | 55 |
| **关键维度** | pseudo_ai_risk + 综合短板 → 避开 |

---

## C1: 真 AI 岗 + 有短板 → 谨慎

| 字段 | 内容 |
|------|------|
| **Cell** | C1 |
| **Case** | `case_005` |
| **方向** | 强交付、弱技术理解 |
| **JD** | [`jd/case_002_jd.md`](jd/case_002_jd.md) — 保险 Agent 落地（脉脉，复用） |
| **Resume** | [`resume/case_005_resume.md`](resume/case_005_resume.md) — 匿名改写（强交付 PM，技术理解弱） |
| **Golden** | [`golden/case_005_golden.json`](golden/case_005_golden.json) |
| **候选人类型** | 强交付 PM，技术理解证据弱 |
| **核心测试点** | 系统是否把"强执行"误判为"足够懂 AI"？是否区分可补偿与不可补偿？ |
| **预期 Recommendation** | 谨慎 |
| **预期 Match Score** | 62 |
| **关键维度** | delivery_execution ↑, ai_understanding ↓, technical_gap |

---

## C2: 伪 AI 岗 + 有短板 → 避开

| 字段 | 内容 |
|------|------|
| **Cell** | C2 |
| **Case** | `case_004` |
| **方向** | 伪 AI 岗 / 换皮岗 |
| **JD** | [`jd/case_004_jd.md`](jd/case_004_jd.md) — 图灵机器人虚拟机器人（脉脉） |
| **Resume** | [`resume/case_004_resume.md`](resume/case_004_resume.md) — 匿名改写（普通 PM，体验型产品背景） |
| **Golden** | [`golden/case_004_golden.json`](golden/case_004_golden.json) |
| **候选人类型** | 普通产品经理，体验型产品背景 |
| **核心测试点** | 系统是否同时识别岗位风险和候选人短板？ |
| **预期 Recommendation** | 避开 |
| **预期 Match Score** | 48 |
| **关键维度** | pseudo_ai_risk + 综合短板 |

---

## D1: 真 AI 岗 + 硬伤 → 避开

| 字段 | 内容 |
|------|------|
| **Cell** | D1 |
| **Case** | `case_003` |
| **方向** | 真 AI 落地岗，候选人 AI 证据明显不足 |
| **JD** | [`jd/case_003_jd.md`](jd/case_003_jd.md) — AI 统一能力平台（BOSS） |
| **Resume** | [`resume/case_003_resume.md`](resume/case_003_resume.md) — 匿名改写（传统 PM，AI 证据弱） |
| **Golden** | [`golden/case_003_golden.json`](golden/case_003_golden.json) |
| **候选人类型** | 传统 PM，AI 证据弱 |
| **核心测试点** | 系统是否识别不可补偿缺口？是否给出"避开"？ |
| **预期 Recommendation** | 避开 |
| **预期 Match Score** | 45 |
| **关键维度** | ai_delivery_gate fail, technical_gate fail |

---

## D2: 伪 AI 岗 + 硬伤 → 不建

- 结论必然是"避开"，与 C2/D1 结论相同。
- 不增加新的测试价值。
- **决策：不建设。**

---

## 文件路径总览

| Case | Cell | JD | Resume | Golden | 预期结论 |
|------|------|----|--------|--------|----------|
| 001 | B1 | [`jd/case_001_jd.md`](jd/case_001_jd.md) | [`resume/case_001_resume.md`](resume/case_001_resume.md) | [`golden/case_001_golden.json`](golden/case_001_golden.json) | 可投 |
| 002 | A1 | [`jd/case_002_jd.md`](jd/case_002_jd.md) | [`resume/case_002_resume.md`](resume/case_002_resume.md) | [`golden/case_002_golden.json`](golden/case_002_golden.json) | 冲 |
| 003 | D1 | [`jd/case_003_jd.md`](jd/case_003_jd.md) | [`resume/case_003_resume.md`](resume/case_003_resume.md) | [`golden/case_003_golden.json`](golden/case_003_golden.json) | 避开 |
| 004 | C2 | [`jd/case_004_jd.md`](jd/case_004_jd.md) | [`resume/case_004_resume.md`](resume/case_004_resume.md) | [`golden/case_004_golden.json`](golden/case_004_golden.json) | 避开 |
| 005 | C1 | [`jd/case_002_jd.md`](jd/case_002_jd.md) | [`resume/case_005_resume.md`](resume/case_005_resume.md) | [`golden/case_005_golden.json`](golden/case_005_golden.json) | 谨慎 |
| 008 | A1-跨域 | [`jd/case_008_jd.md`](jd/case_008_jd.md) | [`resume/case_008_resume.md`](resume/case_008_resume.md) | [`golden/case_008_golden.json`](golden/case_008_golden.json) | 可投 |
| 009 | A2 | [`jd/case_004_jd.md`](jd/case_004_jd.md) | [`resume/case_002_resume.md`](resume/case_002_resume.md) | [`golden/case_009_golden.json`](golden/case_009_golden.json) | 谨慎 |
| 010 | B2 | [`jd/case_004_jd.md`](jd/case_004_jd.md) | [`resume/case_001_resume.md`](resume/case_001_resume.md) | [`golden/case_010_golden.json`](golden/case_010_golden.json) | 避开 |

---

## 使用说明

### 加载一个 Case

```python
import json

case_id = "case_001"
with open(f"data/test_cases_v1/cases/{case_id}.json") as f:
    case = json.load(f)

with open(case["jd_file"]) as f:
    jd = f.read()

with open(case["resume_file"]) as f:
    resume = f.read()

with open(case["golden_label_file"]) as f:
    golden = json.load(f)
```

### 对照金标

每个 case 的 `golden_label` 包含：

- `recommendation`：预期结论（冲 / 可投 / 谨慎 / 避开）
- `dimension_scores`：7 个维度的 1-5 分评分
- `weighted_match_score`：加权匹配分
- `gate_check_result`：门槛检查结果
- `compensatory_gaps` / `non_compensatory_gaps`：可补偿与不可补偿缺口
- `annotation.notes`：标注理由

### 复用关系

- **case_002 JD** 被 case_005 复用 → A1 vs C1 对照
- **case_004 JD** 被 case_009、case_010 复用 → A2 / B2 / C2 对照
- **case_002 Resume** 被 case_009 复用 → A1 vs A2 对照
- **case_001 Resume** 被 case_010 复用 → B1 vs B2 对照

### 历史说明

- case_006、case_007 已删除，无对应 case JSON。
- 其残留简历/JD 文件仍保留在 `resume/` 和 `jd/` 中，仅作为未使用素材。

---

## 相关文档

- `docs/testset-directions-v2.md` — MECE 双轴分类体系设计
- `docs/golden-label-schema-v1.md` — 金标标注方案
- `docs/testset-sourcing-directions-v1.md` — 历史归档：最初的 8 个场景描述型方向
