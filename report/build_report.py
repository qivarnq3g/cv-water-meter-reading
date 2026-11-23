import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

HERE = Path(__file__).resolve().parent
FONT = "Times New Roman"
CAPTION = re.compile(r"^(Bảng|Hình) [A-Z0-9]+\.\d+\.\s")


def set_font(style, size=None, bold=None, italic=None, color=True):
    style.font.name = FONT
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(key), FONT)
    for key in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if fonts.get(qn(key)) is not None:
            del fonts.attrib[qn(key)]
    if size:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    if color:
        style.font.color.rgb = RGBColor(0, 0, 0)


def paragraph_format(style, align=None, line=1.5, before=0, after=6, indent=None, keep=None):
    fmt = style.paragraph_format
    if align is not None:
        fmt.alignment = align
    fmt.line_spacing = line
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    if indent is not None:
        fmt.first_line_indent = indent
    if keep is not None:
        fmt.keep_with_next = keep


def configure_styles(doc):
    styles = doc.styles
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Source Code", "Image Caption", "Table Caption", "Captioned Figure", "Figure"):
        if name in [s.name for s in styles]:
            set_font(styles[name], 13)
    for name in ("Body Text", "First Paragraph"):
        paragraph_format(styles[name], WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 0, 6, Cm(1))
    paragraph_format(styles["Normal"], WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 0, 6)
    paragraph_format(styles["Compact"], WD_ALIGN_PARAGRAPH.LEFT, 1.5, 0, 3)
    sizes = {1: 14, 2: 13, 3: 13}
    for level, size in sizes.items():
        style = styles[f"Heading {level}"]
        set_font(style, size, bold=True, italic=False)
        paragraph_format(style, WD_ALIGN_PARAGRAPH.LEFT, 1.15, 12 if level == 1 else 8, 6, Cm(0), True)
    set_font(styles["Image Caption"], 12, italic=False)
    paragraph_format(styles["Image Caption"], WD_ALIGN_PARAGRAPH.CENTER, 1.15, 3, 12, Cm(0))
    if "Source Code" in [s.name for s in styles]:
        source = styles["Source Code"]
        source.font.name = "Consolas"
        source.font.size = Pt(10)
        paragraph_format(source, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 0, 6, Cm(0))
    if "Bibliography" in [s.name for s in styles]:
        bib = styles["Bibliography"]
    else:
        bib = styles.add_style("Bibliography", 1)
    set_font(bib, 12)
    paragraph_format(bib, WD_ALIGN_PARAGRAPH.LEFT, 1.15, 0, 6)
    bib.paragraph_format.left_indent = Cm(1)
    bib.paragraph_format.first_line_indent = Cm(-1)
    for name in ("Hyperlink",):
        if name in [s.name for s in styles]:
            styles[name].font.color.rgb = RGBColor(0, 0, 0)
            styles[name].font.underline = False


def page_setup(section):
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin, section.right_margin = Cm(3), Cm(2)


def add_field(paragraph, instruction, placeholder=""):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run._r.append(begin)
    run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    run._r.append(instr)
    run = paragraph.add_run()
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run._r.append(sep)
    paragraph.add_run(placeholder)
    run = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(end)


def table_borders(table):
    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblStyle")):
        tbl_pr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), "000000")
        borders.append(element)
    for old in tbl_pr.findall(qn("w:tblBorders")):
        tbl_pr.remove(old)
    tbl_pr.append(borders)
    width = tbl_pr.find(qn("w:tblW"))
    if width is None:
        width = OxmlElement("w:tblW")
        tbl_pr.append(width)
    width.set(qn("w:type"), "pct")
    width.set(qn("w:w"), "5000")
    look = tbl_pr.find(qn("w:tblLook"))
    if look is not None:
        tbl_pr.remove(look)


