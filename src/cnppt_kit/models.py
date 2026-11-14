"""Typed intermediate representation (Slide IR) and lint models for cnppt-kit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SlideLayout = Literal[
    "cover",
    "toc",
    "cards",
    "two_column",
    "metrics",
    "timeline",
    "table",
    "bullets",
    "closing",
]

Severity = Literal["error", "warning", "info"]


@dataclass(slots=True)
class MetricItem:
    """Single KPI / highlight metric card (e.g. '99.2% | 准确率')."""

    value: str
    label: str
    detail: str = ""


@dataclass(slots=True)
class CardItem:
    """Structured content card used in cards/two_column/timeline layouts."""

    title: str
    body: str


@dataclass(slots=True)
class TableData:
    """Native OOXML table rows aligned cleanly for Chinese presentation clarity."""

    headers: list[str]
    rows: list[list[str]]


@dataclass(slots=True)
class SlideSpec:
    """Declarative representation of a single 16:9 presentation slide."""

    index: int
    title: str
    layout: SlideLayout = "bullets"
    subtitle: str = ""
    section_tag: str = ""
    takeaway: str = ""
    bullets: list[str] = field(default_factory=list)
    cards: list[CardItem] = field(default_factory=list)
    metrics: list[MetricItem] = field(default_factory=list)
    table: TableData | None = None
    notes: str = ""


@dataclass(slots=True)
class DeckSpec:
    """Top-level structured deck IR decoupled from PPTX/HTML rendering backends."""

    title: str
    subtitle: str = ""
    author: str = ""
    organization: str = ""
    date: str = ""
    theme: str = "academic"
    font_east_asia: str = ""
    font_latin: str = ""
    slides: list[SlideSpec] = field(default_factory=list)


@dataclass(slots=True)
class LintFinding:
    """Single typography, CJK overflow, or font safety diagnostic."""

    rule_id: str
    severity: Severity
    slide_index: int
    slide_title: str
    message: str
    suggestion: str


@dataclass(slots=True)
class LintReport:
    """Aggregated CJK typography & presentation density audit result."""

    score: int
    status: Literal["PASS", "WARN", "FAIL"]
    slide_count: int
    error_count: int
    warning_count: int
    findings: list[LintFinding] = field(default_factory=list)
