# Figma MCP — script sẵn dùng và bẫy đã biết

Mọi script dưới đây chạy qua `mcp__figma__use_figma`. Trước lần gọi đầu tiên **phải nạp skill `figma-use`** (hoặc đọc resource `skill://figma/figma-use/SKILL.md` nếu không có plugin) — bỏ qua bước này gây ra loạt lỗi khó debug.

Mục lục: [A. Cấp document](#a) · [B. Toàn bộ variable](#b) · [C. Kiểm kê page](#c) · [D. Đếm cách dùng](#d) · [E. Đo contrast](#e) · [F. Dựng page Tokens](#f) · [Bẫy](#bay)

---

<a id="a"></a>
## A. Cấp document — page, text style, effect style, collection

Rẻ, chạy đầu tiên, cho bức tranh tổng thể. Không cần đổi page.

```js
const pages = figma.root.children.map((p) => ({ id: p.id, name: p.name }));

const lh = (v) => (!v || v.unit === 'AUTO') ? 'AUTO' : v.value + (v.unit === 'PERCENT' ? '%' : '');
const ls = (v) => !v ? '0' : v.value + (v.unit === 'PERCENT' ? '%' : 'px');

const textStyles = (await figma.getLocalTextStylesAsync()).map((s) =>
  s.name + ' :: ' + s.fontName.family + ' ' + s.fontName.style +
  ' ' + s.fontSize + '/' + lh(s.lineHeight) + ' ls=' + ls(s.letterSpacing));

const effectStyles = (await figma.getLocalEffectStylesAsync()).map((s) => {
  const eff = s.effects.map((e) =>
    (e.type === 'DROP_SHADOW' || e.type === 'INNER_SHADOW')
      ? e.type + ' x' + e.offset.x + ' y' + e.offset.y + ' blur' + e.radius +
        ' spread' + (e.spread || 0) + ' a' + Math.round((e.color.a || 0) * 100) / 100
      : e.type + ' ' + (e.radius !== undefined ? e.radius : '')).join(' + ');
  return s.name + ' :: ' + eff;
});

const collections = (await figma.variables.getLocalVariableCollectionsAsync())
  .map((c) => ({ name: c.name, id: c.id, modes: c.modes.map((m) => m.name), count: c.variableIds.length }));

return {
  pages,
  textStyleCount: textStyles.length, textStyles,
  paintStyles: (await figma.getLocalPaintStylesAsync()).map((s) => s.name),
  effectStyles,
  gridStyles: (await figma.getLocalGridStylesAsync()).map((s) => s.name),
  collections
};
```

**Đọc gì từ kết quả:** `paintStyles` rỗng nghĩa là màu đi qua variable chứ không qua style — tốt. `effectStyles` rỗng nghĩa là shadow đặt inline — ghi nhận, và liệt kê shadow tìm được ở bước component.

---

<a id="b"></a>
## B. Toàn bộ variable, kèm alias đã resolve

**Đây là cách duy nhất kiểm kê đủ token.** `get_variable_defs` chỉ trả về variable đang được gán.

```js
const toHex = (c) => {
  if (!c || typeof c.r !== 'number') return String(c);
  const h = (n) => Math.round(n * 255).toString(16).padStart(2, '0');
  let s = '#' + h(c.r) + h(c.g) + h(c.b);
  if (typeof c.a === 'number' && c.a < 1) s += h(c.a);
  return s.toUpperCase();
};

const collections = await figma.variables.getLocalVariableCollectionsAsync();
const all = await figma.variables.getLocalVariablesAsync();
const byId = {};
for (const v of all) byId[v.id] = v.name;

const fmt = (raw) => {
  if (raw && raw.type === 'VARIABLE_ALIAS') return '@' + (byId[raw.id] || raw.id);
  if (raw && typeof raw === 'object' && 'r' in raw) return toHex(raw);
  return String(raw);
};

return collections.map((c) => ({
  collection: c.name, id: c.id,
  modes: c.modes.map((m) => m.name),
  count: c.variableIds.length,
  vars: c.variableIds.map((id) => {
    const v = all.find((x) => x.id === id);
    if (!v) return null;
    return v.name + ' [' + v.resolvedType + '] ' +
      c.modes.map((m) => m.name + '=' + fmt(v.valuesByMode[m.modeId])).join(' | ');
  }).filter(Boolean)
}));
```

Giữ nguyên dạng alias (`@primary/400`) trong tài liệu — nó cho thấy kiến trúc thật, hữu ích hơn hex đã phẳng.

---

<a id="c"></a>
## C. Kiểm kê page — section, màn hình, component set

Một call cho mỗi page, **phát song song trong cùng một message**. Mỗi call đổi page đúng một lần.

```js
const page = await figma.getNodeByIdAsync('PAGE_ID');
await figma.setCurrentPageAsync(page);

const sections = [];
const loose = [];
for (const c of page.children) {
  if (c.type === 'SECTION') {
    const screens = c.children
      .filter((n) => n.type === 'FRAME' || n.type === 'COMPONENT' || n.type === 'COMPONENT_SET')
      .map((n) => {
        const sz = Math.round(n.width) + 'x' + Math.round(n.height);
        return n.name + (sz === '375x812' ? '' : ' (' + sz + ')');   // đổi khung chuẩn cho đúng project
      });
    sections.push({ name: c.name, id: c.id, count: screens.length, screens });
  } else {
    loose.push(c.name + ' [' + c.type + '] ' + Math.round(c.width) + 'x' + Math.round(c.height));
  }
}

const sets = page.findAllWithCriteria({ types: ['COMPONENT_SET'] }).map((n) => {
  let props = [], err = null;
  try {
    const defs = n.componentPropertyDefinitions;               // ném lỗi nếu set đang error
    props = Object.keys(defs).map((k) =>
      k + '=' + (defs[k].variantOptions ? defs[k].variantOptions.join('/') : defs[k].type));
  } catch (e) { err = String(e.message || e); }
  return { name: n.name, id: n.id, variants: n.children.length, props, error: err };
});

return { sectionCount: sections.length, sections, looseTopLevel: loose, componentSets: sets };
```

`findAllWithCriteria` dùng index theo type — nhanh hơn `findAll` với predicate hàng trăm lần.

---

<a id="d"></a>
## D. Đếm cách dùng token — bước cho phát hiện giá trị nhất

Trả lời câu hỏi: lớp semantic có thật sự được dùng không, hay chỉ là đồ trang trí?

```js
const page = await figma.getNodeByIdAsync('DESIGN_PAGE_ID');
await figma.setCurrentPageAsync(page);

const vars = await figma.variables.getLocalVariablesAsync();
const byId = {};
for (const v of vars) byId[v.id] = v.name;
const hex = (c) => {
  const h = (n) => Math.round(n * 255).toString(16).padStart(2, '0');
  return ('#' + h(c.r) + h(c.g) + h(c.b)).toUpperCase();
};

const counts = {};
let raw = 0, scanned = 0;
const all = page.findAll((n) => 'fills' in n && Array.isArray(n.fills) && n.fills.length > 0);
for (const n of all) {
  scanned++;
  for (const f of n.fills) {
    if (f.type !== 'SOLID') continue;
    const bv = f.boundVariables && f.boundVariables.color;
    if (bv) {
      const nm = byId[bv.id] || '(unknown)';
      counts[nm] = (counts[nm] || 0) + 1;
    } else {
      raw++;
    }
  }
}

const top = Object.keys(counts).sort((a, b) => counts[b] - counts[a])
  .slice(0, 40).map((k) => k + ' × ' + counts[k]);
return { scanned, hardcodedFills: raw, top };
```

**Cách đọc:** token định nghĩa nhưng đếm ra 0 nghĩa là lớp đó chưa được nối. Số fill hardcode cao nghĩa là hệ đang rò. Cả hai đều đổi thứ tự ưu tiên trong backlog — một lỗi contrast sửa được bằng một dòng nếu layer bind vào semantic, hoặc phải sửa hàng trăm layer nếu không.

---

<a id="e"></a>
## E. Đo contrast — tính ngay trong Figma, không cần runtime ở máy

Nhúng đoạn này vào bất kỳ script nào đã có hex đã resolve.

```js
const lum = (hex) => {
  const v = hex.replace('#', '');
  const ch = [0, 2, 4].map((i) => {
    const c = parseInt(v.substr(i, 2), 16) / 255;
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
};
const ratio = (a, b) => {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return Math.round(((x + 0.05) / (y + 0.05)) * 100) / 100;
};

// ví dụ: ratio('#FFFFFF', '#AB99FF')  →  2.41
```

**Ngưỡng WCAG 2.2 AA:**

| Đối tượng | Tối thiểu |
|---|---|
| Chữ thường | 4.5:1 |
| Chữ ≥ 24px, hoặc ≥ 18.5px bold | 3:1 |
| Icon và viền **mang nghĩa**, focus ring | 3:1 |
| Thành phần disabled | miễn trừ |
| Viền trang trí thuần | miễn trừ |

**Cặp bắt buộc đo:** mọi `text/*` trên nền trắng **và** trên nền màn hình (nền xám thường tệ hơn trắng nửa bậc); foreground trên fill của button chính; focus ring trên nền sáng; từng cặp `feedback/*/bg` + `/fg` (con số chỉ đúng khi fg đứng trên đúng bg của nó).

Khi đề xuất cách sửa, **tìm bậc có sẵn trong ramp trước** rồi mới đề xuất màu mới. Ramp 10 bậc thường đã chứa sẵn bậc đạt chuẩn.

---

<a id="f"></a>
## F. Dựng page Tokens — gỡ nút thắt vĩnh viễn

Bind mọi token lên một swatch thật. Sau đó `get_variable_defs` trên frame này trả đủ toàn bộ token kèm hex trong một call, cho mọi lần audit và mọi AI tool sau này.

Nguyên tắc dựng:

- **Một section cho mỗi nhóm** token.
- **Token nền** (`bg/*`, `surface/*`, `action/*`, `feedback/*/bg`): bind vào `fills` của chip.
- **Token chữ và icon** (`text/*`, `icon/*`): chip nền trắng, bind vào fill của **chữ "Aa"** hoặc của một shape bên trong. Bind vào nền thì swatch không thể hiện đúng token.
- **Token viền** (`border/*`): chip nền trắng, bind vào `strokes`, `strokeWeight` 4 cho dễ thấy.
- **Cặp feedback**: dựng thành banner thật — nền bind `bg`, chữ bind `fg`, viền bind `border/<state>`. Vừa kiểm kê vừa chốt anatomy.
- **Nhân đôi sang bản Dark** bằng `clone()` rồi `setExplicitVariableModeForCollection(collection, darkModeId)`.

Đoạn cốt lõi để bind:

```js
const vars = await figma.variables.getLocalVariablesAsync();
const V = {}; for (const v of vars) V[v.name] = v;

const paintOf = (name) => figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0.5, g: 0.5, b: 0.5 } }, 'color', V[name]);

chip.fills = [paintOf('surface/default')];        // nền
glyph.fills = [paintOf('text/brand')];            // chữ
chip.strokes = [paintOf('border/default')];       // viền
```

`setBoundVariableForPaint` trả về **paint mới** — phải hứng lại và gán, không mutate tại chỗ.

Đặt frame ở vùng trống: quét `page.children` tìm đáy thấp nhất rồi đặt xuống dưới. Đừng đặt ở (0,0) — thường đã có thứ khác ở đó.

---

<a id="bay"></a>
## Bẫy đã biết

| Bẫy | Biểu hiện | Cách vòng |
|---|---|---|
| `get_variable_defs` chỉ trả token **đang apply** | Token có thật nhưng không thấy → kết luận sai "file chưa có" | Dùng Variables API (§B) |
| `search_design_system` không đọc local variable | Trả mảng rỗng, không báo lỗi | Chỉ dùng cho library đã publish |
| Page load lazily | `children: 0` ở lần đọc đầu dù page có nội dung | `setCurrentPageAsync` trước khi đọc children |
| `componentPropertyDefinitions` ném lỗi | Cả script chết vì một set hỏng | try/catch quanh từng set, ghi nhận set lỗi |
| `node.query()` vỡ với ký tự đặc biệt | `Invalid selector: unexpected character '/'` hoặc `(0xc2)` với dấu `·` | Dùng `findAll`/`findOne` với predicate JS |
| `get_metadata` cả page quá lớn | Vượt token limit, bị ghi ra file | Đọc file bằng grep/offset, hoặc đọc từng section |
| Đổi page nhiều lần trong một script | Reload file mỗi lần, rất chậm | Một lần đổi page mỗi call; fan out song song |
| Font thiếu chặn ghi text | `Cannot write to node with unloaded font` | Tạo text bằng font có sẵn → set nội dung → mới `setTextStyleIdAsync` |
| Frame mới duplicate từ frame cũ | Tên đúng format nhưng nội dung khác hẳn | Đọc `characters` bên trong để đối chiếu, đừng tin tên |
| File `.ts` không publish được lên artifact | `extension ".ts" is not served` | Truyền `contentType: "text/plain"` |

---

## Thứ tự gọi khuyến nghị

```
1  use_figma   §A  cấp document                          1 call
2  use_figma   §B  toàn bộ variable                      1 call
3  use_figma   §C  kiểm kê page                          N call song song
4  use_figma   §D  đếm cách dùng                         1 call
5  get_design_context  từng component set                2–3 call một lượt
6  get_screenshot      10–15 màn → tải về → đọc          1 message + 1 lệnh tải
7  use_figma   §E  đo contrast                           gộp vào bước khác
8  use_figma   §F  dựng page Tokens                      4–8 call, dựng từng phần
```

Bước 1–4 là đọc, rẻ và an toàn. Bước 8 là ghi — hỏi người dùng trước.
