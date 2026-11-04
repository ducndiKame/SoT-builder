---
name: figma-style-builder
description: Tạo Variables (Primitives → Semantic Light/Dark, tuỳ chọn Dimension) và bộ Text style trong Figma cho một dự án mới, theo khung đã dùng ở FitAgain, để mọi dự án có cùng tên token, cùng thang chữ và cùng page Foundations. Trước khi dựng, skill hỏi designer màu primary, có màu secondary không (dùng cho điểm nhấn hay cả nút phụ), dùng 1, 2 hay 3 font, font nào cho nhóm chữ nào, và quy tắc dùng font. Sau đó skill dựng hệ style theo đúng câu trả lời, chạy cổng contrast WCAG AA, rồi ghi vào Figma bằng script upsert (không xoá gì) và dựng page `02 Foundations` có swatch bind biến thật. Dùng skill này khi người dùng muốn "tạo variable cho file mới", "dựng token / style cho dự án mới", "tạo text style", "setup design token", "khởi tạo màu và typography", "làm style giống FitAgain cho app X", "đổi màu brand / font rồi cập nhật token", hoặc mở file Figma trống ở giai đoạn đầu dự án, kể cả khi họ không nói chữ "variable". KHÔNG dùng để audit hay viết tài liệu design system từ file đã có (đó là design-system-build), đặt lại tên layer (figma-design-rename) hay dựng component.
---

# Figma Style Builder

Dựng nền token và typography cho file Figma của một dự án mới theo **khung lấy từ FitAgain**, nhưng **hình dạng hệ style theo câu trả lời của designer**:

- dự án có màu secondary thì có thêm ramp `secondary` và nhóm token `accent`; không có thì không tạo;
- dự án dùng 1, 2 hay 3 font thì text style được gán font theo đúng phân vai designer chọn;
- font chỉ có vài weight, hoặc designer có quy tắc dùng font, thì bộ style được lọc theo đó và quy tắc được ghi lại.

Phần giữ cố định giữa các dự án: tên collection, tên nhóm token (`bg`, `text`, `action/primary`…), 10 bậc ramp 50–900, tên và thang cỡ của text style. Nhờ vậy designer, dev và AI tool gặp cùng `text/secondary`, cùng `Body/Medium/Regular` ở mọi file.

Ba nguyên tắc:

1. **Hỏi đủ rồi mới dựng.** Bốn câu bắt buộc (màu primary, có secondary không, mấy font và font nào, phân vai font) phải có câu trả lời của designer. Không đoán, không lấy mặc định cho bốn câu này. Câu trả lời được ghi vào `design-system/style-config.json`: file này là bản ghi "dự án chọn gì", chạy lại ra đúng kết quả cũ.
2. **Contrast được kiểm trước khi ghi.** Cổng contrast bắt các lỗi kiểu FitAgain từ ngày đầu (CTA trắng trên `primary/400` chỉ 2.89:1). Chỗ nào sửa tự động mà phá thứ bậc thì dừng cho designer quyết.
3. **Ghi vào Figma bằng upsert, không xoá.** Script tạo cái thiếu, cập nhật cái lệch, chỉ liệt kê biến / style ngoài spec.

## Khung

| Phần | Luôn có | Theo câu trả lời |
|---|---|---|
| `Primitives` (mode `Default`, scope rỗng, ẩn khi publish) | `white`, `black`, ramp `primary`, `neutral`, `success`, `warning`, `error`, `info` × 10 bậc = 62 | + ramp `secondary` (10) nếu có màu secondary; + ramp thêm (`colors.extra`) |
| `Semantic` (Light · Dark hoặc chỉ Light, mọi giá trị là alias) | `bg` 6 · `surface` 5 · `text` 11 · `icon` 8 · `border` 10 · `action/primary` 5 · `action/secondary` 5 (xám) · `feedback` 8 = 58 | + nhóm `accent` 6 token (`bg/accent`, `bg/accent-subtle`, `text/accent`, `text/on-accent`, `icon/accent`, `border/accent`); `action/secondary/*` chuyển sang màu secondary nếu designer muốn |
| `Dimension` | — | `spacing/0…64`, `radius/none…full` (20) |
| Text style | Thang cỡ của khung: `Display` 3 · `Heading/H1–H6` · `Body` 19 · `Label` 11 · `Caption` 5 · `Overline` 3 · `Link` 2 · `Code` 2 | Font của từng nhóm; nhóm bị bỏ (`null`); style bị lọc theo weight |
| Page `02 Foundations` | `Design Tokens / Light`, `Design Tokens / Dark` (nếu có Dark), `Typography` (có khối "Font usage" ghi phân vai và quy tắc font) | |

