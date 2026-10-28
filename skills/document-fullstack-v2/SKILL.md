---
name: document-fullstack-v2
description: Viết spec feature theo format AC Gherkin (Apero standard), lấy dữ liệu Figma qua MCP `figma` chính thức, kèm Edge-Case Discovery (đọc code / spec để dò edge case chưa handle trước khi viết AC). Xuất kết quả ra file XHTML/HTML local (không tự publish). Dùng khi user yêu cầu "viết spec", "tạo doc AC Gherkin", "dò edge case cho feature" cho feature mới hoặc rewrite feature cũ. Default skill cho IIP506 và mọi app Apero sau này.
version: "2.1"
---

# AC Gherkin Doc Skill (v2.1)

Pipeline tự động: **Edge-Case Discovery → đọc Figma (qua MCP `figma`) → AC Gherkin storage XHTML → lưu file local**.

> **v2 thêm gì:** một phase **Edge-Case Discovery** trước khi viết AC table — đọc **code thật** (path-tracer) hoặc **spec/Figma** (taxonomy 5 nhóm) để liệt kê edge case CHƯA được handle, rồi đổ vào AC table. Phương pháp self-contained tại `references/edge-case-method.md` (không cần cài skill ngoài).
> **v2.1 thay đổi gì:** bỏ hẳn nhánh Confluence (script `confluence_publish.py`, credentials, bước publish/upload attachment) và bỏ MCP `figma-talk`/script `figma_export.py` (yêu cầu PAT) — toàn bộ truy cập Figma giờ dùng MCP `figma` chính thức đã kết nối sẵn trong session (OAuth, không cần PAT). Deliverable là file XHTML local, không tự đẩy lên Confluence. Xem changelog cuối file.

## Khi nào activate

User yêu cầu 1 trong các pattern:
- "Viết spec feature {X}"
- "Tạo doc AC Gherkin cho {Y}"
- "Rewrite page {Z} sang format mới"
- "/ac-gherkin {feature}"
- BA task cho IIP506, IIP505, Notica, hoặc app Apero khác

## Inputs cần có (hỏi user nếu thiếu)

| Input | Bắt buộc | Mô tả |
|---|---|---|
| `feature_name` | ✅ | Tên feature, vd "1. Home", "2. Scenario Detail" |
| `figma_url` | ✅ | Link Figma của frame/section cần viết spec (chứa `fileKey` và `node-id`) |
| `output_path` | ⚠️ | Nơi lưu file XHTML/HTML kết quả — mặc định thư mục làm việc hiện tại nếu không chỉ định |

## Figma access: MCP `figma` chính thức (đã kết nối)

Không cần PAT, không cần Figma desktop mở sẵn — dùng thẳng MCP `figma` (OAuth, remote) đã kết nối trong session. **Trước mỗi lệnh `use_figma`, luôn tải skill `figma-use` trước** (`/figma-use` hoặc resource `skill://figma/figma-use/SKILL.md`) — bắt buộc theo chính MCP này, bỏ qua sẽ lỗi khó debug.

| Việc cần làm | Tool thay thế | Ghi chú |
|---|---|---|
| Đọc tổng quan file/cấu trúc frame, connector | `mcp__figma__get_metadata` hoặc `mcp__figma__use_figma` (script đọc `figma.root.children`) | Không cần join channel, không cần file đang mở trong desktop |
| Lấy code/context + screenshot của 1 node cụ thể | `mcp__figma__get_design_context` | Cần `fileKey` + `nodeId` trích từ URL |
| Extract toàn bộ text/copy trong 1 frame (cho cột Copy vi/en) | `mcp__figma__use_figma` — script `node.query('TEXT')` hoặc `findAllWithCriteria({types:['TEXT']})`, trả về `.characters` của từng node | Thay cho `scan_text_nodes` cũ |
| Xem trực quan 1 frame (không cần export file) | `mcp__figma__get_screenshot` | Trả ảnh trực tiếp trong response, không cần lưu PNG |
| Tìm component/style/variable có sẵn trong file | `mcp__figma__search_design_system` | |
| Đọc reactions/connector giữa các frame (flow) | `mcp__figma__use_figma` — script đọc `node.reactions` | Plugin API, cần `figma-use` |

