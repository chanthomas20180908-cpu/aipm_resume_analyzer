# A1 离线逻辑测试

用于验证标准 `A1` 样本 `case_002` 是否与金标一致，且不触发 `/analyze` 的 trace 落盘。

## 目标

- 直接调用 capability 层：
  - `jd_analysis`
  - `candidate_analysis`
  - `match_scoring`
  - `recommendation`
- 不测 `narration` 和 LLM 文案增强。
- 若环境配置了 `DASHSCOPE_API_KEY` / `OPENAI_API_KEY`，`jd_analysis` / `candidate_analysis` 会走 LLM 抽取；否则 fallback 到规则 parser。
- 结果写到 `/tmp`，不改仓库数据文件。

## 运行命令

```bash
python3 scripts/run_a1_logic_test.py
```

可选参数：

```bash
python3 scripts/run_a1_logic_test.py \
  --case-file data/test_cases_v1/cases/case_002.json \
  --golden-file data/test_cases_v1/golden/case_002_golden.json \
  --output-dir /tmp
```

## 输出文件

- `/tmp/a1_case_002_actual.json`
  - 实际结构化结果，包含 `job_analysis`、`candidate_analysis`、`match_result` 关键字段。
- `/tmp/a1_case_002_eval.md`
  - 金标对比、断言结果、偏差归因、关键中间值。

## 当前断言

- `recommendation == 冲`
- `gate_check_result.passed == true`
- `gate_check_result.failed_reasons == []`
- `job_risk_level == low`
- `confidence.level == high`
- `weighted_match_score` 相对金标 `85` 允许偏差 `±5`
- 7 个维度分数逐项允许偏差 `±1`
- `non_compensatory_gaps` 为空
- `compensatory_gaps` 应体现业务贴合度问题，不应体现 AI/技术弱项

## 为什么不直接调用 `/analyze`

`/analyze` 会经过 `TraceLogger.write()`，默认落盘到仓库 `logs/`。这轮测试的目标是先验证规则逻辑，所以改为直接调用 capability 层，避免把离线评测日志写进仓库。

## 相关脚本

- `scripts/run_a1_logic_test.py` — A1 金标对比评测（v2 capability 层）
- `scripts/verify_llm_extraction.py` — case_002 新字段快速检查（v2）
- `scripts/verify_v3_workflow.py` — v3 工作流结构验证（mock LLM）

## v3 说明

本文档只描述 v2 工作流的 A1 测试。v3 工作流（`/analyze/v3`）不经过规则评分层，因此金标对比逻辑不直接适用，应使用 `scripts/verify_v3_workflow.py` 验证结构和字段完整性。
