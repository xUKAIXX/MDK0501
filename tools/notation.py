"""
Библиотека отрисовки нотаций IDEF0 / DFD / IDEF3 / IDEF1X / UML.

Каждая диаграмма строится из примитивов, соответствующих нотации
(блок IDEF0 с четырьмя сторонами, процесс и накопитель DFD, UOW и перекрёсток
IDEF3, сущность IDEF1X, класс UML и т. д.), поэтому результат повторяет
вид диаграмм, построенных в Visio или Ramus.
"""

import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Circle, Ellipse, FancyBboxPatch, Polygon,
                                Rectangle, Wedge)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9

PAGE_W_CM = 16.2

# оформление как у диаграмм из методички (Visio): блоки светло-голубые,
# контур, текст и стрелки — тёмно-синие
THEME_FILL = "#eef6ff"
THEME_LINE = "#384c6b"
THEME_TEXT = "#384c6b"
LW = 0.9
# цвета потоков DFD (Ramus красит каждый поток своим цветом)
FLOW_COLORS = ["#c0179b", "#e87722", "#1f9bd1", "#5f9b1f", "#d4a017",
               "#8e44ad", "#0f8b8d"]
# холст печатается в ширину 16,2 см, поэтому кегль уменьшается до печатного
FONT_SCALE = 0.78

import layout  # раскладка файлов по папкам практических работ


