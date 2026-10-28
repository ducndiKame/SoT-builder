---
name: sot-feature
description: Làm trọn một tính năng trong SoT của dự án. Skill tạo folder tính năng theo khung, đọc section Figma và doc PM, rồi viết brief/AC, decisions, open-questions, screen-inventory (nối frame Figma ↔ AC ↔ quyết định), flowchart, ui-copy và handoff cho dev, mỗi ý đều ghi nguồn. Dùng skill này mỗi khi người dùng muốn "thêm tính năng X vào SoT", "làm feature page", "tạo folder cho tính năng", "kiểm kê màn của section Figma", "map frame với AC", "chuẩn bị handoff dev cho tính năng X", "làm feature mẫu cho SoT", hoặc đưa một section Figma kèm doc PM và muốn gom thành hồ sơ tính năng, kể cả khi không nói chữ "SoT". KHÔNG dùng để dựng SoT từ đầu (sot-init), chỉ review doc PM (spec-review) hay ghi một quyết định mới vào hồ sơ đã có (sot-sync).
---

# SoT Feature: làm trọn một tính năng

Bước 04 trong quy trình 8 bước. Mục tiêu là **một trang tính năng đủ dùng**: người mới và AI đọc xong làm được một task nhỏ mà không phải đoán. Lỗi hay gặp nhất là mô tả UI nhưng thiếu điều kiện: có frame mà không có AC, có hành vi mà không ghi ai chốt.

Một tính năng "đủ sâu" khi có đủ 5 thứ, mỗi thứ đều dẫn nguồn:
1. **Quyết định**, kèm phương án đã loại
2. **Hành vi và AC** trong brief
3. **UI map**: frame Figma ↔ AC ↔ quyết định
4. **TBD**: câu hỏi còn mở có owner
5. **Trạng thái** rõ ràng (Đã chốt / Đã vẽ / Còn mở)

## Nguyên tắc

1. **Tách "doc ghi" với "tôi suy ra".** Khi tóm tắt doc, trích nguyên văn. Phần suy ra viết thành câu hỏi, không viết thành kết luận. Không ghi **Đã chốt** cho điều chưa có ai xác nhận. Gặp chỗ mơ hồ thì hỏi người dùng bằng AskUserQuestion.
2. **Đọc text bên trong frame, đừng tin tên frame.** Frame duplicate từ frame cũ thường mang tên cũ.
3. **Số trong Figma là số minh hoạ**, không phải expected value. Công thức và giá trị lấy từ brief và quyết định.
4. **Ô trống là thông tin.** Frame chưa có AC thì ghi "Chưa có AC riêng". State chưa có frame thì ghi vào "State còn thiếu". Không lấp chỗ trống bằng suy đoán.

## Bước 0: Đọc bối cảnh dự án

- Đọc `CLAUDE.md`, `sources.md` và `decisions.md` của dự án. Nếu chưa có SoT (không có `CLAUDE.md` chứa `<!-- FEATURES -->`), dừng lại và đề xuất `sot-init`.
- Tính năng đã có folder thì không tạo lại. Đọc các file hiện có rồi bổ sung phần còn thiếu.

## Bước 1: Xác định phạm vi

Cần biết 4 thứ, thiếu thì hỏi:
- tên tính năng (kebab-case tiếng Anh);
- **version, lấy đúng như tên section hoặc page trong Figma** (ví dụ section "Settings V1.0.1" thì version là `1.0.1`). Section không ghi version thì lấy theo tên page chứa nó, ví dụ page "05 More V1.0.0". Cả hai đều không có thì hỏi, không tự đặt v1/v2;
- section Figma (tìm theo tên, vì ID section có thể đổi khi cắt dán);
- doc PM: link, phiên bản, ngày, cách đọc theo tham số trong `CLAUDE.md` dự án.

## Bước 2: Dựng folder

Các lệnh trong skill viết `python3` (macOS / Linux). Trên Windows thay bằng `py`, vì `python3` có thể mở Microsoft Store.

```bash
python3 <thư mục skill>/scripts/new_feature.py --project "<thư mục dự án>" --name <tên> --version <x.y.z>
```