Không còn khái niệm "PAT rotation" hay batch export PNG — mọi thao tác đọc Figma đi qua MCP theo tài khoản đã OAuth.

## Workflow

### 1. Discover Figma structure
Dùng `mcp__figma__get_metadata` hoặc một script `use_figma` đọc-only để liệt kê frame/section/connector trong phạm vi cần viết spec, lưu mapping node_id → tên màn hình.

### 2. Lấy context & copy từng frame
Với mỗi frame cần đưa vào spec: gọi `mcp__figma__get_design_context` (context + screenshot) và, nếu cần bảng Copy riêng, thêm 1 lệnh `use_figma` extract text như ở bảng trên.

### 3. Build storage XHTML AC Gherkin
Dùng template `references/xhtml-template.xml` (hoặc `references/example-home-body.xml` làm mẫu) + fill các AC table. Cấu trúc bắt buộc theo `references/format-spec.md`:
- TOC macro
- System Requirement (Figma link)
- Flow (mô tả ngắn, optional diagram)
- Functional Requirement → nhiều AC (mỗi AC 1 table 7 cột)
- Validation Rules (nếu có form input)
- Non-functional Requirement (key remote bật/tắt + key remote config JSON)

### 4. Lưu file local
Ghi nội dung XHTML ra file tại `output_path` (mặc định `spec-<feature-slug>.xml` trong thư mục làm việc). Đây là deliverable cuối — nếu người dùng muốn đưa lên Confluence, họ tự dán nội dung này vào "Edit source" của trang Confluence theo cách thủ công; skill không tự gọi API publish.

## Format AC table — 7 cột bắt buộc

| Scenario | Given | When | Then | Note | Link UI | Updated Time |

- **Scenario**: số thứ tự + tên ngắn (`1. Tap "Resume conversation"`)
- **Given/When/Then**: bullet list, business-readable
- **Note**: business rule phụ / cross-link memory `[[xxx]]`
- **Link UI**: hyperlink thẳng tới frame trên Figma (`https://figma.com/design/{fileKey}?node-id={nodeId}`) — không còn `<ac:image>`/attachment vì không tự upload lên Confluence nữa
- **Updated Time**: `DD MMM YYYY`

## Quy tắc nội dung

- ❌ **KHÔNG** embed pedagogical rationale (BA tự internalize, dev không cần)
- ❌ **KHÔNG** dùng US-NN block / Context section / ASCII flow inline
- ❌ **KHÔNG mô tả UI dài bằng text** (đã có link Figma — outcome ngắn business-level, UI detail xem trực tiếp trên Figma)
- ❌ **KHÔNG bịa logic** — mọi rule cột Note PHẢI có nguồn (memory đã save HOẶC page Confluence cũ nếu user cung cấp). Nếu chưa có → đánh dấu `🔴 TBD` chờ user confirm
- ❌ **KHÔNG cite nguồn trong Note** (US-XX, BR-XX, `[[memory]]`) — đó là internal BA audit. Note chỉ chứa business rule phụ / edge case / dependency dev cần biết
- ✅ Tiếng Việt diễn giải, giữ EN cho term tech (Given/When/Then, AC, paywall, session)
- ✅ Cover happy path + validation + error/edge case **trong cùng AC table** (KHÔNG tách Exception section)
- ✅ Có Version History table đầu doc
- ✅ Có NFR section với remote key (bật/tắt + JSON config nội dung động)

## Edge-Case Discovery (v2 — chạy TRƯỚC khi viết AC table)

Đây là bước cốt lõi v2. Full phương pháp: `references/edge-case-method.md`. Tóm tắt:

1. **Chọn mode:**
   - Có source code feature → **Code-mode**: `Read` file/function/diff liên quan → chạy **path-tracer** (duyệt cơ học mọi nhánh + boundary, chỉ giữ nhánh CHƯA handle: thiếu else/default, input chưa guard, off-by-one, race/double-tap, timeout, implicit enum branch…).
   - Chỉ có Figma/spec → **Spec-mode**: duyệt **taxonomy 5 nhóm** (Input Validation · Boundary · Error States · Concurrency · Integration) trên từng input/flow.
   - Có cả hai → chạy path-tracer rồi đối chiếu taxonomy để bổ sung cái spec-level.