# ----------------------------------------------------------------------------
# холст
# ----------------------------------------------------------------------------
class Canvas:
    def __init__(self, w=100, h=70, dpi=200, bg="white"):
        self.w, self.h = w, h
        # холст шириной 16,2 см — как ширина полосы набора в отчёте DOCX:
        # подписи масштабируются 1 : 1 и остаются читаемыми при печати
        fig_w = PAGE_W_CM / 2.54
        self.fig, self.ax = plt.subplots(figsize=(fig_w, fig_w * h / w), dpi=dpi)
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(h, 0)          # ось Y вниз, как на экране
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.fig.patch.set_facecolor(bg)
        self.fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    # ---------------- текст ----------------
    def text(self, x, y, s, size=9, ha="center", va="center", bold=False,
             italic=False, color=None, rotation=0, zorder=6, wrap=None,
             bg=None):
        color = color or THEME_TEXT
        if wrap:
            s = self._wrap(s, wrap)
        self.ax.text(x, y, s, fontsize=size * FONT_SCALE, ha=ha, va=va,
                     fontweight="bold" if bold else "normal",
                     style="italic" if italic else "normal",
                     color=color, rotation=rotation, zorder=zorder,
                     linespacing=1.15,
                     bbox=dict(facecolor=bg, edgecolor="none", pad=0.8)
                     if bg else None)

    @staticmethod
    def _wrap(s, width):
        out = []
        for block in str(s).split("\n"):
            words, line = block.split(), ""
            for w in words:
                if len(line) + len(w) + 1 > width and line:
                    out.append(line)
                    line = w
                else:
                    line = (line + " " + w).strip()
            out.append(line)
        return "\n".join(out)

    # ---------------- фигуры ----------------
    def rect(self, x, y, w, h, ec=THEME_LINE, fc=THEME_FILL, lw=LW, ls="-", zorder=3,
             rounded=0.0, hatch=None, alpha=1.0):
        if rounded:
            p = FancyBboxPatch((x, y), w, h,
                               boxstyle=f"round,pad=0,rounding_size={rounded}",
                               ec=ec, fc=fc, lw=lw, ls=ls, zorder=zorder,
                               hatch=hatch, alpha=alpha)
        else:
            p = Rectangle((x, y), w, h, ec=ec, fc=fc, lw=lw, ls=ls,
                          zorder=zorder, hatch=hatch, alpha=alpha)
        self.ax.add_patch(p)
        return p

    def ellipse(self, x, y, w, h, ec=THEME_LINE, fc=THEME_FILL, lw=LW, ls="-", zorder=3):
        p = Ellipse((x + w / 2, y + h / 2), w, h, ec=ec, fc=fc, lw=lw, ls=ls,
                    zorder=zorder)
        self.ax.add_patch(p)
        return p

    def circle(self, cx, cy, r, ec=THEME_LINE, fc=THEME_FILL, lw=LW, zorder=3, fill=True):
        p = Circle((cx, cy), r, ec=ec, fc=fc if fill else "none", lw=lw, zorder=zorder)
        self.ax.add_patch(p)
        return p

    def diamond(self, cx, cy, w, h, ec=THEME_LINE, fc=THEME_FILL, lw=LW, zorder=3):
        pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
        p = Polygon(pts, closed=True, ec=ec, fc=fc, lw=lw, zorder=zorder)
        self.ax.add_patch(p)
        return p

    def poly(self, pts, close=True, **kw):
        p = Polygon(pts, closed=close, **kw)
        self.ax.add_patch(p)
        return p

    # ---------------- стрелки ----------------
    def arrow(self, pts, head="filled", color=None, lw=LW, ls="-",
              label=None, label_at=None, label_dx=0, label_dy=0, size=8,
              label_ha="center", label_va="center", double=False, zorder=2,
              radius=None, curve=None, label_bg=None, label_color=None):
        """Ломаная со стрелкой на конце. pts — список (x, y)."""
        color = color or THEME_LINE
        pts = [tuple(map(float, p)) for p in pts]
        if curve:
            self._curved(pts, head, color, lw, ls, zorder, curve)
        else:
            xs, ys = zip(*pts)
            self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=zorder,
                         solid_capstyle="butt")
        self._head(pts[-2], pts[-1], head, color, lw, size)
        if double:
            self._head(pts[1], pts[0], head, color, lw, size)
        if label is not None:
            if label_at is None:
                mid = len(pts) // 2
                a, b = pts[mid - 1], pts[mid]
                lx, ly = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            else:
                lx, ly = label_at
            self.text(lx + label_dx, ly + label_dy, label, size=size,
                      ha=label_ha, va=label_va, zorder=zorder + 4,
                      bg=label_bg, color=label_color or color)

    def flow(self, pts, **kw):
        """Поток данных DFD: каждый поток своим цветом (как в Ramus)."""
        i = getattr(self, "_flow_i", 0)
        self._flow_i = i + 1
        kw.setdefault("color", FLOW_COLORS[i % len(FLOW_COLORS)])
        return self.arrow(pts, **kw)

    def _curved(self, pts, head, color, lw, ls, zorder, curve):
        t = [i / 40 for i in range(41)]
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        # квадратичная кривая с управляющей точкой, сдвинутой по нормали
        nx, ny = -(y1 - y0), (x1 - x0)
        norm = math.hypot(nx, ny) or 1
        cx = (x0 + x1) / 2 + nx / norm * curve
        cy = (y0 + y1) / 2 + ny / norm * curve
        xs = [(1 - s) ** 2 * x0 + 2 * (1 - s) * s * cx + s ** 2 * x1 for s in t]
        ys = [(1 - s) ** 2 * y0 + 2 * (1 - s) * s * cy + s ** 2 * y1 for s in t]
        self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=zorder)
        pts_new = [(xs[-2], ys[-2]), (xs[-1], ys[-1])]
        self._head(pts_new[0], pts_new[1], head, color, lw, 8)

    def _head(self, p0, p1, head, color, lw, size):
        if head in (None, "none"):
            return
        x0, y0 = p0
        x1, y1 = p1
        ang = math.atan2(y1 - y0, x1 - x0)
        L = max(2.2, size * 0.30)
        W = max(1.0, size * 0.13)
        if head == "filled":
            self.poly([(x1, y1),
                       (x1 - L * math.cos(ang) + W * math.sin(ang),
                        y1 - L * math.sin(ang) - W * math.cos(ang)),
                       (x1 - L * math.cos(ang) - W * math.sin(ang),
                        y1 - L * math.sin(ang) + W * math.cos(ang))],
                      fc=color, ec=color, lw=0.5, zorder=4)
        elif head == "open":
            self.ax.plot([x1 - L * math.cos(ang) + W * math.sin(ang),
                          x1, x1 - L * math.cos(ang) - W * math.sin(ang)],
                         [y1 - L * math.sin(ang) - W * math.cos(ang),
                          y1, y1 - L * math.sin(ang) + W * math.cos(ang)],
                         color=color, lw=lw, zorder=4)
        elif head == "triangle":
            self.poly([(x1, y1),
                       (x1 - L * math.cos(ang) + W * math.sin(ang),
                        y1 - L * math.sin(ang) - W * math.cos(ang)),
                       (x1 - L * math.cos(ang) - W * math.sin(ang),
                        y1 - L * math.sin(ang) + W * math.cos(ang))],
                      fc="#ffffff", ec=color, lw=lw, zorder=4)
        elif head in ("diamond", "diamond_filled"):
            d = L * 1.6
            cx, cy = x1 - d / 2 * math.cos(ang), y1 - d / 2 * math.sin(ang)
            pts = []
            for s in (0, 1, 2, 3):
                a = ang + math.pi / 2 * s
                pts.append((cx + d / 2 * math.cos(a) - d / 2 * math.cos(ang) * 0,
                            cy + d / 2 * math.sin(a)))
            # ромб: конец стрелки в x1
            nx, ny = -math.sin(ang), math.cos(ang)
            pts = [(x1, y1),
                   (cx + nx * W * 0.8, cy + ny * W * 0.8),
                   (x1 - d * math.cos(ang), y1 - d * math.sin(ang)),
                   (cx - nx * W * 0.8, cy - ny * W * 0.8)]
            self.poly(pts, fc=color if head == "diamond_filled" else "white",
                      ec=color, lw=lw, zorder=4)
        elif head == "circle":
            self.circle(x1 - 1.2 * math.cos(ang), y1 - 1.2 * math.sin(ang), 1.2,
                        ec=color, fc=color, zorder=4)

    # ---------------- сохранение ----------------
    def save(self, name, pad=None, vector=True):
        """Сохранить схему в папку своей работы: PNG + .vsdx для Visio."""
        base = name[:-4] if name.endswith(".png") else name
        path = layout.ensure(layout.png(base))
        self.fig.savefig(path, dpi=self.fig.dpi, facecolor="white",
                         bbox_inches="tight", pad_inches=0.15)
        if vector:
            try:
                import vsdx_export
                vsdx_export.export(self, layout.ensure(layout.vsdx(base)))
            except Exception as exc:      # noqa: BLE001
                print("[vsdx] %s: %s" % (base, exc))
        plt.close(self.fig)
        return path