Vì sao token của màu secondary tên `accent`: trong khung, chữ "secondary" đã mang nghĩa thứ bậc (`text/secondary` = chữ phụ, `action/secondary` = nút phụ). Ramp vẫn tên `secondary` trong Primitives cho khớp cách designer gọi. Chi tiết: `references/structure.md`.

---

## Quy trình

### Bước 0: Phỏng vấn designer (bắt buộc, chưa xong thì không làm bước nào khác)

Hỏi theo hai vòng. Câu dạng lựa chọn hỏi bằng `AskUserQuestion` (tối đa 4 câu một lần). Giá trị tự do (mã hex, tên font, quy tắc) để người dùng gõ ở ô "Other" hoặc hỏi bằng tin nhắn thường. Không đoán màu từ ảnh chụp, không tự chọn font.

**Vòng 1: màu, số font và cấu hình chung**

| # | Câu hỏi | Lựa chọn / dạng trả lời | Bắt buộc |
|---|---|---|---|
| 1 | Link file Figma | URL | có |
| 2 | Màu primary là gì? | 1 mã hex (skill sinh ramp 50–900), hoặc đủ 10 mã nếu brand đã có ramp | có |
| 3 | Dự án có màu secondary không? | **Không** · **Có, chỉ làm điểm nhấn** (badge, tag, highlight, biểu đồ; nút phụ vẫn xám) · **Có, điểm nhấn + nút phụ** (`action/secondary/*` dùng màu secondary). Có thì hỏi thêm mã hex | có |
| 4 | Dùng mấy font? | **1 font** · **2 font** (tiêu đề + giao diện) · **3 font** (thêm font thứ 3: mono cho code, font số liệu, hoặc tách Display và Heading). Sau đó hỏi tên từng font | có |
| 5 | Có Dark mode không? | Có (mặc định) · Không. Gói Figma Free chỉ có 1 mode | mặc định được |
| 6 | Có tạo biến spacing / radius không? | Có (mặc định) · Không | mặc định được |
| 7 | Brand có màu success / warning / error / info riêng không? | Không (mặc định, dùng ramp của khung) · Có → mã hex | mặc định được |

**Vòng 2: phân vai font và quy tắc dùng font**

Đề xuất bảng phân vai mặc định theo số font (`baseline.json` → `text_styles.font_presets`), rồi hỏi designer xác nhận hoặc sửa:

| Nhóm | 1 font | 2 font | 3 font (mặc định) |
|---|---|---|---|
| Display, Heading | F1 | F1 | F1 |
| Body, Label, Caption, Overline, Link | F1 | F2 | F2 |
| Code | không tạo | không tạo | F3 |

Hỏi tiếp, gợi ý ví dụ để designer dễ trả lời:

- **Quy tắc dùng font**, ví dụ: "font tiêu đề chỉ dùng tới H3, H4–H6 dùng font giao diện" (gán `Heading/H4` riêng), "nút dùng font tiêu đề" (gán `Label` sang F1), "không dùng chữ in hoa" (bỏ `Overline`), "số liệu lớn dùng Display", "không dùng italic".
- **Weight được dùng** của từng font, ví dụ chỉ Regular và Bold. Style biến thể theo weight (`Body/Medium/Semi Bold`) bị bỏ; style đơn (`Heading/H4`) đổi sang weight gần nhất.
- **Dự án có hiển thị code không** (2 font thì `Code` mặc định không tạo; nếu cần thì gán font mono).
- Với 3 font: font thứ 3 dùng cho nhóm nào (Code, hay Display, hay một tiền tố cụ thể).

**Chốt cấu hình.** Ghi câu trả lời vào `design-system/style-config.json` theo mẫu `assets/style-config.example.json`, rồi cho designer xem bảng tóm tắt: primary, secondary (dùng cho gì), từng font và các nhóm của nó, weight, quy tắc, Dark mode, Dimension. Designer đồng ý mới sang bước 1. Quy tắc nói bằng lời (không tự áp được) ghi vào `fonts.rules`; quy tắc áp được thì đổi thành `assign` / `weights`, đồng thời vẫn ghi lời vào `rules` để người đọc hiểu vì sao.

### Bước 1: Đọc file Figma (read-only)

Nạp skill `figma-use` (hoặc resource `skill://figma/figma-use/SKILL.md`) trước lần gọi `use_figma` đầu tiên, rồi gọi `create_session`. Một call đọc gồm: danh sách collection (tên, mode, số biến), text style (tên), page, và **weight thật của từng font đã chọn** qua `figma.listAvailableFontsAsync()`.

