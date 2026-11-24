"""DFD (нотация Гейна-Сарсона) — пример и вариант «Агентство недвижимости»."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notation import *  # noqa


def dfd_example_context():
    """Контекстная DFD из методических указаний: «Выполнить курсовую работу»
    (внешние сущности «Преподаватель» и «Студенты»)."""
    c = Canvas(150, 80)
    e1 = dfd_external(c, 10, 22, 34, 12, "1  Преподаватель")
    e2 = dfd_external(c, 106, 46, 34, 12, "2  Студенты")
    p = dfd_process(c, 66, 30, 32, 24, "1", "Выполнить\nкурсовую работу")

    c.arrow([e1["r"], (50, 28), (50, 36), p["l"]], label="Задание", size=7.4,
            label_at=(57, 25))
    c.arrow([p["b"], (82, 62), (27, 62), (27, e1["b"][1])], head="filled")
    c.text(30, 66, "Курсовая работа", size=7.4, ha="left")
    c.arrow([e2["l"], p["r"]], label="Пояснительная\nзаписка", size=7.0,
            label_at=(108, 34), label_ha="left")
    return c.save("dfd_example_context")


def dfd_example_level1():
    """Диаграмма декомпозиции DFD из методических указаний: процессы 1–3,
    накопители D1–D3, граничные потоки «Задание», «Курсовая работа»,
    «Пояснительная записка»."""
    c = Canvas(170, 86)
    p1 = dfd_process(c, 34, 28, 34, 22, "1", "Подобрать\nлитературу")
    p2 = dfd_process(c, 88, 28, 34, 22, "2", "Оформить ПЗ")
    p3 = dfd_process(c, 136, 46, 30, 20, "3", "Защитить\nкурсовую работу")
    s1 = dfd_store(c, 22, 6, 42, 9, "D1", "Список литературы")
    s2 = dfd_store(c, 84, 6, 44, 9, "D2", "Методические указания")
    s3 = dfd_store(c, 88, 70, 42, 9, "D3", "Положение о КП")

    c.arrow([s1["b"], p1["t"]], label="Литература", size=6.4,
            label_at=(22, 20), label_ha="left")
    c.arrow([s2["b"], p2["t"]])
    c.arrow([p1["r"], p2["l"]], label="Подобранная\nлитература", size=6.4,
            label_at=(78, 24))
    c.arrow([p2["r"], p3["l"]], label="Пояснительная\nзаписка", size=6.4,
            label_at=(140, 33), label_ha="left")
    c.arrow([p2["b"], s3["t"]], label="Правила\nоформления", size=6.2,
            label_at=(109, 56), label_ha="left")

    # граничные потоки, перенесённые с контекстной диаграммы
    c.arrow([(2, 34), p1["l"]], head="filled")
    c.text(4, 30, "Задание", size=6.4, ha="left")
    c.arrow([p1["l"], (2, 44)], head="filled")
    c.text(4, 48, "Курсовая работа", size=6.4, ha="left")
    c.arrow([p3["r"], (168, p3["r"][1])], head="filled")
    c.text(140, 70, "Готовая ПЗ\n(защита)", size=6.2, ha="left")
    return c.save("dfd_example_level1")


def dfd_variant_context():
    """Контекстная DFD для варианта «Агентство недвижимости»."""
    c = Canvas(160, 96)
    c.text(c.w / 2, 4, "Контекстная диаграмма DFD (уровень 0)", size=9, bold=True)
    p = dfd_process(c, 58, 32, 44, 28, "0", "Оказывать риэлторские\nуслуги")
    e1 = dfd_external(c, 2, 18, 30, 11, "Собственник\nобъекта")
    e2 = dfd_external(c, 2, 52, 30, 11, "Клиент (покупатель,\nарендатор)")
    e3 = dfd_external(c, 124, 40, 34, 11, "ФНС,\nРосстат")
    st = dfd_store(c, 60, 76, 40, 10, "D1", "База объектов и заявок")

    c.arrow([e1["r"], (p["l"][0], 40)], label="Заявка на объект",
            size=6.4, label_at=(46, 22), label_bg="white")
    c.arrow([e2["r"], (p["l"][0], 54)], label="Заявка на подбор",
            size=6.4, label_at=(46, 60), label_bg="white")
    c.arrow([p["r"], e3["l"]], label="Отчётность", size=6.4,
            label_at=(113, 40), label_bg="white")
    # процесс → хранилище и хранилище → процесс: обе стрелки бьют в границу
    c.arrow([(p["cx"] - 6, p["b"][1]), (st["cx"] - 7, st["t"][1])],
            label="Данные объекта", size=6.2, label_at=(70, 70),
            label_bg="white")
    c.arrow([(st["cx"] + 7, st["t"][1]), (p["cx"] + 6, p["b"][1])],
            label="Подборки", size=6.2, label_at=(98, 70), label_bg="white")
    return c.save("dfd_variant_context")


def dfd_variant_level1():
    """Декомпозиция A0 варианта: 5 процессов, хранилища D1 и D2."""
    c = Canvas(190, 106)
    c.text(c.w / 2, 4, "Диаграмма DFD уровня 1", size=9, bold=True)

    p1 = dfd_process(c, 46, 16, 38, 22, "1", "Принять и учесть\nобъект")
    p2 = dfd_process(c, 104, 16, 38, 22, "2", "Оценить объект")
    p3 = dfd_process(c, 46, 64, 38, 22, "3", "Организовать\nпоказы и подбор")
    p4 = dfd_process(c, 104, 64, 38, 22, "4", "Оформить сделку")
    p5 = dfd_process(c, 150, 40, 36, 22, "5", "Сдать\nотчётность")

    e1 = dfd_external(c, 2, 22, 26, 10, "Собственник")
    e2 = dfd_external(c, 2, 70, 26, 10, "Клиент")
    e3 = dfd_external(c, 151, 12, 34, 10, "ФНС, Росстат")

    d1 = dfd_store(c, 52, 45, 32, 8, "D1", "Объекты")
    d2 = dfd_store(c, 108, 45, 32, 8, "D2", "Заявки")

    # внешние сущности
    c.arrow([e1["r"], p1["l"]], label="Заявка", size=5.8, label_at=(37, 27),
            label_bg="white")
    c.arrow([e2["r"], p3["l"]], label="Заявка\nна подбор", size=5.6,
            label_at=(37, 75), label_bg="white")
    # основная цепочка процессов
    c.arrow([p1["r"], p2["l"]], label="Карточка\nобъекта", size=5.6,
            label_at=(94, 25), label_bg="white")
    c.arrow([p3["r"], p4["l"]], label="Варианты", size=5.8, label_at=(94, 75),
            label_bg="white")
    c.arrow([p4["r"], (168, p4["r"][1]), (168, p5["b"][1])],
            label="Договор, акт", size=5.6, label_at=(168, 82), label_bg="white")
    c.arrow([p5["t"], e3["b"]], label="Отчёты", size=5.8, label_at=(171, 31),
            label_ha="left", label_bg="white")
    # хранилища
    c.arrow([(60, p1["b"][1]), (60, d1["t"][1])], label="Объект", size=5.6,
            label_at=(63, 41), label_ha="left", label_bg="white")
    c.arrow([(p2["b"][0] - 4, p2["b"][1]), (80, d1["t"][1])],
            label="Цена", size=5.6, label_at=(92, 41), label_bg="white")
    c.arrow([(56, d1["b"][1]), (56, p3["t"][1])], label="Объекты", size=5.6,
            label_at=(59, 58), label_ha="left", label_bg="white")
    c.arrow([(124, d2["t"][1]), (124, p2["b"][1])], label="Заявки", size=5.6,
            label_at=(127, 41), label_ha="left", label_bg="white")
    c.arrow([(120, p4["t"][1]), (120, d2["b"][1])], label="Запрос", size=5.6,
            label_at=(117, 58), label_ha="right", label_bg="white")
    c.text(c.w / 2, c.h - 4, "Потоки данных согласованы с контекстной диаграммой "
                             "(балансировка)", size=7, italic=True)
    return c.save("dfd_variant_level1")


if __name__ == "__main__":
    for f in (dfd_example_context, dfd_example_level1, dfd_variant_context,
              dfd_variant_level1):
        print(f())