def text_w(c, s, size):
    """Ширина строки в единицах схемы при данном кегле."""
    t = c.ax.text(0, 0, s, fontsize=size * FONT_SCALE)
    bb = t.get_window_extent(c.fig.canvas.get_renderer())
    (x0, _), (x1, _) = c.ax.transData.inverted().transform(
        [[bb.x0, bb.y0], [bb.x1, bb.y1]])
    t.remove()
    return abs(x1 - x0)


def fit_label(c, x, y, s, max_w, size=5.4, ha="center", min_size=3.8, **kw):
    """Подпись, которая гарантированно влезает в max_w по ширине.

    Подбирается кегль и перенос строк: подпись стрелки не должна наезжать
    на соседние блоки (как в диаграммах Visio из методички).
    """
    s = str(s)
    size = float(size)
    while size > min_size:
        lines, cur = [], ""
        ok = True
        for word in s.split():
            cand = (cur + " " + word).strip()
            if text_w(c, cand, size) <= max_w:
                cur = cand
            elif cur:
                lines.append(cur)
                cur = word
                if text_w(c, cur, size) > max_w:
                    ok = False
            else:
                ok = False
                break
        if cur:
            lines.append(cur)
        if ok and all(text_w(c, ln, size) <= max_w for ln in lines):
            return c.text(x, y, "\n".join(lines), size=size, ha=ha, **kw)
        size -= 0.2
    return c.text(x, y, s, size=min_size, ha=ha, **kw)


# ============================================================================
# IDEF0
# ============================================================================
def idef0_block(c, x, y, w, h, code, name, size=8.5, num_size=8, wrap=20):
    """Функциональный блок IDEF0. Возвращает словарь точек подключения."""
    c.rect(x, y, w, h, rounded=1.2)
    fit_label(c, x + w / 2, y + h / 2 - 1.5, name, w - 4.0, size=size)
    c.text(x + 2.2, y + h - 2.2, code, size=num_size, ha="left", va="center")
    return {
        "in": (x, y + h * 0.72),        # вход — левая грань
        "in2": (x, y + h * 0.32),
        "ctl": (x + w * 0.35, y),       # управление — верхняя грань
        "ctl2": (x + w * 0.72, y),
        "out": (x + w, y + h * 0.35),   # выход — правая грань
        "out2": (x + w, y + h * 0.72),
        "mech": (x + w * 0.35, y + h),  # механизм — нижняя грань
        "mech2": (x + w * 0.72, y + h),
        "l": (x, y + h / 2), "r": (x + w, y + h / 2),
        "t": (x + w / 2, y), "b": (x + w / 2, y + h),
        "box": (x, y, w, h),
    }


