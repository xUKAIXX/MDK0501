"""UML-диаграммы: варианты использования, классы, деятельность, состояния,
последовательности и кооперации. Пример из методички + вариант."""

import sys, os
import math
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notation import *  # noqa


# ==================================================== варианты использования
def _sysbox(c, x, y, w, h, name, size=8.4):
    c.rect(x, y, w, h, lw=1.0)
    c.text(x + w / 2, y + 3.6, name, size=size, bold=True)


def uc_example():
    """Пример методических указаний: система учёта заявок (акторы, шесть
    прецедентов, отношения include и extend)."""
    c = Canvas(160, 104)
    _sysbox(c, 36, 8, 88, 92, "Система учёта заявок")
    a_k = uml_actor(c, 12, 20, "Клиент")
    a_m = uml_actor(c, 12, 56, "Менеджер")
    a_i = uml_actor(c, 150, 20, "Исполнитель")
    a_a = uml_actor(c, 150, 64, "Администратор")

    uc1 = uml_usecase(c, 42, 15, 32, 11, "Создать заявку", size=7.4)
    uc2 = uml_usecase(c, 42, 30, 32, 11, "Просмотреть статус", size=6.8)
    uc3 = uml_usecase(c, 42, 45, 32, 11, "Назначить\nисполнителя", size=7.0)
    uc6 = uml_usecase(c, 88, 15, 32, 11, "Сформировать\nотчёт", size=7.2)
    uc5 = uml_usecase(c, 88, 30, 32, 11, "Закрыть заявку", size=7.2)
    uc4 = uml_usecase(c, 42, 62, 32, 11, "Обработать\nзаявку", size=7.4)
    uc8 = uml_usecase(c, 42, 82, 32, 11, "Эскалировать\nзаявку", size=7.0)
    uc7 = uml_usecase(c, 88, 82, 32, 11, "Проверить\nданные", size=7.2)

    # ассоциации «актор — прецедент»: общая шина на каждого актора
    def assoc(ap, bus, ucs):
        ys = [u[1] for u in ucs]
        c.ax.plot([ap[0], bus], [ap[1], ap[1]], color=THEME_LINE, lw=1.0, zorder=2)
        c.ax.plot([bus, bus], [min(ys + [ap[1]]), max(ys + [ap[1]])],
                  color=THEME_LINE, lw=1.0, zorder=2)
        for u in ucs:
            c.ax.plot([bus, u[0]], [u[1], u[1]], color=THEME_LINE, lw=1.0, zorder=2)

    assoc((16, 25.6), 31, [uc1["l"], uc2["l"]])
    assoc((16, 61.6), 26, [uc3["l"], uc4["l"]])
    assoc((154, 25.6), 129, [uc6["r"], uc5["r"]])
    assoc((154, 69.6), 133, [uc5["r"]])

    # include: «Обработать заявку» → «Проверить данные»
    c.arrow([(68, uc4["b"][1]), (68, 77), (104, 77), (104, uc7["t"][1])],
            head="open", ls=(0, (4, 2)), zorder=6)
    c.text(84, 74, "«include»", size=6.4, italic=True, bg="white")
    # extend: «Эскалировать заявку» → «Обработать заявку»
    c.arrow([(uc8["t"][0], uc8["t"][1]), (uc8["t"][0], uc4["b"][1])],
            head="open", ls=(0, (4, 2)), zorder=6)
    c.text(56, 79, "«extend»", size=6.2, italic=True, ha="right")
    return c.save("usecase_example")


def uc_variant():
    """Вариант 3: агентство недвижимости."""
    c = Canvas(178, 122)
    _sysbox(c, 42, 8, 92, 104, "АИС «Агентство недвижимости»")
    a_s = uml_actor(c, 14, 14, "Собственник", size=7.2)
    a_k = uml_actor(c, 14, 46, "Клиент", size=7.2)
    a_g = uml_actor(c, 14, 96, "Агент", size=7.2)
    a_b = uml_actor(c, 160, 14, "Бухгалтер", size=7.2)
    a_u = uml_actor(c, 160, 58, "Юрист", size=7.2)

    uc1 = uml_usecase(c, 46, 14, 40, 11, "Подать заявку на объект", size=6.4)
    uc2 = uml_usecase(c, 46, 30, 40, 11, "Подобрать объект", size=7.2)
    uc3 = uml_usecase(c, 46, 46, 40, 11, "Записаться на показ", size=7.0)
    uc4 = uml_usecase(c, 46, 64, 40, 11, "Отменить показ", size=7.2)
    uc8 = uml_usecase(c, 94, 14, 38, 11, "Сформировать отчёт", size=6.6)
    uc5 = uml_usecase(c, 94, 30, 38, 11, "Оформить договор", size=7.2)
    uc6 = uml_usecase(c, 94, 64, 38, 11, "Проверить документы", size=6.6)
    uc7 = uml_usecase(c, 94, 82, 38, 11, "Зарегистрировать право", size=6.0)

    def assoc(ap, bus, ucs):
        """Шина: актёр → вертикаль на bus → горизонтали в варианты."""
        ys = [u[1] for u in ucs]
        c.ax.plot([ap[0], bus], [ap[1], ap[1]], color=THEME_LINE, lw=1.0, zorder=2)
        c.ax.plot([bus, bus], [min(ys + [ap[1]]), max(ys + [ap[1]])],
                  color=THEME_LINE, lw=1.0, zorder=2)
        for u in ucs:
            c.ax.plot([bus, u[0]], [u[1], u[1]], color=THEME_LINE, lw=1.0, zorder=2)

    # слева: Собственник, Клиент, Агент
    assoc((18, uc1["l"][1]), 35, [uc1["l"]])
    assoc((18, 52), 31, [uc2["l"], uc3["l"], uc4["l"]])
    assoc((18, 102), 27, [uc4["l"]])
    # справа: Бухгалтер, Юрист
    assoc((164, uc8["r"][1]), 145, [uc8["r"]])
    assoc((164, 64), 141, [uc5["r"], uc6["r"], uc7["r"]])

    # include: «Оформить договор» → «Проверить документы»
    c.arrow([(uc5["b"][0] + 4, uc5["b"][1]), (uc5["b"][0] + 4, 57),
             (uc6["t"][0] + 4, 57), (uc6["t"][0] + 4, uc6["t"][1])],
            head="open", ls=(0, (4, 2)), zorder=6)
    c.text(uc5["b"][0] - 2, 53, "«include»", size=6.0, italic=True, ha="right")
    # extend: «Отменить показ» → «Записаться на показ»
    c.arrow([(70, uc4["t"][1]), (70, uc3["b"][1])], head="open",
            ls=(0, (4, 2)), zorder=6)
    c.text(72, 60, "«extend»", size=6.0, italic=True, ha="left")
    return c.save("usecase_variant")


