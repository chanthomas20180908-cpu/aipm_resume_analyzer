# AI PM 岗位判断工具 - 当前后端逻辑说明

日期：2026-07-01  
文档目的：记录当前已经实现的后端逻辑，便于后续继续开发、改规则、调 prompt、接更多能力。

说明：

- 这份文档描述的是当前真实主链路
- 当前 `/analyze` 已经切到 v2 workflow
- 旧版 `app/analyzer.py` 仍保留在仓库里，但不再是主接口入口

## 1. 当前后端的定位

当前后端是一个 `FastAPI` 单体服务，负责三件事：

1. 提供页面入口和静态资源托管
2. 提供岗位分析接口
3. 按配置在文案生成阶段调用一次真实 LLM 做结果增强

当前版本不是完整平台，也不是多服务架构。  
重点是先把 `JD + 简历 -> 结构化判断 -> 结果输出` 这条链路跑通。

## 2. 当前目录中的后端相关文件

- [app/main.py](/Users/test/code/aipm_resume_analyzer/app/main.py)
- [app/workflows/analyze_job_fit.py](/Users/test/code/aipm_resume_analyzer/app/workflows/analyze_job_fit.py)
- [app/trace_logger.py](/Users/test/code/aipm_resume_analyzer/app/trace_logger.py)
- [app/capabilities/jd_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/jd_analysis.py)
- [app/capabilities/candidate_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/candidate_analysis.py)
- [app/capabilities/match_scoring.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/match_scoring.py)
- [app/capabilities/recommendation.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/recommendation.py)
- [app/capabilities/narration.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/narration.py)
- [app/jd_parser.py](/Users/test/code/aipm_resume_analyzer/app/jd_parser.py)
- [app/resume_parser.py](/Users/test/code/aipm_resume_analyzer/app/resume_parser.py)
- [app/llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py)
- [app/prompts.py](/Users/test/code/aipm_resume_analyzer/app/prompts.py)
- [app/analyzer.py](/Users/test/code/aipm_resume_analyzer/app/analyzer.py)
- [requirements.txt](/Users/test/code/aipm_resume_analyzer/requirements.txt)

## 3. 当前服务结构

### 3.1 FastAPI 入口

入口在 [app/main.py](/Users/test/code/aipm_resume_analyzer/app/main.py)。

当前做了这些事：

- 创建 `FastAPI` 应用
- 配置 `CORS`
- 挂载 `/static`
- 提供页面入口 `/`
- 提供健康检查 `/health`
- 提供示例数据 `/demo`
- 提供分析接口 `/analyze`

### 3.2 静态资源托管

当前后端直接托管前端静态资源：

- `/` 返回 `static/index.html`
- `/static/*` 返回静态 JS / CSS

当前还包含独立的前端交互验证页：

- `static/design-preview.html`
- `static/design-preview-01.html`

说明：

- 这些是设计验证用页面，不是正式首页
- `design-preview.html` 用于验证 `输入 -> loading -> 结果聚焦` 的单屏交互
- `design-preview-01.html` 用于验证梗化产品表达下的 `放瓜 -> 劈瓜 -> 看瓤` 三步页面
- `design-preview-01.html` 内置读取 `static/assets/pigua/frame-01.png` 到 `frame-05.png` 作为卡皮巴拉劈瓜帧动画素材；素材缺失时显示占位，不影响主流程
- 当前版本使用前端本地假数据，不调用 `/analyze`

这意味着当前部署方式很简单：

- 一个 Python 服务
- 同时负责 API 和页面

## 4. 当前接口

### 4.1 `GET /`

作用：

- 返回前端首页

当前实现：

- 直接返回 `static/index.html`

### 4.2 `GET /health`

作用：

- 健康检查
- 顺便暴露当前是否检测到 LLM 环境变量

返回结构：

```json
{
  "ok": true,
  "llm_configured": false
}
```

说明：

- `llm_configured` 只代表当前进程是否读到了 `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`
- 不代表真实模型一定可用

### 4.3 `GET /demo`

作用：

- 返回一组示例 JD、简历、用户身份、目标
- 供前端“加载示例”按钮使用

返回结构：

```json
{
  "jd_text": "...",
  "resume_text": "...",
  "user_level": "转岗PM",
  "goal": "转AI"
}
```

### 4.4 `POST /analyze`

作用：

- 核心分析接口

请求体结构：

```json
{
  "jd_text": "岗位 JD 文本",
  "resume_text": "简历文本",
  "user_level": "新人 | 转岗PM | 有经验PM | 有AI项目经验",
  "goal": "求稳 | 冲高薪 | 转AI | 找长期主线"
}
```

