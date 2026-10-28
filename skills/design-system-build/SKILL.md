---
name: design-system-build
description: Audit một file Figma rồi dựng ra tài liệu Design System đầy đủ, chính xác, dùng được làm input cho AI generate màn hình mới. Dùng skill này bất cứ khi nào người dùng muốn tạo / cập nhật / audit / chuẩn hoá design system, design token, style guide, hay tài liệu thiết kế từ Figma — kể cả khi họ chỉ nói "tổng hợp token giúp tôi", "làm tài liệu cho dev", "viết style guide", "file design của tôi xong rồi, làm tài liệu đi", "kiểm tra lại hệ màu", hay dán một link Figma kèm câu hỏi về màu / typography / component. Cũng dùng khi cần re-audit sau khi file Figma đã thay đổi nhiều, khi cần xuất design system ra HTML hoặc artifact để chia sẻ, hoặc khi cần một block prompt để AI tool dựng màn mới đúng ngôn ngữ thiết kế. KHÔNG dùng cho việc thiết kế một màn hình cụ thể (đó là figma-flow-design) hay đặt tên layer (figma-naming-standard).
---

# Design System Build

Dựng tài liệu Design System từ một file Figma có thật. Đầu ra không phải bản mô tả cho đẹp — nó là thứ để **AI tool đọc rồi generate màn mới đúng ngôn ngữ thiết kế**, và để **dev đọc rồi code không phải hỏi lại**.

Ba nguyên tắc chi phối mọi thứ bên dưới:

1. **Chỉ viết cái đọc được từ file.** Mọi con số phải trích từ Figma, không phỏng đoán từ ảnh chụp.
2. **Phân biệt "chưa dùng" với "chưa có".** Đây là lỗi dễ mắc nhất và nó phá hỏng độ tin cậy của cả tài liệu. Xem §1.
3. **Ràng buộc quan trọng hơn danh sách giá trị.** Thứ làm cho thiết kế đồng bộ là luật cấm, không phải bảng hex.

---

## Quy trình

### Bước 0 — Chốt phạm vi

Hỏi ngắn nếu chưa rõ: link file Figma, đầu ra muốn gì (tài liệu Markdown / artifact / trang HTML), và tệp người dùng cuối của sản phẩm. Tệp người dùng quyết định rất nhiều luật — một app cho nữ 35+ và một app cho gamer 20 tuổi sẽ có luật motion và luật màu ngược nhau. Đừng suy ra tệp này từ file Figma; hỏi.

Nếu project đã có skill bối cảnh (kiểu `design-context`), đọc nó trước — nó thường chứa tệp người dùng, chuẩn copy, và chuẩn accessibility cần áp.

**Chọn chế độ** (hỏi nếu chưa rõ):

- **Tối thiểu (SoT phase 1).** Dùng khi dự án mới dựng SoT bằng `sot-init`, hoặc khi người dùng chỉ cần đủ cho một feature mẫu. Phạm vi: token và component **mà feature mẫu thật sự dùng**, cộng 12–16 luật cứng của khối A. Bỏ qua bước 6 (chụp 10–15 màn) và bước 8 (dựng page Tokens), chỉ đo contrast cho các cặp màu feature dùng. Ghi vào `design-system/README.md` của SoT: luật cứng → token feature dùng (kèm cột "dùng ở đâu") → component feature dùng → ngoại lệ đã biết. Cuối file ghi rõ "Phạm vi: chỉ feature <tên>; phần còn lại chưa audit" để AI không tưởng là đã đủ.
- **Đầy đủ.** Toàn bộ quy trình bên dưới. Dùng khi dự án đã có nhiều tính năng, hoặc trước khi bàn giao cho dev. Trong SoT, lưu tài liệu ở `design-system/DesignSystem.md` (+ `.html`), và cập nhật `design-system/README.md` thành bản tóm tắt trỏ tới nó.

### Bước 1 — Đọc cấp document

Một call `use_figma` read-only lấy: danh sách page, toàn bộ text style kèm thông số, paint/effect/grid style, và các variable collection. Script sẵn có ở `references/figma-recipes.md` §A.

Đây là bước rẻ nhất và cho bức tranh tổng thể ngay.

### Bước 2 — Đọc toàn bộ variable

**Không dùng `get_variable_defs` để kiểm kê token.** Nó chỉ trả về variable **đang được gán** trên node được chọn. Token đã tạo nhưng chưa layer nào dùng sẽ không xuất hiện, và bạn sẽ kết luận sai là "file chưa có token đó".

Dùng Variables API qua `use_figma` (§B trong recipes). Nó trả đủ collection, mode, tên biến, giá trị đã resolve, và alias.

`search_design_system` cũng không thay thế được — nó chỉ index library đã publish, trả rỗng cho local variable.

