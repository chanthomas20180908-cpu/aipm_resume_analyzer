from __future__ import annotations

import json
from typing import Any, Dict


JD_V3_SYSTEM_PROMPT = (
    "你是资深 AI PM 岗位分析专家与业务架构师，熟悉 TOGAF 业务架构、ArchiMate 业务层建模、"
    "业务流程分析和 AI 产品生命周期。基于 JD 原文分析该岗位入职后负责的业务工作流程，输出结构化判断。"
    "只基于原文，不编造。输出必须是合法 JSON，不要 markdown、不要解释、不要注释。"
)

CANDIDATE_V3_SYSTEM_PROMPT = (
    "你是资深 AI PM 简历分析专家与人才评估顾问。基于简历原文和目标岗位关键信息，"
    "先识别候选人的证据类型（可建模能力、客观背景事实、主观能力声明），再生成匹配判断。"
    "只基于原文，不编造经历。输出必须是合法 JSON，不要 markdown、不要解释、不要注释。"
)

FINAL_V3_SYSTEM_PROMPT = (
    "你是资深 AI PM 求职顾问。基于 JD 分析、候选人分析和原始文本，给出最终投递建议。"
    "只基于提供的信息做判断，不编造经历。输出必须是合法 JSON，不要 markdown、不要解释、不要注释。"
)


JD_V3_OUTPUT_SCHEMA = """{
  "jd_core_judgment": "50字以内：岗位本质、值不值得投、适合什么人",
  "key_requirements": ["最多3条，岗位真正需要的核心能力/经验，每条≤30字"],
  "key_risks": ["最多3条，投递前必须知道的风险，每条≤30字"],
  "role_type": "产品型|工程型|混合型",
  "business_context": "30字以内：行业/场景一句话，如保险客服Agent落地",
  "business_flow": {
    "analysis_scope": "岗位入职后负责的业务工作流程",
    "value_stream": {
      "name": "≤30字：端到端价值流名称",
      "description": "≤60字：价值流描述",
      "evidence_type": "explicit|inferred",
      "source_evidence": ["JD 原文证据片段"]
    },
    "end_to_end_flow": [
      {"sequence": 1, "process_id": "P1", "process_name": "≤20字流程名"}
    ],
    "processes": [
      {
        "process_id": "P1",
        "process_name": "≤20字，名词+动词或对象+过程",
        "process_goal": "≤40字：该流程要达成的业务目标",
        "lifecycle_stage": "≤20字：生命周期阶段，如场景探索/方案设计/上线运营",
        "trigger": "≤30字：流程触发条件",
        "inputs": ["≤20字输入业务对象"],
        "outputs": ["≤20字输出业务对象"],
        "primary_role": "≤15字：主责角色",
        "participating_roles": ["≤15字参与角色"],
        "activities": [
          {
            "activity_id": "P1-A1",
            "activity_name": "≤20字，动宾结构，禁止'负责''参与''推动'",
            "activity_goal": "≤30字：该活动目标",
            "accountable_role": "≤15字：主责角色",
            "responsible_roles": ["≤15字执行角色"],
            "supporting_roles": ["≤15字协作角色"],
            "tasks": ["≤20字核心任务1", "≤20字核心任务2"],
            "inputs": ["≤20字输入业务对象"],
            "outputs": ["≤20字输出业务对象"],
            "business_objects": ["≤20字业务对象"],
            "source_evidence": ["JD 原文证据片段"],
            "evidence_type": "explicit|inferred",
            "confidence": 0.8
          }
        ],
        "previous_processes": ["P0"],
        "next_processes": ["P2"],
        "feedback_to_processes": ["P1"]
      }
    ],
    "roles": [
      {
        "role_name": "≤20字角色名",
        "role_type": "internal|customer|business|product|technical|delivery|operations",
        "main_responsibilities": ["≤30字主要职责"],
        "source_evidence": ["JD 原文证据片段"],
        "evidence_type": "explicit|inferred"
      }
    ],
    "business_objects": [
      {
        "object_name": "≤20字业务对象名",
        "object_type": "requirement|process|rule|plan|dataset|model|metric|report|case|sop|other",
        "created_by_activities": ["P1-A1"],
        "used_by_activities": ["P2-A1"],
        "evidence_type": "explicit|inferred"
      }
    ],
    "role_responsibility_summary": {
      "primary_responsibilities": ["≤30字岗位主责"],
      "coordination_responsibilities": ["≤30字协调职责"],
      "likely_non_execution_responsibilities": ["≤30字非执行职责"],
      "responsibility_span": "≤60字：岗位责任范围总结"
    },
    "uncertainties": [
      {
        "question": "≤40字信息缺口问题",
        "why_it_matters": "≤40字为什么影响匹配判断",
        "related_process": "相关流程名或ID",
        "recommended_interview_question": "≤40字建议面试反问"
      }
    ],
    "overall_judgment": {
      "process_coverage": "≤40字：流程覆盖度评价",
      "role_characteristics": "≤40字：岗位角色特征",
      "potential_boundary_risks": ["≤40字潜在边界风险"]
    }
  }
}"""


