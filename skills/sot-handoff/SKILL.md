---
name: sot-handoff
description: Bàn giao SoT của dự án cho một designer khác, hoặc tiếp nhận SoT từ người khác. Bên giao gồm các việc: pull bản mới nhất, cập nhật README và trạng thái tính năng, liệt kê nguồn và quyền truy cập cần cấp, ghi quyết định và câu hỏi mở có owner, chạy audit, viết BAN-GIAO.md, commit bàn giao, push, mời người nhận vào repo. Bên nhận gồm các việc: cài công cụ, đăng nhập GitHub, clone, đọc lối vào, kiểm tra quyền truy cập Figma / doc, làm một task nhỏ, tạo branch và pull request đầu tiên. Dùng skill này mỗi khi người dùng nói "bàn giao dự án cho X", "chuẩn bị handoff SoT", "tôi sắp nghỉ / chuyển dự án", "nhận dự án từ X", "onboard designer mới vào SoT", "mới clone repo SoT về, bắt đầu từ đâu", "mời X vào repo". KHÔNG dùng cho bàn giao design cho dev của một tính năng (đó là file handoff-vX.Y.Z.md trong sot-feature).
---

# SoT Handoff: bàn giao và tiếp nhận SoT

Bước 08 trong quy trình 8 bước. Tiêu chí bàn giao nằm ở **khả năng tiếp tục**: người nhận tìm được nguồn, biết điểm nào còn mở, và tạo được thay đổi đầu tiên để người cũ review. Gửi file zip không đạt được điều này: zip chỉ là ảnh chụp tại một thời điểm, không có lịch sử, không có diff, và không biết bản nào mới nhất. Vì vậy bàn giao đi qua private repo.

Trước tiên hỏi người dùng đang **giao** hay **nhận**.

---

## Chế độ GIAO

### 1. Lấy bản mới nhất và kiểm tra
- `git pull`. Còn thay đổi chưa commit thì hỏi người dùng có đưa vào bàn giao không.
- Chạy skill `sot-audit`, ít nhất tầng A và phần chấm DoD. Lỗi mức "Lỗi" phải sửa trước khi bàn giao, sửa qua `sot-sync`.

### 2. Cập nhật lối vào
- `README.md`: trạng thái toàn dự án, ngày, phần nào đủ dùng, phần nào còn nháp.
- `CLAUDE.md` dự án: dòng Trạng thái và cột trạng thái trong bảng Tính năng.
- `CLAUDE.md` của từng tính năng đang dở: bước hiện tại, việc tiếp theo, việc đang chặn.

### 3. Nguồn và quyền truy cập
- Trong `sources.md`, điền cột "Quyền truy cập" cho mọi nguồn **Hiện hành**: Figma file nào, doc portal nào, kênh chat nào, ai cấp.
- Lập danh sách quyền cần cấp cho người nhận, gồm repo, Figma (quyền view hay edit), doc PM, kênh liên lạc. Đánh dấu cái nào người dùng tự cấp, cái nào phải nhờ người khác.

### 4. Quyết định và câu hỏi mở
- Mọi câu trong `open-questions.md` phải có người cần trả lời và ngày hỏi.
- Câu nào người giao đang theo dõi riêng (đã nhắn PM, đang chờ) thì ghi rõ "đã hỏi qua <kênh> ngày <...>".
- Quyết định nói miệng hoặc trong chat mà chưa vào SoT: hỏi người dùng, rồi ghi vào qua `sot-sync`.

### 5. Viết BAN-GIAO.md
Tạo hoặc cập nhật `BAN-GIAO.md` ở gốc dự án theo `assets/ban-giao-template.md`, rồi sinh `.html` bằng `python3 _tools/md_to_html.py BAN-GIAO.md` (Windows dùng `py` thay `python3`). Dự án chưa có `_tools/` thì dùng bản trong skill `sot-init` (`assets/project/_tools/md_to_html.py`), không vá tay file `.html`. Nội dung:
- người giao, người nhận, ngày;
- trạng thái từng tính năng;
- 3–5 việc tiếp theo theo thứ tự ưu tiên;
- danh sách quyền truy cập;
- câu hỏi mở quan trọng;
- bẫy đã gặp (ví dụ "section Figma đổi ID khi cắt dán, tìm theo tên");
- task gợi ý cho người nhận làm đầu tiên.

### 6. Commit, push, mời người nhận
- Commit với message `Bàn giao SoT cho <người nhận>`, rồi push.
- **Hỏi trước khi mời** (GitHub sẽ gửi lời mời đi):
  ```bash
  gh api -X PUT repos/<owner>/<repo>/collaborators/<username> -f permission=push
  ```
- Soạn sẵn tin nhắn cho người nhận, gồm link repo, link `BAN-GIAO.md` trên GitHub, và lời nhắc "chấp nhận lời mời trên GitHub, rồi mở Claude Code và nói: nhận bàn giao SoT từ repo này".

---

## Chế độ NHẬN

### 1. Công cụ và đăng nhập
Kiểm tra Git, GitHub CLI, Python 3. Thiếu thì cài, đăng nhập bằng `gh auth login --web` và `gh auth setup-git`. Xem `references/git-workflow.md` trong skill này. Người nhận phải chấp nhận lời mời repo trên GitHub trước.

### 2. Clone
```bash
gh repo clone <owner>/<repo> "<thư mục đích>"
```
Sau đó mở thư mục đó trong VS Code (File → Open Folder).

### 3. Đọc lối vào
Đọc theo thứ tự: `BAN-GIAO.md` → `README.md` → `CLAUDE.md` → `sources.md`. Sau đó tóm tắt cho người nhận:
- dự án là gì, đang ở đâu;
- 3 việc tiếp theo;
- câu hỏi mở nào đang chờ ai.

### 4. Kiểm tra quyền truy cập
- Với từng nguồn Hiện hành trong `sources.md`, thử mở. Figma kiểm tra bằng `get_metadata` qua Figma MCP. Doc kiểm tra bằng connector hoặc MCP tương ứng.
- Nguồn nào không mở được thì lập danh sách để người nhận xin quyền. Đừng đoán nội dung của nguồn không mở được.

### 5. Task nhỏ đầu tiên
Làm task gợi ý trong `BAN-GIAO.md`. Không có thì chọn một việc nhỏ có thật, ví dụ sửa một link chết hoặc cập nhật một trạng thái mà audit tìm ra. Mục tiêu là xác nhận người nhận hiểu đúng cách đọc và cập nhật SoT, chưa phải làm thay đổi lớn.

### 6. Branch và pull request đầu tiên
```bash
git switch -c onboarding/<tên-người-nhận>
# sửa file, xem diff
git commit -m "<mô tả thay đổi>"
git push -u origin onboarding/<tên-người-nhận>
gh pr create --title "<...>" --body "<thay đổi gì, vì sao, nguồn>"
```
Người giao review PR. Sau khi merge, người nhận làm việc theo nhịp pull → làm → xem diff → commit → push.

## Trả lời trong chat
- **Giao:**
  - đã cập nhật gì;
  - DoD đạt mấy trên 6;
  - quyền nào còn phải cấp;
  - link `BAN-GIAO.md`;
  - tin nhắn soạn sẵn cho người nhận.
- **Nhận:**
  - tóm tắt dự án;
  - nguồn nào chưa có quyền;
  - task đầu tiên đã làm;
  - link pull request.
