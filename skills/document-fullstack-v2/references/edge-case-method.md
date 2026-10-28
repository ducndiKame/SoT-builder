# Edge-Case Discovery Method (ac-gherkin v2)

Phương pháp phát hiện edge case một cách **hệ thống** trước khi viết AC table.
Gộp 2 engine, self-contained (không cần cài skill ngoài):

- **Path-tracer** (đọc CODE) — dò cơ học mọi nhánh/boundary chưa được guard
- **Taxonomy checklist** (đọc SPEC/Figma) — 5 nhóm để không sót khi không có code

> Mục tiêu: mọi edge case đưa vào AC table đều **có nguồn** (code thật hoặc rule đã confirm).
> Cái nào chưa rõ recovery/behavior → `🔴 TBD`, KHÔNG suy diễn.

---

## Chọn mode

| Có gì trong tay | Mode | Làm gì |
|---|---|---|
| Có source code của feature (repo IIP505/IIP506…) | **Code-mode** (chính) | Chạy Path-tracer trên file/function/diff liên quan |
| Chỉ có Figma + spec cũ, không có code | **Spec-mode** | Chạy Taxonomy checklist trên flow + input trong Figma |
| Có cả hai | **Cả hai** | Path-tracer ra danh sách "code chưa handle" → đối chiếu Taxonomy để bổ sung cái spec-level mà code chưa chạm |

⚠️ Nếu không có code, ĐỪNG bịa hành vi code. Spec-mode chỉ liệt kê edge case *cần hỏi/cần thiết kế*, đánh `🔴 TBD` cho recovery chưa chốt.

---

## A. Code-mode — Path-tracer (đọc code detect edge case)

Nguyên tắc: **là path tracer thuần**, không phán code tốt/xấu — chỉ liệt kê nhánh THIẾU xử lý.

**Scope:**
- Đưa **diff** → chỉ soi boundary chạm tới từ dòng đã đổi, thiếu guard trong diff.
- Đưa **full file / function** → toàn bộ nội dung là scope.
- Bỏ qua phần còn lại của codebase trừ khi content gọi hàm ngoài tường minh.

**Các bước (đúng thứ tự):**
1. **Nạp content** — Read file/function/diff của feature. Rỗng/không decode được → dừng, ghi nhận "không có code để soi", chuyển Spec-mode.
2. **Duyệt mọi nhánh** — control flow (if/else, loop, error handler, early return) + domain boundary (chỗ giá trị/state chuyển tiếp). Rút edge class TỪ chính content, không dựa checklist cứng. Ví dụ lớp cần soi:
   - `else`/`default` bị thiếu
   - input chưa guard (null / empty / sai format)
   - off-by-one trong loop, index tràn
   - tràn số học, ép kiểu ngầm
   - race condition, double-tap, data đổi giữa load↔save
   - gap timeout / retry
   - **implicit branch**: code chỉ xử lý vài giá trị của 1 tập hữu hạn (enum, status code, flag) → các giá trị còn lại là nhánh ngầm chưa handle (vd xử lý `RED`,`YELLOW` mà quên `GREEN`)
3. **Với mỗi path**: content có handle không? Chỉ giữ nhánh **CHƯA** handle làm finding; nhánh đã có guard → bỏ im lặng.
4. **Rà lại completeness** — lượt lại từng edge class ở bước 2, bổ sung nhánh sót.
5. **Deletion check** — nếu diff xóa/thay code có nghĩa: kiểm guard/handling nào bị mất theo đó.

**Output trung gian mỗi finding (bảng nháp, chưa phải AC):**

| location | trigger_condition | guard/fix gợi ý | hậu quả nếu bỏ |
|---|---|---|---|
| `file:line` | mô tả 1 dòng (≤15 từ) | cách đóng gap | điều gì hỏng thực tế (≤15 từ) |

Không gán severity ở bước này (severity/priority để bước map sang AC).

---

## B. Spec-mode — Taxonomy checklist (5 nhóm)

Khi không có code, duyệt đủ 5 nhóm trên từng input/flow/màn của Figma:

1. **Input Validation** — field rỗng? quá dài? sai format? ký tự đặc biệt? min/max?
2. **Boundary** — giá trị ở min, max, dưới min, trên max; ranh giới pagination; ngưỡng timeout; rate limit.
3. **Error States** — mất mạng giữa chừng; resource not found (404); permission denied; session hết hạn; server 5xx.
4. **Concurrency** — double-tap submit; 2 user sửa cùng resource; data đổi sau khi load (stale).
5. **Integration** — service ngoài (Azure/AI engine/API) down / trả lỗi / timeout.

Mỗi ô: ghi **Expected Behavior** + **Recovery**. Chưa chốt → `🔴 TBD`.

---

## C. Map edge case → AC Gherkin table

Đây là bước biến finding thành spec Apero. Giữ đúng luật format v1:

- Edge case **là 1 luồng hành vi riêng** (user thấy khác) → tạo **Scenario row mới** trong cùng AC table (KHÔNG tách Exception section).
  - `Given` = tiền điều kiện gây edge (vd "Đang ở màn X, mất mạng")
  - `When` = hành động / sự kiện trigger
  - `Then` = hành vi mong đợi + recovery path (message user thấy, có retry không, data giữ hay mất)
- Edge case **chỉ là ràng buộc phụ** của scenario đã có → nhét vào cột **Note** của scenario đó (business rule / dependency dev cần biết).
- **Error message copy** → đưa vào `Then` (câu chữ user thấy) hoặc Note, KHÔNG tạo bảng error riêng.
- **Validation rules** (min/max/format) từ nhóm Input/Boundary → dồn vào section **Validation Rules** của page (v1 đã có).
- **Integration/timeout/remote** → nếu điều khiển bằng remote key → ghi ở **NFR section** (key + JSON config).

**Luật nguồn (giữ nguyên v1):**
- Recovery/behavior chưa có nguồn (code chưa handle + user chưa confirm) → `🔴 TBD`, đưa vào batch hỏi `AskUserQuestion` trước khi publish.
- KHÔNG cite `US-XX`/`BR-XX`/`[[memory]]` trong Note (đó là internal audit).
- Tiếng Việt diễn giải, giữ EN cho term tech.

---

## D. Priority (để QA & dev biết cái nào phải chắc)

Xếp mỗi edge case theo **Likelihood × Impact**, ghi trong cột Note nếu cần nhấn:
- **P1** = hay xảy ra + hậu quả nặng (mất data, kẹt flow, crash) → BẮT BUỘC handle, phải có trong AC.
- **P2** = trung bình → nên handle, có AC.
- **P3** = hiếm + nhẹ → graceful fail là đủ, có thể chỉ ghi Note.

Nếu bundle này dùng để lập QA test plan riêng: xuất "Must test (P1) / Should test (P2) / Nice to test (P3)" từ danh sách trên.
