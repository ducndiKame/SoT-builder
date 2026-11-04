// figma-style-builder · 03 Foundations. Sinh bởi build_tokens.py emit — không sửa tay.
// Dựng trên page Foundations 3 frame: "Design Tokens / Light", "Design Tokens / Dark", "Typography".
// Mọi swatch bind vào biến thật → get_variable_defs trên frame trả đủ token cho AI tool về sau.
// Frame đã có thì dừng, trừ khi emit với --replace (designer đã đồng ý).
const SPEC = __SPEC__;

const cols = await figma.variables.getLocalVariableCollectionsAsync();
const semCol = cols.find(c => c.name === 'Semantic');
const primCol = cols.find(c => c.name === 'Primitives');
const dimCol = cols.find(c => c.name === 'Dimension');
if (!semCol || !primCol) return { error: 'Chưa có collection Primitives / Semantic. Chạy 01-variables.js trước.' };
const styles = await figma.getLocalTextStylesAsync();
const ST = Object.fromEntries(styles.map(s => [s.name, s]));
const NEED = ['Heading/H1', 'Heading/H4', 'Heading/H5', 'Body/Small/Regular', 'Body/Small/Medium', 'Caption/Regular', 'Label/Medium/Semi Bold'];
const missingStyles = NEED.filter(n => !ST[n]);
if (missingStyles.length) return { error: 'Chưa có text style. Chạy 02-text-styles.js trước.', missing: missingStyles };

let page = figma.root.children.find(p => p.name === SPEC.page);
if (!page) { page = figma.createPage(); page.name = SPEC.page; }
await figma.setCurrentPageAsync(page);
const FRAMES = ['Design Tokens / Light', 'Design Tokens / Dark', 'Typography'];
const old = page.children.filter(n => FRAMES.includes(n.name));
if (old.length && !SPEC.replace) return { error: `Page "${SPEC.page}" đã có: ${old.map(n => n.name).join(', ')}. Hỏi designer, rồi emit lại với --replace.`, existing: old.map(n => ({ id: n.id, name: n.name })) };
const origin = old.length ? { x: Math.min(...old.map(n => n.x)), y: Math.min(...old.map(n => n.y)) } : null;
old.forEach(n => n.remove());
let startX = origin ? origin.x : page.children.reduce((m, n) => Math.max(m, n.x + n.width), 0) + (page.children.length ? 200 : 0);
const startY = origin ? origin.y : 0;

await Promise.all([...new Set(styles.map(s => JSON.stringify(s.fontName)))].map(k => figma.loadFontAsync(JSON.parse(k))));
const loadVars = async col => (await Promise.all(col.variableIds.map(id => figma.variables.getVariableByIdAsync(id)))).filter(Boolean);
const semVars = await loadVars(semCol);
const V = Object.fromEntries(semVars.map(v => [v.name, v]));
const primVars = await loadVars(primCol);
const P = Object.fromEntries(primVars.map(v => [v.name, v]));

const paint = v => figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', v);
const box = (dir, name, gap) => { const f = figma.createAutoLayout(dir, { name, itemSpacing: gap }); f.fills = []; return f; };
async function text(str, style, fillVar) {
  const t = figma.createText();
  await t.setTextStyleIdAsync(ST[style].id);
  t.characters = str;
  if (fillVar) t.fills = [paint(fillVar)];
  return t;
}
function fixedText(parent, t, width) { parent.appendChild(t); t.resize(width, t.height); t.textAutoResize = 'HEIGHT'; return t; }
function centered(name, w, h, fillVar, radius) {
  const f = figma.createAutoLayout('HORIZONTAL', { name });
  f.primaryAxisAlignItems = 'CENTER'; f.counterAxisAlignItems = 'CENTER';
  f.resize(w, h); f.cornerRadius = radius;
  f.fills = fillVar ? [paint(fillVar)] : [];
  return f;
}
function rootFrame(name, x) {
  const r = box('VERTICAL', name, 48);
  r.paddingLeft = r.paddingRight = r.paddingTop = r.paddingBottom = 64;
  r.resize(1240, 100); r.primaryAxisSizingMode = 'AUTO';
  r.cornerRadius = 32; r.fills = [paint(V['bg/primary'] || V[semVars[0].name])];
  r.x = x; r.y = startY;
  return r;
}
async function section(root, title, note) {
  const s = box('VERTICAL', title, 16);
  root.appendChild(s); s.layoutSizingHorizontal = 'FILL';
  s.appendChild(await text(title, 'Heading/H5', V['text/primary']));
  if (note) s.appendChild(await text(note, 'Caption/Regular', V['text/tertiary']));
  const row = box('HORIZONTAL', 'Tiles', 16);
  s.appendChild(row); row.layoutSizingHorizontal = 'FILL'; row.layoutWrap = 'WRAP'; row.counterAxisSpacing = 16;
  return row;
}
async function tile(row, swatch, label) {
  const t = box('VERTICAL', label, 8);
  row.appendChild(t);
  t.appendChild(swatch);
  fixedText(t, await text(label, 'Caption/Regular', V['text/secondary']), swatch.width);
  return t;
}
const has = (v, scope) => v.scopes.includes(scope);
const groupOf = n => (n.startsWith('action/') ? n.split('/').slice(0, 2).join('/') : n.split('/')[0]);

