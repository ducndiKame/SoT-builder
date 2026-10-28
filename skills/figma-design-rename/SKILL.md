---
name: figma-design-rename
description: Đặt lại tên toàn bộ một file Figma có sẵn — page, section, screen frame, layer, component, variant, variable — theo một quy chuẩn phân cấp nhất quán, bằng cách đọc nội dung thật bên trong từng màn rồi ghi hàng loạt qua Figma MCP. Dùng skill này khi người dùng muốn rename / dọn tên / chuẩn hoá / audit tên trong file Figma, kể cả khi họ chỉ nói "file loạn tên quá", "đặt tên lại giúp tôi", "dev đang hỏi màn này tên gì", "layer toàn Frame 427", "chuẩn hoá lại file trước khi bàn giao", hay dán link Figma kèm yêu cầu dọn dẹp. Cũng dùng khi người dùng vừa thêm section/màn mới vào một file đã chuẩn hoá và cần áp tiếp cho phần mới. KHÔNG dùng để thiết kế màn mới (đó là figma-flow-design) hay dựng tài liệu design system (đó là design-system-build).
---

# Figma Design Rename

Đổi tên một file Figma đang sống. Đây là thao tác **ghi hàng loạt, khó hoàn tác**, chạm tới hàng nghìn node, và đầu ra được PM/Dev/QA đọc mỗi ngày. Nên quy trình quan trọng hơn bộ luật.

Ba nguyên tắc chi phối mọi bước bên dưới:

1. **Không bao giờ tin tên frame.** Tên là thứ đang sai — đó là lý do có công việc này. Sự thật nằm ở `characters` bên trong. Xem §2.
2. **Đặt đúng, không chỉ đặt cho đúng format.** Đổi `DAILY CALORIES BURN/No data` thành `Plan / Calories / Daily Burn — Empty` mà không mở ra xem thì chỉ là làm đẹp một cái sai.
3. **Không đụng thứ đã đúng.** Churn có giá: dev đang quen tên cũ, review history mất dấu. Mỗi lần đổi phải trả lời được "đổi để được gì".

Bộ luật đặt tên ở `references/naming-convention.md`. Script sẵn dùng ở `references/rename-recipes.md`.

**Nếu file đang làm đã có quy ước riêng thì quy ước đó thắng** — skill này chỉ cấp quy trình, không áp bộ luật lên một file đã có luật. Kiểm ba chỗ trước khi dùng bộ luật mặc định: page `Naming Registry` trong chính file Figma, file CONVENTION.md trong repo, và skill project-scoped trong `.claude/skills/`. Không có cả ba thì dùng mặc định ở `references/naming-convention.md`.

Trường hợp khó nhất là file **đã có quy ước ngầm nhưng không ai viết ra** — nhận ra bằng cách đọc 20–30 tên hiện có ở bước 0: nếu chúng nhất quán theo một khuôn nào đó, đó là quy ước, và phải hỏi người dùng có giữ không **trước khi** đề xuất đổi sang mặc định.

---

## Quy trình

### Bước 0 — Đọc cấu trúc, đừng đọc nội dung vội

Một call `use_figma` read-only: danh sách page, số children mỗi page. Rồi một call nữa cho page thiết kế: section nào, mỗi section bao nhiêu frame, có gì nằm trần ngoài section.

**Đừng dùng `get_metadata` cho cả page.** File thật vượt token limit và bị ghi ra file tạm. Recipe §A đọc qua Plugin API, gọn hơn nhiều.

Kết thúc bước này phải trả lời được: bao nhiêu page, bao nhiêu section, bao nhiêu screen frame, bao nhiêu node tổng.

### Bước 1 — Đếm trước khi hứa

Chạy recipe §B: đếm node theo type, đếm tên mặc định, liệt kê 25 tên bị trùng nhiều nhất.

