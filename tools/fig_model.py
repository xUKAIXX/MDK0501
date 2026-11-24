"""Организационная диаграмма (Visio) и модель IDEF1X (логическая/физическая)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notation import *  # noqa


# ============================================================ оргструктура
def _org_box(c, x, y, w, h, title, lines=(), size=7.6, bold=True):
    c.rect(x, y, w, h)
    c.text(x + w / 2, y + h / 2 - (len(lines) * 3.2), title, size=size, bold=bold,
           wrap=18)
    for i, ln in enumerate(lines):
        c.text(x + w / 2, y + h / 2 + 2.6 + i * 3.2, ln, size=size - 1.2)
    return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2,
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "l": (x, y + h / 2), "r": (x + w, y + h / 2)}


def _tree(c, top, level1, level2=()):
    """top — руководитель; level1 — список (titles...); level2 — списки подчинённых."""
    y0, h0 = 14, 13
    # вертикаль от руководителя
    c.ax.plot([top["b"][0], top["b"][0]], [top["b"][1], y0 - 6], color=THEME_LINE, lw=0.9)
    if not level1:
        return
    xs = [b["cx"] for b in level1]
    c.ax.plot([min(xs), max(xs)], [y0 - 6, y0 - 6], color=THEME_LINE, lw=0.9)
    for b in level1:
        c.ax.plot([b["cx"], b["cx"]], [y0 - 6, b["t"][1]], color=THEME_LINE, lw=0.9)


def org_example():
    """Рисунок 3 методических указаний: оргструктура предприятия."""
    c = Canvas(150, 96)
    c.text(c.w / 2, 4, "ОРГАНИЗАЦИОННАЯ СТРУКТУРА ПРЕДПРИЯТИЯ", size=9,
           bold=True)
    gen = _org_box(c, 44, 12, 56, 13, "Генеральный директор",
                   ("ЮРКОВ Н.А.",), size=7.4)
    ur = _org_box(c, 4, 36, 40, 12, "Юрисконсульт", ("СЕРОВ П.И.",), size=7.2)
    zam = _org_box(c, 62, 36, 52, 13, "Заместитель директора\nпо экономике",
                   ("СВИРИДОВ Т.А.",), size=7.0)
    glav = _org_box(c, 52, 60, 44, 13, "Главный бухгалтер",
                    ("МИРОНОВ Л.И.",), size=7.0)
    eko = _org_box(c, 108, 60, 38, 12, "Экономист", ("МАТВЕЕВА С.К.",), size=7.0)

    c.ax.plot([gen["b"][0], gen["b"][0]], [gen["b"][1], 32], color=THEME_LINE, lw=0.9)
    c.ax.plot([ur["cx"], zam["cx"]], [32, 32], color=THEME_LINE, lw=0.9)
    for b in (ur, zam):
        c.ax.plot([b["cx"], b["cx"]], [32, b["t"][1]], color=THEME_LINE, lw=0.9)

    c.ax.plot([zam["b"][0], zam["b"][0]], [zam["b"][1], 56], color=THEME_LINE, lw=0.9)
    c.ax.plot([glav["cx"], eko["cx"]], [56, 56], color=THEME_LINE, lw=0.9)
    for b in (glav, eko):
        c.ax.plot([b["cx"], b["cx"]], [56, b["t"][1]], color=THEME_LINE, lw=0.9)

    b1 = _org_box(c, 32, 82, 34, 11, "Бухгалтер", ("АСЕЕВА М.Ю.",), size=7.0)
    b2 = _org_box(c, 70, 82, 34, 11, "Финансист", ("БОЕВ А.А.",), size=7.0)
    b3 = _org_box(c, 108, 82, 34, 11, "Аналитик", ("БАСОВА Н.Н.",), size=7.0)
    c.ax.plot([glav["b"][0], glav["b"][0]], [glav["b"][1], 78], color=THEME_LINE,
              lw=0.9)
    c.ax.plot([b1["cx"], b3["cx"]], [78, 78], color=THEME_LINE, lw=0.9)
    for b in (b1, b2, b3):
        c.ax.plot([b["cx"], b["cx"]], [78, b["t"][1]], color=THEME_LINE, lw=0.9)
    return c.save("org_example")


def org_variant():
    c = Canvas(160, 96)
    c.text(c.w / 2, 4, "Организационная структура агентства недвижимости", size=9,
           bold=True)
    gen = _org_box(c, 30, 12, 44, 13, "Директор агентства")
    it = _org_box(c, 96, 12, 52, 13, "ИТ-специалист\n(АИС, поддержка)", size=6.8)
    c.arrow([gen["r"], it["l"]], head="open", ls=(0, (3, 2)), lw=0.8)

    d1 = _org_box(c, 2, 38, 28, 13, "Отдел продаж", ("агенты",), size=7.2)
    d2 = _org_box(c, 33, 38, 28, 13, "Отдел аренды", ("агенты",), size=7.2)
    d3 = _org_box(c, 64, 38, 28, 13, "Отдел оценки\nи маркетинга", ("оценщик",), size=6.8)
    d4 = _org_box(c, 95, 38, 28, 13, "Юридический\nотдел", ("юрист",), size=6.8)
    d5 = _org_box(c, 126, 38, 30, 13, "Бухгалтерия", ("бухгалтер",), size=7.2)

    c.ax.plot([gen["b"][0], gen["b"][0]], [gen["b"][1], 34], color=THEME_LINE, lw=0.9)
    c.ax.plot([d1["cx"], d5["cx"]], [34, 34], color=THEME_LINE, lw=0.9)
    for b in (d1, d2, d3, d4, d5):
        c.ax.plot([b["cx"], b["cx"]], [34, b["t"][1]], color=THEME_LINE, lw=0.9)

    s1 = _org_box(c, 2, 68, 28, 12, "Старший агент", size=7.2)
    s2 = _org_box(c, 33, 68, 28, 12, "Агент по аренде", size=7.2)
    s3 = _org_box(c, 64, 68, 28, 12, "Специалист\nпо рекламе", size=6.8)
    s4 = _org_box(c, 95, 68, 28, 12, "Помощник\nюриста", size=6.8)

    for d, s in ((d1, s1), (d2, s2), (d3, s3), (d4, s4)):
        c.ax.plot([d["cx"], d["cx"]], [d["b"][1], s["t"][1]], color=THEME_LINE,
                  lw=0.9)

    c.text(c.w / 2, c.h - 5,
           "Сплошные линии — линейное подчинение, пунктир — обеспечивающая "
           "(штабная) функция", size=7, italic=True)
    return c.save("org_variant")


# ============================================================ IDEF1X
def _idef1x(c, x, y, w, name, rows, key_rows=1, size=7.0, row_h=4.2, head_h=6.2):
    h = head_h + row_h * len(rows) + 1.2
    c.rect(x, y, w, h)
    c.ax.plot([x, x + w], [y + head_h + row_h * key_rows, y + head_h + row_h * key_rows],
              color=THEME_LINE, lw=0.8)
    c.text(x + w / 2, y + head_h / 2, name, size=size + 1.2, bold=True, wrap=18)
    for i, r in enumerate(rows):
        c.text(x + 1.6, y + head_h + row_h * i + row_h / 2 + 0.3, r, size=size,
               ha="left")
    return {"x": x, "y": y, "w": w, "h": h,
            "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
            "cx": x + w / 2, "cy": y + h / 2}


def _link(c, pts, kind="ident", cards=(), labels=()):
    """Связь IDEF1X по ломаной; на дочернем конце — чёрный кружок."""
    ls = "-" if kind == "ident" else (0, (4, 2))
    xs, ys = zip(*pts)
    c.ax.plot(xs, ys, color=THEME_LINE, lw=0.9, ls=ls, zorder=2)
    for (x, y, dx, dy, txt) in cards:
        c.text(x + dx, y + dy, txt, size=7.2, ha="left" if dx >= 0 else "right")
    for (x, y, txt, ha) in labels:
        c.text(x, y, txt, size=6.6, italic=True, ha=ha)


def idef1x_example():
    """Рисунок 9 методических указаний: модель уровня «сущность-связь»
    для учебной системы «Курсовая работа»."""
    c = Canvas(206, 136)
    c.text(c.w / 2, 5, "Информационная модель уровня «сущность-связь» "
                       "(пример)", size=9, bold=True)

    st = _idef1x(c, 10, 14, 48, "Студент", ["№ зачётной книжки (PK)"])
    pr = _idef1x(c, 146, 14, 52, "Преподаватель", ["Табельный номер (PK)"])
    zd = _idef1x(c, 10, 54, 48, "Задание", ["Вариант задания (PK)"])
    kr = _idef1x(c, 78, 54, 56, "Курсовая работа",
                 ["№ зачётной книжки (FK)", "Вариант задания (FK)",
                  "Табельный номер (FK)"])
    pz = _idef1x(c, 146, 54, 52, "Пояснительная записка",
                 ["№ зачётной книжки (FK)"])
    mu = _idef1x(c, 10, 106, 56, "Методические указания",
                 ["Дисциплина", "Специальность"])
    pk = _idef1x(c, 78, 106, 56, "Положение о КП",
                 ["Положение о курсовом", "проектировании", "ВУЗ, год издания"])
    gr = _idef1x(c, 146, 106, 48, "График", ["Группа", "Дисциплина"])

    # 1 : N связи (воронка на дочернем конце — «много»)
    _link(c, [(st["cx"], st["b"][1]), (kr["t"][0] - 10, kr["t"][1])], "ident",
          cards=[(st["cx"] + 2, st["b"][1] + 5, 2, 0, "1"),
                 (kr["t"][0] - 13, kr["t"][1] + 5, -2, 0, "N")],
          labels=[(46, 38, "выполняет", "center")])
    _link(c, [(zd["r"][0], zd["r"][1]), (kr["l"][0], kr["l"][1] + 4)], "ident",
          cards=[(zd["r"][0] - 8, zd["r"][1] - 5, -2, 0, "1"),
                 (kr["l"][0] + 3, kr["l"][1] - 5, 2, 0, "N")],
          labels=[(69, 66, "определяет", "center")])
    _link(c, [(pr["l"][0], pr["l"][1]), (kr["t"][0] + 14, kr["t"][1])],
          "nonident",
          cards=[(pr["l"][0] + 4, pr["l"][1] - 8, 2, 0, "1"),
                 (kr["t"][0] + 17, kr["t"][1] + 5, 2, 0, "N")],
          labels=[(156, 34, "проверяет", "left")])
    _link(c, [(kr["r"][0], kr["r"][1]), (pz["l"][0], pz["l"][1])], "ident",
          cards=[(kr["r"][0] + 3, kr["r"][1] - 5, 2, 0, "1"),
                 (pz["l"][0] - 3, pz["l"][1] - 5, -2, 0, "1")],
          labels=[(143, kr["r"][1] + 14, "оформляется", "center")])
    _link(c, [(mu["t"][0], mu["t"][1]), (mu["t"][0], 96), (kr["l"][0] - 10, 96),
              (kr["l"][0] - 10, kr["b"][1])], "nonident",
          cards=[(mu["t"][0] + 3, mu["t"][1] - 5, 2, 0, "1"),
                 (kr["l"][0] - 13, kr["b"][1] + 5, -2, 0, "N")],
          labels=[(14, 92, "определяют требования", "left")])
    _link(c, [(pk["t"][0], pk["t"][1]), (pk["t"][0], kr["b"][1])], "nonident",
          cards=[(pk["t"][0] + 3, pk["t"][1] - 5, 2, 0, "1"),
                 (kr["b"][0] + 12, kr["b"][1] + 5, 3, 0, "N")],
          labels=[(pk["t"][0] + 4, 100, "организует", "left")])
    _link(c, [(gr["t"][0], gr["t"][1]), (pz["b"][0], pz["b"][1])], "nonident",
          cards=[(gr["t"][0] + 3, gr["t"][1] - 5, 2, 0, "1"),
                 (pz["b"][0] + 12, pz["b"][1] + 5, 3, 0, "N")],
          labels=[(158, 96, "определяет дату сдачи", "left")])

    c.text(c.w / 2, c.h - 3,
           "Сплошная линия — идентифицирующая связь, пунктир — "
           "неидентифицирующая", size=7, italic=True)
    return c.save("idef1x_example")


def idef1x_logical():
    c = Canvas(190, 178)
    c.text(c.w / 2, 5, "Логическая модель данных агентства недвижимости "
                       "(IDEF1X, уровень ER)", size=9, bold=True)

    kl = _idef1x(c, 4, 16, 46, "КЛИЕНТ",
                 ["ID_client (PK)", "Фамилия", "Имя", "Телефон", "E-mail"])
    za = _idef1x(c, 4, 66, 46, "ЗАЯВКА",
                 ["ID_request (PK)", "ID_client (FK)", "ID_object (FK)", "Дата",
                  "Вид заявки", "Статус"])
    po = _idef1x(c, 4, 122, 46, "ПОКАЗ",
                 ["ID_show (PK)", "ID_request (FK)", "Дата", "Результат"])

    so = _idef1x(c, 68, 16, 46, "СОБСТВЕННИК",
                 ["ID_owner (PK)", "Наименование", "ИНН", "Адрес", "Телефон"])
    ob = _idef1x(c, 68, 66, 46, "ОБЪЕКТ",
                 ["ID_object (PK)", "ID_owner (FK)", "Тип объекта", "Адрес",
                  "Площадь", "Цена", "Статус"])
    do = _idef1x(c, 68, 122, 46, "ДОГОВОР",
                 ["ID_contract (PK)", "ID_object (FK)", "ID_client (FK)",
                  "ID_staff (FK)", "Номер, дата", "Сумма", "Статус"])

    st = _idef1x(c, 132, 16, 54, "СОТРУДНИК",
                 ["ID_staff (PK)", "ФИО", "Должность", "Телефон"])
    op = _idef1x(c, 132, 122, 54, "ОПЛАТА",
                 ["ID_payment (PK)", "ID_contract (FK)", "Дата", "Сумма",
                  "Способ оплаты"])

    _link(c, [(kl["cx"], kl["b"][1]), (kl["cx"], za["t"][1])], "ident",
          cards=[(kl["cx"], kl["b"][1], 2.5, 4, "1"),
                 (za["cx"], za["t"][1], -3, -3.5, "N")],
          labels=[(kl["cx"] + 3, 52, "подаёт", "left")])
    _link(c, [(za["cx"], za["b"][1]), (za["cx"], po["t"][1])], "ident",
          cards=[(za["cx"], za["b"][1], 2.5, 4, "1"),
                 (po["cx"], po["t"][1], -3, -3.5, "N")],
          labels=[(za["cx"] + 3, 110, "сопровождается\nпоказами", "left")])
    _link(c, [(so["cx"], so["b"][1]), (so["cx"], ob["t"][1])], "ident",
          cards=[(so["cx"], so["b"][1], 2.5, 4, "1"),
                 (ob["cx"], ob["t"][1], -3, -3.5, "N")],
          labels=[(so["cx"] + 3, 52, "владеет", "left")])
    _link(c, [(ob["cx"] - 10, ob["b"][1]), (ob["cx"] - 10, do["t"][1])], "ident",
          cards=[(ob["cx"] - 7.5, ob["b"][1], -2.5, 4, "1"),
                 (do["cx"] - 13, do["t"][1], -3, -3.5, "N")],
          labels=[(ob["cx"] + 25, 113, "является предметом", "left")])
    # ЗАЯВКА ссылается на ОБЪЕКТ (неидентифицирующая связь, FK)
    _link(c, [(ob["l"][0], ob["l"][1]), (za["r"][0], za["r"][1])], "nonident",
          cards=[(ob["l"][0] - 2, ob["l"][1] - 3.5, -2.5, 0, "1"),
                 (za["r"][0] + 2, za["r"][1] - 3.5, 2.5, 0, "N")],
          labels=[(59, ob["l"][1] - 9, "заявка\nна объект", "center")])
    # СОТРУДНИК ведёт ДОГОВОР (неидентифицирующая связь по ID_staff)
    _link(c, [(st["l"][0], st["l"][1]), (128, st["l"][1]), (128, 102),
              (do["cx"] + 22, 102), (do["cx"] + 22, do["t"][1])], "nonident",
          cards=[(st["l"][0] - 2, st["l"][1] - 3.5, -2.5, 0, "1"),
                 (do["cx"] + 25, do["t"][1] - 3.5, 3, 0, "N")],
          labels=[(126, 66, "ведёт\nдоговор", "left")])
    # ДОГОВОР -> ОПЛАТА (идентифицирующая)
    _link(c, [(do["r"][0], do["r"][1]), (op["l"][0], op["l"][1])], "ident",
          cards=[(do["r"][0] + 2, do["r"][1] - 3.5, 2.5, 0, "1"),
                 (op["l"][0] - 2, op["l"][1] - 3.5, -2.5, 0, "N")],
          labels=[(123, do["r"][1] - 6, "оплачивается", "center")])

    c.text(c.w / 2, c.h - 5,
           "PK — первичный ключ, FK — внешний ключ; сплошная линия — "
           "идентифицирующая связь, пунктир — неидентифицирующая", size=7,
           italic=True)
    return c.save("idef1x_logical")


def idef1x_physical():
    c = Canvas(180, 96)
    c.text(c.w / 2, 5, "Физическая модель данных (целевая СУБД — MS Access)",
           size=9, bold=True)
    a = _idef1x(c, 6, 16, 50, "tbl_Client",
                ["ClientID  AutoNumber (PK)", "LastName  Text(50)",
                 "FirstName Text(50)", "Phone     Text(20)", "Email     Text(60)"])
    b = _idef1x(c, 108, 16, 56, "tbl_Object",
                ["ObjectID  AutoNumber (PK)", "OwnerID   Number (FK)",
                 "ObjectType Text(30)", "Address   Text(150)", "Area      Double",
                 "Price     Currency", "Status    Text(20)"])
    d = _idef1x(c, 6, 58, 50, "tbl_Request",
                ["RequestID AutoNumber (PK)", "ClientID  Number (FK)",
                 "ObjectID  Number (FK)", "ReqDate   Date/Time",
                 "Status    Text(20)"])
    e = _idef1x(c, 108, 62, 56, "tbl_Contract",
                ["ContractID AutoNumber (PK)", "ObjectID  Number (FK)",
                 "ClientID  Number (FK)", "DocDate   Date/Time", "Amount Currency"])
    c.ax.plot([a["cx"], a["cx"]], [a["b"][1], d["t"][1]], color=THEME_LINE, lw=0.9)
    c.circle(a["cx"], d["t"][1] + 1.7, 1.0, fc=THEME_LINE, ec=THEME_LINE, zorder=5)
    c.text(a["cx"] + 2.5, d["t"][1] - 3, "1 : N", size=7)
    c.ax.plot([b["cx"], b["cx"]], [b["b"][1], e["t"][1]], color=THEME_LINE, lw=0.9)
    c.circle(b["cx"], e["t"][1] + 1.7, 1.0, fc=THEME_LINE, ec=THEME_LINE, zorder=5)
    c.text(b["cx"] + 2.5, e["t"][1] - 3, "1 : N", size=7)
    c.text(c.w / 2, c.h - 4, "Типы данных назначены для целевой СУБД; связи "
                             "реализуются внешними ключами (1 : N)", size=7,
           italic=True)
    return c.save("idef1x_physical")


if __name__ == "__main__":
    for f in (org_example, org_variant, idef1x_example, idef1x_logical,
              idef1x_physical):
        print(f())