async function semanticTiles(root) {
  const groups = [];
  for (const v of semVars) {
    const g = groupOf(v.name);
    let entry = groups.find(x => x.g === g);
    if (!entry) groups.push(entry = { g, vars: [] });
    entry.vars.push(v);
  }
  for (const { g, vars } of groups) {
    if (g.startsWith('action/')) {
      const fg = V[`${g}/foreground`];
      const row = await section(root, g.replace('/', ' / '), `${vars.length} tokens. Label bound to ${g}/foreground.`);
      for (const v of vars.filter(x => x !== fg)) {
        const pill = centered(v.name, 160, 48, v, 24);
        pill.appendChild(await text('Button', 'Label/Medium/Semi Bold', fg || V['text/primary']));
        await tile(row, pill, v.name.split('/').pop());
      }
      continue;
    }
    if (g === 'feedback') {
      const row = await section(root, g, `${vars.length} tokens. Always pair bg + fg.`);
      const kinds = [...new Set(vars.map(v => v.name.split('/')[1]))];
      for (const k of kinds) {
        const bg = V[`feedback/${k}/bg`], fg = V[`feedback/${k}/fg`];
        if (!bg || !fg) continue;
        const b = box('HORIZONTAL', `feedback/${k}`, 8);
        b.paddingLeft = b.paddingRight = 16; b.paddingTop = b.paddingBottom = 12;
        b.counterAxisAlignItems = 'CENTER'; b.cornerRadius = 12; b.fills = [paint(bg)];
        if (V[`border/${k}`]) { b.strokes = [paint(V[`border/${k}`])]; b.strokeWeight = 1; }
        const dot = figma.createEllipse(); dot.resize(12, 12); dot.fills = [paint(fg)]; b.appendChild(dot);
        b.appendChild(await text(`${k[0].toUpperCase() + k.slice(1)} message`, 'Body/Small/Medium', fg));
        await tile(row, b, `feedback/${k}/bg + /fg`);
      }
      continue;
    }
    const row = await section(root, g, `${vars.length} tokens.`);
    for (const v of vars) {
      let sw;
      if (has(v, 'TEXT_FILL') && !has(v, 'FRAME_FILL')) {
        const back = /inverse/.test(v.name) ? V['bg/inverse'] : /on-brand/.test(v.name) ? V['bg/brand'] : V['surface/default'];
        sw = centered(v.name, 160, 64, back, 12);
        sw.strokes = [paint(V['border/default'])]; sw.strokeWeight = 1;
        sw.appendChild(await text('Aa', 'Heading/H4', v));
      } else if (has(v, 'STROKE_COLOR') && !has(v, 'SHAPE_FILL')) {
        sw = centered(v.name, 160, 64, V['surface/default'], 12);
        sw.strokes = [paint(v)]; sw.strokeWeight = 2;
      } else if (g === 'icon') {
        sw = centered(v.name, 160, 64, V['surface/default'], 12);
        sw.strokes = [paint(V['border/default'])]; sw.strokeWeight = 1;
        const dot = figma.createEllipse(); dot.resize(20, 20); dot.fills = [paint(v)]; sw.appendChild(dot);
      } else {
        sw = figma.createRectangle(); sw.name = v.name; sw.resize(160, 64); sw.cornerRadius = 12;
        sw.fills = [paint(v)]; sw.strokes = [paint(V['border/subtle'] || v)]; sw.strokeWeight = 1;
      }
      await tile(row, sw, v.name);
    }
  }
}

async function primitiveRows(root) {
  const s = box('VERTICAL', 'Primitives', 16);
  root.appendChild(s); s.layoutSizingHorizontal = 'FILL';
  s.appendChild(await text('Primitives', 'Heading/H5', V['text/primary']));
  s.appendChild(await text(`Raw palette, ${primVars.length} tokens. Reference only — product UI binds Semantic.`, 'Caption/Regular', V['text/tertiary']));
  const ramps = [];
  for (const v of primVars) { const r = v.name.includes('/') ? v.name.split('/')[0] : 'base'; if (!ramps.includes(r)) ramps.push(r); }
  const dark = P['neutral/900'] || P['black'], light = P['white'];
  for (const r of ramps) {
    const line = box('HORIZONTAL', r, 8);
    s.appendChild(line); line.counterAxisAlignItems = 'CENTER';
    fixedText(line, await text(r, 'Caption/Regular', V['text/secondary']), 80);
    for (const v of primVars.filter(x => (r === 'base' ? !x.name.includes('/') : x.name.startsWith(r + '/')))) {
      const c = v.valuesByMode[primCol.defaultModeId];
      const lum = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
      const sw = centered(v.name, 88, 48, v, 8);
      if (lum > 0.9) { sw.strokes = [paint(P['neutral/200'] || dark)]; sw.strokeWeight = 1; }
      sw.appendChild(await text(v.name.split('/').pop(), 'Caption/Regular', lum > 0.5 ? dark : light));
      line.appendChild(sw);
    }
  }
}

