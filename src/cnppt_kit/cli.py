"""Command-line interface for cnppt-kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .html_preview import build_html_preview
from .linter import lint_deck
from .models import LintReport
from .parser import load_deck
from .pptx_builder import build_pptx
from .templates import list_scenarios, scaffold_outline
from .themes import list_themes


def _print_lint_report(report: LintReport, *, as_json: bool) -> None:
    if as_json:
        payload = {
            "status": report.status,
            "score": report.score,
            "slide_count": report.slide_count,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "slide_index": f.slide_index,
                    "slide_title": f.slide_title,
                    "message": f.message,
                    "suggestion": f.suggestion,
                }
                for f in report.findings
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(
        f"[cnppt lint] status={report.status} score={report.score}/100 "
        f"slides={report.slide_count} errors={report.error_count} warnings={report.warning_count}"
    )
    for f in report.findings:
        print(f"  [{f.severity.upper():<7}] {f.rule_id} (Slide {f.slide_index}): {f.message}")
        print(f"            建议: {f.suggestion}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cnppt",
        description="面向国内办公/答辩/路演场景的原生可编辑 PPTX 编译器与中文排版体检工具",
    )
    parser.add_argument("-v", "--version", action="version", version=f"cnppt-kit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="将 Markdown / JSON 大纲编译为可编辑 .pptx（可选输出离线 HTML 预演）")
    p_build.add_argument("input", help="输入 .md 或 .json 文件路径")
    p_build.add_argument("-o", "--output", required=True, help="输出 .pptx 文件路径")
    p_build.add_argument("--theme", choices=["academic", "pitch", "executive", "minimal"], help="覆盖主题样式")
    p_build.add_argument("--html", help="同时导出零外网依赖的离线 HTML 预演页面")
    p_build.add_argument("--no-lint", action="store_true", help="跳过排版密度检查")
    p_build.add_argument("--strict", action="store_true", help="遇到排版错误或缺失讲稿时返回失败")

    p_lint = sub.add_parser("lint", help="对中文 PPT 大纲进行防溢出、信息密度与 WPS 字体安全体检")
    p_lint.add_argument("input", help="输入 .md 或 .json 文件路径")
    p_lint.add_argument("--json", action="store_true", help="以 JSON 格式输出体检结果")
    p_lint.add_argument("--strict", action="store_true", help="检查演讲备注是否齐全，若存在 error 返回非零状态码")

    p_scaf = sub.add_parser("scaffold", help="生成面向国内场景的标准 Markdown 大纲脚手架")
    p_scaf.add_argument("scenario", choices=["defense", "pitch", "report"], help="场景类型: defense|pitch|report")
    p_scaf.add_argument("-o", "--output", required=True, help="输出 .md 文件路径")

    sub.add_parser("templates", help="查看内置主题配色与国内三大汇报场景说明")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "templates":
        print("== 内置主题 (Themes) ==")
        for t in list_themes():
            print(f"  - {t.key:<10} {t.name_zh} (字体: {t.east_asia_font} / {t.latin_font})")
        print("\n== 内置场景脚手架 (Scenarios) ==")
        for key, name_zh, desc in list_scenarios():
            print(f"  - {key:<10} {name_zh}: {desc}")
        return 0

    if args.command == "scaffold":
        content = scaffold_outline(args.scenario)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"[cnppt scaffold] 已生成 '{args.scenario}' 模板大纲: {out_path}")
        return 0

    deck = load_deck(args.input)
    if args.command == "lint":
        report = lint_deck(deck, strict_notes=args.strict)
        _print_lint_report(report, as_json=args.json)
        return 1 if report.status == "FAIL" else 0

    if args.command == "build":
        if args.theme:
            deck.theme = args.theme
        if not args.no_lint:
            report = lint_deck(deck, strict_notes=args.strict)
            _print_lint_report(report, as_json=False)
            if args.strict and report.status == "FAIL":
                return 1
        out_pptx = build_pptx(deck, args.output)
        print(f"[cnppt build] 已生成原生可编辑 PPTX: {out_pptx} ({len(deck.slides)} 页, 主题={deck.theme})")
        if args.html:
            out_html = build_html_preview(deck, args.html)
            print(f"[cnppt build] 已生成离线 HTML 预演文件: {out_html}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
