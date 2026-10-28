# -*- coding: utf-8 -*-
"""
install.py: cài các skill của SoT builder vào ~/.claude/skills (dùng được ở mọi dự án trên máy).

Cách dùng (chạy trong thư mục SoT-builder):
    python3 install.py                 # cài / cập nhật tất cả skill          (macOS)
    py install.py                      # như trên                             (Windows)
    python3 install.py --list          # xem skill nào đã cài, bản nào cũ
    python3 install.py --only sot-init,sot-sync
    python3 install.py --dry-run       # chỉ in ra sẽ làm gì
    python3 install.py --uninstall     # gỡ các skill của SoT builder

Skill đã có sẵn trên máy mà khác bản trong repo sẽ được sao lưu vào
~/.claude/skills/.backup-sot-builder/<ngày-giờ>/ trước khi ghi đè.
Chỉ dùng thư viện chuẩn của Python 3.8+.
"""
import argparse
import datetime
import filecmp
import os
import shutil
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(REPO, "skills")
DEST = os.path.join(os.path.expanduser("~"), ".claude", "skills")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def skill_names():
    return sorted(d for d in os.listdir(SRC) if os.path.isfile(os.path.join(SRC, d, "SKILL.md")))


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__", ".DS_Store"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(os.path.join(a, d), os.path.join(b, d)) for d in cmp.common_dirs)


def main():
    ap = argparse.ArgumentParser(description="Cài skill SoT builder vào ~/.claude/skills")
    ap.add_argument("--only", help="danh sách skill, cách nhau bằng dấu phẩy")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()

    names = skill_names()
    if a.only:
        wanted = [n.strip() for n in a.only.split(",") if n.strip()]
        unknown = [n for n in wanted if n not in names]
        if unknown:
            sys.exit("Không có skill: " + ", ".join(unknown) + "\nCó: " + ", ".join(names))
        names = wanted

    if a.list:
        for n in names:
            target = os.path.join(DEST, n)
            if not os.path.isdir(target):
                state = "chưa cài"
            elif same_tree(os.path.join(SRC, n), target):
                state = "đã cài, mới nhất"
            else:
                state = "đã cài, KHÁC bản trong repo (chạy install.py để cập nhật)"
            print("%-24s %s" % (n, state))
        return

    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_root = os.path.join(DEST, ".backup-sot-builder", stamp)
    os.makedirs(DEST, exist_ok=True)
    installed, updated, unchanged, removed, backed_up = [], [], [], [], []

    for n in names:
        src, target = os.path.join(SRC, n), os.path.join(DEST, n)
        exists = os.path.isdir(target)
        if a.uninstall:
            if exists:
                if not a.dry_run:
                    os.makedirs(backup_root, exist_ok=True)
                    shutil.move(target, os.path.join(backup_root, n))
                removed.append(n)
            continue
        if exists and same_tree(src, target):
            unchanged.append(n)
            continue
        if not a.dry_run:
            if exists:
                os.makedirs(backup_root, exist_ok=True)
                shutil.move(target, os.path.join(backup_root, n))
                backed_up.append(n)
            shutil.copytree(src, target, ignore=IGNORE)
        (updated if exists else installed).append(n)

    prefix = "[dry-run] " if a.dry_run else ""
    if a.uninstall:
        print(prefix + "Đã gỡ: " + (", ".join(removed) or "không có skill nào để gỡ"))
        if removed and not a.dry_run:
            print("Bản gỡ ra được giữ ở: " + backup_root)
        return
    print(prefix + "Thư mục skill: " + DEST)
    print(prefix + "Cài mới:      " + (", ".join(installed) or "—"))
    print(prefix + "Cập nhật:     " + (", ".join(updated) or "—"))
    print(prefix + "Không đổi:    " + (", ".join(unchanged) or "—"))
    if backed_up and not a.dry_run:
        print("Bản cũ đã sao lưu ở: " + backup_root)
    if not a.dry_run and (installed or updated):
        print("\nXong. Mở một phiên Claude Code mới (hoặc gõ /reload-skills) rồi gõ / để thấy các skill.")


if __name__ == "__main__":
    main()
