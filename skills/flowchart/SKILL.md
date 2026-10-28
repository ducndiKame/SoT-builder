---
name: flowchart
description: >
  Vẽ flowchart luồng app/tính năng thành file diagram (Mermaid .mmd + HTML render) —
  mỗi bước có màn hình, API call (endpoint/SDK, file:line), tách nhánh success ✅ / fail ❌
  kèm mã lỗi, và retry loop. Dùng khi user nói: "vẽ flowchart", "sơ đồ luồng", "flow diagram",
  "diagram luồng app", "vẽ luồng API", "xuất flowchart", "vẽ nhánh success/fail", "app flow diagram".
  Base trên code/spec thật (audit trước, không bịa). Ghép tốt sau apero-spec-qa hoặc sau khi
  audit codebase (Explore agents) để ra điểm chạm API.
---

# Flowchart — vẽ luồng thành file diagram

Sinh **file diagram Mermaid** (`.mmd`) + **HTML render** cho một luồng app/tính năng. Diagram theo phong cách flowchart cổ điển: terminator bo tròn (start/end), chữ nhật (màn/API), hình thoi (quyết định) với nhánh ✅/❌, mũi tên nét đứt = retry.

**Nguyên tắc — KHÔNG bịa.** Chỉ vẽ từ code/spec thật. Nếu chưa có dữ liệu luồng → audit trước (đọc code hoặc dùng Explore agents), rồi mới vẽ. Chỗ chưa rõ đánh dấu `⚠️` / `TODO` trên node, không tự chế.

## Quy trình

1. **Thu thập luồng (nếu chưa có).** Xác định từng bước: màn hình → API call (endpoint/SDK method + `file:line`) → điều kiện success/fail → điều hướng. Với app iOS Apero, audit các ViewModel/Repository/DataSource; ghi rõ endpoint (`sdk.learningV2.*` v2 / `sdk.learning.*` v1), request/response, error code, retry. Nếu luồng lớn → dùng nhiều Explore agent song song theo cụm (Home→ScenarioDetail, Speaking, Wait1/QA/Summary, Quiz/Scoring, API-layer).
2. **Viết file `.mmd`** theo quy ước ở `mermaid-conventions.md` (đọc file đó). Mỗi API là 1 hình thoi `{"... OK?"}` với nhánh `|"✅ ..."|` đi tiếp và `|"❌ ERRxx·HTTP ..."|` sang node lỗi. Rẽ theo dữ liệu (pendingScore, paywall, allDrillCompleted, nextLesson) dùng hình thoi cam. Retry = `-.->|retry|`.
3. **Render ra HTML** để xem ngay:
   ```bash
   python3 "<skill>/render.py" <flow>.mmd           # → <flow>.html (Mermaid CDN + legend + bảng mã lỗi tùy chọn)
   # Windows: dùng `py` thay cho `python3` (gõ `python3` có thể mở Microsoft Store)
   ```
4. **Bàn giao.** File `.mmd` là nguồn diagram (mở/sửa/export PNG-SVG tại mermaid.live · draw.io Extras→Edit Diagram→Mermaid · VS Code Mermaid Preview). File `.html` để xem nhanh (cần mạng tải Mermaid CDN).

## Assets

| File | Vai trò |
|---|---|
| `mermaid-conventions.md` | **Đọc trước khi viết .mmd** — node types, bảng màu classDef, quy ước nhánh ✅/❌, mã lỗi, retry, terminator/decision |
| `render.py` | `.mmd` → `.html` self-contained (Mermaid CDN + legend). Optional: nhúng bảng tra mã lỗi |
| `examples/languoso-lipe-flow-to-speaking.mmd` (+ `.html`) | Ví dụ mẫu đầy đủ: luồng Languoso LIPE learning → AI Speaking, 3 phân đoạn (Scenario detail / LIPE learning / AI Speaking) gói trong subgraph, gate remote-config 2 key, nhánh ✅/❌ kèm mã lỗi (ERR107/108/17), retry `-.->`, node hide/kill per-screen |

## Mức chi tiết (tùy yêu cầu)

- "vẽ luồng" nhanh → 1 flowchart tuyến tính, mỗi bước 1 node + API chính.
- "vẽ rõ nhánh success/fail" → mỗi API là hình thoi 2 nhánh (bản đầy đủ như example).
- "bổ sung mã lỗi" → thêm `ERRxx·HTTP` lên nhãn nhánh ❌ + bảng tra mã lỗi cuối HTML.
- Luồng dài → tách nhiều diagram con (mỗi màn/cụm 1 `.mmd`) rồi link.

## Output đặt tên

`app-flow-<project>.mmd` / `<feature>-flow.mmd` + `.html` cùng stem. Đặt ở thư mục làm việc (hoặc scratchpad nếu tạm).

**Trong dự án SoT** (dựng bằng `sot-init`): lưu ở `features/<tính-năng>/design/<tính-năng>-flow.mmd` (+ `.html`). Chèn nguyên khối mermaid vào brief của tính năng **ngay dưới H1**, bọc giữa `<!-- FLOWCHART:START -->` và `<!-- FLOWCHART:END -->`, kèm một dòng trỏ về file `.mmd`. Mỗi lần sửa `.mmd` thì sửa luôn khối này. Dự án có `_tools/mmd_to_html.py` thì dùng nó thay cho `render.py` (cùng nội dung).
