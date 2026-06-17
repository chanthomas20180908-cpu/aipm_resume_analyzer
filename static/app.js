const form = document.getElementById("analyze-form");
const loadDemoButton = document.getElementById("load-demo");
const submitButton = document.getElementById("submit-button");
const statusLine = document.getElementById("status-line");
const recommendationBadge = document.getElementById("recommendation-badge");
const summaryBox = document.getElementById("summary-box");
const matchScore = document.getElementById("match-score");
const jobType = document.getElementById("job-type");
const strengthsList = document.getElementById("strengths-list");
const risksList = document.getElementById("risks-list");
const actionsList = document.getElementById("actions-list");

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
  document.getElementById("user-level").value = data.user_level;
  document.getElementById("goal").value = data.goal;
  setStatus("示例已填充，可以直接开始分析。");
}

async function handleSubmit(event) {
  event.preventDefault();

  const payload = {
    jd_text: document.getElementById("jd-text").value.trim(),
    resume_text: document.getElementById("resume-text").value.trim(),
    user_level: document.getElementById("user-level").value,
    goal: document.getElementById("goal").value,
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
    jobType.textContent = result.job_type;
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
