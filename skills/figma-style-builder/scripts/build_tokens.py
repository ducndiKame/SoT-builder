# -*- coding: utf-8 -*-
"""
build_tokens.py: dựng bộ token + text style theo khung FitAgain cho một dự án mới, rồi sinh script use_figma.

Hai lệnh:
  build  Đọc style-config.json (câu trả lời của designer: màu primary, có secondary không, 1–3 font,
         phân vai font, quy tắc dùng font…), tạo tokens.json + báo cáo contrast.
  emit   Đọc tokens.json, sinh 3 file .js để dán vào use_figma:
         01-variables.js, 02-text-styles.js, 03-foundations.js

Ví dụ:
  py build_tokens.py build --config design-system/style-config.json \
      --out design-system/tokens.json --report design-system/tokens-report.md
  py build_tokens.py emit --spec design-system/tokens.json --out-dir <scratchpad>/figma

Mẫu config: ../assets/style-config.example.json

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

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")  # console Windows (cp1252) không in được tiếng Việt


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


WEIGHT_VALUE = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}


def strip_notes(x):
    """Bỏ các khoá chú thích ('_…') của file config."""
    if isinstance(x, dict):
        return {k: strip_notes(v) for k, v in x.items() if not k.startswith("_")}
    if isinstance(x, list):
        return [strip_notes(v) for v in x]
    return x


def check_hex(val, where):
    vals = val if isinstance(val, list) else [val]
    for h in vals:
        try:
            hex_to_rgb(h)
        except (ValueError, AttributeError):
            sys.exit("%s: mã màu không hợp lệ: %r" % (where, h))


def make_ramp(name, val, steps, profile, ramps, generated, order, where):
    """val là một mã hex (sinh ramp) hoặc danh sách đủ số bậc (nhập tay)."""
    check_hex(val, where)
    if isinstance(val, list):
        if len(val) != len(steps):
            sys.exit("%s: cần đúng %d mã màu cho ramp %s" % (where, len(steps), name))
        ramps[name] = [rgb_to_hex(hex_to_rgb(h)) for h in val]
        generated.pop(name, None)
    else:
        ramps[name], k = generate_ramp(val, profile)
        generated[name] = (val.upper(), steps[k])
    if name not in order:
        order.append(name)


def merge_rows(rows, new_rows):
    """Thêm token mới ngay sau token cuối cùng cùng nhóm; token trùng tên thì thay giá trị tại chỗ."""
    names = [r[0] for r in rows]
    for r in new_rows:
        if r[0] in names:
            rows[names.index(r[0])] = list(r)
        else:
            group = r[0].split("/")[0]
            idx = max((i for i, n in enumerate(names) if n.split("/")[0] == group), default=len(rows) - 1)
            rows.insert(idx + 1, list(r))
        names = [x[0] for x in rows]


def merge_gates(gates, new_gates):
    for g in new_gates:
        gates[:] = [x for x in gates if (x[0], x[1]) != (g[0], g[1])] + [list(g)]


def resolve_font(name, assign):
    keys = [k for k in assign if name == k or name.startswith(k + "/")]
    if not keys:
        return False
    return assign[max(keys, key=len)]


def cmd_build(a):
    with open(BASELINE, encoding="utf-8") as f:
        bl = json.load(f)
    with open(a.config, encoding="utf-8") as f:
        cfg = strip_notes(json.load(f))
    steps = bl["steps"]
    ramps = {k: list(v) for k, v in bl["ramps"].items()}
    profile = bl["ramps"][bl["ramp_profile"]]
    generated, order = {}, list(bl["ramp_order"])
    colors = cfg.get("colors") or {}

    # --- màu ---
    if not colors.get("primary"):
        sys.exit("style-config: thiếu colors.primary (mã hex hoặc 10 mã)")
    make_ramp("primary", colors["primary"], steps, profile, ramps, generated, order, "colors.primary")
    for name, val in (colors.get("status") or {}).items():
        if name not in ("success", "warning", "error", "info"):
            sys.exit("colors.status: chỉ nhận success, warning, error, info (có %s)" % name)
        make_ramp(name, val, steps, profile, ramps, generated, order, "colors.status." + name)
    for name, val in (colors.get("extra") or {}).items():
        make_ramp(name, val, steps, profile, ramps, generated, order, "colors.extra." + name)

    rows = [list(r) for r in bl["semantic"]]
    gates = [list(g) for g in bl["gates"]["list"]]
    distinct = [list(d) for d in bl["gates"]["distinct"]]
    sec, sec_tokens = colors.get("secondary"), set()
    if sec:
        bsec = bl["secondary"]
        if not sec.get("hex"):
            sys.exit("colors.secondary: thiếu hex (hoặc đặt secondary = null nếu dự án không có màu secondary)")
        use = sec.get("use", "accent")
        if use not in ("accent", "accent+button"):
            sys.exit("colors.secondary.use: 'accent' hoặc 'accent+button' (có %r)" % use)
        make_ramp(bsec["ramp"], sec["hex"], steps, profile, ramps, generated, order, "colors.secondary.hex")
        for part in ["accent"] + (["button"] if use == "accent+button" else []):
            merge_rows(rows, bsec[part]["semantic"])
            merge_gates(gates, bsec[part]["gates"])
            distinct += bsec[part]["distinct"]
            sec_tokens |= {r[0] for r in bsec[part]["semantic"]}

    modes = ["Light", "Dark"] if cfg.get("darkMode", True) else ["Light"]
    pal = Palette(steps, ramps, bl["base"])
    sem = {n: {"Light": l, "Dark": d} for n, l, d, _ in rows}
    on_dark = bl["on_color"]["dark"]
    ons = {"primary": colors.get("primaryOn", "white"), "secondary": (sec or {}).get("on", "white")}
    for which, on in ons.items():
        if on not in ("white", "dark"):
            sys.exit("Màu chữ trên nền %s chỉ nhận 'white' hoặc 'dark' (có %r)" % (which, on))
        if on == "dark":
            for tok in bl["on_color"][which]:
                if tok in sem and (which == "primary" or tok in sec_tokens):
                    sem[tok] = {"Light": on_dark, "Dark": on_dark}
    anchor_changes = []
    anchor = strip_notes(bl["anchor"])
    for ramp_name, toks in anchor.items():
        if ramp_name not in generated:
            continue
        k = steps.index(generated[ramp_name][1])
        delta = k - steps.index(anchor["step"])
        if not delta or not isinstance(toks, list):
            continue
        for tok in toks:
            for m in (modes if tok in sem else []):
                ref = sem[tok][m]
                if not ref.startswith(ramp_name + "/"):
                    continue
                i = max(0, min(len(steps) - 1, steps.index(int(ref.split("/")[1])) + delta))
                new = "%s/%d" % (ramp_name, steps[i])
                if new != ref:
                    anchor_changes.append((tok, m, ref, new, "neo theo màu brand (bậc %d)" % steps[k]))
                    sem[tok][m] = new
    baseline_sem = {n: dict(v) for n, v in sem.items()}
    keep = set(cfg.get("keep") or [])
    for key, ref in (cfg.get("set") or {}).items():
        tok, _, only = key.partition(":")
        if tok not in sem:
            sys.exit("set: không có token " + tok)
        try:
            pal.hex(ref)
        except (KeyError, ValueError):
            sys.exit("set: không có màu " + ref)
        for m in ([only] if only else modes):
            sem[tok][m] = ref
        keep.add(key)
    desc = {r[0]: r[3] for r in rows}
    changes, blocked = run_gates(pal, sem, modes, gates, keep, cfg.get("fix", True), distinct)
    changes = anchor_changes + changes

    rules = bl["scopes"]
    prim_vars = [{"name": n, "type": "COLOR", "values": {"Default": h}, "scopes": [], "description": ""}
                 for n, h in bl["base"].items()]
    for r in order:
        for s, h in zip(steps, ramps[r]):
            prim_vars.append({"name": "%s/%d" % (r, s), "type": "COLOR", "values": {"Default": h},
                              "scopes": [], "description": ""})
    sem_vars = [{"name": n, "type": "COLOR",
                 "values": {m: "@Primitives:" + sem[n][m] for m in modes},
                 "scopes": scope_for(n, rules), "description": desc[n]} for n, _, _, _ in rows]
    collections = [
        {"name": "Primitives", "modes": ["Default"], "hiddenFromPublishing": True, "variables": prim_vars},
        {"name": "Semantic", "modes": modes, "hiddenFromPublishing": False, "variables": sem_vars},
    ]
    if cfg.get("dimension", True):
        dim = bl["dimension"]
        dvars = [{"name": "spacing/%d" % v, "type": "FLOAT", "values": {"Default": v},
                  "scopes": scope_for("spacing/x", rules), "description": ""} for v in dim["spacing"]]
        dvars += [{"name": "radius/" + n, "type": "FLOAT", "values": {"Default": v},
                   "scopes": scope_for("radius/x", rules), "description": ""} for n, v in dim["radius"]]
        collections.append({"name": "Dimension", "modes": ["Default"], "hiddenFromPublishing": False,
                            "variables": dvars})

    # --- font ---
    fcfg = cfg.get("fonts") or {}
    fams = fcfg.get("families") or []
    if not 1 <= len(fams) <= 3:
        sys.exit("fonts.families cần 1–3 font (có %d)" % len(fams))
    assign, preset_used = fcfg.get("assign"), False
    if not assign:
        preset = strip_notes(bl["text_styles"]["font_presets"])[str(len(fams))]
        assign = {g: (fams[int(v[1]) - 1] if v else None) for g, v in preset.items()}
        preset_used = True
    for k, v in assign.items():
        if v is not None and v not in fams:
            sys.exit("fonts.assign: %s trỏ tới font %r, không có trong fonts.families" % (k, v))
    weights = fcfg.get("weights") or {}
    for fam, ws in weights.items():
        if fam not in fams:
            sys.exit("fonts.weights: font %r không có trong fonts.families" % fam)
        bad = [w for w in ws if w not in WEIGHT_VALUE]
        if bad or not ws:
            sys.exit("fonts.weights.%s: chỉ nhận %s (có %s)" % (fam, ", ".join(WEIGHT_VALUE), ws))
    unassigned = sorted({n.split("/")[0] for n, *_ in bl["text_styles"]["list"] if resolve_font(n, assign) is False})
    if unassigned:
        sys.exit("fonts.assign chưa gán font (hoặc null) cho nhóm: " + ", ".join(unassigned))

    group_desc = strip_notes(bl["text_styles"]["groups"])
    base_list = bl["text_styles"]["list"]
    # Biến thể theo weight = cùng nhánh có style khác cùng cỡ, khác weight (Body/Medium/Regular · …/Bold).
    # Link/Medium, Display/Medium là bậc cỡ chữ, không phải biến thể weight.
    variants = {n for n, w, size, *_ in base_list
                if any(o != n and o.rsplit("/", 1)[0] == n.rsplit("/", 1)[0] and os_ == size and ow != w
                       for o, ow, os_, *_ in base_list)}
    styles, skipped, dropped, remapped = [], [], [], []
    for n, w, size, lh, ls, case, dec in base_list:
        fam = resolve_font(n, assign)
        if fam is None:
            skipped.append(n)
            continue
        allowed = weights.get(fam)
        if allowed and w not in allowed:
            if n in variants:
                dropped.append((n, fam, w))
                continue
            nw = min(allowed, key=lambda x: (abs(WEIGHT_VALUE[x] - WEIGHT_VALUE[w]), -WEIGHT_VALUE[x]))
            remapped.append((n, fam, w, nw))
            w = nw
        styles.append({"name": n, "font": fam, "weight": w, "size": size, "lineHeight": lh,
                       "letterSpacing": ls, "textCase": case, "decoration": dec,
                       "description": group_desc.get(n.split("/")[0], "")})
    kept_parents = {s["name"].rsplit("/", 1)[0] for s in styles}
    emptied = sorted({n.rsplit("/", 1)[0] for n, _, _ in dropped} - kept_parents)
    unused = [f for f in fams if f not in {s["font"] for s in styles}]
    font_rules = list(fcfg.get("rules") or [])

    spec = {
        "meta": {"generator": "figma-style-builder", "baseline": "FitAgain 2026-11-04",
                 "project": cfg.get("project", ""), "created": datetime.date.today().isoformat(),
                 "config": cfg},
        "fonts": {"families": fams, "assign": assign, "weights": weights, "rules": font_rules},
        "codeSyntax": {k: v for k, v in bl["code_syntax"].items() if not k.startswith("_")},
        "collections": collections,
        "textStyles": styles,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        f.write("\n")

    ctx = dict(cfg=cfg, bl=bl, pal=pal, order=order, generated=generated, baseline_sem=baseline_sem, sem=sem,
               modes=modes, gates=gates, keep=keep, changes=changes, blocked=blocked, distinct=distinct,
               styles=styles, skipped=skipped, dropped=dropped, remapped=remapped, emptied=emptied,
               unused=unused, fams=fams, assign=assign, preset_used=preset_used, weights=weights,
               font_rules=font_rules, ons=ons, sec=sec, sec_tokens=sec_tokens)
    report = build_report(ctx)
    if a.report:
        with open(a.report, "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
    fails = sum(1 for line in report.splitlines() if line.startswith("| ") and "❌" in line)
    print("Đã ghi: " + a.out + ((" + " + a.report) if a.report else ""))
    print("Biến: %d Primitives · %d Semantic (%s)%s · Text style: %d (bỏ %d)" % (
        len(prim_vars), len(sem_vars), "/".join(modes),
        (" · %d Dimension" % len(collections[2]["variables"])) if len(collections) > 2 else "",
        len(styles), len(skipped) + len(dropped)))
    print("Font: %s · Secondary: %s" % (" + ".join(fams), (sec or {}).get("use", "không có")))
    print("Dời bậc so với khung: %d · Cặp contrast chưa đạt: %d · Cần designer quyết: %d" % (
        len(changes), fails, len(blocked)))
    if not a.report:
        print(report)


def build_report(c):
    cfg, bl, pal, sem, modes, keep = c["cfg"], c["bl"], c["pal"], c["sem"], c["modes"], c["keep"]
    sec, ons = c["sec"], c["ons"]
    project = cfg.get("project") or "dự án mới"
    L = ["# Báo cáo token — %s" % project, "",
         "Sinh bởi `figma-style-builder` ngày %s, khung FitAgain, từ `style-config.json`. Đọc mục **Cấu hình**, "
         "**Dời bậc** và **Cần designer quyết** trước khi ghi vào Figma." % datetime.date.today().isoformat(), ""]

    # cấu hình
    prim = cfg["colors"]["primary"]
    if sec:
        sec_txt = "`%s`, dùng cho %s, chữ trên nền: %s" % (
            sec["hex"] if isinstance(sec["hex"], str) else "ramp nhập tay",
            "điểm nhấn (nhóm `accent`)" if sec.get("use", "accent") == "accent"
            else "điểm nhấn (nhóm `accent`) + nút phụ (`action/secondary/*`)", ons["secondary"])
    else:
        sec_txt = "không có (nhóm `accent` không được tạo, nút phụ dùng xám)"
    L += ["## Cấu hình (câu trả lời của designer)", "", "| Mục | Giá trị |", "|---|---|",
          "| Primary | `%s`, chữ trên nền: %s |" % (prim if isinstance(prim, str) else "ramp nhập tay", ons["primary"]),
          "| Secondary | %s |" % sec_txt,
          "| Màu trạng thái riêng | %s |" % (", ".join(sorted((cfg["colors"].get("status") or {}))) or "không, dùng ramp của khung"),
          "| Ramp thêm | %s |" % (", ".join(sorted((cfg["colors"].get("extra") or {}))) or "không"),
          "| Số font | %d: %s |" % (len(c["fams"]), ", ".join(c["fams"])),
          "| Dark mode | %s |" % ("có" if "Dark" in modes else "không"),
          "| Dimension (spacing, radius) | %s |" % ("có" if cfg.get("dimension", True) else "không"), ""]

    L += ["## Ramp", "", "| Ramp | Nguồn | " + " | ".join(str(s) for s in pal.steps) + " |",
          "|---|---|" + "---|" * len(pal.steps)]
    for r in c["order"]:
        src = ("sinh từ %s (đặt ở bậc %d)" % c["generated"][r]) if r in c["generated"] else "khung FitAgain" \
            if r in bl["ramps"] and pal.ramps[r] == bl["ramps"][r] else "nhập tay"
        L.append("| %s | %s | %s |" % (r, src, " | ".join("`%s`" % h for h in pal.ramps[r])))
    dark = pal.hex(bl["on_color"]["dark"])
    brand = [("primary", "primaryOn")] + ([("secondary", "secondary.on")] if sec else [])
    L += ["", "Contrast chữ trên từng bậc của ramp brand (nút có chữ cần ≥ 4.5):", "",
          "| Ramp | Chữ | " + " | ".join(str(s) for s in pal.steps) + " |", "|---|---|" + "---|" * len(pal.steps)]
    for r, _ in brand:
        for label, fg in (("trắng", "#FFFFFF"), ("neutral/900", dark)):
            L.append("| %s | %s | %s |" % (r, label, " | ".join("%.2f" % contrast(fg, h) for h in pal.ramps[r])))
    for r, key in brand:
        if r in c["generated"]:
            seed = c["generated"][r][0]
            on = ons["primary" if r == "primary" else "secondary"]
            if on == "white" and contrast("#FFFFFF", seed) < 4.5 <= contrast(dark, seed):
                L += ["", "**Gợi ý:** `%s` là màu sáng, chữ trắng trên nó chỉ đạt %.2f:1 nên cổng sẽ dời nền nút sang bậc "
                      "tối hơn (nút không còn đúng màu brand). Chữ neutral/900 đạt %.2f:1. Muốn giữ đúng màu brand trên "
                      "nút thì đặt `%s: \"dark\"` trong config." % (seed, contrast("#FFFFFF", seed),
                                                                    contrast(dark, seed), key)]
    L.append("")

    L += ["## Dời bậc so với khung FitAgain", ""]
    if c["changes"]:
        L += ["| Token | Mode | Khung | Sau cổng contrast | Lý do |", "|---|---|---|---|---|"]
        for t, m, old, new, why in c["changes"]:
            L.append("| `%s` | %s | `%s` | `%s` | %s |" % (t, m, old, new, why))
        L += ["", "Muốn giữ màu của khung cho token nào thì thêm `\"<token>\"` (hoặc `\"<token>:Dark\"`) vào `keep` "
              "trong `style-config.json`, chạy lại `build`, và ghi ngoại lệ vào `open-questions.md`.", ""]
    else:
        L += ["Không có token nào phải dời.", ""]

    L += ["## Contrast (WCAG 2.2 AA)", "", "| Cặp | Mode | Đo được | Ngưỡng | Kết quả |", "|---|---|---|---|---|"]
    for fg, bg, need, _, _ in c["gates"]:
        for m in modes:
            r = contrast(pal.hex(sem[fg][m]), pal.hex(sem[bg][m]))
            mark = "✅" if r >= need else ("❌ giữ theo keep" if (fg in keep or bg in keep) else "❌")
            L.append("| `%s` / `%s` | %s | %.2f | %.1f | %s |" % (fg, bg, m, r, need, mark))
    if c["blocked"]:
        L += ["", "**Cần designer quyết** (cổng không tự sửa được mà không phá thứ bậc):", ""]
        for (t, m), why in c["blocked"].items():
            L.append("- `%s` (%s): %s. Chọn một: (a) dời token cùng nhóm thêm một bậc: thêm "
                     "`\"<token>:%s\": \"<ramp/bậc>\"` vào `set` rồi chạy lại; (b) giới hạn token này ở nền đạt chuẩn và "
                     "ghi luật vào design system; (c) thêm `\"%s:%s\"` vào `keep` và ghi ngoại lệ vào `open-questions.md`."
                     % (t, m, why, m, t, m))
    warn = []
    for group in c["distinct"]:
        for m in modes:
            refs = [sem[t][m] for t in group]
            if len(set(refs)) < len(refs):
                warn.append("- %s (%s) trùng bậc: %s" % (", ".join("`%s`" % t for t in group), m, ", ".join(refs)))
    if warn:
        L += ["", "**Cảnh báo thứ bậc** (hai token khác vai trò trỏ cùng một bậc):", ""] + warn
    L += ["", "Miễn cổng: token `disabled` (WCAG 1.4.3 miễn cho thành phần vô hiệu), `border/default`, "
          "`border/subtle` (trang trí), nền và surface.", ""]

    # text style
    L += ["## Text style", ""]
    if c["preset_used"]:
        L += ["⚠️ `fonts.assign` để trống nên đang dùng phân vai mặc định cho %d font. Hỏi designer xác nhận trước khi "
              "ghi vào Figma." % len(c["fams"]), ""]
    groups = [g for g in strip_notes(bl["text_styles"]["groups"])]
    L += ["| Nhóm | Font | Số style | Dùng cho |", "|---|---|---|---|"]
    by_group = {}
    for s in c["styles"]:
        by_group.setdefault(s["name"].split("/")[0], []).append(s)
    for g in groups:
        items = by_group.get(g, [])
        fonts = sorted({s["font"] for s in items})
        if len(fonts) > 1:
            font_txt = "; ".join("%s (%s)" % (f, ", ".join(s["name"].split("/", 1)[1] for s in items if s["font"] == f))
                                 for f in fonts)
        else:
            font_txt = fonts[0] if fonts else "— không tạo"
        L.append("| %s | %s | %d | %s |" % (g, font_txt, len(items), bl["text_styles"]["groups"][g]))
    L += ["", "Tổng: %d style." % len(c["styles"]), ""]
    if c["weights"]:
        L += ["Weight được dùng: " + "; ".join("%s: %s" % (f, ", ".join(ws)) for f, ws in c["weights"].items()) + ".", ""]
    if c["dropped"]:
        L += ["Bỏ vì font không dùng weight đó: " + ", ".join("`%s` (%s %s)" % d for d in c["dropped"]) + ".", ""]
    if c["remapped"]:
        L += ["Đổi weight: " + ", ".join("`%s` %s → %s" % (n, w, nw) for n, _, w, nw in c["remapped"]) + ".", ""]
    if c["emptied"]:
        L += ["⚠️ Nhóm mất hết style sau khi lọc weight: " + ", ".join("`%s`" % e for e in c["emptied"])
              + ". Hỏi designer có cần nhóm này không; nếu cần thì thêm weight vào `fonts.weights`.", ""]
    if c["unused"]:
        L += ["⚠️ Font khai báo nhưng không được gán cho nhóm nào: " + ", ".join(c["unused"]) + ".", ""]
    L += ["**Quy tắc dùng font của dự án:**", ""]
    L += (["- " + r for r in c["font_rules"]] if c["font_rules"] else ["- (designer không đặt quy tắc riêng)"]) + [""]
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
    text_spec = {"styles": [
        [s["name"], s["font"], s["weight"], s["size"], s["lineHeight"], s["letterSpacing"], s["textCase"],
         s["decoration"], s.get("description", "")] for s in spec["textStyles"]]}
    usage = {}
    for s in spec["textStyles"]:
        g = s["name"].split("/")[0]
        groups = usage.setdefault(s["font"], [])
        if g not in groups:
            groups.append(g)
    found_spec = {"page": a.page, "replace": bool(a.replace), "title": spec["meta"].get("project") or "",
                  "fonts": [[f, usage.get(f, [])] for f in spec["fonts"]["families"]],
                  "rules": spec["fonts"].get("rules", [])}
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
    b = sub.add_parser("build", help="đọc style-config.json, tạo tokens.json + báo cáo contrast")
    b.add_argument("--config", required=True,
                   help="style-config.json: câu trả lời của designer (mẫu: assets/style-config.example.json)")
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
