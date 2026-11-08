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
T = 1.5                                  # основная толщина AISI 304
T_FR = 1.2                               # фасадные блоки
T_GR = 1.0                               # перфорированная решётка

SIDE_TOP = 1020.0                        # верх боковой стенки (низ столешницы)
TOP_DOWN = 30.0                          # глубина отбортовки столешницы
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
#  Боковая стенка. Развёртка: X = глубина, Y = высота.
#  Пластина 599 x 1020, отбортовки: перед 30 (с пазами), зад 30, верх 40, низ 15.
SW = DEV30 + SIDE_DEPTH + DEV30          # 653.7
SH = DEV15 + SIDE_TOP + DEV40            # 1069.7
PL_X = DEV30                              # 27.35 — левая кромка пластины в развёртке
PL_Y = DEV15                              # 12.35


def side_wall(mirror=False):
    outline = cross_outline(0, 0, SIDE_DEPTH, SIDE_TOP, DEV30, DEV30, DEV15, DEV40)
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
    # пазы и штифты в верхней отбортовке под столешницу
    for x in (120.0, 470.0):
        cuts.append(dict(type='poly', pts=obround_pts(PL_X + x, PL_Y + SIDE_TOP + DEV40 / 2, 26, 11)))
    for x in (250.0, 560.0):
        cuts.append(dict(type='circle', cx=PL_X + x, cy=PL_Y + SIDE_TOP + DEV40 / 2, r=4.5))
    # вентиляционные просечки в задней отбортовке (3 шт.) + отверстия под стяжки
    for z in (300.0, 510.0, 720.0):
        cuts.append(dict(type='poly', pts=obround_pts(PL_X + SIDE_DEPTH + DEV30 / 2,
                                                      PL_Y + z, 9.0, 70.0)))
    # технологические отверстия в углах гиба
    for (x, y) in [(PL_X, PL_Y), (PL_X + SIDE_DEPTH, PL_Y),
                   (PL_X, PL_Y + SIDE_TOP), (PL_X + SIDE_DEPTH, PL_Y + SIDE_TOP)]:
        cuts.append(dict(type='circle', cx=x, cy=y, r=RELIEF / 2))
    # линии гиба
    bends = [
        dict(p1=(PL_X, PL_Y), p2=(PL_X, PL_Y + SIDE_TOP), ang=90, note='передняя отбортовка 30 вверх'),
        dict(p1=(PL_X + SIDE_DEPTH, PL_Y), p2=(PL_X + SIDE_DEPTH, PL_Y + SIDE_TOP), ang=90, note='задняя отбортовка 30'),
        dict(p1=(PL_X, PL_Y + SIDE_TOP), p2=(PL_X + SIDE_DEPTH, PL_Y + SIDE_TOP), ang=90, note='верхняя отбортовка 40'),
        dict(p1=(PL_X, PL_Y), p2=(PL_X + SIDE_DEPTH, PL_Y), ang=90, note='нижняя отбортовка 15'),
    ]
    if mirror:
        def _mx(p):
            return (SW - p[0], p[1])
        cuts = [dict(type='circle', cx=SW - c['cx'], cy=c['cy'], r=c['r'])
                if c['type'] == 'circle' else
                dict(type='poly', pts=[_mx(q) for q in c['pts']][::-1]) for c in cuts]
        bends = [dict(p1=_mx(b['p1']), p2=_mx(b['p2']), ang=b['ang'], note=b['note'])
                 for b in bends]
    notes = ['Отбортовки — внутрь станции.',
             'Пазы 26x11 в верхней отбортовке — под кулачковые замки столешницы.',
             'Отверстия Ø9 в верхней отбортовке — под установочные штифты Ø8.']
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
#  ниже уровня столешницы (1042 против 1050), дренаж Ø20 в торце.
TRAY_WALL = 22.0                      # высота стенок корыта
DEV22, _ = _dev(T_GR, TRAY_WALL, r=0.6)          # 19.35
DEV12T, _ = _dev(T_GR, 12.0, r=0.6)              # 9.35 — отгиб-крюк
TRAY_FLAT_H = DEV12T + DEV22 + DRIP_D + DEV22    # 188.05
TRAY_Y_TOP0 = DEV12T + DEV22                     # 28.7
TRAY_Y_TOP1 = TRAY_Y_TOP0 + DRIP_D               # 168.7
TRAY_RIM = 1042.0                                # верх стенок
TRAY_BOT = 1020.0                                # дно (перфорация)

# перфорация: 5 рядов пазов 40 x 3, шаг 27 по глубине, 46 по ширине, смещение через ряд
PERF = []
for r in range(5):
    yy = TRAY_Y_TOP0 + 14.0 + r * 27.0
    off = 0.0 if r % 2 == 0 else 23.0
    x = 24.0 + off
    while x + 40.0 <= W - 18.0:
        PERF.append((x, yy))
        x += 46.0


def drip_tray():
    outline = [(0, 0), (W, 0), (W, TRAY_FLAT_H), (0, TRAY_FLAT_H)]
    cuts, bends = [], []
    for (x, y) in PERF:
        cuts.append(dict(type='poly', pts=obround_pts(x + 20.0, y, 40.0, 3.0)))
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
    notes = ['Сварной узел: корыто гибкой + штуцер Ø20 дренажа + 2 упора под пальцы.',
             'Перфорация 40x3 — 90 шт., смещение через ряд.',
             'Уклон дна 1,5° к дренажу — подгибом при сварке, контроль уровнем.']
    p = Part('E6', 'Зона выдачи: перфорированный лоток', 'AISI 304, перфорация', T_GR, 1,
             W, TRAY_FLAT_H, outline, cuts, bends, notes)
    return p


