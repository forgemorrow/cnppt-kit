"""Markdown Deck DSL & JSON IR parser decoupled from rendering backends."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import CardItem, DeckSpec, MetricItem, SlideLayout, SlideSpec, TableData

VALID_LAYOUTS: frozenset[str] = frozenset(
    {
        "cover",
        "toc",
        "cards",
        "two_column",
        "metrics",
        "timeline",
        "table",
        "bullets",
        "closing",
    }
)

COMMENT_META_RE = re.compile(r"^<!--\s*([a-zA-Z0-9_-]+)\s*:\s*(.+?)\s*-->$")
BARE_META_RE = re.compile(r"^(layout|tag|subtitle|takeaway)\s*[:：]\s*(.+)$", re.IGNORECASE)
CARD_BULLET_RE = re.compile(r"^[-*]\s+\*\*(.+?)\*\*\s*[:：]\s*(.+)$")
METRIC_RE = re.compile(r"^(?:[-*]\s*)?\[(?:指标|metric)\]\s*(.+)$", re.IGNORECASE)


def _strip_quotes(val: str) -> str:
    s = val.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    normalized = text.replace("\r\n", "\n").lstrip("\ufeff")
    lines = normalized.split("\n")
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                meta: dict[str, str] = {}
                for raw in lines[1:idx]:
                    if ":" not in raw or raw.strip().startswith("#"):
                        continue
                    k, v = raw.split(":", 1)
                    meta[k.strip().lower()] = _strip_quotes(v)
                body = "\n".join(lines[idx + 1 :])
                return meta, body
    return {}, normalized


def _infer_layout(
    idx: int,
    declared: str,
    table: TableData | None,
    metrics: list[MetricItem],
    cards: list[CardItem],
    bullets: list[str],
    title: str,
) -> SlideLayout:
    if declared in VALID_LAYOUTS:
        return declared  # type: ignore[return-value]
    if idx == 1 and not table and not metrics and not cards and len(bullets) <= 2:
        return "cover"
    if any(k in title.lower() for k in ("目录", "contents", "agenda", "提纲")):
        return "toc"
    if any(k in title.lower() for k in ("感谢", "谢谢", "q&a", "致谢", "thank")):
        return "closing"
    if table is not None:
        return "table"
    if metrics:
        return "metrics"
    if cards:
        return "two_column" if len(cards) == 2 else "cards"
    return "bullets"


def _parse_table_lines(table_lines: list[str]) -> TableData | None:
    if len(table_lines) < 2:
        return None
    raw_rows: list[list[str]] = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        raw_rows.append(cells)
    if len(raw_rows) < 2:
        return None
    headers = raw_rows[0]
    width = len(headers)
    rows: list[list[str]] = []
    for r in raw_rows[1:]:
        padded = (r + [""] * width)[:width]
        rows.append(padded)
    return TableData(headers=headers, rows=rows)


def parse_markdown_deck(text: str) -> DeckSpec:
    """Parse Chinese-friendly Markdown slides separated by `---` into DeckSpec."""
    meta, body = _split_frontmatter(text)
    raw_chunks = re.split(r"(?m)^\s*---\s*$", body)
    chunks = [c.strip() for c in raw_chunks if c.strip()]

    slides: list[SlideSpec] = []
    for raw_chunk in chunks:
        lines = raw_chunk.split("\n")
        slide_index = len(slides) + 1
        title = ""
        declared_layout = ""
        subtitle = ""
        section_tag = ""
        takeaway = ""
        bullets: list[str] = []
        cards: list[CardItem] = []
        metrics: list[MetricItem] = []
        table_buf: list[str] = []
        table_data: TableData | None = None
        note_lines: list[str] = []

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                if table_buf and table_data is None:
                    table_data = _parse_table_lines(table_buf)
                    table_buf = []
                continue

            if stripped.startswith("|") and stripped.endswith("|"):
                table_buf.append(stripped)
                continue
            elif table_buf and table_data is None:
                table_data = _parse_table_lines(table_buf)
                table_buf = []

            cm = COMMENT_META_RE.match(stripped)
            if cm:
                key, val = cm.group(1).strip().lower(), cm.group(2).strip()
                if key == "layout":
                    declared_layout = val.lower()
                elif key == "tag":
                    section_tag = val
                elif key == "subtitle":
                    subtitle = val
                elif key == "takeaway":
                    takeaway = val
                continue

            if stripped.startswith("#"):
                heading = stripped.lstrip("#").strip()
                if not title:
                    title = heading
                elif not subtitle:
                    subtitle = heading
                continue

            bm = BARE_META_RE.match(stripped)
            if bm and not bullets and not cards and not metrics:
                key, val = bm.group(1).lower(), bm.group(2).strip()
                if key == "layout":
                    declared_layout = val.lower()
                elif key == "tag":
                    section_tag = val
                elif key == "subtitle":
                    subtitle = val
                elif key == "takeaway":
                    takeaway = val
                continue

            if stripped.startswith(">"):
                note_body = stripped.lstrip(">").strip()
                note_body = re.sub(r"^(?:演讲备注|讲稿|备注|notes?)\s*[:：]\s*", "", note_body, flags=re.IGNORECASE)
                if note_body:
                    note_lines.append(note_body)
                continue

            mm = METRIC_RE.match(stripped)
            if mm:
                parts = [p.strip() for p in mm.group(1).split("|")]
                metrics.append(
                    MetricItem(
                        value=parts[0] if len(parts) > 0 else "",
                        label=parts[1] if len(parts) > 1 else "",
                        detail=parts[2] if len(parts) > 2 else "",
                    )
                )
                continue

            card_match = CARD_BULLET_RE.match(stripped)
            if card_match:
                cards.append(CardItem(title=card_match.group(1).strip(), body=card_match.group(2).strip()))
                continue

            bullet_match = re.match(r"^(?:[-*]|\d+[.)、])\s+(.+)$", stripped)
            if bullet_match:
                bullets.append(bullet_match.group(1).strip())
                continue

            # Plain narrative sentence on cover or summary
            if slide_index == 1 and not subtitle:
                subtitle = stripped
            elif not takeaway and len(stripped) <= 90 and (stripped.startswith("结论") or stripped.startswith("总结")):
                takeaway = stripped
            else:
                bullets.append(stripped)

        if table_buf and table_data is None:
            table_data = _parse_table_lines(table_buf)

        if not title:
            title = meta.get("title", f"第 {slide_index} 页")

        layout = _infer_layout(
            slide_index,
            declared_layout,
            table_data,
            metrics,
            cards,
            bullets,
            title,
        )

        slides.append(
            SlideSpec(
                index=slide_index,
                title=title,
                layout=layout,
                subtitle=subtitle,
                section_tag=section_tag,
                takeaway=takeaway,
                bullets=bullets,
                cards=cards,
                metrics=metrics,
                table=table_data,
                notes="\n".join(note_lines),
            )
        )

    deck_title = meta.get("title") or (slides[0].title if slides else "未命名演示文稿")
    return DeckSpec(
        title=deck_title,
        subtitle=meta.get("subtitle", slides[0].subtitle if slides and slides[0].layout == "cover" else ""),
        author=meta.get("author", ""),
        organization=meta.get("organization", ""),
        date=meta.get("date", ""),
        theme=meta.get("theme", "academic"),
        font_east_asia=meta.get("font_east_asia", ""),
        font_latin=meta.get("font_latin", ""),
        slides=slides,
    )


def parse_json_deck(raw_json: str) -> DeckSpec:
    """Parse structured JSON Slide IR payload into DeckSpec cleanly."""
    payload = json.loads(raw_json)
    if not isinstance(payload, dict):
        raise ValueError("JSON deck root must be an object.")

    raw_slides = payload.get("slides", [])
    if not isinstance(raw_slides, list):
        raise ValueError("'slides' must be a list of slide definitions.")

    slides: list[SlideSpec] = []
    for idx, item in enumerate(raw_slides, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Slide #{idx} must be a JSON object.")
        cards = [
            CardItem(title=str(c.get("title", "")), body=str(c.get("body", "")))
            for c in item.get("cards", [])
            if isinstance(c, dict)
        ]
        metrics = [
            MetricItem(
                value=str(m.get("value", "")),
                label=str(m.get("label", "")),
                detail=str(m.get("detail", "")),
            )
            for m in item.get("metrics", [])
            if isinstance(m, dict)
        ]
        raw_table = item.get("table")
        table_data: TableData | None = None
        if isinstance(raw_table, dict):
            table_data = TableData(
                headers=[str(h) for h in raw_table.get("headers", [])],
                rows=[[str(cell) for cell in row] for row in raw_table.get("rows", [])],
            )
        declared = str(item.get("layout", "")).lower()
        bullets = [str(b) for b in item.get("bullets", [])]
        title = str(item.get("title", f"第 {idx} 页"))
        layout = _infer_layout(idx, declared, table_data, metrics, cards, bullets, title)
        slides.append(
            SlideSpec(
                index=idx,
                title=title,
                layout=layout,
                subtitle=str(item.get("subtitle", "")),
                section_tag=str(item.get("section_tag", "")),
                takeaway=str(item.get("takeaway", "")),
                bullets=bullets,
                cards=cards,
                metrics=metrics,
                table=table_data,
                notes=str(item.get("notes", "")),
            )
        )

    return DeckSpec(
        title=str(payload.get("title", slides[0].title if slides else "未命名演示文稿")),
        subtitle=str(payload.get("subtitle", "")),
        author=str(payload.get("author", "")),
        organization=str(payload.get("organization", "")),
        date=str(payload.get("date", "")),
        theme=str(payload.get("theme", "academic")),
        font_east_asia=str(payload.get("font_east_asia", "")),
        font_latin=str(payload.get("font_latin", "")),
        slides=slides,
    )


def load_deck(path: str | Path) -> DeckSpec:
    """Load and parse a `.md` or `.json` presentation outline file."""
    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() == ".json":
        return parse_json_deck(content)
    return parse_markdown_deck(content)