def idef0_frame(c, code="", title="", num="", author="Студент группы ИС-31",
                project="Агентство недвижимости", date="01.11.2026"):
    """Рамка листа IDEF0/DFD как в Ramus: шапка с полями проекта и строка
    заголовка внизу (ВЕТКА / НАЗВАНИЕ / НОМЕР)."""
    W, H = c.w, c.h
    top, bot = 10.0, 5.0
    L, R = 1.0, W - 1.0
    # внешний контур листа
    c.rect(L, 1, W - 2, H - 2, lw=1.1, fc="none", zorder=0)
    # шапка
    c.rect(L, 1, W - 2, top - 1, lw=0.9, fc="none", zorder=0)
    left_col = 20.0                     # колонка «ИСПОЛЬЗУЕТСЯ В:»
    c.ax.plot([L + left_col, L + left_col], [1, top], color=THEME_LINE, lw=0.7,
              zorder=0)
    c.text(L + left_col / 2, 4.2, "ИСПОЛЬЗУЕТСЯ В:", size=5.0)
    c.text(L + left_col / 2, 7.2, "ДГТУ", size=5.4)
    x0 = L + left_col
    # три строки шапки
    row_h = (top - 1) / 3.0
    for i in (1, 2):
        c.ax.plot([x0, R], [1 + row_h * i, 1 + row_h * i], color=THEME_LINE,
                  lw=0.7, zorder=0)
    # правый столбец «КОНТЕКСТ:»
    ctx_w = 26.0
    xc = R - ctx_w
    c.ax.plot([xc, xc], [1, top - 1 - row_h], color=THEME_LINE, lw=0.7, zorder=0)
    c.text(xc + 2, 2.6, "КОНТЕКСТ:", size=5.0, ha="left")
    c.rect(xc + 8, 3.9, ctx_w - 10, 2.2, lw=0.7, zorder=1)
    c.text(xc + 8 + (ctx_w - 10) / 2, 5.0, "ВЕРХ", size=5.2)
    # колонки средних строк
    xa = x0 + (xc - x0) * 0.30          # АВТОР / ПРОЕКТ
    xb = x0 + (xc - x0) * 0.52          # ДАТА / РЕВИЗИЯ
    xd = x0 + (xc - x0) * 0.78          # РАЗРАБАТЫВАЕТСЯ
    for x in (xa, xb, xd):
        c.ax.plot([x, x], [1, top - 1 - row_h], color=THEME_LINE, lw=0.7, zorder=0)
    r1, r2 = 1 + row_h * 0.5, 1 + row_h * 1.5
    c.text(x0 + 1.2, r1, "АВТОР:  " + author, size=5.0, ha="left")
    c.text(xa + 1.2, r1, "ДАТА:  " + date, size=5.0, ha="left")
    c.text(xd + 1.2, r1, "РАЗРАБАТЫВАЕТСЯ", size=5.0, ha="left")
    c.text(x0 + 1.2, r2, "ПРОЕКТ:  " + project, size=5.0, ha="left")
    c.text(xa + 1.2, r2, "РЕВИЗИЯ:  " + date, size=5.0, ha="left")
    c.text(xd + 1.2, r2, "ЧЕРНОВИК", size=5.0, ha="left")
    r3 = 1 + row_h * 2.5
    c.text(x0 + 1.2, r3, "ЗАМЕЧАНИЯ: 1 2 3 4 5 6 7 8 9 10", size=5.0, ha="left")
    c.text(xa + 1.2, r3, "РЕКОМЕНДОВАНО", size=5.0, ha="left")
    c.text(xd + 1.2, r3, "ПУБЛИКАЦИЯ", size=5.0, ha="left")
    # нижняя строка заголовка
    c.rect(L, H - bot - 1, W - 2, bot, lw=0.9, fc="none", zorder=0)
    b1 = L + (W - 2) * 0.17
    b2 = L + (W - 2) * 0.62
    for x in (b1, b2):
        c.ax.plot([x, x], [H - bot - 1, H - 1], color=THEME_LINE, lw=0.7, zorder=0)
    c.text(L + 1.5, H - bot / 2 - 1, "ВЕТКА:  " + code, size=5.6, ha="left")
    c.text(b1 + 1.5, H - bot / 2 - 1, "НАЗВАНИЕ:", size=5.6, ha="left")
    c.text(b1 + 14, H - bot / 2 - 1, title, size=6.0, ha="left")
    c.text(b2 + 1.5, H - bot / 2 - 1, "НОМЕР:", size=5.6, ha="left")
    c.text(b2 + 12, H - bot / 2 - 1, num, size=6.4, ha="left")
    return {"top": top, "bot": H - bot - 1}


