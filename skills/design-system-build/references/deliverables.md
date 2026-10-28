# Ba dạng đầu ra

Mỗi dạng làm một việc khác nhau. Đừng dựng cả ba mặc định — hỏi người dùng cần gì, rồi nói rõ dạng nào hợp.

| Dạng | Việc của nó | Ai đọc |
|---|---|---|
| **Markdown** | Bản audit đầy đủ nhất, là nguồn để sinh ra hai dạng kia | Người dùng, AI tool, git |
| **Design System artifact** | Component render sống, bảng token có engine đổi theme | Dev tra cứu, designer duyệt |
| **Trang HTML** | Tài liệu đọc, chia sẻ được, có thể song ngữ | PM, stakeholder, team ngoài |

---

## 1. Markdown — luôn làm trước

Một file trong repo. Đây là bản đầy đủ nhất và là nguồn để sinh ra hai dạng kia.

Ưu điểm: diff được qua git, AI đọc trực tiếp, không cần mạng.

Theo dàn ý ở `document-outline.md`.

---

## 2. Design System artifact

Nếu tài khoản có Artifact type **Design System**, dùng nó thay vì dựng trang HTML thuần. Gọi `Artifact` với `action: "quickstart"`, `intent: "other"` để thấy danh sách type.

Nó cho miễn phí: mục lục, engine đổi Light/Dark ngay trên trang, và component render **sống** thay vì ảnh chụp.

**Cấu trúc nội dung** (đọc `SKILL.md` của type để biết chính xác):

```
project/design-system.json          index — viết SAU CÙNG
project/tokens.json                 toàn bộ token
project/README.md                   brand book
project/20-*.md, 30-*.md …          các mục phụ, sắp theo thứ tự path
project/components/bundle.js        một classic script gán window.<Namespace>
project/components/bundle.css       style dùng var(--token)
project/components/index.d.ts       types làm tài liệu
project/components/<Comp>/preview.html   + README.md
project/components/Cover/preview.html    cover, viết cuối cùng, thư mục để TRỐNG
```

**Những chỗ dễ vấp:**

- `tokens.json` phải là **danh sách** `{"tokens":[{name,value,usage}]}`, không phải map kiểu DTCG. Map là JSON hợp lệ nhưng trang không đọc được và sẽ hiện rỗng.
- Tên token không được chứa `/`. Đổi `text/primary` thành `text-primary` và ghi chú mapping trong `meta`.
- Dùng **alias** `"{primary-600}"` cho semantic token — nó phản ánh đúng kiến trúc thật và hiển thị được chuỗi tham chiếu.
- `letterSpacing` dùng `em`, không dùng `%`.
- Font Google: để `type.fonts` rỗng, khai báo trong `type.families`, và thêm thẻ `<link>` Google Fonts trong **từng** preview.
- Mỗi `preview.html` bắt đầu bằng dòng marker `<!-- @dsCard group="…" height=N -->`.
- File `.ts` cần `contentType: "text/plain"` khi publish.
- Publish **một call** với tất cả file; index đi trong call cuối.

---

## 3. Trang HTML

Khi người dùng muốn một trang đọc được, gửi được, hoặc **song ngữ**.

Lưu ý: trang của Artifact type là cố định — không thêm được nút vào khung trang. Cần toggle ngôn ngữ thì phải dựng trang riêng.

### Toggle ngôn ngữ

Cách gọn và bền nhất: đánh dấu mọi node dịch được bằng `data-lang`, bật tắt bằng thuộc tính `hidden`.

```html
<p data-lang="vi">Nền màn hình là xám.</p>
<p data-lang="en" hidden>The screen ground is grey.</p>
```

```js
function setLang(lang) {
  document.querySelectorAll('[data-lang]').forEach(function (n) {
    n.hidden = n.getAttribute('data-lang') !== lang;
  });
  document.documentElement.lang = lang;
  try { localStorage.setItem('lang', lang); } catch (e) {}
}
```

Vì sao dùng `hidden` chứ không phải class CSS: `hidden` giữ nguyên display type gốc, nên span vẫn inline và div vẫn block. Class `display:block` sẽ làm vỡ span nằm trong bảng.

Đặt sẵn `hidden` trong markup cho ngôn ngữ phụ để trang đúng ngay cả trước khi JS chạy.

### Bảng song ngữ

Với bảng dài, đừng nhân đôi markup. Đưa dữ liệu vào một mảng JS rồi render, với helper:

```js
var bi = function (vi, en) {
  return '<span data-lang="vi">' + esc(vi) + '</span>' +
         '<span data-lang="en" hidden>' + esc(en) + '</span>';
};
```

Cột số (hex, px, tỉ lệ contrast) không cần dịch — chỉ dịch header và cột ghi chú.

### Cái gì KHÔNG dịch

**Block prompt cho AI giữ nguyên tiếng Anh ở mọi chế độ.** Token và UI copy đều tiếng Anh; dịch ra là làm hỏng chính thứ nó dùng để ràng buộc model. Nói rõ điều này trên trang.

Tên token, tên component, tên màn hình cũng giữ nguyên.

### Ngôn ngữ mặc định

Chọn theo người mở trang đầu tiên, và nhớ lựa chọn trong `localStorage`. Nói cho người dùng biết bạn đã chọn mặc định nào để họ đổi nếu muốn.

---

## Chia sẻ

Artifact mặc định **riêng tư**. Người khác không mở được link cho tới khi chủ sở hữu share từ menu Share trên trang. Luôn nhắc điều này khi đưa link cho người dùng, nếu trang có ý định để người khác đọc.
