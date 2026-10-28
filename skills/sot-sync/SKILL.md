---
name: sot-sync
description: Đồng bộ SoT sau mỗi thay đổi. Ví dụ: một quyết định vừa được chốt, PM trả lời câu hỏi, doc hoặc brief có bản mới, đổi version / tên file, một tính năng chốt xong cần dọn review. Skill tìm mọi file bị ảnh hưởng (decisions, brief, open-questions, screen-inventory, ui-copy, handoff, CLAUDE.md, sources, flowchart, tính năng dùng chung dữ liệu, note ⚠️ trong Figma), lập checklist chờ người dùng xác nhận, sửa đồng loạt, sửa link, archive hoặc xoá file cũ, sinh lại HTML và commit. Dùng skill này mỗi khi người dùng nói "PM vừa chốt…", "đã chốt X", "ghi quyết định này vào SoT", "cập nhật SoT", "đồng bộ lại các file", "brief có bản mới rồi", "PM trả lời rồi", "tính năng X chốt xong rồi", "dọn review", "đổi tên file cho đúng version", kể cả khi họ chỉ báo một kết luận mà không nói phải sửa file nào. KHÔNG dùng để review một doc mới (spec-review) hay dựng tính năng mới (sot-feature).
---

# SoT Sync: giữ SoT đồng bộ sau mỗi quyết định

Bước 06 trong quy trình 8 bước. Lỗi phổ biến nhất của SoT là **quyết định mới đã có nhưng brief vẫn cũ**. Lỗi tiếp theo là file phụ trợ (handoff, screen-inventory, CLAUDE.md) vẫn ghi điều cũ. Người đọc và Claude ở phiên sau sẽ làm theo thông tin sai mà không biết. Một quyết định thường chạm 4–6 file. Skill này để không sót file nào.

## Nguyên tắc

1. **Brief / doc mới nhất thắng.** File phụ trợ lệch với brief mới nhất thì sửa file phụ trợ, rồi báo người dùng đã sửa chỗ nào.
2. **Không tự chốt.** Chỉ ghi **Đã chốt** khi có người xác nhận, và ghi rõ là ai. Người dùng chỉ kể một ý kiến hoặc một hướng đang nghĩ thì ghi **Đề xuất**. Chỗ brief không nói rõ thì hỏi, không suy ra.
3. **Lập checklist, chờ xác nhận, rồi mới sửa.** Một quyết định có thể lan ra nhiều file, và người dùng cần thấy phạm vi trước. Ngoại lệ: người dùng đã nói rõ "cứ sửa luôn".
4. **Không xoá lịch sử quyết định.** `decisions.md` chỉ thêm dòng. Quyết định bị đảo thì thêm dòng mới, ghi "thay thế #N".

## Bước 0: Lấy bản mới nhất

Dự án có Git thì chạy `git pull` trước khi đọc. Working tree có thay đổi chưa commit của người khác hoặc của phiên trước thì báo người dùng trước khi làm tiếp.

## Bước 1: Xác định thay đổi

Ghi rõ 5 thứ, thiếu thì hỏi bằng AskUserQuestion:
- **Cái gì** đã đổi: trích nguyên văn lời người dùng, câu trả lời của PM, hoặc đoạn doc mới.
- **Ai** chốt, **ngày** nào. Người dùng chỉ nói "PM chốt" thì tìm tên PM trong `context/stakeholders.md` hoặc `CLAUDE.md` dự án trước. Không có ở đâu mới hỏi.
- **Trạng thái**: Đã chốt hay chỉ là Đề xuất.
- **Thay thế** điều gì cũ: số quyết định cũ, giá trị cũ, mã câu hỏi.
- **Phạm vi**: tính năng nào, version nào.

Loại thay đổi thường gặp:
- quyết định mới hoặc đảo quyết định;
- PM trả lời câu hỏi có mã;
- doc PM có bản mới;
- đổi version hoặc đổi tên file;
- tính năng chốt xong toàn bộ.

## Bước 2: Tìm mọi file bị ảnh hưởng