### Bước 3 — Kiểm kê màn hình và component

Fan-out song song: một `use_figma` call cho mỗi page (§C). Mỗi call `setCurrentPageAsync` đúng một lần.

Lưu ý hai bẫy:
- **Page load lazily.** `page.children` rỗng cho tới khi `setCurrentPageAsync`. Đừng kết luận page rỗng từ lần đọc đầu.
- **`componentPropertyDefinitions` ném lỗi** nếu component set đang ở trạng thái error. Bọc try/catch, và ghi nhận set nào lỗi — đó là phát hiện đáng giá, dev sẽ không swap được component đó.

### Bước 4 — Đếm cách dùng, không chỉ liệt kê

Đây là bước hay bị bỏ và là bước cho ra phát hiện giá trị nhất. Quét toàn bộ node có fill, đếm xem mỗi token được bind bao nhiêu lần, và đếm số fill còn hardcode hex (§D).

Ví dụ thật: một file có đủ nhóm `action/primary/*` trong collection Semantic nhưng quét ra **0 lần sử dụng** — mọi button bind thẳng vào primitive. Nếu chỉ liệt kê token thì hệ nhìn hoàn hảo. Đếm mới thấy lớp semantic là đồ trang trí, và lỗi contrast phải sửa ở 634 layer thay vì một dòng.

### Bước 5 — Đọc spec component

`get_design_context` trên từng component set. Nó trả cả code lẫn ảnh, nên rẻ hơn gọi riêng screenshot.

Ưu tiên: component mới hoặc vừa đổi → component xuất hiện nhiều nhất → component định hình pattern (header, tab bar, button, input, card, dialog).

Với component set quá lớn, đọc node con cụ thể thay vì cả set.

### Bước 6 — Xem màn hình thật

Chụp 10–15 màn đại diện, tải về, đọc bằng mắt. Chọn theo tiêu chí phủ: mỗi flow một màn, cộng các màn định hình pattern (empty state, dialog, sheet, permission, result, player, onboarding step).

Đây là bước duy nhất phát hiện được: phong cách hình ảnh, lỗi chính tả, lỗi định dạng số và ngày, và các pattern chưa được component hoá.

### Bước 7 — Đo contrast bằng công thức

Đừng ước lượng bằng mắt, và đừng tin cảm giác "trông cũng ổn". Dùng công thức WCAG. Cách gọn nhất là tính ngay trong script `use_figma` nơi đã có hex đã resolve — không cần runtime nào ở máy (§E).

Đo ít nhất: mọi cặp `text/*` trên nền trắng và trên nền màn hình, chữ trên fill của button chính, focus ring, và từng cặp `feedback/*/bg` + `/fg`.

Kết quả phải ghi thành ba bảng riêng — **đạt**, **chưa đạt**, **cách sửa** — chứ không trộn làm một. Người đọc cần biết cái nào an toàn để dùng ngay.

### Bước 8 — Dựng page Tokens trong Figma (khuyến nghị mạnh)

Nếu file có token chưa được apply ở đâu, đề xuất dựng một page bind **mọi** token lên một swatch thật. Sau đó `get_variable_defs` trên frame đó trả đủ toàn bộ token kèm hex trong một call — vĩnh viễn, cho mọi AI tool sau này, không chỉ cho lần audit này.

Cách dựng ở `references/figma-recipes.md` §F. Lưu ý: `text/*` và `icon/*` phải bind vào fill của **chữ/shape**, không phải nền, nếu không swatch không thể hiện đúng token.

### Bước 9 — Viết tài liệu

Theo cấu trúc ở `references/document-outline.md`. Đọc file đó trước khi viết.

### Bước 10 — Xuất bản (tuỳ chọn)

Ba dạng đầu ra, mỗi dạng một việc khác nhau. Xem `references/deliverables.md`.

---

## Cấu trúc thông tin — năm khối

Không xếp theo kiểu style guide truyền thống. Xếp theo **thứ tự câu hỏi mà AI phải trả lời khi dựng một màn mới**.

| Khối | Nội dung | Trả lời câu hỏi |
|---|---|---|
| **A. Vào việc** | 12–16 luật cứng | "Nếu chỉ đọc được một trang thì đọc gì?" |
| **B. Nền tảng thị giác** | Màu, typography, spacing/grid/radius/elevation | "Nhìn có giống project không?" |
| **C. Vật liệu dựng sẵn** | Component, ngoại lệ lưới, icon, hình ảnh | "Có gì dùng lại được, đừng phát minh?" |
| **D. Ngữ cảnh sản phẩm** | Motion, kiến trúc màn hình, nội dung/localization, đặt tên | "Cái gì làm màn này *thuộc về* app này?" |
| **E. Vận hành** | Block prompt cho AI, checklist nghiệm thu, backlog, phụ lục độ tin cậy | "Dùng tài liệu này ra sao, tin được đến đâu?" |

