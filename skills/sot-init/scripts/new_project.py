# -*- coding: utf-8 -*-
"""
new_project.py: dựng khung SoT cho một dự án mới từ assets/project của skill sot-init.

Cách dùng:
    python3 new_project.py --dest "<thư mục cha>" --name "<Tên dự án>" [--folder "<tên thư mục>"] \
        [--set KEY=VALUE ...] [--dry-run]

Ví dụ:
    python3 new_project.py --dest ~/Projects --name "Meditation App" \
        --set PLATFORM="iOS" --set FIGMA_URL="https://www.figma.com/design/abc"

- Không ghi đè: nếu thư mục đích đã tồn tại thì dừng.
- Thay {{PROJECT_NAME}}, {{DATE}} và mọi {{KEY}} truyền qua --set trong file .md.
- Placeholder chưa có giá trị được giữ nguyên dạng {{KEY}} để skill điền sau; in ra danh sách còn thiếu.
Chỉ dùng thư viện chuẩn của Python 3.8+.
"""
import argparse
import datetime
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.normpath(os.path.join(HERE, "..", "assets", "project"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True, help="thư mục cha sẽ chứa dự án")
    ap.add_argument("--name", required=True, help="tên hiển thị của dự án")
    ap.add_argument("--folder", help="tên thư mục dự án (mặc định = --name)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    values = {"PROJECT_NAME": a.name, "DATE": datetime.date.today().isoformat()}
    for kv in a.set:
        if "=" not in kv:
            sys.exit("--set cần dạng KEY=VALUE: " + kv)
        k, v = kv.split("=", 1)
        values[k.strip().upper()] = v.strip()

    dest = os.path.join(os.path.expanduser(a.dest), a.folder or a.name)
    if os.path.exists(dest):
        sys.exit("Đã tồn tại, không ghi đè: " + dest)

    files = []
    for dirpath, dirnames, filenames in os.walk(TEMPLATE):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            files.append((src, os.path.join(dest, os.path.relpath(src, TEMPLATE))))

    if a.dry_run:
        print("Sẽ tạo:", dest)
        for _, d in files:
            print("  " + os.path.relpath(d, dest))
        return

    missing = set()
    angle = {}
    for src, dst in files:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if src.endswith(".md"):
            with open(src, encoding="utf-8") as f:
                text = f.read()
            for k, v in values.items():
                text = text.replace("{{" + k + "}}", v)
            missing.update(re.findall(r"\{\{([A-Z_]+)\}\}", text))
            found = angle_placeholders(text)
            if found:
                angle[os.path.relpath(dst, dest).replace("\\", "/")] = found
            with open(dst, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        else:
            shutil.copy2(src, dst)

    print("Đã tạo:", dest)
    if missing:
        print("Placeholder {{...}} còn trống (skill cần điền):", ", ".join(sorted(missing)))
    if angle:
        print("Placeholder <...> còn trống (điền từ phỏng vấn / nguồn, chưa biết thì ghi \"Còn mở: <câu hỏi>\"):")
        for path in sorted(angle):
            print("  %s:%s" % (path, ", ".join("%d %s" % (ln, ph) for ln, ph in angle[path])))


HTML_TAGS = {"br", "details", "summary", "sup", "sub", "kbd", "b", "i", "u", "em", "strong", "code", "p", "span", "div"}


def angle_placeholders(text):
    """Placeholder dạng <...> ngoài code block / code span. Bỏ qua thẻ HTML, comment và
    ví dụ quy ước viết hoa như <Flow>."""
    out, in_code = [], False
    for n, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for m in re.finditer(r"<([^<>\n]{1,80})>", re.sub(r"`[^`]*`", "", line)):
            inner = m.group(1).strip()
            word = re.split(r"[\s/>]", inner)[0].lower()
            if inner[:1] in "!/" or inner[:1].isupper() or word in HTML_TAGS or inner.startswith("http"):
                continue
            out.append((n, "<%s>" % inner))
    return out


if __name__ == "__main__":
    main()
