// figma-style-builder · 01 Variables. Sinh bởi build_tokens.py emit — không sửa tay, sửa tokens.json rồi emit lại.
// Upsert theo tên: tạo biến thiếu, cập nhật biến lệch, KHÔNG xoá biến ngoài spec (chỉ liệt kê).
const SPEC = __SPEC__;

const hexToRgba = h => {
  const n = h.replace('#', '');
  return { r: parseInt(n.slice(0, 2), 16) / 255, g: parseInt(n.slice(2, 4), 16) / 255, b: parseInt(n.slice(4, 6), 16) / 255, a: n.length === 8 ? parseInt(n.slice(6, 8), 16) / 255 : 1 };
};
const words = name => name.split(/[\/\s_-]+/).filter(Boolean).map(w => w.toLowerCase());
const codeName = (tpl, name) => {
  const w = words(name);
  const camel = w.map((x, i) => (i ? x[0].toUpperCase() + x.slice(1) : x)).join('');
  return tpl.replace('{kebab}', w.join('-')).replace('{snake}', w.join('_')).replace('{camel}', camel);
};
const sameValue = (cur, want) => {
  if (!cur) return false;
  if (want.type === 'VARIABLE_ALIAS') return cur.type === 'VARIABLE_ALIAS' && cur.id === want.id;
  if (typeof want === 'number') return cur === want;
  return ['r', 'g', 'b', 'a'].every(k => Math.abs((cur[k] ?? 1) - want[k]) < 0.002);
};
const sameList = (a, b) => a.length === b.length && a.every(x => b.includes(x));

const report = { collections: [], created: 0, updated: 0, unchanged: 0, conflicts: [], extras: [], errors: [] };
const lookup = {}; // "Collection:name" -> Variable
const existingCols = await figma.variables.getLocalVariableCollectionsAsync();

for (const c of SPEC.collections) {
  let col = existingCols.find(x => x.name === c.name);
  const isNew = !col;
  if (!col) col = figma.variables.createVariableCollection(c.name);
  const modeIds = [];
  for (const [i, m] of c.modes.entries()) {
    let mode = col.modes.find(x => x.name === m);
    if (!mode && i === 0 && col.modes.length === 1 && (isNew || /^Mode \d+$/.test(col.modes[0].name))) {
      col.renameMode(col.modes[0].modeId, m);
      mode = col.modes[0];
    }
    if (!mode) {
      try { mode = { modeId: col.addMode(m), name: m }; }
      catch (e) { report.errors.push(`Không thêm được mode ${c.name}/${m} (gói Figma giới hạn số mode?): ${e.message}`); }
    }
    modeIds.push(mode ? mode.modeId : null);
  }
  try { col.hiddenFromPublishing = !!c.hidden; } catch (e) { report.errors.push(`${c.name}.hiddenFromPublishing: ${e.message}`); }

  const existing = (await Promise.all(col.variableIds.map(id => figma.variables.getVariableByIdAsync(id)))).filter(Boolean);
  const byName = Object.fromEntries(existing.map(v => [v.name, v]));
  let created = 0, updated = 0, unchanged = 0;

  for (const [name, type, values, scopes, description] of c.vars) {
    let v = byName[name];
    if (v && v.resolvedType !== type) { report.conflicts.push(`${c.name}/${name}: đang là ${v.resolvedType}, spec là ${type}`); continue; }
    const fresh = !v;
    if (fresh) v = figma.variables.createVariable(name, col, type);
    let changed = false;
    values.forEach((raw, i) => {
      const modeId = modeIds[i];
      if (!modeId) return;
      let want;
      if (typeof raw === 'string' && raw.startsWith('@')) {
        const target = lookup[raw.slice(1)];
        if (!target) { report.errors.push(`${c.name}/${name}: không tìm thấy alias ${raw}`); return; }
        want = { type: 'VARIABLE_ALIAS', id: target.id };
      } else want = type === 'COLOR' ? hexToRgba(raw) : raw;
      if (!sameValue(v.valuesByMode[modeId], want)) { v.setValueForMode(modeId, want); changed = true; }
    });
    if (!sameList(v.scopes, scopes)) { v.scopes = scopes; changed = true; }
    if ((v.description || '') !== description) { v.description = description; changed = true; }
    const tpl = SPEC.code[type] || {};
    for (const platform of Object.keys(tpl)) {
      const want = codeName(tpl[platform], name);
      if (v.codeSyntax[platform] !== want) { v.setVariableCodeSyntax(platform, want); changed = true; }
    }
    lookup[`${c.name}:${name}`] = v;
    if (fresh) created++; else if (changed) updated++; else unchanged++;
  }
  const specNames = new Set(c.vars.map(x => x[0]));
  const extras = existing.filter(v => !specNames.has(v.name)).map(v => v.name);
  if (extras.length) report.extras.push({ collection: c.name, count: extras.length, names: extras.slice(0, 40) });
  report.collections.push({ name: c.name, id: col.id, modes: col.modes.map(m => m.name), total: col.variableIds.length, created, updated, unchanged });
  report.created += created; report.updated += updated; report.unchanged += unchanged;
}
return report;
