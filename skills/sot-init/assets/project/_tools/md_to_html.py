# -*- coding: utf-8 -*-
"""
md_to_html.py: sinh bản .html tự chứa (cùng thư mục, cùng tên) cho một hoặc nhiều file .md.

Cách dùng:
    python3 _tools/md_to_html.py <file.md> [<file2.md> ...]      (macOS)
    python  _tools/md_to_html.py <file.md> [<file2.md> ...]      (Windows; hoặc `py`)
    python3 _tools/md_to_html.py --all <thư-mục>                 (mọi .md bên trong, bỏ qua _archive/)

Hỗ trợ: heading, đoạn văn, **đậm**, `code`, link (.md -> .html), bảng, list lồng nhau, task list,
blockquote, code block, khối ```mermaid (vẽ bằng Mermaid CDN), đường kẻ ngang.
Có mục lục bên trái và nút đổi sáng/tối. Sửa file .md rồi chạy lại; không sửa tay file .html.
Chỉ dùng thư viện chuẩn của Python 3.8+.
"""
import html
import os
import re
import sys

NUL = "\x00"

SKIP_FILES = {"CLAUDE.md"}  # file vận hành cho AI, không cần bản HTML


def esc(s):
    return html.escape(s, quote=True)


def inline(s):
    codes = []

    def keep_code(m):
        codes.append("<code>" + esc(m.group(1)) + "</code>")
        return NUL + str(len(codes) - 1) + NUL

    s = re.sub(r"`([^`]+)`", keep_code, s)
    s = esc(s)

    def link(m):
        href = m.group(2)
        target = os.path.basename(href.split("#")[0])
        if not re.match(r"^https?:", href) and target not in SKIP_FILES:
            href = re.sub(r"\.md(#.*)?$", lambda mm: ".html" + (mm.group(1) or ""), href)
        return '<a href="' + href + '">' + m.group(1) + "</a>"

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r'(?<!["=])(https?://[^\s<)]+)', r'<a href="\1">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(NUL + r"(\d+)" + NUL, lambda m: codes[int(m.group(1))], s)
    return s


def cells(row):
    t = row.strip()
    if t.startswith("|"):
        t = t[1:]
    if t.endswith("|"):
        t = t[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", t)]


MERMAID_LEGEND = (
    '<div class="mlegend">'
    '<span><i style="background:#0b3d61"></i>Màn / Terminator</span>'
    '<span><i style="background:#e8f1fb;border-color:#1a6fb0"></i>API / hệ thống</span>'
    '<span><i style="background:#fff7e6;border-color:#c67f1e"></i>Quyết định</span>'
    '<span><i style="background:#fcecec;border-color:#c0392b"></i>Lỗi (retry)</span>'
    '<span><i style="background:#f6d7d4;border-color:#b3261e"></i>Lỗi → thoát</span>'
    '<span><i style="background:#eef0f2;border-color:#8a94a0"></i>Rẽ nhánh khác</span>'
    "</div>"
)

LIST_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.*)$")


