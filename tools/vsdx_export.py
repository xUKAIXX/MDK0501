"""Экспорт схем в Microsoft Visio (.vsdx).

Схемы строятся библиотекой нотаций на matplotlib. Здесь все художники
(патчи, линии, тексты) переводятся в шейпы Visio с явной геометрией:
прямоугольники, эллипсы, ромбы, ломаные и подписи остаются редактируемыми.

Файл собирается на основе «пустого» документа Visio из пакета vsdxkit,
поэтому контейнер (content types, связи, стили) гарантированно корректный.
"""

import os
import re
import zipfile
from xml.sax.saxutils import escape

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text

TEMPLATE_CANDIDATES = (
    ("vsdx", "media", "palette_extended.vsdx"),
)

FIG_W_INCH = 16.2 / 2.54          # ширина полосы набора


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


class VsdxPage:
    """Накопитель шейпов одной страницы."""

    def __init__(self, canvas):
        self.c = canvas
        self.shapes = []
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

    def _box(self, xs, ys):
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        return x0, y0, x1, y1

    # ---------- шейпы ----------
    def add_polygon(self, pts, fill=None, line=None, lw=1.0, pattern=1,
                    closed=True):
        if len(pts) < 2:
            return
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0, x1, y1 = self._box(xs, ys)
        # Visio плохо переносит шейпы нулевой толщины — добиваем до 0.02"
        min_u = 0.02 / self.scale
        for _ in range(2):
            if x1 - x0 < min_u:
                cx = (x0 + x1) / 2
                x0, x1 = cx - min_u / 2, cx + min_u / 2
            if y1 - y0 < min_u:
                cy = (y0 + y1) / 2
                y0, y1 = cy - min_u / 2, cy + min_u / 2
        w = x1 - x0
        h = y1 - y0
        pin_x, pin_y = self._pt(x0 + w / 2, y0 + h / 2)
        local = [(x - x0, h - (y - y0)) for x, y in pts]
        self.shapes.append(dict(
            kind="poly", pin=(pin_x, pin_y), size=(w * self.scale, h * self.scale),
            pts=[(px * self.scale, py * self.scale) for px, py in local],
            fill=fill, line=line, lw=lw, pattern=pattern, closed=closed,
            text=None,
        ))

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
        w = max(abs(dx1 - dx0), 0.4)
        h = max(abs(dy1 - dy0), 0.4)
        cx, cy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
        pin_x, pin_y = self._pt(cx, cy)
        color = _hex(t.get_color(), "#000000") or "#000000"
        style = 0
        if t.get_fontweight() in ("bold", 700, "heavy"):
            style |= 1
        if t.get_style() == "italic":
            style |= 2
        bg = t.get_bbox_patch()
        fill = "#ffffff" if bg is not None else None
        self.shapes.append(dict(
            kind="text", pin=(pin_x, pin_y),
            size=(w * self.scale, h * self.scale),
            pts=[], fill=fill, line=None, lw=1.0, pattern=1, closed=False,
            text=t.get_text(), fontsize=t.get_fontsize() / 72.0 * self.font_scale,
            color=color, style=style, angle=rot,
        ))

    # ---------- сборка ----------
    def _xml_shape(self, idx, s):
        w, h = s["size"]
        pin_x, pin_y = s["pin"]
        out = ["<Shape ID='%d' Type='Shape' LineStyle='3' FillStyle='3' "
               "TextStyle='3'>" % idx]
        out.append("<Cell N='PinX' V='%s'/><Cell N='PinY' V='%s'/>"
                   % (_fmt(pin_x), _fmt(pin_y)))
        out.append("<Cell N='Width' V='%s'/><Cell N='Height' V='%s'/>"
                   % (_fmt(w), _fmt(h)))
        out.append("<Cell N='LocPinX' V='%s' F='Width*0.5'/>"
                   "<Cell N='LocPinY' V='%s' F='Height*0.5'/>"
                   % (_fmt(w / 2), _fmt(h / 2)))
        angle = 0.0
        if s.get("angle"):
            angle = s["angle"] * 3.14159265358979 / 180.0
        out.append("<Cell N='Angle' V='%s'/><Cell N='FlipX' V='0'/>"
                   "<Cell N='FlipY' V='0'/><Cell N='ResizeMode' V='0'/>"
                   % _fmt(angle))
        out.append("<Cell N='LineWeight' V='%s'/><Cell N='LineColor' V='%s'/>"
                   "<Cell N='LinePattern' V='%d'/>"
                   % (_fmt(0.0104 * s["lw"]),
                      s["line"] or "#000000", s["pattern"] if s["line"] else 0))
        out.append("<Cell N='FillForegnd' V='%s'/><Cell N='FillPattern' V='%d'/>"
                   "<Cell N='FillForegndTrans' V='0'/>"
                   % (s["fill"] or "#ffffff", 1 if s["fill"] else 0))
        out.append("<Cell N='VerticalAlign' V='1'/>")

        if s["kind"] == "text":
            size = max(s["fontsize"], 0.02)
            out.append("<Section N='Character'><Row IX='0'>"
                       "<Cell N='Size' V='%s'/><Cell N='Color' V='%s'/>"
                       "<Cell N='Style' V='%d'/><Cell N='Font' V='Arial'/>"
                       "</Row></Section>" % (_fmt(size), s["color"], s["style"]))
            out.append("<Section N='Paragraph'><Row IX='0'>"
                       "<Cell N='HorzAlign' V='1'/><Cell N='Bullet' V='0'/>"
                       "</Row></Section>")
            out.append("<Text>%s</Text>" % escape(s["text"]))
            out.append("</Shape>")
            return "".join(out)

        rows = []
        if s["pts"]:
            pts = s["pts"]
            rows.append("<Row T='MoveTo' IX='1'><Cell N='X' V='%s'/>"
                        "<Cell N='Y' V='%s'/></Row>"
                        % (_fmt(pts[0][0]), _fmt(pts[0][1])))
            seq = pts[1:] + ([pts[0]] if s["closed"] else [])
            for i, (px, py) in enumerate(seq, start=2):
                rows.append("<Row T='LineTo' IX='%d'><Cell N='X' V='%s'/>"
                            "<Cell N='Y' V='%s'/></Row>"
                            % (i, _fmt(px), _fmt(py)))
        out.append("<Section N='Geometry' IX='0'><Cell N='NoFill' V='%d'/>"
                   "<Cell N='NoLine' V='%d'/>%s</Section>"
                   % (0 if s["fill"] else 1, 0 if s["line"] else 1,
                      "".join(rows)))
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
    """Сохранить текущую схему как .vsdx (шейпы Visio, не картинка)."""
    page = VsdxPage(canvas)
    for line in canvas.ax.lines:
        if not isinstance(line, Line2D):
            continue
        xs, ys = line.get_xdata(), line.get_ydata()
        if len(xs) < 2:
            continue
        page.add_polygon(list(zip(xs, ys)),
                         fill=None,
                         line=_hex(line.get_color(), "#000000"),
                         lw=max(line.get_linewidth(), 0.2),
                         pattern=_dash_pattern(line.get_linestyle()),
                         closed=False)
    for patch in canvas.ax.patches:
        if not isinstance(patch, Patch):
            continue
        polys = patch.get_path().to_polygons(patch.get_patch_transform(),
                                             closed_only=True)
        fill = _hex(patch.get_facecolor())
        line = _hex(patch.get_edgecolor())
        lw = max(patch.get_linewidth(), 0.2)
        pattern = _dash_pattern(patch.get_linestyle())
        for poly in polys:
            if len(poly) < 3:
                continue
            page.add_polygon([tuple(p) for p in poly], fill=fill, line=line,
                             lw=lw, pattern=pattern, closed=True)
    for text in canvas.ax.texts:
        if isinstance(text, Text) and text.get_text().strip():
            page.add_text(text)
    return page.build(out_path)
