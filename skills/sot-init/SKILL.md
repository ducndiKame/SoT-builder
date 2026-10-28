---
name: sot-init
description: Dựng SoT (Source of Truth, nguồn sự thật) cho một dự án design mới, hoặc cho dự án đang chạy mà chưa có SoT. Skill phỏng vấn ngắn, gom mọi nguồn vào sources.md, gắn nhãn bản hiện hành / cũ / còn mở, tạo khung README + CLAUDE.md + decisions + context + design-system, rồi khởi tạo Git và private repo. Dùng skill này mỗi khi người dùng nói "tạo SoT", "dựng SoT cho dự án mới", "bắt đầu dự án mới", "tạo folder dự án", "khởi tạo cấu trúc tài liệu cho app X", "gom nguồn dự án", "đưa dự án lên Git / GitHub", hoặc mở một thư mục trống / thư mục toàn file rời rạc và muốn sắp lại để làm việc với AI, kể cả khi họ không nói chữ "SoT". KHÔNG dùng để thêm một tính năng vào SoT đã có (dùng sot-feature), cập nhật sau khi chốt quyết định (sot-sync) hay kiểm tra SoT (sot-audit).
---

# SoT Init: dựng SoT phase 1 cho dự án

SoT là tủ hồ sơ có chỉ mục của dự án. Khi ai đó hỏi "đúng là gì?", họ biết mở ở đâu, xem nguồn nào và thấy ngày quyết định. Skill này làm các bước 01–03 và bước 07 trong quy trình 8 bước:

| Bước | Việc | Đầu ra |
|---|---|---|
| 01 Gom | Liệt kê mọi nguồn đang có | `sources.md` bản nháp |
| 02 Chọn | So sánh, gắn nhãn hiện hành / cũ / còn mở | Bảng mâu thuẫn chờ owner chốt |
| 03 Dựng | Lối vào và cây folder tối thiểu | `README.md`, `CLAUDE.md`, `context/`, `design-system/` |
| 07 Git | Lưu lịch sử và bản từ xa | Commit nền + private repo |

Bước 04 (làm trọn một tính năng) là việc của `sot-feature`. Bước 05–06 là `sot-audit` và `sot-sync`. Bước 08 là `sot-handoff`.

## Nguyên tắc

1. **Không chọn nguồn đúng thay owner.** Claude được phép so sánh và chỉ ra chỗ lệch. Quyền quyết định bản nào có hiệu lực thuộc về người có trách nhiệm. Khi hai nguồn mâu thuẫn, ghi cả hai vào bảng "Mâu thuẫn chờ chốt", không âm thầm chọn một phía.
2. **Tách "nguồn ghi" với "tôi suy ra".** Chỗ chưa có nguồn thì ghi **Còn mở** hoặc để trống kèm câu hỏi. Đừng điền tệp user, màu brand hay tên PM theo phỏng đoán. AI sau này sẽ đọc phỏng đoán đó như sự thật.
3. **Nhỏ mà có lối vào tốt hơn lớn mà rỗng.** Không tạo folder rỗng chỉ để trông đầy đủ. `research/` và `_archive/` chỉ được tạo khi có nội dung thật.
4. **Không di chuyển hay xoá file của người dùng khi chưa hỏi.** Với dự án đang chạy, thư mục cũ có thể chứa thứ họ cần.

## Bước 0: Kiểm tra hiện trạng

- Thư mục đích đã có `CLAUDE.md` chứa marker `<!-- FEATURES -->` thì SoT đã tồn tại. Dừng lại và đề xuất `sot-audit` để kiểm tra, hoặc `sot-feature` để thêm tính năng.
- Thư mục có sẵn nhiều file rời rạc (dự án đang chạy) thì chạy ở **chế độ chuyển đổi**: dựng khung SoT bên cạnh, liệt kê file cũ vào `sources.md`, rồi đề xuất xếp từng file vào đâu. Chỉ chuyển file khi người dùng đồng ý.
- Kiểm tra công cụ: `python3 --version`, `git --version`, `gh --version`. Thiếu công cụ nào thì xem `references/git-workflow.md` phần cài đặt. Thiếu Git vẫn dựng khung được; bước 07 làm sau.

**Lệnh Python theo hệ điều hành:** các lệnh trong skill viết `python3` (macOS / Linux). Trên Windows thay bằng `py`. Đừng gõ `python3` trên Windows, vì lệnh đó có thể mở Microsoft Store thay vì chạy Python.

## Bước 1: Phỏng vấn ngắn

