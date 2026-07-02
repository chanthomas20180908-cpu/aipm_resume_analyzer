# 测试集 Case 映射表 V2（已归档）

> ⚠️ **此文档已归档**。当前测试集目录索引已迁移至 `data/test_cases_v1/README.md`。
> 本文件保留作为历史参考，记录 V2 重构过程中的矩阵设计与变更记录。

---

# 测试集 Case 映射表 V2（按 MECE 双轴分类）

> 分类体系：横轴岗位质量（真 AI / 伪 AI），纵轴匹配类型（强匹配 / 可迁移 / 有短板 / 硬伤）
> 文档：[[testset-directions-v2]]

---

## 矩阵总览

```
              真 AI 岗                              |        伪 AI 岗
           ───────────────────────────────────────┼───────────────────────────────────────
强匹配  │  A1: 002 Shivika (保险Agent)           │  A2: 009 新建
           │      冲/可投                         │      伪AI岗+强匹配简历 → 应谨慎
           │      [已有 ✓]                         │      [空缺 — 需新建]
           ───────────────────────────────────────┼───────────────────────────────────────
可迁移  │  B1: 001 Mackenzie (电商AI, UX背景)    │  B2: 010 新建
           │      可投                            │      伪AI岗+可迁移简历 → 应避开
           │      [已有 ✓]                         │      [空缺 — 需新建]
           ───────────────────────────────────────┼───────────────────────────────────────
有短板  │  C1: 005 强交付弱技术 (case_002 JD)      │  C2: 004 伪AI+普通PM
           │      谨慎                            │      避开
           │      [✓ 已调整]                       │      [✓]
           ───────────────────────────────────────┼───────────────────────────────────────
硬伤   │  D1: 003 传统PM无AI证据                 │  D2: 不建（价值低）
           │      避开                            │
           │      [已有 ✓]                         │
           ───────────────────────────────────────┼───────────────────────────────────────

附加: A1-跨域: 008 Jillani (金融AI, 强匹配但跨行业) → 测试 business_fit
```

---

## A1: 真 AI 岗 + 强匹配 → 冲/可投

| 字段 | 内容 |
|------|------|
| **方向** | 真 AI 落地岗，候选人明显匹配 |
| **JD** | case_002_jd.md — 保险 Agent 落地（脉脉） |
| **Resume** | case_002_resume.md — Shivika 公开 PDF |
| **候选人类型** | 技术型 AI 产品，AI 应用落地能力强 |
| **核心测试点** | 系统是否对强匹配过度保守？是否漏判 match_highlights？ |
| **预期 Recommendation** | 冲 或 可投 |
| **关键维度** | ai_understanding ↑, delivery_execution ↑, data_metrics ↑ |
| **状态** | ✅ 已有，保留 |

---

## A1-跨域: 真 AI 岗 + 强匹配但跨行业 → 可投（测试 business_fit）

| 字段 | 内容 |
|------|------|
| **方向** | 行业/场景高度相关岗，候选人强匹配但跨域 |
| **JD** | case_008_jd.md — 同花顺海外 AI PM（金融方向，脉脉） |
| **Resume** | case_008_resume.md — Jillani 公开 PDF |
| **候选人类型** | AI 技术和落地能力强，但行业/场景不贴合（金融 vs 通用 AI） |
| **核心测试点** | 系统对 business_fit 和 technical_depth 的复合判断 |
| **预期 Recommendation** | 可投（强技术可部分补偿行业 gap） |
| **关键维度** | ai_understanding ↑, business_fit ↓, technical_evidence ↑ |
| **状态** | ✅ 已有，保留 |

---

## A2: 伪 AI 岗 + 强匹配 → 谨慎（岗位风险优先）

