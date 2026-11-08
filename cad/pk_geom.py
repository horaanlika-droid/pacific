# -*- coding: utf-8 -*-
"""
ПАСИФИК КИТ / PACIFIC KIT  —  параметрическая модель мобильной барной станции.
Габарит 900 x 600 x 1050, 8 элементов, плоский чехол, сборка без инструмента.

Модуль содержит только геометрию: контуры деталей в развёртке, вырезы, линии гиба.
Единицы: миллиметры.
"""
import math

# ---------------------------------------------------------------- габариты
W, D, H = 900.0, 600.0, 1050.0          # ширина / глубина / высота
T = 1.2                                  # основная толщина AISI 304 (рев. D: жёсткость — рёбрами, не толщиной)
RIB_H = 15.0                             # высота ребра жёсткости (гиб)
RIB_W = 18.0                             # ширина ребра (расстояние между линиями гиба)
T_FR = 1.2                               # фасадные блоки
T_GR = 1.0                               # перфорированная решётка

SIDE_TOP = 1020.0                        # верх передней стойки боковины (под лоток выдачи)
WORK_H = 850.0                           # высота рабочей поверхности (уровень бедра, -200 от борта)
TOP_DOWN = 30.0                          # глубина отбортовки столешницы
WORK_TOP = WORK_H - TOP_DOWN             # 820.0 — опорная полка рабочей зоны (низ столешницы)
DRIP_D = 140.0                           # глубина зоны выдачи
TOP_D = D - DRIP_D                       # 460 — глубина рабочей зоны
PANEL_H, PANEL_GAP, PANEL_BOT = 334.0, 3.0, 12.0   # фасад: 3 x 334 + 2 x 3 = 1008
SIDE_DEPTH = D - T_FR                    # 598.8 — стенка утоплена за фасадом

# развёртки гибов (K = 0.33, R внутр. = 1.0)
def _dev(t, flange, r=1.0, k=0.33):
    ba = (math.pi / 2.0) * (r + k * t)
    bd = 2.0 * (r + t) - ba
    return flange - bd, bd

DEV30, BD15 = _dev(T, 30.0)      # 27.35
DEV40, _ = _dev(T, 40.0)         # 37.35
DEV15, _ = _dev(T, 15.0)         # 12.35
DEV25, BD12 = _dev(T_FR, 25.0, r=0.8)   # 22.88
DEV20, _ = _dev(T_FR, 20.0, r=0.8)      # 17.88
DEV20_10, BD10 = _dev(T_GR, 20.0, r=0.6)  # 17.9
DEV12, _ = _dev(T_GR, 12.0, r=0.6)

RELIEF = 4.0    # радиус технологических отверстий в углах гиба


# ---------------------------------------------------------------- примитивы
def rrect_pts(x0, y0, w, h, r=0.0, seg=8):
    """Скруглённый прямоугольник, против часовой стрелки."""
    if r <= 0:
        return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    pts = []
    cs = [(x0 + w - r, y0 + r, -90), (x0 + w - r, y0 + h - r, 0),
          (x0 + r, y0 + h - r, 90), (x0 + r, y0 + r, 180)]
    for cx, cy, a0 in cs:
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle_pts(cx, cy, r, seg=32):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def obround_pts(cx, cy, w, h):
    """Продолговатое отверстие w x h (любая ориентация)."""
    r = min(w, h) / 2.0
    pts = []
    if w >= h:
        for i in range(9):
            a = math.radians(-90 + 180 * i / 8)
            pts.append((cx + w / 2 - r + r * math.cos(a), cy + r * math.sin(a)))
        for i in range(9):
            a = math.radians(90 + 180 * i / 8)
            pts.append((cx - w / 2 + r + r * math.cos(a), cy + r * math.sin(a)))
    else:
        for i in range(9):
            a = math.radians(0 + 180 * i / 8)
            pts.append((cx + r * math.cos(a), cy + h / 2 - r + r * math.sin(a)))
        for i in range(9):
            a = math.radians(180 + 180 * i / 8)
            pts.append((cx + r * math.cos(a), cy - h / 2 + r + r * math.sin(a)))
    return pts


