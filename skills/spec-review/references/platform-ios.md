# Điểm riêng của iOS mà doc PM hay viết sai

Đọc khi tính năng chạm tới quyền, notification hoặc hành vi hệ thống. Khi trích các điểm này vào review, ghi rõ là hành vi của nền tảng để PM không coi là ý kiến cá nhân. Nếu không chắc phiên bản iOS hiện tại còn đúng không, kiểm tra tài liệu Apple trước khi khẳng định.

## Permission (camera, ảnh, notification, vị trí, sức khoẻ)

- **Popup xin quyền của hệ thống chỉ hiện một lần** cho mỗi loại quyền. Từ lần thứ hai trở đi, app chỉ có thể dẫn user sang Settings.
  - Doc hay viết "từ chối thì lần sau hỏi lại". Điều này không làm được.
  - Cần thiết kế màn hoặc banner giải thích kèm nút "Open Settings".
- **App không phân biệt được** "user bấm Don't Allow ở popup" với "user tự tắt trong Settings". Cả hai đều là trạng thái `denied`. Doc tách 2 nhánh này thì không làm được.
- Nên có màn **giải thích trước** khi gọi popup hệ thống (pre-permission), vì chỉ có một cơ hội.
- **Ảnh:** chọn ảnh qua picker hệ thống (PHPicker) không cần quyền truy cập thư viện. Doc yêu cầu xin quyền Photos chỉ để chọn 1 ảnh là thừa.
- **Notification:** có trạng thái `provisional` (gửi lặng lẽ, không cần hỏi) và `ephemeral`. Hỏi PM có muốn dùng không nếu tính năng nhắc nhở quan trọng.
- **Vị trí và ảnh** có quyền giới hạn ("While Using", "Limited Photos"). Doc cần nói app xử lý trường hợp giới hạn thế nào.

## Notification cục bộ

- Mỗi app chỉ được **đặt lịch tối đa 64 notification đang chờ**. Lịch nhắc nhiều loại × nhiều ngày có thể vượt giới hạn; cần cách gia hạn lịch theo cuộn.
- Notification đặt theo giờ địa phương: khi user đổi múi giờ, nhắc theo giờ mới hay giờ cũ?
- "Huỷ nhắc khi user đã làm việc đó" chỉ chạy được khi app biết việc đó đã xảy ra trước giờ nhắc. Hỏi nguồn dữ liệu (log trong app, HealthKit).
- Lịch nhắc lưu theo thiết bị hay theo tài khoản: user đăng nhập trên máy thứ hai thì sao?

## Hệ thống khác

- **Dynamic Type:** text lớn làm vỡ layout cố định. Doc không nói thì design tự xử lý, nhưng báo PM.
- **App bị kill giữa luồng:** state không tự giữ. Cần quy định tiếp tục hay bắt đầu lại.
- **Apple Health:** quyền đọc không cho biết user đã từ chối hay chỉ là không có dữ liệu. App không đọc được trạng thái quyền đọc.
- **Đăng nhập Apple:** email có thể bị ẩn (relay). Tên chỉ trả về ở lần đăng nhập đầu tiên.