def convert(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, toc, para, stack = [], [], [], []
    state = {"title": None, "sec": 0, "mermaid": False}

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>\n")
            para.clear()

    def close_top():
        top = stack.pop()
        if top["has_li"]:
            out.append("</li>")
        out.append("</ol>\n" if top["ordered"] else "</ul>\n")

    def close_all():
        while stack:
            close_top()

    i, n = 0, len(lines)
    while i < n:
        l = lines[i]
        if re.match(r"^\s*<!--.*-->\s*$", l):
            i += 1
            continue
        m = re.match(r"^\s*```\s*([\w-]*)", l)
        if m:
            flush_para(); close_all()
            lang = m.group(1)
            code = []
            i += 1
            while i < n and not re.match(r"^\s*```", lines[i]):
                code.append(lines[i]); i += 1
            if lang == "mermaid":
                state["mermaid"] = True
                out.append('<div class="mermaid-wrap">' + MERMAID_LEGEND + '<pre class="mermaid">'
                           + esc("\n".join(code)) + "</pre></div>\n")
            else:
                out.append("<pre><code>" + esc("\n".join(code)) + "</code></pre>\n")
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            flush_para(); close_all()
            lv, txt = len(m.group(1)), m.group(2).strip()
            if lv == 1 and not state["title"]:
                state["title"] = txt
            state["sec"] += 1
            sid = "sec-%d" % state["sec"]
            if lv == 2:
                toc.append((sid, txt))
            out.append('<h%d id="%s">%s</h%d>\n' % (lv, sid, inline(txt), lv))
            i += 1
            continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", l):
            flush_para(); close_all(); out.append("<hr>\n"); i += 1
            continue
        if re.match(r"^\s*\|", l):
            flush_para(); close_all()
            rows = []
            while i < n and re.match(r"^\s*\|", lines[i]):
                rows.append(lines[i]); i += 1
            out.append('<div class="tablewrap"><table>')
            start = 0
            if len(rows) > 1 and re.match(r"^[\s|:\-]+$", rows[1]):
                out.append("<thead><tr>" + "".join("<th>" + inline(c) + "</th>" for c in cells(rows[0])) + "</tr></thead>")
                start = 2
            out.append("<tbody>")
            for r in rows[start:]:
                out.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in cells(r)) + "</tr>")
            out.append("</tbody></table></div>\n")
            continue
        if re.match(r"^\s*>\s?(.*)$", l):
            flush_para(); close_all()
            q = []
            while i < n:
                mm = re.match(r"^\s*>\s?(.*)$", lines[i])
                if not mm:
                    break
                q.append(inline(mm.group(1))); i += 1
            out.append("<blockquote>" + "<br>".join(q) + "</blockquote>\n")
            continue
        m = LIST_RE.match(l)
        if m:
            flush_para()
            ind, content, ordered = len(m.group(1)), m.group(3), bool(re.match(r"^\d", m.group(2)))
            while stack and stack[-1]["indent"] > ind:
                close_top()
            if stack and stack[-1]["indent"] == ind and stack[-1]["ordered"] != ordered:
                close_top()
            if not stack or stack[-1]["indent"] < ind:
                out.append("<ol>" if ordered else "<ul>")
                stack.append({"indent": ind, "ordered": ordered, "has_li": False})
            top = stack[-1]
            if top["has_li"]:
                out.append("</li>")
            t = re.match(r"^\[( |x|X)\]\s+(.*)$", content)
            if t:
                chk = " checked" if t.group(1) != " " else ""
                out.append('<li class="task"><input type="checkbox" disabled' + chk + "> " + inline(t.group(2)))
            else:
                out.append("<li>" + inline(content))
            top["has_li"] = True
            i += 1
            continue
        if re.match(r"^\s*$", l):
            flush_para()
            j = i + 1
            while j < n and re.match(r"^\s*$", lines[j]):
                j += 1
            if stack and (j >= n or not LIST_RE.match(lines[j])):
                close_all()
            i += 1
            continue
        if stack and re.match(r"^\s{2,}\S", l):
            out.append(" " + inline(l.strip())); i += 1
            continue
        close_all(); para.append(l.strip()); i += 1
    flush_para(); close_all()
    return "".join(out), toc, state["title"], state["mermaid"]


