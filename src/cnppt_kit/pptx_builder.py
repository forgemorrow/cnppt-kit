"""Native OOXML PowerPoint (.pptx) builder tuned for WPS Office & MS PowerPoint CJK fidelity."""

from __future__ import annotations

from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from .models import CardItem, DeckSpec, SlideSpec
from .themes import ThemeProfile, resolve_theme


def _rgb(hex_color: str) -> RGBColor:
    clean = hex_color.lstrip("#")
    return RGBColor(int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16))


def _style_run(
    run,
    *,
    ea_font: str,
    latin_font: str,
    size_pt: float,
    color_hex: str,
    bold: bool = False,
) -> None:
    """Set Latin + EastAsian (<a:ea>) OOXML font properties so Chinese never falls back unexpectedly."""
    run.font.name = latin_font
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = _rgb(color_hex)

    rPr = run._r.get_or_add_rPr()
    latin_el = rPr.find(qn("a:latin"))
    if latin_el is None:
        latin_el = etree.SubElement(rPr, qn("a:latin"))
    latin_el.set("typeface", latin_font)

    ea_el = rPr.find(qn("a:ea"))
    if ea_el is None:
        ea_el = etree.SubElement(rPr, qn("a:ea"))
    ea_el.set("typeface", ea_font)


def _set_shape_fill(shape, fill_hex: str, line_hex: str | None = None, line_pt: float = 0.75) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(fill_hex)
    if line_hex:
        shape.line.color.rgb = _rgb(line_hex)
        shape.line.width = Pt(line_pt)
    else:
        shape.line.fill.background()


def _set_bg(slide, color_hex: str) -> None:
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(color_hex)


def _add_textbox(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    *,
    ea_font: str,
    latin_font: str,
    size_pt: float,
    color_hex: str,
    bold: bool = False,
    align: PP_ALIGN = PP_ALIGN.LEFT,
) -> None:
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    _style_run(run, ea_font=ea_font, latin_font=latin_font, size_pt=size_pt, color_hex=color_hex, bold=bold)


def _add_header(slide, spec: SlideSpec, theme: ThemeProfile, ea_font: str, latin_font: str, total: int) -> float:
    """Render standardized content slide header & section pill, returning top Y offset for body."""
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    _set_shape_fill(top_bar, theme.accent_hex)

    if spec.section_tag:
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(0.32), Inches(2.6), Inches(0.34))
        _set_shape_fill(pill, theme.accent_hex)
        p = pill.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        pill.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = p.add_run()
        r.text = spec.section_tag
        _style_run(r, ea_font=ea_font, latin_font=latin_font, size_pt=10.5, color_hex="FFFFFF", bold=True)
        title_top = 0.72
    else:
        title_top = 0.36

    _add_textbox(
        slide,
        0.65,
        title_top,
        11.8,
        0.65,
        spec.title,
        ea_font=ea_font,
        latin_font=latin_font,
        size_pt=24,
        color_hex=theme.primary_hex,
        bold=True,
    )

    body_top = title_top + 0.68
    if spec.subtitle:
        _add_textbox(
            slide,
            0.65,
            body_top - 0.06,
            11.8,
            0.4,
            spec.subtitle,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=13.5,
            color_hex=theme.muted_hex,
        )
        body_top += 0.42

    divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(body_top), Inches(12.0), Inches(0.02))
    _set_shape_fill(divider, theme.border_hex)

    # Footer slide counter
    _add_textbox(
        slide,
        11.5,
        7.05,
        1.2,
        0.3,
        f"{spec.index} / {total}",
        ea_font=ea_font,
        latin_font=latin_font,
        size_pt=10,
        color_hex=theme.muted_hex,
        align=PP_ALIGN.RIGHT,
    )

    return body_top + 0.22


def _add_takeaway_strip(slide, text: str, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    if not text:
        return
    strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(6.35), Inches(11.95), Inches(0.55))
    _set_shape_fill(strip, theme.surface_hex, theme.accent_hex, line_pt=1.0)
    strip.text_frame.word_wrap = True
    strip.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = strip.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"核心结论：{text}" if not text.startswith(("核心结论", "结论", "总结")) else text
    _style_run(r, ea_font=ea_font, latin_font=latin_font, size_pt=12.5, color_hex=theme.primary_hex, bold=True)