| 字段 | 内容 |
|------|------|
| **方向** | 伪 AI 岗 + 强匹配候选人 |
| **JD** | case_004_jd.md — 图灵机器人虚拟机器人（脉脉） |
| **Resume** | case_002_resume.md — Shivika 公开 PDF（复用） |
| **候选人类型** | 强 AI 候选人，能力远超岗位要求 |
| **核心测试点** | 系统是否优先识别岗位风险？是否被候选人质量带偏？ |
| **预期 Recommendation** | 谨慎（岗不行，人不错） |
| **关键维度** | pseudo_ai_risk → 上限 recommendation |
| **状态** | ✅ 已新建 case_009 |

---

## B1: 真 AI 岗 + 可迁移 → 可投

| 字段 | 内容 |
|------|------|
| **方向** | 可迁移型案例 |
| **JD** | case_001_jd.md — 电商 AI PM（售前售后质检营销，BOSS） |
| **Resume** | case_001_resume.md — Mackenzie Clark 公开简历 |
| **候选人类型** | 真实产品经理，偏 UX/用户研究/路线图，可迁移 |
| **核心测试点** | 系统是否识别可迁移能力？是否给出"可投"而非"避开"？ |
| **预期 Recommendation** | 可投 |
| **关键维度** | scenario_abstraction ↑, business_fit ↑, ai_understanding 弱但有潜力 |
| **状态** | ✅ 已有，保留 |

---

## B2: 伪 AI 岗 + 可迁移 → 避开

| 字段 | 内容 |
|------|------|
| **方向** | 伪 AI 岗 + 可迁移候选人 |
| **JD** | case_004_jd.md — 图灵机器人虚拟机器人（脉脉，复用） |
| **Resume** | case_001_resume.md — Mackenzie Clark 公开简历（复用） |
| **候选人类型** | 可迁移背景，但非强匹配，能力一般 |
| **核心测试点** | 系统是否识别"双向一般"？是否给出"避开"？ |
| **预期 Recommendation** | 避开 |
| **关键维度** | pseudo_ai_risk + 综合短板 → 避开 |
| **状态** | ✅ 已新建 case_010 |

---

## C1: 真 AI 岗 + 有短板 → 谨慎

| 字段 | 内容 |
|------|------|
| **方向** | 强交付、弱技术理解 |
| **JD** | case_002_jd.md — 保险 Agent 落地（脉脉，复用） |
| **Resume** | case_005_resume.md — 匿名改写（强交付 PM，技术理解弱） |
| **候选人类型** | 强交付 PM，技术理解证据弱 |
| **核心测试点** | 系统是否把"强执行"误判为"足够懂 AI"？是否区分可补偿与不可补偿？ |
| **预期 Recommendation** | 谨慎 |
| **关键维度** | delivery_execution ↑, ai_understanding ↓, technical_gap |
| **状态** | ✅ 已调整：JD 复用 case_002，与 case_003 不再重复 |

---

## C2: 伪 AI 岗 + 有短板 → 避开

| 字段 | 内容 |
|------|------|
| **方向** | 伪 AI 岗 / 换皮岗 |
| **JD** | case_004_jd.md — 图灵机器人虚拟机器人（脉脉） |
| **Resume** | case_004_resume.md — 匿名改写（普通 PM，体验型产品背景） |
| **候选人类型** | 普通产品经理，体验型产品背景 |
| **核心测试点** | 系统是否同时识别岗位风险和候选人短板？ |
| **预期 Recommendation** | 避开 |
| **关键维度** | pseudo_ai_risk + 综合短板 |
| **状态** | ✅ 已有，保留 |

---

## D1: 真 AI 岗 + 硬伤 → 避开

| 字段 | 内容 |
|------|------|
| **方向** | 真 AI 落地岗，候选人 AI 证据明显不足 |
| **JD** | case_003_jd.md — AI 统一能力平台（BOSS） |
| **Resume** | case_003_resume.md — 匿名改写（传统 PM，AI 证据弱） |
| **候选人类型** | 传统 PM，AI 证据弱 |
| **核心测试点** | 系统是否识别不可补偿缺口？是否给出"避开"？ |
| **预期 Recommendation** | 避开 |
| **关键维度** | ai_delivery_gate fail, technical_gate fail |
| **状态** | ✅ 已有，保留 |

