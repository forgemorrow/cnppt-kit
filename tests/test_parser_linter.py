import json
from pathlib import Path

from cnppt_kit.linter import cjk_char_equivalent, cjk_visual_width, lint_deck
from cnppt_kit.parser import parse_json_deck, parse_markdown_deck

ROOT = Path(__file__).resolve().parent.parent


def test_cjk_width_calculation_distinguishes_cjk_and_ascii():
    assert cjk_visual_width("abc") == 3
    assert cjk_visual_width("中文") == 4
    assert cjk_char_equivalent("中文AB") == 3.0


def test_markdown_parser_extracts_frontmatter_cards_tables_metrics_and_notes():
    md = """---
title: "测试标题"
author: "张三"
theme: pitch
---

# 测试封面
layout: cover
subtitle: 副标题

> 讲稿：开场白内容

---

# 核心数据
layout: metrics
tag: 第一部分

- [指标] 98.5% | 成功率 | 高于基线

> 讲稿：指标解说

---

# 方法对比
layout: table

| 方案 | 得分 |
| --- | --- |
| A | 80 |
| B | 95 |
"""
    deck = parse_markdown_deck(md)
    assert deck.title == "测试标题"
    assert deck.author == "张三"
    assert deck.theme == "pitch"
    assert len(deck.slides) == 3
    assert deck.slides[0].layout == "cover"
    assert "开场白" in deck.slides[0].notes
    assert deck.slides[1].metrics[0].value == "98.5%"
    assert deck.slides[2].table is not None
    assert deck.slides[2].table.headers == ["方案", "得分"]


def test_json_parser_round_trip():
    payload = {
        "title": "JSON 演示文稿",
        "theme": "minimal",
        "slides": [
            {"title": "封面", "layout": "cover", "subtitle": "测试副标题"},
            {
                "title": "时间路线图",
                "layout": "timeline",
                "cards": [
                    {"title": "阶段一", "body": "调研与原型"},
                    {"title": "阶段二", "body": "全面上线"},
                ],
                "notes": "阶段演示备注",
            },
        ],
    }
    deck = parse_json_deck(json.dumps(payload, ensure_ascii=False))
    assert deck.theme == "minimal"
    assert len(deck.slides) == 2
    assert deck.slides[1].layout == "timeline"
    assert deck.slides[1].cards[1].title == "阶段二"


def test_linter_flags_cjk_title_overflow_dense_text_and_unsafe_font():
    md = """---
title: "过度拥挤示例"
font_east_asia: NonExistentWebFont
---

# 封面

---

# 这个主标题特意写得超级啰嗦并且长度远远超过了投影安全可读单行上限三十个汉字之多
layout: cards

- **卡1**：内容A
- **卡2**：内容B
- **卡3**：内容C
- **卡4**：内容D
- **卡5**：内容E
"""
    deck = parse_markdown_deck(md)
    report = lint_deck(deck, strict_notes=True)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.status == "FAIL"
    assert "CJK-UNSAFE-FONT" in rule_ids
    assert "CJK-OVERFLOW-TITLE" in rule_ids
    assert "CJK-TOO-MANY-CARDS" in rule_ids
    assert "MISSING-SPEAKER-NOTES" in rule_ids


def test_all_three_domestic_examples_pass_lint_at_100():
    for fname in ("defense_outline.md", "pitch_outline.md", "report_outline.md"):
        deck = parse_markdown_deck((ROOT / "examples" / fname).read_text(encoding="utf-8"))
        report = lint_deck(deck, strict_notes=True)
        assert report.status == "PASS", f"{fname} unexpected lint findings: {report.findings}"
        assert report.score == 100