- **Font không có trong Figma**: báo designer (cài font, hoặc chọn font Google Fonts khác), quay lại bước 0.
- **Font thiếu weight** mà khung cần: hỏi designer chấp nhận bỏ / đổi weight không, rồi ghi `fonts.weights` vào config.
- **File trống**: sang bước 2.
- **File đã có token / style**: dừng, báo những gì đang có. Upsert sẽ **ghi đè giá trị** của biến trùng tên. Các phương án:
  - (a) Token khác khung: chạy `design-system-build` để audit trước.
  - (b) File đã theo khung này (lần chạy trước): sang bước 2 với `style-config.json` cũ, xem bảng thay đổi.
  - (c) Thử trên một file copy trước.

### Bước 2: Sinh spec và báo cáo

```bash
py <skill>/scripts/build_tokens.py build --config design-system/style-config.json \
   --out design-system/tokens.json --report design-system/tokens-report.md
```

(`py` trên Windows, `python3` trên macOS. `<skill>` là `~/.claude/skills/figma-style-builder`.) Config sai (font trong `assign` không có trong `families`, nhóm chưa gán font, mã hex hỏng…) thì script dừng và báo đúng chỗ sai.

Script làm các việc sau:

- **Sinh ramp** cho màu brand. Màu brand được đặt nguyên ở bậc có độ sáng gần nhất; các bậc khác đi theo nhịp ramp primary của FitAgain (OKLCH). Ví dụ `#9F85FF` tái tạo đúng ramp FitAgain.
- **Neo token theo màu brand.** Khi brand sáng (vàng → bậc 200) hoặc đậm (navy → bậc 700), các token mang màu brand (`bg/brand`, `action/primary/*`, `border/brand`, `border/focus`, và nhóm tương ứng của secondary) dời theo, để nút đúng màu brand.
- **Chạy cổng contrast**: chữ ≥ 4.5:1, icon / viền control / focus ≥ 3:1, ở mọi mode. Chưa đạt thì dời bậc. Nếu dời mà trùng token cùng thứ bậc, cổng ghi vào **Cần designer quyết**.
- **Lọc text style** theo `assign` (font từng nhóm, `null` = bỏ nhóm) và `weights`.

**Điểm dừng bắt buộc.** Cho designer xem bốn phần của báo cáo:

- **Cấu hình**: kiểm lại lần cuối là đúng câu trả lời.
- **Gợi ý** (nếu có): brand sáng, chữ trắng không đạt. Phương án là `primaryOn: "dark"` / `secondary.on: "dark"` để giữ đúng màu brand trên nút.
- **Dời bậc** và **Cần designer quyết**: mỗi chỗ có 3 phương án (`set`, giới hạn nền, `keep` + ghi ngoại lệ).
- **Text style**: bảng nhóm → font → số style, style bị bỏ / đổi weight, quy tắc font.

Sửa `style-config.json` rồi chạy lại `build` tới khi designer đồng ý. Chưa đồng ý thì chưa ghi gì vào Figma.

### Bước 3: Ghi vào Figma

```bash
py <skill>/scripts/build_tokens.py emit --spec design-system/tokens.json --out-dir <scratchpad>/figma-style [--page "02 Foundations"] [--replace]
```

Lệnh sinh 3 file. Đọc từng file, rồi truyền **nguyên văn** nội dung làm `code` của `use_figma` (kèm `sessionId`, `skillNames: "figma-use"` hoặc `"resource:figma-use"`). Chạy đúng thứ tự và đọc kết quả sau mỗi file:

| File | Làm gì | Kết quả cần xem |
|---|---|---|
| `01-variables.js` | Upsert collection, mode, giá trị / alias, scope, code syntax, description | `errors` rỗng (lỗi mode = gói Figma không đủ mode), `conflicts` rỗng, `extras` |
| `02-text-styles.js` | Kiểm font trước, thiếu thì dừng mà chưa tạo gì. Tự dò tên style thật (`SemiBold` / `Semi Bold`…). Ghi description "dùng cho gì" theo nhóm | Không có `error`. Thiếu weight thì quay lại bước 0 (thêm `fonts.weights`) |
| `03-foundations.js` | Dựng page và các frame bind biến, khối "Font usage" | Frame đã có thì script dừng. Hỏi người dùng, rồi emit lại với `--replace` |

Mỗi file nằm dưới giới hạn 50.000 ký tự của `use_figma` (lệnh `emit` cảnh báo nếu vượt).

### Bước 4: Kiểm tra

- Chụp các frame vừa dựng bằng `get_screenshot`. Xem tile không tràn khung, chữ "Aa" đọc được, frame Dark đổi màu thật, và khối "Font usage" khớp câu trả lời.
- Gọi `get_variable_defs` trên frame `Design Tokens / Light`: phải trả đủ token kèm hex.
- Chạy lại `01` hoặc `02` lần hai: kết quả phải là `unchanged` toàn bộ.

