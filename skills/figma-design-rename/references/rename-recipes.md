# Rename recipes — script sẵn dùng và bẫy đã biết

Mọi script chạy qua `mcp__figma__use_figma`. Trước lần gọi đầu **phải nạp skill `figma-use`** (hoặc đọc resource `skill://figma/figma-use/SKILL.md`) — bỏ qua gây loạt lỗi khó debug. Luôn truyền `skillNames: "figma-use"` (hoặc `"resource:figma-use"` nếu nạp qua resource).

Mục lục: [A. Cấu trúc](#a) · [B. Đếm](#b) · [C. Đọc nội dung](#c) · [D. Ghi rename](#d) · [E. Ba pass layer](#e) · [F. Verify](#f) · [G. File thứ hai](#g) · [Bẫy](#bay)

---

<a id="a"></a>
## A. Cấu trúc — page, section, screen, node rời

Rẻ, chạy đầu tiên. **Đừng dùng `get_metadata` cho cả page** — file thật vượt token limit.

```js
const pages = figma.root.children.map((p) => p.id + '  ' + p.name);

const design = await figma.getNodeByIdAsync('DESIGN_PAGE_ID');
await figma.setCurrentPageAsync(design);

const sections = [], loose = [];
for (const c of design.children) {
  if (c.name.indexOf('\u{1F6E0}') === 0) continue;          // bỏ flow connector 🛠
  if (c.type === 'SECTION') {
    const kids = c.children.filter((k) =>
      (k.type === 'FRAME' || k.type === 'COMPONENT') && k.name.indexOf('\u{1F6E0}') !== 0);
    sections.push({ id: c.id, nm: c.name, n: kids.length,
                    kids: kids.map((k) => k.id + '  ' + k.name) });
  } else {
    loose.push(c.id + '  ' + c.type + '  ' + c.name);
  }
}
return { pages, pageName: design.name, sections, loose };
```

**`loose` là phần dễ bỏ sót nhất.** Component set, ảnh reference, text rơi vãi thường nằm trần ngoài mọi section. Trong một file thật từng có 18 node như vậy, gồm toàn bộ component library.

<a id="b"></a>
## B. Đếm node và tên trùng — chạy trước khi hứa phạm vi

```js
const page = await figma.getNodeByIdAsync('DESIGN_PAGE_ID');
await figma.setCurrentPageAsync(page);

const all = page.findAll(function () { return true; });
const byType = {}, byName = {};
for (const n of all) {
  byType[n.type] = (byType[n.type] || 0) + 1;
  byName[n.name] = (byName[n.name] || 0) + 1;
}
const junk = /^(Frame|Group|Rectangle|Ellipse|Vector|Line|Layer|Component|Union|Subtract|Star|Polygon|Slice|Image|image)(\s+\d+)?$/;

return {
  total: all.length,
  byType,
  defaultNamed: all.filter((n) => junk.test(n.name)).length,
  vectorPaths: all.filter((n) => n.name === 'Vector').length,   // KHÔNG cần đổi
  topDuplicates: Object.keys(byName).sort((a, b) => byName[b] - byName[a])
    .slice(0, 25).map((k) => byName[k] + '×  ' + k)
};
```

**Cách đọc:** một tên text layer lặp hơn 500 lần nghĩa là Figma đã đóng băng tên từ nội dung cũ — pass §E-1 sẽ gỡ sạch. Số `Vector` cao là bình thường, trừ ra khỏi mọi con số báo cáo.

<a id="c"></a>
## C. Đọc nội dung text từng màn — bước quyết định độ chính xác

Rẻ hơn và chính xác hơn chụp ảnh. Trả về 6–8 chuỗi đầu theo thứ tự thị giác.

```js
function texts(node, limit) {
  let found = [];
  try { found = node.findAllWithCriteria({ types: ['TEXT'] }); } catch (e) { return []; }
  found = found.filter((t) => t.visible !== false);
  found.sort((a, b) => {
    const ay = a.absoluteBoundingBox ? a.absoluteBoundingBox.y : 0;
    const by = b.absoluteBoundingBox ? b.absoluteBoundingBox.y : 0;
    if (ay !== by) return ay - by;
    return (a.absoluteBoundingBox ? a.absoluteBoundingBox.x : 0)
         - (b.absoluteBoundingBox ? b.absoluteBoundingBox.x : 0);
  });
  const out = [];
  for (const t of found) {
    let c = '';
    try { c = (t.characters || '').trim().replace(/\s+/g, ' '); } catch (e) { continue; }
    if (!c || c.length < 2) continue;
    if (/^\d{1,2}:\d{2}$/.test(c)) continue;            // đồng hồ status bar
    if (out.indexOf(c) !== -1) continue;
    out.push(c.length > 24 ? c.slice(0, 24) : c);
    if (out.length >= limit) break;
  }
  return out;
}

const sec = await figma.getNodeByIdAsync('SECTION_ID');
const kids = sec.children.filter((k) =>
  (k.type === 'FRAME' || k.type === 'COMPONENT') && k.name.indexOf('\u{1F6E0}') !== 0);
return kids.map((k) => ({
  id: k.id, nm: k.name,
  w: Math.round(k.width), h: Math.round(k.height),
  t: texts(k, 7)
}));
```

**Chia theo section.** Cả page một lượt sẽ vượt 20KB và bị cắt giữa chừng. Section > 40 màn thì `slice()` làm hai lần.

`h` quan trọng: cùng nội dung nhưng khác chiều cao thường là `(Full Scroll)` — frame cao hơn viewport 812.

<a id="d"></a>
## D. Ghi rename theo map

Khuôn dùng lại cho mọi tầng. Chia batch 40–70 rename mỗi call.

```js
const design = await figma.getNodeByIdAsync('DESIGN_PAGE_ID');
await figma.setCurrentPageAsync(design);

const map = {
  '132:1215': 'Plan / Home / Dashboard — Default',
  '498:6011': 'Plan / Home / Dashboard — Loading',
  // ...
};

const ok = [], failed = [];
for (const id of Object.keys(map)) {
  const n = await figma.getNodeByIdAsync(id);
  if (!n) { failed.push({ id, to: map[id] }); continue; }
  ok.push({ id, from: n.name, to: map[id] });
  n.name = map[id];
}
return { renamed: ok.length, failed, applied: ok, mutatedNodeIds: ok.map((x) => x.id) };
```

Luôn trả `from` — nó là bản ghi để báo cáo, và là cách phát hiện map đã lệch khỏi file.

### Đổi tên + sắp lại thứ tự page

Page sort theo thứ tự kéo thả, nên đánh số xong **phải kéo cho khớp**:

```js
const order = ['0:1', '25:6', '19:2', '57:256', '57:255'];
for (const id of order) {
  const p = await figma.getNodeByIdAsync(id);
  p.name = pageMap[id];
}
for (let i = 0; i < order.length; i++) {
  const p = await figma.getNodeByIdAsync(order[i]);
  if (p) figma.root.insertChild(i, p);
}
```

<a id="e"></a>
## E. Ba pass layer — đều idempotent, chạy lại được

Helper dùng chung. **Bỏ qua node nằm trong instance** ở cả ba pass:

```js
function inInstance(n) {
  let p = n.parent;
  while (p) {
    if (p.type === 'INSTANCE') return true;
    if (p.type === 'PAGE') return false;
    p = p.parent;
  }
  return false;
}
function slug(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}
```

### E-1. Text layer lấy nội dung của chính nó

```js
let renamed = 0, unchanged = 0, skipped = 0;
for (const t of page.findAllWithCriteria({ types: ['TEXT'] })) {
  if (inInstance(t)) { skipped++; continue; }
  let c = '';
  try { c = (t.characters || '').trim().replace(/\s+/g, ' '); } catch (e) { continue; }
  if (!c || !/[a-zA-Z0-9]/.test(c)) { skipped++; continue; }   // bỏ layer chỉ có glyph
  const target = c.length > 40 ? c.slice(0, 40) : c;
  if (t.name === target) { unchanged++; continue; }
  try { t.name = target; renamed++; } catch (e) {}
}
```

### E-2. Instance lấy tên từ component gốc — deterministic

Không đoán theo hình học. Đọc thẳng `mainComponent`.

```js
const setRole = {
  'Nav / Tab Bar': 'Tab Bar',
  'Nav / Header': 'Header',
  'Core / Avatar': 'Avatar',
  'Core / Input': 'Input',
  'Overlay / Scrim': 'Scrim',
  'Layout / Card / Workout': 'Workout Card',
  'Pattern / Profile Header': 'Profile Header'
  // một dòng cho mỗi component set của project
};

for (const inst of page.findAllWithCriteria({ types: ['INSTANCE'] })) {
  if (inInstance(inst)) continue;
  let main = null;
  try { main = await inst.getMainComponentAsync(); } catch (e) { continue; }
  if (!main) continue;
  const set = main.parent && main.parent.type === 'COMPONENT_SET' ? main.parent.name : null;
  const variant = main.name.indexOf('=') !== -1 ? main.name.split('=')[1] : main.name;

  let target = null;
  if (set === 'Core / Icon / Fill')      target = 'ic_' + slug(variant) + '_fill';
  else if (set === 'Core / Icon / Line') target = 'ic_' + slug(variant) + '_line';
  else if (set && setRole[set])          target = setRole[set];
  else if (setRole[main.name])           target = setRole[main.name];

  if (!target || inst.name === target) continue;
  try { inst.name = target; } catch (e) {}
}
```

**Đọc kỹ `samples` trả về trước khi chạy tiếp.** Ở một file thật, mẫu cho thấy bộ tên `Fill icon`/`Line icon` chứa cả `uncheck`, `right`, `trash` — nghĩa là nó là **bộ icon chung**, không phải icon tab bar. Đặt nhầm rồi phải sửa 1.062 instance. Một lần liếc mẫu tiết kiệm cả lượt.

### E-3. Layer cấu trúc

```js
for (const n of page.findAll(function () { return true; })) {
  if (inInstance(n)) continue;
  try {
    if (n.name === 'HomeIndicator' || n.name === 'Home indicator') {
      n.name = 'Home Indicator'; continue;
    }
    if (/^[a-z0-9-]+:[a-z0-9-]+$/.test(n.name)) {        // mingcute:right-line
      n.name = 'ic_' + slug(n.name.split(':')[1]); continue;
    }
    if ((n.type === 'FRAME' || n.type === 'GROUP') &&
        n.parent && n.parent.type === 'FRAME' && n.parent.width >= 340 &&
        Math.abs(n.y) <= 2 && n.height >= 38 && n.height <= 54 && n.width >= 340 &&
        n.name !== 'Status Bar') {
      n.name = 'Status Bar'; continue;
    }
  } catch (e) {}
}
```

**Đừng đoán Tab Bar theo hình học.** Frame cao 1272 hay 1711 thì tab bar không nằm ở đáy frame. Bắt nó qua `mainComponent` ở E-2.

<a id="f"></a>
## F. Verify — chạy đến khi `problems: []`

```js
const sections = [], problems = [], nameCount = {};
let totalScreens = 0, totalOk = 0;

for (const s of page.children) {
  if (s.type !== 'SECTION') continue;
  const kids = s.children.filter((k) =>
    (k.type === 'FRAME' || k.type === 'COMPONENT') && k.name.indexOf('\u{1F6E0}') !== 0);
  let ok = 0;
  for (const k of kids) {
    nameCount[k.name] = (nameCount[k.name] || 0) + 1;
    const isRef    = /^\[/.test(k.name);
    const hasState = / — /.test(k.name);
    const levels   = k.name.split(' / ').length;
    if (!isRef && (!hasState || levels !== 3)) problems.push(s.name + '  ::  ' + k.id + '  ' + k.name);
    if (hasState || isRef) ok++;
  }
  totalScreens += kids.length; totalOk += ok;
  sections.push(s.name + '  ' + ok + '/' + kids.length);
}

const dupes = Object.keys(nameCount)
  .filter((n) => nameCount[n] > 1 && n.indexOf('[') !== 0)     // [Ref]/[Note] trùng là hợp lệ
  .map((n) => nameCount[n] + '×  ' + n);

return { sections: sections.sort(), totalScreens, totalOk, problems, duplicateScreenNames: dupes };
```

Ba lỗi pass này bắt được mà mắt không thấy: tên chỉ có **một dấu cách trắng**, path **5 cấp**, và hậu tố `(Variant 9)` nhân bản sang frame mới.

<a id="g"></a>
## G. Áp map sang file thứ hai

Figma **giữ nguyên node ID khi duplicate file**, nên map dùng lại được. Nhưng phải verify, đừng giả định.

Chạy §A trên file đích, rồi đối chiếu từng cặp `id + tên hiện tại` với file nguồn. Điều kiện để chạy:

1. Mọi id trong map đều tồn tại.
2. Tên hiện tại khớp tên **cũ** ở file nguồn — nghĩa là chưa ai rename.
3. Số section và số frame mỗi section khớp.

Lệch bất kỳ điểm nào thì dừng, báo lệch ở đâu, hỏi trước khi đi tiếp.

File đích thường có thêm node mà file nguồn không có. Xử lý luôn và nói rõ hai file giờ lệch nhau ở đâu.

---

<a id="bay"></a>
## Bẫy đã biết

| Bẫy | Biểu hiện | Cách vòng |
|---|---|---|
| **Frame mới duplicate từ frame cũ** | Tên đúng format nhưng nội dung khác hẳn — qua mặt mọi check tự động | Luôn đọc `characters` đối chiếu (§C). Đây là bẫy hay gặp nhất |
| **Transport drop giữa call ghi** | `transport dropped mid-call; response was lost` | **Đã ghi rồi.** Đọc lại trạng thái trước khi chạy lại, đừng retry mù |
| `get_metadata` cả page quá lớn | Vượt token limit, bị ghi ra file tạm | Dùng §A qua Plugin API |
| Page load lazily | `children: 0` dù page có nội dung | `setCurrentPageAsync` trước khi đọc children |
| Đổi page nhiều lần trong một script | Reload file mỗi lần, rất chậm | Một lần đổi page mỗi call; fan out song song nếu nhiều page |
| Rename node con của instance | Tạo override rác, hoặc ném lỗi | `inInstance()` bỏ qua — sửa component gốc thì instance theo |
| Chụp ảnh cả section để đọc tên màn | Section 8000px → mỗi màn còn 46px, vô dụng | Đọc text (§C). Chỉ chụp node đơn lẻ không có text |
| Đoán Tab Bar / Header theo hình học | Sai ở frame cao hơn 812 | Bắt qua `mainComponent` (§E-2) |
| `node.query()` vỡ với ký tự đặc biệt | `Invalid selector: unexpected character '/'` | Dùng `findAll`/`findAllWithCriteria` với predicate JS |
| Đổi variant property cùng lượt với rename | Chạm mọi instance, hỏng thì khó lần | Tách lượt riêng, verify riêng |
| Component set có variant trùng tên | Hai variant cùng tên `download` → sinh tên instance trùng | Ghi nhận và báo — đó là lỗi dữ liệu trong file, không phải lỗi đặt tên |

---

## Thứ tự gọi khuyến nghị

```
1  use_figma  §A  cấu trúc                       1–2 call        đọc
2  use_figma  §B  đếm node và tên trùng          1 call          đọc
3  use_figma  §C  nội dung text từng section     1 call / section đọc
4  ── chốt phạm vi với người dùng ──                              HỎI
5  use_figma  §D  page + section + component     1 call          ghi
6  use_figma  §D  screen frame                   1 call / 40–70  ghi
7  use_figma  §E  ba pass layer                  1–2 call        ghi
8  use_figma  §F  verify                         lặp đến sạch    đọc
```

Bước 1–3 rẻ và an toàn. Bước 4 **bắt buộc** trước mọi thao tác ghi.
