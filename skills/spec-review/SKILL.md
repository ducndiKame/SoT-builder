---
name: spec-review
description: Review và phản biện tài liệu yêu cầu của PM (spec, PRD, user story, ticket, doc portal) trước và trong lúc thiết kế, với mục tiêu chốt doc và design trong khoảng 2 vòng. Vòng 1 quét đủ edge case theo checklist. Từ vòng 2 chỉ xét phần doc thay đổi và quét hồi quy. Mỗi câu hỏi gắn nhãn chặn design / không chặn design, có phương án (a) đề xuất, và design được chốt ngay khi hết câu chặn design. Kèm đồng bộ Figma với doc và xuất bản tin gửi PM. Dùng skill này mỗi khi người dùng đưa link hoặc file tài liệu yêu cầu và muốn đọc, review, kiểm tra, đối chiếu với design, hoặc hỏi "PM vừa sửa doc, xem lại giúp", "doc đã chốt chưa", "còn case nào thiếu", "design có khớp doc không", "viết câu hỏi gửi PM", kể cả khi họ không nói chữ "review". Thay thế skill pm-spec-review cũ. KHÔNG dùng cho câu hỏi thiết kế chung không kèm tài liệu yêu cầu, hoặc khi chỉ cần viết spec mới từ đầu.
---

# Spec Review

Mục tiêu: **chốt doc và design trong 2 vòng**.
- **Vòng 1** tìm đủ vấn đề và gửi PM một danh sách gọn, PM trả lời được ngay.
- **Vòng 2** khép lại: kiểm câu trả lời, sửa Figma, rồi xuất bản cuối.

Chỉ mở vòng 3 khi PM đổi phạm vi hoặc ra quyết định mới sinh thêm câu chặn design. Khi đó nói rõ với người dùng lý do phải có thêm vòng.

Bài học gốc của skill (từ 3 tính năng thật, mỗi cái 3–5 vòng): phần lớn case xuất hiện muộn **không phải do doc mới sinh ra**. Chúng có đủ dữ kiện từ vòng 1 nhưng bị bỏ sót, vì từ vòng 2 người review chỉ nhìn phần doc thay đổi. Một số case khác nằm ngay trong phương án mà chính review đề xuất. Checklist ở `references/checklist.md` được viết để bắt đúng những thứ đó.

Chạy song song với skill bối cảnh của người dùng nếu có (ví dụ `design-context`: chuẩn copy, accessibility, thị trường).

---

## Nguyên tắc

1. **Đọc hết rồi mới phán xét.** Nhiều thứ trông như thiếu ở mục 2 lại được viết ở mục 7. Báo thiếu sai làm mất uy tín cả bản review.
2. **Không tự suy luận thay người dùng hay PM.** Tách rõ **"Doc ghi"** với **"Tôi suy ra (cần xác nhận)"**. Không ghi "Đã chốt" khi chưa ai xác nhận. Quyết định thuộc phần design cũng phải hỏi người dùng (AskUserQuestion) trước khi ghi là đã chốt.
3. **Mỗi câu hỏi đều có phương án.** Câu đóng, (a) là phương án đề xuất kèm lý do, có cột ảnh hưởng. PM chỉ cần trả lời bằng chữ cái.
4. **Gắn nhãn chặn design.** Đây là thứ quyết định khi nào xong (xem "Tiêu chí chốt design").
5. **Tự nhận lỗi.** Case bị sót từ vòng trước thì ghi "Bỏ sót từ vòng N". Lỗi do chính design để lại (nhãn sót trong Figma, mock sai) thì ghi "Lỗi của design". Người đọc tin bản review hơn khi nó trung thực.
6. **Không bịa vấn đề.** Doc đủ rõ thì nói thẳng là đủ rõ.

---

## Bước 0 — Lấy tham số dự án

Skill dùng chung cho nhiều dự án, nên những gì riêng của từng dự án nằm ở `CLAUDE.md` của dự án, mục **"Spec review"**. Đọc mục đó trước. Nếu chưa có, hỏi người dùng **một lần** những tham số còn thiếu, rồi đề nghị ghi vào `CLAUDE.md` để lần sau không phải hỏi lại.

