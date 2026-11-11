---
name: document-fullstack-v2
description: Viết spec feature theo format AC Gherkin (Apero standard), lấy dữ liệu Figma qua MCP `figma` chính thức, kèm Edge-Case Discovery (đọc code / spec để dò edge case chưa handle trước khi viết AC). Xuất kết quả ra file XHTML/HTML local (không tự publish). Dùng khi user yêu cầu "viết spec", "tạo doc AC Gherkin", "dò edge case cho feature" cho feature mới hoặc rewrite feature cũ. Default skill cho IIP506 và mọi app Apero sau này.
version: "2.3"
---

# AC Gherkin Doc Skill (v2.3)

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

### 2b. Flowchart (BẮT BUỘC, v2.2)
Gọi skill `flowchart` để vẽ luồng của tính năng theo Figma + doc (mỗi bước là màn, tách nhánh, retry). Lưu `.mmd` + `.html` theo skill đó (dự án SoT: `design/<tính-năng>-flow.mmd`). Nhúng **nguyên văn** sơ đồ vào mục Flow của doc (xem `references/xhtml-snippets.md` → "Flowchart mermaid"), bọc giữa `<!-- FLOWCHART:START -->` / `<!-- FLOWCHART:END -->`. Sửa `.mmd` thì sửa luôn khối này.

### 2c. Chụp UI từ Figma thành ảnh (BẮT BUỘC, v2.2)
Doc phải có **ảnh UI thật**, không chỉ link:
1. Mỗi frame xuất hiện ở cột Link UI → `mcp__figma__get_screenshot` (`maxDimension` 800, không bật base64) lấy URL ảnh.
2. Tải ảnh về bằng `curl -f -L -o <slug>.png "<url>"` vào thư mục `<tên-doc>_assets/` cạnh file `.xml` (URL chỉ sống ngắn hạn, tải ngay). `slug` kebab-case theo state, ví dụ `fasting-running.png`.
3. Cột Link UI: `<ac:image ac:width="220"><ri:attachment ri:filename="<slug>.png"/></ac:image>` rồi tới hyperlink Figma. Frame có popup / sheet thì chụp frame chứa popup / sheet đó.
4. Kiểm tra: không còn ô Link UI nào chỉ có link (trừ scenario thuần logic, ghi "—").

### 3. Build storage XHTML AC Gherkin
Dùng template `references/xhtml-template.xml` (hoặc `references/example-home-body.xml` làm mẫu) + fill các AC table. Cấu trúc bắt buộc theo `references/format-spec.md`:
- TOC macro
- Version History
- System Requirement (Figma link)
- **Phạm vi** (v2.3, bắt buộc): có / không có trong bản này, dữ liệu lưu ở đâu, thay đổi so với bản trước (bảng cũ → mới nếu doc PM có)
- Flow (2–3 câu + **flowchart mermaid từ bước 2b**)
- Functional Requirement → nhiều AC (mỗi AC 1 table 7 cột, cột Link UI có **ảnh** từ bước 2c)
- **UI Copy** (v2.3, bắt buộc): bảng `Màn / thành phần | Copy (EN) | Biến thể / điều kiện | Ghi chú`, chép **nguyên văn** từ Figma (`use_figma` lấy `.characters`) và doc PM, đủ mọi biến thể (theo trạng thái, theo mục tiêu, lỗi, toast, popup, push). Copy Figma lệch doc PM thì ghi cả hai ở cột Ghi chú, không tự chọn
- **Tham chiếu tính toán** (v2.3, bắt buộc khi doc PM có công thức / bảng mức / ví dụ): công thức, bảng ngưỡng, định nghĩa chỉ số, ví dụ tính của PM giữ đủ số liệu. Không chép lại business rule đã nằm ở cột Note
- Validation Rules (nếu có form input)
- Non-functional Requirement (key remote bật/tắt + key remote config JSON)

Thứ tự H1: Version History › System Requirement › Phạm vi › Flow › Functional Requirement › UI Copy › Tham chiếu tính toán › Validation Rules › NFR.

### 3b. Tự đối chiếu với doc PM (BẮT BUỘC, v2.3)
Doc AC phải **đủ thông tin như doc PM**: quy tắc "không mô tả UI bằng chữ" chỉ áp cho cột Then, không được làm mất copy, phạm vi, công thức hay ví dụ tính. Trước khi báo xong:
1. Liệt kê từng mục / ý của doc PM (business rule, edge case, copy, phạm vi, công thức, ví dụ, thay đổi so với bản trước) kèm một chuỗi đặc trưng của mục đó.
2. Chạy script tìm chuỗi (chuẩn hoá khoảng trắng, entity, dấu nháy, chữ thường) trên file `.xml` và in `N/M có trong doc AC` + danh sách THIẾU.
3. Bổ sung mọi mục thiếu, chạy lại tới khi đủ (mục chỉ khác tiêu đề thì ghi rõ trong báo cáo).
Happy case **không** cần mục riêng: đã nằm trong các bảng AC.

