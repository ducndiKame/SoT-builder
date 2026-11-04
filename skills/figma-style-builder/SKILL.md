---
name: figma-style-builder
description: Tạo Variables (Primitives → Semantic Light/Dark, tuỳ chọn Dimension) và bộ Text style trong Figma cho một dự án mới, theo đúng khung đã dùng ở FitAgain, để mọi dự án có cùng tên token, cùng thang chữ và cùng page Foundations. Skill sinh ramp màu từ màu brand, chạy cổng contrast WCAG AA trước khi ghi, rồi ghi vào Figma bằng script upsert (không xoá gì) và dựng page `02 Foundations` có swatch bind biến thật. Dùng skill này khi người dùng muốn "tạo variable cho file mới", "dựng token / style cho dự án mới", "tạo text style", "setup design token", "khởi tạo màu và typography", "làm style giống FitAgain cho app X", "đổi màu brand rồi cập nhật token", hoặc mở file Figma trống ở giai đoạn đầu dự án, kể cả khi họ không nói chữ "variable". KHÔNG dùng để audit hay viết tài liệu design system từ file đã có (đó là design-system-build), đặt lại tên layer (figma-design-rename) hay dựng component.
---

# Figma Style Builder

Dựng nền token và typography cho file Figma của một dự án mới, theo **một khung cố định lấy từ FitAgain**. Mục tiêu là đồng nhất giữa các dự án: designer, dev và AI tool gặp cùng tên `text/secondary`, cùng `Body/Medium/Regular`, cùng page `02 Foundations` ở mọi file. Chỉ giá trị (màu brand, font) thay đổi theo dự án.

Ba nguyên tắc:

1. **Khung cố định, giá trị thay đổi.** Tên collection, nhóm, số bậc, thang chữ giữ y khung. Muốn đổi khung cho mọi dự án sau thì sửa `assets/baseline.json` trong repo SoT-builder. Muốn đổi cho một dự án thì dùng tham số `build` hoặc sửa `tokens.json` của dự án đó.
2. **Contrast được kiểm trước khi ghi.** FitAgain đã ship với 5 lỗi AA (CTA trắng trên `primary/400` 2.89:1, `text/tertiary` 2.55:1…). Cổng contrast bắt các lỗi này từ ngày đầu. Chỗ nào sửa tự động mà phá thứ bậc thì dừng lại cho designer quyết, không tự chọn.
3. **Ghi vào Figma bằng upsert, không xoá.** Script tạo cái thiếu, cập nhật cái lệch, và chỉ liệt kê biến/style ngoài spec. Spec đã áp được lưu vào SoT (`design-system/tokens.json`) để lần sau chạy lại ra đúng kết quả.

## Khung

| Phần | Nội dung | Số lượng |
|---|---|---|
| Collection `Primitives` | mode `Default`; `white`, `black` + 6 ramp × 10 bậc (`primary`, `neutral`, `success`, `warning`, `error`, `info` · 50–900). Scope rỗng, ẩn khi publish | 62 |
| Collection `Semantic` | mode `Light` · `Dark`, mọi giá trị là alias sang Primitives. Nhóm `bg` 6 · `surface` 5 · `text` 11 · `icon` 8 · `border` 10 · `action/primary` 5 · `action/secondary` 5 · `feedback/*/bg,fg` 8 | 58 |
| Collection `Dimension` (tuỳ chọn) | `spacing/0…64`, `radius/none…full` | 20 |
| Text style | `Display` 3 · `Heading/H1–H6` (font display) · `Body` 19 · `Label` 11 · `Caption` 5 · `Overline` 3 · `Link` 2 (font body) · `Code` 2 (font mono, bỏ nếu không cần) | 51 |
| Page `02 Foundations` | `Design Tokens / Light`, `Design Tokens / Dark`, `Typography`: mọi swatch bind biến thật | 3 frame |

Chi tiết từng token, lý do và các chỗ cố ý lệch FitAgain: `references/structure.md`.

---

## Quy trình

### Bước 0: Hỏi đầu vào

Hỏi ngắn, gom một lần. Không đoán màu brand từ ảnh chụp.

| Hỏi | Mặc định nếu người dùng không có ý kiến |
|---|---|
| Link file Figma (file mới hay file đang có màn) | bắt buộc |
| Màu brand chính (hex). Đã có sẵn ramp 10 bậc chưa? | bắt buộc |
| Font display (tiêu đề, số lớn) và font body (giao diện) | bắt buộc |
| Có hiển thị code không → font mono | không, bỏ `Code/*` |
| Có Dark mode không | có (`light,dark`) |
| Có tạo biến spacing / radius không | có (`--dimension`) |
| Màu success / warning / error / info riêng của brand | dùng ramp của khung |