| Tham số | Ví dụ |
|---|---|
| Nguồn doc và cách đọc | Portal nội bộ đọc qua MCP X (WebFetch bị chặn đăng nhập); Google Docs qua connector; file .docx |
| Thứ tự nguồn sự thật (SoT) | Quyết định đã chốt → text doc PM (không theo mock) → Figma → design system |
| Nền cần đối chiếu | Bản đã ship (V1.0.0), Onboarding, các tính năng dùng chung dữ liệu |
| Figma | File, page, section (tìm section theo tên vì ID có thể đổi) |
| Nơi lưu file | `features/<tính-năng>/brief/`, bản cũ chuyển vào `_archive/` |
| Định dạng phụ | Có cần file .html đi kèm không, render bằng gì |
| Sở hữu copy | UI copy: design đề xuất. Notification / marketing: PM đề xuất, design không viết nháp |
| Tiền tố mã câu hỏi | Theo tính năng: `SET`, `REM`, `SCAN`… |
| Thị trường và nền tảng | en-US, iOS (bật phần nền tảng trong checklist) |
| Người nhận và cách xưng hô trong tin gửi PM | "em" / "anh, chị" |

---

## Bước 1 — Xác định đây là vòng mấy

- **Chưa có review nào cho doc này** → **Vòng 1** (Bước 2).
- **Đã có review trước** → **Vòng N** (Bước 3). Tìm review gần nhất trong thư mục brief của tính năng.
- **PM viết lại doc theo design** (doc mô tả lại Figma) → chạy Vòng N theo **chế độ doc ↔ Figma**. Dọn nhãn và annotation sót trong Figma trước, vì PM hay chép nguyên cả nhãn sót vào doc thành logic.
- **Doc gồm nhiều tính năng độc lập** → vòng 1 có thể gộp chung. Từ vòng 2, tách mỗi tính năng một file và trỏ chéo nhau, để PM trả lời từng doc độc lập.

**Khi đọc doc, luôn ghi:** phiên bản, ngày, message của lần sửa cuối, và slug / ID. Doc có thể đổi slug, đổi ID hoặc đánh lại số AC giữa các vòng. Có công cụ diff hoặc changelog thì dùng, không có thì so tay với review trước.

**Mock và text:** ảnh mock trong doc thường cũ hơn text. Text là SoT. Mock lệch với text thì báo một lần, rồi đề nghị PM ghi chú "Mock minh hoạ bố cục — nội dung theo text" dưới mỗi ảnh.

---

## Bước 2 — Vòng 1: quét đủ

Mục tiêu của vòng 1: sau vòng này, mọi vòng sau chỉ còn việc khép câu.

1. **Đọc hết doc một lượt, chỉ ghi chép:** mục tiêu thật của tính năng (PM muốn thay đổi hành vi gì của user), danh sách hành động của user, và mọi chỗ có số liệu, rule, ràng buộc.
2. **Đọc nền cần đối chiếu:** bản đã ship, tính năng dùng chung dữ liệu, kịch bản copy. Doc mới thường viết trên nền cũ hoặc trên một bản chưa build.
3. **Lập 2 bảng làm việc.** Hai bảng này chỉ để quét, không bắt buộc đưa vào file review:
   - **Bảng field:** mỗi dòng là một field hoặc setting user đổi được. Các cột: đường vào / đường sửa · hệ quả (tính lại, tạo lại, điều hướng, thông báo) · user cũ / dữ liệu thiếu · giá trị không đổi hoặc chạm biên · rule cũ còn đúng với option mới không · tính năng nào dùng chung.
   - **Bảng màn:** mỗi dòng là một màn. Các cột: vào từ đâu · ra đi đâu · Back / Cancel khi có dữ liệu dở · offline / lỗi · luồng lồng nhau · CTA cùng nhãn hoặc cùng vị trí.
   Ô nào trống hoặc có từ 2 hệ quả trở lên là một câu hỏi tiềm năng.
4. **Chạy checklist** ở `references/checklist.md`. Chỉ chọn nhóm liên quan, không dán nguyên xi.
5. **Tự kiểm phương án mình đề xuất.** Đây là chỗ bị sót nhiều nhất:
   - Phương án (a) có đường thoát nào (Back, Cancel, thoát app) để lại dữ liệu mâu thuẫn không?
   - Nó có dựa vào khả năng của tính năng khác không? Mở spec hoặc bản build của tính năng đó để xác minh khả năng ấy thật sự có.
   - Nó có sinh thêm thông báo, màn hoặc state mới nào chưa được liệt kê không?
6. **Phân loại** (Bước 4), rồi **viết file** (Bước 6).

---

## Bước 3 — Vòng N: chỉ xét phần thay đổi

Phạm vi xét lại từ vòng 2 trở đi chỉ gồm 4 việc:

