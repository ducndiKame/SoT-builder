---
name: sot-audit
description: Kiểm tra sức khoẻ SoT của dự án. Skill chấm 6 điều kiện Definition of Done của phase 1; tìm link chết, placeholder chưa điền, file trỏ vào _archive, bảng quyết định thiếu người chốt, câu hỏi mở không có owner, tên file lệch version Figma, bản HTML cũ hơn Markdown, nghi lộ token; rà mâu thuẫn giữa decisions, brief, screen-inventory, open-questions và Figma; và chạy thử một task AI chỉ bằng SoT để xem SoT có đủ dùng không. Dùng skill này mỗi khi người dùng hỏi "SoT đã đủ chưa", "kiểm tra SoT", "audit SoT", "rà mâu thuẫn toàn dự án", "trước khi bàn giao kiểm tra giúp", "thử xem AI dùng SoT có đúng không", "chạy thử task với SoT", "còn chỗ nào lệch giữa doc và Figma", kể cả khi không nói chữ "audit". KHÔNG dùng để sửa (sau audit, việc sửa đi qua sot-sync) hay review một doc PM mới (spec-review).
---

# SoT Audit: SoT đã dùng được chưa?

Bước 05 trong quy trình 8 bước, và là bước kiểm tra trước khi bàn giao. Một folder gọn gàng chưa chắc đã là SoT tốt. SoT tốt khi:
- người mới tìm được câu trả lời;
- AI dùng đúng nguồn và tránh được phương án đã loại;
- quyết định mới đã lan tới mọi file liên quan.

Skill này **chỉ kiểm tra và báo cáo, không tự sửa.** Sửa thì đi qua `sot-sync`, có checklist và có người dùng xác nhận.

Có 3 tầng kiểm tra. Mặc định chạy cả 3. Người dùng chỉ muốn nhanh thì chạy tầng A.

## Tầng A: Kiểm tra máy móc (script)

```bash
python3 <thư mục skill>/scripts/audit_sot.py "<thư mục dự án>"
```

Trên Windows thay `python3` bằng `py`. Script chỉ đọc, không sửa, và bỏ qua thư mục `audits/` (báo cáo cũ). Kết quả có 3 mức:
- **Lỗi** (phải sửa): link chết, bảng Tính năng lệch với thư mục, nghi lộ token.
- **Cảnh báo:** link trỏ vào `_archive/`, placeholder chưa điền, bảng quyết định thiếu người chốt hoặc thiếu phương án đã loại, câu hỏi mở không có owner, thiếu `sources.md`, trạng thái nguồn không chuẩn, bản `.html` cũ hơn `.md`.
- **Thông tin:** frame chưa có AC, số frame ghi trong `CLAUDE.md` hoặc heading lệch với bảng, tên file thiếu ngày hoặc version.

Đọc lại từng mục trước khi đưa vào báo cáo. Script dùng heuristic nên có thể báo nhầm, ví dụ một dòng "Ghi chú" cố ý nằm trong bảng quyết định. Mục nào báo nhầm thì bỏ, và ghi lại lý do.

**Nghi lộ token** thì báo người dùng ngay, kể cả khi đang giữa chừng. Nếu file đã từng được push, token cần được thu hồi, không chỉ xoá khỏi file.

## Tầng B: Kiểm tra mâu thuẫn (đọc hiểu)

Làm cho từng tính năng. Có nhiều tính năng thì ưu tiên tính năng đang làm và tính năng sắp bàn giao.

1. **Quyết định ↔ brief:** mỗi dòng Đã chốt trong `decisions.md` có được phản ánh trong brief mới nhất không? Brief có câu nào còn ghi theo quyết định cũ hoặc phương án đã loại không?
2. **Quyết định ↔ open-questions:** có câu nào đã chốt mà vẫn nằm ở mục chưa trả lời không? Ngược lại, có câu "Đã trả lời" nào chưa được ghi vào decisions không?
3. **screen-inventory ↔ Figma:**
   - Lấy mẫu 3–5 frame. Đọc text thật bằng `use_figma` chạy script chỉ đọc (lấy `characters` của text node), hoặc nhìn qua `get_screenshot`. Đừng tin tên layer trong `get_metadata`: tên layer thường là câu cũ còn sót. Text có khớp quyết định không, ví dụ con số, nhãn, đơn vị?
   - Frame mới trong section đã có trong inventory chưa?
   - Note ⚠️ còn sót trên frame mà câu hỏi tương ứng đã chốt không?
