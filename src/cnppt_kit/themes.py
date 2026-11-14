"""Domestic WPS/PowerPoint compatible visual themes and CJK font fallback profiles."""

from __future__ import annotations

from dataclasses import dataclass

# Curated pre-installed Chinese fonts across Windows, macOS, and domestic Linux desktops.
# Avoids broken third-party Google Fonts dependencies on offline/intranet environments.
SAFE_CJK_FONTS: frozenset[str] = frozenset(
    {
        "Microsoft YaHei",
        "微软雅黑",
        "SimHei",
        "黑体",
        "SimSun",
        "宋体",
        "KaiTi",
        "楷体",
        "FangSong",
        "仿宋",
        "DengXian",
        "等线",
        "PingFang SC",
        "苹方-简",
        "Hiragino Sans GB",
        "Source Han Sans SC",
        "思源黑体",
        "Noto Sans CJK SC",
        "Noto Serif CJK SC",
        "WenQuanYi Micro Hei",
    }
)

DEFAULT_LATIN_FALLBACK = "Calibri"


@dataclass(frozen=True, slots=True)
class ThemeProfile:
    """Color palette and typography defaults tuned for Chinese readability."""

    key: str
    name_zh: str
    description: str
    east_asia_font: str
    latin_font: str
    bg_hex: str
    surface_hex: str
    cover_bg_hex: str
    primary_hex: str
    accent_hex: str
    text_hex: str
    muted_hex: str
    border_hex: str
    cover_text_hex: str


THEMES: dict[str, ThemeProfile] = {
    "academic": ThemeProfile(
        key="academic",
        name_zh="学术答辩蓝 (Academic Defense)",
        description="High-contrast off-white canvas with deep academic navy & steel blue accents for thesis defenses and lab meetings.",
        east_asia_font="Microsoft YaHei",
        latin_font="Calibri",
        bg_hex="F8FAFC",
        surface_hex="FFFFFF",
        cover_bg_hex="0F294A",
        primary_hex="1E3A5F",
        accent_hex="2563EB",
        text_hex="0F172A",
        muted_hex="475569",
        border_hex="CBD5E1",
        cover_text_hex="FFFFFF",
    ),
    "pitch": ThemeProfile(
        key="pitch",
        name_zh="双创路演橙 (Innovation Pitch)",
        description="Dark slate hero cover paired with energetic coral-orange accents suited for innovation contests and startup roadshows.",
        east_asia_font="Microsoft YaHei",
        latin_font="Segoe UI",
        bg_hex="FFFFFF",
        surface_hex="F8FAFC",
        cover_bg_hex="0F172A",
        primary_hex="0F172A",
        accent_hex="EA580C",
        text_hex="1E293B",
        muted_hex="64748B",
        border_hex="E2E8F0",
        cover_text_hex="FFFFFF",
    ),
    "executive": ThemeProfile(
        key="executive",
        name_zh="政务述职红/金 (Executive & Gov Report)",
        description="Formal crimson-navy executive hierarchy tailored for SOE reviews, annual summaries, and project acceptance boards.",
        east_asia_font="Microsoft YaHei",
        latin_font="Arial",
        bg_hex="FFFFFF",
        surface_hex="FEF2F2",
        cover_bg_hex="881337",
        primary_hex="991B1B",
        accent_hex="B45309",
        text_hex="111827",
        muted_hex="4B5563",
        border_hex="E5E7EB",
        cover_text_hex="FFFFFF",
    ),
    "minimal": ThemeProfile(
        key="minimal",
        name_zh="极简科技灰青 (Swiss Minimal)",
        description="Ultra-clean neutral canvas with teal-indigo hierarchy for engineering reviews and architecture briefings.",
        east_asia_font="Source Han Sans SC",
        latin_font="Inter",
        bg_hex="F9FAFB",
        surface_hex="FFFFFF",
        cover_bg_hex="111827",
        primary_hex="1F2937",
        accent_hex="0D9488",
        text_hex="111827",
        muted_hex="6B7280",
        border_hex="D1D5DB",
        cover_text_hex="FFFFFF",
    ),
}


def resolve_theme(theme_key: str) -> ThemeProfile:
    """Look up a built-in theme by key, falling back cleanly or raising ValueError."""
    normalized = (theme_key or "academic").strip().lower()
    if normalized not in THEMES:
        supported = ", ".join(sorted(THEMES))
        raise ValueError(f"Unknown theme '{theme_key}'. Supported themes: {supported}")
    return THEMES[normalized]


def list_themes() -> list[ThemeProfile]:
    """Return all registered domestic presentation themes."""
    return [THEMES[k] for k in ("academic", "pitch", "executive", "minimal")]
