# 真实简历来源抓取记录 v1

## 核心结论

- 这轮实际可落盘的高质量来源是 `R03` 和 `R04`。
- `R02` 可以抓到正文，但它是公开人才库，不是单人原始简历，只能算 `半原始来源`。
- `R01` 当前无法稳定抓取：匿名访问被上游拦截，不应强行入池。

## 抓取结果

| 来源 ID | 结果 | 本地文件 | 结论 |
|---|---|---|---|
| R01 | 失败 | 无 | `maimai.cn` 通过 `r.jina.ai` 返回 `451 SecurityCompromiseError`，匿名访问被封。当前不建议继续用静态抓取。 |
| R02 | 成功（摘录） | [r02_web3_talent_pool_excerpt.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r02_web3_talent_pool_excerpt.md) | 能抓到公开人才库正文，适合做候选池参考，不适合直接当黄金样本。 |
| R03 | 成功 | [r03_shivika_resume_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r03_shivika_resume_raw.md) | 个人站 + PDF 简历，真实性高，正文密度足够，可以进入测试集候选。 |
| R04 | 成功 | [r04_jillani_resume_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r04_jillani_resume_raw.md) | 公开 PDF 简历，信息完整，项目经历密度高，可以进入测试集候选。 |
| R05 | 成功 | [r05_shantanu_portfolio_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r05_shantanu_portfolio_raw.md) | 公开个人站，AI PM 信息密度高，适合作为强 AI PM 候选来源，但不是传统 PDF 简历。 |
| R06 | 成功 | [r06_kelsey_resume_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r06_kelsey_resume_raw.md) | AI Advisory Product Manager + 数据科学背景，兼具路线图、UAT、forecasting、stakeholder 信息，适合作为偏分析和结果导向的 PM 样本。 |
| R08 | 成功 | [r08_mai_resume_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r08_mai_resume_raw.md) | Senior Technical Product Manager，含 AI 产品、SaaS、NPS、backlog、release planning，适合作为强交付/平台型 PM 样本。 |
| R09 | 成功 | [r09_namratha_resume_raw.md](/Users/test/code/aipm_resume_analyzer/data/test_cases_v1/resume_candidates/r09_namratha_resume_raw.md) | Technical Product Manager，含 AI tooling、API 平台、PRD、analytics、A/B testing、onboarding，真实性高，适合替换中等强度 PM 匿名样本。 |

## 处理说明

- 本轮只做了 `最小脱敏`：
  - 邮箱替换为 `[redacted_email]`
  - 电话替换为 `[redacted_phone]`
  - 明显实名替换为 `[redacted_name]`
- 保留了：
  - 原始经历顺序
  - 项目与职责描述
  - 技能列表
  - 自我总结与冗余关键词

## 来源判断

### R03

- 来源：`https://sbisen.github.io/files/Resume_Shivika.pdf`
- 类型：个人站附带公开 PDF 简历
- 判断：
  - 真实性高
  - 不是教程文
  - 不是平台二次整理
  - 内容接近真实投递简历文本

### R04

- 来源：`https://mgjillanimughal.github.io/Jillani%20Resume.pdf`
- 类型：公开 PDF 简历
- 判断：
  - 真实性高
  - 文本原始度高
  - 含完整工作经历、项目经历、技能、教育和证书
  - 适合做“技术强、AI 工程能力强”的候选人样本

### R02

- 来源：`https://abetterweb3.notion.site/57b3f805061944229c495d20284ce161`
- 类型：公开人才库
- 判断：
  - 能抓到正文
  - 不是单人原始简历
- 更适合做能力结构参考或补充样本，不适合做第一批黄金样本

### R05

- 来源：`https://shantanu9.github.io/`
- 类型：AI 产品经理个人站
- 判断：
  - 真实性高
  - 不是传统 PDF 简历，但包含大量可视作简历原文的项目、指标、roadmap、GTM 信息
- 适合后续映射到强 AI PM / GTM / Agentic AI 方向样本

### R06

- 来源：`https://kelseygonzalez.github.io/files/resume.pdf`
- 类型：公开 PDF 简历
- 判断：
  - 真实性高
  - 兼具产品与数据科学背景
  - 有 `AI Advisory Product Manager`、`roadmap`、`pilot`、`forecasting`、`dashboard`、`stakeholder` 等强产品证据
  - 更适合替换 `case_007` 一类对结果和指标敏感的样本

### R08

- 来源：`https://lephanthuymai.github.io/media/resume.pdf`
- 类型：公开 PDF 简历
- 判断：
  - 真实性高
  - 偏资深技术产品 / 交付 / 平台管理路线
  - 含 `Katalon AI`、`product architecture`、`backlog`、`release planning`、`NPS` 等线索
  - 更适合替换 `case_005` 这类强交付、平台型 PM 匿名样本

### R09

- 来源：`https://drive.google.com/uc?export=download&id=1gyEJqVQILpkge0qgQEw3ljmu7R9csmoo`
- 原页面：`https://namrathalb.github.io/`
- 类型：公开 PDF 简历
- 判断：
  - 真实性高
  - 贴近真实产品经理投递文本
  - 有 `AI-powered feature`、`internal AI tooling`、`analytics dashboard`、`PRD`、`API specifications`、`A/B testing`、`customer onboarding`
  - 适合替换 `case_006` 或 `case_007` 这类中等强度产品样本

### R01

- 来源：`https://maimai.cn/article/detail?efid=PDMzRQXInfRaxR8ww-3-rA&fid=1869448815`
- 结果：
  - 静态抓取超时或无正文
  - `r.jina.ai` 返回 `451 SecurityCompromiseError`
- 判断：
  - 当前不可稳定获取
  - 除非后续改用浏览器态抓取，否则先排除

## 下一步建议

1. 先用 `R03`、`R04` 替换当前低真实性的匿名简历样本
2. `R02` 只作为候选池参考，不直接写入黄金测试集
3. 继续补 `2-3` 份正式岗位、非教程、可直接拿到正文的公开简历来源

## 已执行替换

- `R03 -> case_002`
  - 方向：`真 AI 落地岗，候选人明显匹配`
- `R04 -> case_008`
  - 方向：`行业 / 场景高度相关岗`
- `Mackenzie Clark -> case_001`
  - 方向：`可迁移型案例`

## 当前优先替换建议

1. `R08 -> case_005`
   - 原因：强交付、强组织与平台管理，比当前匿名改写更真实
2. `R09 -> case_006`
   - 原因：有 AI tooling 和 PRD/analytics/onboarding 证据，适合测试“有 AI 词汇也有部分落地，但不一定足够强”
3. `R06 -> case_007`
   - 原因：结果、指标、路线图、pilot、forecasting 证据完整，适合测试结果导向判断
