"""China-ready presentation compiler, CJK typography linter, and Agent Skill."""

from .html_preview import build_html_preview
from .linter import cjk_visual_width, lint_deck
from .models import CardItem, DeckSpec, LintFinding, LintReport, MetricItem, SlideSpec, TableData
from .parser import load_deck, parse_json_deck, parse_markdown_deck
from .pptx_builder import build_pptx
from .templates import list_scenarios, scaffold_outline
from .themes import THEMES, list_themes, resolve_theme

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "CardItem",
    "DeckSpec",
    "LintFinding",
    "LintReport",
    "MetricItem",
    "SlideSpec",
    "TableData",
    "THEMES",
    "build_html_preview",
    "build_pptx",
    "cjk_visual_width",
    "lint_deck",
    "list_scenarios",
    "list_themes",
    "load_deck",
    "parse_json_deck",
    "parse_markdown_deck",
    "resolve_theme",
    "scaffold_outline",
]