# ==================================================== классы
def _iface(c, cx, cy, name, w=30, h=9):
    c.rect(cx - w / 2, cy - h / 2, w, h)
    c.text(cx, cy - 2.2, "«interface»", size=6.2)
    c.text(cx, cy + 2.2, name, size=7.6, bold=True)
    return {"l": (cx - w / 2, cy), "r": (cx + w / 2, cy),
            "t": (cx, cy - h / 2), "b": (cx, cy + h / 2), "cx": cx, "cy": cy}


def class_example():
    """Рисунок 1 методических указаний: диаграмма классов «Учёт заявок»."""
    c = Canvas(212, 130)
    c.text(c.w / 2, 4, "Диаграмма классов «Система учёта заявок»", size=9,
           bold=True)

    kl = uml_class(c, 6, 14, 56, "Клиент",
                   ["- id: int", "- ФИО: string", "- email: string"],
                   ["+ СоздатьЗаявку()", "+ ОбновитьКонтакты()"], size=7.0)
    za = uml_class(c, 78, 14, 60, "Заявка",
                   ["- номер: string", "- датаСоздания: DateTime",
                    "- статус: СтатусЗаявки", "- приоритет: int = 3"],
                   ["+ Назначить(и: Исполнитель): void",
                    "+ Закрыть(причина: string): bool", "+ Просрочена(): bool"],
                   size=6.8)
    km = uml_class(c, 152, 8, 54, "Комментарий",
                   ["- текст: string", "- дата: DateTime"], ["+ Добавить()"],
                   size=7.0)
    sr = uml_class(c, 84, 82, 48, "СрочнаяЗаявка", ["- срокЭскалации: int"],
                   ["+ Эскалировать(): void"], size=6.8)
    ka = uml_class(c, 6, 62, 54, "Категория", ["- код: string",
                                              "- название: string"],
                   ["+ Переименовать()"], size=7.0)
    isp = uml_class(c, 152, 62, 54, "Исполнитель",
                    ["- id: int", "- ФИО: string", "- должность: string"],
                    ["+ ВзятьЗаявку()"], size=7.0)
    nz = uml_class(c, 144, 104, 54, "Назначение",
                   ["- датаНазначения: DateTime", "- роль: string"], [],
                   size=6.8)

    # Заявка — Клиент: ассоциация * — 1 с ролями
    c.ax.plot([kl["r"][0], za["l"][0]], [kl["r"][1] + 4, za["l"][1] + 8],
              color=THEME_LINE, lw=1.0, zorder=1)
    c.text(kl["r"][0] + 5, kl["r"][1] + 7, "*", size=8)
    c.text(za["l"][0] - 5, za["l"][1] + 4, "1", size=8)
    c.text(kl["r"][0] + 9, kl["r"][1] + 11, "клиент", size=6.2, italic=True)
    c.text(za["l"][0] - 12, za["l"][1] + 14, "заявки", size=6.2, italic=True)

    # Заявка ◆— Комментарий: композиция 1 — *
    c.ax.plot([za["r"][0], km["l"][0]], [za["r"][1], km["l"][1]], color=THEME_LINE,
              lw=1.0, zorder=1)
    d = 8
    c.poly([(za["r"][0], za["r"][1]),
            (za["r"][0] + d / 2, za["r"][1] - 2.4),
            (za["r"][0] + d, za["r"][1]),
            (za["r"][0] + d / 2, za["r"][1] + 2.4)],
           fc=THEME_LINE, ec=THEME_LINE, zorder=5)
    c.text(za["r"][0] + 10, za["r"][1] + 4, "1", size=8)
    c.text(km["l"][0] - 5, km["l"][1] - 5, "*", size=8)
    c.text(km["l"][0] - 26, km["l"][1] + 5, "комментарии", size=6.0,
           italic=True, bg="white")

    # СрочнаяЗаявка — Заявка: обобщение
    c.arrow([(sr["t"][0], sr["t"][1]), (sr["t"][0], za["b"][1])], head="triangle")
    c.text(sr["t"][0] + 3, sr["t"][1] - 8, "«generalization»", size=6.0,
           italic=True, ha="left")

    # Заявка — Категория: ассоциация * — 1
    c.ax.plot([ka["r"][0], za["l"][0]], [ka["r"][1], za["b"][1]], color=THEME_LINE,
              lw=1.0, zorder=1)
    c.text(ka["r"][0] + 2, ka["r"][1] - 4, "1", size=8, ha="left")
    c.text(ka["r"][0] + 5, ka["r"][1] + 5, "категория", size=6.0, italic=True,
           bg="white")

    # Заявка — Исполнитель: ассоциация * — 0..1
    c.ax.plot([za["r"][0], isp["t"][0]], [za["r"][1] + 6, isp["t"][1]],
              color=THEME_LINE, lw=1.0, zorder=1)
    c.text(za["r"][0] + 2, za["r"][1] + 10, "*", size=8, ha="left")
    c.text(isp["t"][0] - 6, isp["t"][1] - 5, "0..1", size=7, ha="right",
           bg="white")
    c.text(150, 44, "исполнитель", size=6.0, italic=True, ha="left",
           bg="white")

    # Назначение — класс-ассоциация (пунктирная линия к классу «Исполнитель»)
    c.ax.plot([nz["t"][0], nz["t"][0]], [nz["t"][1], isp["b"][1]], color=THEME_LINE,
              lw=0.9, ls=(0, (3, 2)), zorder=0)
    c.text(nz["t"][0] - 3, nz["t"][1] - 5, "назначение", size=6.0, italic=True,
           ha="right", bg="white")

    c.text(c.w / 2, c.h - 2,
           "Ассоциация, композиция (комментарий не существует без заявки), "
           "обобщение, класс-ассоциация «Назначение»", size=6.6, italic=True)
    return c.save("class_example")