Grep theo nhiều khoá: mã câu hỏi (`SET-12`), số quyết định (`#4`), giá trị cũ (`2,000 ml`), tên màn, tên file cũ. Sau đó xét lần lượt danh sách sau, không bỏ qua mục nào dù nghĩ là không liên quan:

| File | Xét gì |
|---|---|
| `features/<tn>/decisions.md` | Thêm dòng mới; ghi "thay thế #N" nếu đảo |
| `decisions.md` dự án | Quyết định ảnh hưởng nhiều tính năng |
| Brief mới nhất | Câu cũ còn sót ở mục khác, ở AC, ở bảng |
| `open-questions.md` | Chuyển câu đã trả lời xuống "Đã trả lời" |
| `design/screen-inventory.md` | Trạng thái frame, cột quyết định, note ⚠️ |
| `copy/ui-copy.md` | Copy đổi theo quyết định |
| `handoff/handoff-v<x.y.z>.md` | Logic, điều kiện hiển thị, danh sách ⚠️ |
| `CLAUDE.md` tính năng | Dòng trạng thái, "Đã chốt", link file mới nhất |
| `CLAUDE.md` + `README.md` dự án | Trạng thái, bảng tính năng, việc còn mở |
| `sources.md` (nếu dự án có) | Nguồn mới, nguồn chuyển thành Cũ, mâu thuẫn đã chốt |
| Review đang mở (`brief/…spec-review…`) | Câu vừa được trả lời |
| Brief các version cũ của tính năng khác | Chỉ thêm ghi chú, không sửa nội dung (xem bước 4) |
| `design-system/` | Khi quyết định chạm token, component, quy ước copy |
| `design/<tn>-flow.mmd` + khối FLOWCHART trong brief | Luồng đổi |
| Tính năng dùng chung dữ liệu | Ví dụ đổi đơn vị ở Settings chạm Water, Home |
| Figma | Frame có note ⚠️ ghi mã câu hỏi vừa được trả lời |

**Tìm note ⚠️ trong Figma:** chạy `use_figma` với một script chỉ đọc. Script duyệt các text node trong section, lấy những node có `characters` chứa `⚠️` hoặc mã câu hỏi (ví dụ `STEP-2`), rồi trả về node ID và frame cha. Đừng tìm theo tên layer: note thường được duplicate nên tên layer không khớp nội dung. Chưa kết nối Figma MCP thì ghi "chưa kiểm Figma" vào checklist, không đoán.

## Bước 3: Checklist chờ xác nhận

Trình bày một bảng **File → Sửa gì → Vì sao**, ghi rõ sửa từ nội dung nào sang nội dung nào. Kèm theo:
- những điểm cần người dùng quyết định thêm, ví dụ quyết định mới mâu thuẫn với một quyết định Đã chốt khác;
- frame Figma sẽ phải sửa. Liệt kê ra; chỉ sửa Figma khi người dùng đồng ý.

Hỏi xác nhận bằng AskUserQuestion. Người dùng bỏ bớt mục nào thì không sửa mục đó.

## Bước 4: Sửa

- **decisions.md:**
  - Dòng mới đặt trên cùng, số tăng dần.
  - Ghi đủ các cột: Ngày, Trạng thái, Quyết định, Lý do, Phương án đã loại, Ai chốt.
  - Khi đảo quyết định: dòng cũ giữ nguyên, dòng mới ghi "thay thế #N".
- **open-questions.md:**
  - Chuyển câu đã trả lời xuống "Đã trả lời", dạng `→ <câu trả lời> (<ai>, <ngày>)`.
  - Câu trả lời là một quyết định thì ghi luôn vào decisions.
  - Câu trả lời làm nảy ra câu hỏi mới: ghi câu đó vào open-questions với mã mới, người cần trả lời, nhãn chặn design / không chặn design, và dòng "Phát sinh từ <mã cũ>".
- **PM chỉ trả lời một phần câu hỏi của vòng review:**
  - Vòng review vẫn đang mở, tức PM chưa ra bản doc mới: sửa ngay trong file review hiện tại. Đánh dấu câu đã trả lời và ghi câu trả lời cạnh câu hỏi. Không tạo file mới.
  - Chỉ tạo file vòng mới `-r<N+1>` khi PM ra bản doc mới, hoặc khi `spec-review` chạy vòng tiếp theo.
