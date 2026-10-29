# Template

Các template dưới đây dùng tiếng Việt cho phần review, tiếng Anh cho UI copy. Bỏ khối nào không có nội dung, đừng để khối trống.

## Mục lục
1. File review vòng 1
2. File review vòng N
3. Bản review cuối (chốt design)
4. Tin gửi PM
5. File handoff

---

## 1. File review vòng 1

```markdown
# Spec Review — <Tính năng>

**Doc được review:** [<tên doc>](<link>), bản <x>, <ngày> (lần sửa cuối: "<message>").
**Đối chiếu với:** <bản đã ship / Onboarding / tính năng dùng chung>.
**Figma:** <file / page / section>, hoặc "chưa dựng".

---

## Tóm tắt

- **Kết luận:** chưa chốt được design. Còn **<n> câu chặn design**, <m> câu không chặn.
- **Vấn đề đáng lo nhất:** <một câu>.
- <1–3 gạch đầu dòng khác nếu thật cần>.

## 1. Mục tiêu tính năng (theo cách tôi hiểu)
<1–3 câu. Hỏi người dùng xác nhận trước khi xuất file.>

## 2. Câu hỏi cho PM

### Chặn design

### <TT>-1. <Câu hỏi đóng> *(chặn design)*
<Tình huống, trích doc kèm vị trí. Tách "Doc ghi" với "Tôi suy ra (cần xác nhận)" nếu có.>

| | Phương án | Ảnh hưởng |
|---|---|---|
| **(a) — đề xuất** | … | … |
| (b) | … | … |

**Cần chốt kèm:** … *(nếu có; câu phụ cũng có mã riêng: <TT>-2)*

### Không chặn design
…

### Cần PM xác nhận dữ kiện

| Mã | Câu hỏi có / không | Tôi đang giả định | Chặn design? |
|---|---|---|---|

## 3. Doc cần sửa (không cần quyết định mới)

| Mã | Chỗ | Doc đang ghi | Đề xuất câu mới |
|---|---|---|---|

## 4. Design đề xuất
<Chỉ ghi những gì người dùng đã xác nhận.>

PM cân nhắc cập nhật doc cho khớp các thay đổi design dưới đây, để doc và Figma không lệch nhau (design đã sửa mà doc không ghi, hoặc ghi thiếu). Câu viết sẵn ở cột cuối.

| Mã | Design làm | Lý do | Doc cần cập nhật (chỗ · câu viết sẵn) |
|---|---|---|---|
| <TT>-20 | … | … | 2.2.7 Thành phần · "…" / Không cần |

## 5. Ngoài phạm vi

## 6. Figma
- Đã dựng / đã sửa: | Thay đổi | Frame / node |
- Chờ PM: | Nếu PM chọn | Sửa gì |

## 7. Tin gửi PM
> Copy nguyên khối
<xem mục 4 của file này>
```

---

## 2. File review vòng N

Giống vòng 1, thêm và đổi các phần sau:

```markdown
**Review vòng trước:** [<file>](<link>). Mã <…> giữ nguyên.

## Tóm tắt
- **Vòng <N−1> có <k> câu, doc mới xử lý <j>.** Còn mở: <mã>.
- **Còn <n> câu chặn design.**
- <Thay đổi mới đáng chú ý trong doc.>
- <Nếu có> **<s> case bỏ sót từ vòng trước**, trong đó <t> chặn design.

## 1. Trạng thái các câu vòng trước

| Mã | Nội dung | Text doc | Mock | Figma |
|---|---|---|---|---|
| SET-3 | … | ✅ / ◐ / ❌ / ⚠️ + một câu | … | … |

## 2. Thay đổi mới trong doc

| # | Doc ghi | Hệ quả / Figma |
|---|---|---|

## 3. Doc còn tự mâu thuẫn (chỉ cần sửa câu)
<Trích quy tắc mới và các câu cũ sót, cạnh nhau. Viết sẵn câu AC đã sửa.>

## 4. Câu hỏi cho PM
<Case mới ghi nguồn gốc: *(mới — do quyết định <mã>)* hoặc *(bỏ sót từ vòng <x>)*.>
```

---

## 3. Bản review cuối (chốt design)

```markdown
# Spec Review — <Tính năng> — Bản cuối

**Kết luận: design đã chốt** ngày <ngày>. Không còn câu chặn design.

## 1. Design đã chốt theo các quyết định và đề xuất sau
| Mã | Quyết định | Nguồn (PM chốt / design đề xuất, PM chưa phản đối) | Frame |

## 2. Câu hỏi logic cho PM / dev (không mở lại vòng design)
| Mã | Câu hỏi | Đề xuất | Người trả lời |

## 3. Doc cần sửa câu chữ
<Gồm cả các Design đề xuất mà doc chưa ghi hoặc ghi thiếu.>
| Mã | Chỗ | Câu mới |

## 4. Figma
<Section, số frame, các note ⚠️ còn lại và vì sao còn.>
```

---

## 4. Tin gửi PM

Ngắn, copy nguyên được, xưng hô theo tham số dự án. Tách câu chặn design để PM trả lời trước.

```markdown
> Copy nguyên khối

Chào <cách gọi theo tham số dự án>, em đã xem doc <tên> bản <x>.

**Cần anh/chị chốt trước (ảnh hưởng UI):**
- <TT>-5: <câu hỏi một dòng>. Em đề xuất (a) <một dòng>.

**Không gấp (logic, không ảnh hưởng UI):**
- <TT>-7: … *(tối đa khoảng 5 câu quan trọng nhất)*
- Còn <k> câu logic khác, không gấp, ở mục <X> của file.

**Xác nhận giúp em (có / không):**
- <TT>-12: <câu hỏi>? Em đang giả định là <…>.

**Doc cần sửa câu:** <TT>-8, <TT>-9 (câu mới em ghi sẵn trong file review).

**Design đề xuất:** <TT>-20, <TT>-21 — <một dòng tóm tắt>. Nhờ anh/chị cân nhắc cập nhật doc cho khớp (câu viết sẵn ở mục <X> của file), để doc và Figma không lệch nhau.

Anh/chị chỉ cần trả lời theo mã + chữ cái, ví dụ "5a, 7b". File review: <link>.
```

---

## 5. File handoff

Viết khi kết thúc một đợt dài hoặc trước khi chuyển conversation.

```markdown
# Handoff — <Tính năng>

## 1. Bối cảnh
<Dự án, tính năng, PM, người dùng, nền.>

## 2. Nguồn
| Thứ | Ở đâu |  (doc, kịch bản, Figma, cách đọc doc)

## 3. Diễn biến các vòng
| Vòng | Ngày | Kết quả chính |

## 4. Quyết định đã chốt
### Do người dùng chọn
### Theo doc PM

## 5. Còn mở
| Mã | Nội dung | Đề xuất | Chặn design? |

**Việc kế tiếp:** …

## 6. Figma — trạng thái hiện tại
<Section, nhóm luồng, component mới, quy ước trình bày, bẫy kỹ thuật đã gặp.>

## 7. File trong repo

## 8. Lưu ý khi làm tiếp
```
