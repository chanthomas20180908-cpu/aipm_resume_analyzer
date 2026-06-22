const form = document.getElementById("analyze-form");
const loadDemoButton = document.getElementById("load-demo");
const submitButton = document.getElementById("submit-button");
const statusLine = document.getElementById("status-line");
const recommendationBadge = document.getElementById("recommendation-badge");
const summaryBox = document.getElementById("summary-box");
const matchScore = document.getElementById("match-score");
const jobType = document.getElementById("job-type");
const businessDomain = document.getElementById("business-domain");
const aiMaturity = document.getElementById("ai-maturity");
const deliveryMode = document.getElementById("delivery-mode");
const technicalDepth = document.getElementById("technical-depth");
const gateStatus = document.getElementById("gate-status");
const jobRiskLevel = document.getElementById("job-risk-level");
const readinessLevel = document.getElementById("readiness-level");
const confidenceLevel = document.getElementById("confidence-level");
const confidenceScore = document.getElementById("confidence-score");
const dimensionList = document.getElementById("dimension-list");
const strengthsList = document.getElementById("strengths-list");
const risksList = document.getElementById("risks-list");
const actionsList = document.getElementById("actions-list");

const FIELD_LABELS = {
  enterprise_collaboration: "企业协作 / 内部效率",
  internal_ai_platform: "内部 AI 平台",
  ai_workflow_tool: "AI 工作流工具",
  marketing_ai_product: "营销 AI 产品",
  robotics_ai_product: "机器人 / 多模态 AI",
  general_ai_pm: "通用 AI 产品",
  marketing: "营销",
  collaboration: "协作 / 内部效率",
  knowledge_management: "知识管理",
  education: "教育",
  robotics: "机器人 / 多模态",
  efficiency: "效率工具",
  general: "通用",
  concept_heavy: "概念偏重",
  application_driven: "应用落地型",
  deep_delivery: "深度交付型",
  "0_to_1": "从 0 到 1",
  "1_to_10": "持续迭代",
  platform: "平台型",
  scenario_driven: "场景型",
  mixed: "混合型",
  low: "低",
  medium: "中",
  high: "高",
  ready: "准备好了",
  "near-ready": "接近可投",
  stretch: "需要拉伸",
  "not-ready": "暂不适合",
};

const DIMENSION_LABELS = {
  ai_understanding: "AI 理解",
  scenario_abstraction: "场景抽象",
  workflow_design: "工作流设计",
  delivery_execution: "交付执行",
  data_metrics: "数据与指标",
  stakeholder_push: "跨团队推进",
  business_fit: "业务贴合度",
};

function setList(element, items) {
  element.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  });
}

function setStatus(message) {
  statusLine.textContent = message;
}

function displayValue(value) {
  if (value === null || value === undefined || value === "") {
    return "--";
  }
  return FIELD_LABELS[value] || value;
}

function setText(element, value) {
  element.textContent = displayValue(value);
}

function renderDimensions(scores, confidence) {
  dimensionList.innerHTML = "";
  const entries = Object.entries(scores || {});
  if (!entries.length) {
    dimensionList.innerHTML = `<div class="dimension-item empty">等待分析</div>`;
    confidenceScore.textContent = "--";
    return;
  }

  entries.forEach(([key, value]) => {
    const item = document.createElement("div");
    item.className = "dimension-item";
    const percent = Math.max(0, Math.min(100, (Number(value) / 5) * 100));
    item.innerHTML = `
      <div class="dimension-head">
        <span class="dimension-label">${DIMENSION_LABELS[key] || key}</span>
        <span class="dimension-score">${value}/5</span>
      </div>
      <div class="dimension-bar">
        <span class="dimension-bar-fill" style="width:${percent}%"></span>
      </div>
    `;
    dimensionList.appendChild(item);
  });

  if (confidence && typeof confidence.score !== "undefined") {
    confidenceScore.textContent = `判断置信度 ${confidence.score}`;
  } else {
    confidenceScore.textContent = "--";
  }
}

function setRecommendation(value) {
  recommendationBadge.textContent = value;
  recommendationBadge.className = "result-badge";

  if (value === "冲") {
    recommendationBadge.style.background = "rgba(109, 148, 100, 0.16)";
    recommendationBadge.style.color = "#456449";
  } else if (value === "可投") {
    recommendationBadge.style.background = "rgba(146, 171, 118, 0.18)";
    recommendationBadge.style.color = "#5a7047";
  } else if (value === "谨慎") {
    recommendationBadge.style.background = "rgba(201, 125, 82, 0.16)";
    recommendationBadge.style.color = "#9d603d";
  } else if (value === "避开") {
    recommendationBadge.style.background = "rgba(164, 94, 94, 0.14)";
    recommendationBadge.style.color = "#8d4747";
  } else {
    recommendationBadge.classList.add("idle");
  }
}

async function loadDemo() {
  setStatus("正在加载示例…");
  const response = await fetch("/demo");
  const data = await response.json();
  document.getElementById("jd-text").value = data.jd_text;
  document.getElementById("resume-text").value = data.resume_text;
  setStatus("示例已填充，可以直接开始分析。");
}

async function handleSubmit(event) {
  event.preventDefault();

  const payload = {
    jd_text: document.getElementById("jd-text").value.trim(),
    resume_text: document.getElementById("resume-text").value.trim(),
  };

  submitButton.disabled = true;
  setStatus("正在分析岗位和你的匹配情况…");
  setRecommendation("分析中");

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("分析失败，请检查输入长度后重试。");
    }

    const result = await response.json();
    setRecommendation(result.recommendation);
    summaryBox.innerHTML = `<p class="summary-text">${result.summary}</p>`;
    matchScore.textContent = `${result.match_score}`;
    setText(jobType, result.job_type);
    setText(businessDomain, result.job_analysis?.job_profile?.business_domain);
    setText(aiMaturity, result.job_analysis?.job_profile?.ai_maturity);
    setText(deliveryMode, result.job_analysis?.job_profile?.delivery_mode);
    setText(technicalDepth, result.job_analysis?.job_requirements?.technical_depth);
    gateStatus.textContent = result.match_result?.gate_check_result?.passed ? "通过" : "未通过";
    setText(jobRiskLevel, result.recommendation_result?.job_risk_level);
    setText(readinessLevel, result.recommendation_result?.candidate_readiness_level);
    setText(confidenceLevel, result.match_result?.confidence?.level);
    renderDimensions(result.match_result?.dimension_scores, result.match_result?.confidence);
    setList(strengthsList, result.strengths);
    setList(risksList, result.risks);
    setList(actionsList, result.next_actions);
    setStatus("分析完成。可以继续修改内容再分析一次。");
  } catch (error) {
    setRecommendation("等待分析");
    summaryBox.innerHTML = `<p class="summary-text">${error.message}</p>`;
    setStatus("这次没跑通，先检查文本长度和格式。");
  } finally {
    submitButton.disabled = false;
  }
}

loadDemoButton.addEventListener("click", loadDemo);
form.addEventListener("submit", handleSubmit);