def class_variant():
    c = Canvas(190, 158)
    c.text(c.w / 2, 4, "Диаграмма классов «Агентство недвижимости»", size=9,
           bold=True)
    so = uml_class(c, 4, 12, 46, "Собственник",
                   ["- id: int", "- наименование: string", "- инн: string"],
                   ["+ добавитьОбъект()"])
    ob = uml_class(c, 62, 12, 48, "Объект",
                   ["- id: int", "- адрес: string", "- площадь: double",
                    "- цена: decimal", "- статус: string"], ["+ изменитьЦену()"])
    kl = uml_class(c, 126, 12, 50, "Клиент",
                   ["- id: int", "- фио: string", "- телефон: string"],
                   ["+ податьЗаявку()"])
    po = uml_class(c, 4, 62, 40, "Показ",
                   ["- id: int", "- дата: DateTime", "- результат: string"],
                   ["+ провести()"])
    za = uml_class(c, 62, 62, 48, "Заявка",
                   ["- id: int", "- дата: DateTime", "- вид: string",
                    "- статус: string"], ["+ закрыть()"])
    do = uml_class(c, 126, 62, 50, "Договор",
                   ["- номер: string", "- дата: DateTime", "- сумма: decimal"],
                   ["+ подписать()", "+ расторгнуть()"])
    sot = uml_class(c, 4, 112, 46, "Сотрудник",
                    ["# id: int", "# фио: string", "- должность: string"],
                    ["+ оформить()"])
    ag = uml_class(c, 68, 118, 40, "Агент", ["- процент: double"],
                   ["+ вестиСделку()"], size=7.2)
    op = uml_class(c, 126, 112, 50, "Оплата",
                   ["- id: int", "- дата: DateTime", "- сумма: decimal"],
                   ["+ провести()"])

    # 1. Собственник 1 — 1..* Объект
    c.ax.plot([so["r"][0], ob["l"][0]], [so["r"][1], ob["l"][1]], color=THEME_LINE,
              lw=1.0, zorder=2)
    c.text(so["r"][0] + 2, so["r"][1] - 3.4, "1", size=7, ha="left")
    c.text(ob["l"][0] - 2, ob["l"][1] - 3.4, "1..*", size=7, ha="right")

    # 2. Объект 1 —— 0..* Заявка (вертикаль)
    c.ax.plot([ob["cx"] + 8, ob["cx"] + 8], [ob["b"][1], za["t"][1]],
              color=THEME_LINE, lw=1.0, zorder=2)
    c.text(ob["cx"] + 12, ob["b"][1] + 4.5, "1", size=7, ha="left")
    c.text(za["t"][0] + 12, za["t"][1] - 4.0, "0..*", size=7, ha="left")

    # 3. Клиент 1 — 0..* Договор (вертикаль)
    c.ax.plot([kl["cx"], do["cx"]], [kl["b"][1], do["t"][1]], color=THEME_LINE,
              lw=1.0, zorder=2)
    c.text(kl["cx"] + 3, kl["b"][1] + 6, "1", size=7, ha="left")
    c.text(do["cx"] + 3, do["t"][1] - 6, "0..*", size=7, ha="left")

    # 4. Клиент 0..* — 1 Заявка (диагональ)
    c.ax.plot([kl["l"][0], 116], [kl["l"][1] + 6, kl["l"][1] + 6], color=THEME_LINE,
              lw=1.0, zorder=1)
    c.ax.plot([116, 116], [kl["l"][1] + 6, za["r"][1] + 6], color=THEME_LINE, lw=1.0,
              zorder=1)
    c.ax.plot([116, za["r"][0]], [za["r"][1] + 6, za["r"][1] + 6], color=THEME_LINE,
              lw=1.0, zorder=1)
    c.text(kl["l"][0] - 2, kl["l"][1] + 9, "1", size=7, ha="right")
    c.text(za["r"][0] + 2, za["r"][1] + 2.5, "0..*", size=7, ha="left")

    # 5. Объект ◇—— Показ (агрегация: целое — Объект)
    ax_ = ob["l"][0] + 8
    c.ax.plot([ax_, ax_], [ob["b"][1], 50], color=THEME_LINE, lw=1.0, zorder=1)
    c.ax.plot([ax_, 24], [50, 50], color=THEME_LINE, lw=1.0, zorder=1)
    c.ax.plot([24, 24], [50, po["t"][1]], color=THEME_LINE, lw=1.0, zorder=1)
    d = 8
    c.poly([(ax_, ob["b"][1] + d),
            (ax_ - 2.6, ob["b"][1] + d / 2),
            (ax_, ob["b"][1]),
            (ax_ + 2.6, ob["b"][1] + d / 2)],
           fc=THEME_FILL, ec=THEME_LINE, lw=1.0, zorder=5)
    c.text(ax_ - 7, ob["b"][1] + d + 4, "1", size=7, ha="right")
    c.text(po["t"][0] + 6, po["t"][1] - 4, "0..*", size=7, ha="left")

    # 6. Заявка 1 —— 0..* Показ
    c.ax.plot([za["l"][0], po["r"][0]], [za["l"][1], po["r"][1]], color=THEME_LINE,
              lw=1.0, zorder=1)
    c.text(za["l"][0] - 3, za["l"][1] - 4.5, "1", size=7, ha="right")
    c.text(po["r"][0] + 3, po["r"][1] - 4.5, "0..*", size=7, ha="left")

    # 7. Договор ◆—— Оплата (композиция)
    c.ax.plot([do["cx"], op["cx"]], [do["b"][1], op["t"][1]], color=THEME_LINE,
              lw=1.0, zorder=2)
    d = 8
    c.poly([(do["cx"], do["b"][1]),
            (do["cx"] - 2.6, do["b"][1] + d / 2),
            (do["cx"], do["b"][1] + d),
            (do["cx"] + 2.6, do["b"][1] + d / 2)],
           fc=THEME_LINE, ec=THEME_LINE, lw=1.0, zorder=5)
    c.text(do["cx"] + 4, do["b"][1] + d + 6, "1", size=7, ha="left")
    c.text(op["cx"] - 3, op["t"][1] - 4, "1..*", size=7, ha="right")

    # 8. Агент → Сотрудник (обобщение)
    c.arrow([ag["l"], sot["r"]], head="triangle")
    c.text((ag["l"][0] + sot["r"][0]) / 2, ag["l"][1] - 4.5, "обобщение", size=6.0,
           italic=True)

    c.text(c.w / 2, c.h - 6,
           "Ассоциации 1 : 0..*, агрегация «Объект — Показ», композиция "
           "«Договор — Оплата», обобщение «Агент — Сотрудник»", size=7, italic=True)
    return c.save("class_variant")


