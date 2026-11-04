# -*- coding: utf-8 -*-
"""
build_tokens.py: dựng bộ token + text style theo khung FitAgain cho một dự án mới, rồi sinh script use_figma.

Hai lệnh:
  build  Tạo tokens.json (spec đầy đủ, designer đọc và sửa được) + báo cáo contrast.
  emit   Đọc tokens.json, sinh 3 file .js để dán vào use_figma:
         01-variables.js, 02-text-styles.js, 03-foundations.js

Ví dụ:
  py build_tokens.py build --primary "#2BB673" --display-font "Playfair Display" \
      --body-font "Inter" --out design-system/tokens.json --report design-system/tokens-report.md
  py build_tokens.py emit --spec design-system/tokens.json --out-dir <scratchpad>/figma

Chỉ dùng thư viện chuẩn của Python 3.8+. Chạy được trên macOS và Windows.
"""
import argparse
import datetime
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "..", "assets", "baseline.json")
TEMPLATES = os.path.join(HERE, "templates")
USE_FIGMA_LIMIT = 50000

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------- màu ----------

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError("Mã màu không hợp lệ: #" + h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join("%02X" % max(0, min(255, round(c * 255))) for c in rgb)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _delin(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def _cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def rgb_to_oklch(rgb):
    r, g, b = (_lin(c) for c in rgb)
    l = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def oklch_to_rgb_raw(L, C, H):
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return r, g, b


def oklch_to_rgb(L, C, H):
    """Giảm chroma tới khi nằm trong gamut sRGB (giữ L và H)."""
    def inside(c):
        return all(-1e-4 <= x <= 1 + 1e-4 for x in oklch_to_rgb_raw(L, c, H))
    if not inside(C):
        lo, hi = 0.0, C
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid) else (lo, mid)
        C = lo
    return tuple(_delin(max(0.0, min(1.0, x))) for x in oklch_to_rgb_raw(L, C, H))


def luminance(hexv):
    r, g, b = (_lin(c) for c in hex_to_rgb(hexv))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def generate_ramp(brand_hex, profile_hexes):
    """10 bậc theo đường L/C của ramp mẫu (FitAgain primary); màu brand giữ nguyên ở bậc gần nhất."""
    prof = [rgb_to_oklch(hex_to_rgb(h)) for h in profile_hexes]
    Lb, Cb, Hb = rgb_to_oklch(hex_to_rgb(brand_hex))
    k = min(range(10), key=lambda i: abs(prof[i][0] - Lb))
    dL = Lb - prof[k][0]
    out = []
    for i in range(10):
        if i == k:
            out.append(brand_hex.upper())
            continue
        span = k if i < k else 9 - k
        w = 1 - abs(i - k) / span if span else 0
        L = prof[i][0] + dL * w
        C = Cb * (prof[i][1] / prof[k][1]) if prof[k][1] > 1e-6 else prof[i][1]
        drift = (prof[i][2] - prof[k][2] + 180) % 360 - 180
        out.append(rgb_to_hex(oklch_to_rgb(L, C, (Hb + drift) % 360)))
    return out, k


# ---------- token ----------

class Palette:
    def __init__(self, steps, ramps, base):
        self.steps, self.ramps, self.base = steps, ramps, base

    def hex(self, ref):
        if ref in self.base:
            return self.base[ref]
        ramp, step = ref.split("/")
        return self.ramps[ramp][self.steps.index(int(step))]

    def shift(self, ref, delta):
        if ref in self.base or "/" not in ref:
            return None
        ramp, step = ref.split("/")
        i = self.steps.index(int(step)) + delta
        if 0 <= i < len(self.steps):
            return "%s/%d" % (ramp, self.steps[i])
        return None


def run_gates(pal, sem, modes, gates, keep, fix, distinct):
    """Dời bậc token để đạt ngưỡng contrast. sem: {token: {mode: ref}}.
    Không dời một token lên trùng bậc với token cùng nhóm thứ bậc (vd text/tertiary trùng text/secondary):
    chỗ đó để designer quyết. Trả về (thay đổi, chỗ bị chặn)."""
    siblings = {t: [x for x in g if x != t] for g in distinct for t in g}
    changes, blocked = [], {}
    for _ in range(3):
        moved = False
        for fg, bg, need, side, links in gates:
            for mode in modes:
                ratio = contrast(pal.hex(sem[fg][mode]), pal.hex(sem[bg][mode]))
                if ratio >= need:
                    continue
                target, other = (fg, bg) if side == "fg" else (bg, fg)
                if not fix or target in keep or (target + ":" + mode) in keep:
                    continue
                cur = sem[target][mode]
                if cur in pal.base:
                    continue
                darker = luminance(pal.hex(sem[other][mode])) > luminance(pal.hex(cur))
                direction = 1 if darker else -1
                for d in range(1, len(pal.steps)):
                    cand = pal.shift(cur, direction * d)
                    if cand is None:
                        break
                    clash = [x for x in siblings.get(target, []) if x not in links and sem[x][mode] == cand]
                    if clash:
                        blocked[(target, mode)] = "dời tiếp sẽ trùng `%s` (`%s`)" % (clash[0], cand)
                        break
                    pair = (pal.hex(cand), pal.hex(sem[other][mode]))
                    if contrast(*pair) >= need:
                        changes.append((target, mode, cur, cand, "%s / %s %.2f → %.2f" % (fg, bg, ratio, contrast(*pair))))
                        sem[target][mode] = cand
                        for ln in links:
                            nref = pal.shift(sem[ln][mode], direction * d)
                            if nref is None:
                                nref = pal.shift(sem[ln][mode], direction * (d - 1)) or sem[ln][mode]
                            if nref != sem[ln][mode]:
                                changes.append((ln, mode, sem[ln][mode], nref, "dời theo " + target))
                                sem[ln][mode] = nref
                        moved = True
                        break
        if not moved:
            break
    return changes, blocked


def scope_for(name, rules):
    for pattern, scopes in rules:
        parts, segs = pattern.split("/"), name.split("/")
        if parts[-1] == "*":
            if len(segs) >= len(parts) and all(p in ("*", s) for p, s in zip(parts[:-1], segs)):
                return scopes
        elif len(parts) == len(segs) and all(p in ("*", s) for p, s in zip(parts, segs)):
            return scopes
    return []


def parse_kv(items, what):
    out = {}
    for it in items or []:
        if "=" not in it:
            sys.exit("%s phải có dạng tên=giá trị: %s" % (what, it))
        k, v = it.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def cmd_build(a):
    with open(BASELINE, encoding="utf-8") as f:
        bl = json.load(f)
    steps = bl["steps"]
    ramps = {k: list(v) for k, v in bl["ramps"].items()}
    profile = bl["ramps"][bl["ramp_profile"]]
    generated = {}

    manual = parse_kv(a.ramp_hex, "--ramp-hex")
    seeds = parse_kv(a.ramp, "--ramp")
    extra = parse_kv(a.add_ramp, "--add-ramp")
    if a.primary:
        seeds["primary"] = a.primary
    if "primary" not in seeds and "primary" not in manual:
        sys.exit("Cần --primary <hex> hoặc --ramp-hex primary=<10 mã>")
    order = list(bl["ramp_order"])
    for name, seed in list(seeds.items()) + list(extra.items()):
        ramps[name], k = generate_ramp(seed, profile)
        generated[name] = (seed.upper(), steps[k])
        if name not in order:
            order.append(name)
    for name, vals in manual.items():
        hexes = [v.strip() for v in vals.split(",")]
        if len(hexes) != len(steps):
            sys.exit("--ramp-hex %s cần đúng %d mã màu" % (name, len(steps)))
        ramps[name] = [rgb_to_hex(hex_to_rgb(h)) for h in hexes]
        generated.pop(name, None)
        if name not in order:
            order.append(name)

    modes = ["Light", "Dark"] if a.modes == "light,dark" else ["Light"]
    pal = Palette(steps, ramps, bl["base"])
    baseline_sem = {n: {"Light": l, "Dark": d} for n, l, d, _ in bl["semantic"]}
    sem = {n: dict(v) for n, v in baseline_sem.items()}
    for item in a.set or []:
        if "=" not in item:
            sys.exit("--set phải có dạng token[:Mode]=ramp/bậc: " + item)
        tok, ref = item.split("=", 1)
        tok, _, only = tok.partition(":")
        if tok not in sem:
            sys.exit("--set: không có token " + tok)
        try:
            pal.hex(ref)
        except (KeyError, ValueError):
            sys.exit("--set: không có màu " + ref)
        for m in ([only] if only else modes):
            sem[tok][m] = ref
    keep_set = set(a.keep or [])
    for item in a.set or []:
        keep_set.add(item.split("=", 1)[0])
    desc = {n: d for n, _, _, d in bl["semantic"]}
    gates = bl["gates"]["list"]
    keep = keep_set
    changes, blocked = run_gates(pal, sem, modes, gates, keep, not a.no_fix, bl["gates"]["distinct"])

    rules = bl["scopes"]
    prim_vars = [{"name": n, "type": "COLOR", "values": {"Default": h}, "scopes": [], "description": ""}
                 for n, h in bl["base"].items()]
    for r in order:
        for s, h in zip(steps, ramps[r]):
            prim_vars.append({"name": "%s/%d" % (r, s), "type": "COLOR", "values": {"Default": h},
                              "scopes": [], "description": ""})
    sem_vars = [{"name": n, "type": "COLOR",
                 "values": {m: "@Primitives:" + sem[n][m] for m in modes},
                 "scopes": scope_for(n, rules), "description": desc[n]} for n, _, _, _ in bl["semantic"]]
    collections = [
        {"name": "Primitives", "modes": ["Default"], "hiddenFromPublishing": True, "variables": prim_vars},
        {"name": "Semantic", "modes": modes, "hiddenFromPublishing": False, "variables": sem_vars},
    ]
    if a.dimension:
        dim = bl["dimension"]
        dvars = [{"name": "spacing/%d" % v, "type": "FLOAT", "values": {"Default": v},
                  "scopes": scope_for("spacing/x", rules), "description": ""} for v in dim["spacing"]]
        dvars += [{"name": "radius/" + n, "type": "FLOAT", "values": {"Default": v},
                   "scopes": scope_for("radius/x", rules), "description": ""} for n, v in dim["radius"]]
        collections.append({"name": "Dimension", "modes": ["Default"], "hiddenFromPublishing": False,
                            "variables": dvars})

    fonts = {"display": a.display_font, "body": a.body_font, "mono": a.mono_font or None}
    styles, skipped = [], []
    for n, role, w, size, lh, ls, case, dec in bl["text_styles"]["list"]:
        if not fonts.get(role):
            skipped.append(n)
            continue
        styles.append({"name": n, "role": role, "weight": w, "size": size, "lineHeight": lh,
                       "letterSpacing": ls, "textCase": case, "decoration": dec})

    spec = {
        "meta": {"generator": "figma-style-builder", "baseline": "FitAgain 2026-11-04",
                 "project": a.project or "", "created": datetime.date.today().isoformat(),
                 "inputs": {"primary": a.primary, "ramp": seeds, "rampHex": list(manual), "addRamp": extra,
                            "modes": modes, "dimension": bool(a.dimension), "keep": sorted(keep),
                            "noFix": bool(a.no_fix)}},
        "fonts": fonts,
        "codeSyntax": {k: v for k, v in bl["code_syntax"].items() if not k.startswith("_")},
        "collections": collections,
        "textStyles": styles,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        f.write("\n")

    report = build_report(a, bl, pal, order, generated, baseline_sem, sem, modes, gates, keep, changes,
                          blocked, styles, skipped, fonts)
    if a.report:
        with open(a.report, "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
    fails = sum(1 for line in report.splitlines() if line.startswith("| ") and "❌" in line)
    print("Đã ghi: " + a.out + ((" + " + a.report) if a.report else ""))
    print("Biến: %d Primitives · %d Semantic (%s)%s · Text style: %d (bỏ %d)" % (
        len(prim_vars), len(sem_vars), "/".join(modes),
        (" · %d Dimension" % len(collections[2]["variables"])) if a.dimension else "", len(styles), len(skipped)))
    print("Dời bậc so với khung: %d · Cặp contrast chưa đạt: %d" % (len(changes), fails))
    if not a.report:
        print(report)


def build_report(a, bl, pal, order, generated, baseline_sem, sem, modes, gates, keep, changes, blocked,
                 styles, skipped, fonts):
    L = ["# Báo cáo token — %s" % (a.project or "dự án mới"), "",
         "Sinh bởi `figma-style-builder` ngày %s, khung FitAgain. Đọc bảng **Dời bậc** và **Contrast** trước "
         "khi ghi vào Figma." % datetime.date.today().isoformat(), ""]
    L += ["## Ramp", "", "| Ramp | Nguồn | " + " | ".join(str(s) for s in pal.steps) + " |",
          "|---|---|" + "---|" * len(pal.steps)]
    for r in order:
        src = ("sinh từ %s (đặt ở bậc %d)" % generated[r]) if r in generated else "khung FitAgain" \
            if r in bl["ramps"] and pal.ramps[r] == bl["ramps"][r] else "nhập tay"
        L.append("| %s | %s | %s |" % (r, src, " | ".join("`%s`" % h for h in pal.ramps[r])))
    L += ["", "Chữ trắng trên từng bậc của ramp primary (cần ≥ 4.5 cho nút có chữ):", "",
          "| " + " | ".join(str(s) for s in pal.steps) + " |", "|" + "---|" * len(pal.steps),
          "| " + " | ".join("%.2f" % contrast("#FFFFFF", h) for h in pal.ramps["primary"]) + " |", ""]

    L += ["## Dời bậc so với khung FitAgain", ""]
    if changes:
        L += ["| Token | Mode | Khung | Sau cổng contrast | Lý do |", "|---|---|---|---|---|"]
        for t, m, old, new, why in changes:
            L.append("| `%s` | %s | `%s` | `%s` | %s |" % (t, m, old, new, why))
        L += ["", "Muốn giữ màu của khung cho token nào thì chạy lại `build` với `--keep <token>` "
              "(hoặc `--keep <token>:Dark`) và ghi ngoại lệ vào `open-questions.md`.", ""]
    else:
        L += ["Không có token nào phải dời.", ""]

    L += ["## Contrast (WCAG 2.2 AA)", "", "| Cặp | Mode | Đo được | Ngưỡng | Kết quả |", "|---|---|---|---|---|"]
    for fg, bg, need, _, _ in gates:
        for m in modes:
            r = contrast(pal.hex(sem[fg][m]), pal.hex(sem[bg][m]))
            mark = "✅" if r >= need else ("❌ giữ theo --keep" if (fg in keep or bg in keep) else "❌")
            L.append("| `%s` / `%s` | %s | %.2f | %.1f | %s |" % (fg, bg, m, r, need, mark))
    if blocked:
        L += ["", "**Cần designer quyết** (cổng không tự sửa được mà không phá thứ bậc):", ""]
        for (t, m), why in blocked.items():
            L.append("- `%s` (%s): %s. Chọn một: (a) dời token cùng nhóm thêm một bậc bằng "
                     "`--set <token>:%s=<ramp/bậc>` rồi chạy lại; (b) giới hạn token này ở nền đạt chuẩn và ghi luật "
                     "vào design system; (c) `--keep %s:%s` và ghi ngoại lệ vào `open-questions.md`." % (t, m, why, m, t, m))
    warn = []
    for group in bl["gates"]["distinct"]:
        for m in modes:
            refs = [sem[t][m] for t in group]
            if len(set(refs)) < len(refs):
                warn.append("- %s (%s) trùng bậc: %s" % (", ".join("`%s`" % t for t in group), m, ", ".join(refs)))
    if warn:
        L += ["", "**Cảnh báo thứ bậc** (hai token khác vai trò trỏ cùng một bậc):", ""] + warn
    L += ["", "Miễn cổng: token `disabled` (WCAG 1.4.3 miễn cho thành phần vô hiệu), `border/default`, "
          "`border/subtle` (trang trí), nền và surface.", ""]

    L += ["## Text style", "",
          "| Vai trò | Font | Dùng cho |", "|---|---|---|"]
    for role, use in bl["text_styles"]["role_usage"].items():
        L.append("| %s | %s | %s |" % (role, fonts.get(role) or "— (bỏ qua)", use))
    L += ["", "%d style sẽ được tạo%s." % (len(styles), (", bỏ %d style vì chưa chọn font: %s" % (
        len(skipped), ", ".join("`%s`" % s for s in skipped))) if skipped else ""), ""]
    L += ["## Lệch so với FitAgain (cố ý)", ""] + ["- " + d for d in bl["deviations_from_fitagain"]] + [""]
    return "\n".join(L)


# ---------- emit ----------

def cmd_emit(a):
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    os.makedirs(a.out_dir, exist_ok=True)
    var_spec = {"code": spec["codeSyntax"], "collections": [
        {"name": c["name"], "modes": c["modes"], "hidden": c.get("hiddenFromPublishing", False),
         "vars": [[v["name"], v["type"], [v["values"][m] for m in c["modes"]], v["scopes"], v["description"]]
                  for v in c["variables"]]}
        for c in spec["collections"]]}
    text_spec = {"fonts": spec["fonts"], "styles": [
        [s["name"], s["role"], s["weight"], s["size"], s["lineHeight"], s["letterSpacing"], s["textCase"],
         s["decoration"]] for s in spec["textStyles"]]}
    found_spec = {"page": a.page, "replace": bool(a.replace), "title": spec["meta"].get("project") or ""}
    jobs = [("01-variables.js", var_spec), ("02-text-styles.js", text_spec), ("03-foundations.js", found_spec)]
    for fname, data in jobs:
        with open(os.path.join(TEMPLATES, fname), encoding="utf-8") as f:
            tpl = f.read()
        code = tpl.replace("__SPEC__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        path = os.path.join(a.out_dir, fname)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
        flag = "  ⚠️ vượt giới hạn use_figma %d ký tự" % USE_FIGMA_LIMIT if len(code) > USE_FIGMA_LIMIT else ""
        print("%s  %6d ký tự%s" % (path, len(code), flag))


def main():
    ap = argparse.ArgumentParser(description="Dựng Variables + Text style theo khung FitAgain")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="tạo tokens.json + báo cáo contrast")
    b.add_argument("--project", help="tên dự án, ghi vào báo cáo và tiêu đề page Foundations")
    b.add_argument("--primary", help="màu brand chính, vd #9F85FF; sinh ramp primary 50–900")
    b.add_argument("--ramp", action="append", metavar="TÊN=#HEX",
                   help="sinh lại một ramp có sẵn từ màu gốc, vd success=#22C55E")
    b.add_argument("--ramp-hex", action="append", metavar="TÊN=HEX,…",
                   help="nhập tay đủ 10 bậc cho một ramp, vd primary=#F3F0FF,…,#2A1964")
    b.add_argument("--add-ramp", action="append", metavar="TÊN=#HEX",
                   help="thêm ramp mới (chỉ vào Primitives), vd accent=#FF7A59")
    b.add_argument("--display-font", required=True, help="font nhận diện cho Display/Heading")
    b.add_argument("--body-font", required=True, help="font giao diện cho Body/Label/Caption…")
    b.add_argument("--mono-font", help="font mono cho Code/*; bỏ trống thì không tạo Code/*")
    b.add_argument("--modes", choices=["light", "light,dark"], default="light,dark")
    b.add_argument("--dimension", action="store_true", help="thêm collection Dimension (spacing, radius)")
    b.add_argument("--set", action="append", metavar="TOKEN[:MODE]=RAMP/BẬC",
                   help="trỏ một token Semantic sang bậc khác, vd text/secondary:Light=neutral/700 (token này không bị cổng dời nữa)")
    b.add_argument("--keep", action="append", metavar="TOKEN[:MODE]",
                   help="không tự dời token này dù chưa đạt contrast")
    b.add_argument("--no-fix", action="store_true", help="chỉ báo cáo, không tự dời bậc")
    b.add_argument("--out", required=True, help="đường dẫn tokens.json")
    b.add_argument("--report", help="đường dẫn báo cáo .md (bỏ trống thì in ra màn hình)")
    e = sub.add_parser("emit", help="sinh script use_figma từ tokens.json")
    e.add_argument("--spec", required=True)
    e.add_argument("--out-dir", required=True)
    e.add_argument("--page", default="02 Foundations", help="page chứa frame Design Tokens / Typography")
    e.add_argument("--replace", action="store_true",
                   help="cho phép xoá và dựng lại frame Design Tokens / Typography đã có")
    a = ap.parse_args()
    cmd_build(a) if a.cmd == "build" else cmd_emit(a)


if __name__ == "__main__":
    main()