Con số này quyết định phạm vi, và nó **luôn lớn hơn bạn nghĩ**. Một file 10 section có thể có 21.000 node. Đừng đưa ra con số ước lượng cho người dùng trước khi chạy bước này — nếu lỡ đưa rồi thì đính chính thẳng khi có số thật.

Ba chỉ số đáng chú ý nhất:
- Số node mang tên mặc định (`Frame 427`, `Rectangle 5`, `Group 12`).
- Tên text layer bị trùng hàng loạt — dấu hiệu Figma đã "đóng băng" tên từ nội dung cũ.
- Số node `Vector` — **không cần đổi**, đó là path bên trong icon, Figma tự đặt.

### Bước 2 — Đọc nội dung, không chụp ảnh

Đây là bước quan trọng nhất và là chỗ dễ làm sai nhất.

Để đặt **đúng** tên 200 màn, cần biết mỗi màn thực sự là gì. Hai cách:

| Cách | Chi phí | Độ chính xác |
|---|---|---|
| Chụp ảnh từng màn | 200 screenshot | Cao nhưng tốn khủng khiếp |
| Chụp ảnh cả section | 8 ảnh | **Vô dụng** — mỗi màn còn ~46px, không đọc được |
| **Đọc `characters` bên trong** | 1–3 call | **Cao nhất** — đọc được cả chữ bị che, và chính xác hơn mắt |

Dùng recipe §C: với mỗi screen frame, trả về id, tên hiện tại, kích thước, và 6–8 chuỗi text đầu tiên **xếp theo thứ tự thị giác** (sort theo `absoluteBoundingBox.y` rồi `x`).

Lọc bỏ: chuỗi < 2 ký tự, chuỗi trùng, và đồng hồ status bar (`/^\d{1,2}:\d{2}$/`). Cắt mỗi chuỗi còn 22–26 ký tự.

Chỉ chụp ảnh khi đọc text không đủ — node không có text (ảnh, illustration, scrim). Lúc đó chụp đúng node đó, `maxDimension` 700.

### Bước 3 — Đối chiếu tên với nội dung, ghi lại mọi mâu thuẫn

Lúc này bạn có bảng `tên hiện tại → nội dung thật`. Quét tìm ba loại mâu thuẫn:

**a. Nhãn bị gán ngược.** Frame tên `Favourite` nhưng bên trong ghi "Downloads". Đây là phát hiện giá trị nhất của cả công việc — nó nghĩa là dev đã implement sai màn. Báo riêng, có bảng, đừng chôn trong danh sách rename.

**b. Tên thừa hưởng do duplicate.** Người dùng nhân bản frame cũ để dựng màn mới, tên cũ đi theo. Frame mới **nhìn thì đúng format** nên qua mặt được mọi check tự động. Chỉ đọc nội dung mới bắt được.

**c. Tên mô tả sai nội dung.** `Focus zone/Belly` nhưng trong màn ghi "Abs". `Lesson infor`, `Resttime`, `Plause`, `Favouting` — lỗi chính tả đóng băng trong tên.

### Bước 4 — Chốt phạm vi với người dùng trước khi ghi

**Bắt buộc.** Đây là ghi hàng loạt khó hoàn tác, và không phải tầng nào cũng đặt tên đúng được bằng máy.

Hỏi bằng quick response, ba lựa chọn, kèm con số thật từ bước 1:

| Phạm vi | Gồm gì | Khi nào chọn |
|---|---|---|
| **Screen + layer chắc chắn** *(mặc định nên đề xuất)* | Page, Section, toàn bộ screen frame (đọc nội dung để đặt đúng), cộng các layer đặt được **chắc chắn**: text → nội dung thật, instance → tên component gốc, icon → `ic_*`, Status Bar / Home Indicator theo hình học | Gần như luôn luôn |
| Toàn bộ, kể cả frame wrapper | Thêm ~2.000 frame kiểu `Frame 65` suy từ children | Khi muốn sạch tuyệt đối và chấp nhận rà tay |
| Chỉ Page + Section + Screen | Không đụng layer | Khi muốn xem kết quả trước rồi quyết tiếp |