Script tạo `CLAUDE.md`, `decisions.md`, `open-questions.md`, `design/screen-inventory.md`, `copy/ui-copy.md`, và thêm dòng tính năng vào bảng trong `CLAUDE.md` dự án. Các folder `brief/`, `handoff/`, `research/`, `_archive/` chỉ tạo khi có file đầu tiên.

## Bước 3: Kiểm kê Figma → screen-inventory

- Đọc Figma bằng bộ công cụ sau, tất cả đều chỉ đọc:
  - `get_metadata`: danh sách frame, tên, node ID, kích thước.
  - `use_figma` chạy script chỉ đọc: lấy `characters` của mọi text node trong frame. Đây là cách đọc text thật. Tên layer thường là câu cũ còn sót lại từ lúc duplicate.
  - `get_screenshot`: nhìn vài frame đại diện bằng mắt.
  
  `get_design_context` dành cho việc chuyển design sang code, và server bắt buộc load skill riêng. Không cần dùng nó để kiểm kê.
- Liệt kê mọi frame trong section. Với từng frame, đọc text bên trong.
- Tên frame lộn xộn (`Frame 427`, tên trùng, tên cũ còn sót) thì đề nghị chạy skill `figma-design-rename` trước. Đặt tên đúng giúp tìm frame và state nhanh hơn.
- Mỗi frame một dòng trong `design/screen-inventory.md`: tên frame, vai trò, link node (`https://www.figma.com/design/<fileKey>/<name>?node-id=<a-b>`), AC liên quan, quyết định liên quan, trạng thái.
- Rà danh sách state chuẩn (loading, empty, error, offline, permission bị từ chối, dữ liệu biên, user cũ / thiếu dữ liệu). State nào chưa có frame thì ghi vào mục "State còn thiếu".

## Bước 4: Doc PM → brief

- Lưu nội dung doc vào `brief/YYYY-MM-DD_spec-<tính-năng>-v<x.y.z>.md`. Đầu file ghi: link doc gốc, phiên bản, ngày, người viết, cách đọc. Doc là PDF, ảnh hay docx thì giữ file gốc, kèm bản `.md` cùng tên.
- **Ngày trong tên file là ngày của bản doc**, tức ngày PM phát hành hoặc cập nhật bản đó, không phải ngày lưu. Nhờ vậy hai bản doc của cùng một version xếp đúng thứ tự. Doc không ghi ngày thì dùng ngày lưu, và ghi rõ ở đầu file: "Ngày trong tên = ngày lưu, doc gốc không ghi ngày".
- **Doc PM đã có flowchart:** giữ nguyên flowchart đó trong brief, vì đó là nội dung của PM. Flowchart của design (bước 6) vẽ theo Figma, đặt ở khối FLOWCHART đầu brief. Hai sơ đồ lệch nhau ở bước nào thì ghi bước đó vào `open-questions.md`. Không âm thầm sửa sơ đồ của PM.
- **Doc cần phản biện** (doc mới, còn mơ hồ, mâu thuẫn với Figma): chạy skill `spec-review`. Kết quả review nằm trong `brief/`, các câu hỏi đi vào `open-questions.md`.
- **Chưa có AC, hoặc AC chưa kiểm thử được**: dùng skill `document-fullstack-v2` để viết AC dạng Gherkin. Đánh dấu rõ AC nào do design viết và đang chờ PM xác nhận.

## Bước 5: Nối frame ↔ AC ↔ quyết định

Đây là phần làm cho SoT dùng được, không chỉ là đống file.
- Điền cột "AC liên quan" và "Quyết định liên quan" cho từng frame trong screen-inventory.
- AC không có frame nào thể hiện, và frame không có AC nào mô tả: cả hai đều là lỗ hổng. Ghi lại và đưa vào open-questions nếu cần người chốt.
- Ghi `decisions.md`:
  - **Đã chốt** chỉ dành cho điều doc ghi rõ là quyết định, hoặc người dùng / PM xác nhận trong cuộc trò chuyện. Ghi rõ người chốt.
  - Doc ghi rõ là quyết định nhưng không nói ai chốt: vẫn ghi **Đã chốt**, cột "Ai chốt" ghi `Doc PM <phiên bản>, <ngày>`. Không đoán tên người.
  - Phương án design đề xuất, chưa ai duyệt: **Đề xuất**.
  - Luôn điền cột "Phương án đã loại". Nếu không có thì ghi "—", đừng bỏ trống.
  - Quyết định chạm nhiều tính năng (đơn vị đo, ngày bắt đầu tuần, quy ước copy): ghi vào `decisions.md` **của dự án**. `decisions.md` của tính năng chỉ ghi một dòng trỏ tới đó, không chép lại nội dung.
