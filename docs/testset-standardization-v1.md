# 测试样本标准化说明 V1

## 核心假设

- 当前阶段先做 `3` 组试样，验证目录结构、匿名化方式和 case 格式。
- 标准化目标不是保留原网页形态，而是沉淀成后续可直接用于标注和评测的统一样本。
- 所有公开简历样例只保留能力结构、项目经历、职责和结果表达，不保留身份信息。

## 目录结构

```text
data/test_cases_v1/
  cases/
  jd/
  resume/
```

## 文件类型

### 1. JD 文件

- 目录：`data/test_cases_v1/jd/`
- 格式：`.md`
- 内容：
  - 岗位名称
  - 来源链接
  - 原始 JD 摘录
  - 简要备注

### 2. 简历文件

- 目录：`data/test_cases_v1/resume/`
- 格式：`.md`
- 内容：
  - 匿名候选人画像
  - 经改写后的简历文本
  - 脱敏说明

### 3. Case 文件

- 目录：`data/test_cases_v1/cases/`
- 格式：`.json`
- 用途：
  - 把 `JD + 简历` 配成一组候选样本
  - 供后续加入 `golden_label`、`rubric` 和评测结果

## 当前 Case JSON 结构

```json
{
  "id": "case_001",
  "direction": "可迁移型案例",
  "jd_file": "data/test_cases_v1/jd/case_001_jd.md",
  "resume_file": "data/test_cases_v1/resume/case_001_resume.md",
  "jd_source_url": "",
  "resume_source_url": "",
  "candidate_type": "",
  "status": "draft_standardized",
  "notes": []
}
```

## 匿名化原则

- 删除：
  - 姓名
  - 电话
  - 邮箱
  - 精确学校学号
  - 精确公司与部门名（必要时泛化）
- 保留：
  - 年限
  - 岗位方向
  - 项目职责
  - 指标结果
  - 技术理解层级

## 当前试样覆盖方向

1. `可迁移型案例`
2. `真 AI 落地岗，候选人明显匹配`
3. `真 AI 落地岗，候选人 AI 证据明显不足`

## 下一步

- 在这 3 组试样基础上补 `golden_recommendation` 和 `gaps`
- 确认格式稳定后扩到完整 `8` 组