# ==================================================== деятельность
def _dec(c, cx, cy, w=10, h=7):
    c.diamond(cx, cy, w, h)
    return {"l": (cx - w / 2, cy), "r": (cx + w / 2, cy), "t": (cx, cy - h / 2),
            "b": (cx, cy + h / 2), "c": (cx, cy)}


def activity_example():
    """Рисунок 1 методических указаний: диаграмма деятельности «Учёт заявок»."""
    c = Canvas(120, 138)
    c.text(c.w / 2, 4, "Диаграмма деятельности для системы «Учёт заявок»",
           size=8.6, bold=True)
    s0 = uml_start(c, 52, 13)
    a1 = uml_action(c, 30, 18, 44, 10, "Принять заявку")
    d1 = _dec(c, 52, 35)
    a2 = uml_action(c, 8, 43, 34, 10, "Вернуть на доработку", size=7.6)
    f1 = uml_fork(c, 52, 60, 40, 2.4)
    a3 = uml_action(c, 10, 68, 34, 10, "Зарегистрировать заявку", size=7.0)
    a4 = uml_action(c, 60, 68, 34, 10, "Уведомить исполнителя", size=7.0)
    j1 = uml_fork(c, 52, 84, 40, 2.4)
    a5 = uml_action(c, 30, 89, 44, 10, "Выполнить заявку")
    d2 = _dec(c, 52, 105)
    a6 = uml_action(c, 8, 108, 32, 10, "Доработать заявку", size=7.4)
    a7 = uml_action(c, 58, 108, 32, 10, "Закрыть заявку", size=7.6)
    e = uml_end(c, 74, 124)

    c.arrow([s0["b"], a1["t"]])
    c.arrow([a1["b"], (52, d1["t"][1])])
    # [нет] — влево на «Вернуть на доработку», затем возврат к «Принять заявку»
    c.arrow([d1["l"], a2["t"]], head="filled")
    c.text(33, 32, "[нет]", size=6.6)
    c.arrow([a2["l"], (4, a2["l"][1]), (4, a1["l"][1]), a1["l"]],
            head="filled")
    # [да] — дальше к полосе fork
    c.arrow([d1["b"], (52, f1["t"][1])])
    c.text(57, 50, "[да]", size=6.6, ha="left")
    c.arrow([f1["l"], (27, f1["l"][1]), a3["t"]], head="none")
    c.arrow([f1["r"], (77, f1["r"][1]), a4["t"]], head="none")
    c.arrow([a3["b"], (27, j1["l"][1]), j1["l"]], head="none")
    c.arrow([a4["b"], (77, j1["r"][1]), j1["r"]], head="none")
    c.arrow([(52, j1["b"][1]), a5["t"]])
    c.arrow([a5["b"], (52, d2["t"][1])])
    c.arrow([d2["l"], (40, d2["l"][1]), (40, 107), (24, 107), (24, a6["t"][1])],
            head="filled")
    c.text(28, 100, "[да]", size=6.6)
    c.arrow([a6["l"], (4, a6["l"][1]), (4, a5["l"][1]), a5["l"]],
            head="filled")
    c.arrow([d2["r"], a7["l"]], head="filled")
    c.text(60, 100, "[нет]", size=6.6)
    c.arrow([a7["b"], (74, a7["b"][1]), (74, e["t"][1])])
    c.text(60, c.h - 4,
           "Параллельные ветви запускаются полосой fork\n"
           "и синхронизируются полосой join", size=6.6, italic=True)
    return c.save("activity_example")