Hỏi bằng AskUserQuestion, tối đa 4 câu một lần. Những gì đã có trong cuộc trò chuyện hoặc trong file thì không hỏi lại.

| Cần biết | Vì sao |
|---|---|
| Tên dự án, thư mục đặt dự án | Tên thư mục và tiêu đề các file |
| Loại sản phẩm: **mới** / **đã chạy** / **nhiều dòng hoặc nền tảng** | Quyết định độ sâu (bảng dưới) |
| Nền tảng, thị trường, ngôn ngữ UI copy | Ghi vào quy ước chung |
| Link Figma chính (file, page, section) | Nguồn UI; version trong tên file lấy theo Figma |
| Doc PM ở đâu, đọc bằng gì (portal, Google Docs, file) | Tham số cho `spec-review` |
| Ai chốt được gì (PM, lead), cách xưng hô khi gửi PM | `context/stakeholders.md` |
| Tệp người dùng cuối | **Hỏi, không suy từ Figma.** Tệp user quyết định nhiều luật thiết kế |

Độ sâu theo loại sản phẩm:
- **Sản phẩm mới:** một brief, một design system nền, một feature mẫu. Bắt đầu mỏng, cập nhật khi học thêm.
- **Sản phẩm đã chạy:** thêm màn hiện tại, AC, quyết định, bản cũ. Ghi rõ bản nào đang hiệu lực. Version trong tên file phân biệt bản đã ship với bản đang làm.
- **Nhiều dòng / nền tảng:** ghi phần dùng chung trước (`context/`, `design-system/`, `decisions.md` cấp dự án), rồi ghi khác biệt cho từng dòng để tránh bản sao lệch nhau.

## Bước 2: Dựng khung

Chạy script trong skill này (đường dẫn tính từ thư mục skill):

```bash
python3 scripts/new_project.py --dest "<thư mục cha>" --name "<Tên dự án>" \
  --set STAGE="discovery" --set PLATFORM="iOS" --set FIGMA_URL="<link>" \
  --set PRODUCT_ONE_LINER="<...>" --set AUDIENCE_ONE_LINER="<...>" \
  --set COPY_LOCALE="en-US" --set PM_DOC_SOURCE="<...>" --set PM_NAME_AND_TONE="<...>"
```

Script không ghi đè thư mục đã có. Nó in ra hai loại placeholder còn trống, kèm file và số dòng:
- `{{KEY}}`: giá trị một dòng, truyền được bằng `--set`.
- `<...>`: ô trong bảng hoặc đoạn mẫu, ví dụ `<designer>` trong `sources.md` hay `<...>` trong `context/stakeholders.md`.

Điền cả hai loại bằng Edit sau phỏng vấn. Chỗ không có câu trả lời thì thay bằng `Còn mở: <câu hỏi>`, không để nguyên placeholder. Dòng mẫu không áp dụng cho dự án thì xoá.

Khung tạo ra: `README.md` (lối vào cho người), `CLAUDE.md` (lối vào cho AI, dưới 100 dòng), `sources.md`, `decisions.md`, `context/`, `design-system/README.md`, `features/README.md`, `_tools/` (script sinh `.html`), `.gitignore`, `.gitattributes`.

## Bước 3: Gom nguồn (bước 01)

Mục tiêu là danh sách đầy đủ. Ở bước này chưa cần biết nguồn nào đúng.

- Liệt kê mọi nguồn người dùng đưa: Figma, doc PM, ticket, research, biên bản họp, chat, bản đã ship.
- Figma: đọc danh sách page và section bằng `get_metadata`. Nếu chỉ thấy một page, thử thêm `nodeId: "0:1"` rồi mới kết luận file ít page. Ghi tên section kèm version (ví dụ `V1.0.1`) vì version trong tên file sẽ lấy theo đó.
- Mỗi nguồn một dòng trong `sources.md`, gồm link, loại, owner, ngày hoặc phiên bản, mục đích sử dụng, và ai cần quyền truy cập.
- Chưa biết owner hay ngày thì ghi "Còn mở", và thêm câu hỏi vào mục "Còn thiếu".

## Bước 4: Chọn bản hiện hành (bước 02)

- Gom các nguồn nói về cùng một chủ đề, ví dụ hai bản doc của cùng một tính năng, hoặc doc và Figma.
- Gắn nhãn cho từng nguồn:
  - **Hiện hành:** đang có hiệu lực.
  - **Cũ:** ghi rõ bị bản nào thay.
  - **Còn mở:** chưa biết bản nào đúng.