def cross_outline(x0, y0, plate_w, plate_h, left, right, bottom, top):
    """Крестовидный контур развёртки: пластина + отбортовки по 4 сторонам.

    Возвращает внешний контур (CCW) и список угловых вырезов.
    """
    x1, x2 = x0 + left, x0 + left + plate_w
    x3 = x2 + right
    y1, y2 = y0 + bottom, y0 + bottom + plate_h
    y3 = y2 + top
    # против часовой стрелки, начиная с левого нижнего угла нижней отбортовки
    return [(x1, y0), (x2, y0), (x2, y1), (x3, y1), (x3, y2), (x2, y2),
            (x2, y3), (x1, y3), (x1, y2), (x0, y2), (x0, y1), (x1, y1)]


class Part(object):
    def __init__(self, code, name, mat, t, qty, flat_w, flat_h, outline,
                 cuts=None, bends=None, notes=None, holes_r=None, dens=7.93):
        self.code, self.name, self.mat, self.t, self.qty = code, name, mat, t, qty
        self.dens = dens
        self.flat_w, self.flat_h = flat_w, flat_h
        self.outline = outline
        self.cuts = cuts or []       # dict(type, ...) — контуры вырезов
        self.bends = bends or []     # dict(p1, p2, ang, note)
        self.notes = notes or []
        self.holes_r = holes_r or []

    def area(self):
        """Площадь развёртки за вычетом вырезов, м2."""
        a = abs(_poly_area(self.outline))
        for c in self.cuts:
            if c['type'] == 'circle':
                a -= math.pi * c['r'] ** 2
            elif c['type'] == 'poly':
                a -= abs(_poly_area(c['pts']))
        return a / 1e6

    def mass(self):
        return self.area() * self.t * self.dens   # кг

    def cuts_polys(self):
        out = []
        for c in self.cuts:
            if c['type'] == 'circle':
                out.append(circle_pts(c['cx'], c['cy'], c['r']))
            elif c['type'] == 'poly':
                out.append(c['pts'])
        return out


