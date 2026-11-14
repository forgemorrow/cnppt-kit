"""CJK-aware typography, layout density, and WPS font safety linter."""

from __future__ import annotations

import unicodedata

from .models import DeckSpec, LintFinding, LintReport, SlideSpec
from .themes import SAFE_CJK_FONTS


def cjk_visual_width(text: str) -> int:
    """Return display units where CJK full-width glyphs count as 2 units and ASCII counts as 1."""
    units = 0
    for ch in text:
        if ch.isspace():
            units += 1
        elif unicodedata.east_asian_width(ch) in ("W", "F", "A"):
            units += 2
        else:
            units += 1
    return units


def cjk_char_equivalent(text: str) -> float:
    """Express mixed Chinese/English string length in full-width Chinese character equivalents."""
    return cjk_visual_width(text) / 2.0


def _slide_body_cjk_eq(slide: SlideSpec) -> float:
    parts = [slide.subtitle, slide.takeaway, *slide.bullets]
    for card in slide.cards:
        parts.append(card.title)
        parts.append(card.body)
    for metric in slide.metrics:
        parts.append(metric.value)
        parts.append(metric.label)
        parts.append(metric.detail)
    if slide.table:
        parts.extend(slide.table.headers)
        for row in slide.table.rows:
            parts.extend(row)
    return sum(cjk_char_equivalent(p) for p in parts if p)


def lint_deck(deck: DeckSpec, *, strict_notes: bool = False) -> LintReport:
    """Audit Slide IR for CJK overflow, Word-style dense text walls, and unsafe WPS fonts."""
    findings: list[LintFinding] = []

    if deck.font_east_asia and deck.font_east_asia not in SAFE_CJK_FONTS:
        findings.append(
            LintFinding(
                rule_id="CJK-UNSAFE-FONT",
                severity="warning",
                slide_index=0,
                slide_title=deck.title,
                message=f"东亚字体 '{deck.font_east_asia}' 不在跨平台安全中文字体表内，WPS/PowerPoint 跨机打开可能回退错位。",
                suggestion="建议使用 Microsoft YaHei / Source Han Sans SC / PingFang SC / SimHei。",
            )
        )

    for slide in deck.slides:
        title_eq = cjk_char_equivalent(slide.title)
        if slide.layout not in ("cover", "closing") and title_eq > 30:
            findings.append(
                LintFinding(
                    rule_id="CJK-OVERFLOW-TITLE",
                    severity="error",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页主标题等效汉字达 {title_eq:.1f} 字（超过 30 字上限），极易折成两行遮挡版心。",
                    suggestion="将主标题提炼为 16–22 字以内的核心观点，补充信息下沉至 subtitle 或 takeaway。",
                )
            )
        elif slide.layout not in ("cover", "closing") and title_eq > 22:
            findings.append(
                LintFinding(
                    rule_id="CJK-OVERFLOW-TITLE",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页主标题偏长（等效 {title_eq:.1f} 个全角汉字，建议 <= 22 字）。",
                    suggestion="精简冗余修饰词，保留「主语 + 核心结果/动作」。",
                )
            )

        body_eq = _slide_body_cjk_eq(slide)
        if body_eq > 320:
            findings.append(
                LintFinding(
                    rule_id="CJK-DENSE-SLIDE",
                    severity="error",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页正文等效汉字达 {body_eq:.0f} 字（严重过密，Word 化严重）。",
                    suggestion="拆分为 2 页，或删减 40% 描述文本保留关键词卡片与核心数据。",
                )
            )
        elif body_eq > 220:
            findings.append(
                LintFinding(
                    rule_id="CJK-DENSE-SLIDE",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页内容偏多（等效 {body_eq:.0f} 个全角汉字，建议控制在 200 字内）。",
                    suggestion="将长句改写为「短标题 + 1 句要点」，把细节移入演讲备注。",
                )
            )

        if len(slide.cards) > 4:
            findings.append(
                LintFinding(
                    rule_id="CJK-TOO-MANY-CARDS",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页包含 {len(slide.cards)} 张卡片，16:9 横屏单页推荐不超过 4 张卡片。",
                    suggestion="合并次要维度为 3–4 个核心模块，或拆成多页展示。",
                )
            )

        if len(slide.metrics) > 4:
            findings.append(
                LintFinding(
                    rule_id="CJK-TOO-MANY-CARDS",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页并列 {len(slide.metrics)} 个指标卡，超过 4 个会削弱视觉聚焦度。",
                    suggestion="突出展示最关键的 3–4 个量化指标。",
                )
            )

        if len(slide.bullets) > 7 and slide.layout in ("bullets", "toc"):
            findings.append(
                LintFinding(
                    rule_id="CJK-TOO-MANY-BULLETS",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页列表条目多达 {len(slide.bullets)} 条，现场观众难以快速抓取焦点。",
                    suggestion="保留 3–5 条主干要点或转换为分栏卡片。",
                )
            )

        if slide.table and len(slide.table.headers) > 6:
            findings.append(
                LintFinding(
                    rule_id="TABLE-WIDE-COLUMNS",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页表格有 {len(slide.table.headers)} 列，PPT 投影容易因列宽过窄触发汉字竖排折行。",
                    suggestion="合并或裁剪为 4–5 列以保证单元格阅读舒适度。",
                )
            )

        if strict_notes and slide.layout not in ("cover", "toc", "closing") and not slide.notes.strip():
            findings.append(
                LintFinding(
                    rule_id="MISSING-SPEAKER-NOTES",
                    severity="warning",
                    slide_index=slide.index,
                    slide_title=slide.title,
                    message=f"第 {slide.index} 页未填写演讲逐字稿/备注（答辩或路演模式下建议配齐讲稿）。",
                    suggestion="使用 `> 讲稿：...` 为该页补充口头过渡与数据解释脚本。",
                )
            )

    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    penalty = errors * 22 + warnings * 8
    score = max(0, 100 - min(100, penalty))

    status = "FAIL" if errors > 0 else ("WARN" if warnings > 0 else "PASS")
    return LintReport(
        score=score,
        status=status,
        slide_count=len(deck.slides),
        error_count=errors,
        warning_count=warnings,
        findings=findings,
    )