2. **Lập bảng finding nháp** (location · trigger · fix/guard · hậu quả). KHÔNG bịa hành vi nếu không có code.
3. **Map sang AC table**: edge case là luồng riêng → **Scenario row mới** (Given=tiền điều kiện, When=trigger, Then=hành vi+recovery); chỉ là ràng buộc phụ → cột **Note**; validation min/max/format → **Validation Rules**; remote-controlled → **NFR**.
4. **Priority** P1/P2/P3 theo Likelihood×Impact (ghi Note nếu cần nhấn; xuất Must/Should/Nice-to-test nếu làm QA plan).
5. **Recovery chưa chốt** → `🔴 TBD` → gom vào batch `AskUserQuestion`.

## Pre-write checklist (BẮT BUỘC mỗi page)

1. **Scan memory liên quan**: list file memory matching feature (vd Home → learning-path, lessons-per-week-logic, ai-speaking-streak)
2. **Kiểm tra spec cũ nếu có**: nếu user cung cấp link/nội dung page Confluence cũ hoặc file spec cũ, đọc lại trước khi viết bản mới (không tự bịa nếu không có)
3. **Liệt kê logic confirmed** trước khi viết AC table
4. **Edge-Case Discovery** (v2): chạy path-tracer trên code HOẶC taxonomy 5 nhóm trên Figma/spec → bảng finding → map vào AC table. Xem `references/edge-case-method.md`
5. **Audit gap** (Rule 4): so Figma + source spec, list element/flow chưa rõ (gộp cả edge case `🔴 TBD` từ bước 4)
6. **Hỏi user qua `AskUserQuestion`** cho từng gap (gom 3-4 câu/batch) trước khi viết file cuối
7. **Logic chưa có nguồn + user chưa confirm** → flag `🔴 TBD`, KHÔNG suy diễn

## Anti-patterns

- Tạo Context/Background section (US v2 deprecated)
- Tách Business Rules ra section riêng (gộp vào cột Note)
- ASCII state machine trong spec (dùng diagram embed nếu cần)
- Pedagogical Rationale column (internal memory only)

## References

- `references/edge-case-method.md` — **(v2)** phương pháp Edge-Case Discovery: path-tracer (code) + taxonomy 5 nhóm (spec) + map sang AC table
- `references/format-spec.md` — full spec format
- `references/xhtml-snippets.md` — Confluence storage XHTML cheatsheet (vẫn dùng để viết đúng cú pháp storage format, chỉ khác là không tự PUT lên Confluence nữa)
- `references/example-home-body.xml` — full example body của page "1. Home" IIP506

## Trong dự án SoT

Nếu dự án có `CLAUDE.md` chứa `<!-- FEATURES -->` (dựng bằng `sot-init`), mặc định `output_path` là `features/<tính-năng>/brief/YYYY-MM-DD_ac-<tính-năng>-v<x.y.z>.xml`, version lấy theo tên section Figma. Ghi thêm một dòng trỏ tới file này trong `CLAUDE.md` của tính năng, và điền cột "AC liên quan" trong `design/screen-inventory.md` theo mã AC vừa viết. AC do design viết, chưa có PM duyệt thì đánh dấu "chờ PM xác nhận".

## Changelog

- **v2.1** — Bỏ nhánh Confluence (script `confluence_publish.py`, 3 biến `CONFLUENCE_USER/PAT/BASE`, bước publish/upload attachment) và bỏ MCP `figma-talk`/script `figma_export.py` (yêu cầu `FIGMA_PAT`). Toàn bộ truy cập Figma chuyển sang MCP `figma` chính thức (OAuth, đã kết nối sẵn). Cột "Link UI" đổi từ `<ac:image>` + attachment sang hyperlink thẳng tới frame Figma. Deliverable là file XHTML lưu local, không tự publish.
- **v2.0** — Thêm phase **Edge-Case Discovery** trước khi viết AC table (path-tracer đọc code + taxonomy 5 nhóm cho spec/Figma), fold self-contained vào `references/edge-case-method.md`; thêm bước 4 vào pre-write checklist; mở rộng description để trigger cả "dò edge case". Nguồn method: gộp `bmad-review-edge-case-hunter` (path enumeration) + `deliver-edge-cases` (taxonomy + recovery + priority).
- **v1.0** — Pipeline Figma → PNG → Confluence → AC Gherkin 7 cột.