Hỏi thêm hai câu nếu liên quan: có đổi text style không (thường **không** — xem §Đừng đụng), và có bật Screen ID `[FLOW-SUB-NN]` không (chỉ bật khi QA có test case trỏ đích danh màn).

Nói rõ những gì bạn **sẽ không đụng** và tại sao. Điều này quan trọng ngang việc nói sẽ làm gì.

### Bước 5 — Ghi, theo đúng thứ tự này

```
1  Page + thứ tự page          ~5 rename
2  Section                     ~10 rename
3  Component set               ~15 rename
4  Screen frame                chia 40–70 rename mỗi call
5  Layer (text → instance → cấu trúc)   3 pass quét toàn page
```

Vì sao thứ tự này: page/section cho người dùng thấy tiến độ ngay ở layer panel; component trước screen vì tên component được dùng làm tên vai trò cho instance ở bước 5; layer cuối vì nó phụ thuộc tên component.

**Chia batch 40–70 rename mỗi call.** Nhỏ hơn thì tốn round trip, lớn hơn thì mất nhiều khi rớt kết nối.

Mỗi map viết dạng `{ nodeId: 'tên mới' }`, lặp qua `getNodeByIdAsync`, `return { renamed, failed, mutatedNodeIds }`. Luôn trả về `failed` — id không tồn tại là tín hiệu file đã đổi dưới chân bạn.

### Bước 6 — Rớt kết nối ≠ chưa ghi

`MCP server "figma" transport dropped mid-call` nghĩa là **mất response**, không nghĩa là chưa ghi.

**Đọc lại trạng thái thật trước khi chạy lại.** Chạy lại mù có thể tạo `(Variant 2)` chồng lên frame đã đúng tên. Trong một lần chạy thật, call bị rớt đã ghi thành công đủ 41/41.

### Bước 7 — Ba pass layer, đều phải idempotent

Viết script sao cho chạy lại lần hai không gây hại — người dùng sẽ thêm màn mới và bạn sẽ phải chạy lại.

**Pass 1 — text layer lấy nội dung của chính nó làm tên.** Đây không phải phát minh: đó **đúng là hành vi mặc định của Figma**. Tên bị kẹt ở nội dung cũ vì ai đó sửa chữ sau khi tạo layer. Cắt 40 ký tự, bỏ qua layer chỉ có glyph (`!/[a-zA-Z0-9]/`).

**Pass 2 — instance lấy tên từ component gốc.** Dùng `await inst.getMainComponentAsync()` rồi đọc `main.parent.name` (tên component set) và `main.name.split('=')[1]` (variant). **Deterministic, không đoán theo hình học.** Map component set → tên vai trò, ví dụ `Nav / Tab Bar` → `Tab Bar`, `Core / Icon / Fill` → `ic_<variant>_fill`.

**Pass 3 — layer cấu trúc.** `HomeIndicator` → `Home Indicator`. Tên kiểu iconify `mingcute:right-line` → `ic_right_line`. Status Bar theo hình học: con trực tiếp của frame rộng ≥ 340, `y ≈ 0`, cao 38–54.

Cả ba pass đều **bỏ qua node nằm trong instance** — dùng helper `inInstance()` ở recipe §E. Rename node con của instance vừa không cần (nó thừa kế từ component gốc) vừa dễ tạo override rác.

### Bước 8 — Verify bằng luật, không bằng cảm giác

Recipe §F kiểm ba thứ, mỗi section một dòng:

1. Mọi screen frame có ` — ` và **đúng 3 cấp** `/` (trừ frame prefix `[`).
2. Không có tên trùng (bỏ qua `[Ref]` / `[Note]` — trùng ở đó là hợp lệ, section đã phân biệt).
3. Không có tên rỗng hoặc chỉ có dấu cách.