def activity_variant():
    c = Canvas(168, 140)
    c.text(c.w / 2, 4, "Диаграмма деятельности «Оформление сделки с недвижимостью»",
           size=9, bold=True)
    s = uml_start(c, 62, 12)
    a1 = uml_action(c, 40, 18, 44, 9, "Принять заявку и документы", size=7.6)
    a2 = uml_action(c, 40, 32, 44, 9, "Проверить документы", size=7.6)
    d1 = _dec(c, 62, 47)
    a3 = uml_action(c, 112, 42, 44, 9, "Запросить недостающие документы", size=7.0)
    f1 = uml_fork(c, 62, 56, 40, 2.4)
    a4 = uml_action(c, 12, 64, 40, 9, "Оценить объект", size=7.6)
    a5 = uml_action(c, 72, 64, 40, 9, "Подобрать покупателя", size=7.4)
    j1 = uml_fork(c, 62, 86, 40, 2.4)
    a6 = uml_action(c, 40, 92, 44, 9, "Согласовать условия сделки", size=7.4)
    d2 = _dec(c, 62, 105)
    a7 = uml_action(c, 112, 100, 44, 9, "Уведомить об отказе", size=7.4)
    a8 = uml_action(c, 12, 114, 44, 9, "Подготовить и подписать договор", size=7.0)
    e = uml_end(c, 34, 128)

    c.arrow([s["b"], a1["t"]])
    c.arrow([a1["b"], a2["t"]])
    c.arrow([a2["b"], (62, d1["t"][1])])
    c.arrow([(d1["r"][0], d1["r"][1]), (a3["l"][0], d1["r"][1]), a3["l"]])
    c.text(78, 44, "[документы неполные]", size=6.2)
    # возврат на повторную проверку
    c.arrow([(a3["t"][0], a3["t"][1]), (a3["t"][0], 24), (86, 24), (86, a2["r"][1])])
    c.text(96, 21, "повторная проверка", size=6.0, italic=True, ha="left")
    c.arrow([d1["b"], (62, f1["t"][1])])
    c.text(30, 52, "[документы полные]", size=6.2)
    c.arrow([f1["l"], (32, f1["l"][1]), a4["t"]], head="none")
    c.arrow([f1["r"], (92, f1["r"][1]), a5["t"]], head="none")
    c.arrow([a4["b"], (32, 76), (42, 76), (42, j1["l"][1])], head="filled")
    c.arrow([a5["b"], (92, 76), (82, 76), (82, j1["r"][1])], head="filled")
    c.arrow([(62, j1["b"][1]), (62, a6["t"][1])])
    c.arrow([a6["b"], (62, d2["t"][1])])
    c.arrow([d2["l"], (6, d2["l"][1]), (6, a8["l"][1]), a8["l"]])
    c.text(8, 101, "[условия согласованы]", size=6.0, ha="left")
    c.arrow([d2["r"], a7["l"]])
    c.text(88, 107, "[отказ клиента]", size=6.0)
    c.arrow([a8["b"], (34, e["t"][1])])
    c.arrow([a7["b"], (134, 130), (38.6, 130), e["r"]])
    c.text(70, 60, "fork", size=6.0, italic=True, ha="left")
    c.text(70, 89, "join", size=6.0, italic=True, ha="left")
    return c.save("activity_variant")


# ==================================================== деятельность с дорожками
def _lane(c, x, y, w, h, title, title_w=16):
    c.rect(x, y, w, h, lw=1.0, zorder=1)
    c.ax.plot([x + title_w, x + title_w], [y, y + h], color=THEME_LINE, lw=1.0,
              zorder=3)
    c.text(x + title_w / 2, y + h / 2, title, size=7.6, bold=True, rotation=90)
    return x + title_w


def activity_lanes_example():
    """Рисунок 1 методических указаний: три дорожки, система «Учёт заявок»."""
    c = Canvas(160, 142)
    c.text(c.w / 2, 4, "Диаграмма деятельности с дорожками\n"
                       "для системы «Учёт заявок»", size=8.4, bold=True)
    lx, w = 8, 144
    lane_w = w / 3
    top, bot = 22, 134
    xs = [lx + lane_w * i for i in range(3)]
    for i, t in enumerate(("Клиент", "Менеджер", "Исполнитель")):
        c.rect(xs[i], top, lane_w, bot - top, lw=1.0, zorder=1)
        c.ax.plot([xs[i], xs[i] + lane_w], [top + 8, top + 8], color=THEME_LINE,
                  lw=0.9, zorder=4)
        c.text(xs[i] + lane_w / 2, top + 4, t, size=7.4, bold=True)

    c1, c2, c3 = xs
    s0 = uml_start(c, c1 + 23, 35)
    a1 = uml_action(c, c1 + 6, 41, 34, 9, "Создать заявку", size=6.8)
    a2 = uml_action(c, c2 + 8, 41, 34, 9, "Проверить данные", size=6.8)
    d1 = _dec(c, c2 + 25, 60)
    a3 = uml_action(c, c1 + 6, 69, 34, 9, "Исправить заявку", size=6.6)
    a4 = uml_action(c, c2 + 8, 69, 34, 9, "Назначить\nисполнителя", size=6.2)
    a5 = uml_action(c, c3 + 4, 69, 40, 9, "Обработать заявку", size=6.6)
    d2 = _dec(c, c3 + 24, 89)
    a6 = uml_action(c, c3 + 4, 95, 40, 9, "Доработать заявку", size=6.4)
    a7 = uml_action(c, c3 + 4, 109, 40, 9, "Закрыть заявку", size=6.8)
    e = uml_end(c, c3 + 24, 125)

    c.arrow([s0["b"], a1["t"]])
    c.arrow([a1["r"], a2["l"]])
    c.arrow([a2["b"], d1["t"]])
    # [есть ошибки] — в дорожку клиента, на «Исправить заявку»
    c.arrow([d1["l"], (c1 + 40, d1["l"][1]), (c1 + 40, a3["l"][1]), a3["r"]],
            head="filled")
    c.text(c2 + 2, d1["l"][1] - 5, "[есть ошибки]", size=5.8, ha="left")
    # возврат к «Создать заявку»
    c.arrow([a3["l"], (c1 + 2, a3["l"][1]), (c1 + 2, a1["l"][1]), a1["l"]],
            head="filled")
    # [данные верны] — вниз, к назначению исполнителя
    c.arrow([d1["b"], a4["t"]], head="filled")
    c.text(c2 + 27, d1["b"][1] + 2, "[данные верны]", size=5.8, ha="left")
    # передача работы исполнителю
    c.arrow([a4["r"], a5["l"]])
    c.arrow([a5["b"], d2["t"]])
    # [да] — на доработку
    c.arrow([d2["l"], (c3 + 10, d2["l"][1]), (c3 + 10, a6["t"][1])], head="filled")
    c.text(c3 + 8, d2["l"][1] - 4, "[да]", size=5.8, ha="left")
    # возврат от доработки к обработке
    c.arrow([a6["l"], (c3 + 2, a6["l"][1]), (c3 + 2, a5["l"][1]), a5["l"]],
            head="filled")
    # [нет] — закрыть заявку
    c.arrow([(c3 + 28, d2["r"][1]), (c3 + 46, d2["r"][1]),
             (c3 + 46, a7["r"][1]), a7["r"]], head="filled")
    c.text(c3 + 30, d2["r"][1] - 4, "[нет]", size=5.8, ha="left")
    c.arrow([a7["b"], (c3 + 24, a7["b"][1]), e["t"]])
    c.text(c.w / 2, c.h - 3,
           "Дорожки показывают, кто выполняет действие; переходы могут "
           "пересекать их границы", size=6.6, italic=True)
    return c.save("activity_lanes_example")