CSS = """:root{--bg:#FAF6F0;--surface:#FFFFFF;--surface-2:#F3EEE6;--text:#18191F;--text-2:#5F6063;--text-3:#707070;--line:#E7E0D5;--brand:#C4381F;--code:#F3EEE6;--quote:#8A5A00;--quote-bg:#FBEFD5;--shadow:0 4px 24px rgba(0,0,0,.05)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#16161A;--surface:#1F1F25;--surface-2:#26262D;--text:#F2F0EC;--text-2:#B9B7B2;--text-3:#9A9893;--line:#34343C;--brand:#FF8A73;--code:#26262D;--quote:#F2C46B;--quote-bg:#352B17;--shadow:none}}
:root[data-theme="dark"]{--bg:#16161A;--surface:#1F1F25;--surface-2:#26262D;--text:#F2F0EC;--text-2:#B9B7B2;--text-3:#9A9893;--line:#34343C;--brand:#FF8A73;--code:#26262D;--quote:#F2C46B;--quote-bg:#352B17;--shadow:none}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 -apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--brand);word-break:break-word}
.layout{display:grid;grid-template-columns:240px minmax(0,1fr);max-width:1320px;margin:0 auto}
nav.toc{position:sticky;top:0;height:100vh;overflow:auto;padding:28px 18px;border-right:1px solid var(--line)}
nav.toc .doc{font-weight:700;font-size:15px;margin-bottom:14px;line-height:1.35}
nav.toc a{display:block;color:var(--text-2);text-decoration:none;font-size:13.5px;padding:4px 8px;border-radius:8px;line-height:1.35}
nav.toc a:hover{background:var(--surface-2);color:var(--text)}
.themebtn{margin-top:18px;border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:20px;padding:8px 14px;font:inherit;font-size:13px;cursor:pointer;min-height:40px}
main{padding:36px 44px 100px;min-width:0}
h1{font-size:30px;line-height:1.25;margin:0 0 16px}
h2{font-size:22px;margin:40px 0 12px;padding-top:8px;border-top:1px solid var(--line);scroll-margin-top:12px}
h3{font-size:17px;margin:26px 0 8px}h4{font-size:15px;margin:20px 0 6px}
p,li{max-width:84ch}
blockquote{margin:14px 0;padding:12px 16px;border-left:4px solid var(--quote);background:var(--quote-bg);border-radius:0 12px 12px 0;font-size:14.5px}
.tablewrap{overflow-x:auto;margin:12px 0 18px;border-radius:14px;background:var(--surface);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:9px 13px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;letter-spacing:.03em;text-transform:uppercase;color:var(--text-3);background:var(--surface-2);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
code{font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:1px 6px;border-radius:6px;word-break:break-word}
pre{background:var(--code);border-radius:14px;padding:14px 16px;overflow-x:auto;font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre code{background:none;padding:0}
li.task{list-style:none;margin-left:-22px}li.task input{margin-right:6px;transform:translateY(1px)}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
footer{margin-top:48px;color:var(--text-3);font-size:12.5px}
.mermaid-wrap{background:#fff;border:1px solid #d9dee4;border-radius:14px;padding:12px;margin:14px 0 22px;overflow:auto}
.mermaid-wrap pre.mermaid{background:#fff;margin:0;padding:0;min-width:760px;white-space:pre;color:#1b2733}
.mlegend{display:flex;flex-wrap:wrap;gap:12px;font-size:11.5px;color:#41505f;margin-bottom:10px}
.mlegend i{display:inline-block;width:12px;height:12px;border-radius:3px;border:1px solid #08324f;vertical-align:middle;margin-right:4px}
.themebtn:focus-visible,nav.toc a:focus-visible{outline:3px solid var(--brand);outline-offset:2px}
@media (max-width:900px){.layout{grid-template-columns:1fr}nav.toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:16px}nav.toc .links{display:none}main{padding:22px 16px 72px}h1{font-size:25px}}
"""

JS = """(function(){var r=document.documentElement,b=document.getElementById('themeBtn');try{var t=localStorage.getItem('doc-theme');if(t)r.setAttribute('data-theme',t);}catch(e){}
b.addEventListener('click',function(){var c=r.getAttribute('data-theme');if(!c){c=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('doc-theme',n);}catch(e){}});})();
"""

MERMAID_JS = ("<script type=\"module\">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';"
              "mermaid.initialize({startOnLoad:true,theme:'default',flowchart:{curve:'basis',nodeSpacing:38,rankSpacing:42},securityLevel:'loose'});</script>\n")


def render_file(path):
    with open(path, encoding="utf-8-sig") as f:
        md = f.read()
    body, toc, title, has_mermaid = convert(md)
    title = re.sub(r"[`*]", "", title) if title else os.path.splitext(os.path.basename(path))[0]
    nav = "".join('<a href="#%s">%s</a>' % (sid, inline(t)) for sid, t in toc)
    doc = (
        "<!DOCTYPE html>\n<html lang=\"vi\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"generator\" content=\"sot-builder md_to_html\">\n"
        "<title>" + esc(title) + "</title>\n<style>\n" + CSS + "</style>\n</head>\n<body>\n<div class=\"layout\">\n"
        "<nav class=\"toc\" aria-label=\"Mục lục\"><div class=\"doc\">" + esc(title) + "</div><div class=\"links\">" + nav
        + "</div><button class=\"themebtn\" type=\"button\" id=\"themeBtn\">Đổi sáng/tối</button></nav>\n<main>\n" + body
        + "<footer>Sinh tự động từ <code>" + esc(os.path.basename(path)) + "</code> bằng <code>_tools/md_to_html.py</code>. "
        "Sửa file .md rồi chạy lại script, không sửa trực tiếp file .html.</footer>\n</main>\n</div>\n<script>\n" + JS
        + "</script>\n" + (MERMAID_JS if has_mermaid else "") + "</body>\n</html>\n"
    )
    out = os.path.splitext(path)[0] + ".html"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return out


def iter_all(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("_archive", ".git", "_tools", "node_modules")]
        for fn in filenames:
            if fn.lower().endswith(".md") and fn not in SKIP_FILES:
                yield os.path.join(dirpath, fn)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    paths = list(iter_all(argv[1])) if argv[0] == "--all" else argv
    for p in paths:
        print(render_file(p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
