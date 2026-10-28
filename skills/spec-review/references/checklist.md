# Checklist edge case

Dùng ở vòng 1 để quét toàn bộ, và ở vòng N chỉ cho phần mà quyết định mới chạm tới. Chọn nhóm liên quan, không dán nguyên xi vào file review. Mỗi mục có ví dụ thật (đã khái quát hoá) từ các review trước, để nhận ra mẫu.

Nhóm **★** là những nhóm từng bị phát hiện muộn (vòng 2–5) dù dữ kiện có từ vòng 1. Ưu tiên quét kỹ các nhóm này.

## Mục lục
1. ★ User cũ và dữ liệu thiếu
2. ★ Mọi đường sửa của một field
3. ★ Một hành động, nhiều hệ quả
4. ★ Kết quả không đổi, giá trị biên
5. ★ Rule cũ gặp option mới
6. ★ Dữ liệu và khả năng dùng chung giữa các tính năng
7. ★ Tự kiểm phương án mình đề xuất
8. Mâu thuẫn trong doc
9. Doc viết trên nền cũ, hồi quy
10. Điểm vào, điểm ra, luồng lồng nhau
11. Vòng đời dữ liệu: empty, loading, error, offline
12. Permission và hệ thống
13. Thông báo: dialog, toast, notification
14. CTA và nhãn
15. Số liệu và mock
16. Copy, thị trường, claim
17. Phạm vi ngầm
18. Lỗi do chính design để lại

---

## 1. ★ User cũ và dữ liệu thiếu

- Với mỗi field mới: user tạo tài khoản **trước** bản này có giá trị gì?
  - **Hiển thị** gì ("Not set", ẩn row, giá trị mặc định)?
  - **Tính toán** bằng gì cho tới khi user chọn? Phải xét cả hai vế. Xét mỗi phần hiển thị là cách bị sót phổ biến nhất.
- Giá trị cũ ánh xạ sang thang mới có đúng nghĩa không?
- Field bắt buộc cho logic (ví dụ để tạo plan) mà user cũ không có thì dùng mặc định ngầm nào, và có hiện ra như user đã chọn không?
- Field mới được suy ra từ dữ liệu cũ được không?

> Ví dụ đã sót: doc thêm "Main goal" và ghi "hướng tính calo chỉ lấy từ goal". User cũ có row Main goal "Not set", nhưng doc không nói calo của họ tính theo hướng nào. Dữ kiện có từ vòng 1, tới vòng 5 mới phát hiện.
> Ví dụ: hệ số hoạt động cũ 1.55 của user cũ trùng với mức "Very active" mới. Nếu hiển thị theo ánh xạ thì như user đã tự chọn mức đó.

## 2. ★ Mọi đường sửa của một field

- Liệt kê **mọi** chỗ user có thể đổi field đó: luồng chính, sửa trực tiếp từ row, tính năng khác, import hoặc sync.
- Rule của mỗi đường có giống nhau không? Doc thường chỉ mô tả đường chính.
- Hai nơi cùng sửa một field (đồng bộ 2 chiều): xung đột xử lý thế nào, offline thì sao?

> Ví dụ đã sót: doc mô tả "đổi Main goal → mở Edit Target, picker chỉ cho chọn đúng chiều". Không ai hỏi chuyện gì xảy ra khi user bấm thẳng row Target Weight.
> Ví dụ: sửa Current Weight trong Profile và log cân ở Weigh Log cùng tạo một loại bản ghi, nhưng chỉ đường đầu kích hoạt tính lại.

## 3. ★ Một hành động, nhiều hệ quả

- Lập bảng **hành động × hệ quả**: tính lại, tạo lại dữ liệu, mở màn khác, dialog, toast, notification.
- Ô nào có ≥ 2 hệ quả: thứ tự ra sao, có gộp được không, user có bị dội nhiều thông báo không?
- Đã thấy mẫu này ở một field thì **quét ngang sang mọi field khác** ngay trong vòng đó.

> Ví dụ đã sót: vòng 2 đã phát hiện "đổi Activity level ra cả dialog calo lẫn toast plan". Nhưng không quét ngang, nên tới vòng 3 mới thấy "đổi Main goal ra 3 hệ quả cùng lúc".

## 4. ★ Kết quả không đổi, giá trị biên

