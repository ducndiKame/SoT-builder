# Dàn ý tài liệu Design System

Mười lăm mục, xếp theo năm khối ở SKILL.md. Bỏ mục nào không có dữ liệu thật, nhưng **đừng đổi thứ tự** — thứ tự chính là thứ tự câu hỏi mà người đọc (hoặc AI) đặt ra.

Mở đầu bằng một khối metadata ngắn: nguồn (file key + node id), ngày audit, phạm vi (số section / màn / token / style / component), và một câu về sản phẩm và tệp người dùng.

---

## Khối A — Vào việc

### 0. TL;DR — 12–16 luật cứng

Mỗi dòng một luật, đủ ngắn để quét. Đây là thứ duy nhất được đọc nếu prompt bị cắt.

Phủ cho đủ: nền và card · radius chữ ký · radius cho thứ bấm được · khung và content width · phân vai hai typeface · đơn vị lưới · màu hành động · luật bind token · pattern nào dùng native OS · bộ icon · phong cách hình ảnh · gradient trên ảnh · cách trình bày số liệu · empty state · chuẩn copy và locale · luật motion.

Viết ở dạng mệnh lệnh có lý do, không phải danh sách thuộc tính:

> **Nền màn hình là xám `#F3F4F6`, không phải trắng.** Card mới là màu trắng. Phân tách bằng tương phản nền/card, **không dùng shadow**.

---

## Khối B — Nền tảng thị giác

### 1. Kiến trúc file Figma

Bảng page: id, tên, nội dung. Chỉ rõ page nào là **nguồn sự thật của token** và cách đọc lại nó.

### 2. Màu

Theo đúng thứ tự này:

1. **Kiến trúc token** — mấy collection, mỗi cái bao nhiêu biến, mấy mode, cái nào được phép apply lên layer.
2. **Primitives** — bảng ramp dạng ma trận (bậc × họ màu). Gọn hơn liệt kê dọc nhiều.
3. **Vai trò thực tế của ramp thương hiệu** — bậc nào dùng ở đâu. Đây là chỗ bắt được những phân biệt tinh vi kiểu "bậc này cho bề mặt, bậc kia cho chữ".
4. **Semantic** — tách bảng theo nhóm (`bg`, `surface`, `text`, `icon`, `border`, `action`, `feedback`). Cột: token · giá trị mode chính · mode phụ (ghi alias, không ghi hex — alias cho thấy ý đồ) · dùng cho.
5. **Màu ngoài hệ token** — màu biểu đồ, badge, gauge thường nằm ngoài. Liệt kê và đánh dấu là nợ.
6. **Luật dùng màu** — nền, màu thương hiệu, phân cấp chữ, trạng thái, binding.
7. **Accessibility** — ba bảng tách bạch: đạt ✅ / chưa đạt ❌ / cách sửa. Bảng "cách sửa" ghi rõ chi phí ("đổi 1 giá trị token, 0 layer" so với "rebind 634 layer").

### 3. Typography

Font family và vai trò, kèm **quy tắc phân vai chặt** (font nào tuyệt đối không xuất hiện ở đâu).

Bảng đầy đủ text style theo nhóm: size/line-height, weight có sẵn, tracking, dùng cho. Nếu bộ style lớn (40+), ghi chú theo **nhóm** thay vì từng style — dễ đọc hơn.

Ghi rõ đơn vị tracking. Figma ghi phần trăm; CSS cần `em`. `-1%` ở 30px = `-0.3px` = `-0.01em`.

Rồi đến **mẫu lặp lại** — tiêu đề màn hình, cụm số liệu, card thống kê. Đây là thứ AI copy được ngay:

```
Value   Lora, theo cấp
Unit    sans, nhỏ hơn 1–2 bậc, text/tertiary, cách 4, canh baseline
Context body-xsmall · text/tertiary
```

### 4. Khung, giãn cách, bo góc, độ nổi

Bảng khung: frame, margin, content width, chiều cao header/tab bar, vùng scroll an toàn.

Thang spacing kèm cột "dùng cho". Thang radius kèm cột "dùng cho".

**Mục riêng cho ngoại lệ lưới** — giá trị nào lệch grid, cái nào cố ý giữ, cái nào nên chuẩn hoá. Không có mục này thì AI sẽ "sửa" nhầm.

Độ nổi: liệt kê **mọi** shadow tìm được. Nếu hệ gần như không dùng shadow thì nói thẳng — đó là một quyết định thiết kế, không phải thiếu sót.

---

## Khối C — Vật liệu dựng sẵn

### 5. Component

Bảng tổng trước: tên · id · số variant · property. Rồi spec từng cái đáng kể.

Spec viết dạng khối cấu trúc, không văn xuôi:

```
Container  343 · p-6 · radius 48 · bg rgba(255,255,255,.8) · blur 6
Active     bg primary/300 · px-16 py-12 · gap 6 · shadow 0 2 4 rgba(159,133,255,.4)
Idle       flex-1 · icon 24 · KHÔNG label
```

Với mỗi component ghi thêm: **luật dùng** và **dev phải tự lo gì**. Phần thứ hai hay bị bỏ và là phần dev cần nhất.

Nếu component set có lỗi naming hoặc lỗi trạng thái, ghi ở đây kèm chi phí sửa.