CANDIDATE_V3_OUTPUT_SCHEMA = """{
  "candidate_profile": "50字以内：候选人画像，如5年AI工程师，强技术交付",
  "role_mismatch_flag": false,
  "candidate_match_summary": "50字以内：与这个岗位的核心匹配判断",
  "match_points": ["最多3条，每条≤30字，必须引用 candidate_evidence 中的具体证据"],
  "gaps": ["最多3条，每条≤30字，必须是对目标岗位重要的真实缺口"],
  "candidate_evidence": {
    "modeled_capabilities": [
      {
        "capability_name": "能力名称，如业务流程设计",
        "task_name": "任务名称",
        "inputs": ["输入业务对象1"],
        "actions": ["具体动作1"],
        "outputs": ["输出业务对象1"],
        "outcomes": ["结果或效果1"],
        "project_context": "≤30字项目背景",
        "responsibility_level": "participated|executed|owned|led",
        "evidence_text": "简历原文证据片段",
        "completeness": "complete|partial",
        "confidence": 0.82
      }
    ],
    "incomplete_capabilities": [
      {
        "capability_name": "能力名称",
        "known": {"task": "已知的任务线索"},
        "unknown": ["输入", "具体动作", "输出", "责任范围", "结果"],
        "confidence": 0.45
      }
    ],
    "objective_facts": [
      {
        "fact_name": "事实名称，如产品经理工作年限",
        "fact_type": "work_duration|job_title|company|industry|education|degree|major|certificate|award",
        "value": "5年",
        "evidence_text": "简历原文证据片段",
        "verifiability": "high|medium|low"
      }
    ],
    "subjective_claims": [
      {
        "claim_name": "声明名称，如执行力",
        "claim_type": "work_style|personality|self_evaluation",
        "value": "强",
        "evidence_text": "简历原文",
        "supporting_evidence": ["支持该声明的具体任务证据"],
        "evidence_strength": "self_report_only|partially_supported|supported"
      }
    ]
  }
}"""