def column_widths(table, total=9070):
    count = len(table.columns)
    weights = [6.0] * count
    for row in table.rows:
        seen = set()
        cells = []
        for cell in row.cells:
            if id(cell._tc) not in seen:
                seen.add(id(cell._tc))
                cells.append(cell)
        for index, cell in enumerate(cells[:count]):
            text = cell.text.strip()
            longest = max((len(word) for word in text.split()), default=0)
            weights[index] = max(weights[index], min(len(text), 30) + 3, longest * 1.3 + 3)
    scale = total / sum(weights)
    return [int(w * scale) for w in weights]


def fix_widths(table):
    widths = column_widths(table)
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    width = tbl_pr.find(qn("w:tblW"))
    width.set(qn("w:type"), "dxa")
    width.set(qn("w:w"), str(sum(widths)))
    grid = table._tbl.find(qn("w:tblGrid"))
    for col, value in zip(grid.findall(qn("w:gridCol")), widths):
        col.set(qn("w:w"), str(value))
    for row in table.rows:
        for tc, value in zip(row._tr.findall(qn("w:tc")), widths):
            tc_pr = tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.insert(0, tc_w)
            tc_w.set(qn("w:type"), "dxa")
            tc_w.set(qn("w:w"), str(value))


def format_tables(doc):
    for table in doc.tables:
        following = table._tbl.getnext()
        if following is not None and following.tag == qn("w:p"):
            p_pr = following.get_or_add_pPr()
            spacing = p_pr.find(qn("w:spacing"))
            if spacing is None:
                spacing = OxmlElement("w:spacing")
                p_pr.append(spacing)
            spacing.set(qn("w:before"), "160")
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_borders(table)
        fix_widths(table)
        for index, row in enumerate(table.rows):
            tr_pr = row._tr.get_or_add_trPr()
            if not tr_pr.findall(qn("w:cantSplit")):
                tr_pr.append(OxmlElement("w:cantSplit"))
            if index == 0:
                header = OxmlElement("w:tblHeader")
                tr_pr.append(header)
            for cell in row.cells:
                for shade in cell._tc.findall(".//" + qn("w:shd")):
                    shade.getparent().remove(shade)
                for paragraph in cell.paragraphs:
                    fmt = paragraph.paragraph_format
                    fmt.line_spacing = 1.0
                    fmt.space_before = Pt(2)
                    fmt.space_after = Pt(2)
                    fmt.first_line_indent = Cm(0)
                    if fmt.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY or fmt.alignment is None:
                        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in paragraph.runs:
                        run.font.size = Pt(11)
                        if index == 0:
                            run.font.bold = True


def format_paragraphs(doc):
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        has_image = bool(paragraph._p.findall(".//" + qn("w:drawing")))
        if has_image:
            fmt = paragraph.paragraph_format
            fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fmt.first_line_indent = Cm(0)
            fmt.keep_with_next = True
            fmt.line_spacing = 1.0
        elif paragraph.style.name == "Source Code":
            paragraph.paragraph_format.keep_together = True
            previous = paragraph._p.getprevious()
            if previous is not None and previous.tag == qn("w:p"):
                Paragraph(previous, paragraph._parent).paragraph_format.keep_with_next = True
        elif text.startswith("Bảng ") and CAPTION.match(text):
            fmt = paragraph.paragraph_format
            fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fmt.first_line_indent = Cm(0)
            fmt.keep_with_next = True
            fmt.space_before = Pt(6)
            for run in paragraph.runs:
                run.font.size = Pt(12)