参数约束：

- `jd_text` 最少 30 个字符
- `resume_text` 最少 30 个字符
- `user_level` 和 `goal` 必须落在当前限定枚举里

## 5. 当前分析主链路

当前 `/analyze` 的执行顺序如下：

1. 接收前端输入
2. 进入 `workflows.analyze_job_fit.run(...)`
3. 执行 `JD 分析`（默认走 LLM 结构化抽取，失败 fallback 到规则版）
4. 执行 `候选人分析`（默认走 LLM 结构化抽取，失败 fallback 到规则版）
5. 执行 `匹配评分`
6. 执行 `推荐结论`
7. 执行 `文案生成`
8. 如果配置了 LLM，Step 1/2/5 均会调用真实 LLM
9. 生成 `trace_id` 和单次流程日志
10. 返回 v2 结构和兼容字段

可以理解为：

`规则判断仍控制最终 recommendation，LLM 已负责 Step 1/2 的结构化抽取和 Step 5 的结果增强。`

## 5.1 v3 工作流（新增）

除原有 v2 工作流外，新增了 `/analyze/v3` 入口，对应 `app/workflows/analyze_job_fit_v3.py`。

v3 是 LLM-Native 的三步工作流：

1. **Step 1：JD 分析**（LLM）
   - 输出英文 key、中文枚举值/内容。
   - 新增 `implied_requirements` 字段，输出 JD 原文背后的潜台词。
   - 新增 `jd_core_judgment` 字段，一句话总结岗位本质。
2. **Step 2：候选人分析**（LLM）
   - 输出英文 key、中文枚举值/内容。
   - 保留产品/商业视角证据和缺口。
   - 新增 `candidate_match_summary` 字段，一句话总结匹配判断。
3. **Step 3：终局判断**（LLM）
   - 直接输出 `recommendation`、`match_score`、`summary`、`strengths`、`risks`、`next_actions`。
   - 不再经过规则评分层。

v3 工作流要求必须配置 `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`，无 key 时返回 503。
旧 `/analyze`（v2）继续保留，前端可逐步切换到 `/analyze/v3`。

## 6. 当前 v2 模块职责

### 6.1 workflow

- [app/workflows/analyze_job_fit.py](/Users/test/code/aipm_resume_analyzer/app/workflows/analyze_job_fit.py)

职责：

- 顶层流程编排
- 聚合最终返回结构
- 写入 `meta.trace_id`
- 触发 trace 日志落盘

### 6.2 JD 分析

- [app/capabilities/jd_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/jd_analysis.py)
- [app/jd_parser.py](/Users/test/code/aipm_resume_analyzer/app/jd_parser.py)
- [app/llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py) `extract_jd_with_llm(...)`

职责：

- 默认调用 LLM 从原始 JD 文本抽取结构化岗位画像
- LLM 失败或未配置时，自动 fallback 到 `app/jd_parser.py` 规则版
- 归一化成 `job_analysis`
- 产出 `meta.jd_extraction` 与 `meta.jd_extraction_meta`

新增字段：

- `job_profile.industry_domain`：垂直行业（如 insurance、finance、healthcare）
- `job_profile.business_orientation`：`business-heavy | tech-heavy | hybrid`
- `job_profile.role_perspective`：`pm | engineer | hybrid`
- `job_profile.enterprise_type`：`traditional_enterprise | ai_native | hybrid`

### 6.3 候选人分析

- [app/capabilities/candidate_analysis.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/candidate_analysis.py)
- [app/resume_parser.py](/Users/test/code/aipm_resume_analyzer/app/resume_parser.py)
- [app/llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py) `extract_candidate_with_llm(...)`

职责：

- 默认调用 LLM 从简历文本抽取候选人画像、证据与缺口
- LLM 会收到 `job_analysis`，用于判断角色错配
- LLM 失败或未配置时，自动 fallback 到 `app/resume_parser.py` 规则版
- 生成 `candidate_analysis`
- 产出 `meta.resume_extraction`

新增字段：

- `candidate_profile.candidate_role_orientation`：`pm | engineer | researcher | ambiguous`
- `candidate_evidence.product_evidence`：产品经理视角证据
- `candidate_evidence.business_evidence`：业务/商业视角证据
- `role_mismatch_flag`：当 JD 要求 PM 但候选人明显是 engineer/researcher 时为 `true`

### 6.4 匹配评分

- [app/capabilities/match_scoring.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/match_scoring.py)

职责：

- 做 gate check
- 计算 7 个维度分
- 生成 `weighted_match_score`
- 生成 gaps / highlights / confidence / job_risk_level

### 6.5 推荐结论

