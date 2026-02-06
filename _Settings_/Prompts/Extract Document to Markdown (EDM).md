---
title: Extract Document to Markdown (EDM)
abbreviation: EDM
category: ingestion
---

Convert documents to well-formatted markdown.

## Supported Formats

| Format | Tool |
|--------|------|
| `.epub` | `python3 epub_to_markdown.py "<path>" -o "<output>"` |
| `.docx` | `python3 docx_to_markdown.py "<path>" -o "<output>"` |
| `.pdf` | pdfplumber (OCR if scanned) |
| `.txt` | Direct read with encoding detection |

## Process

1. **PRE-CHECK**: Skip if `.md` exists and is newer than source
2. **EXTRACT**: Run appropriate tool/script
3. **VERIFY**: Ensure frontmatter and content extracted correctly

## Output

- `{original_filename}.md` (same folder, same base filename)
- Frontmatter with `source_file`, `source_type`, `extracted`, `status: extracted`

## PDF-Specific (no skill yet)

- Use pdfplumber for text extraction
- Extract tables as markdown tables
- If <100 chars extracted → use pytesseract OCR
- Add `ocr_used: true` to frontmatter if OCR needed

## TXT-Specific

- Try UTF-8 first, then latin-1
- Log encoding in frontmatter if non-UTF-8
- Wrap in basic markdown structure with frontmatter

## Caveats

- **Large files (>50 pages)**: Process in chunks, add page count note
- **Scanned PDFs**: Attempt text first, fallback to OCR
- **Complex tables**: Merged cells may not convert perfectly
- **DOCX/EPUB**: See skill docs for format-specific limitations