def cover(doc, info):
    body = doc.element.body
    first = body[0]
    created = []

    def para(text="", size=13, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, before=0):
        paragraph = doc.add_paragraph()
        fmt = paragraph.paragraph_format
        fmt.alignment = align
        fmt.first_line_indent = Cm(0)
        fmt.space_after = Pt(after)
        fmt.space_before = Pt(before)
        fmt.line_spacing = 1.15
        if text:
            run = paragraph.add_run(text)
            run.font.size = Pt(size)
            run.font.bold = bold
        created.append(paragraph._p)
        return paragraph

    para(info["university"].upper(), 13, True)
    para(info["faculty"].upper(), 13, True, after=6)
    para("---o0o---", 12, after=60)
    para("BÁO CÁO BÀI TẬP LỚN", 16, True, after=6)
    para(f"Học phần: {info['course']}", 13, False, after=48)
    para(info["title"].upper(), 18, True, after=60)
    table = doc.add_table(rows=1 + len(info["members"]), cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(table)
    for cell, text in zip(table.rows[0].cells, ("Họ và tên", "Mã số sinh viên", "Vai trò")):
        cell.text = text
        cell.paragraphs[0].runs[0].font.bold = True
    for row, member in zip(table.rows[1:], info["members"]):
        for cell, key in zip(row.cells, ("name", "id", "role")):
            cell.text = member.get(key, "")
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.first_line_indent = Cm(0)
                paragraph.paragraph_format.line_spacing = 1.15
                paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    run.font.size = Pt(12)
    created.append(table._tbl)
    if info.get("lecturer"):
        para(f"Giảng viên hướng dẫn: {info['lecturer']}", 13, before=24)
    para(info["place_date"], 13, before=96)
    end = para()
    end.add_run().add_break(WD_BREAK.PAGE)
    heading = para("Mục lục", 14, True, WD_ALIGN_PARAGRAPH.CENTER, after=12)
    toc = para(align=WD_ALIGN_PARAGRAPH.LEFT)
    add_field(toc, 'TOC \\o "1-2" \\h \\z \\u', "Cập nhật mục lục.")
    for paragraph in doc.paragraphs:
        if paragraph.style.name == "Heading 1":
            paragraph.paragraph_format.page_break_before = True
            break
    for element in created:
        first.addprevious(element)


def footer_page_numbers(doc):
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(paragraph, "PAGE", "1")


def word_finish(docx_path, pdf_path):
    script = f"""
$ErrorActionPreference = 'Stop'
$before = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object Id)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
  $doc = $word.Documents.Open('{docx_path}')
  foreach ($id in -20, -21) {{
    $style = $doc.Styles.Item($id)
    $style.Font.Name = 'Times New Roman'
    $style.Font.Size = 12
    $style.ParagraphFormat.SpaceBefore = 0
    $style.ParagraphFormat.SpaceAfter = 0
    $style.ParagraphFormat.LineSpacingRule = 0
  }}
  foreach ($toc in $doc.TablesOfContents) {{ $toc.Update() }}
  $doc.Fields.Update() | Out-Null
  foreach ($toc in $doc.TablesOfContents) {{ $toc.Update() }}
  $doc.Repaginate()
  Write-Output ("pages=" + $doc.ComputeStatistics(2))
  $doc.Save()
  $doc.ExportAsFixedFormat('{pdf_path}', 17)
  $doc.Close(0)
}} finally {{
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
  Start-Sleep -Seconds 2
  Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object {{ $before -notcontains $_.Id }} | Stop-Process -Force
}}
"""
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig") as handle:
        handle.write(script)
    result = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", handle.name], capture_output=True, text=True, timeout=300)
    Path(handle.name).unlink(missing_ok=True)
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Build the report DOCX and PDF from report.md with pandoc and Word.")
    parser.add_argument("--cover", default=str(HERE / "cover.local.json"))
    parser.add_argument("--out-dir", default=str(HERE / "build"))
    parser.add_argument("--no-word", action="store_true")
    args = parser.parse_args()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.docx"
    subprocess.run(["pandoc", "report.md", "-f", "markdown-auto_identifiers", "-o", str(raw), "--resource-path", "."], cwd=HERE, check=True)
    doc = Document(raw)
    for section in doc.sections:
        page_setup(section)
    configure_styles(doc)
    for paragraph in list(doc.paragraphs):
        if paragraph.style.name in ("Title", "Subtitle"):
            paragraph._p.getparent().remove(paragraph._p)
    format_tables(doc)
    format_paragraphs(doc)
    info = json.loads(Path(args.cover).read_text(encoding="utf-8"))
    cover(doc, info)
    footer_page_numbers(doc)
    final = out / "bao-cao.docx"
    doc.save(final)
    raw.unlink()
    if not args.no_word:
        word_finish(str(final), str(out / "bao-cao.pdf"))


if __name__ == "__main__":
    main()