4. **Lối vào:**
   - Dòng "Trạng thái" trong `CLAUDE.md` của dự án và tính năng có khớp thực tế không?
   - `sources.md` có nguồn nào ghi Hiện hành mà thực ra đã có bản mới thay chưa?
5. **Tính năng dùng chung dữ liệu:** một quyết định ở tính năng A (ví dụ đơn vị đo) có làm sai chỗ nào ở tính năng B không? Ở tính năng B chỉ đọc phần dùng chung dữ liệu đó, không audit toàn bộ tính năng B.

Mỗi mâu thuẫn ghi đủ: **file A nói gì** (trích, kèm dòng) · **file B nói gì** · **bên nào đúng theo thứ tự nguồn sự thật**. Thứ tự nguồn lấy theo `CLAUDE.md` dự án. Nếu thứ tự nguồn không đủ để phân xử thì ghi "cần người dùng chốt".

Phân loại từng mâu thuẫn:
- **Quyết định:** cần người dùng hoặc PM chọn.
- **Đồng bộ:** đã có bên đúng, chỉ cần sửa chữ ở bên kia. Claude sửa được qua `sot-sync`.

## Tầng C: Chạy thử một task AI

Đây là phép thử thật nhất. Nó dùng chính SoT làm đầu vào cho một task design nhỏ.

1. **Chọn task** cùng người dùng. Nên là task chạm một quyết định Đã chốt có phương án đã loại, vì đó là chỗ AI dễ sai nhất. Ví dụ: "Phác card Home Water cho người dùng mới ở chế độ metric". Người dùng không có ý tưởng thì đề xuất 2–3 task từ chính `decisions.md`.
2. **Giao task cho một subagent mới** (Agent tool). Subagent không có ngữ cảnh của cuộc trò chuyện này, nên kết quả phản ánh đúng việc SoT tự đủ hay chưa. Prompt cho subagent gồm 4 mảnh:
   - **Nhiệm vụ:** task nhỏ, cụ thể.
   - **Nguồn:** chỉ đường dẫn thư mục dự án và lời dặn "bắt đầu từ CLAUDE.md". Dặn thêm: chỉ đọc file trong thư mục đó; không dùng Figma, web, memory của người dùng hay kiến thức có sẵn về dự án; cuối bài liệt kê mọi file đã mở. Subagent có thể có sẵn quyền Figma MCP và memory về chính dự án này. Nếu nó dùng những nguồn đó, phép thử "SoT tự đủ" không còn ý nghĩa.
   - **Ranh giới:** không tự chốt điều chưa có trong SoT.
   - **Đầu ra:** phương án kèm **nguồn của từng con số và từng hành vi**, cùng danh sách giả thuyết cần designer kiểm tra.
3. **Chấm kết quả.** Không chấm độ đẹp. Chấm theo các câu hỏi sau:
   - Có tìm đúng file không?
   - Có dùng giá trị Đã chốt, và tránh phương án đã loại không?
   - Có dẫn nguồn cho từng ý không?
   - Có tách được giả thuyết khỏi điều đã chốt không?
   - Phải đoán ở chỗ nào?
   Chỗ subagent phải đoán chính là **lỗ hổng của SoT**.
4. Ghi lại task, prompt, kết quả và danh sách lỗ hổng vào báo cáo. Đây là bằng chứng cho điều kiện DoD số 6.

## Chấm Definition of Done phase 1