def _poly_area(p):
    s = 0.0
    for i in range(len(p)):
        x1, y1 = p[i]
        x2, y2 = p[(i + 1) % len(p)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


# ================================================================ E1 / E2
#  Боковая стенка ступенчатая. Развёртка: X = глубина, Y = высота.
#  Передняя стойка 140 x 1020 (под фасад и лоток выдачи 1050),
#  рабочая часть 460 x 820 (под столешницу на уровне бедра 850).
#  Отбортовки: перед 30 (с пазами), зад 30, верх 40 (двухуровневая), низ 15.
SW = DEV30 + SIDE_DEPTH + DEV30          # 653.5
SH = DEV15 + SIDE_TOP + DEV40            # 1069.7
PL_X = DEV30                              # 27.35 — левая кромка пластины в развёртке
TOPY = DRIP_D                             # 140.0 — сдвиг вырезов E7 в станции по Y
PL_Y = DEV15                              # 12.35
STEP_X = PL_X + (DRIP_D - T_FR)           # 166.15 — граница уступа 1020 -> 820


def side_wall(mirror=False):
    x_r = PL_X + SIDE_DEPTH
    y_hi = PL_Y + SIDE_TOP
    y_lo = PL_Y + WORK_TOP
    outline = [
        (PL_X, 0), (x_r, 0), (x_r, PL_Y),
        (SW, PL_Y), (SW, y_lo), (x_r, y_lo),
        (x_r, y_lo + DEV40), (STEP_X, y_lo + DEV40),
        (STEP_X, y_hi), (STEP_X, SH), (PL_X, SH),
        (PL_X, y_hi), (0, y_hi), (0, PL_Y), (PL_X, PL_Y),
    ]
    if mirror:
        outline = [(SW - x, y) for (x, y) in outline][::-1]

    cuts, bends = [], []
    # пазы-«замочные скважины» под крючки фасадных блоков — в передней отбортовке
    hook_z = []
    for i in range(3):
        zb = PANEL_BOT + i * (PANEL_H + PANEL_GAP)
        hook_z += [zb + 92.0, zb + 246.0]
    for z in hook_z:
        cy = PL_Y + z
        cuts.append(dict(type='circle', cx=13.5, cy=cy, r=6.5))
        cuts.append(dict(type='poly', pts=obround_pts(13.5, cy + 13.0, 9.0, 13.0 + 12.0)))
    # Опорная полка рабочей зоны — без крепёжных отверстий; столешница садится
    # в направляющий зазор и фиксируется геометрией загнутых кромок.
    # вентиляционные просечки в задней отбортовке (3 шт., в пределах высоты 820)
    for z in (220.0, 410.0, 600.0):
        cuts.append(dict(type='poly', pts=obround_pts(x_r + DEV30 / 2,
                                                      PL_Y + z, 9.0, 70.0)))
    # технологические отверстия в углах гиба
    for (x, y) in [(PL_X, PL_Y), (x_r, PL_Y),
                   (PL_X, y_hi), (STEP_X, y_lo), (x_r, y_lo)]:
        cuts.append(dict(type='circle', cx=x, cy=y, r=RELIEF / 2))
    # линии гиба
    bends = [
        dict(p1=(PL_X, PL_Y), p2=(PL_X, y_hi), ang=90, note='передняя отбортовка 30 вверх'),
        dict(p1=(x_r, PL_Y), p2=(x_r, y_lo), ang=90, note='задняя отбортовка 30'),
        dict(p1=(PL_X, y_hi), p2=(STEP_X, y_hi), ang=90, note='верхняя полка 40 (зона выдачи 1020)'),
        dict(p1=(STEP_X, y_lo), p2=(x_r, y_lo), ang=90, note='опорная полка 40 (рабочая зона 820)'),
        dict(p1=(PL_X, PL_Y), p2=(x_r, PL_Y), ang=90, note='нижняя отбортовка 15'),
    ]
    # ребро жёсткости: два гиба на высоте ~520 мм (вниз внутрь станции, 15 мм)
    yh = PL_Y + 520.0
    bends += [dict(p1=(PL_X, yh), p2=(x_r, yh), ang=90, note='ребро жёсткости, гиб внутрь 15'),
              dict(p1=(PL_X, yh + RIB_W), p2=(x_r, yh + RIB_W), ang=90, note='ребро жёсткости, гиб внутрь 15')]
    if mirror:
        def _mx(p):
            return (SW - p[0], p[1])
        cuts = [dict(type='circle', cx=SW - c['cx'], cy=c['cy'], r=c['r'])
                if c['type'] == 'circle' else
                dict(type='poly', pts=[_mx(q) for q in c['pts']][::-1]) for c in cuts]
        bends = [dict(p1=_mx(b['p1']), p2=_mx(b['p2']), ang=b['ang'], note=b['note'])
                 for b in bends]
    notes = ['Отбортовки — внутрь станции.',
             'Ступенчатый профиль: передняя стойка 1020 мм (под выдачу 1050), рабочая зона 820 мм (под столешницу 850).',
             'Рабочая полка 820 мм — цельный опорный фланец; крепёжные отверстия не предусмотрены.']
    p = Part('E1' if not mirror else 'E2',
             'Стенка боковая левая' if not mirror else 'Стенка боковая правая',
             'AISI 304, шлиф. Scotch-Brite', T, 1, SW, SH, outline, cuts, bends, notes)
    p.mirror = mirror
    return p


# ================================================================ E3 / E4 / E5
PH_FLAT = PANEL_H + DEV25 + DEV20          # 374.75
PU_FLAT = DEV20 + PANEL_H + DEV25          # 374.75

# крючки-язычки на торцах фасада (выполняются просечкой с отгибом)
HOOK_X = [18.0, 862.0]        # левый торец 18..38, правый 862..882
HOOK_W, HOOK_H = 20.0, 11.0


def front_panel(idx):
    outline = [(0, 0), (W, 0), (W, PU_FLAT), (0, PU_FLAT)]
    cuts, bends = [], []
    # просечные крючки: U-образные надрезы (открытые контуры)
    hooks = []
    for x in HOOK_X:
        for z in (86.0, 250.0):
            hooks.append([(x, DEV20 + z), (x + HOOK_W, DEV20 + z),
                          (x + HOOK_W, DEV20 + z + HOOK_H), (x, DEV20 + z + HOOK_H)])
    # верхняя отбортовка: 2 паза под шипы блока выше
    if idx < 3:
        for x in (230.0, 670.0):
            cuts.append(dict(type='poly', pts=obround_pts(x, DEV20 + PANEL_H + DEV25 / 2, 24, 10)))
    else:
        for x in (150.0, 750.0):
            cuts.append(dict(type='poly', pts=obround_pts(x, DEV20 + PANEL_H + DEV25 / 2, 20, 10)))
    # нижняя отбортовка: 2 шипа (просечка) — на блоке выше
    tabs = []
    if idx > 1:
        for x in (230.0, 670.0):
            tabs.append([(x, 2.0), (x + 20.0, 2.0), (x + 20.0, DEV20 - 2.0), (x, DEV20 - 2.0)])
    bends = [dict(p1=(0, DEV20), p2=(W, DEV20), ang=90, note='низ 20 внутрь'),
             dict(p1=(0, DEV20 + PANEL_H), p2=(W, DEV20 + PANEL_H), ang=90,
                  note='верх 25 внутрь')]
    notes = ['Торцевые крючки — 4 шт., отгиб 90° внутрь, зацепление в пазы боковины (ход 8 мм).']
    p = Part('E%d' % (idx + 2), ['Фасадный блок нижний', 'Фасадный блок средний',
                                 'Фасадный блок верхний'][idx - 1],
             'AISI 304, шлиф. Scotch-Brite', T_FR, 1, W, PU_FLAT, outline, cuts, bends, notes)
    p.hooks = hooks
    p.tabs = tabs
    p.idx = idx
    return p


# ================================================================ E6 зона выдачи
#  Лоток-каплеуловитель: корыто 900 x 140 x 22, перфорированное дно, борт 8 мм
#  борт лотка — верхняя плоскость бара 1050, рабочая поверхность опущена до 850 (на уровень бедра).
TRAY_WALL = 22.0                      # высота стенок корыта
DEV22, _ = _dev(T_GR, TRAY_WALL, r=0.6)          # 19.35
DEV12T, _ = _dev(T_GR, 12.0, r=0.6)              # 9.35 — отгиб-крюк
TRAY_FLAT_H = DEV12T + DEV22 + DRIP_D + DEV22    # 188.05
TRAY_Y_TOP0 = DEV12T + DEV22                     # 28.7
TRAY_Y_TOP1 = TRAY_Y_TOP0 + DRIP_D               # 168.7
TRAY_RIM = 1042.0                                # верх стенок
TRAY_BOT = 1020.0                                # дно (перфорация)

# Перфорация 40 x 3 с центральным негативным логотипом «ПАСИФИК ТУРБО».
# Наклонная скорописная надпись дополнена тремя скоростными штрихами.
SPORT_GLYPHS = {
    'П': ('11111','10001','10001','10001','10001','10001','10001'),
    'А': ('01110','10001','10001','11111','10001','10001','10001'),
    'С': ('01111','10000','10000','10000','10000','10000','01111'),
    'И': ('10001','10011','10101','10101','11001','10001','10001'),
    'Ф': ('00100','11111','10101','10101','11111','00100','00100'),
    'К': ('10001','10010','10100','11000','10100','10010','10001'),
    'Т': ('11111','00100','00100','00100','00100','00100','00100'),
    'У': ('10001','10001','01010','00100','00100','01000','10000'),
    'Р': ('11110','10001','10001','11110','10100','10010','10001'),
    'Б': ('11111','10000','10000','11110','10001','10001','11110'),
    'О': ('01110','10001','10001','10001','10001','10001','01110'),
}
LOGO_CELL, LOGO_GAP, LOGO_SHEAR = 3.0, 0.6, 0.24
LOGO_WORD = 'ПАСИФИК ТУРБО'
LOGO_W = (sum(3 if ch == ' ' else 6 for ch in LOGO_WORD) - 1) * (LOGO_CELL + LOGO_GAP)
LOGO_X0 = (W - LOGO_W) / 2.0
LOGO_Y0 = (TRAY_FLAT_H - 7 * LOGO_CELL) / 2.0
LOGO_BOX = (LOGO_X0 - 5.0, LOGO_Y0 - 2.0,
            LOGO_X0 + LOGO_W + 5.0, LOGO_Y0 + 7 * LOGO_CELL + 2.0)


def logo_cuts():
    """Closed laser-cut pixels forming italic Cyrillic branding."""
    cuts, cursor = [], 0.0
    cell = LOGO_CELL
    for ch in LOGO_WORD:
        if ch == ' ':
            cursor += 3 * (cell + LOGO_GAP)
            continue
        for row, glyph_row in enumerate(SPORT_GLYPHS[ch]):
            for col, bit in enumerate(glyph_row):
                if bit != '1':
                    continue
                x = LOGO_X0 + cursor + col * (cell + LOGO_GAP) + LOGO_SHEAR * (6 - row)
                y = LOGO_Y0 + (6 - row) * (cell + LOGO_GAP)
                cuts.append(dict(type='poly', name='логотип ПАСИФИК ТУРБО',
                                 pts=[(x, y), (x + cell, y),
                                      (x + cell, y + cell), (x, y + cell)]))
        cursor += 6 * (cell + LOGO_GAP)
    for i in range(3):
        x = LOGO_X0 - 13.0 + i * 3.6
        y = TRAY_FLAT_H / 2.0 + (i - 1) * 4.2
        cuts.append(dict(type='poly', name='скоростные штрихи логотипа',
                         pts=obround_pts(x + 1.7, y, 5.0, 1.5)))
    return cuts


# Пять рядов пазов; центр освобождён для логотипа.
PERF = []
for r in range(5):
    yy = TRAY_Y_TOP0 + 14.0 + r * 27.0
    off = 0.0 if r % 2 == 0 else 23.0
    x = 24.0 + off
    while x + 40.0 <= W - 18.0:
        if not (LOGO_BOX[0] < x + 20.0 < LOGO_BOX[2] and
                LOGO_BOX[1] < yy < LOGO_BOX[3]):
            PERF.append((x, yy))
        x += 46.0


def drip_tray():
    outline = [(0, 0), (W, 0), (W, TRAY_FLAT_H), (0, TRAY_FLAT_H)]
    cuts, bends = [], []
    for (x, y) in PERF:
        cuts.append(dict(type='poly', pts=obround_pts(x + 20.0, y, 40.0, 3.0)))
    cuts.extend(logo_cuts())
    # пальцевые вырезы для съёма лотка
    for x in (96.0, 764.0):
        cuts.append(dict(type='poly', pts=obround_pts(x + 40.0, TRAY_Y_TOP0 + 70.0, 80.0, 16.0)))
    # дренаж Ø20 в правом торце (в дне)
    cuts.append(dict(type='circle', cx=W - 26.0, cy=6.0, r=5.0))
    # отгиб-крюк: оставляем два языка 25 мм, остальное вырезаем
    for (x0, x1) in ((0.0, 218.0), (243.0, 658.0), (683.0, W)):
        cuts.append(dict(type='poly', pts=[(x0, TRAY_Y_TOP0 - 0.1), (x1, TRAY_Y_TOP0 - 0.1),
                                          (x1, -0.1), (x0, -0.1)]))
    bends = [
        dict(p1=(0, DEV12T), p2=(W, DEV12T), ang=90, note='крюк 12 (языки 2 шт.)'),
        dict(p1=(0, DEV12T + DEV22), p2=(W, DEV12T + DEV22), ang=90, note='задняя стенка 22'),
        dict(p1=(0, TRAY_Y_TOP1), p2=(W, TRAY_Y_TOP1), ang=90, note='передняя стенка 22'),
    ]
    notes = ['Цельная деталь из листа AISI 304: корыто сформировано гибкой; дренажный узел уточнить под выбранную ёмкость.',
             'Перфорация 40x3 и сквозной логотип «ПАСИФИК ТУРБО» в стиле советской спортивной эмблемы.',
             'Уклон дна формуется гибкой; сварка и крепёж для сборки стойки не предусмотрены.']
    p = Part('E6', 'Зона выдачи: перфорированный лоток', 'AISI 304, перфорация', T_GR, 1,
             W, TRAY_FLAT_H, outline, cuts, bends, notes)
    return p


# ================================================================ E7 столешница
TW_FLAT = W + 2 * DEV30                  # 954.7
TH_FLAT = TOP_D + 2 * DEV30              # 514.7

# Вырезы в координатах сборки: малые ёмкости + большая GN 1/2 как мойка.
GN_X0, GN_Y0, GN_W, GN_H, GN_R, GN_STEP, GN_N = 48, 55, 90, 160, 8, 108, 4
CUT_GNS = [dict(x=GN_X0 + i * GN_STEP, y=GN_Y0, w=GN_W, h=GN_H, r=GN_R)
           for i in range(GN_N)]
# Большая GN 1/2 имеет верхнюю рамку около 325 x 265; отверстие меньше, чтобы рамка опиралась на столешницу.
CUT_SINK = dict(x=535, y=55, w=300, h=240, r=12)
CUT_SINKS = [CUT_SINK]
# Кран убран из проекта: отверстия под фитинг Ø8 нет.


def _f(x, y):
    """координаты сборки столешницы -> развёртка"""
    return DEV30 + x, DEV30 + y


def worktop():
    outline = cross_outline(0, 0, W, TOP_D, DEV30, DEV30, DEV30, DEV30)
    cuts, bends = [], []
    for i, g in enumerate(CUT_GNS, 1):
        x, y = _f(g['x'], g['y'])
        cuts.append(dict(type='poly', name='Отсек GN 1/9 #%d 90x160 R8' % i,
                         pts=rrect_pts(x, y, g['w'], g['h'], g['r'], 6)))
    for i, s in enumerate(CUT_SINKS, 1):
        x, y = _f(s['x'], s['y'])
        cuts.append(dict(type='poly', name='Посадочное отверстие под GN 1/2: 300x240 R12',
                         pts=rrect_pts(x, y, s['w'], s['h'], s['r'], 6)))
    # Ненужные отверстия ринсера, кабельного ввода, коммуникаций и крепежа удалены.
    # технологические отверстия в углах гиба
    for (cx, cy) in [(0, 0), (W, 0), (0, TOP_D), (W, TOP_D)]:
        x, y = _f(cx, cy)
        cuts.append(dict(type='circle', cx=x, cy=y, r=RELIEF / 2))
    # пазы в передней отбортовке под крюки лотка E6
    for cx in (230.0, 670.0):
        cuts.append(dict(type='poly', name='крюк лотка',
                         pts=obround_pts(DEV30 + cx, DEV30 / 2 + 3.0, 26, 11)))
    # ребра жёсткости под столешницей (вниз 15 мм), две полосы на участках без перегородки
    ribs = []
    for (xa, xb) in ((0.0, SEP_X - 28.0), (SEP_X + 28.0, W)):
        for yy in (320.0, 320.0 + RIB_W):
            ribs.append(dict(p1=(DEV30 + xa, DEV30 + yy), p2=(DEV30 + xb, DEV30 + yy), ang=90,
                             note='ребро жёсткости столешницы, гиб вниз 15'))
    bends = [
        dict(p1=(DEV30, DEV30), p2=(DEV30 + W, DEV30), ang=90, note='передняя отбортовка 30'),
        dict(p1=(DEV30, DEV30 + TOP_D), p2=(DEV30 + W, DEV30 + TOP_D), ang=90, note='задняя отбортовка 30'),
        dict(p1=(DEV30, DEV30), p2=(DEV30, DEV30 + TOP_D), ang=90, note='левая отбортовка 30'),
        dict(p1=(DEV30 + W, DEV30), p2=(DEV30 + W, DEV30 + TOP_D), ang=90, note='правая отбортовка 30'),
    ] + ribs
    notes = ['Вырезы под GN 1/9 и съёмную большую гастроёмкость GN 1/2 (мойка); кромки шлифовать R1,5.',
             'Кран не предусмотрен: отверстие под фитинг удалено.',
             'Цельная заготовка AISI 304 с отбортовкой 30 мм; установка скользящей посадкой на опорные полки.']
    p = Part('E7', 'Рабочая зона: столешница с вырезами', 'AISI 304, шлиф. Scotch-Brite', T, 1,
             TW_FLAT, TH_FLAT, outline, cuts, bends, notes)
    return p


# ================================================================ E9 перегородка
#  Внутренняя вертикальная перегородка под столешницей: отделяет зону льда
#  (4 гастроёмкости GN 1/9) от зоны мойки (GN 1/2). Ставится поперёк станции,
#  в плоскости YZ. Верх — полка 25 мм под столешницу E7, низ — полка 20 мм на пол.
SEP_X = 498.5                              # между правым краем зоны льда (462) и левым краем мойки (535)
SEP_Y0, SEP_Y1 = 20.0, 560.0               # глубина: от фасадов до задней отбортовки
SEP_W = SEP_Y1 - SEP_Y0                    # 540 — ширина развёртки (вдоль глубины)
SEP_TOP = WORK_H - T - 1.0                 # 845.0 — верхняя кромка стенки (под столешницей)
SEP_BOT = 0.0                              # низ — пол станции
SEP_FL_TOP, SEP_FL_BOT = 25.0, 20.0        # полки, мм
SEP_H = SEP_TOP - SEP_BOT                  # 845 — высота между линиями гиба


def partition():
    """Перегородка t=1,5: стенка 540 x 845 + две полки (верх 25, низ 20)."""
    dev_t = _dev(T, SEP_FL_TOP)[0]
    dev_b = _dev(T, SEP_FL_BOT)[0]
    flat_h = dev_b + SEP_H + dev_t
    outline = [(0, 0), (SEP_W, 0), (SEP_W, flat_h), (0, flat_h)]
    yb = dev_b                             # линия гиба низа
    yt = dev_b + SEP_H                     # линия гиба верха
    cuts = []
    # вентиляционные просечки для циркуляции воздуха в зоне льда (2 шт.)
    for x in (120.0, 420.0):
        cuts.append(dict(type='poly', name='вентиляционная просечка',
                         pts=obround_pts(x, yb + SEP_H / 2, 40.0, 10.0)))
    # технологические отверстия в углах гиба
    for (x, y) in [(0, yb), (SEP_W, yb), (0, yt), (SEP_W, yt)]:
        cuts.append(dict(type='circle', cx=x, cy=y, r=RELIEF / 2))
    xm = SEP_W / 2.0
    bends = [
        dict(p1=(0, yb), p2=(SEP_W, yb), ang=90, note='низ: полка 20 на пол'),
        dict(p1=(0, yt), p2=(SEP_W, yt), ang=90, note='верх: полка 25 под столешницу'),
        dict(p1=(xm - RIB_W / 2, yb), p2=(xm - RIB_W / 2, yt), ang=90, note='вертикальное ребро жёсткости'),
        dict(p1=(xm + RIB_W / 2, yb), p2=(xm + RIB_W / 2, yt), ang=90, note='вертикальное ребро жёсткости'),
    ]
    notes = ['Стенка разделяет зону льда (GN 1/9) и мойку (GN 1/2).',
             'Верхняя полка 25 мм упирается в низ столешницы E7; нижняя полка 20 мм стоит на полу станции.',
             'Крепёж не предусмотрен: прижим к столешнице и полу; контроль по образцу.']
    p = Part('E9', 'Перегородка внутренняя', 'AISI 304, шлиф. Scotch-Brite',
             T, 1, SEP_W, flat_h, outline, cuts, bends, notes)
    p.sep_x = SEP_X
    p.sep_y = (SEP_Y0, SEP_Y1)
    p.flange_top, p.flange_bot = SEP_FL_TOP, SEP_FL_BOT
    return p


# ================================================================ чехол E8
BAG_EXT = (1180.0, 720.0, 145.0)
BAG_INT = (1140.0, 690.0, 110.0)
# перегородки чехла (3 мм HDPE)
DIVIDERS = [('E8.1', 640.0, 240.0), ('E8.2', 640.0, 240.0), ('E8.3', 500.0, 200.0)]


def all_parts():
    return [side_wall(False), side_wall(True), front_panel(1), front_panel(2), front_panel(3),
            drip_tray(), worktop(), partition()]


# ================================================================ изометрия
C30 = math.cos(math.radians(30.0))


def iso_pt(p, ox, oy, s):
    x, y, z = p
    return (ox + (x - y) * C30 * s, oy + (z - 0.5 * (x + y)) * s)


def iso_poly(pts3, ox, oy, s):
    return [iso_pt(p, ox, oy, s) for p in pts3]


if __name__ == '__main__':
    for p in all_parts():
        print('%-4s %-40s %7.1f x %7.1f  %6.2f кг' % (p.code, p.name, p.flat_w, p.flat_h, p.mass()))
