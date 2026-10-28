# Git cho SoT: cài đặt, đăng nhập, nhịp làm việc

Người dùng của bộ skill này là designer, không nhất thiết biết lập trình. Khi hướng dẫn, giải thích bằng lời thường. Tự chạy lệnh khi có thể, chỉ đưa lệnh cho người dùng khi bước đó cần họ thao tác (đăng nhập trên trình duyệt, bấm Yes ở hộp thoại cài đặt).

## 1. Cài công cụ

| Công cụ | macOS | Windows |
|---|---|---|
| Git | `xcode-select --install` (có sẵn Git), hoặc `brew install git` | `winget install --id Git.Git -e` |
| GitHub CLI (`gh`) | `brew install gh` | `winget install --id GitHub.cli -e` |
| Python 3 | Thường có sẵn sau `xcode-select --install`; hoặc `brew install python` | `winget install --id Python.Python.3.13 -e` |

Bẫy trên Windows:
- Sau khi cài, terminal đang mở chưa thấy lệnh mới. Mở terminal mới, hoặc gọi bằng đường dẫn đầy đủ: `C:\Program Files\Git\cmd\git.exe`, `C:\Program Files\GitHub CLI\gh.exe`.
- Lệnh `python` có thể trỏ vào bản giả của Microsoft Store. Dùng `py`, hoặc đường dẫn đầy đủ `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`.
- Hộp thoại UAC ("Do you want to allow this app to make changes") có thể nhấp nháy dưới taskbar mà không bật lên trước. Nhắc người dùng bấm Yes.

## 2. Đăng nhập GitHub (một lần mỗi máy)

```bash
gh auth login -h github.com -p https -s workflow --web
gh auth setup-git
git config --global user.name "<tên GitHub>"
git config --global user.email "<email>"
```

- Nếu Claude chạy `gh auth login --web` trong nền: đọc mã one-time trong output, đưa cho người dùng kèm link `https://github.com/login/device`. Nhắc họ kiểm tra góc trên phải trình duyệt xem có đúng tài khoản không.
- `gh auth setup-git` cho Git dùng chung đăng nhập của `gh`, nên không phải nhập lại mật khẩu khi push.
- Windows: thêm `git config --global core.longpaths true`, vì đường dẫn SoT có thể rất dài.
- Không bao giờ xin token hay mật khẩu qua chat.

## 3. Nối một thư mục có sẵn với repo có sẵn (không clone lại)

Dùng khi thư mục local và repo đã tồn tại độc lập, ví dụ máy chưa từng cài Git:

```bash
git init
git remote add origin https://github.com/<owner>/<repo>.git
git fetch origin
git reset --mixed origin/main      # chỉ đổi lịch sử, không đụng file trên máy
git branch --set-upstream-to=origin/main main
git status --short                 # thấy chính xác máy khác repo ở đâu
```

Trước khi commit, xem `git status`: phía nào mới hơn? Hỏi người dùng nếu có file mà máy và repo đều đã sửa.

## 4. Nhịp làm việc hằng ngày

1. **Pull** trước khi sửa: `git pull`
2. **Làm**: designer và Claude sửa file
3. **Xem diff**: `git status`, `git diff`. Kiểm tra từng thay đổi có căn cứ
4. **Commit** kèm lý do: `git commit -m "<Tính năng>: <đã chốt / đã sửa gì>"`
5. **Push**: `git push`

- Đổi máy: push ở máy cũ, pull ở máy mới **trước khi** sửa.
- Thay đổi lớn hoặc nhiều người cùng làm: tạo branch (`git switch -c <tên>`) rồi mở pull request (`gh pr create`).
- Commit message viết tiếng Việt, ngắn, nói **điều gì đã chốt / đã đổi**, không chỉ "update".

## 5. Conflict

Git báo conflict khi hai máy cùng sửa một chỗ. Git không âm thầm ghi đè.
- Đọc cả hai phiên bản. Phía nào đúng là **quyết định của người dùng**, không phải của Claude.
- Với `decisions.md`, thường giữ cả hai dòng và đánh lại số, vì bảng này chỉ thêm, không xoá.
- Sửa xong: `git add <file>`, `git commit`, `git push`.

## 6. Quyền truy cập repo

- Mời người khác: `gh api -X PUT repos/<owner>/<repo>/collaborators/<username> -f permission=push`. Hỏi người dùng trước khi chạy, vì GitHub sẽ gửi lời mời đi.
- Người được mời phải chấp nhận lời mời trên GitHub (qua email hoặc github.com/notifications) rồi mới clone được.
