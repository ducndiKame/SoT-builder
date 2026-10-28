# Quy trình dựng SoT cho dự án mới

Tài liệu này đi từ một thư mục trống đến một SoT phase 1 đã nằm trên private repo, sẵn sàng bàn giao. Mỗi chặng ghi rõ: dùng skill nào, nhắn Claude câu gì, và đầu ra cần kiểm tra là gì.

> Đo tiến độ bằng **đầu ra mở ra kiểm tra được**, không bằng số giờ viết tài liệu.

## Tổng quan

| Chặng | Bước | Skill | Đầu ra cần kiểm tra |
|---|---|---|---|
| Nguồn | 01 Gom · 02 Chọn | `sot-init` | `sources.md` có link + owner; bảng mâu thuẫn có người chốt |
| Khung | 03 Dựng | `sot-init` | `README.md`, `CLAUDE.md` chỉ rõ thứ tự đọc |
| Phase 1 | 04 Làm | `sot-feature` (+ `spec-review`, `figma-design-rename`, `flowchart`, `document-fullstack-v2`, `design-system-build`) | Một tính năng có quyết định, AC, danh sách màn, câu hỏi mở |
| Phase 1 | 05 Thử | `sot-audit` | Báo cáo chạy thử task + danh sách lỗ hổng |
| Phase 1 | 06 Giữ / chốt | `sot-sync` | Các file đồng bộ sau mỗi quyết định; đủ 6 điều kiện DoD |
| Git | 07 Git | `sot-init` (bước Git) | Commit nền trên private repo |
| Bàn giao | 08 Bàn giao | `sot-handoff` | `BAN-GIAO.md`, người nhận mở được PR đầu tiên |

---

## Chuẩn bị (5 phút)

- Đã cài xong theo [Cài đặt](1-cai-dat.md).
- Chuẩn bị link: file Figma chính, doc PM (hoặc file spec), research nếu có.
- Trong VS Code: **File → Open Folder…** và chọn thư mục cha nơi sẽ đặt dự án, ví dụ `~/Projects`. Mở cả thư mục thay vì mở từng file rời, để Claude thấy được cây file.

## Chặng 1: Gom và chọn nguồn, dựng khung (`sot-init`)

Nhắn Claude:

> Dựng SoT cho dự án mới tên "Meditation App". Figma: <link>. Doc PM ở <portal / link>. Sản phẩm mới, iOS, thị trường US.

Claude sẽ:
1. Hỏi thêm vài câu: tệp user, ai chốt được gì, cách đọc doc PM... Trả lời ngắn. Chỗ nào chưa biết thì cứ nói chưa biết, Claude sẽ ghi "Còn mở" chứ không đoán.
2. Dựng khung thư mục. Không tạo folder rỗng.
3. Gom nguồn vào `sources.md`. Chưa kết luận nguồn nào đúng.
4. So sánh các nguồn trùng chủ đề, gắn nhãn **Hiện hành / Cũ / Còn mở**, và hỏi bạn ai chốt các chỗ mâu thuẫn.

**Bạn kiểm tra:**
- `README.md` có chỉ đúng thứ tự đọc không?
- `sources.md` có thiếu nguồn nào không? Owner có đúng không?
- Có mâu thuẫn nào bạn chốt được ngay không? Chốt luôn thì Claude ghi vào `decisions.md`.

Lúc này chưa cần đưa lên Git. Để sang chặng 4.

## Chặng 2: Làm trọn một tính năng (`sot-feature`)

Chọn **một** tính năng nhỏ làm mẫu. Ví dụ FitAgain chọn Water Tracker. Đừng làm tất cả tính năng một lúc.

> Làm tính năng water-tracker vào SoT. Section Figma "Water V1.0.0", doc PM <link>.

Trong lúc làm, `sot-feature` sẽ đề nghị gọi các skill hỗ trợ khi cần:

| Gặp tình huống | Skill hỗ trợ |
|---|---|
| Tên frame trong Figma lộn xộn (`Frame 427`, tên trùng) | `figma-design-rename` |
| Doc PM mới, mơ hồ, lệch với Figma | `spec-review`: gửi PM danh sách câu hỏi có phương án (a) |
| Chưa có AC, hoặc AC không kiểm thử được | `document-fullstack-v2` |
| Cần sơ đồ luồng | `flowchart` |
| Chưa có design system | `design-system-build`, **chế độ tối thiểu**: chỉ token và component tính năng này dùng |

