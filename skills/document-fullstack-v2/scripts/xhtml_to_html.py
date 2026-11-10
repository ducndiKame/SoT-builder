# -*- coding: utf-8 -*-
"""
xhtml_to_html.py — render file AC Gherkin (Confluence storage XHTML) thành 1 file HTML tự chứa.

- Kiểm tra XHTML well-formed (báo lỗi và dừng nếu hỏng).
- TOC macro  -> mục lục từ h1/h2.
- info/note/warning/tip macro -> khối ghi chú.
- code macro language=mermaid -> sơ đồ Mermaid render bằng mermaid.js (CDN).
- <ac:image><ri:attachment ri:filename="x.png"/></ac:image> -> <img> nhúng base64
  (ảnh lấy từ thư mục --assets, mặc định <tên-file>_assets/ cạnh file .xml),
  nên file HTML gửi đi vẫn hiện ảnh, không phụ thuộc link.

Cách dùng:
    python xhtml_to_html.py <doc>.xml [--assets <dir>] [--title "Tiêu đề"]
Ra: <doc>.html cùng thư mục.
"""
import argparse, base64, html, mimetypes, os, re, sys
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--assets")
ap.add_argument("--title")
a = ap.parse_args()

src = os.path.abspath(a.src)
stem = os.path.splitext(src)[0]
assets = os.path.abspath(a.assets) if a.assets else stem + "_assets"
body = open(src, encoding="utf-8-sig").read()

# 1. well-formed
try:
    ET.fromstring(('<root xmlns:ac="http://atlassian.com/ac" xmlns:ri="http://atlassian.com/ri">'
                   + body + "</root>").encode("utf-8"))
except ET.ParseError as e:
    sys.exit("XHTML không hợp lệ: %s" % e)

# 2. mermaid code macro
def mermaid(m):
    code = m.group(1)
    return '<div class="flow"><pre class="mermaid">%s</pre></div>' % html.escape(code)
body = re.sub(r'<ac:structured-macro ac:name="code">\s*<ac:parameter ac:name="language">mermaid</ac:parameter>\s*'
              r'<ac:plain-text-body><!\[CDATA\[(.*?)\]\]></ac:plain-text-body>\s*</ac:structured-macro>',
              mermaid, body, flags=re.S)

# 3. images -> base64
missing = []
def img(m):
    width = m.group(1) or "220"
    fn = m.group(2)
    p = os.path.join(assets, fn)
    if not os.path.isfile(p):
        missing.append(fn)
        return '<span class="missing">[thiếu ảnh %s]</span>' % html.escape(fn)
    mime = mimetypes.guess_type(p)[0] or "image/png"
    data = base64.b64encode(open(p, "rb").read()).decode()
    return '<img src="data:%s;base64,%s" width="%s" alt="%s">' % (mime, data, width, html.escape(fn))
body = re.sub(r'<ac:image(?: ac:width="(\d+)")?>\s*<ri:attachment ri:filename="([^"]+)"\s*/>\s*</ac:image>', img, body)

# 4. headings + TOC
toc = []
def head(m):
    lvl, text = m.group(1), m.group(2)
    slug = "h-%d" % len(toc)
    toc.append((int(lvl), re.sub("<[^>]+>", "", text), slug))
    return '<h%s id="%s">%s</h%s>' % (lvl, slug, text, lvl)
body = re.sub(r"<h([12])>(.*?)</h\1>", head, body)
toc_html = ('<nav class="toc"><strong>Mục lục</strong><ul>'
            + "".join('<li class="l%d"><a href="#%s">%s</a></li>' % (l, s, t) for l, t, s in toc) + "</ul></nav>")
body = re.sub(r'<p><ac:structured-macro ac:name="toc">.*?</ac:structured-macro></p>', toc_html, body, flags=re.S)

# 5. note macros
body = re.sub(r'<ac:structured-macro ac:name="(info|note|warning|tip)"><ac:rich-text-body>(.*?)</ac:rich-text-body></ac:structured-macro>',
              r'<div class="macro \1">\2</div>', body, flags=re.S)
body = re.sub(r"(<table>.*?</table>)", r'<div class="wrap">\1</div>', body, flags=re.S)

title = a.title or os.path.basename(stem)
page = """<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>%(t)s</title>
<meta name="generator" content="document-fullstack-v2 xhtml_to_html">
<style>
:root{--bg:#fff;--fg:#1d1f24;--muted:#5b6170;--line:#dde0e6;--head:#f3f1fb;--accent:#6b4dd6;--note:#fff7e6;--noteb:#e0a43a}
@media (prefers-color-scheme:dark){:root{--bg:#16171b;--fg:#e8e9ec;--muted:#a3a8b4;--line:#33363e;--head:#24223a;--accent:#a996ff;--note:#2e2716;--noteb:#a8792a}}
body{background:var(--bg);color:var(--fg);font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:24px 16px}
main{max-width:1360px;margin:auto} h1{font-size:22px;margin:32px 0 10px;border-bottom:2px solid var(--accent);padding-bottom:4px}
h2{font-size:17px;margin:26px 0 8px;color:var(--accent)} a{color:var(--accent)}
.wrap{overflow-x:auto} table{border-collapse:collapse;width:100%%;margin:6px 0 14px;font-size:13px}
th,td{border:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left} th{background:var(--head)}
td ul{margin:0;padding-left:18px} td img{display:block;border:1px solid var(--line);border-radius:10px;margin:2px 0 6px;max-width:100%%;height:auto}
.toc{border:1px solid var(--line);border-radius:8px;padding:10px 14px;display:inline-block} .toc ul{margin:6px 0 0;padding-left:18px} .toc .l2{margin-left:16px;font-size:13px}
.macro{border-left:4px solid var(--noteb);background:var(--note);padding:8px 14px;border-radius:6px;margin:10px 0}
.flow{border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;background:#fff}
.missing{color:#b3261e;font-weight:600}
</style></head><body><main><h1 style="border:0;font-size:26px">%(t)s</h1>
%(b)s</main>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true,securityLevel:'loose',flowchart:{htmlLabels:true}});</script>
</body></html>""" % {"t": html.escape(title), "b": body}
out = stem + ".html"
open(out, "w", encoding="utf-8").write(page)
print("OK", out, "| headings:", len(toc), "| missing images:", ", ".join(missing) if missing else "0")