1. **Bảng trạng thái các câu vòng trước.** Mỗi mã có kết quả: ✅ đã xử lý · ◐ xử lý một nửa · ❌ chưa · ⚠️ xử lý nhưng sinh vấn đề. Cột **Text doc** và **Mock** tách riêng, kèm cột **Figma**.
2. **Phần doc thay đổi:** đọc từng thay đổi và đối chiếu với các mục còn lại của doc. Lỗi hay gặp nhất là PM viết quy tắc mới ở một mục nhưng **quên sửa các câu cũ** ở mục khác và ở AC. Khi gặp, viết sẵn câu AC đã sửa.
3. **Hệ quả của chính các quyết định mới:** quyết định vừa chốt có tạo case mới không? Chạy lại checklist **chỉ cho phần bị quyết định đó chạm tới**.
4. **Quét hồi quy:** những chỗ đã sửa ở vòng trước có bị quay lại bản cũ không (tên, thứ tự, nhãn).

**Case mới không phát sinh từ 4 việc trên** thì vẫn ghi ra, nhưng bắt buộc:
- gắn "Bỏ sót từ vòng N";
- xét kỹ nhãn: nếu không chặn design thì đưa vào danh sách cho dev/PM, **không giữ design lại vì nó**.

Trước khi xuất file, so với review vòng trước: không được có câu nào **ngược** với kết luận của vòng trước mà không giải thích lý do.

---

## Bước 4 — Phân loại

Mọi điểm tìm được đều rơi vào đúng một khối:

| Khối | Nội dung | Ai xử lý |
|---|---|---|
| **Câu hỏi cho PM** | Rule nghiệp vụ, dữ liệu, tiền, quyền, mục tiêu | PM |
| **Doc cần sửa** | Mâu thuẫn câu chữ, câu cũ sót, đánh số, copy chưa ghi vào doc. Không cần quyết định mới | PM sửa, review viết sẵn câu mới |
| **Design đề xuất** | Thuộc chuyên môn design: pattern, layout, state, copy UI | Hỏi người dùng xác nhận, rồi thông báo PM "design làm X" |
| **Ngoài phạm vi** | Kéo theo nhưng không thuộc lần này | Đề xuất tách |

Mỗi câu trong khối Câu hỏi và Design đề xuất phải có thêm **một trong hai nhãn**:
- **Chặn design:** câu trả lời làm đổi UI, đổi state hoặc thêm/bớt màn.
- **Không chặn design:** chỉ ảnh hưởng logic, backend, công thức hoặc câu chữ.

Cách phân định khi lưỡng lự: "Nếu PM trả lời khác đề xuất (a), mình có phải sửa frame nào không?" Có thì là chặn design.

**Không có câu hỏi "lọt" ra ngoài bảng.** Mọi chỗ cần PM trả lời phải nằm ở một trong hai dạng sau. Các dạng như "Cần chốt kèm…", "cần PM xác nhận", "Nếu chọn (b) thì…" cũng không ngoại lệ.
- **Câu hỏi có mã:** gồm nhãn chặn / không chặn design, phương án (a) đề xuất và cột ảnh hưởng.
- **Xác nhận dữ kiện:** câu có / không về một sự thật, ví dụ "App có bắt buộc đăng nhập không?". Vẫn có mã và nhãn, kèm câu "tôi đang giả định là …". Gom các câu này vào bảng **Cần PM xác nhận dữ kiện**.

Không viết câu hỏi lẫn trong đoạn văn. Câu không có mã sẽ rơi mất ở vòng sau, và PM sẽ không biết phải trả lời nó.

**Gom theo gốc.** Nhiều câu cùng xuất phát từ một chỗ doc chưa định nghĩa (ví dụ "một dòng nguyên liệu gộp được lưu thế nào") thì đặt **một câu gốc** và hỏi nó trước. Các câu con chỉ cần ghi "phụ thuộc <mã gốc>", không gửi PM riêng từng câu. Câu nhiều quá thường là dấu hiệu doc có vấn đề ở tầng cao hơn; nói thẳng điều đó.

**Mỗi câu phụ** cũng phải có mã riêng và dòng riêng trong bảng trạng thái.

---

## Bước 5 — Viết câu hỏi

Cấu trúc mỗi câu: **tình huống cụ thể (trích doc, ghi vị trí) → bảng phương án → cần chốt kèm (nếu có)**.

```markdown
### SET-12. Goal mới bằng goal hiện tại thì có hiện dialog không? *(mới · không chặn design)*

Mục 3 ghi "mỗi lần app tính lại → luôn hiện dialog". Ví dụ user đang ở mức sàn 1,200 kcal đổi Activity level: goal vẫn 1,200, nhưng dialog vẫn hỏi "Update to 1,200? / Keep 1,200".

| | Phương án | Ảnh hưởng |
|---|---|---|
| **(a) — đề xuất** | Goal không đổi thì không hiện dialog, không toast | Bớt 1 thông báo vô nghĩa |
| (b) | Giữ như doc | — |
```

