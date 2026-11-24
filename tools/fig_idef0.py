"""Диаграммы IDEF0 (пример из методички и вариант «Агентство недвижимости»)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notation import *  # noqa


# ---------------------------------------------------------------- helper
def idef0_chain(c, blocks, w=22, h=21, y=42, gap=11, x0=28, title="", code="",
                num="", flow_labels=(), controls=(), mechs=(), inputs=(),
                outputs=(), extra=(), block_size=7.6):
    """Ряд функциональных блоков IDEF0 с подписями дуг по нотации."""
    idef0_frame(c, code, title, num)
    xs = [x0 + i * (w + gap) for i in range(len(blocks))]
    pts = []
    for (cd, nm), x in zip(blocks, xs):
        pts.append(idef0_block(c, x, y, w, h, cd, nm, size=block_size,
                               wrap=max(9, int(w * 0.34))))

    ys = [y + h * 0.22, y + h * 0.64, y + h * 0.92][:len(inputs)]
    for (lab, yy) in zip(inputs, ys):
        c.arrow([(3, yy), (x0, yy)])
        c.text(x0 - 4, yy - 1.6, lab, size=6.0, ha="right", va="bottom", wrap=17)

    for i, lab in enumerate(flow_labels):
        a, b = pts[i]["r"], pts[i + 1]["l"]
        c.arrow([(a[0], a[1]), (b[0], b[1])])
        fit_label(c, (a[0] + b[0]) / 2, a[1] - 1.8, lab, b[0] - a[0] - 1.0,
                  size=5.4, va="bottom")

    out_y = [y + h * 0.30, y + h * 0.70][:len(outputs)]
    for lab, yy in zip(outputs, out_y):
        p = pts[-1]
        c.arrow([(p["r"][0], yy), (c.w - 3, yy)])
        fit_label(c, (p["r"][0] + c.w) / 2, yy - 2.2, lab, c.w - p["r"][0] - 6,
                  size=5.9, va="bottom")

    for i, lab in enumerate(controls):
        if not lab:
            continue
        p = pts[i]
        c.arrow([(p["ctl"][0], 6), (p["ctl"][0], y)])
        c.text(p["ctl"][0] + 2.4, 25, lab, size=5.9, ha="left", wrap=18,
               va="bottom")

    for i, lab in enumerate(mechs):
        if not lab:
            continue
        p = pts[i]
        c.arrow([(p["mech"][0], c.h - 16), (p["mech"][0], y + h)])
        c.text(p["mech"][0] + 2.4, c.h - 26, lab, size=5.9, ha="left", wrap=16,
               va="top")

    for (txt, xx, yy) in extra:
        c.text(xx, yy, txt, size=6.2, ha="left", wrap=16)
    return pts


# ---------------------------------------------------------------- пример
def idef0_example_context():
    """Таблица 2 методических указаний: контекстная диаграмма
    «Выполнить курсовую работу»."""
    c = Canvas(150, 100)
    idef0_frame(c, "А0", "Выполнить курсовую работу", "1")
    b = idef0_block(c, 42, 34, 64, 34, "0", "Выполнить курсовую\nработу", size=9)

    # входы (левая грань): Варианты заданий, График, Список литературы
    c.arrow([(2, 42), (b["l"][0], 42)], label="Варианты заданий", size=7.4,
            label_at=(21, 39), label_dy=-2.2)
    c.arrow([(2, 51), (b["l"][0], 51)], label="График консультаций\nи сроки сдачи",
            size=7.4, label_at=(21, 47), label_dy=-2.2)
    c.arrow([(2, 60), (b["l"][0], 60)], label="Список литературы", size=7.4,
            label_at=(21, 57), label_dy=-2.2)

    # управления (верхняя грань)
    c.arrow([(56, 2), (56, b["t"][1])],
            label="Методические указания", size=7.4, label_at=(57, 11),
            label_ha="left")
    c.arrow([(95, 2), (95, b["t"][1])],
            label="Положение о курсовом\nпроектировании", size=7.4,
            label_at=(96, 9), label_ha="left")

    # выходы (правая грань)
    c.arrow([(b["r"][0], 45), (148, 45)], label="Курсовая работа", size=7.4,
            label_at=(127, 41), label_dy=-2.2)
    c.arrow([(b["r"][0], 57), (148, 57)], label="Оценка за курсовую\nработу",
            size=7.4, label_at=(127, 55), label_dy=-2.2)

    # механизмы (нижняя грань)
    c.arrow([(56, b["b"][1]), (56, 88)], label="Студент", size=7.4,
            label_at=(45, 78), label_dy=-1)
    c.arrow([(95, b["b"][1]), (95, 88)], label="Преподаватель", size=7.4,
            label_at=(112, 78), label_dy=-1)
    return c.save("idef0_example_context")


def example_a1():
    """Диаграмма декомпозиции примера: семь работ (A1-A7) в линейной цепочке,
    как на рисунке методических указаний."""
    c = Canvas(430, 112)
    idef0_frame(c, "А1", "Выполнить курсовую работу", "2")

    names = ["Получить\nзадание", "Подобрать\nлитературу", "Сделать\nрасчёты",
             "Сделать\nграфическую\nчасть", "Оформить\nПЗ",
             "Получить\nконсультацию", "Защитить\nкурсовую\nработу"]
    flows = ["Задание", "Литература", "Расчёты", "Граф. часть", "ПЗ",
             "Замечания"]
    w, h, gap, x0, y0 = 32, 30, 14, 44, 32
    pts = []
    for i, nm in enumerate(names):
        pts.append(idef0_block(c, x0 + i * (w + gap), y0, w, h, str(i + 1), nm,
                               size=5.9, num_size=6.4, wrap=12))

    # входы (левая грань первой работы)
    c.arrow([(2, pts[0]["in"][1]), (pts[0]["l"][0], pts[0]["in"][1])])
    c.text(x0 - 4, pts[0]["in"][1] - 5.5, "Варианты заданий", size=5.8,
           ha="right", va="bottom")
    c.arrow([(2, pts[0]["in2"][1]), (pts[0]["l"][0], pts[0]["in2"][1])])
    c.text(x0 - 4, pts[0]["in2"][1] + 5.5, "График и сроки сдачи", size=5.8,
           ha="right", va="top")

    # управления (верхние грани работ 2, 3, 4)
    ctrls = [("Список литературы", 1), ("Методические указания", 2),
             ("Положение о КП", 3)]
    for lab, idx in ctrls:
        p = pts[idx]
        c.arrow([(p["ctl"][0], p["t"][1] - 14), (p["ctl"][0], p["t"][1])])
        c.text(p["ctl"][0], p["t"][1] - 15, lab, size=5.8, va="bottom", wrap=18)

    # механизмы (нижние грани работ 1 и 7)
    for lab, idx in (("Студент", 0), ("Преподаватель", 6)):
        p = pts[idx]
        c.arrow([(p["mech"][0], p["mech"][1] + 16), (p["mech"][0], p["mech"][1])])
        c.text(p["mech"][0], p["mech"][1] + 17, lab, size=5.8, va="top", wrap=16)

    # потоки между работами
    for i, lab in enumerate(flows):
        a, b = pts[i], pts[i + 1]
        yy = a["out"][1]
        c.arrow([(a["r"][0], yy), (b["in2"][0], yy),
                 (b["in2"][0], b["in2"][1])])
        c.text((a["r"][0] + b["in2"][0]) / 2, yy - 2.4, lab, size=5.2, wrap=10,
               va="bottom", rotation=90)

    # выходы (правая грань последней работы)
    c.arrow([(pts[-1]["r"][0], pts[-1]["out"][1]), (c.w - 2, pts[-1]["out"][1])])
    c.text(pts[-1]["r"][0] + 2, pts[-1]["out"][1] - 2.2, "Курсовая работа",
           size=5.8, ha="left", va="bottom", wrap=16)
    c.arrow([(pts[-1]["r"][0], pts[-1]["out2"][1]), (c.w - 2, pts[-1]["out2"][1])])
    c.text(pts[-1]["r"][0] + 2, pts[-1]["out2"][1] + 2.2,
           "Оценка за курсовую работу", size=5.8, ha="left", va="top", wrap=16)
    return c.save("idef0_example_a1")


# ---------------------------------------------------------------- вариант
def idef0_variant_context():
    c = Canvas(150, 100)
    idef0_frame(c, "А0", "Деятельность агентства недвижимости", "1")
    b = idef0_block(c, 45, 34, 62, 32, "0",
                    "Оказывать риэлторские услуги\n(агентство недвижимости)",
                    size=8.5)
    c.arrow([(2, 44), b["in"]], label="Заявки клиентов (собственников,\n"
                                      "арендаторов, покупателей)",
            size=7.2, label_at=(23, 38), label_dy=-2)
    c.arrow([(2, 56), b["in2"]], label="Оплата услуг", size=7.5,
            label_at=(18, 55), label_dy=-2)
    c.arrow([(55, 2), b["ctl"]], label="Законодательство РФ\n(№ 218-ФЗ, ГК РФ)",
            size=7.2, label_at=(53, 11))
    c.arrow([(100, 2), b["ctl2"]],
            label="Договоры с собственниками,\nтарифы агентства", size=7.2,
            label_at=(103, 10))
    c.arrow([b["out"], (148, 44)],
            label="Права собственности\nоформлены, объект сдан/продан",
            size=7.2, label_at=(126, 37), label_dy=-2)
    c.arrow([b["out2"], (148, 58)],
            label="Отчётность в ФНС\nи Росстат, налоги", size=7.2,
            label_at=(127, 63))
    c.arrow([b["mech"], (58, 88)], label="Агенты по недвижимости,\nюрист",
            size=7.2, label_at=(44, 76))
    c.arrow([b["mech2"], (100, 88)], label="АИС «Агентство»,\nбаза объектов, ПК",
            size=7.2, label_at=(116, 76))
    return c.save("idef0_variant_context")


def variant_a1():
    c = Canvas(240, 100)
    idef0_chain(
        c,
        blocks=[("1", "Принять и учесть объект"), ("2", "Оценить объект"),
                ("3", "Организовать показы и подбор"),
                ("4", "Оформить сделку"), ("5", "Сдать отчётность")],
        w=21, h=21, y=40, gap=17, x0=26,
        title="Деятельность агентства недвижимости", code="А1", num="2",
        inputs=["Заявка собственника", "Документы на объект"],
        flow_labels=["Карточка", "Отчёт об оценке", "Вариант", "Договор"],
        controls=["Договор с собственником", "Методика оценки, рыночные данные",
                  "Прайс-лист, реклама", "ГК РФ, 218-ФЗ", "НК РФ, тарифы"],
        mechs=["Агент", "Оценщик, юрист", "Агент, АИС «Агентство»",
               "Юрист, нотариус", "Бухгалтер"],
        outputs=["Объект продан/сдан, право\nсобственности зарегистрировано",
                 "Отчётность в ФНС и Росстат"],
    )
    return c.save("idef0_variant_a1")


def variant_a4():
    """Декомпозиция работы 4 «Оформить сделку» — третий уровень модели."""
    c = Canvas(190, 96)
    idef0_chain(
        c,
        blocks=[("1", "Подготовить проект\nдоговора"),
                ("2", "Провести и подписать\nдоговор"),
                ("3", "Зарегистрировать\nправо собственности")],
        w=34, h=24, y=38, gap=16, x0=24,
        title="Деятельность агентства недвижимости", code="А4", num="3",
        inputs=["Согласованные условия", "Документы объекта"],
        flow_labels=["Проект договора", "Подписанный договор"],
        controls=["Шаблон договора", "ГК РФ, 218-ФЗ", "Регламент Росреестра"],
        mechs=["Юрист", "Агент, клиент", "Юрист, МФЦ"],
        outputs=["Выписка ЕГРН", "Акт приёма-передачи"],
    )
    return c.save("idef0_variant_a4")


if __name__ == "__main__":
    for f in (idef0_example_context, example_a1, idef0_variant_context,
              variant_a1, variant_a4):
        print(f())
