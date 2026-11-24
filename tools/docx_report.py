"""Сборка отчётов по практическим работам в DOCX.

Оформление по требованиям методичек: Times New Roman 14 пт, интервал 1,5,
поля 2/1/2/2 см, выравнивание по ширине, нумерация страниц, подписи рисунков
и таблиц.
"""

import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "reports", "отчёт")
OUT = os.path.join(ROOT, "reports", "сделано")

FONT = "Times New Roman"
MAX_IMAGE_CM = 16.2


def _set_font(run, size=14, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), FONT)


def _page_number_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    _set_font(run, 12)
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)


class Report:
    def __init__(self, number, title, goal, variant, tools, pages=None):
        self.doc = Document()
        self.number = number
        self.title = title
        self.variant = variant
        self.fig_no = 0
        self.tab_no = 0
        self._setup()

    # ------------------------------------------------------------ настройка
    def _setup(self):
        st = self.doc.styles["Normal"]
        st.font.name = FONT
        st.font.size = Pt(14)
        st.paragraph_format.line_spacing = 1.5
        st.paragraph_format.space_after = Pt(0)
        st.paragraph_format.first_line_indent = Cm(1.25)
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts"); rpr.append(rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rf.set(qn(a), FONT)

        s = self.doc.sections[0]
        s.top_margin = Cm(2)
        s.bottom_margin = Cm(2)
        s.left_margin = Cm(3)
        s.right_margin = Cm(1.5)
        _page_number_footer(s)

    # ------------------------------------------------------------ примитивы
    def h1(self, text, page_break=False):
        if page_break:
            self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        _set_font(p.add_run(text), 14, bold=True)
        return p

    def h2(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _set_font(p.add_run(text), 14, bold=True)
        return p

    def p(self, text, first_line=True, align="justify", size=14, bold=False,
          italic=False, space_after=0):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(1.25) if first_line else Cm(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
                       "left": WD_ALIGN_PARAGRAPH.LEFT,
                       "center": WD_ALIGN_PARAGRAPH.CENTER,
                       "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
        _set_font(p.add_run(text), size, bold=bold, italic=italic)
        return p

    def bullets(self, items, marker="–"):
        for it in items:
            p = self.doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            _set_font(p.add_run(f"{marker} {it}"), 14)

    def numbered(self, items):
        for i, it in enumerate(items, 1):
            p = self.doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            _set_font(p.add_run(f"{i}. {it}"), 14)

    def image(self, name, caption, width_cm=16.0):
        path = os.path.join(ASSETS, name if name.endswith(".png") else name + ".png")
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        # ширина полосы набора при полях 3 / 1,5 см и формате A4 — 16,5 см
        width_cm = min(width_cm, MAX_IMAGE_CM)
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(6)
        run = p.add_run()
        run.add_picture(path, width=Cm(width_cm))
        self.fig_no += 1
        cp = self.doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.first_line_indent = Cm(0)
        cp.paragraph_format.space_after = Pt(10)
        _set_font(cp.add_run(f"Рисунок {self.fig_no} — {caption}"), 12)
        return self.fig_no

    def table(self, header, rows, caption, widths=None, size=12,
              align_first_left=True):
        self.tab_no += 1
        cp = self.doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        cp.paragraph_format.first_line_indent = Cm(0)
        cp.paragraph_format.space_before = Pt(8)
        _set_font(cp.add_run(f"Таблица {self.tab_no} — {caption}"), 12)

        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = t.rows[0].cells
        for i, h in enumerate(header):
            hdr[i].text = ""
            pp = hdr[i].paragraphs[0]
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pp.paragraph_format.first_line_indent = Cm(0)
            pp.paragraph_format.line_spacing = 1.0
            _set_font(pp.add_run(h), size, bold=True)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                pp = cells[i].paragraphs[0]
                pp.paragraph_format.line_spacing = 1.0
                pp.paragraph_format.first_line_indent = Cm(0)
                pp.alignment = (WD_ALIGN_PARAGRAPH.LEFT if (i == 0 and align_first_left)
                                else WD_ALIGN_PARAGRAPH.CENTER)
                _set_font(pp.add_run(str(v)), size)
        if widths:
            for r in t.rows:
                for c, wd in zip(r.cells, widths):
                    c.width = Cm(wd)
        ap = self.doc.add_paragraph()
        ap.paragraph_format.space_after = Pt(10)
        ap.paragraph_format.first_line_indent = Cm(0)
        return self.tab_no

    # ------------------------------------------------------------ титульный лист
    def title_page(self):
        d = self.doc
        for line, size, bold in [
            ("МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ", 13, False),
            ("Государственное бюджетное профессиональное образовательное учреждение", 12, False),
            ("________________________________________________", 12, False),
        ]:
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
            _set_font(p.add_run(line), size, bold=bold)

        for _ in range(3):
            d.add_paragraph()

        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        _set_font(p.add_run(f"ОТЧЁТ"), 20, bold=True)
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        _set_font(p.add_run(f"по практической работе № {self.number}"), 16)
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(10)
        _set_font(p.add_run(f"«{self.title}»"), 15, bold=True)
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(16)
        _set_font(p.add_run("МДК 05.01 Проектирование и разработка "
                            "информационных систем"), 14)

        for _ in range(4):
            d.add_paragraph()

        for line in [f"Вариант: {self.variant}",
                     "Выполнил(а): ____________________________",
                     "Группа: ____________________________",
                     "Проверил(а): ____________________________"]:
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.left_indent = Cm(8)
            _set_font(p.add_run(line), 14)

        for _ in range(3):
            d.add_paragraph()
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        _set_font(p.add_run("2026 г."), 14)

        d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ------------------------------------------------------------ блоки
    def goal_block(self, goal, task, equipment=None):
        self.h2("Цель работы")
        self.p(goal)
        self.h2("Индивидуальное задание")
        if isinstance(task, str):
            self.p(task)
        else:
            self.numbered(task)
        self.h2("Используемое программное обеспечение")
        self.p(equipment or "Персональный компьютер, Microsoft Word, "
                             "Microsoft Visio, Ramus Educational.")

    def conclusion(self, text):
        self.h2("Вывод")
        self.p(text)

    def questions(self, qa):
        self.h2("Ответы на контрольные вопросы")
        for i, (q, a) in enumerate(qa, 1):
            p = self.doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(6)
            _set_font(p.add_run(f"Вопрос {i}. {q}"), 14, bold=True)
            self.p(a)

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, name)
        self.doc.save(path)
        return path