def activity_lanes_variant():
    """Вариант 3: дорожки Клиент / Агент / Юрист / Бухгалтер."""
    c = Canvas(160, 132)
    c.text(c.w / 2, 4, "Диаграмма деятельности с дорожками\n"
                       "«Сделка с недвижимостью»", size=8.6, bold=True)
    w, tw = 144, 18
    titles = ["Клиент", "Агент", "Юрист", "Бухгалтер"]
    ys = [18, 44, 78, 106]
    hs = [26, 34, 28, 20]
    for y, h, t in zip(ys, hs, titles):
        _lane(c, 8, y, w, h, t, tw)

    s = uml_start(c, 50, 23)
    a1 = uml_action(c, 32, 27, 36, 9, "Подать заявку", size=7.0)
    a2 = uml_action(c, 32, 48, 36, 9, "Принять заявку", size=7.0)
    d1 = _dec(c, 50, 66)
    a3 = uml_action(c, 100, 48, 44, 10, "Запросить документы", size=6.6)
    a4 = uml_action(c, 32, 84, 36, 9, "Оформить договор", size=6.8)
    a5 = uml_action(c, 100, 84, 44, 9, "Проверить документы", size=6.6)
    a6 = uml_action(c, 32, 112, 36, 9, "Подписать договор", size=6.8)
    a7 = uml_action(c, 100, 112, 44, 9, "Рассчитать оплату", size=6.6)
    e = uml_end(c, 50, 124)

    c.arrow([s["b"], a1["t"]])
    # передача «Клиент» → «Агент»
    c.arrow([a1["b"], (50, 44), a2["t"]])
    c.arrow([a2["b"], (50, d1["t"][1])])
    # [документов нет] → «Запросить документы» (агент) → возврат клиенту
    c.arrow([d1["r"], a3["l"]])
    c.text(76, 62, "[документов нет]", size=5.8, ha="left")
    c.arrow([a3["t"], (122, 40), (122, 22), (26, 22), (26, a1["l"][1]),
             a1["l"]], head="filled")
    c.ax.plot([8 + 18, 8 + 18], [18, 124], color=THEME_LINE, lw=1.0, zorder=6)
    c.text(28, 39, "повторно", size=5.8, italic=True, ha="left")
    # [документы есть] → «Оформить договор» (юрист)
    c.arrow([d1["b"], (50, a4["t"][1])], head="filled")
    c.text(52, 74, "[документы есть]", size=5.8, ha="left")
    # юрист проверяет документы
    c.arrow([a4["r"], a5["l"]])
    # документы → бухгалтеру
    c.arrow([a5["b"], (122, 106), (122, 112), a7["t"]], head="filled")
    # расчёт оплаты → подписание договора
    c.arrow([a7["l"], a6["r"]])
    c.arrow([a6["b"], (50, 121), e["t"]])
    c.text(c.w / 2, c.h - 2,
           "Каждое действие закреплено за одним исполнителем; переходы "
           "пересекают границы дорожек", size=6.6, italic=True)
    return c.save("activity_lanes_variant")


# ==================================================== состояния
def state_example():
    """Рисунок 1 методических указаний: жизненный цикл заявки."""
    c = Canvas(176, 126)
    c.text(c.w / 2, 4, "Диаграмма состояний заявки", size=9, bold=True)
    s0 = uml_start(c, 16, 22)
    n = uml_state(c, 10, 28, 34, 11, "Новая")
    p = uml_state(c, 66, 28, 36, 11, "На проверке", size=8.0)
    z = uml_state(c, 124, 28, 36, 11, "Назначена", size=8.0)
    w = uml_state(c, 62, 58, 88, 40, "В работе", label_top=True)
    v1 = uml_state(c, 76, 66, 38, 9, "Выполняется", size=7.4)
    v2 = uml_state(c, 76, 82, 38, 9, "На доработке", size=7.4)
    ot = uml_state(c, 10, 104, 34, 11, "Отменена", size=8.0)
    cl = uml_state(c, 124, 104, 36, 11, "Закрыта", size=8.0)
    e1 = uml_end(c, 27, 120)
    e2 = uml_end(c, 142, 120)

    c.arrow([s0["b"], (n["t"][0] - 4, n["t"][1])])
    c.arrow([n["r"], p["l"]], label="подать", size=6.6, label_at=(55, 24))
    c.arrow([p["r"], z["l"]])
    c.text(112, 18, "проверить\n[данные верны]", size=6.0)
    # [есть ошибки] — обратно в «Новую»
    c.arrow([(78, p["b"][1]), (78, 50), (27, 50), (27, n["b"][1])],
            head="filled")
    c.text(34, 53, "вернуть [есть ошибки]", size=6.0, ha="left")
    # начать → составное состояние
    c.arrow([z["b"], (z["b"][0], 46), (146, 46), (146, w["t"][1])],
            head="filled")
    c.text(148, 42, "начать", size=6.2, ha="left")
    # начальное псевдосостояние внутри составного
    c.circle(70, 70.5, 1.4, fc=THEME_LINE, ec=THEME_LINE)
    c.arrow([(71.4, 70.5), (v1["l"][0], 70.5)])
    # внутренние переходы
    c.arrow([(95, v1["b"][1]), (95, v2["t"][1])])
    c.text(97, 77.5, "доработать\n[есть замечания]", size=5.4, ha="left")
    c.arrow([(v2["r"][0], v2["r"][1]), (134, v2["r"][1]), (134, 70.5),
             (v1["r"][0], 70.5)], head="filled")
    c.text(131, 88, "исправить", size=5.6, ha="right")
    # внутренние действия составного состояния
    c.text(64, 94, "entry / уведомить исполнителя    exit / архивировать",
           size=5.6, ha="left")
    # закрыть [принято]
    c.arrow([(136, w["b"][1]), (136, cl["t"][1])])
    c.text(134, 101, "закрыть [принято]", size=5.6, ha="right")
    # отменить — из состояния «Новая»
    c.arrow([(16, n["b"][1]), (16, ot["t"][1])], head="filled")
    c.text(18, 70, "отменить", size=6.0, ha="left")
    c.arrow([ot["b"], e1["t"]])
    c.arrow([cl["b"], e2["t"]])
    c.text(c.w / 2, c.h - 2,
           "«В работе» — составное состояние с вложенными статусами",
           size=6.8, italic=True)
    return c.save("state_example")