def build_jd_v3_user_prompt(jd_text: str) -> str:
    return (
        "请分析下面的 JD 原文，输出一个 JSON 对象。字段名必须用英文，字段值必须用中文。\n\n"
        "## 目的\n"
        "判断这个岗位入职后实际负责什么业务流程、值不值得投、主要风险是什么。\n\n"
        "## 你的角色\n"
        "你是熟悉 TOGAF 业务架构、ArchiMate 业务层建模、AI 产品生命周期的业务架构师。"
        "本任务分析的是该岗位入职后负责的业务工作流程，不是招聘流程。\n\n"
        "## 建模概念（必须严格区分）\n"
        "1. 业务价值流 Value Stream：岗位最终参与的端到端业务价值链，例如“AI 场景从发现到上线运营”。\n"
        "2. 业务流程 Business Process：为实现业务目标的一组相关活动，名称用“名词+动词”或“对象+过程”，"
        "例如“业务场景探索”“Agent 方案设计”。不要把“沟通能力”“熟悉大模型”识别为流程。\n"
        "3. 业务活动 Business Activity：流程中可分配给某个角色、具有明确输入输出的工作单元，使用动宾结构。\n"
        "   错误：负责需求分析、参与方案设计、推动项目上线。\n"
        "   正确：分析客户需求、设计 Agent 解决方案、制定项目上线方案、协调研发与测试资源。\n"
        "4. 岗位任务 Task：角色在某项业务活动中具体承担的工作。\n"
        "5. 业务角色 Business Role：承担活动或任务的责任角色，例如“AI产品经理”“算法工程师”。\n"
        "   “具备保险业务理解”是能力要求，不是角色；“保险业务专家”才是角色。\n"
        "6. 业务对象 Business Object：流程活动操作、产生、传递或修改的信息与材料，例如“Agent方案”“评测数据集”。\n"
        "   工具、平台通常不属于业务对象。\n"
        "7. 业务参与者 Business Actor：承担业务角色的组织或团队，例如“AI产品团队”“算法团队”。\n\n"
        "## 分析步骤（按顺序完成，不输出中间结果）\n"
        "1. 提取职责事实：逐条读取 JD，提取动作、工作对象、参与角色、交付物、业务场景、生命周期阶段。先提取事实，不要立即总结岗位类型。\n"
        "2. 动作标准化：把 JD 中的招聘语言转换为标准业务活动。例如“负责客户需求洞察与对接”转换为："
        "访谈客户业务人员、收集客户需求、分析业务痛点、确认需求范围。不得只将原文重新排列。\n"
        "3. 活动归并为流程：按业务目标、输入输出和生命周期阶段分组。可参考 AI 产品生命周期（场景探索→需求分析→方案设计→数据准备→能力建设→效果评估→开发测试→上线→运营→优化→SOP沉淀），但不能机械套用。只输出 JD 中有证据支持的流程。\n"
        "4. 恢复流程顺序：根据活动之间的输入输出关系恢复端到端顺序。流程可能是线性、含判断节点或反馈闭环；“运营优化”通常会回到方案设计或数据建设，“评估不通过”通常返回开发或方案设计。\n"
        "5. 识别角色与责任：对每个活动判断主责角色、执行角色、协作角色。不要因为 JD 主语都是该岗位，就认为它亲自执行所有工作。例如“协调研发测试资源”表示协调推进，不代表其亲自开发或测试。\n"
        "6. 提取输入输出与业务对象：每个活动至少识别输入、输出、业务对象。JD 没有足够信息时可合理推断，但必须标记为 inferred。\n"
        "7. 识别信息缺口：列出无法从 JD 确定但会影响岗位匹配判断的事项，不得自行补全为事实。\n"
        "8. 质量自检：检查是否误写招聘流程、是否存在抽象名词活动、每个活动是否有证据或被标记推断、是否把 AI 产品经理误当成研发/测试执行者、流程是否有合理顺序、是否识别上线后运营闭环、是否把工具误认为流程、是否将岗位职责原文简单改写。\n\n"
        "## 推断规则\n"
        "- 每项主要结论标记 evidence_type：explicit（JD 明确表达）、inferred（合理推断）、unknown（无法确定）。\n"
        "- 只有满足以下至少两项时，才识别为独立业务活动：有明确业务目标、有独立输入或输出、可分配给具体角色、可以单独判断是否完成、在流程中具有明确前后依赖。\n"
        "- 角色与能力分离、任务与成果分离、管理动作与执行动作分离。例如“推动研发完成开发”不能改写成“开发 Agent”。\n"
        "- 保留 AI 产品特有活动：意图体系设计、实体及槽位设计、对话状态设计、Prompt 与上下文设计、Agent 工作流设计、工具调用设计、知识库设计、数据标注规则设计、评测集建设、AI 效果指标设计、Bad Case 分析、模型或策略迭代、人工接管与异常兜底、成本时延和风险监控。\n\n"
        "## 输出要求\n"
        "输出必须包含两部分：\n"
        "1. 简明的流程分析摘要（自然语言，放在 JSON 之前）。\n"
        "2. 严格符合以下结构的 JSON（字段名英文，值中文）：\n\n"
        "```json\n"
        f"{JD_V3_OUTPUT_SCHEMA}\n"
        "```\n\n"
        "## 数量与长度限制\n"
        "- jd_core_judgment ≤50 字。\n"
        "- key_requirements / key_risks 各最多 3 条，每条 ≤30 字。\n"
        "- business_context ≤30 字。\n"
        "- processes：4-8 个；每个 process.activities：2-6 个；每个 activity.tasks：1-5 个。\n"
        "- 每个 activity.inputs / outputs / business_objects：1-4 个。\n"
        "- roles：2-8 个；business_objects：3-10 个；uncertainties：0-4 个。\n"
        "- role_responsibility_summary 中每个列表最多 4 条，每条 ≤30 字。\n"
        "- overall_judgment.potential_boundary_risks 最多 4 条。\n\n"
        "## 禁止行为\n"
        "- 禁止把 JD 原文切片放进 key_requirements，例如“负责 AI Agent 产品规划与落地”。\n"
        "- 禁止 role_type 输出“产品型|工程型”这种多选形式。\n"
        "- 禁止 jd_core_judgment 写成“该岗位招聘 AI 产品经理，要求具备...”这种原文复述。\n"
        "- 禁止 activity_name 使用“负责”“参与”“推动”。\n"
        "- 禁止把工具/能力误认为流程或业务对象，例如“熟悉 Dify”是能力，“使用 Dify 配置 Agent 工作流”才是活动。\n"
        "- 禁止把招聘流程写成业务流程。\n\n"
        f"## 原始 JD 文本\n{jd_text}"
    )


