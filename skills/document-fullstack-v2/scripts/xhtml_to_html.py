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
    width = m.group(1) or "360"
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
main{max-width:1680px;margin:auto} h1{font-size:22px;margin:32px 0 10px;border-bottom:2px solid var(--accent);padding-bottom:4px}
h2{font-size:17px;margin:26px 0 8px;color:var(--accent)} a{color:var(--accent)}
.wrap{overflow-x:auto} table{border-collapse:collapse;width:100%%;margin:6px 0 14px;font-size:13px}
th,td{border:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left} th{background:var(--head)}
td ul{margin:0;padding-left:18px} td img{display:block;border:1px solid var(--line);border-radius:10px;margin:2px 0 6px;max-width:none;height:auto}
.toc{border:1px solid var(--line);border-radius:8px;padding:10px 14px;display:inline-block} .toc ul{margin:6px 0 0;padding-left:18px} .toc .l2{margin-left:16px;font-size:13px}
.macro{border-left:4px solid var(--noteb);background:var(--note);padding:8px 14px;border-radius:6px;margin:10px 0}
.flow{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fff}
.missing{color:#b3261e;font-weight:600}
</style></head><body><main><h1 style="border:0;font-size:26px">%(t)s</h1>
%(b)s</main>
<!-- FLOWZOOM:START — sơ đồ Mermaid zoom / kéo / toàn màn hình (SoT-builder) -->
<style>
.fz-bar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 8px;font:12px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;color:#5b6170;white-space:normal}
.fz-bar button{border:1px solid #c9cdd6;background:#fff;color:#1d1f24;border-radius:6px;padding:4px 10px;font:inherit;cursor:pointer}
.fz-bar button:hover{border-color:#6b4dd6;color:#6b4dd6}
.fz-view{position:relative;overflow:hidden;height:72vh;min-height:420px;border:1px solid #dde0e6;border-radius:8px;background:#fff;cursor:zoom-in;touch-action:none;white-space:normal}
.fz-full .fz-view{cursor:grab}.fz-view.drag{cursor:grabbing}
.fz-stage{position:absolute;left:0;top:0;transform-origin:0 0}
.fz-stage svg{max-width:none!important;display:block}
.fz-modal{position:fixed;inset:0;background:rgba(15,17,22,.78);z-index:9999;display:none;flex-direction:column;padding:16px;gap:6px}
.fz-modal.on{display:flex}.fz-modal .fz-bar{color:#e8e9ec}.fz-modal .fz-view{flex:1;height:auto;min-height:0}
</style>
<script>
window.flowZoomAll=function(){
 document.querySelectorAll('.mermaid').forEach(function(host){
  var svg=host.querySelector('svg'); if(!svg||host.getAttribute('data-fz')) return; host.setAttribute('data-fz','1');
  var vb=svg.viewBox&&svg.viewBox.baseVal, W=(vb&&vb.width)||svg.getBBox().width, H=(vb&&vb.height)||svg.getBBox().height;
  svg.setAttribute('width',W); svg.setAttribute('height',H); svg.style.maxWidth='none';
  var bar=document.createElement('div'); bar.className='fz-bar';
  bar.innerHTML='<button data-a="in" title="Phóng to">＋</button><button data-a="out" title="Thu nhỏ">－</button><button data-a="fit">Vừa khung</button><button data-a="one">100%%</button><button data-a="full">⤢ Toàn màn hình</button><span>Bấm vào sơ đồ để mở toàn màn hình · kéo để di chuyển · cuộn chuột (hoặc Ctrl + cuộn khi xem trong trang) để zoom · nhấp đúp để phóng to chỗ đó · Esc để đóng</span>';
  var view=document.createElement('div'); view.className='fz-view';
  var stage=document.createElement('div'); stage.className='fz-stage';
  host.innerHTML=''; stage.appendChild(svg); view.appendChild(stage); host.appendChild(bar); host.appendChild(view);
  host.style.minWidth='0'; host.style.whiteSpace='normal';
  var s=1,x=0,y=0,full=false,modal=document.createElement('div'); modal.className='fz-modal'; document.body.appendChild(modal);
  function apply(){stage.style.transform='translate('+x+'px,'+y+'px) scale('+s+')';}
  function fit(){var r=view.getBoundingClientRect(); s=Math.min(r.width/W,r.height/H)*0.96; x=(r.width-W*s)/2; y=(r.height-H*s)/2; apply();}
  function zoomAt(f,cx,cy){var n=Math.max(0.05,Math.min(10,s*f)); x=cx-(cx-x)*n/s; y=cy-(cy-y)*n/s; s=n; apply();}
  function mid(f){var r=view.getBoundingClientRect(); zoomAt(f,r.width/2,r.height/2);}
  function open(){if(full)return; full=true; modal.appendChild(bar); modal.appendChild(view); modal.classList.add('on','fz-full'); document.body.style.overflow='hidden'; bar.querySelector('[data-a=full]').textContent='✕ Đóng (Esc)'; requestAnimationFrame(fit);}
  function close(){if(!full)return; full=false; host.appendChild(bar); host.appendChild(view); modal.classList.remove('on','fz-full'); document.body.style.overflow=''; bar.querySelector('[data-a=full]').textContent='⤢ Toàn màn hình'; requestAnimationFrame(fit);}
  bar.addEventListener('click',function(e){var a=e.target.getAttribute('data-a'); if(!a)return;
   if(a==='in')mid(1.25); else if(a==='out')mid(0.8); else if(a==='fit')fit();
   else if(a==='one'){var r=view.getBoundingClientRect(); s=1; x=(r.width-W)/2; y=16; apply();} else full?close():open();});
  view.addEventListener('wheel',function(e){if(!full&&!e.ctrlKey)return; e.preventDefault(); var r=view.getBoundingClientRect(); zoomAt(e.deltaY<0?1.15:1/1.15,e.clientX-r.left,e.clientY-r.top);},{passive:false});
  var d=null,moved=false;
  view.addEventListener('pointerdown',function(e){d={px:e.clientX,py:e.clientY,x:x,y:y}; moved=false; view.setPointerCapture(e.pointerId);});
  view.addEventListener('pointermove',function(e){if(!d)return; var dx=e.clientX-d.px,dy=e.clientY-d.py; if(Math.abs(dx)+Math.abs(dy)>4){moved=true; view.classList.add('drag');} if(moved){x=d.x+dx; y=d.y+dy; apply();}});
  view.addEventListener('pointerup',function(){var c=d&&!moved; d=null; view.classList.remove('drag'); if(c&&!full)open();});
  view.addEventListener('dblclick',function(e){if(!full)return; var r=view.getBoundingClientRect(); zoomAt(1.6,e.clientX-r.left,e.clientY-r.top);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  fit();
 });
};
</script>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:false,securityLevel:'loose',flowchart:{htmlLabels:true,curve:'basis',nodeSpacing:38,rankSpacing:42}});
await mermaid.run({querySelector:'.mermaid'});
window.flowZoomAll();
</script>
<!-- FLOWZOOM:END -->
</body></html>""" % {"t": html.escape(title), "b": body}
out = stem + ".html"
open(out, "w", encoding="utf-8").write(page)
print("OK", out, "| headings:", len(toc), "| missing images:", ", ".join(missing) if missing else "0")
