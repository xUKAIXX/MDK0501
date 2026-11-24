"""Сборка листов предпросмотра: все схемы отчётов на двух картинках."""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import layout

EXAMPLES = [
    ("idef0_example_context", "IDEF0 · контекст A-0 (пример)"),
    ("idef0_example_a1", "IDEF0 · декомпозиция A1 (пример)"),
    ("dfd_example_context", "DFD · контекст, уровень 0 (пример)"),
    ("dfd_example_level1", "DFD · уровень 1 (пример)"),
    ("idef3_example", "IDEF3 · сборка ПК (пример)"),
    ("org_example", "Оргструктура (пример)"),
    ("idef1x_example", "IDEF1X · ER-модель (пример)"),
    ("usecase_example", "Use case · учёт заявок (пример)"),
    ("class_example", "Классы · учёт заявок (пример)"),
    ("activity_example", "Деятельность (пример)"),
    ("activity_lanes_example", "Деятельность с дорожками (пример)"),
    ("state_example", "Состояния заявки (пример)"),
]

VARIANTS = [
    ("idef0_variant_context", "IDEF0 · контекст A-0 (вариант 3)"),
    ("idef0_variant_a1", "IDEF0 · декомпозиция A1 (вариант 3)"),
    ("idef0_variant_a4", "IDEF0 · декомпозиция A4 (вариант 3)"),
    ("dfd_variant_context", "DFD · контекст (вариант 3)"),
    ("dfd_variant_level1", "DFD · уровень 1 (вариант 3)"),
    ("idef3_variant", "IDEF3 · оформление сделки (вариант 3)"),
    ("org_variant", "Оргструктура агентства (вариант 3)"),
    ("idef1x_logical", "IDEF1X · логическая модель (вариант 3)"),
    ("idef1x_physical", "IDEF1X · физическая модель (вариант 3)"),
    ("usecase_variant", "Use case · агентство (вариант 3)"),
    ("class_variant", "Классы · агентство (вариант 3)"),
    ("activity_variant", "Деятельность · сделка (вариант 3)"),
    ("activity_lanes_variant", "Дорожки · сделка (вариант 3)"),
    ("state_variant", "Состояния объекта (вариант 3)"),
]

COL_W = 1180      # ширина колонки
COLS = 2
PAD = 26
LABEL_H = 46
TITLE_H = 96


def _font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else ["DejaVuSans.ttf"]
    for n in names:
        for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype"):
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sheet(items, title, out):
    tiles = []
    for key, cap in items:
        im = Image.open(layout.png(key)).convert("RGB")
        k = COL_W / im.width
        im = im.resize((COL_W, max(1, round(im.height * k))), Image.LANCZOS)
        tiles.append((im, cap))

    rows = (len(tiles) + COLS - 1) // COLS
    row_h = []
    for r in range(rows):
        h = max(t[0].height for t in tiles[r * COLS:(r + 1) * COLS])
        row_h.append(h + LABEL_H)

    total_h = TITLE_H + sum(row_h) + PAD * (rows + 1)
    total_w = PAD + COLS * (COL_W + PAD)
    canvas = Image.new("RGB", (total_w, total_h), "white")
    draw = ImageDraw.Draw(canvas)
    f_title = _font(40, bold=True)
    f_cap = _font(26)

    draw.text((PAD, 30), title, font=f_title, fill="black")
    y = TITLE_H
    for r in range(rows):
        for c in range(COLS):
            i = r * COLS + c
            if i >= len(tiles):
                break
            im, cap = tiles[i]
            x = PAD + c * (COL_W + PAD)
            drawer_box = (x, y, x + COL_W, y + im.height)
            canvas.paste(im, (x, y))
            draw.rectangle(drawer_box, outline=(200, 200, 200), width=2)
            draw.text((x, y + im.height + 8), cap, font=f_cap, fill=(60, 60, 60))
        y += row_h[r]

    canvas.save(out)
    print(out, canvas.size)


if __name__ == "__main__":
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    sheet(EXAMPLES, "Схемы: примеры из методических указаний",
          os.path.join(out_dir, "предпросмотр_1_примеры.png"))
    sheet(VARIANTS, "Схемы: вариант 3 «Агентство недвижимости»",
          os.path.join(out_dir, "предпросмотр_2_вариант.png"))