- Giá trị mới **bằng** giá trị cũ thì còn thông báo, còn ghi lịch sử, còn tạo lại dữ liệu không?
- Chạm mức sàn hoặc trần (calo tối thiểu, giới hạn số item) thì sao?
- Giá trị 0, rỗng, âm, rất lớn; 0 / 1 / rất nhiều item.
- Thao tác lặp lại nhiều lần (log hằng ngày) thì thông báo có bị dày quá không? Cân nhắc ngưỡng.

> Ví dụ đã sót: "luôn hiện dialog khi goal được tính lại". User ở mức sàn 1,200 đổi một field, goal vẫn 1,200, dialog vẫn hỏi "Update to 1,200 / Keep 1,200".
> Ví dụ: dialog cập nhật goal sau mỗi lần log cân, trong khi user cân mỗi ngày và mỗi kg chỉ làm goal đổi khoảng 12–15 kcal.

## 5. ★ Rule cũ gặp option mới

- Bản cũ có validation, chặn hoặc mặc định nào giả định một option duy nhất không?
- Option mới (Gain / Maintain bên cạnh Lose; nhiều loại thay vì một) có bị rule cũ chặn sai không?
- Kịch bản content hoặc doc khác có ghi chú về xung đột này không? (Thường là có, chỉ là nằm ở doc khác.)

> Ví dụ đã sót: bản cũ chặn Target ≥ Current vì chỉ có giảm cân. Bản mới thêm "Gain muscle" nhưng không sửa rule đó. Kịch bản content Onboarding đã ghi chú việc này từ trước.

## 6. ★ Dữ liệu và khả năng dùng chung giữa các tính năng

- Field hoặc màn này có được tính năng khác đọc hoặc ghi không? Đổi ở đây thì bên kia cập nhật không?
- Doc có dựa vào một khả năng của tính năng khác (lịch, trạng thái, sự kiện) không? **Mở spec hoặc bản build của tính năng đó để xác minh khả năng ấy có thật.**
- Option và copy có khớp với nơi gốc (Onboarding, kịch bản content) không?

> Ví dụ đã sót: doc nhắc nhịn ăn "theo lịch fasting", nhưng tính năng Fasting đã ship không có lịch. Chính phương án review đề xuất ở vòng 1 cũng dựa vào "lịch fasting đang chạy".

## 7. ★ Tự kiểm phương án mình đề xuất

Với mỗi phương án (a):
- Có đường thoát nào (Back, Cancel, thoát app, mất mạng) để lại dữ liệu mâu thuẫn không?
- Có dựa vào khả năng chưa tồn tại không (xem nhóm 6)?
- Có sinh thêm màn, state, thông báo nào chưa liệt kê không?
- Nếu PM chọn (b), (b) có kéo theo câu hỏi nào không? Ghi sẵn "nếu chọn (b) cần định nghĩa thêm…".

> Ví dụ đã sót: đề xuất "đổi goal ngược chiều → lưu goal rồi mở Edit Target". Đề xuất không xét chuyện user bấm Back ở Edit Target, khi goal đã lưu còn Target vẫn ngược chiều.

## 8. Mâu thuẫn trong doc

- Hai mục, hoặc mục và AC, nói khác nhau. Trích cả hai cạnh nhau, ghi vị trí.
- Khi PM thêm quy tắc mới ở một mục, kiểm tra **mọi** câu cũ cùng chủ đề ở mục khác và ở AC. Đây là lỗi lặp lại nhiều nhất từ vòng 2.
- Đánh số trùng hoặc nhảy; mã AC trùng giữa 2 doc.
- Hai doc của cùng tính năng mô tả khác nhau (cấu trúc dữ liệu, đường vào, tên).

> Ví dụ: mục 3 đổi thành "dialog cho mọi user", nhưng 2.3.22 và 2 AC vẫn ghi "dialog nếu user đã tự đặt goal".
> Ví dụ: 3 chỗ trong doc nói 3 ý khác nhau về việc từ chối quyền camera.

## 9. Doc viết trên nền cũ, hồi quy

- Doc có mô tả theo bản đã ship hay theo một bản cũ hơn / bản chưa build không? Tên thành phần, thứ tự, nhãn.
- Vòng N: những chỗ đã sửa có bị quay lại bản cũ không?

> Ví dụ: doc dùng giỏ "Added Food" + nút LOG FOOD, trong khi bản đã build là "Your meal" + ADD. Sau một vòng sửa, tên giỏ và thứ tự macro lại quay về bản cũ.

