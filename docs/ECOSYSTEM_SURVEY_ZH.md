# 2026 年高星开源 PPT 生态深度调研与国内选型指南

本文面向国内开发者、高校科研团队、职场与政企内网环境，系统梳理 GitHub 上当前极具代表性的高星 PPT / 演示文稿开源项目，重点从 **WPS/Office 原生编辑体验、中文字体兼容性、国产大模型协同成本、以及开源协议商用合规** 四个维度给出选型建议。

---

## 一、四大流派与高星项目横向对比

> 注：下表星标数、编程语言与协议均来自 GitHub 公开仓库元数据；本仓库仅做架构调研与链接索引，不复制任何第三方源代码。

| 技术流派 | 代表项目 | GitHub Stars | 语言 | 开源协议 | 输出形态 / 原生编辑 | 国内适应性与核心特点 |
| --- | --- | --- | --- | --- | --- | --- |
| **AI 原生文档引擎** | [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) | `76,730` | Python | **MIT** | 原生 `.pptx`（形状/图表/动画/讲稿配音） | 当前 GitHub 最高星 AI 生成原生 `.pptx` 项目，支持自定义 `.pptx` 母版 |
| | [`iOfficeAI/OfficeCLI`](https://github.com/iOfficeAI/OfficeCLI) | `33,276` | C# | **Apache-2.0** | 单二进制 CLI 直接读写 Word/Excel/PPT | 专门围绕 Coding Agent 无 Office 环境自动化操作 `.pptx` 打造 |
| | [`Anionex/banana-slides`](https://github.com/Anionex/banana-slides) | `15,998` | Python | ⚠️ **AGPL-3.0** | 多模态生图解析 + 导出可编辑 `.pptx` | 视觉上限极高、支持上传参考图，但依赖图像生成模型且为 AGPL-3.0 协议 |
| | [`genspark-ai/genoffice`](https://github.com/genspark-ai/genoffice) | `12,328` | TypeScript | **Apache-2.0** | 本地办公套件 + CLI & Agent Skill | 支持 BYOK 自带模型 Key 操作本地 `.docx/.xlsx/.pptx` |
| | [`presenton/presenton`](https://github.com/presenton/presenton) | `11,895` | TypeScript | **Apache-2.0** | 私有化部署 API / `.pptx` / PDF + MCP | 开源版 Gamma，支持 Ollama 本地模型及 Claude Code MCP 接入 |
| **Agent Skill 设计规范** | [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | `32,314` | JavaScript | **MIT** | 前端单页 HTML 幻灯片 | 发挥编码助手的前端排版强项生成网页 Deck，需额外转换才能进 WPS 编辑 |
| | [`op7418/guizang-ppt-skill`](https://github.com/op7418/guizang-ppt-skill) | `29,772` | HTML | ⚠️ **AGPL-3.0** | 杂志/瑞士网格风 HTML Deck + WebGL | 审美与提示词设计极其出色，但偏 HTML 展现且为 AGPL-3.0 协议 |
| | [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) | `29,456` | HTML | **MIT** | HTML / 可编辑 PPTX / 信息图（84 套样张） | 引入「外观账本与设计体检」机制，对中文语境审美非常友好 |
| | [`tw93/Kami`](https://github.com/tw93/Kami) | `12,543` | HTML | **MIT** | 布局规则引擎 + 导出 PDF / PNG / `.pptx` | 将版式规则固化成 Agent 可遵循的结构约束，减少排版错乱 |
| **代码 / Markdown 演示** | [`hakimel/reveal.js`](https://github.com/hakimel/reveal.js) | `72,572` | JavaScript | **MIT** | 纯 Web HTML5 演示 | Web 演示鼻祖，学术数学公式和代码展示强，但无原生 `.pptx` 编辑导出 |
| | [`slidevjs/slidev`](https://github.com/slidevjs/slidev) | `49,462` | TypeScript | **MIT** | Vite + Vue3 实时互动 PPT / PDF / `.pptx` | 程序员技术分享神器，注意其 PPTX 导出本质偏光栅截图而非精细可改形状 |
| | [`marp-team/marp`](https://github.com/marp-team/marp) | `12,743` | TypeScript | **MIT** | Markdown 直出 HTML / PDF / `.pptx` | 语法简洁、VS Code 生态成熟，适合快节奏写技术提纲 |
| **GUI 编辑器与底层库** | [`pipipi-pikachu/PPTist`](https://github.com/pipipi-pikachu/PPTist) | `9,496` | Vue | ⚠️ **AGPL-3.0** | 在线 PowerPoint 复刻编辑 + AIPPT JSON | 国内最早且最完善的 Web PPT 编辑器之一，AIPPT Schema 结构值得学习 |
| | [`gitbrent/PptxGenJS`](https://github.com/gitbrent/PptxGenJS) | `6,379` | TypeScript | **MIT** | 前端/Node 原生 OOXML 生成库 | JS 技术栈项目生成真正可编辑 `.pptx` 的事实底座 |
| | [`scanny/python-pptx`](https://github.com/scanny/python-pptx) | `3,585` | Python | **MIT** | Python 原生 OOXML `.pptx` 读写库 | 学术、数据处理、Agent 后端生成原生 `.pptx` 的稳定基石 |

---

## 二、面向国内场景的关键选型避坑（4 条一线总结）

1. **分清“看起来好看”和“交上去能改”**：
   国内高校论文送审、大创比赛提交、国企/职场部门汇总**绝大多数要求交付可在 WPS Office 或 MS PowerPoint 中直接修改文字和表格的 `.pptx`**。纯 HTML 方案或将网页整页截图拼进 PPT 的工具，一旦导师或领导让“改第三页表格里那个数”，就会面临返工。
2. **注意协议传染风险（MIT / Apache-2.0 vs AGPL-3.0）**：
   如果要把 PPT 工具二次封装进公司内部平台或 SaaS 服务，`Anionex/banana-slides`、`op7418/guizang-ppt-skill` 与 `pipipi-pikachu/PPTist` 采用 **AGPL-3.0**（网络提供服务也需开放修改源码）；企业内网与商业集成更建议以 **MIT**（`python-pptx`、`PptxGenJS`、`ppt-master`、`huashu-design`、`Kami`、`marp`）或 **Apache-2.0**（`OfficeCLI`、`presenton`、`genoffice`）为底座。
3. **中英混排宽字符与 WPS 东亚字体坑**：
   英文模板通常按单倍拉丁字符估算文本框高度，但一个汉字在视觉宽度上约等值于 `2` 个拉丁字符；且若 OOXML 中只设置 `font.name` 而未写入东亚字体节点 `<a:ea typeface="Microsoft YaHei"/>`，在部分 WPS / macOS / 统信 UOS 环境下中文会突然退化为默认宋体导致撑爆卡片。
4. **告别外网字体与强绑定海外闭源 API**：
   校园网与企业内网常无法稳定访问 Google Fonts 或海外商业多模态生图服务。可靠的本土工程架构应当采用**「结构化大纲 DSL（适配 DeepSeek / 通义千问 / Kimi / Ollama）+ 离线确定性本地编译 + 系统预装中文字体安全表」**。

---

## 三、我们从上述高星项目中提炼出的 6 大核心设计（并已在 `cnppt-kit` 实现）

1. **Slide IR 中间层与版式模板库解耦**（借鉴 `PPTist` Schema 与 `Kami` 约束思想）：模型只输出结构化 Markdown 或 JSON 语义节点（`cards` / `metrics` / `timeline` / `table`），几何坐标和边距留白由引擎统一计算。
2. **东亚字体 XML 原生注入**（基于 `python-pptx` 深入底层 `lxml` 节点）：对每个文本 Run 显式注入 `<a:latin>` 与 `<a:ea>`，保障 Windows、macOS、WPS 中文字体风格一致。
3. **CJK 排版密度与溢出体检（`cnppt lint`）**（致敬 `huashu-design` 设计体检理念）：利用 Unicode `east_asian_width` 对中英混排文本按 `2:1` 权重换算等效汉字字数，在生成前提前预警长标题折行、Word 式大段文本墙、超 4 卡拥挤布局和过宽表格。
4. **聚焦国内高频汇报母版**：原生内置**学术答辩**（`academic`）、**双创路演**（`pitch`）、**职场述职**（`executive`）三类大纲脚手架。
5. **零外网依赖离线预演**：一条命令同时导出可编辑 `.pptx` 与无任何 CDN 依赖的交互式单文件 HTML5 讲稿预演器。
6. **原生 Agent Skill（`skill/SKILL.md`）**：可直接挂载到 DeepSeek Harness、Cursor、Claude Code、Antigravity 等智能体平台，让国产或本地大模型按约束直接产出高质量合规文稿。