---

## D2: 伪 AI 岗 + 硬伤 → 避开（价值低，不建）

- 结论必然是"避开"，与 C2/D1 结论相同
- 不增加新的测试价值
- **决策：不建设**

---

## 素材缺口总结

| 缺口 | 说明 | 优先级 |
|------|------|--------|
| A2 (case_009) | 伪 AI 岗 + 强匹配简历 | P1 — 复用现有素材即可新建 |
| B2 (case_010) | 伪 AI 岗 + 可迁移简历 | P1 — 复用现有素材即可新建 |
| C1-技术 JD | case_005 需换 JD，与 003 不重复 | P1 — 需新选 |
| C1-证据 Resume | case_006 当前匿名改写，可寻找更真实来源 | P2 — 可选 |
| C1-指标 Resume | case_007 当前匿名改写，可寻找更真实来源 | P2 — 可选 |
| 中文真实简历 | 全部真实简历为英文，缺中文真实来源 | P2 — 长期补充 |

---

## 执行建议

### 立即执行（P1）

1. 新建 case_009：A2（伪 AI 岗 + 强匹配）
   - JD: case_004_jd.md（复用）
   - Resume: case_002_resume.md（复用 Shivika）
   - 预期：谨慎

2. 新建 case_010：B2（伪 AI 岗 + 可迁移）
   - JD: case_004_jd.md（复用）
   - Resume: case_001_resume.md（复用 Mackenzie）
   - 预期：避开

3. 为 case_005 选新 JD
   - 要求：真 AI 岗、明确要求技术深度、与 003/006 不重复
   - 方向：偏 Agent 评测 / 模型产品 / 技术平台

### 可选优化（P2）

4. 评估 R08 是否适合 case_005（C1-技术）
5. 评估是否保留 case_006/007 当前匿名简历，或寻找更真实来源
6. 补充 1-2 份中文真实简历来源

---

## 文件清单

### 已有文件（保留）

- `data/test_cases_v1/jd/case_001_jd.md` → B1
- `data/test_cases_v1/jd/case_002_jd.md` → A1
- `data/test_cases_v1/jd/case_003_jd.md` → D1
- `data/test_cases_v1/jd/case_004_jd.md` → C2 / A2 / B2（复用）
- `data/test_cases_v1/jd/case_007_jd.md` → C1-指标
- `data/test_cases_v1/jd/case_008_jd.md` → A1-跨域
- `data/test_cases_v1/resume/case_001_resume.md` → B1 / B2（复用）
- `data/test_cases_v1/resume/case_002_resume.md` → A1 / A2（复用）
- `data/test_cases_v1/resume/case_004_resume.md` → C2
- `data/test_cases_v1/resume/case_008_resume.md` → A1-跨域

### 需调整文件

- `data/test_cases_v1/jd/case_005_jd.md` → 需替换（与 003 重复）
- `data/test_cases_v1/jd/case_006_jd.md` → 可保留，但需确认不与新 005 JD 重复
- `data/test_cases_v1/resume/case_005_resume.md` → 可替换为 R08
- `data/test_cases_v1/resume/case_006_resume.md` → 可保留或优化
- `data/test_cases_v1/resume/case_007_resume.md` → 可保留或优化

### 已新建文件

- `data/test_cases_v1/cases/case_009.json` → A2 ✅ 已创建
- `data/test_cases_v1/cases/case_010.json` → B2 ✅ 已创建
- 可能的新 JD 文件（case_005 替换）
- 可能的新 resume 文件（R08 标准化）

---

## 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| V1 | 2025-06 | 8 个场景描述型方向 |
| V2 | 2026-06-29 | 重构为 MECE 双轴分类，明确 10 case 目标结构，识别 2 个空缺 |
| V2.1 | 2026-06-29 | 新建 case_009 (A2) 和 case_010 (B2)，填补矩阵空缺 |
| V2.2 | 2026-06-29 | C1 精简为单 case (005)，JD 复用 case_002；删除 case_006/007 |