Khối A tồn tại vì ngân sách context: prompt hay bị cắt, và 12–16 dòng đầu phải đủ giữ phần lớn nhận diện.

Khối E là thứ biến tài liệu từ "để đọc" thành "để chạy". Đừng bỏ.

---

## Ba pattern lặp lại trong mọi phần

**1. Bảng token luôn có cột "dùng ở đâu".**
`primary/300 #AB99FF` là thông tin vô dụng với AI. `primary/300 — fill không mang chữ: progress bar, arc, trang trí` mới dùng được. Không có cột này thì bảng chỉ là danh bạ hex.

**2. Luật tách khỏi bảng.**
Mỗi phần có một mục "Cách dùng — luật" riêng, và tài liệu kết thúc bằng một danh sách **CẤM**. Một model có đủ hex vẫn dựng sai nếu không ai cấm nó đặt shadow lên card hay dùng font serif cho button.

**3. Độ tin cậy gắn ngay tại chỗ.**
✅ đọc được từ file · ⚠️ đề xuất, chưa chốt · ⛔ chưa đọc được. Rồi tổng hợp lại ở phụ lục cuối, kèm **phương pháp đã dùng**. Chỗ nào để trống mà không đánh dấu thì AI sẽ điền bừa một cách rất tự tin.

---

## Những thứ dễ bỏ sót nhưng đáng giá nhất

**Ngoại lệ lưới có chủ đích.** Liệt kê thành mục riêng những giá trị không chia hết cho grid (6, 10, 0.33, 26…), và nói rõ cái nào **cố ý giữ**, cái nào **nên chuẩn hoá**. Không có mục này, AI sẽ "sửa" padding tab bar từ 6 thành 8 và làm hỏng component.

**Từ vựng state.** Trích ra bộ từ state mà project đã dùng nhất quán (`First Run`, `Empty`, `Loading`, `Offline`, `Goal Reached`…). Màn mới phải sinh state theo đúng bộ này, không phải bộ generic. Cái này hữu ích hơn sitemap nhiều.

**Lỗi thật trong file.** Lỗi chính tả, sai định dạng ngày/số, nhãn màn bị gán ngược, token đặt tên ngược nghĩa. Báo thẳng, kèm bảng "hiện tại → phải là". Đừng làm mượt đi. Đây thường là phần người dùng thấy giá trị nhất.

**Quyết định trên giấy chưa vào file.** Nếu người dùng từng chốt đổi một token nhưng Figma chưa đổi, **ghi theo file thật** và nêu rõ độ lệch. Tài liệu mô tả cái đang có, không mô tả cái định có.

**Phân biệt "chưa dùng" với "chưa có".** Nhắc lại vì nó quan trọng. Viết "token này chưa được apply ở màn nào" (đọc được), không viết "file chưa có token này" (không đọc được từ MCP).

---

## Cách viết

Viết cho người đọc, không cho máy chấm điểm.

- Câu ngắn, chủ động. Nói cái gì sai và sửa thế nào, không chỉ nói là sai.
- Nêu **tại sao** một luật tồn tại, không chỉ nêu luật. "Không shadow trên card — chiều sâu đến từ card trắng trên nền xám" dạy được nhiều hơn "cấm shadow".
- Con số cụ thể thay cho tính từ. "contrast 2.41:1, dưới ngưỡng AA 4.5:1" thay cho "màu hơi nhạt".
- Ngôn ngữ tài liệu theo ngôn ngữ người dùng; tên token, UI copy và block prompt giữ tiếng Anh.

---

## Bốn đường đọc

Ghi phần này vào cuối tài liệu — nó giúp người mới biết bắt đầu từ đâu:

- **AI generate màn hình:** khối A → dán block prompt → dùng mẫu prompt → nghiệm thu bằng checklist
- **Designer mới:** khối A → B → C → kiến trúc màn hình
- **Dev:** luật bind token → spacing/radius → component → quy tắc kỹ thuật localization → đặt tên
- **Người audit lần sau:** backlog → phụ lục độ tin cậy

---

## Tài liệu tham chiếu

Đọc khi cần, không nạp hết từ đầu:

| File | Khi nào đọc |
|---|---|
| `references/figma-recipes.md` | Trước khi gọi `use_figma` lần đầu. Script sẵn dùng + toàn bộ bẫy đã biết |
| `references/document-outline.md` | Trước khi viết tài liệu. Dàn ý từng mục và nội dung cần có |
| `references/deliverables.md` | Khi người dùng muốn artifact, trang HTML, hoặc bản song ngữ |
