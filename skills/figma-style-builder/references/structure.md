# Khung token và text style (chuẩn FitAgain)

Nguồn: file Figma FitAgain (`D3U7RV0Wi8k05AbY8faRNj`), đọc qua Variables API ngày 2026-11-04: 2 collection, 120 biến, 51 text style. Số liệu máy đọc nằm ở `assets/baseline.json`. File này giải thích **vì sao** khung được dựng như vậy và cách mở rộng mà không phá tính đồng nhất.

## 1. Hai lớp màu

```
Primitives (1 mode)            Semantic (Light · Dark)            Layer trong UI
primary/400  #9F85FF   ◄──alias──  action/primary/default   ◄──bind──  nút chính
neutral/900  #111827   ◄──alias──  text/primary              ◄──bind──  tiêu đề
```

- **Primitives** là bảng màu thô: `white`, `black` và 6 ramp × 10 bậc. Không mang nghĩa, không có mode. Scope rỗng, nên designer không chọn được trong picker. Chỉ swatch tài liệu (page Foundations) bind vào lớp này.
- **Semantic** mang nghĩa ("chữ phụ", "nền nút chính"). Mọi giá trị là alias, nên đổi một bậc Primitives thì mọi token trỏ vào đều đổi theo. Đây là **lớp duy nhất UI được bind**: bind Primitive thì màn đó không đổi khi bật Dark mode.
- Ramp đặt tên theo bậc 50–900 (bậc càng cao càng tối). Ramp `primary` sinh từ màu brand; 5 ramp còn lại dùng chung giữa các dự án, trừ khi brand có màu trạng thái riêng (`--ramp success=#…`).

## 2. Nhóm Semantic: tên và vai trò

| Nhóm | Token | Dùng cho | Scope |
|---|---|---|---|
| `bg/*` | primary, secondary, tertiary, inverse, brand, brand-subtle | Nền vùng lớn của màn | Frame fill, shape fill |
| `surface/*` | default, elevated, overlay, sunken, disabled | Card, sheet, popover, ô nhập. FitAgain: màn nền `surface/elevated` xám, card `surface/default` trắng | Frame fill, shape fill |
| `text/*` | primary, secondary, tertiary, disabled, inverse, brand, success, warning, error, info, on-brand | Màu chữ. 3 bậc thứ tự primary → secondary → tertiary | Text fill |
| `icon/*` | primary, secondary, disabled, brand, success, warning, error, info | Icon vector | Shape fill, stroke |
| `border/*` | default, strong, subtle, disabled, brand, success, warning, error, info, focus | Viền, divider, focus ring. `default` / `subtle` là trang trí; `strong` cho viền control | Stroke |
| `action/primary/*`, `action/secondary/*` | default, hover, pressed, disabled, foreground | Nút. `foreground` là chữ + icon trên nút | Fill (state) · text/shape/stroke (foreground) |
| `feedback/<loại>/*` | bg, fg (success, warning, error, info) | Banner, toast. Luôn dùng theo cặp | Fill (bg) · text/shape/stroke (fg) |

Ánh xạ Light / Dark đầy đủ: `baseline.json` → `semantic` (mỗi dòng: tên, Light, Dark, mô tả). Mô tả được ghi vào description của biến nên hiện ngay trong picker.

**Thêm token riêng cho dự án** (vd biểu đồ, badge kế hoạch): thêm nhóm mới cùng cấp (`chart/*`, `badge/*`), alias sang Primitives, đặt scope theo bảng trên, và ghi vào `design-system/README.md` của dự án. Không chèn token mới vào nhóm có sẵn. Nếu token đó có ích cho mọi dự án, đề xuất thêm vào `baseline.json`.

## 3. Cổng contrast

`baseline.json` → `gates.list`, mỗi dòng: `[fg, bg, ngưỡng, bên được dời, token dời theo]`.

| Loại | Ngưỡng | Căn cứ |
|---|---|---|
| Chữ (`text/*`, `foreground`, `feedback/*/fg`) | 4.5:1 | WCAG 2.2 SC 1.4.3 |
| Icon, `border/strong`, `border/error`, `border/focus` | 3:1 | SC 1.4.11 |
| `*/disabled`, `border/default`, `border/subtle`, nền | miễn | Thành phần vô hiệu và trang trí được miễn |

Mỗi cặp được đo ở mọi mode, trên `bg/primary`, và với chữ phụ thì đo thêm trên `surface/elevated` (nền màn xám). Dời bậc theo hướng làm tăng contrast. `action/primary/hover` và `pressed` dời cùng số bậc với `default` để giữ nhịp trạng thái.

`gates.distinct` liệt kê các nhóm thứ bậc không được trùng bậc (`text/primary · secondary · tertiary`; `action/primary/default · hover · pressed`). Khi cổng phải dời một token lên trùng token cùng nhóm, nó dừng và hỏi designer.

