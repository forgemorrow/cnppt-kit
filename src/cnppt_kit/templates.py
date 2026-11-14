"""Original China-focused presentation narrative templates (defense, pitch, executive report)."""

from __future__ import annotations

SCENARIO_TEMPLATES: dict[str, dict[str, str]] = {
    "defense": {
        "name": "学术与毕业答辩 (Academic Defense)",
        "description": "覆盖研究背景、核心科学问题、方法框架、对照实验表与总结展望的答辩标准结构。",
        "content": """---
title: "面向复杂场景的多智能体可信推理方法研究"
subtitle: "硕士学位论文答辩汇报"
author: "答辩人：张同学"
organization: "计算机学院 · 智能系统实验室"
date: "2026 年 5 月"
theme: academic
---

# 面向复杂场景的多智能体可信推理方法研究
layout: cover
subtitle: 硕士学位论文答辩汇报

> 讲稿：各位评委老师好，下面我将汇报论文《面向复杂场景的多智能体可信推理方法研究》的核心工作。

---

# 汇报提纲
layout: toc
tag: 目录 Agenda

- 研究背景与核心科学问题
- 总体技术框架与创新机制
- 实验对比评测与消融分析
- 研究总结与下一步展望

> 讲稿：汇报分为背景问题、核心方法、实验评估与未来展望四个部分。

---

# 现有方案在真实落地中的三大瓶颈
layout: cards
tag: 01 · 研究背景
takeaway: 需要建立“推理验证—规则约束—可追溯评测”闭环架构

- **长程幻觉累积**：多轮工具调用后，单步小误差经上下文放大导致最终决策失真。
- **跨步状态漂移**：缺乏显式中间基线追踪，无法定量对比修改前后的收益与退化。
- **工程可复用性弱**：高度绑定特定海外商业闭源接口，本地离线和中文长文本适配不足。

> 讲稿：针对现有多智能体系统在长链路下幻觉累积和状态漂移的问题，我们提出了三层闭环机制。

---

# 关键定量评测结果对比
layout: table
tag: 03 · 实验验证
takeaway: 本文方法在保持零额外推理延迟开销的同时将综合准确率提升至 94.6%

| 方法对比 | 任务成功率 (%) | 越权阻断率 (%) | 平均单轮耗时 (ms) | 本地离线支持 |
| --- | --- | --- | --- | --- |
| Baseline 单体推理 | 78.4 | 61.0 | 840 | 是 |
| ReAct + 基础反思 | 85.2 | 74.5 | 1420 | 是 |
| 本文双阶段闭环架构 | 94.6 | 98.5 | 790 | 完全支持 |

> 讲稿：如表所示，双阶段闭环架构将任务成功率提升至 94.6%，同时把越权阻断率提高到 98.5%。

---

# 感谢各位老师批评指正
layout: closing
subtitle: 请各位评委提问 · Q&A

> 讲稿：以上是我的全部汇报，恳请各位老师批评指正。
""",
    },
    "pitch": {
        "name": "双创大赛与商业路演 (Innovation Pitch)",
        "description": "遵循“行业痛点—技术破局—量化指标—商业落地”黄金路演结构。",
        "content": """---
title: "智排云文档：面向本土办公生态的原生智能演示引擎"
subtitle: "创新创业大赛路演汇报"
author: "项目团队"
organization: "智创工坊"
date: "2026 年 11 月"
theme: pitch
---

# 智排云文档：本土原生智能演示引擎
layout: cover
subtitle: 让国产大模型一键输出在 WPS 中可逐字编辑的高质量演示文稿

> 讲稿：各位评委好，今天带来我们的项目：智排云文档。

---

# 为什么现有 AI PPT 仍难以直接交付使用？
layout: cards
tag: 01 · 行业痛点
takeaway: 市场缺的不是“再画一张图片”，而是可编辑、不出界、国产可用的原生文档引擎

- **截图化不可编辑**：整页生图导出后无法在 WPS 或 PowerPoint 里修改单个错别字与表格数字。
- **中文字宽与版式炸裂**：直接照搬英文模板，汉字超出文本框或字体跨电脑打开后错位。
- **私有化与合规成本高**：部分高星开源工具采用 AGPL 协议且强依赖海外 API，政企内网难以采购。

> 讲稿：用户把大模型生成的 PPT 拿回 WPS 打开后，往往面临改不动、字体乱和合规风险三大痛点。

---

# 核心技术指标与性能表现
layout: metrics
tag: 03 · 实测验证
takeaway: 全流程毫秒级离线编排，保障 100% 原生形状可编辑交付

- [指标] 100% | 原生可编辑率 | 所有文本框、卡片、表格均为标准 OOXML 矢量对象
- [指标] < 120ms | 单套编排耗时 | 纯本地确定性编译器，无需等待慢速云端渲染
- [指标] 0 | 外部字体断链 | 内置微软雅黑 / 思源黑体 / 苹方东亚字体 XML 节点

> 讲稿：实测表明，我们的引擎能在 120 毫秒内生成全矢量原生文档，实现 100% 可编辑交付。

---

# 产品商业化推进路线图
layout: timeline
tag: 04 · 落地规划
takeaway: 先切入高校科研与 Agent 开发者工具链，再扩展至政企私有化部署

- **V0.1 开源冷启动**：发布 MIT 开源引擎、中文排版体检器与 Agent Skill 生态适配。
- **V0.5 国产大模型接入**：无缝衔接 DeepSeek、通义千问与本地 Ollama 大纲流。
- **V1.0 行业模板矩阵**：联合高校实验室与职场团队沉淀多套垂直合规母版。
- **V2.0 企业私有部署**：提供零外网依赖的内网 CLI 与 API 文档网关。

> 讲稿：路线图分四阶段推进，以开源与 Agent 工具链先期验证口碑，逐步切入企业内网部署。

---

# 欢迎合作与技术交流
layout: closing
subtitle: 开源驱动创新 · 感谢聆听

> 讲稿：感谢各位评委与嘉宾的聆听。
""",
    },
    "report": {
        "name": "职场述职与国企工作汇报 (Executive Report)",
        "description": "面向季度/年度述职、项目验收与跨部门协同汇报的稳重结构。",
        "content": """---
title: "2026 年度研发效能与自动化合规建设述职报告"
subtitle: "工程效率与平台质量部工作总结"
author: "汇报人：平台研发组"
organization: "基础架构部"
date: "2026 年 11 月"
theme: executive
---

# 2026 年度研发效能与合规建设述职报告
layout: cover
subtitle: 聚焦质量门禁、国产化工具链与研发成本优化

> 讲稿：各位领导和同事好，下面做年度研发效能与合规建设述职汇报。

---

# 年度核心量化达成情况
layout: metrics
tag: 01 · 核心业绩
takeaway: 三大质量基线指标超额完成年初 OKR 目标

- [指标] 99.6% | 发布一次通过率 | 较去年同期提升 +8.4 个百分点
- [指标] 0 起 | 敏感凭据泄露事件 | 上线提交前安全审计门禁后实现零事故
- [指标] -38% | 跨部门汇报制图耗时 | 推广标准化 Markdown 自动化生成规范

> 讲稿：今年我们在稳定性、安全合规和办公协作提效方面均超额达成预期。

---

# 重点问题复盘与下一阶段改进措施
layout: two_column
tag: 02 · 复盘与计划
takeaway: 下季度将推动全团队文档模板化并打通统一流水线

- **当前短板复盘**：跨团队历史文档格式不统一，多项目汇报材料仍存在人工重复粘贴数据与字体不规范问题。
- **下阶段攻坚动作**：推广 Markdown/JSON 标准化大纲源，结合自动化排版检查工具与 CI 预览链路，实现一次编写多端发布。

> 讲稿：最后是存在的问题及下一季度重点整改措施。

---

# 汇报完毕 · 敬请指导
layout: closing
subtitle: 谢谢各位领导与同事

> 讲稿：我的汇报到此结束，请各位领导提出宝贵意见。
""",
    },
}


def list_scenarios() -> list[tuple[str, str, str]]:
    """Return list of `(key, display_name, description)` for available templates."""
    return [(k, v["name"], v["description"]) for k, v in SCENARIO_TEMPLATES.items()]


def scaffold_outline(scenario: str) -> str:
    """Return clean Markdown starter outline for the given domestic scenario."""
    key = (scenario or "defense").strip().lower()
    if key not in SCENARIO_TEMPLATES:
        available = ", ".join(sorted(SCENARIO_TEMPLATES))
        raise ValueError(f"Unknown scenario '{scenario}'. Available: {available}")
    return SCENARIO_TEMPLATES[key]["content"]
