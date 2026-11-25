"""Проверка .vsdx: обратная отрисовка шейпов в картинку.

Visio в этой среде нет, поэтому корректность экспорта проверяется так:
шейпы из ``visio/pages/page1.xml`` читаются обратно и рисуются matplotlib —
если схема на картинке совпадает с исходным PNG, значит блоки, линии,
наконечники и подписи легли на свои места.

Запуск: python3 tools/vsdx_check.py activity_lanes_example
Результат: /tmp/vsdx_check_<имя>.png (слева PNG, справа отрисовка из vsdx)
"""

import math
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout  # noqa: E402

NS = "{http://schemas.microsoft.com/office/visio/2012/main}"


def _render(vsdx_path, out_png):
    z = zipfile.ZipFile(vsdx_path)
    root = ET.fromstring(z.read("visio/pages/page1.xml").decode())
    pages = ET.fromstring(z.read("visio/pages/pages.xml").decode())
    pw = ph = None
    for c in pages.iter(NS + "Cell"):
        if c.get("N") == "PageWidth":
            pw = float(c.get("V"))
        if c.get("N") == "PageHeight":
            ph = float(c.get("V"))
    fig, ax = plt.subplots(figsize=(7.2, 7.2 * ph / pw), dpi=200)
    ax.set_xlim(0, pw)
    ax.set_ylim(0, ph)
    ax.set_aspect("equal")
    ax.axis("off")

    for s in root.findall(".//" + NS + "Shape"):
        c = {e.get("N"): e.get("V") for e in s.findall(NS + "Cell")}
        px, py = float(c["PinX"]), float(c["PinY"])
        w, h = float(c["Width"]), float(c["Height"])
        x0, y0 = px - w / 2, py - h / 2
        fill = c.get("FillForegnd") if c.get("FillPattern") == "1" else None
        line = c.get("LineColor") if c.get("LinePattern", "0") != "0" else None
        lw = float(c.get("LineWeight", 0.0104)) * 72
        rnd = float(c.get("Rounding", 0))
        ea = c.get("EndArrow", "0") != "0"
        ba = c.get("BeginArrow", "0") != "0"

        txt = s.find(NS + "Text")
        if txt is not None and txt.text and txt.text.strip():
            size = s.find('.//' + NS + 'Section[@N="Character"]/' + NS
                          + 'Row/' + NS + 'Cell[@N="Size"]')
            color = s.find('.//' + NS + 'Section[@N="Character"]/' + NS
                           + 'Row/' + NS + 'Cell[@N="Color"]')
            style = s.find('.//' + NS + 'Section[@N="Character"]/' + NS
                           + 'Row/' + NS + 'Cell[@N="Style"]')
            geo = s.find(NS + 'Section[@N="Geometry"]')
            if geo is not None:
                ax.add_patch(Rectangle((x0, y0), w, h, facecolor=fill or "none",
                                       edgecolor="none", zorder=4))
            ax.text(px, py, txt.text.strip(),
                    fontsize=float(size.get("V")) * 72 if size is not None else 6,
                    ha="center", va="center",
                    color=color.get("V") if color is not None else "#000000",
                    fontweight="bold" if style is not None
                    and int(style.get("V")) & 1 else "normal",
                    style="italic" if style is not None
                    and int(style.get("V")) & 2 else "normal",
                    zorder=6, linespacing=1.15)
            continue

        geo = s.find(NS + 'Section[@N="Geometry"]')
        if geo is None:
            continue
        rows = geo.findall(NS + "Row")
        if not rows:
            continue
        if rows[0].get("T") == "Ellipse":
            ax.add_patch(Ellipse((x0 + w / 2, y0 + h / 2), w, h,
                                 facecolor=fill or "none",
                                 edgecolor=line or "none", lw=lw, zorder=2))
            continue
        pts = []
        for r in rows:
            pts.append((x0 + float(r.find(NS + 'Cell[@N="X"]').get("V")),
                        y0 + float(r.find(NS + 'Cell[@N="Y"]').get("V"))))
        if rnd > 0 and len(pts) == 5:
            ax.add_patch(FancyBboxPatch(
                (x0 + rnd, y0 + rnd), max(w - 2 * rnd, 0.01),
                max(h - 2 * rnd, 0.01),
                boxstyle="round,pad=%f,rounding_size=%f" % (rnd, rnd),
                facecolor=fill or "none", edgecolor=line or "none",
                lw=lw, zorder=2))
            continue
        if len(pts) == 2:
            (xa, ya), (xb, yb) = pts
            ax.plot([xa, xb], [ya, yb], color=line or "#000000", lw=lw, zorder=3,
                    solid_capstyle="butt")
            if ea:
                ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                            arrowprops=dict(arrowstyle="-|>",
                                            color=line or "#000000", lw=lw,
                                            mutation_scale=7), zorder=3)
            if ba:
                ax.annotate("", xy=(xa, ya), xytext=(xb, yb),
                            arrowprops=dict(arrowstyle="-|>",
                                            color=line or "#000000", lw=lw,
                                            mutation_scale=7), zorder=3)
            continue
        closed = math.dist(pts[0], pts[-1]) < 1e-6
        ax.add_patch(Polygon(pts, closed=closed, facecolor=fill or "none",
                             edgecolor=line or "none", lw=lw, zorder=2))

    fig.savefig(out_png, facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return out_png


def compare(name):
    """Отрисовать vsdx и положить рядом исходный PNG для сравнения."""
    from PIL import Image
    out = "/tmp/vsdx_check_%s.png" % name
    _render(layout.vsdx(name), out)
    a = Image.open(layout.png(name)).convert("RGB")
    b = Image.open(out).convert("RGB")
    H = 900
    a = a.resize((int(a.width * H / a.height), H))
    b = b.resize((int(b.width * H / b.height), H))
    canvas = Image.new("RGB", (a.width + b.width + 20, H), "white")
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width + 20, 0))
    canvas.save(out)
    print(out, canvas.size)
    return out


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        compare(nm)