def _render_cover(slide, spec: SlideSpec, deck: DeckSpec, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    _set_bg(slide, theme.cover_bg_hex)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(1.55), Inches(0.14), Inches(3.8))
    _set_shape_fill(bar, theme.accent_hex)

    _add_textbox(
        slide,
        1.25,
        1.65,
        10.8,
        1.8,
        spec.title,
        ea_font=ea_font,
        latin_font=latin_font,
        size_pt=36,
        color_hex=theme.cover_text_hex,
        bold=True,
    )
    subtitle_text = spec.subtitle or deck.subtitle
    if subtitle_text:
        _add_textbox(
            slide,
            1.25,
            3.55,
            10.5,
            0.95,
            subtitle_text,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=18,
            color_hex="CBD5E1",
        )

    meta_parts = [p for p in (deck.organization, deck.author, deck.date) if p]
    if meta_parts:
        _add_textbox(
            slide,
            1.25,
            5.05,
            10.5,
            0.5,
            "  |  ".join(meta_parts),
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=13.5,
            color_hex="94A3B8",
        )


def _render_cards(slide, cards: list[CardItem], body_top: float, has_takeaway: bool, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    avail_h = (6.15 if has_takeaway else 6.85) - body_top
    count = len(cards)
    if count <= 3:
        cols, rows = max(1, count), 1
    else:
        cols, rows = 2, (count + 1) // 2

    gap_x = 0.28
    gap_y = 0.24
    card_w = (12.0 - gap_x * (cols - 1)) / cols
    card_h = (avail_h - gap_y * (rows - 1)) / rows

    for idx, card in enumerate(cards):
        row = idx // cols
        col = idx % cols
        left = 0.65 + col * (card_w + gap_x)
        top = body_top + row * (card_h + gap_y)

        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(card_w), Inches(card_h))
        _set_shape_fill(box, theme.surface_hex, theme.border_hex, line_pt=1.0)

        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(card_w), Inches(0.08))
        _set_shape_fill(accent, theme.accent_hex)

        _add_textbox(
            slide,
            left + 0.16,
            top + 0.16,
            card_w - 0.32,
            0.48,
            card.title,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=15.5,
            color_hex=theme.primary_hex,
            bold=True,
        )
        _add_textbox(
            slide,
            left + 0.16,
            top + 0.66,
            card_w - 0.32,
            max(0.5, card_h - 0.8),
            card.body,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=13,
            color_hex=theme.text_hex,
        )


def _render_metrics(slide, spec: SlideSpec, body_top: float, has_takeaway: bool, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    metrics = spec.metrics
    cols = max(1, min(4, len(metrics)))
    gap = 0.26
    card_w = (12.0 - gap * (cols - 1)) / cols
    card_h = 2.35 if spec.bullets else ((6.1 if has_takeaway else 6.75) - body_top)

    for idx, m in enumerate(metrics[:4]):
        left = 0.65 + idx * (card_w + gap)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(body_top), Inches(card_w), Inches(card_h))
        _set_shape_fill(box, theme.surface_hex, theme.border_hex, line_pt=1.0)

        _add_textbox(
            slide,
            left + 0.18,
            body_top + 0.24,
            card_w - 0.36,
            0.78,
            m.value,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=30,
            color_hex=theme.accent_hex,
            bold=True,
        )
        _add_textbox(
            slide,
            left + 0.18,
            body_top + 1.05,
            card_w - 0.36,
            0.42,
            m.label,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=14.5,
            color_hex=theme.primary_hex,
            bold=True,
        )
        if m.detail:
            _add_textbox(
                slide,
                left + 0.18,
                body_top + 1.48,
                card_w - 0.36,
                max(0.4, card_h - 1.62),
                m.detail,
                ea_font=ea_font,
                latin_font=latin_font,
                size_pt=12,
                color_hex=theme.muted_hex,
            )

    if spec.bullets:
        _render_bullets_area(slide, spec.bullets, body_top + card_h + 0.28, has_takeaway, theme, ea_font, latin_font)


def _render_timeline(slide, cards: list[CardItem], body_top: float, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    count = max(1, min(4, len(cards)))
    track_y = body_top + 0.55
    track = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(track_y), Inches(11.1), Inches(0.05))
    _set_shape_fill(track, theme.border_hex)

    gap = 0.28
    col_w = (12.0 - gap * (count - 1)) / count
    for idx, card in enumerate(cards[:4]):
        left = 0.65 + idx * (col_w + gap)
        cx = left + col_w / 2 - 0.24
        node = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx), Inches(track_y - 0.22), Inches(0.48), Inches(0.48))
        _set_shape_fill(node, theme.accent_hex)
        p = node.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        node.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = p.add_run()
        r.text = f"{idx + 1:02d}"
        _style_run(r, ea_font=ea_font, latin_font=latin_font, size_pt=12, color_hex="FFFFFF", bold=True)

        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(track_y + 0.5), Inches(col_w), Inches(3.25))
        _set_shape_fill(box, theme.surface_hex, theme.border_hex, line_pt=1.0)
        _add_textbox(
            slide,
            left + 0.15,
            track_y + 0.68,
            col_w - 0.3,
            0.48,
            card.title,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=14.5,
            color_hex=theme.primary_hex,
            bold=True,
        )
        _add_textbox(
            slide,
            left + 0.15,
            track_y + 1.2,
            col_w - 0.3,
            2.35,
            card.body,
            ea_font=ea_font,
            latin_font=latin_font,
            size_pt=12.5,
            color_hex=theme.text_hex,
        )