async function dimensionTiles(root) {
  const dv = await loadVars(dimCol);
  const sp = dv.filter(v => v.name.startsWith('spacing/'));
  const rd = dv.filter(v => v.name.startsWith('radius/'));
  if (sp.length) {
    const row = await section(root, 'spacing', `${sp.length} tokens. Gap and padding.`);
    for (const v of sp) {
      const val = v.valuesByMode[dimCol.defaultModeId];
      const holder = centered(v.name, 96, 48, null, 0); holder.primaryAxisAlignItems = 'MIN';
      const bar = figma.createRectangle(); bar.resize(Math.max(val, 1), 16); bar.fills = [paint(V['bg/brand'])];
      holder.appendChild(bar);
      await tile(row, holder, `${v.name} · ${val}`);
    }
  }
  if (rd.length) {
    const row = await section(root, 'radius', `${rd.length} tokens.`);
    for (const v of rd) {
      const r = figma.createRectangle(); r.name = v.name; r.resize(96, 64);
      r.fills = [paint(V['bg/brand-subtle'] || V['bg/brand'])];
      r.strokes = [paint(V['border/brand'] || V['border/default'])]; r.strokeWeight = 1;
      for (const k of ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius']) r.setBoundVariable(k, v);
      await tile(row, r, `${v.name} · ${v.valuesByMode[dimCol.defaultModeId]}`);
    }
  }
}

const created = [];
const pad = 120;
const light = rootFrame('Design Tokens / Light', startX);
const lightMode = semCol.modes.find(m => m.name === 'Light') || semCol.modes[0];
light.setExplicitVariableModeForCollection(semCol, lightMode.modeId);
light.appendChild(await text(`Design Tokens — Light${SPEC.title ? ' · ' + SPEC.title : ''}`, 'Heading/H1', V['text/primary']));
light.appendChild(await text(`Semantic (${semVars.length}) aliases Primitives (${primVars.length}). Every swatch is bound to a live variable — edit a token and this page updates.`, 'Body/Small/Regular', V['text/secondary']));
await semanticTiles(light);
await primitiveRows(light);
if (dimCol) await dimensionTiles(light);
created.push(light.id);
startX += light.width + pad;

const darkMode = semCol.modes.find(m => m.name === 'Dark');
if (darkMode) {
  const dark = rootFrame('Design Tokens / Dark', startX);
  dark.setExplicitVariableModeForCollection(semCol, darkMode.modeId);
  dark.appendChild(await text('Design Tokens — Dark', 'Heading/H1', V['text/primary']));
  dark.appendChild(await text('Same Semantic tokens, Dark mode applied to this frame.', 'Body/Small/Regular', V['text/secondary']));
  await semanticTiles(dark);
  created.push(dark.id);
  startX += dark.width + pad;
}

const typo = rootFrame('Typography', startX);
typo.setExplicitVariableModeForCollection(semCol, lightMode.modeId);
typo.appendChild(await text('Typography', 'Heading/H1', V['text/primary']));
typo.appendChild(await text(`${styles.length} text styles. Size / line height in px, letter spacing in %.`, 'Body/Small/Regular', V['text/secondary']));
const list = box('VERTICAL', 'Styles', 24);
typo.appendChild(list); list.layoutSizingHorizontal = 'FILL';
for (const s of styles) {
  const row = box('HORIZONTAL', s.name, 24);
  list.appendChild(row); row.layoutSizingHorizontal = 'FILL'; row.counterAxisAlignItems = 'CENTER';
  fixedText(row, await text(s.name, 'Caption/Regular', V['text/secondary']), 200);
  const sample = await text('The quick brown fox 1,250', s.name, V['text/primary']);
  row.appendChild(sample); sample.layoutSizingHorizontal = 'FILL'; sample.textAutoResize = 'HEIGHT';
  const ls = Math.round(s.letterSpacing.value * 100) / 100;
  const meta = `${s.fontName.family} ${s.fontName.style} · ${s.fontSize}/${s.lineHeight.unit === 'PIXELS' ? s.lineHeight.value : 'auto'} · ${ls}%${s.textCase === 'UPPER' ? ' · UPPER' : ''}${s.textDecoration === 'UNDERLINE' ? ' · underline' : ''}`;
  fixedText(row, await text(meta, 'Caption/Regular', V['text/tertiary']), 220);
}
created.push(typo.id);

return { page: { id: page.id, name: page.name }, createdNodeIds: created, replaced: old.length };