- **Brief version cũ của tính năng khác** bị quyết định mới làm sai: không sửa nội dung, vì brief cũ ghi lại điều đã đúng tại thời điểm đó. Thêm một dòng ghi chú dưới H1, dạng `> Từ v<x.y.z> (<ngày>): <điều đã đổi>, xem decisions #N.`
- **Brief:** sửa cả các câu cũ còn sót ở mục khác, không chỉ mục đang bàn. Brief là doc của PM mà chưa được phép sửa thì ghi chỗ lệch vào open-questions dưới dạng "Doc cần sửa", kèm câu viết sẵn.
- **Ngày:** ghi ngày sửa ở dòng trạng thái hoặc đầu file.
- **Doc PM có bản mới:**
  - Lưu bản mới vào `brief/` với tên có ngày và version theo Figma.
  - Chuyển bản cũ vào `_archive/`, tạo `_archive/` nếu chưa có.
  - Sửa mọi link trỏ tới bản cũ.
- **Đổi tên file:** đổi đúng quy ước `YYYY-MM-DD_<mô-tả>-v<x.y.z>.md`. Vòng review dùng `-rN`. Đổi cả bản `.html` đi kèm.
- **Tính năng chốt xong** (đã có doc chính thức trong `brief/`): xoá các file review của tính năng đó, cả trong `brief/` và `_archive/`, cả `.md` lẫn `.html`. Làm theo thứ tự:
  1. Chuyển những gì còn sống sang doc chính thức, `decisions.md` hoặc `open-questions.md`: câu logic cho dev chưa trả lời, tin gửi PM đang gộp chung.
  2. File review dùng chung với một tính năng chưa chốt thì giữ lại, và nói rõ với người dùng.
  3. Sửa link trỏ vào file sắp xoá. Xoá. Grep lại để chắc không còn link chết.
  4. Ghi vào đầu doc chính thức rằng review đã xoá và doc này là nguồn duy nhất.

## Bước 5: Kiểm tra lại

- Grep giá trị cũ và mã cũ: còn sót ở đâu không?
- Kiểm tra link `.md` trong các file vừa sửa: file đích còn tồn tại không?
- Số đếm khớp nhau giữa các file: số câu còn mở, số frame, số quyết định trong `CLAUDE.md` so với file chi tiết.

## Bước 6: Sinh HTML, commit

- Sinh lại `.html` cho mọi file `.md` vừa sửa **mà đã có bản `.html` cạnh nó**, và cho file output mới (brief, review, handoff):
  ```bash
  python3 _tools/md_to_html.py <file.md> ...
  ```
  Không sinh cho `CLAUDE.md`. Trên Windows thay `python3` bằng `py`.
- Dự án chưa có `_tools/md_to_html.py` (SoT dựng trước khi có bộ skill này):
  - chạy bản dự phòng ở `<thư mục skill sot-init>/assets/project/_tools/md_to_html.py`;
  - đề nghị người dùng chép thư mục `_tools/` vào dự án;
  - **không vá tay file `.html`**. HTML vá tay sẽ lệch với `.md` ở lần sửa sau.
- Có Git:
  - commit với message nói điều đã chốt, ví dụ `Water: chốt goal gốc 2,500 ml (#1), cập nhật brief + inventory`;
  - push nếu người dùng đã yêu cầu, hoặc đã dặn push luôn; nếu chưa thì hỏi một lần.
- Sửa Figma (đã được đồng ý):
  - bỏ ⚠️ ở frame đã chốt, đổi note sang quy tắc đã chốt;
  - ghi node đã sửa vào screen-inventory.

## Trả lời trong chat

- Đã sửa file nào, một dòng mỗi file. Kèm link.
- Còn lại gì:
  - câu còn mở, số câu chặn design;
  - frame Figma còn ⚠️;
  - việc chờ người khác.
- Đã commit / push chưa.
- Nếu phát hiện file phụ trợ đang lệch với brief từ trước (không do lần thay đổi này), nói rõ đó là lỗi cũ vừa được sửa.