def _build_business_flow_summary(job_analysis: Dict[str, Any]) -> Dict[str, Any]:
    business_flow = job_analysis.get("business_flow") or {}
    value_stream = business_flow.get("value_stream") or {}
    value_stream_name = value_stream.get("name", "") if isinstance(value_stream, dict) else str(value_stream)

    processes = []
    for p in business_flow.get("processes", []) or []:
        activities = []
        for a in (p.get("activities", []) or []):
            activities.append(
                {
                    "activity_name": a.get("activity_name", ""),
                    "tasks": (a.get("tasks", []) or [])[:5],
                    "key_business_objects": (a.get("business_objects", []) or [])[:4],
                    "accountable_role": a.get("accountable_role", ""),
                }
            )
        processes.append(
            {
                "process_name": p.get("process_name", ""),
                "activities": activities,
                "key_deliverables": (p.get("outputs", []) or [])[:4],
            }
        )

    summary = business_flow.get("role_responsibility_summary") or {}
    uncertainties = business_flow.get("uncertainties", []) or []

    return {
        "value_stream": value_stream_name,
        "end_to_end_flow": [
            {"sequence": e.get("sequence", i + 1), "process_name": e.get("process_name", "")}
            for i, e in enumerate(business_flow.get("end_to_end_flow", []) or [])
        ],
        "processes": processes,
        "role_responsibility_summary": {
            "primary_responsibilities": (summary.get("primary_responsibilities", []) or [])[:4],
            "coordination_responsibilities": (summary.get("coordination_responsibilities", []) or [])[:4],
            "likely_non_execution_responsibilities": (summary.get("likely_non_execution_responsibilities", []) or [])[:4],
        },
        "key_uncertainties": [
            {"question": u.get("question", ""), "related_process": u.get("related_process", "")}
            for u in uncertainties[:4]
        ],
    }


