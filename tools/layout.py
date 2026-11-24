"""Раскладка файлов по папкам практических работ.

Каждая работа живёт в своей папке ``reports/<имя отчёта>/``: рядом с DOCX
лежат его схемы — PNG (как схема выглядит) и VSDX (редактируемая схема Visio).

Модуль знает, какая схема к какой работе относится, поэтому остальные скрипты
(отрисовка, сборка DOCX, листы предпросмотра) не привязываются к путям жёстко.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")

# (папка = имя отчёта без .docx, ключи схем в этой папке)
PRACTICES = [
    ("ПР01_Классический_жизненный_цикл", []),
    ("ПР02_Анализ_предметной_области", []),
    ("ПР03-04_Разработка_технического_задания", []),
    ("ПР05_Организационная_диаграмма",
     ["org_example", "org_variant"]),
    ("ПР06-07_Функциональные_диаграммы_IDEF0",
     ["idef0_example_context", "idef0_example_a1", "idef0_variant_context",
      "idef0_variant_a1", "idef0_variant_a4"]),
    ("ПР08_Диаграмма_потоков_данных_DFD",
     ["dfd_example_context", "dfd_example_level1", "dfd_variant_context",
      "dfd_variant_level1"]),
    ("ПР09_Методология_IDEF3", ["idef3_example", "idef3_variant"]),
    ("ПР10_Логическая_модель_IDEF1X",
     ["idef1x_example", "idef1x_logical", "idef1x_physical"]),
    ("ПР12_Диаграмма_вариантов_использования",
     ["usecase_example", "usecase_variant"]),
    ("ПР13_Диаграмма_классов", ["class_example", "class_variant"]),
    ("ПР14_Диаграмма_деятельности", ["activity_example", "activity_variant"]),
    ("ПР15_Диаграмма_деятельности_с_дорожками",
     ["activity_lanes_example", "activity_lanes_variant"]),
    ("ПР16_Диаграмма_состояний", ["state_example", "state_variant"]),
    # схемы, которых нет ни в одной работе задания (диаграммы взаимодействия)
    ("Дополнительно_диаграммы_взаимодействия",
     ["sequence_example", "sequence_variant", "comm_example", "comm_variant"]),
]

_FOLDER_OF = {key: folder for folder, keys in PRACTICES for key in keys}


def folder_of(diagram):
    """Папка, в которой лежит схема (по ключу схемы)."""
    return _FOLDER_OF.get(diagram)


def practice_dir(name):
    """Путь к папке работы по имени отчёта (с .docx или без)."""
    base = name[:-5] if name.endswith(".docx") else name
    return os.path.join(REPORTS, base)


def png(diagram):
    return os.path.join(REPORTS, _FOLDER_OF[diagram], diagram + ".png")


def vsdx(diagram):
    return os.path.join(REPORTS, _FOLDER_OF[diagram], diagram + ".vsdx")


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
