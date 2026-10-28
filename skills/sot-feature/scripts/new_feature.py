# -*- coding: utf-8 -*-
"""
new_feature.py: dựng khung một tính năng trong dự án SoT và đăng ký vào bảng Tính năng của CLAUDE.md dự án.

Cách dùng:
    python3 new_feature.py --project "<thư mục dự án>" --name <kebab-case> [--version 1.0.0] [--dry-run]

- Dự án phải có CLAUDE.md (tên dự án lấy từ dòng "# " đầu tiên).
- Không ghi đè: nếu features/<name>/ đã tồn tại thì dừng.
- Thêm một dòng "| <name> | features/<name>/ | khung |" ngay trước marker <!-- FEATURES --> trong CLAUDE.md dự án.
Chỉ dùng thư viện chuẩn của Python 3.8+.
"""
import argparse
import datetime
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.normpath(os.path.join(HERE, "..", "assets", "feature"))
MARKER = "<!-- FEATURES -->"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--name", required=True, help="kebab-case, ví dụ water-tracker")
    ap.add_argument("--version", default="1.0.0", help="version theo Figma, ví dụ 1.0.1")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", a.name):
        sys.exit("Tên tính năng phải là kebab-case tiếng Anh, ví dụ water-tracker: " + a.name)

    project = os.path.expanduser(a.project)
    project_md = os.path.join(project, "CLAUDE.md")
    if not os.path.isfile(project_md):
        sys.exit("Không thấy CLAUDE.md trong " + project + ". Đây có phải thư mục dự án SoT không?")
    with open(project_md, encoding="utf-8") as f:
        project_text = f.read()
    heading = next((l[2:].strip() for l in project_text.splitlines() if l.startswith("# ")), os.path.basename(project))

    dest = os.path.join(project, "features", a.name)
    if os.path.exists(dest):
        sys.exit("Đã tồn tại, không ghi đè: " + dest)

    values = {
        "FEATURE_NAME": a.name,
        "PROJECT_NAME": heading,
        "DATE": datetime.date.today().isoformat(),
        "VERSION": a.version,
    }
    files = []
    for dirpath, _, filenames in os.walk(TEMPLATE):
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            files.append((src, os.path.join(dest, os.path.relpath(src, TEMPLATE))))

    if a.dry_run:
        print("Sẽ tạo:", dest)
        for _, d in files:
            print("  " + os.path.relpath(d, dest))
        return

    for src, dst in files:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if src.endswith(".md"):
            with open(src, encoding="utf-8") as f:
                text = f.read()
            for k, v in values.items():
                text = text.replace("{{" + k + "}}", v)
            with open(dst, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        else:
            shutil.copy2(src, dst)

    if MARKER in project_text:
        row = "| %s | features/%s/ | khung |" % (a.name, a.name)
        project_text = project_text.replace(MARKER, row + "\n" + MARKER)
        with open(project_md, "w", encoding="utf-8", newline="\n") as f:
            f.write(project_text)
    else:
        print("Cảnh báo: không thấy " + MARKER + " trong CLAUDE.md dự án, hãy thêm dòng tính năng bằng tay.")

    print("Đã tạo:", dest)


if __name__ == "__main__":
    main()
