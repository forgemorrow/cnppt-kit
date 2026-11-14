"""Ground-truth benchmark for CJK typography linting and PPTX compilation latency."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cnppt_kit.linter import lint_deck  # noqa: E402
from cnppt_kit.parser import load_deck, parse_markdown_deck  # noqa: E402
from cnppt_kit.pptx_builder import build_pptx  # noqa: E402

EVAL_CASES = [
    # 6 positive defect cases (expected specific rule triggered)
    {
        "id": "pos-overflow-title",
        "expected_positive": True,
        "expected_rule": "CJK-OVERFLOW-TITLE",
        "md": "---\ntitle: 测试\n---\n# 测试封面\n---\n# 这是一个刻意写得非常冗长严重超出单页投影横向宽度容忍范围三十多个字的主标题示例\n\n- 要点一\n",
    },
    {
        "id": "pos-dense-slide",
        "expected_positive": True,
        "expected_rule": "CJK-DENSE-SLIDE",
        "md": "---\ntitle: 测试\n---\n# 测试\n---\n# 正文过密测试\n\n"
        + "\n".join(f"- 这是一段第 {i} 条用于验证单页等效汉字超过两百二十字阈值时的过密警告检测文本内容说明。" for i in range(1, 10)),
    },
    {
        "id": "pos-too-many-cards",
        "expected_positive": True,
        "expected_rule": "CJK-TOO-MANY-CARDS",
        "md": "---\ntitle: 测试\n---\n# 测试\n---\n# 过多卡片对比\nlayout: cards\n\n"
        + "\n".join(f"- **模块{i}**：卡片说明" for i in range(1, 6)),
    },
    {
        "id": "pos-wide-table",
        "expected_positive": True,
        "expected_rule": "TABLE-WIDE-COLUMNS",
        "md": "---\ntitle: 测试\n---\n# 测试\n---\n# 宽表格超限\nlayout: table\n\n| C1 | C2 | C3 | C4 | C5 | C6 | C7 |\n| --- | --- | --- | --- | --- | --- | --- |\n| 1 | 2 | 3 | 4 | 5 | 6 | 7 |\n",
    },
    {
        "id": "pos-unsafe-font",
        "expected_positive": True,
        "expected_rule": "CJK-UNSAFE-FONT",
        "md": "---\ntitle: 测试\nfont_east_asia: RemoteCloudCustomFont2099\n---\n# 测试\n\n副标题\n",
    },
    {
        "id": "pos-too-many-bullets",
        "expected_positive": True,
        "expected_rule": "CJK-TOO-MANY-BULLETS",
        "md": "---\ntitle: 测试\n---\n# 测试\n---\n# 条目过多列表\nlayout: bullets\n\n"
        + "\n".join(f"- 列表要点 {i}" for i in range(1, 9)),
    },
    # 6 negative clean cases (expected zero findings)
    {
        "id": "neg-clean-cards",
        "expected_positive": False,
        "md": "---\ntitle: 测试\n---\n# 清晰封面\n---\n# 三栏核心架构对比\nlayout: cards\n\n- **输入层**：接收 Markdown。\n- **校验层**：核算字宽。\n- **输出层**：编译 PPTX。\n",
    },
    {
        "id": "neg-clean-table",
        "expected_positive": False,
        "md": "---\ntitle: 测试\n---\n# 清晰封面\n---\n# 实验结果对比\nlayout: table\n\n| 模型 | 准确率 | 延迟 |\n| --- | --- | --- |\n| Baseline | 81.2% | 420ms |\n| Ours | 94.6% | 310ms |\n",
    },
    {
        "id": "neg-clean-metrics",
        "expected_positive": False,
        "md": "---\ntitle: 测试\n---\n# 清晰封面\n---\n# 关键达成指标\nlayout: metrics\n\n- [指标] 99.6% | 通过率 | 稳步提升\n- [指标] 15ms | 耗时 | 毫秒级\n- [指标] 0 | 断链 | 全离线\n",
    },
    {
        "id": "neg-defense-example",
        "expected_positive": False,
        "path": ROOT / "examples" / "defense_outline.md",
    },
    {
        "id": "neg-pitch-example",
        "expected_positive": False,
        "path": ROOT / "examples" / "pitch_outline.md",
    },
    {
        "id": "neg-report-example",
        "expected_positive": False,
        "path": ROOT / "examples" / "report_outline.md",
    },
]


def main() -> int:
    t0 = time.perf_counter()
    tp = fp = tn = fn = 0

    for case in EVAL_CASES:
        deck = load_deck(case["path"]) if "path" in case else parse_markdown_deck(case["md"])
        report = lint_deck(deck, strict_notes=False)
        rules = {f.rule_id for f in report.findings}
        if case["expected_positive"]:
            if case["expected_rule"] in rules:
                tp += 1
            else:
                fn += 1
        else:
            if not report.findings:
                tn += 1
            else:
                fp += 1

    lint_ms = (time.perf_counter() - t0) * 1000.0

    build_times_ms: list[float] = []
    with tempfile.TemporaryDirectory() as tmp:
        for example_name in ("defense_outline.md", "pitch_outline.md", "report_outline.md"):
            deck = load_deck(ROOT / "examples" / example_name)
            b0 = time.perf_counter()
            build_pptx(deck, Path(tmp) / f"{example_name}.pptx")
            build_times_ms.append((time.perf_counter() - b0) * 1000.0)

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 1.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    avg_build_ms = sum(build_times_ms) / len(build_times_ms)

    result = {
        "cases": len(EVAL_CASES),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision_pct": round(precision * 100, 1),
        "recall_pct": round(recall * 100, 1),
        "f1_pct": round(f1 * 100, 1),
        "fpr_pct": round(fpr * 100, 1),
        "lint_total_ms": round(lint_ms, 2),
        "avg_pptx_compile_ms": round(avg_build_ms, 2),
    }

    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"[cnppt-kit benchmark] cases={result['cases']} TP={tp} TN={tn} FP={fp} FN={fn} "
            f"Precision={result['precision_pct']}% Recall={result['recall_pct']}% F1={result['f1_pct']}% FPR={result['fpr_pct']}%"
        )
        print(f"  Avg PPTX OOXML compile latency (3 domestic demo decks): {result['avg_pptx_compile_ms']}ms")

    return 0 if (fp == 0 and fn == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
