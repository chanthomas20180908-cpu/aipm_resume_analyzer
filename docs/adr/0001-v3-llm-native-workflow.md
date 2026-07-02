# ADR 0001: 新增 v3 三步 LLM-Native 工作流

日期：2026-07-01
状态：已决策

## 背景

原 `/analyze` 工作流（v2）的链路是：

1. JD 分析（LLM/规则）
2. 候选人分析（LLM/规则）
3. 匹配评分（规则）
4. 推荐结论（规则）
5. 文案生成（LLM）

在把 Step 1/2 改成 LLM 抽取后，用户发现：

- LLM 输出太长、包含大量英文枚举值，不适合中文场景；
- Step 1/2 的交付物只是“原文重排”，没有专家解读，无法直接给用户看；
- 中间规则评分层与 LLM 抽取的中文值不兼容，维护成本高。

因此决定新增一个只有三步的 LLM-Native 工作流，同时保留旧工作流不动。

## 决策

1. **新增 v3 工作流 `app/workflows/analyze_job_fit_v3.py`**，链路为：
   - Step 1：JD 分析（LLM）
   - Step 2：候选人分析（LLM）
   - Step 3：终局判断（LLM 直接输出 recommendation、match_score、summary、strengths、risks、next_actions）
2. **旧工作流 `app/workflows/analyze_job_fit.py` 和 `POST /analyze` 完全保留**，继续服务现有前端。
3. **新接口为 `POST /analyze/v3`**，新前端接入。
4. **Step 1/2 输出使用英文 key + 中文枚举值/内容**，不再为了迁就规则评分把中文值翻译回英文。
5. **v3 必须配置 LLM key**，无 key 时直接返回 503，不做 fallback。

## 取舍

| 方案 | 优点 | 缺点 |
|------|------|------|
| A. 在现有 v2 上改，保留规则评分 | 改动集中 | 中英文映射复杂，Step 1/2 输出被评分层绑架 |
| B. 新增 v3，彻底 LLM-Native | 输出更自然，更短，可直接阅读，旧接口稳定 | 需要维护两套工作流一段时间 |

选择 **B**。

## 影响

- 新增文件：`app/prompts_v3.py`、`app/capabilities/jd_analysis_v3.py`、`app/capabilities/candidate_analysis_v3.py`、`app/workflows/analyze_job_fit_v3.py`。
- 修改文件：`app/llm_client.py`、`app/main.py`。
- 旧工作流、旧 capability、旧 prompt 不改动。
- 后续如果 v3 稳定，可逐步让 `/analyze` 也切到 v3，届时再废弃旧工作流。