### Bước 5: Ghi vào SoT

- `design-system/style-config.json` (câu trả lời của designer), `design-system/tokens.json`, `design-system/tokens-report.md` (+ `.html` bằng `_tools/md_to_html.py`). Đây là file sống, sửa tại chỗ, không có version trong tên.
- `design-system/README.md`, mục "Token và text style", gồm:
  - bảng khung với số thực tế;
  - màu primary / secondary và vai trò;
  - bảng font → nhóm;
  - **quy tắc dùng font** (lấy nguyên văn `fonts.rules`);
  - node ID các frame Foundations;
  - token đã dời, ngoại lệ đã `keep`;
  - lệnh `build` đã chạy.
- Quyết định chọn màu, font, phương án cho "Cần designer quyết" → `decisions.md`. Ngoại lệ contrast chưa ai chốt → `open-questions.md`, có owner.
- `sources.md`: thêm dòng page `02 Foundations` (link node).
- Khi dự án đã có vài màn, đề xuất `design-system-build` (chế độ tối thiểu) để viết luật dùng token.

## Cập nhật sau này

- **Đổi màu, font, phân vai, thêm / bỏ secondary:**
  1. Sửa `design-system/style-config.json` (hỏi lại đúng câu liên quan ở bước 0).
  2. Chạy `build`, xem báo cáo, rồi `emit`.
  3. Chạy `01` và `02`. Layer đang bind giữ nguyên binding, chỉ đổi giá trị.
  4. Chạy `03` với `--replace`.

  Bỏ secondary thì token `accent` cũ còn lại trong Figma (script không xoá) và hiện ở `extras`. Hỏi designer có xoá tay không.
- **Thêm token riêng của dự án** (vd `chart/*`): tạo tay theo quy ước tên và scope ở `references/structure.md`, ghi vào `design-system/README.md`.
- **Đổi khung cho mọi dự án:** sửa `assets/baseline.json` trong repo SoT-builder, chạy `install.py`, ghi lý do vào commit.

## Bẫy đã biết

- **Ghi đè giá trị trùng tên.** Luôn đọc file trước (bước 1).
- **Brand sáng + chữ trắng.** Cổng sẽ dời nút sang bậc tối, nút không còn đúng màu brand. Báo cáo có dòng **Gợi ý**; hỏi designer chọn `on: "dark"` hay chấp nhận nút đậm hơn.
- **Primitives không hiện trong picker.** Đây là cố ý: UI chỉ bind Semantic.
- **Scope `GAP`** trong Figma áp cho cả gap và padding của auto layout.
- **Hover / pressed ở Dark mode không qua cổng.** Nếu dự án cần thì thêm gate vào `baseline.json`.
- **`text/tertiary` trên nền xám** (`surface/elevated`) chỉ đạt 4.39:1 với ramp neutral của khung. Báo cáo sẽ hỏi. Phương án thường chọn: `"set": {"text/secondary:Light": "neutral/700"}`.
- **Font chưa có trong Figma, hoặc thiếu weight**: script 02 dừng trước khi tạo. Kiểm sớm ở bước 1 để khỏi phải hỏi lại designer.
- **`Display/Medium`, `Link/Medium`** là bậc cỡ chữ, không phải weight. Lọc weight chỉ bỏ style biến thể (cùng cỡ, khác weight); style đơn được đổi weight.
- **Không dùng `get_variable_defs` để kiểm kê.** Lệnh này chỉ trả biến đang bind trên node đã chọn.

## Không làm

Component, effect style (shadow), grid style, đặt tên layer, xoá hay đổi tên biến / style có sẵn, tài liệu luật dùng token (việc của `design-system-build`), chọn màu hay font thay designer.

## Tài liệu tham chiếu

| File | Khi nào đọc |
|---|---|
| `assets/style-config.example.json` | Mẫu ghi câu trả lời của designer (ví dụ là cấu hình tái tạo FitAgain), có chú thích từng khoá |
| `references/structure.md` | Khi cần giải thích khung, nhóm `accent`, neo màu brand, phân vai font, lý do lệch FitAgain |
| `assets/baseline.json` | Nguồn số liệu của khung: ramp, ánh xạ Light/Dark, khối secondary, anchor, scope, gate, thang chữ, preset font, code syntax |
| `scripts/build_tokens.py` | `build --config` và `emit`. Chỉ dùng thư viện chuẩn Python 3.8+ |
| `scripts/templates/*.js` | Mã gốc của 3 script `use_figma`. Sửa ở đây, không sửa file đã emit |
