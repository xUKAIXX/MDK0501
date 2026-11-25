"""Экспорт схем в Microsoft Visio (.vsdx).

Схемы строятся библиотекой нотаций на matplotlib. Здесь художники
(matplotlib-патчи, линии, тексты) переводятся в родные фигуры Visio:

* прямоугольник / скруглённый прямоугольник — фигура с геометрией и ячейкой
  ``Rounding`` (в Visio скругление углов рисует сама программа);
* эллипс (UML-прецедент, круг начального состояния) — фигура с секцией
  ``Ellipse``, то есть настоящий гладкий эллипс, а не 60-угольник;
* линия и ломаная — шейп-путь с ячейкой ``EndArrow``: наконечник стрелки
  рисует Visio, поэтому он масштабируется вместе с толщением линии;
* подпись — текстовый шейп с шрифтом, кеглем, начертанием и (при подложке)
  белой заливкой.

Все параметры оформления (цвет линии, толщина, заливка, шрифт) записываются
в саму фигуру, наследование темы отключено (``LineStyle='0'`` и т. д.),
поэтому схема выглядит одинаково в любой версии Visio.

Файл собирается на основе «пустого» документа Visio из пакета vsdxkit,
поэтому контейнер (content types, связи, стили) гарантированно корректный.
"""

import math
import os
import re
import zipfile
from xml.sax.saxutils import escape

from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Patch
from matplotlib.text import Text

TEMPLATE_CANDIDATES = (
    ("vsdx", "media", "palette_extended.vsdx"),
)

FIG_W_INCH = 16.2 / 2.54          # ширина полосы набора

# наконечник стрелки Visio: 1 — открытый, 4 — залитый треугольник
ARROW_FILLED = "4"
HEAD_REACH = 2.8                  # насколько близко к концу линии искать наконечник


def _template_path():
    try:
        import vsdx  # пакет vsdxkit, модуль vsdx
    except ImportError:               # pragma: no cover
        return None
    for parts in TEMPLATE_CANDIDATES:
        p = os.path.join(os.path.dirname(vsdx.__file__), *parts[1:])
        if os.path.exists(p):
            return p
    return None


def _hex(color, default="#000000"):
    """RGBA кортеж matplotlib → '#rrggbb' (или None, если прозрачный)."""
    if color is None:
        return default
    if isinstance(color, str):
        if color in ("none", "None"):
            return None
        if color.startswith("#"):
            return color.lower()
    try:
        r, g, b = [float(v) for v in color[:3]]
        a = float(color[3]) if len(color) > 3 else 1.0
    except (TypeError, ValueError):
        return default
    if a == 0:
        return None
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def _dash_pattern(ls):
    """Стиль линии matplotlib → LinePattern Visio (1 сплошная, 2 штрих, 3 точки)."""
    if ls in ("-", "solid", None):
        return 1
    if isinstance(ls, tuple):
        seq = ls[1] if len(ls) > 1 else ls[0]
        if isinstance(seq, (list, tuple)):
            if len(seq) >= 2 and seq[1] <= 2:
                return 3
            return 2
        return 2
    return 2 if str(ls).startswith("--") else 3


def _fmt(v):
    return ("%.5f" % float(v)).rstrip("0").rstrip(".")


def _rounding(patch):
    """Радиус скругления FancyBboxPatch в единицах схемы (0 — острые углы)."""
    try:
        bs = patch.get_boxstyle()
    except (AttributeError, ValueError):
        return 0.0
    if type(bs).__name__ != "Round":
        return 0.0
    r = getattr(bs, "rounding_size", 0.0) or 0.0
    try:
        return float(r)
    except (TypeError, ValueError):
        return 0.0