- Ghi `open-questions.md`: mỗi câu có mã, người cần trả lời, ngày hỏi, và nhãn chặn design / không chặn design.

## Bước 6: Flowchart và copy

- Flowchart: dùng skill `flowchart`, lưu `design/<tính-năng>-flow.mmd` và `.html`. Chèn khối mermaid vào brief **ngay dưới H1**, bọc giữa `<!-- FLOWCHART:START -->` và `<!-- FLOWCHART:END -->`, kèm một dòng trỏ về file `.mmd`. Từ đó, mỗi lần sửa `.mmd` thì sửa luôn khối này.
- `copy/ui-copy.md`: chép copy từ Figma theo từng màn. Copy do PM sở hữu (notification, marketing) ghi "chờ PM", design không viết nháp. Copy lệch chuẩn thị trường thì ghi đề xuất ở cột Ghi chú.

## Bước 7: Handoff dev (chỉ khi tới bước bàn giao)

**Không tạo handoff trong lần dựng hồ sơ tính năng.** Lúc đó còn câu hỏi mở, và file handoff tạo sớm sẽ lệch dần với brief. Chỉ tạo khi:
- người dùng yêu cầu làm handoff; hoặc
- tính năng đã hết câu chặn design, và người dùng đồng ý chuyển sang bàn giao.

Ở lần dựng đầu, chỉ ghi vào phần trả lời trong chat rằng handoff sẽ làm sau.

Tạo `handoff/handoff-v<x.y.z>.md` theo `assets/handoff-template.md`. Đây là file sống: luôn sửa theo spec mới nhất. Chỉ tạo file version mới khi version trước đã chốt. Nội dung gồm:
- logic không nhìn thấy được trên Figma;
- điều kiện hiển thị từng state;
- tracking;
- danh sách điểm ⚠️ còn chờ;
- link section Figma.

## Bước 8: Cập nhật lối vào và sinh HTML

- `CLAUDE.md` tính năng: trạng thái, các quyết định chính, link tới brief và file mới nhất.
- `CLAUDE.md` dự án: cột trạng thái trong bảng Tính năng. `sources.md`: thêm nguồn mới (doc, section Figma).
- Sinh HTML cho file đọc được:
  ```bash
  python3 _tools/md_to_html.py <các file .md vừa tạo hoặc sửa>
  ```
  Không cần sinh cho `CLAUDE.md`.
- Dự án chưa có `_tools/md_to_html.py` (SoT dựng trước khi có bộ skill này): chạy bản dự phòng ở `<thư mục skill sot-init>/assets/project/_tools/md_to_html.py`, rồi đề nghị người dùng chép thư mục `_tools/` vào dự án. Không viết hay vá tay file `.html`.
- Có Git thì đề xuất commit `<tính-năng> v<x.y.z>: dựng hồ sơ tính năng`. Chỉ push khi người dùng đồng ý.

## Trả lời trong chat

Ngắn gọn:
- 5 thứ của "đủ sâu" đã đạt / chưa đạt;
- số frame, số AC, số quyết định Đã chốt / Đề xuất, số câu còn mở (bao nhiêu câu chặn design);
- lỗ hổng đáng lo nhất;
- link các file.

Gợi ý bước tiếp: chạy thử một task bằng `sot-audit` (bước 05) để xem trang tính năng đã đủ dùng chưa.

## Tài liệu kèm theo

- `scripts/new_feature.py`: dựng folder từ `assets/feature/` và đăng ký vào `CLAUDE.md` dự án.
- `assets/feature/`: template các file của tính năng.
- `assets/handoff-template.md`: khung handoff cho dev.
