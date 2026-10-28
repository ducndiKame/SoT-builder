# {{PROJECT_NAME}}

> Claude tự đọc file này ở đầu mỗi phiên. Giữ ngắn (dưới 100 dòng): chỉ chỉ đường, không chứa nội dung chi tiết.

## Trạng thái (cập nhật {{DATE}})
- Giai đoạn: {{STAGE}}
- Đang làm: <tính năng + việc cụ thể>
- Đang chặn: <chờ ai, chờ gì, hoặc "không">

## Sản phẩm
- Là gì: {{PRODUCT_ONE_LINER}}
- Nền tảng: {{PLATFORM}}
- End user: {{AUDIENCE_ONE_LINER}} (chi tiết ở context/brand-and-audience.md)

## Nguồn sự thật
Khi hai nguồn lệch nhau, ưu tiên theo thứ tự:
1. **Quyết định đã chốt** trong `decisions.md` hoặc `features/<tính-năng>/decisions.md`
2. **Logic và AC** trong brief mới nhất của tính năng (`features/<tính-năng>/brief/`)
3. **UI và state đã vẽ** trong Figma
4. **Token, accessibility, quy ước copy** trong `design-system/`

Ba nhãn trạng thái dùng trong mọi file:
- **Đã chốt**: người có quyền đã xác nhận. Chỉ nhãn này mới là hành vi có hiệu lực.
- **Đã vẽ**: frame có thật trong Figma. Không có nghĩa là đã duyệt hay đủ AC.
- **Còn mở**: chưa có câu trả lời, nằm trong `open-questions.md`. Không tự chọn một phía.

Số liệu minh hoạ trong Figma không phải expected value. Ô "Chưa có AC riêng" là lỗ hổng cần báo, không phải quyền tự suy ra hành vi.

| Thứ | Ở đâu |
|---|---|
| Danh sách nguồn (link, owner, trạng thái) | sources.md |
| Figma chính | {{FIGMA_URL}} |
| Design system | design-system/README.md |
| Brand, audience, tone | context/brand-and-audience.md |
| Người liên quan, ai chốt được gì | context/stakeholders.md |
| Quyết định cấp dự án | decisions.md |

## Tính năng
| Tính năng | Folder | Trạng thái |
|---|---|---|
<!-- FEATURES -->

## Quy ước đặt tên
- Tài liệu có phiên bản: `YYYY-MM-DD_mo-ta-ngan-vX.Y.Z.md`. Version **lấy đúng như tên section/page trong Figma** (ví dụ `settings-v1.0.1`), không tự đặt v1/v2.
- Vòng review dùng hậu tố `-rN` (ví dụ `spec-review-onboarding-v1.0.1-r2`), không dùng `-vN`.
- Handoff theo version: `handoff/handoff-vX.Y.Z.md`, là file sống.
- Mỗi file `.md` gửi người đọc có bản `.html` cùng tên, sinh bằng `_tools/md_to_html.py`. Không sửa tay file `.html`.
- Tên frame Figma: `<Flow> / <Sub-flow> / <Screen> — <State> (<Qualifier>)`.

## Quy ước chung
- UI copy: {{COPY_LOCALE}}, sentence case
- Lưới 4pt; chỉ dùng color/text style và component có sẵn trong file Figma
- Có bản spec mới: chuyển bản cũ vào `_archive/`, sửa mọi link trỏ tới nó
- Tính năng chốt xong và đã có doc chính thức trong `brief/`: xoá các file review của tính năng đó

## Spec review (tham số cho skill `spec-review`)
- Doc PM: {{PM_DOC_SOURCE}}
- Lưu: `features/<tính-năng>/brief/YYYY-MM-DD_spec-review-<tính-năng>-vX.Y.Z[-rN].md` + .html
- Copy: UI copy do design đề xuất; copy notification / marketing do PM đề xuất
- Tin gửi PM: {{PM_NAME_AND_TONE}}

## Đừng đọc
- `_archive/`: bản cũ đã bị thay thế