def build_candidate_v3_user_prompt(resume_text: str, job_analysis: Dict[str, Any]) -> str:
    job_context = {
        "role_type": job_analysis.get("role_type", ""),
        "key_requirements": job_analysis.get("key_requirements", []),
        "business_context": job_analysis.get("business_context", ""),
        "business_flow_summary": _build_business_flow_summary(job_analysis),
    }
    return (
        "请分析下面的简历原文，输出一个 JSON 对象。字段名必须用英文，字段值必须用中文。\n\n"
        "## 目的\n"
        "先识别候选人简历中的证据类型，再判断其与目标岗位的匹配度。\n\n"
        "## 核心概念（必须严格区分）\n"
        "1. 可建模能力 modeled_capability：简历中能识别具体任务，并能明确回答“处理什么输入 → 执行什么动作 → 产生什么输出”的能力。"
        "这是唯一可以直接证明岗位匹配度的证据类型，优先级最高。\n"
        "   例如原文“负责需求调研、业务抽象、流程设计、功能规划和上线推进”可拆分为：\n"
        "   - 需求调研与分析（输入：业务诉求/现有流程；动作：收集需求/分析问题；输出：结构化需求）\n"
        "   - 业务流程设计（输入：现状流程/业务规则；动作：梳理流程/设计目标流程；输出：目标流程）\n"
        "   - 项目交付推进（输入：项目计划/模块依赖/研发资源；动作：推进排期/协调资源；输出：上线版本）\n\n"
        "2. 客观背景事实 objective_fact：简历中客观发生、可验证，但不能直接还原为“输入—任务—输出”的事实。"
        "包括工作年限、任职公司、岗位名称、教育经历、毕业院校、专业、学历、行业经历、证书、奖项等。\n"
        "   这些事实可以辅助判断经历相关性、持续时间、行业熟悉度，但不能直接证明能力强弱。\n"
        "   例如：“5年产品经理经验” ≠ 具备高级产品能力。\n\n"
        "3. 主观能力声明 subjective_claim：候选人对自身能力、性格或工作风格的概括，但无法从文本中还原出明确任务和结果。\n"
        "   例如：抗压能力强、主动积极、执行力强、学习能力强、沟通能力优秀、责任心强、逻辑思维清晰。\n"
        "   这些属于工作风格/自我评价，不是具体任务能力，必须标注证据强度。\n\n"
        "4. 不完整任务能力 incomplete_capability：简历中有任务线索但信息不完整，无法确认输入、具体动作、输出、责任范围或结果。\n"
        "   例如“负责知识库建设”——不知道输入是业务知识还是 RAG 数据，也不清楚本人是主导还是参与。\n\n"
        "## 识别逻辑（对简历中每条信息依次判断）\n"
        "1. 能否识别具体任务？\n"
        "   ├── 能 → 能否识别输入、动作和输出？\n"
        "   │       ├── 能 → 可建模能力\n"
        "   │       └── 不能 → 不完整任务能力\n"
        "   └── 不能 → 是否为可验证的经历事实？\n"
        "           ├── 是 → 客观背景事实\n"
        "           └── 否 → 主观能力声明\n\n"
        "## 可建模能力判断规则\n"
        "满足以下任意三项，即可识别为 modeled_capability：\n"
        "- 有明确工作对象；\n"
        "- 有具体动作；\n"
        "- 有可识别的输入；\n"
        "- 有可识别的输出；\n"
        "- 有交付物；\n"
        "- 有结果；\n"
        "- 能定位到具体项目或经历。\n\n"
        "## 输出结构（只包含这些字段）\n"
        "```json\n"
        f"{CANDIDATE_V3_OUTPUT_SCHEMA}\n"
        "```\n\n"
        "## 数量与长度限制\n"
        "- candidate_profile / candidate_match_summary 各 ≤50 字。\n"
        "- match_points / gaps 各最多 3 条，每条 ≤30 字。\n"
        "- modeled_capabilities 最多 8 条；incomplete_capabilities 最多 6 条。\n"
        "- objective_facts 最多 8 条；subjective_claims 最多 6 条。\n"
        "- modeled_capabilities 每条字段：inputs/actions/outputs/outcomes 各 1-4 项；evidence_text ≤80 字；project_context ≤30 字。\n"
        "- incomplete_capabilities.unknown 至少列出 1-3 项未知信息。\n\n"
        "## 匹配推导规则\n"
        "- `match_points` 必须从 `candidate_evidence.modeled_capabilities` 中推导，优先引用能支撑岗位业务流程（business_flow）中某个 activity、business_object 或 role_responsibility 的证据。\n"
        "- `gaps` 必须对比岗位关键要求 / 业务流程，指出 `candidate_evidence.modeled_capabilities` 未覆盖的重要环节。\n"
        "- `candidate_match_summary` 应综合 `modeled_capabilities` 的覆盖度、`incomplete_capabilities` 的数量、`objective_facts` 的相关性以及 `subjective_claims` 的证据强度给出判断。\n"
        "- `role_mismatch_flag`：当目标岗位是 `产品型` 或 `混合型`，而候选人明显是工程/研究背景（如头衔是数据科学家、算法工程师、软件工程师，且内容以技术实现为主）时，必须置 `true`。\n\n"
        "## 禁止行为\n"
        "- 禁止把“5年产品经理经验”“毕业于清华”“高级产品经理”等客观背景事实直接写进 match_points 当作能力证据。\n"
        "- 禁止把“执行力强”“抗压能力强”等主观声明直接写进 match_points。\n"
        "- 禁止 match_points / gaps 写成无证据的概括句，例如“候选人具备扎实的AI Agent技术落地能力”。\n"
        "- 禁止 gaps 超过3条或每条超过30字。\n"
        "- 禁止 candidate_profile 写成“候选人工作认真负责”这种无信息量描述。\n\n"
        "## 目标岗位关键信息\n"
        f"```json\n{json.dumps(job_context, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## 原始简历文本\n{resume_text}"
    )