- [app/capabilities/recommendation.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/recommendation.py)

职责：

- 把评分结果转成：
  - `recommendation`
  - `recommendation_reason`
  - `job_risk_level`
  - `candidate_readiness_level`

### 6.6 文案生成

- [app/capabilities/narration.py](/Users/test/code/aipm_resume_analyzer/app/capabilities/narration.py)

职责：

- 生成：
  - `summary`
  - `strengths`
  - `risks`
  - `next_actions`
- 如果 LLM 可用，则在 Step 5 调用一次真实模型做文案增强
- Step 1/2 的结构化抽取不在这里，分别由 `jd_analysis.py` / `candidate_analysis.py` 负责

### 6.7 Trace 日志

- [app/trace_logger.py](/Users/test/code/aipm_resume_analyzer/app/trace_logger.py)

职责：

- 为每次分析生成 `trace_id`
- 把整条流程落盘到 `logs/{trace_id}.md`
- 记录每一步的：
  - 输入
  - 输出
  - 关键信息
- 如果调用了 LLM，则把 request / response 记在对应步骤下面（Step 1/2/5 都会记录）

## 7. 当前返回结构

当前返回同时包含两层：

### 7.1 v2 主结构

- `job_analysis`
- `candidate_analysis`
- `match_result`
- `recommendation_result`
- `meta`

### 7.2 兼容字段

- `recommendation`
- `match_score`
- `job_type`
- `summary`
- `strengths`
- `risks`
- `next_actions`

## 8. 当前 LLM 链路

当前真实 LLM 链路如下：

- 是否启用：
  - `llm_is_configured()`
- 调用位置：
  - `app/capabilities/jd_analysis.py`（Step 1）
  - `app/capabilities/candidate_analysis.py`（Step 2）
  - `app/capabilities/narration.py`（Step 5）
- 实际调用函数：
  - `extract_jd_with_llm(...)`
  - `extract_candidate_with_llm(...)`
  - `enhance_v2_narration(...)`
- 当前每次分析最多调用 3 次 LLM
- LLM 已参与 JD/简历结构化抽取和结果文案增强
- 规则版 `app/jd_parser.py` / `app/resume_parser.py` 作为 fallback 保留

### 6.9 投递建议规则

最终 recommendation 由 `_recommendation()` 决定。

当前规则：

- 如果判定为明显 `伪 AI 岗`，直接 `避开`
- `match_score >= 78` 且风险不高 -> `冲`
- `match_score >= 64` -> `可投`
- `match_score >= 50` -> `谨慎`
- 其他 -> `避开`

这里的 recommendation 目前完全由规则控制。

### 6.10 风险与行动建议

当前风险由两部分组成：

1. 候选人风险
2. 岗位风险

候选人风险来自：

- AI 经验差距
- 场景抽象差距
- 交付差距
- 数据能力差距
- 业务结果表达差距
- 协作推动差距
- 技术理解差距

岗位风险来自：

- `伪 AI 岗`
- 协调倾向过高
- 指标责任过弱
- 落地深度过浅

行动建议由 `_next_actions()` 负责，当前主要根据：

- `ai_experience`
- `technical_understanding`
- `business_results`
- 当前 recommendation

来生成最多 3 条建议。

### 6.11 规则分析器输出结构

当前 `analyze_job_fit()` 返回：

```json
{
  "recommendation": "可投",
  "match_score": 73,
  "job_type": "成长型 AI PM",
  "job_signals": {},
  "candidate_signals": {},
  "strengths": [],
  "risks": [],
  "next_actions": [],
  "summary": "...",
  "meta": {
    "user_level": "转岗PM",
    "goal": "转AI",
    "jd_hits": {},
    "resume_hits": {}
  }
}
```

说明：

- `job_signals` 和 `candidate_signals` 是分数字段
- `jd_hits` 和 `resume_hits` 记录了命中的关键词
- `summary` 是规则生成的一句结论

## 7. LLM 增强层逻辑

LLM 增强层入口在 [app/llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py)，提示词统一维护在 [app/prompts.py](/Users/test/code/aipm_resume_analyzer/app/prompts.py)。

### 7.1 当前定位

当前 LLM 的职责不是做最终决策，而是：

- 在规则结果基础上，生成更自然的结果文案
- 改写 `summary`
- 改写 `strengths`
- 改写 `risks`
- 改写 `next_actions`

它不会改：

- `recommendation`
- `match_score`
- `job_type`

### 7.2 当前模型配置

默认配置如下：

- `base_url`: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `model`: `qwen-plus`

支持读取的环境变量：