# ============================================================================
# DFD
# ============================================================================
def dfd_process(c, x, y, w, h, num, name, size=8.5):
    """Процесс DFD (Гейн-Сарсон, Ramus): эллипс с номером в правом нижнем
    углу — так процессы нарисованы в методических указаниях."""
    c.ellipse(x, y, w, h)
    fit_label(c, x + w / 2, y + h / 2 - 1.2, name, w - 13.0, size=size)
    c.text(x + w / 2 + (w / 2 - 6) * 0.72, y + h / 2 + (h / 2 - 4) * 0.62,
           num, size=8.4, ha="right")
    return {"cx": x + w / 2, "cy": y + h / 2,
            "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "bx": (x, y, w, h)}


def dfd_store(c, x, y, w, h, sid, name, size=8.5):
    """Накопитель данных в нотации Гейна-Сарсона: открытый слева прямоугольник."""
    c.rect(x, y, w, h, lw=1.0)
    c.ax.plot([x + 11, x + 11], [y, y + h], color=THEME_LINE, lw=0.9, zorder=4)
    c.text(x + 5.5, y + h / 2, sid, size=7.5)
    fit_label(c, x + 11 + (w - 11) / 2, y + h / 2, name, w - 15.0, size=size)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def dfd_external(c, x, y, w, h, name, size=8.5):
    c.rect(x, y, w, h)
    fit_label(c, x + w / 2, y + h / 2, name, w - 4.0, size=size)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h)}


# ============================================================================
# IDEF3
# ============================================================================
def idef3_uow(c, x, y, w, h, num, name, size=8.5):
    c.rect(x, y, w, h)
    c.text(x + 2, y + h - 3, num, size=7, ha="left")
    fit_label(c, x + w / 2, y + h / 2, name, w - 4.0, size=size)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def idef3_junction(c, cx, cy, kind, jid, size=10):
    """kind: '&' (И), 'O' (ИЛИ), 'X' (исключающее ИЛИ)."""
    s = 7
    c.rect(cx - s / 2, cy - s / 2, s, s)
    sym = {"&": "&", "O": "O", "X": "X"}[kind]
    c.text(cx, cy, sym, size=size + 2, bold=False)
    c.text(cx + s / 2 + 2.5, cy - s / 2 + 1, f"J{jid}", size=6.5, ha="left")
    return {"l": (cx - s / 2, cy), "r": (cx + s / 2, cy),
            "t": (cx, cy - s / 2), "b": (cx, cy + s / 2), "c": (cx, cy)}


def idef3_referent(c, x, y, w, h, name, size=8.5):
    c.rect(x, y, w, h)
    c.text(x + w / 2, y + h / 2, name, size=size, wrap=14)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


