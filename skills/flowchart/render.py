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
 .note{color:#6b7787;font-size:11.5px;margin-top:12px}
 code{background:#eef3f7;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace}
</style></head><body>
<h1>__TITLE__</h1>
<div class="legend">__LEGEND__</div>
<div class="wrap"><pre class="mermaid">
__MERMAID__
</pre></div>
<p class="note">Nguồn diagram: <code>__SRC__</code> — mở/sửa/export PNG·SVG tại <b>mermaid.live</b> · <b>draw.io</b> (Extras → Edit Diagram → Mermaid) · <b>VS Code</b> (Mermaid Preview). Nếu diagram không hiện (offline/chặn CDN) → dùng file .mmd.</p>
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
  bar.innerHTML='<button data-a="in" title="Phóng to">＋</button><button data-a="out" title="Thu nhỏ">－</button><button data-a="fit">Vừa khung</button><button data-a="one">100%</button><button data-a="full">⤢ Toàn màn hình</button><span>Bấm vào sơ đồ để mở toàn màn hình · kéo để di chuyển · cuộn chuột (hoặc Ctrl + cuộn khi xem trong trang) để zoom · nhấp đúp để phóng to chỗ đó · Esc để đóng</span>';
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