# ================================================================ E7 столешница
TW_FLAT = W + 2 * DEV30                  # 954.7
TH_FLAT = TOP_D + 2 * DEV30              # 514.7

# вырезы в координатах сборки (x от левого торца, y от передней кромки столешницы)
CUT_SINK = dict(x=55, y=45, w=360, h=300, r=15)
CUT_ICE = dict(x=470, y=45, w=320, h=280, r=15)
CUT_TAP = dict(cx=235, cy=390, d=35)
CUT_RINSE = dict(cx=845, cy=110, d=60)
CUT_CABLE = dict(cx=442, cy=415, d=50)
CUT_PLUMB = dict(x=100, y=405, w=120, h=40, r=20)


def _f(x, y):
    """координаты сборки столешницы -> развёртка"""
    return DEV30 + x, DEV30 + y


def worktop():
    outline = cross_outline(0, 0, W, TOP_D, DEV30, DEV30, DEV30, DEV30)
    cuts, bends = [], []
    x, y = _f(CUT_SINK['x'], CUT_SINK['y'])
    cuts.append(dict(type='poly', name='Раковина 360x300 R15',
                     pts=rrect_pts(x, y, CUT_SINK['w'], CUT_SINK['h'], CUT_SINK['r'], 6)))
    x, y = _f(CUT_ICE['x'], CUT_ICE['y'])
    cuts.append(dict(type='poly', name='Ледник 320x280 R15',
                     pts=rrect_pts(x, y, CUT_ICE['w'], CUT_ICE['h'], CUT_ICE['r'], 6)))
    x, y = _f(CUT_TAP['cx'], CUT_TAP['cy'])
    cuts.append(dict(type='circle', name='Смеситель Ø35', cx=x, cy=y, r=CUT_TAP['d'] / 2))
    x, y = _f(CUT_RINSE['cx'], CUT_RINSE['cy'])
    cuts.append(dict(type='circle', name='Ринсер Ø60', cx=x, cy=y, r=CUT_RINSE['d'] / 2))
    x, y = _f(CUT_CABLE['cx'], CUT_CABLE['cy'])
    cuts.append(dict(type='circle', name='Кабельный ввод Ø50', cx=x, cy=y, r=CUT_CABLE['d'] / 2))
    x, y = _f(CUT_PLUMB['x'], CUT_PLUMB['y'])
    cuts.append(dict(type='poly', name='Ввод коммуникаций 120x40',
                     pts=rrect_pts(x, y, CUT_PLUMB['w'], CUT_PLUMB['h'], CUT_PLUMB['r'], 6)))
    # 4 паза под кулачковые замки + 2 Ø9 под штифты
    for (cx, cy) in [(45, 30), (855, 30), (45, 430), (855, 430)]:
        x, y = _f(cx, cy)
        cuts.append(dict(type='poly', name='замок', pts=obround_pts(x, y, 24, 12)))
    # технологические отверстия в углах гиба
    for (cx, cy) in [(0, 0), (W, 0), (0, TOP_D), (W, TOP_D)]:
        x, y = _f(cx, cy)
        cuts.append(dict(type='circle', cx=x, cy=y, r=RELIEF / 2))
    # пазы в передней отбортовке под крюки лотка E6
    for cx in (230.0, 670.0):
        cuts.append(dict(type='poly', name='крюк лотка',
                         pts=obround_pts(DEV30 + cx, DEV30 / 2 + 3.0, 26, 11)))
    bends = [
        dict(p1=(DEV30, DEV30), p2=(DEV30 + W, DEV30), ang=90, note='передняя отбортовка 30'),
        dict(p1=(DEV30, DEV30 + TOP_D), p2=(DEV30 + W, DEV30 + TOP_D), ang=90, note='задняя отбортовка 30'),
        dict(p1=(DEV30, DEV30), p2=(DEV30, DEV30 + TOP_D), ang=90, note='левая отбортовка 30'),
        dict(p1=(DEV30 + W, DEV30), p2=(DEV30 + W, DEV30 + TOP_D), ang=90, note='правая отбортовка 30'),
    ]
    notes = ['Обеспечить плоскостность ±0,8 мм на 900 — рабочая поверхность.',
             'Кромки вырезов под раковину/ледник — шлифовка R1,5, без заусенца (HACCP).',
             '4 паза 24x12 — кулачковые замки; 2 отв. Ø9 — штифты.']
    p = Part('E7', 'Рабочая зона: столешница с вырезами', 'AISI 304, шлиф. Scotch-Brite', T, 1,
             TW_FLAT, TH_FLAT, outline, cuts, bends, notes)
    return p


# ================================================================ чехол E8
BAG_EXT = (1180.0, 720.0, 145.0)
BAG_INT = (1140.0, 690.0, 110.0)
# перегородки чехла (3 мм HDPE)
DIVIDERS = [('E8.1', 640.0, 240.0), ('E8.2', 640.0, 240.0), ('E8.3', 500.0, 200.0)]


def all_parts():
    return [side_wall(False), side_wall(True), front_panel(1), front_panel(2), front_panel(3),
            drip_tray(), worktop()]


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