# ============================================================================
# IDEF1X
# ============================================================================
def idef1x_entity(c, x, y, w, rows, name, key_rows=1, size=8, header_h=7,
                  row_h=5.4):
    """Сущность IDEF1X: шапка + область ключа (отделена линией) + данные."""
    h = header_h + row_h * len(rows) + 1.5
    c.rect(x, y, w, h)
    c.ax.plot([x, x + w], [y + header_h + row_h * key_rows,
                           y + header_h + row_h * key_rows], color=THEME_LINE, lw=0.8)
    fit_label(c, x + w / 2, y + header_h / 2, name, w - 4.0, size=size, bold=True)
    for i, r in enumerate(rows):
        yy = y + header_h + row_h * i + row_h / 2 + 0.4
        c.text(x + 2, yy, r, size=size - 0.7, ha="left")
    return {"x": x, "y": y, "w": w, "h": h,
            "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


# ============================================================================
# UML
# ============================================================================
def uml_class(c, x, y, w, name, attrs=(), ops=(), size=7.8, attr_h=4.8,
              bold_stereotype=None):
    head_h = 6 if bold_stereotype is None else 9
    h = head_h + attr_h * max(len(attrs), 1) + attr_h * max(len(ops), 1) + 2
    c.rect(x, y, w, h)
    c.ax.plot([x, x + w], [y + head_h, y + head_h], color=THEME_LINE, lw=0.9)
    y_split = y + head_h + attr_h * max(len(attrs), 1)
    c.ax.plot([x, x + w], [y_split, y_split], color=THEME_LINE, lw=0.9)
    c.text(x + w / 2, y + head_h / 2, name, size=size + 0.4, bold=True, wrap=20)
    for i, a in enumerate(attrs):
        c.text(x + 1.6, y + head_h + attr_h * i + attr_h / 2 + 0.3, a,
               size=size - 0.4, ha="left")
    for i, o in enumerate(ops):
        c.text(x + 1.6, y_split + attr_h * i + attr_h / 2 + 0.3, o,
               size=size - 0.4, ha="left")
    return {"x": x, "y": y, "w": w, "h": h,
            "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def uml_actor(c, cx, cy, name, size=8, label_below=True):
    r = 2.2
    c.circle(cx, cy, r, lw=1.0)
    c.ax.plot([cx, cx], [cy + r, cy + r + 5.5], color=THEME_LINE, lw=1.0, zorder=3)
    c.ax.plot([cx - 3.4, cx + 3.4], [cy + r + 3.4, cy + r + 3.4],
              color=THEME_LINE, lw=1.0, zorder=3)
    c.ax.plot([cx, cx - 3.2], [cy + r + 5.5, cy + r + 9.5], color=THEME_LINE, lw=1.0,
              zorder=3)
    c.ax.plot([cx, cx + 3.2], [cy + r + 5.5, cy + r + 9.5], color=THEME_LINE, lw=1.0,
              zorder=3)
    if label_below:
        c.text(cx, cy + r + 11.5, name, size=size, wrap=14)
        return {"t": (cx, cy - r), "b": (cx, cy + r + 13),
                "l": (cx - 4, cy + r + 4), "r": (cx + 4, cy + r + 4)}
    c.text(cx, cy - r - 2, name, size=size, va="top", wrap=14)
    return {"t": (cx, cy - r), "b": (cx, cy + r + 10)}


def uml_usecase(c, x, y, w, h, name, size=8.2):
    c.ellipse(x, y, w, h)
    fit_label(c, x + w / 2, y + h / 2, name, w - 4.0, size=size)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def uml_action(c, x, y, w, h, name, size=8.2):
    c.rect(x, y, w, h, rounded=2.4)
    fit_label(c, x + w / 2, y + h / 2, name, w - 5.0, size=size)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def uml_state(c, x, y, w, h, name, size=8.4, inner=(), label_top=False):
    c.rect(x, y, w, h, rounded=2.6)
    if label_top:
        c.ax.plot([x + 0.4, x + w - 0.4], [y + 6, y + 6], color=THEME_LINE, lw=0.8)
        c.text(x + w / 2, y + 3, name, size=size, bold=True, wrap=18)
    else:
        c.text(x + w / 2, y + h / 2 - (len(inner) * 3.6), name, size=size,
               bold=False, wrap=18, va="center")
    for i, s in enumerate(inner):
        c.text(x + w / 2, y + h / 2 + 3.4 + i * 3.6, s, size=size - 1.6)
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2, "box": (x, y, w, h)}


def uml_start(c, cx, cy, r=2.0):
    c.circle(cx, cy, r, fc=THEME_LINE, ec=THEME_LINE)
    return {"c": (cx, cy), "l": (cx - r, cy), "r": (cx + r, cy),
            "t": (cx, cy - r), "b": (cx, cy + r)}


def uml_end(c, cx, cy, r=2.6):
    c.circle(cx, cy, r, fc="#ffffff", ec=THEME_LINE)
    c.circle(cx, cy, r * 0.55, fc=THEME_LINE, ec=THEME_LINE)
    return {"c": (cx, cy), "l": (cx - r, cy), "r": (cx + r, cy),
            "t": (cx, cy - r), "b": (cx, cy + r)}


def uml_fork(c, cx, cy, w=22, h=2.4):
    c.rect(cx - w / 2, cy - h / 2, w, h, fc=THEME_LINE, ec=THEME_LINE)
    return {"l": (cx - w / 2, cy), "r": (cx + w / 2, cy), "c": (cx, cy),
            "t": (cx, cy - h / 2), "b": (cx, cy + h / 2)}


def uml_note(c, x, y, w, h, text, size=7.6):
    c.poly([(x, y), (x + w - 4, y), (x + w, y + 4), (x + w, y + h), (x, y + h)],
           fc="#ffffff", ec=THEME_LINE, lw=0.8, zorder=3)
    c.ax.plot([x + w - 4, x + w - 4, x + w], [y, y + 4, y + 4], color=THEME_LINE,
              lw=0.8, zorder=4)
    c.text(x + w / 2, y + h / 2, text, size=size, wrap=18)
