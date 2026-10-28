# Confluence Storage XHTML — Cheatsheet

## TOC
```xml
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
</ac:structured-macro>
```

## Image attachment embed
```xml
<ac:image ac:width="220">
  <ri:attachment ri:filename="screen.png"/>
</ac:image>
```

## Hyperlink
```xml
<a href="https://www.figma.com/design/{KEY}/...?node-id={ID}">Link UI</a>
```

## Code block (inline + multi-line)
- Inline: `<code>variable_name</code>`
- Multi-line (preserve formatting): `<pre>{ "key": "value" }</pre>`

## Cross-link memory (Confluence không hiểu `[[]]`)
Trong storage XHTML: dùng text thường, không link. Memory reference chỉ trong Note column để dev biết tên memory.

## Bullet list trong cell
```xml
<td><ul><li>Item 1</li><li>Item 2</li></ul></td>
```

## Bold/Italic
- `<strong>bold</strong>`
- `<em>italic</em>`

## Table headers
```xml
<table>
<tbody>
<tr><th>Col 1</th><th>Col 2</th></tr>
<tr><td>v1</td><td>v2</td></tr>
</tbody>
</table>
```

## Info/Warning/Note macro
```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Note text</p></ac:rich-text-body>
</ac:structured-macro>
```
Types: `info`, `note`, `warning`, `tip`.

## Page link (nội bộ)
```xml
<ac:link><ri:page ri:content-title="Page Title"/></ac:link>
```

## Special chars to escape
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- Trong code/pre: vẫn cần escape