Gói Figma giới hạn số mode: gói Free chỉ có 1 mode, nên chỉ làm được `--modes light`. Gói Professional có tối đa 4 mode.

### Bước 1: Đọc file Figma (read-only)

Nạp skill `figma-use` (hoặc resource `skill://figma/figma-use/SKILL.md`) trước lần gọi `use_figma` đầu tiên, rồi gọi `create_session`. Một call đọc: danh sách collection (tên, mode, số biến), text style (tên), page.

- **File trống** (không có collection, không có style): sang bước 2.
- **File đã có token / style:** dừng lại, báo người dùng những gì đang có. Script upsert **sẽ ghi đè giá trị** của biến trùng tên. Phương án:
  (a) file có token khác khung → chạy `design-system-build` để audit trước, rồi mới quyết có chuyển sang khung này không;
  (b) file đã theo khung này (lần chạy trước) → bước 2 với đúng tham số cũ, xem bảng thay đổi trước khi ghi;
  (c) thử trên một file copy trước.
  Skill không bao giờ đổi tên hay xoá biến / style có sẵn.

### Bước 2: Sinh spec và báo cáo

```bash
py <skill>/scripts/build_tokens.py build --project "<Tên app>" \
   --primary "#9F85FF" --display-font "Lora" --body-font "Be Vietnam Pro" [--mono-font "JetBrains Mono"] \
   [--modes light] [--dimension] [--ramp success=#22C55E] [--ramp-hex primary=#..,..(10 mã)] [--add-ramp accent=#FF7A59] \
   [--set text/secondary:Light=neutral/700] [--keep bg/brand] \
   --out design-system/tokens.json --report design-system/tokens-report.md
```

(`py` trên Windows, `python3` trên macOS. `<skill>` là `~/.claude/skills/figma-style-builder`.)

- Màu brand được đặt nguyên ở bậc có độ sáng gần nhất. Các bậc khác đi theo đường sáng/độ bão hoà của ramp primary FitAgain (OKLCH), nên ramp mới có cùng "nhịp" với FitAgain. Kiểm chứng: `--primary "#9F85FF"` tái tạo đúng 10 mã primary của FitAgain.
- Cổng contrast (`baseline.json` → `gates`): chữ ≥ 4.5:1, icon / viền control / focus ≥ 3:1, đo ở mọi mode. Chưa đạt thì dời token sang bậc kế tiếp. Nếu bậc mới trùng token cùng thứ bậc (vd `text/tertiary` trùng `text/secondary`), cổng không dời mà ghi vào mục **Cần designer quyết**.

**Điểm dừng bắt buộc.** Đưa người dùng xem 3 phần của báo cáo: bảng **Dời bậc so với khung**, mục **Cần designer quyết** (nếu có) và dòng font. Mỗi chỗ cần quyết có sẵn 3 phương án: dời token cùng nhóm bằng `--set`, giới hạn nền được dùng, hoặc `--keep` kèm ghi ngoại lệ. Chạy lại `build` tới khi người dùng đồng ý. Chưa đồng ý thì chưa ghi gì vào Figma.

### Bước 3: Ghi vào Figma

```bash
py <skill>/scripts/build_tokens.py emit --spec design-system/tokens.json --out-dir <scratchpad>/figma-style [--page "02 Foundations"] [--replace]
```

Lệnh sinh 3 file. Đọc từng file, rồi truyền **nguyên văn** nội dung làm `code` của `use_figma` (kèm `sessionId`, `skillNames: "figma-use"` hoặc `"resource:figma-use"`). Chạy đúng thứ tự, đọc kết quả trả về sau mỗi file:

| File | Làm gì | Kết quả cần xem |
|---|---|---|
| `01-variables.js` | Upsert 3 collection, mode, giá trị / alias, scope, code syntax, description | `errors` rỗng (lỗi mode = gói Figma không đủ mode), `conflicts` rỗng, `extras` |
| `02-text-styles.js` | Kiểm font trước, thiếu thì dừng mà chưa tạo gì. Tự dò tên style thật (`SemiBold` / `Semi Bold`…) | Không có `error`. Nếu thiếu font: báo người dùng cài font hoặc đổi font, rồi build lại |
| `03-foundations.js` | Dựng page và 3 frame bind biến | Frame đã có thì script dừng. Hỏi người dùng, rồi emit lại với `--replace` |