def state_variant():
    """Вариант 3: жизненный цикл объекта недвижимости."""
    c = Canvas(190, 130)
    c.text(c.w / 2, 4, "Диаграмма состояний объекта «Объект недвижимости»",
           size=9, bold=True)
    s0 = uml_start(c, 28, 16)
    n = uml_state(c, 8, 24, 40, 11, "Новый", size=8.0)
    p = uml_state(c, 68, 24, 44, 11, "На проверке",
                  inner=["do / проверка документов"], size=7.6)
    v = uml_state(c, 132, 24, 50, 11, "В продаже / сдаётся", size=7.6)
    sn = uml_state(c, 8, 62, 40, 11, "Снят с продажи", size=7.6)
    b = uml_state(c, 132, 62, 50, 11, "Забронирован", size=7.8)
    d = uml_state(c, 56, 82, 70, 34, "Сделка", label_top=True)
    d1 = uml_state(c, 62, 90, 48, 8, "Подготовка договора", size=6.5)
    d2 = uml_state(c, 62, 104, 48, 8, "Регистрация права", size=6.5)
    r = uml_state(c, 140, 98, 44, 11, "Продан / сдан", size=7.8)
    e = uml_end(c, 162, 122)

    c.arrow([s0["b"], n["t"]])
    c.arrow([n["r"], p["l"]])
    c.text(58, 18, "внести в базу", size=6.0)
    c.arrow([p["r"], v["l"]])
    c.text(122, 16, "документы в порядке", size=6.0)
    # отклонить: «На проверке» → «Снят с продажи»
    c.arrow([(78, p["b"][1]), (78, 44), (20, 44), (20, sn["t"][1])],
            head="filled")
    c.text(76, 47, "отклонить", size=6.0, ha="right")
    # снять с продажи: «В продаже» → «Снят с продажи»
    c.arrow([(150, v["b"][1]), (150, 52), (44, 52), (44, sn["t"][1])],
            head="filled")
    c.text(100, 55, "снять с продажи", size=6.0, ha="left")
    # забронировать
    c.arrow([(157, v["b"][1]), (157, b["t"][1])], head="filled")
    c.text(159, 52, "забронировать", size=6.0, ha="left")
    # оформить сделку: «Забронирован» → составное «Сделка»
    c.arrow([b["l"], (112, b["l"][1]), (112, d["t"][1])], head="filled")
    c.text(110, 78, "оформить сделку", size=6.0, ha="right")
    # внутри составного состояния
    c.arrow([d1["b"], d2["t"]])
    c.text(112, 101, "подписать", size=5.8, ha="left")
    # «Сделка» → «Продан / сдан»
    c.arrow([d["r"], (r["l"][0], d["r"][1])], head="filled")
    c.text(133, 94, "зарегистрировать", size=5.5)
    c.arrow([(r["b"][0], r["b"][1]), (r["b"][0], 118), e["t"]])
    c.text(c.w / 2, c.h - 2,
           "«Сделка» — составное состояние: подготовка договора → "
           "регистрация права", size=6.8, italic=True)
    return c.save("state_variant")


# ==================================================== последовательности
def seq_diagram(c, objects, messages, w=150, top=18, step=7.0, title=""):
    """objects: [(x, label, is_actor)]; messages: [(from_i, to_i, text, kind,
    {alt})] где kind: sync|ret|create."""
    for (x, label, is_actor) in objects:
        if is_actor:
            uml_actor(c, x, top - 2, label)
        else:
            c.rect(x - 13, top - 8, 26, 8)
            c.text(x, top - 4, label, size=7.4)
        c.ax.plot([x, x], [top + 2, top + step * len(messages) + 12],
                  color=THEME_LINE, lw=0.7, ls=(0, (5, 3)), zorder=1)
    y = top + 8
    for (i, j, text, kind) in messages:
        x1, x2 = objects[i][0], objects[j][0]
        if kind == "ret":
            c.arrow([(x1, y), (x2, y)], head="open", ls=(0, (4, 2)))
        else:
            c.arrow([(x1, y), (x2, y)], head="filled")
        c.text((x1 + x2) / 2, y - 2.6, text, size=6.4)
        y += step
    return y


def seq_example():
    c = Canvas(160, 96)
    c.text(c.w / 2, 5, "Диаграмма последовательности «Создание и обработка заявки»",
           size=8.6, bold=True)
    objs = [(20, "Клиент", True), (60, ":Форма заявки", False),
            (100, ":Заявка", False), (140, ":Менеджер", True)]
    msgs = [(0, 1, "1: открыть()", "sync"),
            (1, 0, "2: форма", "ret"),
            (0, 1, "3: заполнить()", "sync"),
            (1, 2, "4: создать()", "sync"),
            (2, 1, "5: номер заявки", "ret"),
            (1, 0, "6: подтверждение", "ret"),
            (3, 2, "7: назначить()", "sync"),
            (2, 3, "8: статус", "ret")]
    y_end = seq_diagram(c, objs, msgs)
    # фрагмент alt
    top = 18 + 8 + 7 * len(msgs) - 12
    c.rect(34, top, 96, 12, lw=0.9, ls="-", fc="none")
    c.poly([(34, top), (44, top), (44, top + 3.5), (39, top + 5), (34, top + 3.5)],
           fc=THEME_FILL, ec=THEME_LINE, lw=0.8, zorder=4)
    c.text(39, top + 1.8, "alt", size=6.4, zorder=5)
    c.text(90, top + 4, "[данные верны] / [есть ошибки]", size=6.4)
    return c.save("sequence_example")