Chạy đến khi `problems: []`. Trong một lần chạy thật, pass này bắt được một frame bị đổi thành **một dấu cách trắng** và một frame có **5 cấp**.

### Bước 9 — Báo cáo

Ba phần, theo thứ tự này:

1. **Đã đổi gì** — bảng theo tầng, có số lượng.
2. **Lỗi nội dung phát hiện được** — nhãn gán ngược, lỗi chính tả. Đây là phần người dùng thấy giá trị nhất. Đừng làm mượt đi.
3. **Cần người quyết** — frame trùng hệt nhau cần dedup, chỗ bạn phải đoán, việc còn lại.

Đính chính thẳng mọi số liệu bạn lỡ đưa sai ở đầu.

---

## Đừng đụng

Phần này quan trọng ngang phần quy trình.

| Đối tượng | Lý do |
|---|---|
| **Variable đã đúng tier** | Nếu file đã có `Primitives` + `Semantic` với tên lowercase/slash thì nó đã đạt chuẩn. Kiểm tra rồi nói rõ "không đụng một dòng nào" — điều này xây niềm tin cho phần còn lại |
| **Text style** đang nhất quán | `Body/Medium/Regular` Title Case là chuẩn phổ biến (Material, Apple đều vậy), nằm ở picker khác với variable. Đổi 51 style là churn, lợi ích mỏng. **Hỏi, mặc định giữ** |
| **Node `Vector`** | Path bên trong icon. Figma tự đặt. Đặt tên từng cái là vô nghĩa |
| **Node con của instance** | Thừa kế từ component gốc. Sửa gốc thì instance theo |
| **Nội dung page Draft / Archive** | Vùng không bàn giao. Đổi tên page là đủ |
| **Variant property** trong cùng lượt | `Property 1` sai thật, nhưng đổi nó chạm mọi instance trong file. **Tách thành lượt riêng có verify.** Đừng gộp hai thao tác hàng loạt rủi ro vào một lần |

---

## Áp cho file thứ hai (bản copy, bản branch, file song sinh)

Figma **giữ nguyên node ID khi duplicate file**. Nên map rename dùng lại được nguyên vẹn.

Nhưng **phải verify trước, không giả định**: đọc toàn bộ section + screen ở file đích, đối chiếu từng id và tên hiện tại với file nguồn. Chỉ chạy khi khớp 100% và chưa cái nào bị đổi tên.

Nếu file đích có thêm node mà file nguồn không có — chuyện bình thường — xử lý luôn, và nói rõ hai file giờ lệch nhau ở đâu.

---

## Chạy lại khi file lớn thêm

Người dùng sẽ thêm section mới rồi nhờ "đặt tên như các section khác". Lúc đó:

1. **Quét cả page, không chỉ section mới.** Section cũ cũng trôi — trong một lần chạy thật, `03 Workout` +2 màn, `05 More` +4, `04 Progress` −1, và có node rời mới nằm ngoài mọi section.
2. **Giả định mọi frame mới đều mang tên thừa hưởng.** Đọc nội dung đối chiếu, đừng tin format.
3. **Chạy lại cả ba pass layer** — chúng idempotent, và nội dung mới cần chúng.
4. **Kiểm tên trùng trên toàn page**, không chỉ trong section mới. Frame nhân bản mang theo cả hậu tố `(Variant 9)`.
5. Xử lý luôn component set mới nằm trần — chúng thuộc về đợt làm mới đó.

---

## Tài liệu tham chiếu

| File | Khi nào đọc |
|---|---|
| `references/naming-convention.md` | Trước khi dựng map tên. Bộ luật đầy đủ cho cả 7 tầng |
| `references/rename-recipes.md` | Trước khi gọi `use_figma` lần đầu. Script sẵn dùng + bẫy |

Trước lần gọi `use_figma` đầu tiên **phải nạp skill `figma-use`**, hoặc đọc resource `skill://figma/figma-use/SKILL.md` nếu máy không có plugin đó.
