# Cài đặt SoT builder

Làm **một lần mỗi máy**, theo đúng thứ tự dưới đây. Mất khoảng 15–20 phút. Bạn không cần biết lập trình: mỗi bước là một vài lệnh copy–paste, hoặc nhờ Claude Code chạy giúp.

Mở terminal:
- **macOS:** mở app **Terminal**, hoặc trong VS Code chọn Terminal → New Terminal.
- **Windows:** trong VS Code chọn Terminal → New Terminal (PowerShell).

## Bước 1: VS Code và Claude Code

1. Cài **Visual Studio Code**: https://code.visualstudio.com
2. Trong VS Code, mở Extensions (Cmd/Ctrl + Shift + X), tìm **Claude Code**, bấm Install.
3. Đăng nhập bằng tài khoản Claude của công ty khi extension hỏi.

Từ bước 2 trở đi, bạn có thể dán nguyên phần hướng dẫn của bước đó vào khung chat Claude Code và nhờ Claude làm. Khi cần bạn thao tác (bấm Yes, đăng nhập trên trình duyệt), Claude sẽ nói rõ.

## Bước 2: Git, GitHub CLI, Python 3

| Công cụ | Dùng để | macOS | Windows |
|---|---|---|---|
| Git | Lưu lịch sử SoT, đồng bộ giữa các máy | `xcode-select --install` | `winget install --id Git.Git -e` |
| GitHub CLI (`gh`) | Đăng nhập GitHub, tạo repo, clone | `brew install gh` | `winget install --id GitHub.cli -e` |
| Python 3 | Chạy script của các skill (dựng khung, sinh HTML, audit) | Có sẵn sau `xcode-select --install` | `winget install --id Python.Python.3.13 -e` |

- **macOS** chưa có Homebrew thì cài trước theo https://brew.sh.
- **Windows:**
  - Nếu hộp thoại **"Do you want to allow this app to make changes"** hiện lên (có thể chỉ nhấp nháy dưới taskbar), bấm **Yes**.
  - Cài xong, **đóng hẳn VS Code rồi mở lại** để terminal nhận lệnh mới.
  - Lệnh Python trên Windows là `py` (hoặc `python`), trên Mac là `python3`.

Kiểm tra:
```bash
git --version
gh --version
python3 --version     # Windows: py --version
```

## Bước 3: Đăng nhập GitHub

Cần có tài khoản GitHub. Repo SoT builder đang để **private**, nên hãy nhờ owner (ducndiKame) mời tài khoản của bạn, rồi **chấp nhận lời mời** trong email hoặc tại https://github.com/notifications.

```bash
gh auth login -h github.com -p https -s workflow --web
```

- Terminal hiện một **mã 8 ký tự**. Mở https://github.com/login/device, kiểm tra góc trên phải trình duyệt có đúng tài khoản của bạn không, rồi nhập mã và bấm **Authorize**.
- Sau đó chạy tiếp:
  ```bash
  gh auth setup-git
  git config --global user.name "<tên GitHub của bạn>"
  git config --global user.email "<email công ty>"
  ```
- Thêm trên **Windows**:
  ```bash
  git config --global core.longpaths true
  ```

`gh auth setup-git` cho Git dùng chung lần đăng nhập này, nên sau này push / pull không phải nhập mật khẩu. **Không bao giờ dán token hay mật khẩu vào chat với Claude.**

## Bước 4: Kết nối Figma MCP

Các skill đọc và sửa Figma qua **Figma MCP chính thức**: `sot-feature`, `sot-audit`, `spec-review`, `design-system-build` và `figma-design-rename`. Kết nối theo hướng dẫn của Figma cho Claude Code (help.figma.com, mục *Figma MCP server*), rồi kiểm tra bằng cách nhắn Claude:

> Dùng Figma MCP gọi whoami

Claude trả về tài khoản Figma của bạn là đã kết nối. Chưa kết nối Figma thì các skill vẫn chạy được phần tài liệu. Phần nào cần đọc Figma, Claude sẽ báo thiếu chứ không đoán.

Doc PM nằm trên portal nội bộ hoặc Google Docs thì cần thêm connector / MCP tương ứng. Ghi cách đọc doc vào `CLAUDE.md` của dự án (skill `sot-init` sẽ hỏi bạn).

## Bước 5: Cài skill

### Cách A (khuyên dùng): clone repo và chạy script

```bash
gh repo clone ducndiKame/SoT-builder
cd SoT-builder
python3 install.py          # Windows: py install.py
```

- Script chép 10 skill vào `~/.claude/skills/` (Windows: `C:\Users\<bạn>\.claude\skills\`), dùng được ở mọi dự án.
- Máy đã có skill cùng tên (ví dụ `spec-review`) mà khác bản trong repo: bản cũ được **sao lưu** vào `~/.claude/skills/.backup-sot-builder/<ngày-giờ>/` trước khi ghi đè.
- Các lệnh khác:

| Lệnh | Tác dụng |
|---|---|
| `python3 install.py --list` | Skill nào đã cài, bản nào cũ |
| `python3 install.py --only sot-init,sot-sync` | Chỉ cài vài skill |
| `python3 install.py --dry-run` | Xem trước, không cài |
| `python3 install.py --uninstall` | Gỡ |

Tên skill khi gọi: `/sot-init`, `/sot-feature`...

### Cách B: cài theo dạng plugin

Trong khung chat Claude Code (VS Code), gõ `/plugins` để mở **Manage plugins**.
1. Tab **Marketplaces**: thêm `ducndiKame/SoT-builder`.
2. Tab **Plugins**: cài `sot-builder`, chọn phạm vi *Install for you*.

Lưu ý khi dùng cách B:
- Máy chưa có SSH key cho GitHub thì phải đặt biến môi trường `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` trước, nếu không việc cài từ repo private sẽ lỗi. Cách A không cần bước này.
- Tên skill có tiền tố: `/sot-builder:sot-init`.
- Nếu đã cài cách A thì đừng cài thêm cách B (và ngược lại). Nếu cài cả hai, mỗi skill sẽ hiện hai lần.
- Cập nhật: `/plugins` → Marketplaces → cập nhật `sot-builder`, rồi gõ `/reload-plugins`.

## Bước 6: Kiểm tra

Mở một phiên Claude Code **mới** (hoặc gõ `/reload-skills`), rồi:
1. Gõ `/`: thấy `sot-init`, `sot-feature`, `sot-sync`, `sot-audit`, `sot-handoff`.
2. Nhắn Claude: *"Liệt kê các skill sot-* đang có và mỗi skill dùng khi nào"*.

Xong bước này thì chuyển sang [Quy trình dựng SoT cho dự án mới](2-quy-trinh-du-an-moi.md).

## Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `git` / `gh` / `py`: command not found ngay sau khi cài (Windows) | Đóng hẳn VS Code rồi mở lại |
| `python` mở Microsoft Store (Windows) | Dùng `py` thay cho `python` |
| `gh repo clone` báo không tìm thấy repo | Chưa được mời, hoặc chưa chấp nhận lời mời repo private |
| Gõ `/` không thấy skill | Mở phiên Claude Code mới, hoặc gõ `/reload-skills`; chạy `install.py --list` để kiểm tra |
| Push báo lỗi đăng nhập | Chạy lại `gh auth login --web` rồi `gh auth setup-git` |
| Claude báo không đọc được Figma | Kiểm tra lại bước 4 (Figma MCP) |
