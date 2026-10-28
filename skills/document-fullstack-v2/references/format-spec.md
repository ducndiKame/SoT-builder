# AC Gherkin Format — Spec lock 2026-05-19

Format default cho mọi spec từ giờ. Replaces deprecated US v2.

## Cấu trúc page (theo thứ tự)

### 1. TOC macro
```xml
<p><ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">3</ac:parameter></ac:structured-macro></p>
```

### 2. System Requirement
1 dòng duy nhất:
```xml
<h1>System Requirement</h1>
<p><strong>Link Figma</strong>: <a href="{FIGMA_URL}">{Section name}</a></p>
```

### 3. Flow (optional)
Chỉ khi flow > 4 bước hoặc có branching. Mô tả ngắn 2-3 câu hoặc embed diagram.

### 4. Functional Requirement (CORE)
Chia thành nhiều `<h2>Acceptance Criteria N: {tên nhóm}</h2>`. Mỗi AC = 1 table 7 cột:

```xml
<table>
<tbody>
<tr>
  <th>Scenario</th><th>Given</th><th>When</th><th>Then</th><th>Note</th><th>Link UI</th><th>Updated Time</th>
</tr>
<tr>
  <td><strong>1. {Tên scenario}</strong></td>
  <td><ul><li>{precondition}</li></ul></td>
  <td>{trigger action}</td>
  <td><ul><li>{outcome 1}</li><li>{outcome 2}</li></ul></td>
  <td>{business rule phụ / cross-link memory}</td>
  <td>
    <p><ac:image ac:width="220"><ri:attachment ri:filename="{slug}.png"/></ac:image></p>
    <p><a href="{FIGMA_URL}">Link UI</a></p>
  </td>
  <td>DD MMM YYYY</td>
</tr>
</tbody>
</table>
```

Rules:
- Mỗi AC chứa đầy đủ happy path + validation + error/edge case
- KHÔNG tách "Exception flows" thành section riêng
- Scenario: `{số}. {tên ngắn}` (vd `1. Tap "Resume conversation"`)
- Given/When/Then: bullet list khi nhiều ý, single line khi 1 ý
- Note: business rule phụ, cross-link `[[memory-name]]` khi cần
- Link UI: image embed + hyperlink Figma node

### 5. Validation Rules (chỉ khi feature có form input)
Table 4 cột: `Tên | Validation Rules | Mô tả | UI`

### 6. Non-functional Requirement
Bắt buộc khi có remote config:

**6.1. Key remote bật/tắt** — table: `Parameter Name | Data Type | Default Value | Description`

**6.2. Key remote config nội dung** — same table, Default Value chứa JSON schema mẫu đầy đủ.

## Rules nội dung (LOCKED 2026-05-20)

### Rule 1: Trim text mô tả UI
- Đã có image embed trong cột Link UI → **KHÔNG mô tả UI bằng text dài dòng** trong cột Then
- ❌ BAD: liệt kê từng element (header, target card, sub-line, lesson nodes với 4 màu, bottom tab...) — user không đọc, dev xem image trực tiếp
- ✅ GOOD: outcome ngắn business-level (vd "Home render lesson list theo thứ tự LP, lesson active highlight cam, lesson sau lock"). UI detail xem image.
- Tiêu chí: nếu xoá text mà nhìn image vẫn hiểu → xoá

### Rule 2: KHÔNG bịa logic
- Mọi business rule trong cột Note **PHẢI có nguồn** verify được (memory đã save HOẶC Confluence cũ) — BA tự audit nội bộ, **KHÔNG cite nguồn trong spec**
- Khi viết spec mới: scan memory liên quan trước (silent audit, không ghi vào doc)
- Khi rewrite page cũ: fetch body Confluence cũ qua REST API, extract logic, KHÔNG suy diễn thêm
- ❌ BAD: "Soft delete BE — summary cũ vẫn giữ nguyên template" (nếu chưa có trong memory/Confluence)
- ✅ GOOD: chỉ ghi rule đã verify được nguồn; nếu cần thêm → đánh dấu `🔴 TBD — chưa có spec` để user confirm

### Rule 3: Note column — thông tin liên quan, KHÔNG cite US/BR
- Cột Note dành cho **business rule phụ / edge case / dependency** dev cần biết khi build
- ❌ BAD: `US-02 AC3 — đỡ phân tâm`, `BR23`, `xem [[memory-xxx]]`
- ✅ GOOD: `Pro user hide để giảm phân tâm`, `Trigger window 24h sau session abandoned`, `Lesson đỏ KHÔNG count streak`
- Nguồn (US/BR/memory) là internal tracking của BA, không belong trong spec dev đọc

### Rule 4: Proactive gap-finding (BA nghiệp vụ)
- Với MỖI page, BA phải audit toàn bộ element/flow trên Figma + source spec → nếu có gap (element chưa mô tả, flow chưa rõ, action chưa định nghĩa) → **chủ động hỏi user qua `AskUserQuestion`** trước khi publish
- KHÔNG silent skip, KHÔNG mark TBD rồi publish luôn — TBD chỉ dùng khi user explicit defer hoặc đã hỏi mà chưa có answer
- Sau khi user confirm → viết vào AC table (không bịa, dùng đúng wording user)
- Phải hỏi: dismiss/close action của modal, edge case (offline / fail / empty), animation trigger, exact copy của status text, scroll position behavior, edit/back navigation
- Output trước hỏi: "Đã audit Figma + source, còn N gap. Confirm trước khi publish:" + AskUserQuestion (gom 3-4 câu/lần)

## KHÔNG bao gồm
- ❌ Context / Background section (US v2 deprecated)
- ❌ User Story `US-NN` block
- ❌ Business Rules section riêng (gộp vào Note)
- ❌ ASCII flow inline
- ❌ Pedagogical Rationale column (internal BA memory only)
- ❌ Exception flows section (gộp vào AC table dưới dạng row)

## Naming conventions
- Page title: `{Số}. {Tên feature}` (vd `1. Home`, `2.1 Scenario Detail`)
- PNG slug: kebab-case mô tả state (vd `home-default`, `home-old-lesson-good`)
- AC heading: `Acceptance Criteria N: {tên nhóm scenario}`