## 10. Điểm vào, điểm ra, luồng lồng nhau

Với mỗi màn:
- Vào từ những đâu (thường nhiều hơn doc viết)? Sau khi xong thì đi đâu?
- Back hoặc Cancel khi đang có dữ liệu dở: mất hay giữ, có xác nhận không?
- Thoát app giữa chừng rồi quay lại: tiếp tục hay bắt đầu lại?
- Luồng lồng nhau (mở luồng B từ trong luồng A): state của A (giỏ, form) xử lý thế nào khi B xong hoặc huỷ?

> Ví dụ đã sót: rời màn Search khi giỏ còn món; mở Scan từ Search khi giỏ còn món.

## 11. Vòng đời dữ liệu: empty, loading, error, offline

- Empty lần đầu, và empty sau khi user xoá hết (hai trường hợp khác nhau).
- Loading lần đầu và loading khi refresh.
- Lỗi mạng, lỗi server, timeout, lỗi validation: mỗi loại có thông báo và đường thoát riêng.
- Thành công một phần (8/10 item).
- Offline hoàn toàn, mất mạng giữa luồng; đồng bộ lại khi có mạng; xung đột (last-write-wins?).
- Xoá có xác nhận hay Undo?

## 12. Permission và hệ thống

- Chưa từng hỏi / đang hỏi / đã từ chối / bị giới hạn. Đường quay lại Settings.
- **Lần sau:** đã từ chối rồi, user bấm lại tính năng thì sao?
- Hệ điều hành có phân biệt được "từ chối lần đầu" với "tắt trong Settings" không? Thường là không. Xem `platform-ios.md`.
- Có cách làm không cần quyền không (ví dụ chọn ảnh qua picker hệ thống)?

## 13. Thông báo: dialog, toast, notification

- Mỗi thông báo: điều kiện hiện, copy, nút, sau khi bấm đi đâu.
- Thông báo trùng hoặc chồng nhau (xem nhóm 3).
- Notification: lịch, huỷ khi user đã làm việc đó, giới hạn của hệ điều hành, múi giờ, lưu theo thiết bị hay theo tài khoản.
- Copy notification thuộc ai (tham số dự án). Không viết nháp phần thuộc PM.

## 14. CTA và nhãn

- Liệt kê mọi CTA cùng nhãn hoặc cùng vị trí. Cùng nhãn mà khác nghĩa, hoặc một hành động mà nhiều tên ("Log food" / "Add" / "Done"), đều phải hỏi.
- Trạng thái disabled: khi nào enable lại?

## 15. Số liệu và mock

- AC có chép số từ mock ("1 cup = 195 g", "216 kcal") thành expected value không? Số mock chỉ minh hoạ.
- Số trong mock có tự mâu thuẫn không (5 món nhưng toast "4 foods added")?
- Mock trong doc lệch với text: text thắng, nhưng phải báo.

## 16. Copy, thị trường, claim

- Chuẩn thị trường (xem skill bối cảnh): giờ 12h hay 24h, tuần bắt đầu ngày nào, sentence case, định dạng ngày và số.
- Từ ngữ nhạy cảm với tệp user; tên field đúng nghĩa (ví dụ "Sex" khi dùng cho công thức sinh học, không phải "Gender").
- Claim có số liệu ("80% more likely") hoặc chứng nhận ("Verified by nutritionists"): hỏi nguồn. Rủi ro quảng cáo sai sự thật và rủi ro review của store.
- Dùng dữ liệu user (ảnh, sức khoẻ) cho mục đích khác (train AI): có cần consent và khai báo với store không?
- Copy đã có trong doc hay design phải viết? Ai sở hữu?

## 17. Phạm vi ngầm

- Thành phần có trên mock nhưng không có mô tả (một nút "Create food" có thể là 6 màn).
- Field hoặc tính năng mới xuất hiện trong mock mà text không nhắc.
- Một câu ngắn kéo theo khối lượng lớn: chỉ ra để bảo vệ tiến độ, đề xuất tách.

## 18. Lỗi do chính design để lại

- Nhãn hoặc annotation sót khi clone connector, PM chép vào doc thành logic ("Auto next").
- Mock design có dữ liệu sai (serving, đơn vị).
- Trước khi review chế độ doc ↔ Figma, dọn Figma trước. Lỗi của design thì ghi "Lỗi của design".
