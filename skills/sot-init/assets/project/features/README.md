# Features

Mỗi tính năng là một thư mục con, tạo bằng skill `sot-feature`. Tên thư mục: kebab-case tiếng Anh, ví dụ `onboarding`, `water-tracker`, `paywall`.

## Cách đọc một tính năng
1. `CLAUDE.md` của tính năng: trạng thái và nguồn.
2. `decisions.md`: chỉ dòng **Đã chốt** có hiệu lực. Đổi ý thì thêm dòng mới, ghi "thay thế #N".
3. `brief/`: hành vi và AC đúng phiên bản.
4. `design/screen-inventory.md`: frame Figma ↔ AC ↔ quyết định. **Đã vẽ** chỉ là trạng thái thiết kế; ô **Chưa có AC riêng** là lỗ hổng.
5. `open-questions.md`: những gì chưa chốt, ai cần trả lời.

## Khi chốt hoặc sửa một hành vi
Cập nhật theo thứ tự: quyết định → brief/AC → Figma → screen-inventory → open-questions → handoff. Ghi ngày, rồi sinh lại `.html`. Skill `sot-sync` làm việc này.