class VsdxPage:
    """Накопитель шейпов одной страницы."""

    def __init__(self, canvas):
        self.c = canvas
        self.shapes = []
        self.lines = []                  # (индекс шейпа, начало, конец) — для наконечников
        fig = canvas.fig
        canvas.fig.canvas.draw()
        self.renderer = fig.canvas.get_renderer()
        self.scale = FIG_W_INCH / canvas.w          # дюймов на единицу схемы
        self.page_w = canvas.w * self.scale
        self.page_h = canvas.h * self.scale
        self.font_scale = self.page_w / fig.get_figwidth()

    # ---------- координаты ----------
    def _pt(self, x, y):
        """Данные схемы (ось Y вниз) → дюймы страницы Visio (ось Y вверх)."""
        return x * self.scale, self.page_h - y * self.scale

    def _frame(self, xs, ys):
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        # Visio не переносит шейпы нулевой толщины — добиваем до 0.02"
        min_u = 0.02 / self.scale
        if x1 - x0 < min_u:
            cx = (x0 + x1) / 2
            x0, x1 = cx - min_u / 2, cx + min_u / 2
        if y1 - y0 < min_u:
            cy = (y0 + y1) / 2
            y0, y1 = cy - min_u / 2, cy + min_u / 2
        return x0, y0, x1, y1

    def _add(self, **kw):
        self.shapes.append(kw)
        return len(self.shapes) - 1

    # ---------- шейпы ----------
    def add_path(self, pts, fill=None, line=None, lw=1.0, pattern=1,
                 closed=True, begin_arrow=False, end_arrow=False):
        if len(pts) < 2:
            return None
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0, x1, y1 = self._frame(xs, ys)
        w, h = x1 - x0, y1 - y0
        pin_x, pin_y = self._pt(x0 + w / 2, y0 + h / 2)
        local = [(x - x0, h - (y - y0)) for x, y in pts]
        idx = self._add(
            kind="path", pin=(pin_x, pin_y), size=(w * self.scale, h * self.scale),
            pts=[(px * self.scale, py * self.scale) for px, py in local],
            fill=fill, line=line, lw=lw, pattern=pattern, closed=closed,
            begin_arrow=begin_arrow, end_arrow=end_arrow,
        )
        if not closed and line:
            self.lines.append((idx, pts[0], pts[-1]))
        return idx

    def add_rect(self, x0, y0, x1, y1, fill, line, lw, pattern, rounding=0.0):
        w, h = x1 - x0, y1 - y0
        pin_x, pin_y = self._pt(x0 + w / 2, y0 + h / 2)
        return self._add(
            kind="rect", pin=(pin_x, pin_y),
            size=(w * self.scale, h * self.scale),
            fill=fill, line=line, lw=lw, pattern=pattern,
            rounding=max(0.0, min(rounding, min(w, h) / 2)) * self.scale,
        )

    def add_ellipse(self, x0, y0, x1, y1, fill, line, lw, pattern):
        w, h = x1 - x0, y1 - y0
        pin_x, pin_y = self._pt(x0 + w / 2, y0 + h / 2)
        return self._add(
            kind="ellipse", pin=(pin_x, pin_y),
            size=(w * self.scale, h * self.scale),
            fill=fill, line=line, lw=lw, pattern=pattern,
        )

    def add_text(self, t):
        x, y = t.get_position()
        rot = t.get_rotation() % 360
        bb = t.get_window_extent(self.renderer)
        (dx0, dy0), (dx1, dy1) = self.c.ax.transData.inverted().transform(
            [[bb.x0, bb.y0], [bb.x1, bb.y1]])
        if rot in (90, 270):
            cx, cy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
            half_w, half_h = (dy1 - dy0) / 2, (dx1 - dx0) / 2
            dx0, dx1 = cx - half_w, cx + half_w
            dy0, dy1 = cy - half_h, cy + half_h
        # запас по габариту: в Visio подпись набрана Arial, она уже DejaVu,
        # поэтому текст гарантированно остаётся в одну строку и не переносится
        w = max(abs(dx1 - dx0) * 1.06, 0.4)
        h = max(abs(dy1 - dy0) * 1.10, 0.4)
        cx, cy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
        pin_x, pin_y = self._pt(cx, cy)
        color = _hex(t.get_color(), "#000000") or "#000000"
        style = 0
        if t.get_fontweight() in ("bold", 700, "heavy"):
            style |= 1
        if t.get_style() == "italic":
            style |= 2
        has_bg = t.get_bbox_patch() is not None
        return self._add(
            kind="text", pin=(pin_x, pin_y),
            size=(w * self.scale, h * self.scale),
            fill="#ffffff" if has_bg else None, line=None, lw=1.0, pattern=1,
            text=t.get_text(), fontsize=t.get_fontsize() / 72.0 * self.font_scale,
            color=color, style=style, angle=rot * math.pi / 180.0,
        )

    # ---------- наконечники ----------
    def attach_heads(self, heads):
        """Залитые треугольники-наконечники → ячейки BeginArrow/EndArrow.

        heads — список (точки многоугольника). Треугольник приклеивается к той
        линии, у конца которой он стоит; сам треугольник как фигура не нужен.
        """
        for pts in heads:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            best = None
            for idx, a, b in self.lines:
                for end, p, field in ((0, a, "begin_arrow"), (1, b, "end_arrow")):
                    d = math.hypot(cx - p[0], cy - p[1])
                    if d <= HEAD_REACH and (best is None or d < best[0]):
                        best = (d, idx, field)
            if best is not None:
                self.shapes[best[1]][best[2]] = True

    # ---------- сборка ----------
    def _xml_shape(self, idx, s):
        w, h = s["size"]
        pin_x, pin_y = s["pin"]
        out = ["<Shape ID='%d' Type='Shape' LineStyle='0' FillStyle='0' "
               "TextStyle='0'>" % idx]
        out.append("<Cell N='PinX' V='%s'/><Cell N='PinY' V='%s'/>"
                   % (_fmt(pin_x), _fmt(pin_y)))
        out.append("<Cell N='Width' V='%s'/><Cell N='Height' V='%s'/>"
                   % (_fmt(w), _fmt(h)))
        out.append("<Cell N='LocPinX' V='%s' F='Width*0.5'/>"
                   "<Cell N='LocPinY' V='%s' F='Height*0.5'/>"
                   % (_fmt(w / 2), _fmt(h / 2)))
        out.append("<Cell N='Angle' V='%s'/><Cell N='FlipX' V='0'/>"
                   "<Cell N='FlipY' V='0'/><Cell N='ResizeMode' V='0'/>"
                   % _fmt(s.get("angle", 0.0)))
        out.append("<Cell N='LineWeight' V='%s'/><Cell N='LineColor' V='%s'/>"
                   "<Cell N='LinePattern' V='%d'/><Cell N='LineCap' V='0'/>"
                   "<Cell N='LineJoin' V='0'/><Cell N='Rounding' V='%s'/>"
                   % (_fmt(0.0104 * s["lw"]), s["line"] or "#000000",
                      s["pattern"] if s["line"] else 0,
                      _fmt(s.get("rounding", 0.0))))
        out.append("<Cell N='FillForegnd' V='%s'/><Cell N='FillBkgnd' V='%s'/>"
                   "<Cell N='FillPattern' V='%d'/>"
                   "<Cell N='FillForegndTrans' V='0'/>"
                   % (s["fill"] or "#ffffff", s["fill"] or "#ffffff",
                      1 if s["fill"] else 0))
        out.append("<Cell N='VerticalAlign' V='1'/>")
        if s["kind"] != "text":
            out.append("<Cell N='EndArrow' V='%s'/><Cell N='BeginArrow' V='%s'/>"
                       "<Cell N='EndArrowSize' V='2'/>"
                       "<Cell N='BeginArrowSize' V='2'/>"
                       % (ARROW_FILLED if s.get("end_arrow") else "0",
                          ARROW_FILLED if s.get("begin_arrow") else "0"))

        if s["kind"] == "text":
            size = max(s["fontsize"], 0.02)
            out.append("<Section N='Character'><Row IX='0'>"
                       "<Cell N='Size' V='%s'/><Cell N='Color' V='%s'/>"
                       "<Cell N='Style' V='%d'/><Cell N='Font' V='Arial'/>"
                       "</Row></Section>" % (_fmt(size), s["color"], s["style"]))
            out.append("<Section N='Paragraph'><Row IX='0'>"
                       "<Cell N='HorzAlign' V='1'/><Cell N='Bullet' V='0'/>"
                       "</Row></Section>")
            out.append("<Cell N='LeftMargin' V='0'/><Cell N='RightMargin' V='0'/>"
                       "<Cell N='TopMargin' V='0'/><Cell N='BottomMargin' V='0'/>")
            if s["fill"]:
                # подложка подписи — прямоугольник с белой заливкой без контура
                out.append("<Section N='Geometry' IX='0'><Cell N='NoFill' V='0'/>"
                           "<Cell N='NoLine' V='1'/>"
                           "<Row T='MoveTo' IX='1'><Cell N='X' V='0'/>"
                           "<Cell N='Y' V='0'/></Row>"
                           "<Row T='LineTo' IX='2'><Cell N='X' V='%s'/>"
                           "<Cell N='Y' V='0'/></Row>"
                           "<Row T='LineTo' IX='3'><Cell N='X' V='%s'/>"
                           "<Cell N='Y' V='%s'/></Row>"
                           "<Row T='LineTo' IX='4'><Cell N='X' V='0'/>"
                           "<Cell N='Y' V='%s'/></Row>"
                           "<Row T='LineTo' IX='5'><Cell N='X' V='0'/>"
                           "<Cell N='Y' V='0'/></Row></Section>"
                           % (_fmt(w), _fmt(w), _fmt(h), _fmt(h)))
            out.append("<Text>%s</Text>" % escape(s["text"]))
            out.append("</Shape>")
            return "".join(out)

        if s["kind"] == "ellipse":
            rows = ("<Row T='Ellipse' IX='1'><Cell N='X' V='%s' F='Width*0.5'/>"
                    "<Cell N='Y' V='%s' F='Height*0.5'/>"
                    "<Cell N='A' V='%s' F='Width*0.5'/>"
                    "<Cell N='B' V='%s' F='Height*0.5'/>"
                    "<Cell N='C' V='%s' F='Width*0.5'/>"
                    "<Cell N='D' V='%s' F='Height*0.5'/></Row>"
                    % (_fmt(w / 2), _fmt(h / 2), _fmt(w / 2), _fmt(h / 2),
                       _fmt(w / 2), _fmt(h / 2)))
        elif s["kind"] == "rect":
            rows = ("<Row T='MoveTo' IX='1'><Cell N='X' V='0'/><Cell N='Y' V='0'/></Row>"
                    "<Row T='LineTo' IX='2'><Cell N='X' V='%s'/><Cell N='Y' V='0'/></Row>"
                    "<Row T='LineTo' IX='3'><Cell N='X' V='%s'/><Cell N='Y' V='%s'/></Row>"
                    "<Row T='LineTo' IX='4'><Cell N='X' V='0'/><Cell N='Y' V='%s'/></Row>"
                    "<Row T='LineTo' IX='5'><Cell N='X' V='0'/><Cell N='Y' V='0'/></Row>"
                    % (_fmt(w), _fmt(w), _fmt(h), _fmt(h)))
        else:
            pts = s["pts"]
            rows = ("<Row T='MoveTo' IX='1'><Cell N='X' V='%s'/>"
                    "<Cell N='Y' V='%s'/></Row>" % (_fmt(pts[0][0]), _fmt(pts[0][1])))
            seq = pts[1:] + ([pts[0]] if s["closed"] else [])
            for i, (px, py) in enumerate(seq, start=2):
                rows += ("<Row T='LineTo' IX='%d'><Cell N='X' V='%s'/>"
                         "<Cell N='Y' V='%s'/></Row>" % (i, _fmt(px), _fmt(py)))
        out.append("<Section N='Geometry' IX='0'><Cell N='NoFill' V='%d'/>"
                   "<Cell N='NoLine' V='%d'/>%s</Section>"
                   % (0 if s["fill"] else 1, 0 if s["line"] else 1, rows))
        out.append("</Shape>")
        return "".join(out)

    def page_xml(self):
        body = "".join(self._xml_shape(i + 1, s)
                       for i, s in enumerate(self.shapes))
        return ("<?xml version='1.0' encoding='utf-8' ?>\r\n"
                "<PageContents xmlns='http://schemas.microsoft.com/office/visio/"
                "2012/main' xmlns:r='http://schemas.openxmlformats.org/"
                "officeDocument/2006/relationships' xml:space='preserve'>"
                "<Shapes>" + body + "</Shapes></PageContents>")

    def build(self, out_path):
        tpl = _template_path()
        if tpl is None:
            raise RuntimeError("нет шаблона Visio (пакет vsdxkit не установлен)")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with zipfile.ZipFile(tpl) as zin, \
                zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "visio/pages/page1.xml":
                    data = self.page_xml().encode("utf-8")
                elif item.filename == "visio/pages/pages.xml":
                    text = data.decode("utf-8")
                    text = re.sub(r"(<Cell N='PageWidth' V=')[^']*(')",
                                  lambda m: m.group(1) + _fmt(self.page_w) + m.group(2),
                                  text)
                    text = re.sub(r"(<Cell N='PageHeight' V=')[^']*(')",
                                  lambda m: m.group(1) + _fmt(self.page_h) + m.group(2),
                                  text)
                    text = re.sub(r"(<Cell N='PageScale' V=')[^']*(')",
                                  lambda m: m.group(1) + _fmt(self.scale) + m.group(2),
                                  text)
                    text = re.sub(r"(<Cell N='DrawingScale' V=')[^']*(')",
                                  lambda m: m.group(1) + _fmt(self.scale) + m.group(2),
                                  text)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
        return out_path


