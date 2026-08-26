# sk8 — File & Artifact Production (SYADAGENTIC)
# Load when: PDF, DOCX, XLSX, PPTX, generate file, export, dokumen, file
# Category: Operations

## Operator Profile

Structured output specialist. When a format is requested → render the actual artifact, not a preview. Descriptive filenames. One specific edit offer after each delivery.

---

## Render Targets

| Format | Use case | Library |
|--------|----------|---------|
| `.md` | Specs, prompts, docs | direct emit |
| `.docx` | Proposals, contracts, briefs | python-docx |
| `.xlsx` | Trackers, models, budgets | openpyxl / xlsxwriter |
| `.pptx` | Decks, pitches | python-pptx |
| `.pdf` | Final delivery, invoices, certificates | reportlab |
| `.csv` | Data export | csv stdlib / pandas |
| `.html` | Reports w/ styling, landing pages | direct emit / jinja2 |
| `.py/.js/.sh` | Executable scripts | direct emit |
| `.json/.yaml` | Config, schemas | direct emit |

---

## DOCX Template

```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document()
title = doc.add_heading('Proposal — Project X', level=0)

doc.add_paragraph('Executive summary:')
p = doc.add_paragraph()
p.add_run('Key benefit. ').bold = True
p.add_run('Detail in same paragraph.')

doc.add_heading('Investment', level=1)
table = doc.add_table(rows=1, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = 'Tier', 'Price', 'Includes'
for tier, price, inc in [('Entry', 'IDR 500K', 'Basic'), ('Core', 'IDR 2.5M', 'Standard'), ('Premium', 'IDR 8M', 'Full')]:
    row = table.add_row().cells
    row[0].text, row[1].text, row[2].text = tier, price, inc

doc.save('proposal-projectx.docx')
```

---

## XLSX Template (with formulas + formatting)

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Summary'

headers = ['Date', 'Channel', 'Revenue (IDR)', 'Conversion %']
ws.append(headers)
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='2E5BBA')
    c.alignment = Alignment(horizontal='center')

data = [
    ('2025-05-01', 'IG',     1_200_000, 3.2),
    ('2025-05-02', 'TikTok', 2_400_000, 2.1),
]
for row in data:
    ws.append(row)

# Formula at bottom
ws['C5'] = '=SUM(C2:C4)'
ws['C5'].font = Font(bold=True)

# Column widths
for col, w in zip('ABCD', [12, 12, 16, 14]):
    ws.column_dimensions[col].width = w

wb.save('revenue-may2025.xlsx')
```

---

## PPTX Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.33); prs.slide_height = Inches(7.5)  # 16:9

# Title slide
s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = 'Project X'
s.placeholders[1].text = 'Q3 2025 Pitch'

# Content slide
s = prs.slides.add_slide(prs.slide_layouts[1])
s.shapes.title.text = 'Why now?'
tf = s.placeholders[1].text_frame
for i, point in enumerate(['Market timing', 'Distribution unlock', 'Cost collapse']):
    p = tf.add_paragraph() if i else tf.paragraphs[0]
    p.text = point
    p.font.size = Pt(28)

prs.save('pitch-projectx.pptx')
```

---

## PDF with Clickable Hyperlinks (ReportLab)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import HexColor

doc = SimpleDocTemplate('directory.pdf', pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)
styles = getSampleStyleSheet()
link_style = ParagraphStyle('Link', parent=styles['Normal'],
                            textColor=HexColor('#2E5BBA'), fontSize=11)

flow = [Paragraph('<b>Web3 Project Directory</b>', styles['Title']), Spacer(1, 12)]
for name, url in [('Project A', 'https://a.xyz'), ('Project B', 'https://b.xyz')]:
    flow.append(Paragraph(f'<a href="{url}">{name}</a> — {url}', link_style))
    flow.append(Spacer(1, 4))

doc.build(flow)
```

---

## Batch File Operations

```python
import os, shutil
from pathlib import Path

src = Path('input')
dst = Path('output'); dst.mkdir(exist_ok=True)

for f in src.glob('**/*.pdf'):
    rel = f.relative_to(src)
    target = dst / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, target)
    print(f'✅ {rel}')
```

---

## Image Processing Pipeline (Pillow + rembg)

```python
from PIL import Image, ImageOps
from rembg import remove

# Background removal
with open('input.jpg', 'rb') as fi, open('cutout.png', 'wb') as fo:
    fo.write(remove(fi.read()))

# Resize for Twitter avatar (400x400)
img = Image.open('cutout.png').convert('RGBA')
img = ImageOps.fit(img, (400, 400), Image.LANCZOS)
img.save('avatar.png', optimize=True)
```

---

## Structural Templates

### Proposal
```
1. Executive summary (1 paragraph)
2. Problem
3. Solution
4. Timeline
5. Investment (3 tiers, anchor on premium)
6. Proof / case studies
7. Next step (specific, dated)
```

### Technical spec
```
# [ID] — short description
## Goals      ## Non-goals    ## Setup
## Usage     ## Reference     ## Edge cases
```

### Insight report
```
1. Executive summary (1 paragraph)
2. Method
3. Findings (3–7 bullets)
4. Analysis
5. Prescriptions (exactly 3, specific, dated)
6. Appendix
```

---

## Render Protocol

```
1. Confirm scope (max 1 clarifying exchange)
2. Generate artifact
3. Save to output path with descriptive filename
4. Deliver with present_files
5. Offer: "Adjust [specific section]?"
```

---

## Constraints

- Render the ACTUAL artifact — inline preview is not a deliverable
- Filenames descriptive: `q3-revenue-analysis.xlsx` not `output.xlsx`
- One specific edit offer after delivery, not generic "any changes?"
- For multi-file deliverables: bundle into zip when > 3 files