**Mã câu hỏi:**
- Dạng `<TIỀN TỐ>-<số>`. Số tăng dần qua mọi vòng và **không bao giờ dùng lại**.
- Mã giữ nguyên qua các vòng. Vòng phát hiện ghi trong ngoặc: *(mới)*, *(mang từ vòng 2)*, *(bỏ sót từ vòng 1)*.
- Nếu dự án đã có quy ước mã riêng thì theo quy ước đó, nhưng vẫn tránh dùng lại một chữ cái cho hai nghĩa khác nhau.

**Copy:** UI copy viết theo chuẩn thị trường (xem skill bối cảnh). Copy thuộc sở hữu PM (theo tham số dự án, thường là notification và marketing) thì **không viết nháp**, chỉ đề nghị PM đề xuất. Claim có số liệu hoặc chứng nhận thì hỏi nguồn.

---

## Bước 6 — File review

Tên file: `YYYY-MM-DD_spec-review-<tính-năng>-v<x.y.z>[-rN].md`, lưu ở nơi dự án quy định. `v<x.y.z>` là **version lấy đúng như tên section / page trong Figma**, không tự đặt v1/v2. Vòng review dùng hậu tố `-rN` (vòng 2 là `-r2`), không dùng `-vN` để khỏi nhầm với version. Review vòng trước chuyển vào `_archive/` khi có bản mới, trừ khi dự án muốn giữ tại chỗ. Nếu dự án yêu cầu, render file .html cùng tên. Trong dự án SoT (dựng bằng `sot-init`), render bằng `python3 _tools/md_to_html.py <file.md>` (Windows dùng `py` thay `python3`). Dự án chưa có `_tools/` thì dùng bản trong skill `sot-init` (`assets/project/_tools/md_to_html.py`), không vá tay file `.html`.

Dùng template trong `references/templates.md`. Khung chung:

1. **Phần đầu:** doc được review (link, phiên bản, ngày, message lần sửa cuối), link review vòng trước, nguồn đối chiếu, Figma.
2. **Tóm tắt:** kết luận "chốt được / chưa chốt được design", số đếm (ví dụ "7 câu vòng trước, đã xử lý 5"), **vấn đề đáng lo nhất**, và **số câu còn chặn design**, tách thành 2 con số: "<n> chờ PM" và "<m> đề xuất design chờ người dùng xác nhận". Mọi câu mang nhãn chặn design ở bất kỳ đâu trong file đều phải được đếm vào một trong hai con số này. Trước khi xuất file, đếm lại cho khớp.
3. **Trạng thái các câu vòng trước** (từ vòng 2).
4. **Câu hỏi cho PM:** nhóm chặn design trước, nhóm không chặn sau.
5. **Doc cần sửa:** kèm câu viết sẵn.
6. **Design đề xuất:** những gì design đã làm hoặc sẽ làm, PM chỉ cần biết.
7. **Ngoài phạm vi.**
8. **Figma:** đã sửa gì (bảng thay đổi → node), và sẽ sửa gì theo từng câu trả lời của PM.
9. **Tin gửi PM:** khối copy nguyên được, xưng hô theo tham số dự án. Tin này **ngắn hơn file review** để PM trả lời được ngay trong một lần:
   - **Tất cả** câu chặn design và câu gốc, đặt lên đầu.
   - Tối đa khoảng 5 câu không chặn design quan trọng nhất. Các câu còn lại chỉ ghi "<k> câu logic khác, không gấp, ở mục X của file".
   - Danh sách mã cần sửa câu chữ (không liệt kê nội dung).
   - Các câu xác nhận dữ kiện, dạng có / không.

Trước khi xuất, hỏi người dùng những điểm mình chưa chắc (AskUserQuestion), đặc biệt là cách hiểu mục tiêu tính năng ở vòng 1 và các đề xuất thuộc design.

---

## Bước 7 — Đồng bộ Figma

Mục tiêu là doc và Figma không mâu thuẫn ở bất kỳ thời điểm bàn giao nào.

- Câu còn mở → dựng theo phương án (a), gắn note ⚠️ ngay trên frame, ghi mã câu hỏi.
- Câu đã chốt → bỏ ⚠️, đổi note sang quy tắc đã chốt. Chỉ giữ note thật cần thiết.
- Text doc thay đổi (headline, option, copy) → sửa Figma theo **text**, không theo mock.
- Kiểm tra cả số liệu minh hoạ trong cùng một luồng: số giữa các màn phải khớp nhau, dù không phải expected value.
- Trước khi sửa bố cục mà người dùng đã tự sắp, hỏi họ trước.
- Ghi lại danh sách frame / node đã đổi vào file review và vào danh sách màn của tính năng.