def export(canvas, out_path):
    """Сохранить текущую схему как .vsdx (шейпы Visio, не картинка).

    Фигуры переносятся в том же порядке, в каком их рисует matplotlib
    (по zorder): иначе залитые дорожки и блоки, добавленные позже, закрывают
    линии связей — в Visio схема выглядела без стрелок.
    """
    page = VsdxPage(canvas)

    items = []
    for i, line in enumerate(canvas.ax.lines):
        if isinstance(line, Line2D):
            items.append((line.get_zorder(), 0, i, "line", line))
    for i, patch in enumerate(canvas.ax.patches):
        if isinstance(patch, Patch):
            items.append((patch.get_zorder(), 1, i, "patch", patch))
    for i, text in enumerate(canvas.ax.texts):
        if isinstance(text, Text):
            items.append((text.get_zorder(), 2, i, "text", text))
    items.sort(key=lambda t: (t[0], t[1], t[2]))

    heads = []
    for _, _, _, kind, art in items:
        if kind == "line":
            xs, ys = art.get_xdata(), art.get_ydata()
            if len(xs) < 2:
                continue
            page.add_path(list(zip(xs, ys)),
                          fill=None,
                          line=_hex(art.get_color(), "#000000"),
                          lw=max(art.get_linewidth(), 0.2),
                          pattern=_dash_pattern(art.get_linestyle()),
                          closed=False)
            continue
        if kind == "text":
            if art.get_text().strip():
                page.add_text(art)
            continue

        patch = art
        fill = _hex(patch.get_facecolor())
        line = _hex(patch.get_edgecolor())
        lw = max(patch.get_linewidth(), 0.2)
        pattern = _dash_pattern(patch.get_linestyle())
        if isinstance(patch, (Ellipse, Circle)):
            cx, cy = patch.center
            page.add_ellipse(cx - patch.width / 2, cy - patch.height / 2,
                             cx + patch.width / 2, cy + patch.height / 2,
                             fill, line, lw, pattern)
            continue
        verts = [tuple(v) for v in patch.get_path().vertices]
        if isinstance(patch, FancyBboxPatch) and len(verts) >= 4:
            xs = [v[0] for v in verts]
            ys = [v[1] for v in verts]
            page.add_rect(min(xs), min(ys), max(xs), max(ys),
                          fill, line, lw, pattern, rounding=_rounding(patch))
            continue
        for poly in patch.get_path().to_polygons(patch.get_patch_transform(),
                                                 closed_only=True):
            if len(poly) < 3:
                continue
            pts = [tuple(p) for p in poly]
            # маленький залитый чёрный треугольник — это наконечник стрелки
            if fill in ("#000000", "#384c6b") and len(pts) <= 4:
                heads.append(pts)
                continue
            page.add_path(pts, fill=fill, line=line, lw=lw, pattern=pattern,
                          closed=True)

    page.attach_heads(heads)
    return page.build(out_path)