def _render_table(slide, spec: SlideSpec, body_top: float, has_takeaway: bool, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    if not spec.table:
        return
    tbl_data = spec.table
    n_rows = 1 + len(tbl_data.rows)
    n_cols = max(1, len(tbl_data.headers))
    max_h = (6.1 if has_takeaway else 6.75) - body_top
    tbl_h = min(max_h, 0.55 + 0.48 * n_rows)

    graphic_frame = slide.shapes.add_table(n_rows, n_cols, Inches(0.65), Inches(body_top), Inches(12.0), Inches(tbl_h))
    table = graphic_frame.table

    for col_idx, header_text in enumerate(tbl_data.headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = _rgb(theme.primary_hex)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = header_text
        _style_run(r, ea_font=ea_font, latin_font=latin_font, size_pt=13, color_hex="FFFFFF", bold=True)

    for r_idx, row_vals in enumerate(tbl_data.rows, start=1):
        row_bg = "FFFFFF" if r_idx % 2 == 1 else "F1F5F9"
        for c_idx in range(n_cols):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _rgb(row_bg)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = row_vals[c_idx] if c_idx < len(row_vals) else ""
            _style_run(r, ea_font=ea_font, latin_font=latin_font, size_pt=12, color_hex=theme.text_hex)


def _render_bullets_area(slide, bullets: list[str], body_top: float, has_takeaway: bool, theme: ThemeProfile, ea_font: str, latin_font: str) -> None:
    box_h = max(1.2, (6.15 if has_takeaway else 6.8) - body_top)
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(body_top), Inches(12.0), Inches(box_h))
    _set_shape_fill(panel, theme.surface_hex, theme.border_hex, line_pt=1.0)

    tf = panel.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.32)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        run = p.add_run()
        run.text = f"▪  {item}"
        _style_run(run, ea_font=ea_font, latin_font=latin_font, size_pt=15, color_hex=theme.text_hex)


def build_pptx(deck: DeckSpec, output_path: str | Path) -> Path:
    """Compile DeckSpec Slide IR into an editable 16:9 WPS & MS PowerPoint `.pptx` file."""
    theme = resolve_theme(deck.theme)
    ea_font = deck.font_east_asia or theme.east_asia_font
    latin_font = deck.font_latin or theme.latin_font

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    total_slides = len(deck.slides)

    for spec in deck.slides:
        slide = prs.slides.add_slide(blank_layout)

        if spec.layout == "cover":
            _render_cover(slide, spec, deck, theme, ea_font, latin_font)
        elif spec.layout == "closing":
            _render_cover(slide, spec, deck, theme, ea_font, latin_font)
        else:
            _set_bg(slide, theme.bg_hex)
            body_top = _add_header(slide, spec, theme, ea_font, latin_font, total_slides)
            has_takeaway = bool(spec.takeaway)

            if spec.layout == "table" and spec.table:
                _render_table(slide, spec, body_top, has_takeaway, theme, ea_font, latin_font)
            elif spec.layout == "metrics" and spec.metrics:
                _render_metrics(slide, spec, body_top, has_takeaway, theme, ea_font, latin_font)
            elif spec.layout == "timeline" and spec.cards:
                _render_timeline(slide, spec.cards, body_top, theme, ea_font, latin_font)
            elif spec.cards:
                _render_cards(slide, spec.cards, body_top, has_takeaway, theme, ea_font, latin_font)
            elif spec.bullets:
                items = (
                    [f"{i + 1:02d}   {b}" for i, b in enumerate(spec.bullets)]
                    if spec.layout == "toc"
                    else spec.bullets
                )
                _render_bullets_area(slide, items, body_top, has_takeaway, theme, ea_font, latin_font)

            if spec.takeaway:
                _add_takeaway_strip(slide, spec.takeaway, theme, ea_font, latin_font)

        if spec.notes:
            notes_tf = slide.notes_slide.notes_text_frame
            notes_tf.text = spec.notes

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out
