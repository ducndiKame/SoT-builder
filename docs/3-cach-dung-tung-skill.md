# Cách dùng từng skill

Không cần gõ tên skill. Claude tự chọn skill phù hợp theo câu bạn nhắn. Muốn chắc chắn thì gõ `/` cộng tên skill, ví dụ `/sot-sync`. Nếu cài theo dạng plugin thì gõ `/sot-builder:sot-sync`.

Mọi skill tuân theo 3 luật chung:
- **Không tự chốt thay bạn.** Phần suy ra được viết dạng câu hỏi. Chỉ ghi **Đã chốt** khi có người xác nhận.
- **Hỏi trước khi làm việc khó hoàn tác hoặc ra bên ngoài:** sửa nhiều file, sửa Figma, tạo repo, push, mời người.
- **Ghi nguồn cho mọi ý**, để người sau kiểm tra lại được.

---

## sot-init: dựng SoT cho dự án

| | |
|---|---|
| **Dùng khi** | Bắt đầu dự án mới; hoặc dự án đang chạy mà tài liệu rải rác, chưa có SoT |
| **Câu mẫu** | "Dựng SoT cho dự án Meditation App, Figma <link>, doc PM <link>" · "Gom nguồn dự án này lại" · "Đưa SoT lên GitHub" |
| **Đầu vào** | Tên dự án, link Figma, doc PM, ai chốt được gì, tệp user |
| **Đầu ra** | `README.md`, `CLAUDE.md`, `sources.md`, `decisions.md`, `context/`, `design-system/README.md`, `features/README.md`, `_tools/`; commit nền + private repo (khi bạn đồng ý) |
| **Lưu ý** | Không tạo folder rỗng. Không di chuyển file cũ khi chưa hỏi. Mâu thuẫn giữa các nguồn được ghi vào bảng chờ chốt, không âm thầm chọn một phía |
| **Dùng tiếp** | `sot-feature` cho một tính năng mẫu |

## sot-feature: làm trọn một tính năng

| | |
|---|---|
| **Dùng khi** | Thêm một tính năng vào SoT; kiểm kê màn của một section Figma; chuẩn bị handoff dev |
| **Câu mẫu** | "Làm tính năng water-tracker vào SoT, section Figma Water V1.0.0, doc <link>" · "Map frame của section Settings V1.0.1 với AC" · "Làm handoff dev cho reminders v1.0.1" |
| **Đầu vào** | Tên tính năng, version theo Figma, section Figma, doc PM |
| **Đầu ra** | `features/<tên>/`, gồm `CLAUDE.md`, `decisions.md`, `open-questions.md`, `brief/…-v<x.y.z>.md`, `design/screen-inventory.md` (frame ↔ AC ↔ quyết định), `design/<tên>-flow.mmd`, `copy/ui-copy.md`. Tới bước bàn giao thì thêm `handoff/handoff-v<x.y.z>.md` |
| **Lưu ý** | Version trong tên file lấy đúng như Figma (section, nếu không có thì theo page). Ngày trong tên brief là ngày của bản doc. Đọc text trong frame, không tin tên frame. Frame chưa có AC thì ghi "Chưa có AC riêng". Handoff chỉ làm khi bạn yêu cầu, không làm trong lần dựng đầu |
| **Gọi kèm** | `figma-design-rename`, `spec-review`, `document-fullstack-v2`, `flowchart`, `design-system-build` |

## sot-sync: đồng bộ sau mỗi quyết định

| | |
|---|---|
| **Dùng khi** | PM trả lời câu hỏi; bạn chốt một điều; doc có bản mới; đổi version / tên file; tính năng chốt xong |
| **Câu mẫu** | "PM chốt SET-12 theo (a)" · "Đã chốt goal nước 2,500 ml, bỏ 2,000" · "Doc Settings có bản 5 rồi" · "Tính năng reminders chốt xong, dọn review" |
| **Đầu vào** | Thay đổi là gì, ai chốt, ngày nào, thay thế điều gì cũ |
| **Đầu ra** | Checklist **File → Sửa gì → Vì sao** để bạn xác nhận; sau đó sửa đồng loạt, chuyển bản cũ vào `_archive/`, sửa link, sinh lại HTML, commit |
| **Lưu ý** | Brief mới nhất thắng file phụ trợ. `decisions.md` chỉ thêm dòng, không xoá. Đảo quyết định thì ghi "thay thế #N" |
| **Đây là skill dùng nhiều nhất** | Mỗi quyết định thường chạm 4–6 file. Skill này để không sót file nào |