| # | Điều kiện | Bằng chứng cần thấy |
|---|---|---|
| 1 | README chỉ lối vào và thứ tự đọc | README.md có mục "Bắt đầu ở đây" và thứ tự nguồn |
| 2 | Nguồn chính có owner, trạng thái, link | sources.md không còn ô owner / trạng thái trống ở nguồn chính |
| 3 | Một tính năng có quyết định, hành vi, AC, UI map | Một folder có decisions (Đã chốt), brief có AC, screen-inventory nối frame ↔ AC |
| 4 | Design system đủ token và component cho tính năng đó | design-system/ nêu được token và component mà tính năng mẫu dùng |
| 5 | Mâu thuẫn chưa chốt được ghi rõ | Mâu thuẫn tìm được ở tầng B đều đã nằm trong open-questions hoặc bảng mâu thuẫn của sources.md |
| 6 | Đã chạy một task AI và designer đã review | Có kết quả tầng C, và người dùng đã xem |

Mỗi điều kiện chấm **Đạt / Chưa đạt / Đạt một phần**, kèm bằng chứng (đường dẫn file). Chấm theo **chức năng**, không theo tên file hay tên heading:
- DoD 1: README chỉ được lối vào và thứ tự nguồn là đạt, dù heading không tên là "Bắt đầu ở đây".
- DoD 2: không có `sources.md`, nhưng có một bảng tương đương (ví dụ trong `CLAUDE.md`), thì chấm theo bảng đó. Bảng có đủ owner, trạng thái, link: **Đạt một phần**, vì nguồn chưa nằm ở chỗ chuẩn. Thiếu owner hoặc trạng thái: **Chưa đạt**.
- DoD 3: chấm tính năng mẫu người dùng chọn. Người dùng chưa chọn thì chấm tính năng đầy đủ nhất, và ghi rõ đã chọn tính năng nào.
- DoD 5: mâu thuẫn được tính là "đã ghi rõ" nếu nằm trong `open-questions.md`, trong bảng mâu thuẫn của `sources.md`, hoặc trong một file ghi lệch mà lối vào có trỏ tới (ví dụ `doc-vs-design.md`, mục ⚠️ trong brief). Mâu thuẫn chỉ ghi ở file không ai trỏ tới thì chưa tính. Đủ 6 điều kiện thì SoT sẵn sàng cho commit nền hoặc bàn giao. Chưa đủ thì vẫn giữ trạng thái nháp: Git vẫn lưu được bản nháp, nhưng chưa nên gọi đó là bản nền để bàn giao.

## Báo cáo

Lưu `audits/YYYY-MM-DD_sot-audit.md` trong thư mục dự án (tạo `audits/` nếu chưa có), rồi sinh `.html` bằng `_tools/md_to_html.py`.

Dự án chưa có `_tools/md_to_html.py`:
- dùng bản dự phòng ở `<thư mục skill sot-init>/assets/project/_tools/md_to_html.py`;
- đưa việc "chép `_tools/` vào dự án" vào danh sách đề xuất sửa;
- không vá tay file `.html`.

Bố cục báo cáo:

1. **Kết luận:**
   - DoD đạt mấy trên 6;
   - SoT đã sẵn sàng bàn giao chưa;
   - **3 vấn đề đáng sửa nhất**.
2. **Bảng DoD**, kèm bằng chứng.
3. **Mâu thuẫn** (tầng B): bảng gồm các cột "File A / File B / Bên đúng theo thứ tự nguồn / Loại (quyết định / đồng bộ) / Ai cần chốt".
4. **Chạy thử task** (tầng C): task, kết quả tóm tắt, lỗ hổng tìm được.
5. **Kiểm tra máy móc** (tầng A): gộp theo mã, bỏ các mục báo nhầm.
6. **Đề xuất sửa:**
   - danh sách có thể chuyển thẳng cho `sot-sync`;
   - việc nào Claude sửa được ngay (link chết, placeholder, HTML cũ);
   - việc nào cần người dùng hoặc PM quyết định.

Trong chat chỉ nói phần Kết luận và đường dẫn file báo cáo (link markdown tới file `.md`, không publish ra ngoài). Hỏi người dùng có muốn chạy `sot-sync` cho danh sách sửa không.
