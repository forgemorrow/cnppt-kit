---
name: cnppt-kit-presenter
description: 为 DeepSeek / 通义千问 / Cursor / Claude Code / DeepSeek Harness 提供面向国内 WPS 与 Microsoft PowerPoint 的中文结构化 PPT 编排、防溢出体检与编译技能。当用户需要制作毕业答辩、科研组会、双创比赛路演或职场述职汇报 PPT 时调用。
---

# `cnppt-kit` 中文原生 PPT 生成规范

本 Skill 将大模型的职责聚焦在**信息提炼与叙事节奏**，而把**几何坐标、WPS 东亚字体绑定（`<a:ea>`）与防溢出计算**完全交给确定性编译器 `cnppt`。

## 1. 版面约束铁律（避免“Word 搬家”）

1. **主标题字数**：单页内容页标题控制在 **16–22 个等效全角汉字**以内（超过 22 字触发警告，超过 30 字阻断失败）。
2. **一页一结论（Action Title）**：每页必须写明 `takeaway:` 或观点式标题，拒绝只写“背景介绍”“实验数据”等干瘪名词。
3. **正文信息密度**：单页正文等效汉字尽量控制在 **180–220 字**以内；详细口述解释全部放入 `> 讲稿：...`。
4. **组件容量上限**：卡片布局（`cards` / `timeline`）最多 4 张；列表（`bullets`）最多 7 条；表格最多 6 列。
5. **跨端安全字体**：优先使用内置主题字体（`Microsoft YaHei`、`Source Han Sans SC`、`PingFang SC`、`SimHei`），不要指定需要翻墙加载的在线字体。

## 2. 标准产出流（先体检、再编译）

1. 按需求选择场景基调：
   - 科研与学位答辩：`theme: academic`（可参考 `cnppt scaffold defense`）
   - 双创大赛与商业路演：`theme: pitch`（可参考 `cnppt scaffold pitch`）
   - 职场述职与政务汇报：`theme: executive`（可参考 `cnppt scaffold report`）
2. 将 Markdown 幻灯片写入 `.md` 文件（每页以 `---` 分隔，合理搭配 `cover`、`toc`、`cards`、`metrics`、`timeline`、`table`、`two_column`、`closing`）。
3. 执行体检，确保无高危溢出：

```bash
cnppt lint outline.md --strict
```

4. 编译为 16:9 原生可编辑 `.pptx` 及零外网依赖 HTML 预演文件：

```bash
cnppt build outline.md -o output.pptx --html preview.html
```
