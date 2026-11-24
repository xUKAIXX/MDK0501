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

    c.flow([e1["r"], (50, 28), (50, 36), p["l"]], label="Задание", size=7.4,
            label_at=(57, 25))
    c.flow([p["b"], (82, 62), (27, 62), (27, e1["b"][1])], head="filled")
    c.text(30, 66, "Курсовая работа", size=7.4, ha="left")
    c.flow([e2["l"], p["r"]], label="Пояснительная\nзаписка", size=7.0,
            label_at=(108, 34), label_ha="left")
    return c.save("dfd_example_context")


def dfd_example_level1():
    """DFD уровня 1 из методических указаний: процессы «Сделать расчёты»,
    «Сделать графическую часть», «Получить консультацию», накопитель
    «Методические указания», потоки «Правила оформления», «Расчёты»,
    «Графическая часть», «Пояснительная записка»."""
    c = Canvas(170, 88)
    st = dfd_store(c, 100, 6, 62, 9, "Б", "Методические указания")
    p1 = dfd_process(c, 22, 34, 40, 24, "1", "Сделать\nрасчёты")
    p2 = dfd_process(c, 88, 34, 44, 24, "2", "Сделать\nграфическую часть")
    p3 = dfd_process(c, 88, 66, 44, 18, "3", "Получить\nконсультацию")

    # входной поток от предыдущего уровня
    c.flow([(2, 44), p1["l"]], label="Подобранная\nлитература", size=6.2,
           label_at=(6, 34), label_ha="left")
    # управление: правила оформления из накопителя
    c.flow([(st["l"][0] + 4, st["b"][1]), (p1["t"][0] + 6, 20),
            (p1["t"][0] + 6, p1["t"][1])],
           label="Правила\nоформления", size=6.0, label_at=(66, 15),
           label_va="bottom")
    c.flow([(st["l"][0] + 4, st["b"][1]), p2["t"]], head="filled")
    # потоки между процессами
    c.flow([p1["r"], p2["l"]], label="Расчёты", size=6.2,
           label_at=(80, 30), label_va="bottom")
    c.flow([p2["b"], p3["t"]], label="Графическая\nчасть", size=6.0,
           label_at=(p2["b"][0] + 4, 62), label_ha="left", label_va="bottom")
    # пояснительная записка — выход
    c.flow([p3["r"], (168, p3["r"][1])], label="Пояснительная\nзаписка",
           size=6.2, label_at=(150, 78), label_ha="right", label_va="top")
    # замечания из накопителя в консультацию
    c.flow([(st["r"][0] - 6, st["b"][1]), (p3["r"][0] + 6, p3["t"][1] + 2),
            (p3["r"][0] - 2, p3["r"][1])],
           label="Замечания,\nдополнения", size=6.0, label_at=(152, 36),
           label_ha="right")
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

    c.flow([e1["r"], (p["l"][0], 40)], label="Заявка на объект",
            size=6.4, label_at=(46, 22), label_bg="#ffffff")
    c.flow([e2["r"], (p["l"][0], 54)], label="Заявка на подбор",
            size=6.4, label_at=(46, 60), label_bg="#ffffff")
    c.flow([p["r"], e3["l"]], label="Отчётность", size=6.4,
            label_at=(113, 40), label_bg="#ffffff")
    # процесс → хранилище и хранилище → процесс: обе стрелки бьют в границу
    c.flow([(p["cx"] - 6, p["b"][1]), (st["cx"] - 7, st["t"][1])],
            label="Данные объекта", size=6.2, label_at=(70, 70),
            label_bg="#ffffff")
    c.flow([(st["cx"] + 7, st["t"][1]), (p["cx"] + 6, p["b"][1])],
            label="Подборки", size=6.2, label_at=(98, 70), label_bg="#ffffff")
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
    c.flow([e1["r"], p1["l"]], label="Заявка", size=5.8, label_at=(37, 27),
            label_bg="#ffffff")
    c.flow([e2["r"], p3["l"]], label="Заявка\nна подбор", size=5.6,
            label_at=(37, 75), label_bg="#ffffff")
    # основная цепочка процессов
    c.flow([p1["r"], p2["l"]], label="Карточка\nобъекта", size=5.6,
            label_at=(94, 25), label_bg="#ffffff")
    c.flow([p3["r"], p4["l"]], label="Варианты", size=5.8, label_at=(94, 75),
            label_bg="#ffffff")
    c.flow([p4["r"], (168, p4["r"][1]), (168, p5["b"][1])],
            label="Договор, акт", size=5.6, label_at=(168, 82), label_bg="#ffffff")
    c.flow([p5["t"], e3["b"]], label="Отчёты", size=5.8, label_at=(171, 31),
            label_ha="left", label_bg="#ffffff")
    # хранилища
    c.flow([(60, p1["b"][1]), (60, d1["t"][1])], label="Объект", size=5.6,
            label_at=(63, 41), label_ha="left", label_bg="#ffffff")
    c.flow([(p2["b"][0] - 4, p2["b"][1]), (80, d1["t"][1])],
            label="Цена", size=5.6, label_at=(92, 41), label_bg="#ffffff")
    c.flow([(56, d1["b"][1]), (56, p3["t"][1])], label="Объекты", size=5.6,
            label_at=(59, 58), label_ha="left", label_bg="#ffffff")
    c.flow([(124, d2["t"][1]), (124, p2["b"][1])], label="Заявки", size=5.6,
            label_at=(127, 41), label_ha="left", label_bg="#ffffff")
    c.flow([(120, p4["t"][1]), (120, d2["b"][1])], label="Запрос", size=5.6,
            label_at=(117, 58), label_ha="right", label_bg="#ffffff")
    c.text(c.w / 2, c.h - 4, "Потоки данных согласованы с контекстной диаграммой "
                             "(балансировка)", size=7, italic=True)
    return c.save("dfd_variant_level1")


if __name__ == "__main__":
    for f in (dfd_example_context, dfd_example_level1, dfd_variant_context,
              dfd_variant_level1):
        print(f())
