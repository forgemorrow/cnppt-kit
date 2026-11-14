"""Zero-CDN standalone HTML5 slide previewer and speaker-notes viewer."""

from __future__ import annotations

import html
import json
from pathlib import Path

from .models import DeckSpec
from .themes import resolve_theme


def build_html_preview(deck: DeckSpec, output_path: str | Path) -> Path:
    """Export a self-contained offline HTML presentation deck (no external CDN fonts/scripts)."""
    theme = resolve_theme(deck.theme)
    ea_font = deck.font_east_asia or theme.east_asia_font
    slide_payload = []

    for s in deck.slides:
        slide_payload.append(
            {
                "index": s.index,
                "layout": s.layout,
                "sectionTag": s.section_tag,
                "title": s.title,
                "subtitle": s.subtitle,
                "takeaway": s.takeaway,
                "bullets": s.bullets,
                "cards": [{"title": c.title, "body": c.body} for c in s.cards],
                "metrics": [{"value": m.value, "label": m.label, "detail": m.detail} for m in s.metrics],
                "table": {"headers": s.table.headers, "rows": s.table.rows} if s.table else None,
                "notes": s.notes,
            }
        )

    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(deck.title)} — cnppt-kit 离线预演</title>
  <style>
    :root {{
      --bg: #{theme.bg_hex};
      --surface: #{theme.surface_hex};
      --cover: #{theme.cover_bg_hex};
      --primary: #{theme.primary_hex};
      --accent: #{theme.accent_hex};
      --text: #{theme.text_hex};
      --muted: #{theme.muted_hex};
      --border: #{theme.border_hex};
      --font-sans: "{html.escape(ea_font)}", "PingFang SC", "Microsoft YaHei", "Source Han Sans SC", system-ui, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: var(--font-sans); background: #0f172a; color: var(--text); height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }}
    .stage {{ width: min(92vw, 1120px); aspect-ratio: 16 / 9; background: var(--bg); border-radius: 10px; box-shadow: 0 24px 60px rgba(0,0,0,.45); padding: 40px 52px; display: flex; flex-direction: column; overflow: hidden; position: relative; border-top: 6px solid var(--accent); }}
    .stage.cover {{ background: var(--cover); color: #fff; justify-content: center; border-top: none; border-left: 10px solid var(--accent); }}
    .tag {{ display: inline-block; background: var(--accent); color: #fff; font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 999px; margin-bottom: 10px; width: fit-content; }}
    h1 {{ color: var(--primary); font-size: clamp(24px, 2.8vw, 34px); margin-bottom: 8px; }}
    .stage.cover h1 {{ color: #fff; font-size: clamp(30px, 3.6vw, 44px); }}
    .subtitle {{ color: var(--muted); font-size: 16px; margin-bottom: 18px; }}
    .stage.cover .subtitle {{ color: #cbd5e1; font-size: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; flex: 1; align-content: start; margin-top: 8px; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-top: 4px solid var(--accent); border-radius: 8px; padding: 18px; }}
    .card h3 {{ color: var(--primary); font-size: 17px; margin-bottom: 8px; }}
    .card p {{ font-size: 14px; line-height: 1.55; }}
    .metric-val {{ color: var(--accent); font-size: 32px; font-weight: 800; margin-bottom: 6px; }}
    ul {{ list-style: none; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px 28px; display: flex; flex-direction: column; gap: 12px; flex: 1; }}
    li {{ font-size: 16px; line-height: 1.5; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--surface); font-size: 14px; margin-top: 8px; }}
    th {{ background: var(--primary); color: #fff; padding: 10px 12px; text-align: left; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
    tr:nth-child(even) td {{ background: #f1f5f9; }}
    .takeaway {{ margin-top: auto; background: var(--surface); border: 1px solid var(--accent); border-radius: 6px; padding: 10px 16px; color: var(--primary); font-weight: 700; font-size: 14px; }}
    .controls {{ display: flex; align-items: center; gap: 14px; color: #e2e8f0; font-size: 14px; }}
    button {{ background: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 6px 14px; border-radius: 6px; cursor: pointer; }}
    button:hover {{ background: #334155; }}
    .notes-box {{ width: min(92vw, 1120px); background: #1e293b; color: #cbd5e1; padding: 10px 16px; border-radius: 8px; font-size: 13px; display: none; white-space: pre-wrap; }}
    .notes-box.open {{ display: block; }}
  </style>
</head>
<body>
  <div id="stage" class="stage"></div>
  <div class="controls">
    <button onclick="go(-1)">← 上一页</button>
    <span id="counter"></span>
    <button onclick="go(1)">下一页 →</button>
    <button onclick="toggleNotes()">讲稿备注 (N)</button>
  </div>
  <div id="notes" class="notes-box"></div>
  <script>
    const SLIDES = {json.dumps(slide_payload, ensure_ascii=False)};
    let cur = 0;
    function esc(s) {{ return String(s ?? '').replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c])); }}
    function render() {{
      const s = SLIDES[cur];
      const st = document.getElementById('stage');
      st.className = 'stage' + ((s.layout === 'cover' || s.layout === 'closing') ? ' cover' : '');
      let h = '';
      if (s.sectionTag && s.layout !== 'cover') h += `<span class="tag">${{esc(s.sectionTag)}}</span>`;
      h += `<h1>${{esc(s.title)}}</h1>`;
      if (s.subtitle) h += `<p class="subtitle">${{esc(s.subtitle)}}</p>`;
      if (s.table) {{
        h += '<table><thead><tr>' + s.table.headers.map(x => `<th>${{esc(x)}}</th>`).join('') + '</tr></thead><tbody>';
        h += s.table.rows.map(r => '<tr>' + r.map(c => `<td>${{esc(c)}}</td>`).join('') + '</tr>').join('') + '</tbody></table>';
      }} else if (s.metrics && s.metrics.length) {{
        h += '<div class="grid">' + s.metrics.map(m => `<div class="card"><div class="metric-val">${{esc(m.value)}}</div><h3>${{esc(m.label)}}</h3><p>${{esc(m.detail)}}</p></div>`).join('') + '</div>';
      }} else if (s.cards && s.cards.length) {{
        h += '<div class="grid">' + s.cards.map(c => `<div class="card"><h3>${{esc(c.title)}}</h3><p>${{esc(c.body)}}</p></div>`).join('') + '</div>';
      }} else if (s.bullets && s.bullets.length) {{
        h += '<ul>' + s.bullets.map(b => `<li>▪ ${{esc(b)}}</li>`).join('') + '</ul>';
      }}
      if (s.takeaway) h += `<div class="takeaway">核心结论：${{esc(s.takeaway)}}</div>`;
      st.innerHTML = h;
      document.getElementById('counter').textContent = `${{cur + 1}} / ${{SLIDES.length}}`;
      document.getElementById('notes').textContent = s.notes ? '演讲备注：\\n' + s.notes : '（当前页暂无演讲备注）';
    }}
    function go(d) {{ cur = Math.max(0, Math.min(SLIDES.length - 1, cur + d)); render(); }}
    function toggleNotes() {{ document.getElementById('notes').classList.toggle('open'); }}
    window.addEventListener('keydown', e => {{
      if (e.key === 'ArrowRight' || e.key === ' ') go(1);
      else if (e.key === 'ArrowLeft') go(-1);
      else if (e.key.toLowerCase() === 'n') toggleNotes();
    }});
    render();
  </script>
</body>
</html>
"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out