### 6. Icon

Bộ icon, quy ước tên, hai biến thể line/fill và ý nghĩa, các size được dùng, luật màu, cách export. Nếu icon set đang lỗi, đây là mục P0.

### 7. Hình ảnh và illustration

Liệt kê **từng phong cách** kèm địa bàn riêng. Một sản phẩm thường có 3–5 phong cách (ảnh chụp, illustration phẳng, 3D render, ảnh sản phẩm cắt nền, emoji minh hoạ) và trộn chúng là cách nhanh nhất làm màn hình lạc hệ.

Mỗi phong cách: chủ thể, tông màu, bối cảnh, bố cục, crop. Cộng luật chung — gradient bắt buộc trên ảnh có chữ, cấm gì, export ra sao.

### 8. Data visualization

Từng loại biểu đồ kèm spec. Đánh dấu rõ màu nào chưa có token.

---

## Khối D — Ngữ cảnh sản phẩm

### 9. Motion

Nguyên tắc trước (suy ra từ tệp người dùng), rồi kịch bản cụ thể đã đặc tả trong file, rồi bảng token đề xuất nếu chưa có.

Nếu file có note motion viết tay, **trích nguyên văn** — đó là ý đồ của designer, đừng diễn giải lại.

Nhắc Reduce Motion nếu tệp người dùng cần.

### 10. Kiến trúc màn hình

Bảng section × số màn × flow chính.

Rồi **từ vựng state** — bộ từ mà project đã dùng nhất quán. Mục này hữu ích hơn cả sitemap.

Rồi **khoảng trống**: flow nào còn thiếu, mức độ nghiêm trọng.

### 11. Pattern màn hình

Các khuôn lặp lại: dialog, sheet, empty state, permission, bước onboarding, màn kết quả, player, dashboard, toast. Mỗi khuôn một khối cấu trúc.

Ghi rõ khuôn nào dùng native OS thay vì component tự dựng, và **tại sao**.

### 12. Nội dung và bản địa hoá

Ba tầng:

- **Bảng format** — đúng / sai cạnh nhau. Chính tả, viết hoa, ngày, giờ, đơn vị, số, tiền, tuần bắt đầu thứ mấy.
- **Quy tắc kỹ thuật** — placeholder thay vì nối chuỗi, số nhiều, đơn vị là dữ liệu không phải chữ, chừa chỗ cho bản dịch.
- **Luật viết copy** — giọng, error, empty state, điều cấm nói.

Rồi bảng **lỗi copy đã phát hiện**: màn · hiện tại · phải là. Tách riêng lỗi bản địa hoá khỏi lỗi chính tả — chúng có nguyên nhân khác nhau.

### 13. Quy ước đặt tên

Mẫu tên màn, tiền tố đặc biệt, quy ước component và token. Kèm trạng thái áp dụng: đã chuẩn hoá tới đâu, còn gì chưa.

---

## Khối E — Vận hành

### 14. Dùng tài liệu này cho AI

Ba phần, và đây là mục biến tài liệu thành công cụ:

**14.1 Block luật cứng** — nén toàn bộ hệ còn 50–80 dòng plain text để dán thẳng vào prompt. Gồm khung, type scale, toàn bộ token, component bắt buộc tái sử dụng, pattern, icon, ảnh, motion, copy, và một danh sách **CẤM**.

Giữ tiếng Anh kể cả khi tài liệu viết tiếng Việt — token và UI copy đều tiếng Anh, dịch ra làm hỏng thứ nó dùng để ràng buộc model.

**14.2 Checklist nghiệm thu** — 12–15 dòng tick để kiểm màn AI sinh ra.

**14.3 Mẫu prompt** — khung điền sẵn: tên màn, flow, mục tiêu người dùng, dữ liệu, điểm vào, điểm ra, các state phải sinh, quy ước đặt tên.

### 15. Việc cần làm

Xếp theo **mức chặn**, không theo chủ đề: đã xong ✅ / P0 chặn bàn giao / P1 cần trước khi thiết kế thêm / P2 hoàn thiện.

Mỗi mục nêu cả **chi phí sửa**. "Đổi một giá trị token" và "đụng 1.319 instance" là hai việc rất khác nhau và người đọc cần biết để xếp lịch.

### Phụ lục — Độ tin cậy

Bảng: mục nào ✅ đọc trực tiếp từ file · ⚠️ đề xuất chưa chốt · ⛔ chưa đọc được, và vì sao.

Kèm một ghi chú về **phương pháp** — công cụ nào đã dùng, giới hạn của nó là gì. Người audit lần sau cần biết để không lặp lại nhầm lẫn của bạn.

---

## Ba lỗi hay mắc khi viết

**Viết đẹp thay vì viết đúng.** Nếu file có lỗi, tài liệu phải có lỗi đó kèm cách sửa. Một tài liệu mượt mà che mất lỗi thì vô dụng.

**Mô tả ý định thay vì mô tả hiện trạng.** Nếu người dùng từng chốt một thay đổi nhưng Figma chưa đổi, ghi theo file và nêu rõ độ lệch.

**Quên cột "dùng ở đâu".** Bảng token không có cột này chỉ là danh bạ hex. Nó không dạy AI được gì.
