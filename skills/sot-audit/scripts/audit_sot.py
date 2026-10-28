# -*- coding: utf-8 -*-
"""
audit_sot.py: các phép kiểm tra máy móc trên một thư mục SoT. Chỉ đọc, không sửa file nào.

Cách dùng:
    python3 audit_sot.py "<thư mục dự án>" [--out report.md] [--json]

Kiểm tra:
  L1  Link tương đối trong .md trỏ tới file không tồn tại
  L2  File ngoài _archive/ trỏ link vào _archive/ (trừ link "vòng trước" giữa các vòng review)
  P1  Placeholder template chưa điền ({{...}} hoặc <...>)
  F1  Bảng Tính năng trong CLAUDE.md lệch với thư mục features/
  D1  Bảng quyết định: trạng thái lạ, thiếu "Ai chốt", thiếu "Phương án đã loại"
  Q1  Câu hỏi mở chưa ghi người cần trả lời (owner ghi ở heading mục cũng được tính)
  S0  Thiếu sources.md ở gốc dự án
  S1  sources.md: trạng thái không thuộc Hiện hành / Cũ / Còn mở
  I1  screen-inventory: frame chưa có AC hoặc ghi "Chưa có AC riêng"
  C1  Heading ghi số đếm "(N)" lệch số dòng của bảng ngay dưới
  N1  Tên file trong brief/ hoặc handoff/ sai quy ước ngày / version
  H1  File .html cũ hơn file .md cùng tên (quên sinh lại); bỏ qua .html là bản gốc (có ảnh nhúng)
  K1  Nghi lộ token / mật khẩu
Thư mục audits/ (báo cáo audit cũ) không được quét.
Chỉ dùng thư viện chuẩn của Python 3.8+.
"""
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "__pycache__", "_tools", "audits"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}|<[^<>\n]*\.\.\.[^<>\n]*>")
SECRET_RE = re.compile(r"(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}"
                       r"|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|(?i:password|passwd|api[_-]?key|secret)\s*[:=]\s*\S{6,})")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_")
DECISION_STATES = {"đã chốt", "đề xuất"}
NOTE_STATES = {"ghi chú"}
SOURCE_STATES = {"hiện hành", "cũ", "còn mở"}
OWNER_RE = re.compile(r"hỏi|chờ\s+\S+|\b(PM|PO|Dev|BE|FE|QA|Content|Designer|Lead|Owner)\b|—\s*\S+\s*—", re.I)
PREV_ROUND_RE = re.compile(r"vòng trước|review vòng|previous round", re.I)
GENERATOR_MARK = 'name="generator" content="sot-builder md_to_html"'

SEVERITY = {"L1": "Lỗi", "L2": "Cảnh báo", "P1": "Cảnh báo", "F1": "Lỗi", "D1": "Cảnh báo", "Q1": "Cảnh báo",
            "S0": "Cảnh báo", "S1": "Cảnh báo", "I1": "Thông tin", "C1": "Thông tin", "N1": "Thông tin",
            "H1": "Cảnh báo", "K1": "Lỗi"}
TITLE = {"L1": "Link chết", "L2": "Link trỏ vào _archive/", "P1": "Placeholder chưa điền",
         "F1": "Bảng Tính năng lệch thư mục", "D1": "Bảng quyết định thiếu thông tin",
         "Q1": "Câu hỏi mở chưa có người trả lời", "S0": "Thiếu sources.md",
         "S1": "Trạng thái nguồn không chuẩn", "I1": "Frame chưa có AC", "C1": "Số đếm lệch bảng",
         "N1": "Tên file sai quy ước", "H1": "Bản .html cũ hơn .md", "K1": "Nghi lộ token / mật khẩu"}