- Không dùng ngày của file làm căn cứ duy nhất. Bản mới hơn có thể là bản nháp bị bỏ.
- Một nguồn chỉ đúng **một phần** là chuyện thường. Ví dụ PRD v2 còn là nháp nhưng có mục mới mà v1 không có. Khi đó:
  - gắn nhãn nguồn theo vai trò chính của nó: v1 đã duyệt là **Hiện hành**, v2 nháp là **Còn mở**;
  - ở cột "Dùng để", ghi rõ phần nào của nguồn đang được dùng;
  - từng điểm lệch cụ thể vẫn vào bảng mâu thuẫn. Không gắn nhãn chung để che chỗ lệch.
- Mâu thuẫn cụ thể (một con số, một rule, một luồng) ghi vào bảng "Mâu thuẫn chờ chốt". Cột "Các nguồn nói gì" liệt kê **mọi** nguồn có ý kiến, không chỉ hai. Mỗi nguồn một dòng con, gồm trích dẫn và vị trí, ví dụ `PRD v1 §3: "20 recipes"` · `PRD v2 nháp: "10"` · `Họp 12/10: "chắc 15"`. Sau đó hỏi người dùng ai là người chốt, hoặc họ có chốt luôn được không.
- Người dùng chốt ngay thì ghi vào `decisions.md` với trạng thái **Đã chốt**, ghi tên người chốt, và điền cột "Phương án đã loại". Chưa chốt thì để nguyên trong bảng mâu thuẫn.

So sánh sâu từng tính năng (doc PM với Figma, từng AC) là việc của `spec-review` và `sot-feature`. Ở bước này chỉ cần đủ để biết nguồn nào làm nền.

## Bước 5: Context và design system tối thiểu

- `context/brand-and-audience.md` và `context/stakeholders.md`: điền từ phỏng vấn và nguồn. Mỗi ý ghi nguồn.
- `design-system/README.md`: ở phase 1 chỉ cần đủ cho feature mẫu. Nếu file Figma có Variables hoặc style, đề xuất chạy skill `design-system-build` ở **chế độ tối thiểu**: chỉ lấy token và component mà feature mẫu dùng. Bản đầy đủ để dành khi dự án lớn hơn.

## Bước 6: Sinh bản HTML

Làm trước bước Git, để commit nền có đủ bản `.html`. Sinh `.html` cho các file người khác sẽ đọc:

```bash
python3 _tools/md_to_html.py README.md sources.md decisions.md context/*.md design-system/README.md
```

Chạy lệnh này trong thư mục dự án. Không cần sinh cho `CLAUDE.md`.

## Bước 7: Git và private repo (bước 07)

Đọc `references/git-workflow.md` trước khi làm bước này.

1. **Quét bí mật trước khi commit.** Tìm token, mật khẩu, khoá API và file `.env`. Gặp thì dừng lại và báo người dùng. Private chỉ giới hạn người xem, không thay thế quy tắc bảo mật.
2. `git init`, rồi commit nền với message `Khởi tạo SoT <tên dự án>`.
3. **Hỏi trước khi tạo repo trên GitHub.** Đây là thao tác ra bên ngoài. Mặc định là private, tên repo gợi ý `<TenDuAn>-SoT`. Người dùng đồng ý thì chạy:
   ```bash
   gh repo create <owner>/<TenDuAn>-SoT --private --source . --push
   ```
4. Nếu người dùng chưa đăng nhập `gh` thì hướng dẫn `gh auth login --web` và `gh auth setup-git`. Không bao giờ xin token qua chat.

## Bước 8: Báo cáo

- Báo cáo trong chat, ngắn gọn:
  - đã tạo gì, link tới các file chính;
  - có bao nhiêu nguồn, bao nhiêu mâu thuẫn đang chờ chốt và ai chốt;
  - những gì còn "Còn mở";
  - trạng thái Git (đã commit, đã push hay chưa).
- Đề xuất bước tiếp theo: chọn **một** tính năng nhỏ làm feature mẫu, rồi chạy `sot-feature`. Không đề xuất làm tất cả tính năng một lúc.

## Tài liệu kèm theo

- `scripts/new_project.py`: dựng khung từ `assets/project/`.
- `assets/project/`: template của khung dự án. Sửa template ở đây sẽ áp cho các dự án tạo sau, dự án cũ không bị ảnh hưởng.
- `references/git-workflow.md`: cài Git và GitHub CLI theo hệ điều hành, đăng nhập, nhịp pull–commit–push, xử lý conflict. Đọc trước bước 7.
- `assets/project/_tools/md_to_html.py`: bản gốc của script sinh HTML. Các skill khác dùng bản này làm dự phòng khi dự án chưa có `_tools/`.