Với chính FitAgain, cổng dời: `text/tertiary` (400 → 500), `action/primary/*` (400 → 600, hover 700, pressed 800), `bg/brand` (400 → 600), `border/strong` (400 → 500), `border/focus` (400 → 500). Còn một chỗ hỏi designer: `text/tertiary` trên nền xám. Đây chính là các lỗi đã ghi trong `DesignSystem.md` §2.6 của FitAgain.

## 4. Text style

Tên theo `Nhóm/Cỡ/Weight` (Title Case, có dấu cách trong `Semi Bold`). Line height ghi px, letter spacing ghi %.

| Nhóm | Font | Cỡ (size / line height) | Weight | Tracking |
|---|---|---|---|---|
| `Display/Large · Medium · Small` | display | 72/80 · 56/64 · 44/52 | Bold · Bold · SemiBold | −2% · −2% · −1% |
| `Heading/H1…H6` | display | 36/44 · 30/38 · 24/32 · 20/28 · 18/26 · 16/24 | Bold · SemiBold ×2 · Medium ×3 | −1% (H1, H2), 0 |
| `Body/XLarge · Large · Medium · Small · XSmall` | body | 20/32 · 18/28 · 16/24 · 14/22 · 12/18 | Regular · Medium · Semi Bold · Bold (XSmall không có Bold) | 0 |
| `Label/Large · Medium · Small` | body | 16/24 · 14/20 · 12/16 | 4 weight (Small không có Bold) | +1% |
| `Caption/*`, `Caption/Small/*` | body | 12/16 · 10/14 | Regular · Medium · Semi Bold / Regular · Medium | 0 · +1% |
| `Overline/Large · Medium · Small` | body | 14/20 · 12/16 · 10/14 | SemiBold · SemiBold · Medium | +8%, UPPER |
| `Link/Medium · Small` | body | 16/24 · 14/22 | Medium | 0, gạch chân |
| `Code/Block · Inline` | mono | 14/22 | Regular | 0 |

Vai trò font:
- **display**: font nhận diện cho Display, Heading và mọi con số lớn (timer, kcal, cân nặng). FitAgain dùng Lora (serif).
- **body**: font giao diện cho mọi thứ còn lại, kể cả nút và ô nhập.
- **mono**: chỉ để hiển thị code. Không có thì bỏ `Code/*`, đừng thay bằng font body.

Thang chữ nhắm tới màn mobile 375 pt. Dự án web có thể giữ nguyên thang và bổ sung style riêng theo đúng quy ước tên.

## 5. Dimension (tuỳ chọn)

`spacing/<px>` theo lưới 4pt (0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64), scope Gap. `radius/<cỡ>` (none 0 · xs 4 · sm 8 · md 12 · lg 16 · xl 24 · 2xl 32 · full 999), scope Corner radius. Spacing đặt tên theo px để không mơ hồ giữa các dự án. Radius đặt tên theo cỡ vì từng dự án có radius chữ ký khác nhau (FitAgain: 26 cho card). Muốn đổi thì sửa giá trị trong `tokens.json` của dự án, giữ nguyên tên.

## 6. Code syntax

Gắn cho mọi biến: WEB `var(--color-text-primary)` / `var(--spacing-16)`, iOS `Color.textPrimary` / `Dimension.spacing16`, Android `R.color.text_primary` / `R.dimen.spacing_16`. Mẫu nằm ở `baseline.json` → `code_syntax`. Nếu dev của dự án đã có quy ước khác, sửa `codeSyntax` trong `tokens.json` của dự án rồi emit lại.

## 7. Page Foundations

Page `02 Foundations` (thứ tự page FitAgain: `00 Cover`, `01 Design vX.Y.Z`, `02 Foundations`…), 3 frame rộng 1240:

- `Design Tokens / Light`: các nhóm Semantic (nền = swatch, chữ = "Aa", icon = chấm, viền = khung viền, action = nút, feedback = banner), Primitives theo ramp, Dimension.
- `Design Tokens / Dark`: cùng nội dung Semantic, frame đặt mode Dark.
- `Typography`: mỗi style một dòng (tên · mẫu chữ · thông số).

Frame do script sinh ra, không sửa tay: đổi token thì frame tự đổi theo, đổi khung thì chạy lại `03` với `--replace`.

## 8. Chỗ cố ý lệch FitAgain

Danh sách đầy đủ ở `baseline.json` → `deviations_from_fitagain`. Tóm tắt: scope theo nhóm thay cho `ALL_SCOPES`; có code syntax và description; contrast được sửa trước khi ghi; `Code/*` dùng font mono; có thêm tuỳ chọn Dimension. Tên, nhóm, ramp, thang chữ giữ nguyên.
