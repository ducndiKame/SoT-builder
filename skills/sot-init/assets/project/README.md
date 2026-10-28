# {{PROJECT_NAME}}: nguồn thông tin dự án (SoT)

Trạng thái: **bản nháp phase 1**, dựng ngày {{DATE}}. Đây là điểm bắt đầu cho designer, PM, dev, QA và AI.

## Bắt đầu ở đây

1. Đọc [sources.md](sources.md): nguồn nào đang có hiệu lực, ai sở hữu, cần quyền truy cập gì.
2. Mở tính năng cần làm trong `features/<tính-năng>/`, đọc `CLAUDE.md` của tính năng đó trước.
3. Xem [decisions.md](decisions.md) và `decisions.md` của tính năng để biết điều gì đã chốt, vì sao, và phương án nào đã loại.

## Thứ tự nguồn sự thật

1. Quyết định **Đã chốt**: [decisions.md](decisions.md) và `features/<tính-năng>/decisions.md`.
2. Hành vi, công thức, phạm vi và AC: `features/<tính-năng>/brief/`.
3. UI và state đã vẽ: Figma (link trong [sources.md](sources.md)).
4. Token, component, copy, accessibility: [design-system/](design-system/README.md).

Điểm chưa chốt nằm trong `features/<tính-năng>/open-questions.md`. Không suy ra quyết định từ dữ liệu mock hoặc từ frame chưa có.

**Cách đọc trạng thái:** chỉ dòng **Đã chốt** có hiệu lực. **Đề xuất** là phương án chờ duyệt, kể cả khi đã có frame Figma. **Đã vẽ** không có nghĩa là **Đã duyệt**.

## Cấu trúc

- [CLAUDE.md](CLAUDE.md): bản chỉ đường ngắn cho AI, được đọc đầu mỗi phiên.
- [sources.md](sources.md): danh sách nguồn kèm link, owner, ngày và trạng thái.
- [decisions.md](decisions.md): quyết định ảnh hưởng nhiều tính năng.
- `context/`: người dùng, brand, người liên quan.
- `design-system/`: token, component, quy ước copy.
- `features/<tính-năng>/`: brief, quyết định, câu hỏi mở, danh sách màn, copy, handoff.
- `_tools/`: script sinh bản `.html` từ `.md` (chạy được trên Mac và Windows).
- `_archive/`, `research/`: chỉ tạo khi có nội dung thật.

## Cập nhật SoT

- Mỗi khi chốt một điều: ghi vào `decisions.md` kèm phương án đã loại, rồi sửa các file liên quan (brief, danh sách màn, câu hỏi mở, handoff). Skill `sot-sync` làm việc này.
- Làm việc qua Git: `pull` trước khi sửa, xem diff, `commit` kèm lý do, `push` sau khi xong.

## Definition of Done của phase 1

- [ ] README chỉ lối vào và thứ tự đọc
- [ ] Nguồn chính có owner, trạng thái và link
- [ ] Ít nhất một tính năng có quyết định, hành vi, AC và danh sách màn
- [ ] Design system đủ token và component cho tính năng đó
- [ ] Mâu thuẫn chưa chốt được ghi rõ
- [ ] Đã chạy một task với AI và designer đã review kết quả