---

## Bước 8 — Cập nhật hồ sơ tính năng

**Dự án SoT** (có `CLAUDE.md` chứa `<!-- FEATURES -->`, dựng bằng `sot-init`): khi PM trả lời hoặc design chốt, chuyển sang skill `sot-sync` để lan quyết định ra mọi file liên quan (brief, inventory, handoff, CLAUDE.md, sources, tính năng dùng chung dữ liệu). `sot-sync` có checklist chờ xác nhận nên không sót file. Nếu không có `sot-sync`, làm thủ công theo danh sách dưới.

Nếu dự án có các file sau, cập nhật cho khớp:
- **open-questions:** các câu còn mở, có mã và người trả lời.
- **decisions:**
  - chỉ ghi "Đã chốt" khi có người xác nhận;
  - không xoá dòng cũ, quyết định bị đảo thì ghi "thay thế #N";
  - quyết định của design ghi người chốt là designer.
- **Danh sách màn / inventory:** node mới, note ⚠️ còn lại.
- **CLAUDE.md của tính năng:** trạng thái một dòng và link review mới nhất.

Hết một đợt làm việc dài, hoặc khi người dùng sắp chuyển conversation, viết **file handoff** gồm: bối cảnh, nguồn, diễn biến các vòng, quyết định, việc còn mở, việc kế tiếp, và bẫy kỹ thuật đã gặp.

**Khi tính năng đã chốt hết và đã có doc chính thức trong `brief/`**, xoá toàn bộ file review của tính năng đó (`brief/` và `_archive/`, cả `.md` lẫn `.html`). Từ lúc đó review không còn ý nghĩa. Thứ tự làm:
1. Chuyển những gì còn sống sang doc chính thức, `decisions.md` hoặc `open-questions.md`: câu logic cho dev chưa trả lời, tin gửi PM đang gộp với tính năng khác.
2. File review dùng chung với một tính năng chưa chốt thì giữ lại, nói rõ với người dùng, và xoá khi tính năng kia chốt.
3. Sửa mọi link trỏ vào file sắp xoá, xoá file, rồi grep lại để chắc không còn link chết.
4. Ghi vào header doc chính thức rằng review đã xoá và doc này là nguồn duy nhất.

---

## Tiêu chí chốt design

Design của tính năng được chốt khi **không còn câu nào mang nhãn chặn design**.

**Ở vòng 2, mặc định là chốt.** Câu chặn design PM chưa trả lời thì dựng theo (a), gắn ⚠️. Câu mới phát sinh mà không chặn design thì chuyển sang danh sách cho dev. Chỉ không chốt khi câu trả lời của PM sinh thêm câu chặn design mới; khi đó nói rõ đó là câu nào và vì sao.

Khi chốt:

1. Viết **bản review cuối**: "Design đã chốt theo các đề xuất sau" + "Câu hỏi logic cho PM / dev (không mở lại vòng design)".
2. Câu không chặn design chuyển sang open-questions cho dev / PM.
3. Nếu còn 1–2 câu chặn design mà PM chậm trả lời: đề nghị người dùng dựng theo (a), gắn ⚠️, rồi chốt. Nếu PM chọn khác thì chỉ sửa các frame liên quan.

Mỗi vòng, nói rõ cho người dùng biết còn bao nhiêu câu chặn design, để họ biết còn cách chốt bao xa.

---

## Trả lời trong chat

Không lặp lại cả file. Chỉ nói:
- doc đã ổn chưa: số câu đã xử lý, số câu còn chặn design;
- vấn đề đáng lo nhất;
- Figma đã sửa gì và còn chờ gì;
- link các file đã tạo hoặc sửa.

Nếu có case bị sót từ vòng trước, nói thẳng là sót, đừng trình bày như case mới.

---

## Tài liệu kèm theo

- `references/checklist.md`: checklist edge case đầy đủ, kèm ví dụ thật các case từng bị sót. **Đọc ở vòng 1**, và đọc phần liên quan ở vòng N.
- `references/templates.md`: template file review vòng 1, vòng N, bản cuối, tin gửi PM, file handoff.
- `references/platform-ios.md`: những điểm riêng của iOS (permission, notification) thường bị doc viết sai. Đọc khi tính năng chạm tới quyền, notification hoặc nền tảng.
