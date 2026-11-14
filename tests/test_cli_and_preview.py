import json
import os
import subprocess
import sys
from pathlib import Path

from cnppt_kit.cli import main
from cnppt_kit.html_preview import build_html_preview
from cnppt_kit.parser import load_deck

ROOT = Path(__file__).resolve().parent.parent


def test_html_preview_is_self_contained_with_zero_external_cdn_links(tmp_path: Path):
    deck = load_deck(ROOT / "examples" / "pitch_outline.md")
    html_out = tmp_path / "preview.html"
    build_html_preview(deck, html_out)
    text = html_out.read_text(encoding="utf-8")
    assert "cnppt-kit 离线预演" in text
    assert "智排云文档" in text
    assert "http://" not in text
    assert "https://" not in text


def test_cli_scaffold_lint_json_and_build_workflow(tmp_path: Path, capsys):
    outline_path = tmp_path / "my_report.md"
    assert main(["scaffold", "report", "-o", str(outline_path)]) == 0
    assert outline_path.exists()

    assert main(["lint", str(outline_path), "--json", "--strict"]) == 0
    captured = capsys.readouterr()
    lint_payload = json.loads(captured.out[captured.out.index("{") :])
    assert lint_payload["status"] == "PASS"
    assert lint_payload["score"] == 100

    pptx_out = tmp_path / "deck.pptx"
    html_out = tmp_path / "deck.html"
    assert main(["build", str(outline_path), "-o", str(pptx_out), "--html", str(html_out), "--theme", "minimal"]) == 0
    assert pptx_out.exists()
    assert html_out.exists()


def test_cli_lint_strict_fails_on_overflow_title(tmp_path: Path):
    bad_md = tmp_path / "bad.md"
    bad_md.write_text(
        "---\ntitle: 测试\n---\n# 封面\n---\n# 这是一个为了触发严格模式下报错而设计得非常冗长极其繁琐超过三十个汉字的单页主标题文本\n\n- A\n",
        encoding="utf-8",
    )
    assert main(["lint", str(bad_md), "--strict"]) == 1


def test_cli_build_succeeds_under_cp1252_console_encoding(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONPATH"] = str(ROOT / "src")
    out_pptx = tmp_path / "cp1252.pptx"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "cnppt_kit.cli",
            "build",
            str(ROOT / "examples" / "defense_outline.md"),
            "-o",
            str(out_pptx),
        ],
        env=env,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", errors="replace")
    assert out_pptx.exists()