## sot-audit: kiểm tra SoT

| | |
|---|---|
| **Dùng khi** | Sau khi làm xong tính năng mẫu; trước khi bàn giao; định kỳ; khi nghi SoT bị lệch |
| **Câu mẫu** | "Audit SoT" · "SoT đã đủ để bàn giao chưa?" · "Chạy thử một task với SoT xem AI có dùng đúng nguồn không" |
| **Đầu ra** | `audits/YYYY-MM-DD_sot-audit.md` (+ `.html`), gồm: điểm DoD x/6, 3 vấn đề đáng sửa nhất, bảng mâu thuẫn, kết quả chạy thử task, danh sách đề xuất sửa |
| **Lưu ý** | Chỉ kiểm tra, không tự sửa. Sửa thì nhắn "sửa theo báo cáo audit", việc đó đi qua `sot-sync` |
| **Chạy riêng script** | `python3 ~/.claude/skills/sot-audit/scripts/audit_sot.py "<thư mục dự án>"` |

## sot-handoff: bàn giao và tiếp nhận

| | |
|---|---|
| **Dùng khi** | Chuyển dự án cho designer khác, nghỉ dài ngày, onboard người mới |
| **Câu mẫu (giao)** | "Bàn giao SoT cho Lan, GitHub lan-design" |
| **Câu mẫu (nhận)** | "Nhận bàn giao SoT từ repo ducndiKame/FitAgain-SoT" |
| **Đầu ra** | Giao: `BAN-GIAO.md`, README / trạng thái đã cập nhật, commit bàn giao, tin nhắn soạn sẵn cho người nhận. Nhận: repo đã clone, danh sách quyền còn thiếu, pull request đầu tiên |
| **Lưu ý** | Không dùng cho bàn giao design → dev. Việc đó là file `handoff-v<x.y.z>.md` của `sot-feature` |

---

## Skill hỗ trợ

| Skill | Dùng khi | Câu mẫu | Ghi chú trong SoT |
|---|---|---|---|
| **spec-review** | Có doc PM cần đọc, phản biện, đối chiếu với Figma | "Review doc Settings <link>" · "PM vừa sửa doc, xem lại" | File `brief/YYYY-MM-DD_spec-review-<tn>-v<x.y.z>[-rN].md`. Tham số dự án (cách đọc doc, xưng hô với PM) nằm trong `CLAUDE.md`, mục "Spec review". Chốt xong thì chuyển sang `sot-sync` |
| **design-system-build** | Cần tài liệu design system từ Figma | "Dựng design system tối thiểu cho tính năng water" · "Audit design system đầy đủ" | **Tối thiểu**: ghi vào `design-system/README.md`. **Đầy đủ**: ghi vào `design-system/DesignSystem.md` |
| **figma-design-rename** | Tên trong Figma lộn xộn | "Đặt tên lại section Water theo chuẩn" | Nên chạy trước khi kiểm kê màn, để `screen-inventory` dùng tên đúng |
| **flowchart** | Cần sơ đồ luồng | "Vẽ flowchart tính năng water" | Lưu ở `design/<tn>-flow.mmd`, chèn vào đầu brief |
| **document-fullstack-v2** | Cần viết AC Gherkin, dò edge case | "Viết AC cho tính năng reminders" | Lưu ở `brief/`, AC chưa duyệt thì ghi "chờ PM xác nhận" |

## Script dùng chung trong mỗi dự án SoT

`sot-init` chép sẵn vào `_tools/` của dự án:

| Script | Dùng để |
|---|---|
| `python3 _tools/md_to_html.py <file.md> …` | Sinh bản `.html` (có mục lục, sáng/tối, vẽ Mermaid) cho file `.md` |
| `python3 _tools/md_to_html.py --all features/` | Sinh lại toàn bộ, bỏ qua `_archive/` |
| `python3 _tools/mmd_to_html.py <flow.mmd>` | Sinh `.html` cho flowchart |

Windows dùng `py` thay cho `python3`. Không sửa tay file `.html`: sửa file `.md` rồi chạy lại script.

Dự án dựng trước khi có bộ skill này (chưa có `_tools/`): các skill tự dùng bản dự phòng trong skill `sot-init` và sẽ đề nghị chép `_tools/` vào dự án. Muốn chép ngay thì nhắn "chép _tools của sot-init vào dự án này".