### 4. Lưu file local + bản HTML
Ghi nội dung XHTML ra file tại `output_path` (mặc định `spec-<feature-slug>.xml` trong thư mục làm việc). Sau đó chạy `python scripts/xhtml_to_html.py <file>.xml` để sinh `<file>.html` tự chứa: ảnh nhúng base64 và flowchart được render, gửi file đi vẫn xem được. Script báo ảnh thiếu thì tải bổ sung rồi chạy lại. Muốn đưa lên Confluence: dán XHTML vào "Edit source" và upload thư mục `_assets` làm attachment; skill không tự gọi API publish.

## Format AC table — 7 cột bắt buộc

| Scenario | Given | When | Then | Note | Link UI | Updated Time |

- **Scenario**: số thứ tự + tên ngắn (`1. Tap "Resume conversation"`)
- **Given/When/Then**: bullet list, business-readable
- **Note**: business rule phụ / cross-link memory `[[xxx]]`
- **Link UI**: **ảnh chụp frame** (`<ac:image>` + attachment trong `<tên-doc>_assets/`, bước 2c) **và** hyperlink tới frame Figma (`https://figma.com/design/{fileKey}?node-id={nodeId}`). Chỉ có link là thiếu (v2.2)
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

Nếu dự án có `CLAUDE.md` chứa `<!-- FEATURES -->` (dựng bằng `sot-init`), mặc định `output_path` là `features/<tính-năng>/brief/YYYY-MM-DD_ac-<tính-năng>-v<x.y.z>.xml`, version lấy theo tên section Figma. Ảnh UI ở `brief/YYYY-MM-DD_ac-<tính-năng>-v<x.y.z>_assets/`, flowchart ở `design/<tính-năng>-flow.mmd` (+ `.html`). Ghi thêm một dòng trỏ tới file này trong `CLAUDE.md` của tính năng, và điền cột "AC liên quan" trong `design/screen-inventory.md` theo mã AC vừa viết. AC do design viết, chưa có PM duyệt thì đánh dấu "chờ PM xác nhận".

**Khi doc PM và design của tính năng đã chốt**, doc chính thức của tính năng trong SoT **luôn** viết bằng skill này (kèm flowchart từ skill `flowchart` và ảnh UI cắt từ Figma), không viết spec Markdown thủ công. Doc này thay hoàn toàn brief / spec cũ của cùng version: chuyển bản cũ vào `_archive/`, sửa link, rồi chạy `sot-sync` để dọn handoff, ui-copy, doc-vs-design và flowchart.

## Changelog

- **v2.3** — Doc AC phải đủ thông tin như doc PM: thêm 3 mục bắt buộc **Phạm vi**, **UI Copy** (nguyên văn Figma + PRD, đủ biến thể), **Tham chiếu tính toán** (công thức, bảng mức, ví dụ tính); thêm bước 3b tự đối chiếu từng mục doc PM bằng script tìm chuỗi trước khi báo xong. Happy case không có mục riêng (đã nằm trong AC).
- **v2.2** — Doc bắt buộc có **flowchart** (gọi skill `flowchart`, nhúng mermaid vào mục Flow) và **ảnh UI chụp từ Figma** trong cột Link UI (`get_screenshot` → tải PNG vào `_assets/` → `<ac:image>`), không chỉ link. Thêm `scripts/xhtml_to_html.py` sinh HTML tự chứa (ảnh base64, render mermaid). Quy tắc SoT: doc PM + design chốt → doc tính năng viết bằng skill này.
- **v2.1** — Bỏ nhánh Confluence (script `confluence_publish.py`, 3 biến `CONFLUENCE_USER/PAT/BASE`, bước publish/upload attachment) và bỏ MCP `figma-talk`/script `figma_export.py` (yêu cầu `FIGMA_PAT`). Toàn bộ truy cập Figma chuyển sang MCP `figma` chính thức (OAuth, đã kết nối sẵn). Cột "Link UI" đổi từ `<ac:image>` + attachment sang hyperlink thẳng tới frame Figma. Deliverable là file XHTML lưu local, không tự publish.
- **v2.0** — Thêm phase **Edge-Case Discovery** trước khi viết AC table (path-tracer đọc code + taxonomy 5 nhóm cho spec/Figma), fold self-contained vào `references/edge-case-method.md`; thêm bước 4 vào pre-write checklist; mở rộng description để trigger cả "dò edge case". Nguồn method: gộp `bmad-review-edge-case-hunter` (path enumeration) + `deliver-edge-cases` (taxonomy + recovery + priority).
- **v1.0** — Pipeline Figma → PNG → Confluence → AC Gherkin 7 cột.
