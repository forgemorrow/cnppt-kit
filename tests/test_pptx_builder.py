from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

from cnppt_kit.parser import load_deck
from cnppt_kit.pptx_builder import build_pptx

ROOT = Path(__file__).resolve().parent.parent


def _collect_ea_fonts(prs: Presentation) -> set[str]:
    fonts: set[str] = set()
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        rPr = r._r.find(qn("a:rPr"))
                        if rPr is not None:
                            ea = rPr.find(qn("a:ea"))
                            if ea is not None and ea.get("typeface"):
                                fonts.add(ea.get("typeface"))
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                rPr = r._r.find(qn("a:rPr"))
                                if rPr is not None:
                                    ea = rPr.find(qn("a:ea"))
                                    if ea is not None and ea.get("typeface"):
                                        fonts.add(ea.get("typeface"))
    return fonts


def test_build_pptx_generates_editable_shapes_tables_notes_and_ea_fonts(tmp_path: Path):
    for fname in ("defense_outline.md", "pitch_outline.md", "report_outline.md"):
        deck = load_deck(ROOT / "examples" / fname)
        out_file = tmp_path / f"{Path(fname).stem}.pptx"
        build_pptx(deck, out_file)

        assert out_file.exists() and out_file.stat().st_size > 10_000
        reloaded = Presentation(str(out_file))
        assert len(reloaded.slides) == len(deck.slides)

        ea_fonts = _collect_ea_fonts(reloaded)
        assert "Microsoft YaHei" in ea_fonts

        notes_found = [s.notes_slide.notes_text_frame.text.strip() for s in reloaded.slides if s.has_notes_slide]
        assert any(len(n) > 0 for n in notes_found)


def test_defense_deck_contains_native_ooxml_table(tmp_path: Path):
    deck = load_deck(ROOT / "examples" / "defense_outline.md")
    out_file = tmp_path / "defense.pptx"
    build_pptx(deck, out_file)

    reloaded = Presentation(str(out_file))
    tables = [shape.table for slide in reloaded.slides for shape in slide.shapes if shape.has_table]
    assert len(tables) == 1
    assert tables[0].cell(0, 0).text == "方法对比"
    assert tables[0].cell(3, 1).text == "94.6"