def seq_variant():
    c = Canvas(170, 104)
    c.text(c.w / 2, 5, "Диаграмма последовательности «Оформление договора»",
           size=8.8, bold=True)
    objs = [(20, "Клиент", True), (58, ":Агент", True), (96, ":АИС", False),
            (134, ":Договор", False), (168, ":БД", False)]
    msgs = [(0, 1, "1: подать заявку()", "sync"),
            (1, 2, "2: зарегистрировать()", "sync"),
            (2, 4, "3: сохранить()", "sync"),
            (4, 2, "4: подтверждение", "ret"),
            (2, 1, "5: номер заявки", "ret"),
            (1, 2, "6: подобрать объект()", "sync"),
            (2, 4, "7: выборка()", "sync"),
            (4, 2, "8: список объектов", "ret"),
            (1, 2, "9: оформить договор()", "sync"),
            (2, 3, "10: создать()", "sync"),
            (3, 2, "11: проект договора", "ret"),
            (2, 1, "12: договор", "ret")]
    seq_diagram(c, objs, msgs, w=190)
    return c.save("sequence_variant")


def comm_example():
    c = Canvas(150, 100)
    c.text(c.w / 2, 5, "Диаграмма кооперации «Обработка заявки»", size=9, bold=True)
    k = (24, 80)
    f = (66, 44)
    app = (112, 80)
    men = (112, 26)

    def obj(x, y, label, is_actor=False):
        if is_actor:
            uml_actor(c, x, y - 6, label)
            return {"l": (x - 6, y), "r": (x + 6, y)}
        c.rect(x - 15, y - 4.5, 30, 9)
        c.text(x, y, label, size=7.0)
        return {"l": (x - 15, y), "r": (x + 15, y), "t": (x, y - 4.5),
                "b": (x, y + 4.5), "c": (x, y)}

    o_k = obj(*k, "Клиент", True)
    o_f = obj(*f, ":Форма заявки")
    o_a = obj(*app, ":Заявка")
    o_m = obj(*men, "Менеджер", True)

    c.ax.plot([o_k["r"][0], o_f["l"][0]], [k[1], f[1]], color=THEME_LINE, lw=1)
    c.ax.plot([o_f["r"][0], o_a["l"][0]], [f[1], app[1]], color=THEME_LINE, lw=1)
    c.ax.plot([o_k["r"][0] + 2, o_m["l"][0] - 2], [k[1] + 2, men[1] - 2],
              color=THEME_LINE, lw=1, ls=(0, (4, 2)))
    c.ax.plot([o_a["l"][0], o_m["r"][0] - 4], [app[1] + 4, men[1] - 4],
              color=THEME_LINE, lw=1)

    c.text(44, 60, "1: открыть()", size=6.4, rotation=-32)
    c.text(88, 60, "2: создать()", size=6.4, rotation=32)
    c.text(44, 90, "3: подтверждение", size=6.4, rotation=12)
    c.text(120, 56, "4: назначить()", size=6.4, rotation=-40)
    c.text(70, 40, "2.1: проверить данные()", size=6.0, rotation=0)
    c.text(c.w / 2, c.h - 5,
           "Порядок сообщений задаётся десятичной нумерацией (1, 2, 2.1, 3, 4)",
           size=7, italic=True)
    return c.save("comm_example")


def comm_variant():
    c = Canvas(160, 104)
    c.text(c.w / 2, 5, "Диаграмма кооперации «Оформление договора»", size=9,
           bold=True)
    k = (22, 84)
    a = (66, 60)
    ai = (112, 84)
    dg = (112, 30)
    bd = (150, 58)

    def obox(x, y, label, w=34):
        c.rect(x - w / 2, y - 4.5, w, 9)
        c.text(x, y, label, size=7.0)
        return {"l": (x - w / 2, y), "r": (x + w / 2, y), "c": (x, y)}

    o_k = uml_actor(c, k[0], k[1] - 6, "Клиент")
    o_a = uml_actor(c, a[0], a[1] - 6, "Агент")
    o_ai = obox(*ai, ":АИС", 30)
    o_dg = obox(*dg, ":Договор", 34)
    o_bd = obox(*bd, ":БД", 22)

    c.ax.plot([k[0] + 2, a[0] - 2], [k[1] + 2, a[1] - 2], color=THEME_LINE, lw=1)
    c.ax.plot([a[0] + 6, o_ai["l"][0]], [a[1] - 2, ai[1] - 2], color=THEME_LINE, lw=1)
    c.ax.plot([a[0] + 6, o_dg["l"][0]], [a[1] + 4, dg[1] + 4], color=THEME_LINE, lw=1)
    c.ax.plot([o_ai["r"][0], o_bd["l"][0]], [ai[1], bd[1]], color=THEME_LINE, lw=1)
    c.ax.plot([o_dg["r"][0], o_bd["l"][0]], [dg[1], bd[1]], color=THEME_LINE, lw=1)

    c.text(42, 76, "1: подать заявку()", size=6.2, rotation=-22)
    c.text(90, 72, "2: зарегистрировать()", size=6.2, rotation=-16)
    c.text(132, 74, "3: сохранить()", size=6.2, rotation=-16)
    c.text(88, 42, "4: оформить договор()", size=6.2, rotation=16)
    c.text(136, 42, "5: создать()", size=6.2, rotation=-16)
    c.text(30, 52, "2.1: уведомить агента", size=6.0, rotation=-60)
    c.text(c.w / 2, c.h - 5,
           "Сообщения пронумерованы десятично; связи показывают, между какими "
           "объектами идёт обмен", size=7, italic=True)
    return c.save("comm_variant")


if __name__ == "__main__":
    for f in (uc_example, uc_variant, class_example, class_variant,
              activity_example, activity_variant, activity_lanes_example,
              activity_lanes_variant, state_example, state_variant, seq_example,
              seq_variant, comm_example, comm_variant):
        print(f())