Mỗi file nằm dưới giới hạn 50.000 ký tự của `use_figma` (lệnh `emit` cảnh báo nếu vượt).

### Bước 4: Kiểm tra

- `get_screenshot` 3 frame vừa dựng. Xem: tile không tràn khung, chữ "Aa" đọc được, frame Dark đổi màu thật.
- `get_variable_defs` trên frame `Design Tokens / Light` phải trả đủ token kèm hex. Từ đây, mọi AI tool sau này lấy token qua frame này trong một call.
- Chạy lại `01` hoặc `02` lần hai: kết quả phải là `unchanged` toàn bộ. Nếu không, script đang ghi lệch giá trị.

### Bước 5: Ghi vào SoT

- `design-system/tokens.json` và `design-system/tokens-report.md` (+ `.html` bằng `_tools/md_to_html.py`). Không dùng version trong tên file: đây là file sống, sửa tại chỗ.
- `design-system/README.md`, mục "Token và text style": khung (bảng ở trên, kèm số thực tế), node ID của 3 frame Foundations, các token đã dời so với khung, ngoại lệ đã `--keep`, lệnh `build` đầy đủ đã chạy (để lần sau chạy lại đúng như vậy).
- Quyết định chọn màu và phương án cho mục "Cần designer quyết" → `decisions.md`. Ngoại lệ contrast chưa ai chốt → `open-questions.md`, có owner.
- `sources.md`: thêm dòng page `02 Foundations` (link node).
- Khi dự án đã có vài màn, đề xuất `design-system-build` (chế độ tối thiểu) để viết luật dùng token.

## Cập nhật sau này

- **Đổi màu brand hoặc font:** chạy lại `build` với lệnh trong `design-system/README.md`, chỉ đổi tham số cần đổi → xem bảng dời bậc → `emit` → chạy `01` và `02` (layer đang bind giữ nguyên binding, chỉ đổi giá trị) → `03` với `--replace`.
- **Thêm token riêng của dự án** (vd `chart/*`): tạo tay trong Figma theo đúng quy ước tên và scope ở `references/structure.md`, rồi ghi vào `design-system/README.md`. Script không xoá biến ngoài spec, chỉ liệt kê ở `extras`.
- **Đổi khung cho mọi dự án:** sửa `assets/baseline.json` trong repo SoT-builder, chạy `install.py`, ghi lý do vào commit.

## Bẫy đã biết

- **Ghi đè giá trị trùng tên.** Đọc file trước (bước 1). Đây là lý do upsert không bao giờ chạy mù trên file đang có màn.
- **Primitives không hiện trong picker.** Đây là cố ý: UI chỉ bind Semantic. Swatch tài liệu vẫn bind Primitives được qua script.
- **Scope `GAP`** trong Figma áp cho cả gap và padding của auto layout.
- **Hover / pressed ở Dark mode không qua cổng.** Chúng sáng dần từ `default` nên chữ trắng có thể dưới 4.5:1. Báo cáo không đo cặp này. Nếu dự án cần thì thêm gate vào `baseline.json`.
- **`text/tertiary` trên nền xám** (`surface/elevated`) với ramp neutral của khung chỉ đạt 4.39:1 ở bậc 500. Báo cáo sẽ hỏi designer. Phương án thường chọn: `--set text/secondary:Light=neutral/700` để `text/tertiary` xuống được `neutral/600`.
- **Font chưa có trong Figma** (font không thuộc Google Fonts, chưa cài máy): script 02 dừng trước khi tạo, liệt kê font và style đang có.
- **Không dùng `get_variable_defs` để kiểm kê.** Lệnh này chỉ trả biến đang bind trên node đã chọn. Kiểm kê bằng Variables API, hoặc gọi trên frame Foundations.

## Không làm

Component, effect style (shadow), grid style, đặt tên layer, xoá hay đổi tên biến / style có sẵn, tài liệu luật dùng token (việc của `design-system-build`).

## Tài liệu tham chiếu

| File | Khi nào đọc |
|---|---|
| `references/structure.md` | Khi cần giải thích khung, ánh xạ Semantic, lý do lệch FitAgain, hoặc thêm token tay đúng quy ước |
| `assets/baseline.json` | Nguồn số liệu của khung: ramp, ánh xạ Light/Dark, scope, gate, thang chữ, code syntax |
| `scripts/build_tokens.py` | `build` và `emit`. Chỉ dùng thư viện chuẩn Python 3.8+ |
| `scripts/templates/*.js` | Mã gốc của 3 script `use_figma`. Sửa ở đây, không sửa file đã emit |