- `DASHSCOPE_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

优先级：

- API Key 优先读 `DASHSCOPE_API_KEY`
- 如果没有，再读 `OPENAI_API_KEY`
- `base_url` 默认走 DashScope 兼容接口
- `model` 默认是 `qwen-plus`

### 7.3 是否启用 LLM

由 `llm_is_configured()` 控制。

当前逻辑很简单：

- 只要检测到 `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`
- 就认为 LLM 已配置

注意：

- 这里只是“环境变量存在”
- 还没有额外做模型可达性探测

### 7.4 Prompt 结构

当前是单次调用，不分抽取和生成两步。

提示词管理方式：

- `LLM_RESULT_SYSTEM_PROMPT` 放在 `app/prompts.py`
- `build_llm_result_user_prompt(payload)` 放在 `app/prompts.py`
- `app/llm_client.py` 只负责构造 payload、调用模型、解析返回

Prompt 结构：

1. `system prompt`
   约束模型：
   - 只能根据 JD、简历和规则结果生成解释
   - 不能改 recommendation / match_score / job_type
   - 不能编造经历
   - 只输出 JSON

2. `user prompt`
   输入：
   - `user_level`
   - `goal`
   - `jd_text`
   - `resume_text`
   - `rule_result`

   要求输出字段：
   - `summary`
   - `strengths`
   - `risks`
   - `next_actions`

### 7.5 当前输出解析

LLM 返回内容后，后端会：

1. 读取 `message.content`
2. 尝试从中提取 JSON
3. 支持去掉 ```json 包裹
4. 如果拿不到合法 JSON，抛 `LLMEnhancementError`

### 7.6 当前结果合并方式

LLM 成功后：

- 复制一份规则结果
- 只替换：
  - `summary`
  - `strengths`
  - `risks`
  - `next_actions`
- 在 `meta.llm` 中写入：
  - `used: true`
  - `provider: dashscope-compatible`
  - `model`

### 7.7 当前 fallback 逻辑

如果发生以下任一情况：

- 没配置 API key
- 构建 client 失败
- 模型返回内容无法解析成 JSON

则：

- 不中断接口
- 直接返回规则结果

如果是执行异常导致 fallback，当前会把错误信息挂到：

```json
meta.llm.error
```

这保证了：

- 前端不会因为 LLM 失败直接崩掉
- 系统始终能给结果

## 8. 当前 `meta` 字段含义

当前结果中的 `meta` 用于调试和可追踪性。

已包含内容：

- `user_level`
- `goal`
- `jd_hits`
- `resume_hits`
- `llm`

其中 `llm` 结构目前大致如下：

```json
{
  "used": false,
  "provider": "rule-fallback",
  "model": null
}
```

或：

```json
{
  "used": true,
  "provider": "dashscope-compatible",
  "model": "qwen-plus"
}
```

## 9. 当前后端的边界

当前后端已经实现：

- 页面可访问
- API 可用
- 规则分析可用
- DashScope 兼容 OpenAI 接口可接入
- LLM 失败自动回退

当前后端还没有实现：

- 数据库存储
- 用户系统
- 历史记录
- 文件上传与 PDF 解析
- LLM 结构化抽取阶段（Step 1/2）已实现，但仍需测试集校准
- Prompt 配置中心
- 日志系统
- 单元测试
- 更细的异常监控

## 10. 当前实现的优点

当前这套实现的优点很明确：

1. 链路短，容易 debug
2. 没有 LLM 也能跑
3. 有 LLM 时能显著改善结果文案
4. recommendation 仍被规则控制，输出更稳
5. 单人开发维护成本低

## 11. 当前实现的主要问题

当前后端也有几个明显问题：

1. 规则层仍然比较粗糙  
   主要还是关键词命中，不是真语义理解。已作为 LLM 失败 fallback。

2. LLM 已参与 Step 1/2 结构化抽取  
   但仍需通过测试集持续验证输出稳定性。

3. `user_level` 还没有真正进入评分逻辑  
   现在只是元信息。

4. prompt 还比较简陋  
   只是第一版可用，不是优化后的生产 prompt。

5. 没有测试  
   当前验证主要靠手工请求和页面试跑。

## 12. 当前最适合的后续演进方向

如果继续迭代后端，最合理的顺序应该是：

1. 继续用测试集校准 Step 1/2 的 LLM 提取稳定性
2. 把 LLM 抽取来源在前端显式展示
3. 再逐步削弱纯关键词规则的权重
4. 最后再考虑持久化、历史记录和上传解析

当前阶段，不建议一口气把系统改成重架构。  
现在最重要的是继续提升：

- 判断质量
- 输出稳定性
- 结果可信度
