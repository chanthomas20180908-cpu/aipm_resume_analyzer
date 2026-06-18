# AI PM 岗位判断工具 - 当前后端逻辑说明

日期：2026-06-18  
文档目的：记录当前已经实现的后端逻辑，便于后续继续开发、改规则、调 prompt、接更多能力

## 1. 当前后端的定位

当前后端是一个 `FastAPI` 单体服务，负责三件事：

1. 提供页面入口和静态资源托管
2. 提供岗位分析接口
3. 在规则分析结果之上，按配置调用真实 LLM 做文案增强

当前版本不是完整平台，也不是多服务架构。  
重点是先把 `JD + 简历 -> 结构化判断 -> 结果输出` 这条链路跑通。

## 2. 当前目录中的后端相关文件

- [app/main.py](/Users/test/code/aipm_resume_analyzer/app/main.py)
- [app/analyzer.py](/Users/test/code/aipm_resume_analyzer/app/analyzer.py)
- [app/llm_client.py](/Users/test/code/aipm_resume_analyzer/app/llm_client.py)
- [app/prompts.py](/Users/test/code/aipm_resume_analyzer/app/prompts.py)
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
2. 调用规则分析器 `analyze_job_fit`
3. 先得到一份纯规则结果
4. 给结果补上默认 `meta.llm`
5. 判断是否配置了 LLM
6. 如果未配置，直接返回规则结果
7. 如果已配置，调用 `enhance_analysis_result`
8. 如果 LLM 成功返回，使用增强后的结果
9. 如果 LLM 报错，保留规则结果并在 `meta.llm.error` 中记录错误

可以理解为：

`规则判断是主链路，LLM 是增强层，不是决策核心。`

## 6. 规则分析器逻辑

规则分析器在 [app/analyzer.py](/Users/test/code/aipm_resume_analyzer/app/analyzer.py)。

### 6.1 输入

输入 4 项：

- `jd_text`
- `resume_text`
- `user_level`
- `goal`

注意：

- 当前 `user_level` 只进入结果 `meta`，还没有深入参与评分逻辑
- 当前 `goal` 会进入权重调整逻辑

### 6.2 两组关键词字典

当前分析器有两套关键词映射：

1. `JD_SIGNAL_KEYWORDS`
2. `RESUME_SIGNAL_KEYWORDS`

它们分别用于扫描：

- 岗位文本里的岗位信号
- 简历文本里的候选人信号

### 6.3 当前岗位侧维度

当前岗位侧维度共 6 个：

- `ai_density`
- `user_proximity`
- `delivery_depth`
- `data_ownership`
- `business_link`
- `coordination_bias`

### 6.4 当前候选人侧维度

当前候选人侧维度共 7 个：

- `ai_experience`
- `product_design`
- `abstraction`
- `technical_understanding`
- `data_analysis`
- `business_results`
- `cross_team_push`

### 6.5 关键词扫描方式

当前扫描逻辑比较直接：

- 把文本转小写
- 遍历每个维度下的关键词
- 只要关键词出现在文本里就算命中
- 每个维度保留最多 4 个命中关键词
- 分数按命中数量计算

当前分数规则：

- 最低分是 `1`
- 最高分是 `5`
- 命中越多，分越高

这意味着当前规则仍然是一个 `轻量启发式评分器`，并不是语义理解模型。

### 6.6 岗位类型判断

岗位类型由 `_job_type()` 决定，当前规则是：

- `ai_density >= 4` 且 `delivery_depth >= 4` -> `技术落地型 AI PM`
- `coordination_bias >= 4` 且 `ai_density <= 2` -> `协调型 PM`
- `ai_density <= 2` 且 `coordination_bias >= 3` -> `伪 AI 岗`
- `business_link >= 4` -> `增长型 AI PM`
- 其他情况 -> `成长型 AI PM`

这是一个硬编码分类规则，后续可以继续优化。

### 6.7 匹配度计算

匹配度由 `_score_alignment()` 负责。

当前做法：

1. 建立岗位维度和候选人维度的映射关系
2. 根据 `goal` 给部分岗位维度加权
3. 比较岗位要求和候选人对应能力的差值
4. 同时单独看一次 `technical_understanding` 和 `ai_density` 的技术落差
5. 输出：
   - `match_score`
   - `strengths`
   - `risks`

当前映射关系：

- `ai_density -> ai_experience`
- `user_proximity -> abstraction`
- `delivery_depth -> product_design`
- `data_ownership -> data_analysis`
- `business_link -> business_results`
- `coordination_bias -> cross_team_push`

### 6.8 目标加权

当前 `goal` 会影响岗位要求权重：

- `求稳`：提升 `coordination_bias`、`user_proximity`
- `冲高薪`：提升 `ai_density`、`business_link`
- `转AI`：提升 `ai_density`、`delivery_depth`
- `找长期主线`：提升 `delivery_depth`、`data_ownership`

这不是改最终 recommendation，而是先改变匹配判断中的要求强度。

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
- 真正的 LLM 结构化抽取阶段
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
   主要还是关键词命中，不是真语义理解。

2. LLM 只做文案增强  
   还没有参与更可靠的结构化抽取。

3. `user_level` 还没有真正进入评分逻辑  
   现在只是元信息。

4. prompt 还比较简陋  
   只是第一版可用，不是优化后的生产 prompt。

5. 没有测试  
   当前验证主要靠手工请求和页面试跑。

## 12. 当前最适合的后续演进方向

如果继续迭代后端，最合理的顺序应该是：

1. 先把 LLM 输出来源在前端显式展示
2. 再把 LLM 拆成 `抽取阶段 + 解释阶段`
3. 再逐步削弱纯关键词规则的权重
4. 最后再考虑持久化、历史记录和上传解析

当前阶段，不建议一口气把系统改成重架构。  
现在最重要的是继续提升：

- 判断质量
- 输出稳定性
- 结果可信度