def strip_md(s):
    return re.sub(r"[*`_]", "", s).strip().lower()


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def read(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return None


def rel(root, path):
    return os.path.relpath(path, root).replace("\\", "/")


def tables(text):
    """Trả về list các bảng; mỗi bảng = (header_cells, [(line_no, cells), ...])."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s|:\-]+\|?\s*$", lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, [c.strip() for c in lines[j].strip().strip("|").split("|")]))
                j += 1
            out.append((head, rows))
            i = j
        else:
            i += 1
    return out


def col(head, *names):
    for idx, h in enumerate(head):
        if any(n in strip_md(h) for n in names):
            return idx
    return None


def audit(root):
    root = os.path.abspath(root)
    findings = []

    def add(code, path, line, msg):
        findings.append({"code": code, "file": rel(root, path), "line": line, "msg": msg})

    md_files = [p for p in iter_files(root) if p.lower().endswith(".md")]
    if os.path.exists(os.path.join(root, "_tools", "md_to_html.py")):
        html_tool = "`_tools/md_to_html.py`"
    else:
        html_tool = "script sinh HTML (dự án chưa có `_tools/md_to_html.py`: dùng bản trong skill sot-init)"
    if not os.path.isfile(os.path.join(root, "sources.md")):
        add("S0", os.path.join(root, "sources.md"), 0, "chưa có bảng nguồn (owner, trạng thái, link): DoD 2 chưa đạt")
    in_archive = lambda p: "/_archive/" in "/" + rel(root, p) or rel(root, p).startswith("_archive/")

    for path in md_files:
        text = read(path)
        if text is None:
            continue
        archived = in_archive(path)
        lines = text.split("\n")
        in_code = False
        for n, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if not archived:
                for m in LINK_RE.finditer(line):
                    target = m.group(1).split("#")[0]
                    if not target or re.match(r"^(https?:|mailto:|#)", target):
                        continue
                    full = os.path.normpath(os.path.join(os.path.dirname(path), target))
                    if not os.path.exists(full):
                        add("L1", path, n, "`%s` không tồn tại" % target)
                    elif "/_archive/" in "/" + rel(root, full) and not PREV_ROUND_RE.search(line):
                        add("L2", path, n, "trỏ vào `%s`" % rel(root, full))
                if os.path.basename(path) != "README.md" or os.path.dirname(path) != root:
                    for m in PLACEHOLDER_RE.finditer(line):
                        add("P1", path, n, "`%s`" % m.group(0)[:80])
            if SECRET_RE.search(line):
                add("K1", path, n, "dòng có chuỗi giống token / mật khẩu")

        if archived:
            continue
        base = os.path.basename(path)
        parent = os.path.basename(os.path.dirname(path))

        if base == "decisions.md":
            for head, rows in tables(text):
                c_state, c_who, c_alt = col(head, "trạng thái"), col(head, "ai chốt"), col(head, "đã loại")
                if c_who is None and c_alt is None:
                    continue
                for ln, cells in rows:
                    if c_state is not None and c_state < len(cells) and strip_md(cells[c_state]).startswith(tuple(NOTE_STATES)):
                        continue
                    if c_state is not None and c_state < len(cells) and not strip_md(cells[c_state]).startswith(tuple(DECISION_STATES)):
                        add("D1", path, ln, "trạng thái `%s` (chỉ dùng Đã chốt / Đề xuất)" % cells[c_state][:40])
                    if c_who is not None and (c_who >= len(cells) or not cells[c_who] or cells[c_who].startswith("<")):
                        add("D1", path, ln, "thiếu Ai chốt")
                    if c_alt is not None and (c_alt >= len(cells) or not cells[c_alt]):
                        add("D1", path, ln, "thiếu Phương án đã loại (ghi \"—\" nếu không có)")

        if base == "open-questions.md":
            section, h2_owner, h3_owner = "", False, False
            for n, line in enumerate(lines, 1):
                if line.startswith("## "):
                    section, h2_owner, h3_owner = line.lower(), bool(OWNER_RE.search(line[3:])), False
                elif line.startswith("### "):
                    h3_owner = bool(OWNER_RE.search(line[4:]))
                if "đã trả lời" in section:
                    continue
                if re.match(r"^\s*-\s*\[ \]", line) and not (h2_owner or h3_owner or OWNER_RE.search(line)):
                    add("Q1", path, n, "chưa ghi ai cần trả lời: `%s`" % line.strip()[:90])

        for n, line in enumerate(lines, 1):
            m = re.match(r"^#{2,4}\s.*\((\d+)\)\s*$", line)
            if not m:
                continue
            j = n
            while j < len(lines) and not lines[j].strip().startswith("|") and not lines[j].startswith("#"):
                j += 1
            if j + 1 < len(lines) and lines[j].strip().startswith("|") and re.match(r"^\s*\|[\s|:\-]+\|?\s*$", lines[j + 1]):
                k = j + 2
                while k < len(lines) and lines[k].strip().startswith("|"):
                    k += 1
                if k - (j + 2) != int(m.group(1)):
                    add("C1", path, n, "heading ghi %s nhưng bảng dưới có %d dòng" % (m.group(1), k - (j + 2)))

        if base == "sources.md" and os.path.dirname(path) == root:
            for head, rows in tables(text):
                c_state = col(head, "trạng thái")
                if c_state is None or col(head, "nguồn") is None or col(head, "owner") is None:
                    continue
                for ln, cells in rows:
                    if c_state < len(cells) and not strip_md(cells[c_state]).startswith(tuple(SOURCE_STATES)):
                        add("S1", path, ln, "trạng thái `%s`" % cells[c_state][:40])

        if base == "screen-inventory.md":
            for head, rows in tables(text):
                c_ac, c_node = col(head, "ac"), col(head, "node")
                if c_ac is None or c_node is None:
                    continue
                for ln, cells in rows:
                    v = cells[c_ac] if c_ac < len(cells) else ""
                    if not v or v in ("—", "-") or "chưa có ac" in v.lower():
                        add("I1", path, ln, "frame `%s` chưa có AC" % (cells[1] if len(cells) > 1 else "?")[:70])

        if parent in ("brief", "handoff") and base.lower() != "readme.md":
            if parent == "brief" and not DATE_PREFIX_RE.match(base):
                add("N1", path, 0, "thiếu tiền tố ngày `YYYY-MM-DD_`")
            if not re.search(r"-v\d+\.\d+\.\d+", base):
                add("N1", path, 0, "thiếu version dạng `-vX.Y.Z` (lấy theo Figma)")
            if re.search(r"spec-review.*-v\d+\.md$", base):
                add("N1", path, 0, "vòng review nên dùng hậu tố `-rN`, không dùng `-vN`")

        html = os.path.splitext(path)[0] + ".html"
        if os.path.exists(html) and os.path.getmtime(html) + 1 < os.path.getmtime(path):
            html_text = read(html) or ""
            # .html có ảnh nhúng mà không do md_to_html sinh: đó là bản gốc, .md chỉ là tóm tắt
            if GENERATOR_MARK in html_text or "data:image" not in html_text:
                add("H1", path, 0, "sinh lại bằng " + html_tool)

    claude = os.path.join(root, "CLAUDE.md")
    feat_dir = os.path.join(root, "features")
    if os.path.isfile(claude) and os.path.isdir(feat_dir):
        text = read(claude) or ""
        listed = set(re.findall(r"features/([a-z0-9][a-z0-9-]*)/", text))
        actual = {d for d in os.listdir(feat_dir) if os.path.isdir(os.path.join(feat_dir, d)) and not d.startswith("_")}
        for d in sorted(actual - listed):
            add("F1", claude, 0, "thư mục `features/%s/` chưa có trong bảng Tính năng" % d)
        for d in sorted(listed - actual):
            add("F1", claude, 0, "bảng Tính năng có `%s` nhưng không có thư mục" % d)
        for d in sorted(actual):
            f_claude = os.path.join(feat_dir, d, "CLAUDE.md")
            inv = os.path.join(feat_dir, d, "design", "screen-inventory.md")
            if not (os.path.isfile(f_claude) and os.path.isfile(inv)):
                continue
            said = set(re.findall(r"(\d+)\s+frame", read(f_claude) or "", re.I))
            m = re.search(r"^#{2,4}\s.*frame.*\((\d+)\)\s*$", read(inv) or "", re.I | re.M)
            if said and m and m.group(1) not in said:
                add("C1", f_claude, 0, "ghi %s frame, screen-inventory ghi %s" % ("/".join(sorted(said)), m.group(1)))

    for path in iter_files(root):
        if os.path.basename(path).lower() in (".env",) or path.lower().endswith(".env"):
            add("K1", path, 0, "file .env nằm trong SoT")

    return findings


def report(root, findings):
    order = ["Lỗi", "Cảnh báo", "Thông tin"]
    counts = {s: sum(1 for f in findings if SEVERITY[f["code"]] == s) for s in order}
    out = ["# Kiểm tra máy móc SoT", "",
           "Thư mục: `%s`" % os.path.abspath(root), "",
           "| Mức | Số mục |", "|---|---|"] + ["| %s | %d |" % (s, counts[s]) for s in order] + [""]
    for code in sorted(SEVERITY, key=lambda c: (order.index(SEVERITY[c]), c)):
        items = [f for f in findings if f["code"] == code]
        if not items:
            continue
        out.append("## %s %s: %s (%d)" % (code, TITLE[code], SEVERITY[code], len(items)))
        out.append("")
        for f in items[:60]:
            loc = f["file"] + (":%d" % f["line"] if f["line"] else "")
            out.append("- `%s` — %s" % (loc, f["msg"]))
        if len(items) > 60:
            out.append("- … và %d mục khác" % (len(items) - 60))
        out.append("")
    if not findings:
        out.append("Không phát hiện vấn đề máy móc nào.")
    return "\n".join(out)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    root = argv[0]
    findings = audit(root)
    if "--json" in argv:
        print(json.dumps(findings, ensure_ascii=False, indent=1))
        return 0
    text = report(root, findings)
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print(out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
