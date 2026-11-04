// figma-style-builder · 02 Text styles. Sinh bởi build_tokens.py emit — không sửa tay, sửa tokens.json rồi emit lại.
// Kiểm tra font trước: thiếu font/weight nào thì dừng, chưa tạo gì. Upsert theo tên, không xoá style ngoài spec.
const SPEC = __SPEC__;
const WEIGHT_ALIASES = {
  Regular: ['Regular', 'Book', 'Normal', 'Roman'],
  Medium: ['Medium'],
  SemiBold: ['SemiBold', 'Semi Bold', 'Semibold', 'DemiBold', 'Demi Bold'],
  Bold: ['Bold'],
};

const available = await figma.listAvailableFontsAsync();
const stylesOf = fam => available.filter(f => f.fontName.family === fam).map(f => f.fontName.style);
const resolved = {}; // "role|weight" -> FontName
const missing = new Set();
for (const [, role, weight] of SPEC.styles) {
  const key = `${role}|${weight}`;
  if (key in resolved) continue;
  const fam = SPEC.fonts[role];
  const have = stylesOf(fam);
  if (!have.length) { missing.add(`${fam}: font chưa có trong Figma (Google Fonts hoặc cài vào máy rồi mở lại Figma)`); resolved[key] = null; continue; }
  const style = WEIGHT_ALIASES[weight].find(s => have.includes(s));
  if (!style) missing.add(`${fam} ${weight} — font có: ${have.join(', ')}`);
  resolved[key] = style ? { family: fam, style } : null;
}
if (missing.size) return { error: 'Thiếu font, chưa tạo style nào', missing: [...missing] };

const fontKeys = [...new Set(Object.values(resolved).map(f => JSON.stringify(f)))];
await Promise.all(fontKeys.map(k => figma.loadFontAsync(JSON.parse(k))));

const existing = await figma.getLocalTextStylesAsync();
const byName = Object.fromEntries(existing.map(s => [s.name, s]));
const out = { created: [], updated: [], unchanged: 0, extras: [], fonts: fontKeys.map(k => JSON.parse(k)) };

for (const [name, role, weight, size, lh, ls, textCase, decoration] of SPEC.styles) {
  const font = resolved[`${role}|${weight}`];
  let s = byName[name];
  const fresh = !s;
  if (fresh) { s = figma.createTextStyle(); s.name = name; }
  if (!fresh) await figma.loadFontAsync(s.fontName);
  const same = !fresh && s.fontName.family === font.family && s.fontName.style === font.style && s.fontSize === size
    && s.lineHeight.unit === 'PIXELS' && s.lineHeight.value === lh
    && s.letterSpacing.unit === 'PERCENT' && Math.abs(s.letterSpacing.value - ls) < 0.01
    && s.textCase === textCase && s.textDecoration === decoration;
  if (same) { out.unchanged++; continue; }
  s.fontName = font;
  s.fontSize = size;
  s.lineHeight = { unit: 'PIXELS', value: lh };
  s.letterSpacing = { unit: 'PERCENT', value: ls };
  s.textCase = textCase;
  s.textDecoration = decoration;
  (fresh ? out.created : out.updated).push(name);
}
const specNames = new Set(SPEC.styles.map(x => x[0]));
out.extras = existing.filter(s => !specNames.has(s.name)).map(s => s.name);
out.total = (await figma.getLocalTextStylesAsync()).length;
out.created = out.created.length;
return out;
