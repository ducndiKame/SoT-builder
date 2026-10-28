# Bộ luật đặt tên — 7 tầng

Quy ước mặc định. **Nếu project đã có quy ước riêng thì quy ước đó thắng** — file này chỉ là mặc định khi chưa có gì.

Mục lục: [Nguyên lý](#nl) · [Cơ chế vs quy ước](#co) · [1 Page](#p1) · [2 Section](#p2) · [3 Screen](#p3) · [4 State](#p4) · [5 Layer](#p5) · [6 Component](#p6) · [7 Variant](#p7) · [8 Token](#p8) · [Registry](#reg)

---

<a id="nl"></a>
## Nguyên lý: một vocabulary, mọi bề mặt

```
Product
└─ Flow           luồng / tính năng lớn      Checkout
   └─ Sub-flow    bước, tab, hoặc chế độ     Payment
      └─ Screen   màn hình                   Card Form
         └─ State trạng thái                 Error
```

Một feature tên `Checkout` thì phải là `Checkout` ở mọi nơi: section `03 Checkout`, screen `Checkout / Payment / ...`, component `Pattern / Checkout Summary`. Section ghi "Checkout" mà screen ghi "Payment Flow" là vi phạm nặng nhất — nó làm mọi luật còn lại vô nghĩa.

<a id="co"></a>
## Cơ chế vs quy ước — phải phân biệt

Dấu `/` chỉ tạo cấu trúc **thật** ở một số nơi:

| Đối tượng | `/` tạo folder thật? |
|---|---|
| Component, Color/Text style, Variable | **Có** — folder trong Assets panel / style picker |
| Variant property | Không dùng `/` — Figma ép `Property=Value` |
| Page, Section, Frame, Layer | **Không** — chỉ là ký tự text, dùng để đọc và search |

Dùng `/` cho screen frame vẫn đúng, nhưng là mua **khả năng tra cứu**, không phải cấu trúc.

Hai cơ chế thật khác: component tên bắt đầu bằng `.` hoặc `_` **không xuất hiện** khi publish library. Page sort theo **thứ tự kéo thả**, không theo tên — đánh số là cho người đọc, và phải kéo cho khớp số.

---

<a id="p1"></a>
## 1. Page — `<NN> <Tên>`

```
00 Cover           01 Design           02 Foundations
03 Components      04 Prototype        05 Draft          06 Archive
```

Số hai chữ số để thêm page mới vẫn giữ thứ tự. Không cần đủ cả 7 — bỏ slot không dùng, đừng tạo page rỗng cho đủ bộ.

Page phân cách (một hàng dấu gạch) là hợp lệ và hữu ích, nhưng **biến nó thành thông tin**: `──────  NOT FOR HANDOFF  ──────` tốt hơn `------------------`.

File có version: `01 Design v1.0.0`.

<a id="p2"></a>
## 2. Section — `<NN> <Flow>`

```
01 Login        02 Plan        03 Workout       04 Progress
05 More         06 Water       07 Steps         08 Weight
```

Số mã hoá **thứ tự flow trong sản phẩm**, không phải thứ tự vẽ. PM và QA đọc file theo trình tự này nên nó phải khớp PRD.

Tên Flow ngắn, Title Case, danh từ. `06 Water` chứ không `Water tracker` — hậu tố "tracker" không thêm thông tin.

**Một section chứa hai flow là chấp nhận được** khi chúng nối liền nhau: `01 Login & Onboarding`. Lúc đó level 1 của screen dùng hai flow riêng (`Login / ...` và `Onboarding / ...`), và cả hai phải có trong Registry.

Sub-section không đánh số, tên trần. Gom từ 2 màn trở lên cho một sub-task → sub-section. Một màn → frame. **Không để icon/component/layer nằm trực tiếp trong section.**

<a id="p3"></a>
## 3. Screen frame — `<Flow> / <Sub-flow> / <Screen> — <State>`

` / ` (space hai bên) ngăn cấp taxonomy. ` — ` (em dash, space hai bên) tách state.

```
Checkout / Payment / Card Form — Default
Checkout / Payment / Card Form — Invalid
Home / Feed / Article List — Empty
```

**Đúng 3 cấp.** 4–5 cấp là lỗi thường gặp khi duplicate — `More / Settings / Profile List / Apple Health / Permission Request` phải rút về `More / Apple Health / Permission Request`.

**Vì sao tách state bằng dấu khác:** hai kiểu tìm kiếm cho hai người.
- Search `Checkout / Payment / Card Form` → mọi state của đúng màn đó (dev cần).
- Search `— Error` → mọi màn lỗi trong file (QA cần).

Nhét state vào chung level 3 thì mất khả năng thứ hai.

### Hậu tố trong ngoặc đơn

Biến thể của **cùng** một state. Ưu tiên mô tả có nghĩa hơn `(Variant N)`:

```
— Invalid (Expired Card)          ưu tiên: nói được nó khác ở đâu
— Default (Kg)  (Lb)              đơn vị
— Default (Full Scroll)           cùng màn nhưng frame cao hơn viewport
— Default (Signed Out)            điều kiện tài khoản
— Default (75.5 kg)               giá trị dữ liệu, khi nó chính là thứ phân biệt
— Default (Variant 2)             cuối cùng mới dùng, khi thật sự không phân biệt được
```

Ghép được: `— Default (Square Crop, Paused)`.

`(Variant 9)` trở lên là **tín hiệu cần dedup**, không phải thành tựu.

### Luồng theo bước

```
<Flow> / <Sub-flow> / Step <NN> <Mô tả> — <State>

Onboarding / Profile Setup / Step 01 Height — Default (Cm)
Onboarding / Result / Step 08 Fitness Summary — Default (BMI 31.2 Obese)
```

Hai chữ số để sort đúng từ bước 10. Giữ nguyên số của người thiết kế kể cả khi có lỗ hổng (1→5 rồi 8, 9) — hỏi, đừng tự đánh lại.

### Prefix ngoặc vuông — frame không phải bản thiết kế đang sống

Đặt **đầu tên**, và frame có prefix được miễn luật 3 cấp:

| Prefix | Dùng cho |
|---|---|
| `[Ref]` | Bản copy của màn thuộc flow khác, đặt ở đây làm điểm vào prototype. Giữ nguyên đường dẫn gốc phía sau: `[Ref] Plan / Home / Dashboard — First Run` |
| `[Note]` | Frame ghi chú, link tham khảo, câu hỏi để ngỏ |
| `[WIP]` | Mảnh đang dựng, chưa thuộc màn nào |
| `[iOS]` / `[Android]` | Màn hệ điều hành dùng làm tham chiếu: `[iOS] Photo Library — Reference` |
| `[Store]` / `[Marketing]` / `[QA]` | Bản copy cho App Store, marketing, hồi quy |

Không bao giờ để bản copy giữ y nguyên tên gốc — trong layer panel phải phân biệt được ngay đâu là bản đang maintain.

### Connector nối luồng prototype

Mũi tên/đường nối giữa các màn đặt tên có prefix emoji, ví dụ `🛠 Flows / Snake`, `🛠 Flows / Straight`. Dùng lại đúng instance và đúng tên khi thêm connector mới.

Đây **không phải màn hình**. Mọi script đếm màn, verify, hay rename phải lọc chúng ra — kiểm bằng `name.indexOf('\u{1F6E0}') === 0`. Quên lọc thì mọi con số thống kê đều sai.

### Screen ID — tuỳ chọn

`Checkout / Payment / Card Form — Error [CKO-PAY-03]`, format `<FLOW3>-<SUB3>-<NN>`, đặt **cuối** tên.

Chỉ bật khi QA có test case hoặc bug ticket trỏ đích danh màn. Không bật cho file explore — chỉ thêm việc maintain.

<a id="p4"></a>
## 4. Từ vựng State — danh sách đóng

Phần quan trọng nhất cho QA. Chỉ dùng đúng các từ này, không dùng đồng nghĩa.

| State | Khi nào |
|---|---|
| `Default` | Chuẩn, có dữ liệu bình thường |
| `Empty` | Không có dữ liệu — 0 item |
| `Loading` | Đang tải |
| `Error` | Lỗi hệ thống, server, timeout |
| `Invalid` | Lỗi validation do input người dùng |
| `Success` | Xác nhận hành động thành công |
| `Disabled` | Không thao tác được |
| `Offline` | Mất kết nối |
| `Permission Denied` | Bị từ chối quyền |
| `First Run` | Lần đầu mở, khác returning user |
| `Max Data` | Dữ liệu biên trên |
| `Long Content` | Text tràn, truncate |

Cấm `No data`, `Blank`, `Nothing here`, `Nodata` — tất cả là `Empty`.

Danh sách này cũng là **checklist thiết kế**: mỗi màn mới, rà 12 dòng và hỏi state nào áp dụng. Rẻ hơn nhiều so với để dev phát hiện thiếu.

Project thêm state riêng (`Goal Reached`, `Running`) thì ghi vào Registry trước khi dùng.

<a id="p5"></a>
## 5. Layer — vai trò, không phải hình thức

Kiểm tra nhanh: tên nói nó *làm gì* → đúng. Nói nó *trông thế nào* → sai. Hình thức sẽ đổi, vai trò thì không.

```
Blue Box      → Price Container        Rectangle 5  → Divider
Group 12      → Action Group           Big Card     → Featured Article Card
```

**Casing: Title Case, ngăn bằng dấu cách.** Không underscore, hyphen, camelCase.

### Từ vựng Role

```
Cấu trúc   Status Bar · Header · Content · Footer · Nav Bar · Tab Bar
           Safe Area · Scroll Area · Home Indicator
Danh sách  <X> List · <X> Item · <X> Row · <X> Cell · <X> Grid
Trạng thái Empty State · Loading State · Error State · Success State
Lớp nổi    Scrim · Sheet · Dialog · Toast · Tooltip · Popover · Menu
```

### Ba hậu tố gom nhóm — chọn theo bản chất

| Hậu tố | Khi nào | Ví dụ |
|---|---|---|
| `Group` | Cụm liên quan ngữ nghĩa, **không** có ranh giới thị giác | Title Group, Action Group |
| `Container` | **Có** ranh giới thị giác — nền, viền, bo góc, shadow | Price Container |
| `Wrapper` | Khung kỹ thuật thuần, chỉ để layout | Layout Wrapper |

### Text layer — lấy nội dung làm tên

Đây **đúng là hành vi mặc định của Figma**. Text layer tên `Heart Rate` mà nội dung là "Hi, Yolina" nghĩa là tên bị đóng băng từ lần tạo. Trả về nội dung thật, cắt 40 ký tự.

Ngoại lệ: layer chỉ chứa glyph (SF Symbols `􀆄`) — giữ nguyên, tên glyph vô nghĩa.

### Icon — `ic_snake_case`

```
ic_arrow_left · ic_flash · ic_close_fill · ic_plan_line
```

Ngoại lệ casing duy nhất ở tầng layer, vì icon sẽ export thành file cho dev và tên file theo snake_case.

Tên kiểu iconify (`mingcute:right-line`) → `ic_right_line`.

### Cấm tuyệt đối

Tên mặc định còn sót (`Frame 427`, `Group 12`, `Rectangle 5`, `Ellipse 3`), tên mô tả màu/kích thước (`Blue Bar`, `Big Text`), và hai layer cùng vai trò ở hai màn mà tên khác nhau.

<a id="p6"></a>
## 6. Component — `<Category> / <Component> / <Modifier>`

Bộ category nhỏ và cố định, đừng để phình:

| Category | Chứa gì |
|---|---|
| `Core` | Button, Input, Search Field, Checkbox, Radio, Toggle, Chip, Badge, Avatar, Icon |
| `Layout` | Card, List Item, Section Header, Divider, Accordion, Tile, Progress Ring |
| `Nav` | Nav Bar, Tab Bar, Header, Segmented Control, Breadcrumb, Pagination |
| `Feedback` | Toast, Alert, Dialog, Banner, Empty State, Skeleton, Progress |
| `Overlay` | Sheet, Popover, Menu, Tooltip, Scrim |
| `Pattern` | Component ghép, gắn với một feature cụ thể |

`Pattern` là nơi **duy nhất** tên feature xuất hiện trong component, và phải dùng đúng tên Flow trong Registry.

### Quy tắc cứng: state không nằm trong tên component

```
SAI                            ĐÚNG
Button / Primary / Hover   →   Core / Button
Button / Primary / Disabled    + Type=Primary | Secondary
Button / Secondary / Hover     + Size=SM | MD | LG
                               + State=Default | Hover | Disabled
```

Sai cách tạo ra hàng chục component rời không swap được. Đúng cách tạo một component set, dev map thẳng sang props.

### Base component ẩn

`.Button Base`, `.Input Base` — prefix dấu chấm, Figma không publish lên library.

### Component phải khớp code

Điều kiện để handoff không cần phiên dịch. `Core / Button` ↔ `<Button>`, `Layout / Card / Article` ↔ `<ArticleCard>`. Không khớp được thì phải có bảng mapping trong Registry.

<a id="p7"></a>
## 7. Variant property

Figma ép `Property=Value`. Phần cần chuẩn hoá là **chọn từ nào**.

| Property | Value |
|---|---|
| `Type` | Primary · Secondary · Tertiary · Ghost · Destructive |
| `Size` | XS · SM · MD · LG · XL (luôn viết tắt) |
| `State` | Default · Hover · Pressed · Focused · Disabled · Loading |
| `Theme` | Light · Dark (chỉ khi không dùng được variable mode) |
| `Orientation` | Horizontal · Vertical |
| `Platform` | iOS · Android · Web (chỉ khi thật sự khác) |

Boolean dùng tiền tố `Has` / `Is` / `Show`, value `True` / `False`: `Has Icon`, `Is Selected`, `Show Divider`.

Thứ tự: `Type` → `Size` → `State` → boolean. Thứ tự này hiện nguyên trong instance panel và trong thứ tự props dev đọc.

Casing Title Case — đây là thứ designer đọc trong panel. Dev tự map sang `hasIcon`.

**`Property 1` là lỗi phổ biến nhất.** Nhưng xem phần "Đừng đụng" trong SKILL.md: đổi property chạm mọi instance, phải là lượt riêng.

<a id="p8"></a>
## 8. Variable, Style, Token — `<category>/<role>/<variant>`

**lowercase, kebab-case, `/` không có space.** Ngoại lệ có chủ đích so với các tầng trên.

Logic casing toàn hệ thống:
- **Title Case + space** → thứ designer đọc trong layer panel (screen, layer, component, property).
- **lowercase + kebab + slash** → thứ dev đọc và export ra code (token, icon, asset).

Nhìn một cái tên là biết ngay nó thuộc tầng nào.

### Ba tier

```
1 Primitive    color/base/blue-500        giá trị thô, KHÔNG mang nghĩa
2 Semantic     color/text/primary         vai trò, dùng hằng ngày
3 Component    color/button/primary/bg    chỉ khi cần override riêng
```

**Designer chỉ apply Tier 2 và 3.** Tier 1 chỉ tồn tại để Tier 2 trỏ vào. Vi phạm thì dark mode và rebrand phải sửa tay từng layer.

### Category chuẩn

```
color/text/    primary secondary tertiary disabled inverse link error success
color/bg/      primary secondary tertiary elevated overlay inverse
color/border/  default subtle strong focus error
color/icon/    primary secondary disabled inverse accent
space/         0 4 8 12 16 24 32 48 64 96
radius/        none sm md lg xl full
size/icon/     16 20 24 32        size/tap/min = 48
type/          display heading body label caption
elevation/ duration/ easing/
```

### Tên phải semantic, không mô tả giá trị

```
color/text/dark-gray  →  color/text/primary      (dark mode làm tên tự mâu thuẫn)
color/bg/white        →  color/bg/primary
space/small           →  space/8                 (small là 4 hay 8?)
radius/8              →  radius/md
```

Token `space/` là ngoại lệ ngược: dùng **số thật**, vì nó là hệ 4pt và dev cần con số.

---

<a id="reg"></a>
## Naming Registry

Một frame trên page Foundations, tên `Naming Registry`. Bốn bảng:

1. **Flow list** — Flow và Sub-flow chính thức, kèm mã 3 chữ nếu dùng Screen ID.
2. **State vocabulary** — §4 cộng state riêng của project đã duyệt.
3. **Role vocabulary** — §5 cộng role mới phát sinh.
4. **Component ↔ Code mapping** — §6.

Registry là single source of truth. Thêm từ mới → ghi vào registry trước, dùng sau. Không có registry thì quy ước trôi trong vòng hai sprint.

---

## Khi phát hiện hai frame trùng tên — bốn trường hợp

Verify sẽ trả về danh sách tên trùng. Trùng **không mặc nhiên là lỗi** — phân loại trước khi sửa:

| Trường hợp | Dấu hiệu | Xử lý |
|---|---|---|
| **Copy-paste rồi quên đổi tên** | Nội dung giống hệt, không phân biệt được gì | Hợp nhất hoặc xoá bản dư, chỉ giữ một. **Không tự xoá** — đây là quyết định của người thiết kế, báo và để họ chọn |
| **Là state/variant thật khác nhau** | Nội dung khác ở một điểm cụ thể | Thêm hậu tố phân biệt có nghĩa: `(Filled)`, `(Signed Out)`, `(75.5 kg)` |
| **Khác ngữ cảnh sử dụng** | Một bản là thiết kế đang sống, bản kia dùng cho App Store / QA / marketing | Đổi namespace theo prefix `[Store]`, `[QA]`, `[Marketing]` |
| **Component dùng chung có chủ đích** | Cùng một bottom sheet được gọi từ nhiều entry point, hoặc `[Ref]` xuất hiện ở nhiều section | **Giữ tên giống nhau là ĐÚNG** — section đã phân biệt. Không cần sửa |

Trường hợp 4 là lý do script verify phải bỏ qua frame có prefix `[`. Nếu không, mỗi lần chạy lại sẽ báo hàng chục "lỗi" giả.

Hậu tố lên tới `(Variant 9)` trở đi luôn thuộc trường hợp 1, không phải trường hợp 2.

## Checklist khi đặt tên một thứ lẻ

Dùng khi đang thiết kế và vừa tạo một frame/layer mới — không phải khi rename hàng loạt.

1. Đây là tầng nào: Page, Section, Screen, Layer, Component, Property, hay Token?
2. Từ dùng ở level 1 và 2 đã có trong Naming Registry chưa? Chưa → thêm vào registry **trước**, dùng sau.
3. Screen: có hậu tố ` — <State>` không, state đó có nằm trong danh sách đóng §4 không, và có **đúng 3 cấp** `/` không?
4. Layer: tên mô tả **vai trò** hay mô tả **hình thức**? Vai trò này đã có tên chuẩn chưa — nếu rồi thì dùng lại đúng tên đó, đừng nghĩ tên mới.
5. Component: state có bị nhét vào tên thay vì để ở variant property không?
6. Token: có đang apply Tier 1 trực tiếp lên layer không?
7. Casing đúng tầng chưa — Title Case cho thứ designer đọc, lowercase/kebab cho thứ dev export?
8. Còn sót tên mặc định nào không (`Frame`, `Group`, `Rectangle`, `Vector`)?

Câu 4 là câu hay bị bỏ qua nhất, và nó là nguồn gốc số một khiến file mất nhất quán: cùng một vai trò nhưng mỗi lần đặt một tên khác.

## Áp dần cho file cũ rất lớn

Khi file quá lớn hoặc đang có nhiều người cùng làm, đừng rename toàn bộ một lượt — review history mất dấu và cả team mất phương hướng. Thứ tự đúng, mỗi bước một sprint:

1. **Variable và Style trước.** Ít việc nhất, ảnh hưởng lớn nhất, không phá cấu trúc file.
2. **Component.** Gộp các component bị tách theo state thành component set. Tốn thời gian nhất nhưng trả lại nhiều nhất cho dev.
3. **Screen frame.** Đổi tên **không** phá prototype — Figma giữ link theo node ID, không theo tên.
4. **Layer bên trong.** Làm dần khi đụng tới màn nào, không làm đại trà.

Trong lúc chuyển đổi, đánh dấu section đã chuẩn hoá bằng hậu tố ` ✓` để cả team biết vùng nào đã xong.

---

## Ai đọc gì — kiểm tra khi bàn giao

| Vai trò | Tìm gì | Tầng nào phục vụ |
|---|---|---|
| PM | Section number + Flow name | §2 — thứ tự section khớp PRD |
| Dev | Component name + property + token | §6 §7 §8 — map thẳng sang code |
| QA | Hậu tố `— <State>` + Screen ID | §3 §4 — quét đủ state, trỏ đúng màn |

Test bàn giao: hỏi dev "component này tên gì trong code" — phải hỏi lại là §6 chưa đạt. Hỏi QA "liệt kê mọi màn error" — phải cuộn tay là §4 chưa đạt.
