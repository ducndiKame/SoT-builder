# -*- coding: utf-8 -*-
"""
render.py — wrap a Mermaid .mmd file into a self-contained HTML viewer.

Usage:
    python render.py <flow>.mmd [--title "Tiêu đề"] [--out <path>.html]

Output: an HTML (same stem by default) that renders the diagram via Mermaid CDN,
with a color legend. The .mmd stays the editable source (mermaid.live / draw.io / VS Code).
"""
import sys, os, html, argparse

LEGEND = [
    ("#0b3d61", "#08324f", "Màn / Terminator"),
    ("#e8f1fb", "#1a6fb0", "API call"),
    ("#fff7e6", "#c67f1e", "Quyết định ◇"),
    ("#fcecec", "#c0392b", "Lỗi (retry)"),
    ("#f6d7d4", "#b3261e", "Lỗi → thoát/kết thúc"),
    ("#eef0f2", "#8a94a0", "Rẽ nhánh khác"),
]

TEMPLATE = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
 body{margin:0;font:13px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1b2733;background:#eef2f6;padding:22px}
 h1{font-size:19px;margin:0 0 10px}
 .legend{background:#fff;border:1px solid #d9dee4;border-radius:8px;padding:9px 13px;margin-bottom:14px;font-size:11.5px;display:flex;gap:14px;flex-wrap:wrap;align-items:center}
 .sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:middle;margin-right:4px}
 .wrap{background:#fff;border:1px solid #d9dee4;border-radius:10px;padding:12px;overflow:auto}
 .mermaid{min-width:760px}
 .note{color:#6b7787;font-size:11.5px;margin-top:12px}
 code{background:#eef3f7;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace}
</style></head><body>
<h1>__TITLE__</h1>
<div class="legend">__LEGEND__</div>
<div class="wrap"><pre class="mermaid">
__MERMAID__
</pre></div>
<p class="note">Nguồn diagram: <code>__SRC__</code> — mở/sửa/export PNG·SVG tại <b>mermaid.live</b> · <b>draw.io</b> (Extras → Edit Diagram → Mermaid) · <b>VS Code</b> (Mermaid Preview). Nếu diagram không hiện (offline/chặn CDN) → dùng file .mmd.</p>
<script type="module">
 import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
 mermaid.initialize({ startOnLoad:true, flowchart:{ curve:'basis', nodeSpacing:38, rankSpacing:42 }, securityLevel:'loose' });
</script>
</body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mmd")
    ap.add_argument("--title", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    src = a.mmd
    with open(src, encoding="utf-8") as f:
        mer = f.read()

    title = a.title or ("Flowchart — " + os.path.splitext(os.path.basename(src))[0])
    out = a.out or (os.path.splitext(src)[0] + ".html")
    legend = "".join(
        '<span><span class="sw" style="background:%s;border:1px solid %s"></span>%s</span>' % (bg, br, html.escape(t))
        for bg, br, t in LEGEND
    )
    doc = (TEMPLATE.replace("__TITLE__", html.escape(title))
                   .replace("__LEGEND__", legend)
                   .replace("__SRC__", html.escape(os.path.basename(src)))
                   .replace("__MERMAID__", mer))
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("WROTE", out)

if __name__ == "__main__":
    main()