def build_final_v3_user_prompt(
    *,
    jd_text: str,
    resume_text: str,
    job_analysis: Dict[str, Any],
    candidate_analysis: Dict[str, Any],
) -> str:
    payload = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "job_analysis": job_analysis,
        "candidate_analysis": candidate_analysis,
    }
    return (
        "基于下面的 JD 分析、候选人分析和原始文本，给出最终投递建议。"
        "输出必须是合法 JSON，字段必须只有：recommendation, match_score, summary, strengths, risks, next_actions。\n\n"
        "## 目的\n"
        "给出候选人是否应该投递这个岗位的明确结论和下一步行动。\n\n"
        "## 输出结构\n"
        "{\n"
        '  "recommendation": "冲|可投|谨慎|避开",\n'
        '  "match_score": 75,\n'
        '  "summary": "30字以内结论",\n'
        '  "strengths": ["2-4条，引用真实证据"],\n'
        '  "risks": ["2-4条，引用真实证据"],\n'
        '  "next_actions": ["2-4条，具体可执行"]\n'
        "}\n\n"
        "## 字段定义与规则\n"
        "1. `recommendation` 与 `match_score` 必须同时存在，且严格对齐：\n"
        "   - 冲：80-100\n"
        "   - 可投：65-79\n"
        "   - 谨慎：50-64\n"
        "   - 避开：0-49\n"
        "2. `summary`：30字以内，一句话结论，必须基于证据。\n"
        "3. `strengths` / `risks`：2-4条，每条不超过40字，必须引用具体线索。\n"
        "   - strengths 优先引用 `candidate_analysis.candidate_evidence.modeled_capabilities` 与岗位 `business_flow` 的对应关系，"
        "即候选人在哪个流程/活动/交付物上有直接任务证据。\n"
        "   - risks 优先引用 `candidate_analysis.candidate_evidence.incomplete_capabilities`、"
        "`candidate_analysis.gaps` 和 `candidate_analysis.candidate_evidence.subjective_claims` 中证据不足的部分。\n"
        "4. `next_actions`：2-4条，每条不超过40字，具体可执行。应针对如何补全 `incomplete_capabilities` 或验证 `subjective_claims`。\n"
        "5. 禁止编造简历中没有的经历。\n\n"
        "## 禁止行为\n"
        "- 禁止 recommendation 与 match_score 不一致，例如 `recommendation=\"冲\"` 但 `match_score=62`。\n"
        "- 禁止 strengths/risks 写成无证据的概括句。\n"
        "- 禁止 next_actions 写成“继续优化简历”这种空泛建议。\n\n"
        "## 输入信息\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
