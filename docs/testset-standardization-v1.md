# 测试样本标准化说明 V1

## 核心假设

- 当前阶段先做 `3` 组试样，验证目录结构、匿名化方式和 case 格式。
- 样本文件现在保存的是 `原始输入风格文本`，不是摘要版文本。
- 所有公开简历样例只做 `脱敏 + 最小清洗`，不再先做总结式提炼。

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
  - 原始 JD 文本
  - 简要备注

### 2. 简历文件

- 目录：`data/test_cases_v1/resume/`
- 格式：`.md`
- 内容：
  - 匿名候选人画像
  - 原始简历风格文本
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
  - 完整工作经历结构
  - 项目职责
  - 指标结果
  - 技术理解层级

## 当前样本覆盖方向

1. `可迁移型案例`
2. `真 AI 落地岗，候选人明显匹配`
3. `真 AI 落地岗，候选人 AI 证据明显不足`
4. `伪 AI 岗 / 换皮岗`
5. `强交付、弱技术理解`
6. `有 AI buzzword，但无落地结果`
7. `指标和结果导向强岗位`
8. `行业 / 场景高度相关岗`

## 当前处理原则

- `jd/*.md`：尽量保存用户真实会粘贴进系统的长文本
- `resume/*.md`：尽量保存完整经历、项目、技能、教育等原始简历结构
- 允许保留：
  - 公司介绍
  - 薪资地点
  - 福利标签
  - 发布人口吻
  - 页面里的无关附言
  - 简历里的自我评价和套话
- 只做：
  - 脱敏
  - 格式清洗
  - 必要的轻量泛化

## 下一步

- 再进入 `golden_recommendation` 和 `gaps` 标注
