# Example Workflow — Page "1. Home" IIP506

End-to-end commands đã chạy thành công để tạo page Home dưới parent `304546393` (IIP506 Version 1.0.0 New).

## Inputs
- `feature_name`: `1. Home`
- `figma_file_key`: `FSbG2FIBhHsCxSv7wmGnwh`
- `figma_section_id`: `883:12529` (Home section)
- `parent_page_id`: `304546393`

## Step 1: Discover Figma section
```bash
python scripts/figma_export.py discover FSbG2FIBhHsCxSv7wmGnwh 883:12529
```
Output: liệt kê 18 children (FRAME + CONNECTOR + SECTION).

## Step 2: Export 8 PNG @2x
```bash
python scripts/figma_export.py export FSbG2FIBhHsCxSv7wmGnwh \
  "883:12530=home-default,1600:13737=home-jump-to-current,883:12706=home-old-lesson-good,883:12883=home-old-lesson-okay,883:13060=home-old-lesson-bad,883:13237=home-alp-bottomsheet,883:13504=home-welcome-back,1321:9140=home-old-lesson-tap-below" \
  C:/tmp/figma_home
```

## Step 3: Create empty Confluence page
```bash
python scripts/confluence_publish.py create 304546393 "1. Home"
# → ID: 304546395
```

## Step 4: Upload PNG attachments
```bash
python scripts/confluence_publish.py upload 304546395 C:/tmp/figma_home
```

## Step 5: Build storage XHTML body
Manually build per `references/format-spec.md`, save to `body.xml`. Reference: `references/example-home-body.xml`.

Sections:
- TOC macro
- `<h1>System Requirement</h1>` + Figma link
- `<h1>Flow</h1>` (3-câu mô tả)
- `<h1>Functional Requirement</h1>`
  - `<h2>Acceptance Criteria 1: First-time vào Home</h2>` + table (3 scenarios)
  - `<h2>Acceptance Criteria 2: Home default state</h2>` + table (4 scenarios)
  - `<h2>Acceptance Criteria 3: Jump to current</h2>` + table (2 scenarios)
  - `<h2>Acceptance Criteria 4: Tap lesson hiện tại</h2>` + table (2 scenarios)
  - `<h2>Acceptance Criteria 5: Tap lesson cũ (Good/Okay/Bad)</h2>` + table (5 scenarios)
  - `<h2>Acceptance Criteria 6: Resume conversation</h2>` + table (4 scenarios)
  - `<h2>Acceptance Criteria 7: Cảnh báo Lessons-per-week</h2>` + table (2 scenarios)
- `<h1>Validation Rules</h1>` + 4-row table
- `<h1>Non-functional Requirement</h1>`
  - `<h2>Key remote bật/tắt feature</h2>` (4 keys)
  - `<h2>Key remote config nội dung ALP intro</h2>` (JSON)
  - `<h2>Key remote config nội dung Welcome Back</h2>` (JSON)

## Step 6: PUT body
```bash
python scripts/confluence_publish.py update 304546395 body.xml
```

## Result
- Page URL: {CONFLUENCE_HOST}/pages/viewpage.action?pageId=304546395
- 8 attachments uploaded
- 7 AC tables với total ~22 scenario rows
- 4 remote keys + 2 JSON config blocks