**Bạn kiểm tra** "đủ sâu" theo 5 tiêu chí:
- Có quyết định, kèm phương án đã loại.
- Brief có hành vi và AC.
- `screen-inventory.md` nối được frame ↔ AC ↔ quyết định.
- Câu hỏi mở có owner.
- Trạng thái rõ ràng: Đã chốt / Đã vẽ / Còn mở.

## Chặng 3: Chạy thử bằng một task AI (`sot-audit`)

> Audit SoT dự án này và chạy thử một task với tính năng water-tracker.

Claude chạy 3 tầng kiểm tra:
1. Script kiểm tra máy móc: link chết, placeholder chưa điền, bảng quyết định thiếu người chốt...
2. Đọc hiểu để rà mâu thuẫn: quyết định ↔ brief ↔ Figma.
3. Giao một task nhỏ cho một AI mới chỉ được đọc SoT, rồi chấm xem nó có dẫn đúng nguồn và tránh được phương án đã loại không.

Kết quả lưu ở `audits/YYYY-MM-DD_sot-audit.md`.

**Bạn kiểm tra:** đọc kết quả task chạy thử. Đừng chấm UI có đẹp không. Hãy hỏi: AI phải đoán ở chỗ nào? Mỗi chỗ phải đoán là một lỗ hổng cần vá trong SoT.

## Chặng 4: Vá lỗ hổng, chốt phase 1, đưa lên Git (`sot-sync` + `sot-init`)

Vá các lỗ hổng mà audit tìm ra:

> Sửa các mục trong báo cáo audit mới nhất.

`sot-sync` lập checklist (file nào, sửa gì, vì sao) và **chờ bạn xác nhận** rồi mới sửa.

Lặp chặng 3 và 4 cho đến khi đủ **6 điều kiện Definition of Done**:
1. README chỉ lối vào và thứ tự đọc
2. Nguồn chính có owner, trạng thái, link
3. Một tính năng có quyết định, hành vi, AC và danh sách màn
4. Design system đủ token và component cho tính năng đó
5. Mâu thuẫn chưa chốt được ghi rõ
6. Đã chạy một task AI và designer đã review

Đủ 6 điều kiện thì đưa lên Git:

> Đưa SoT này lên GitHub, repo private.

Claude quét bí mật (token, mật khẩu), tạo commit nền, **hỏi bạn trước khi tạo repo**, rồi push.

## Từ đây: nhịp làm việc hằng ngày

| Khi | Nhắn Claude | Skill |
|---|---|---|
| Bắt đầu buổi làm | "pull repo" | (Git) |
| PM gửi doc mới / doc sửa | "PM vừa sửa doc <tính năng>, xem lại giúp" | `spec-review` |
| PM trả lời, hoặc bạn chốt một điều | "PM chốt SET-12 theo (a)" / "đã chốt goal 2,500 ml" | `sot-sync` |
| Bắt đầu tính năng mới | "Làm tính năng <tên> vào SoT, section Figma <...>" | `sot-feature` |
| Tính năng chốt xong | "Tính năng <tên> chốt xong rồi, dọn review" | `sot-sync` |
| Trước khi bàn giao / định kỳ | "Audit SoT" | `sot-audit` |
| Kết thúc buổi làm | "push lên repo" | (Git) |

Đổi máy: push ở máy cũ, **pull ở máy mới trước khi sửa**.

## Bàn giao (`sot-handoff`)

- **Người giao:** "Bàn giao SoT cho <tên>, GitHub <username>". Claude cập nhật README và trạng thái, chạy audit, viết `BAN-GIAO.md`, commit, push, và hỏi bạn trước khi mời người nhận vào repo.
- **Người nhận:** sau khi chấp nhận lời mời repo, nhắn "Nhận bàn giao SoT từ repo <owner>/<repo>". Claude clone, đọc lối vào, kiểm tra quyền truy cập Figma / doc, làm một task nhỏ, rồi mở pull request đầu tiên để người giao review.

---

## 30 phút đầu, nếu chỉ có 30 phút

| Thời gian | Làm gì | Skill |
|---|---|---|
| 10 phút | Mở folder trong VS Code. "Dựng SoT cho dự án <tên>": có README + sources.md | `sot-init` |
| 10 phút | Chọn một tính năng. "Làm tính năng <tên> vào SoT": có Figma, doc, quyết định | `sot-feature` |
| 10 phút | Đọc lại bản nháp, sửa chỗ sai, đánh dấu TBD | (bạn) |

Đầu ra tối thiểu: **1 lối vào + 1 bảng nguồn + 1 trang tính năng**.
