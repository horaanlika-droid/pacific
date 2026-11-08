"""ПАСИФИК ТУРБО · попап-версия из берёзовой фанеры 12 мм (PK-POP-900).

Генерирует DXF-детали (мм, 1:1, R2010) и раскрой на листы 1220 × 2440.
Слои: CUT — рез по контуру; DRILL — отверстия (Ø); TEXT — подписи (не резать).
Механизм складывания (вариант A/B) не нанесён: ждём выбор после макета.
Запуск: /tmp/pkenv/bin/python cad/pk_popup.py
"""
import math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'popup', 'cnc')
T = 12.0                      # толщина фанеры
W, D, H = 900.0, 600.0, 1050.0
SHEET = (1220.0, 2440.0)      # лист берёзовой фанеры, мм
FRONT_CLR = 0.5               # зазор фасада до боковины
FRONT_W = W - 2 * T - 2 * FRONT_CLR   # 875 — фасад между боковинами
PANEL_H, PANEL_GAP, PANEL_BOT = 334.0, 3.0, T

def rrect(x, y, w, h, r):
    """Прямоугольник со скруглёнными углами (радиус r) — полилиния с дугами."""
    b = math.tan(math.radians(90) / 4)   # bulge для дуги 90°
    pts = [
        (x + r, y, 0), (x + w - r, y, b), (x + w, y + r, 0), (x + w, y + h - r, b),
        (x + w - r, y + h, 0), (x + r, y + h, b), (x, y + h - r, 0), (x, y + r, b),
    ]
    return pts, True

def rect(x, y, w, h):
    return [(x, y, 0), (x + w, y, 0), (x + w, y + h, 0), (x, y + h, 0)], True

class Part:
    def __init__(self, code, name, w, h, qty, note):
        self.code, self.name, self.w, self.h, self.qty, self.note = code, name, w, h, qty, note
        self.cuts = []     # список (pts, closed) — контуры реза
        self.holes = []    # (x, y, d)
        self.texts = []    # (x, y, текст)

# ---------- детали ----------
def side():
    # профиль в плоскости YZ: y — глубина от фасада, z — высота
    p = Part('PK-POP-01', 'Боковина (2 шт., зеркально)', 600, 1020, 2,
             'ступень: 1020 спереди, 838 под столешницей (рабочая плоскость 850)')
    p.cuts.append(([(0, 0, 0), (600, 0, 0), (600, 838, 0), (140, 838, 0), (140, 1020, 0), (0, 1020, 0)], True))
    # винты в торец дна: Ø4 на z=6
    for y in (60, 200, 400, 540):
        p.holes.append((y, 6, 4.0))
    # винты крепления рейки: Ø4 через боковину в рейку
    for y in (6, 30.5):
        for z in (100, 300, 500, 700, 900):
            p.holes.append((y, z, 4.0))
    p.texts.append((20, 960, 'PK-POP-01'))
    return p

def bottom():
    p = Part('PK-POP-02', 'Дно', W - 2 * T, D, 1, 'между боковинами; винты в торец из боковин')
    p.cuts.append(rect(0, 0, W - 2 * T, D))
    for y in (60, 200, 400, 540):
        p.holes.append((0, y, 4.0))
        p.holes.append((W - 2 * T, y, 4.0))
    p.texts.append((20, 560, 'PK-POP-02'))
    return p

def countertop():
    # столешница: 900 × 460; local y=0 — передняя кромка рабочей зоны
    p = Part('PK-POP-03', 'Столешница рабочей зоны', W, 460, 1,
             '4 × GN 1/9 и мойка; верх — ламинат или лист 304; мойка — стальная вставка')
    p.cuts.append(rect(0, 0, W, 460))
    for i in range(4):
        x = 48 + i * 108
        p.cuts.append(rrect(x, 55, 90, 160, 8))
    p.cuts.append(rrect(535, 55, 300, 240, 12))
    # винты в боковины (сверху) и в перегородку
    for y in (100, 230, 360):
        p.holes.append((6, y, 4.0))
        p.holes.append((W - 6, y, 4.0))
    for y in (150, 300, 400):
        p.holes.append((498, y, 4.0))
    p.texts.append((20, 430, 'PK-POP-03'))
    return p

def front():
    p = Part('PK-POP-04', 'Фасадный блок (3 шт.)', FRONT_W, PANEL_H, 3,
             'ход в рейки; ручка-вырез сверху; без крепежа')
    p.cuts.append(rect(0, 0, FRONT_W, PANEL_H))
    # вырез под палец сверху по центру
    cx = FRONT_W / 2
    p.cuts.append(([(cx - 40, PANEL_H, 0), (cx - 40, PANEL_H - 20, 0),
                    (cx + 40, PANEL_H - 20, 0), (cx + 40, PANEL_H, 0)], False))
    p.texts.append((20, 300, 'PK-POP-04'))
    return p

def partition():
    p = Part('PK-POP-05', 'Перегородка (лёд / мойка)', 502, 826, 1,
             'x = 498 от левой кромки; высота от дна до низа столешницы (838)')
    p.cuts.append(rect(0, 0, 502, 826))
    p.texts.append((20, 780, 'PK-POP-05'))
    return p

def rail():
    p = Part('PK-POP-06', 'Рейка направляющей (4 шт.)', 1008, 40, 4,
             'Ø4 под саморезы через боковину; канал 12,5 мм')
    p.cuts.append(rect(0, 0, 1008, 40))
    for z in (100, 300, 500, 700, 900):
        p.holes.append((z, 20, 4.0))
    p.texts.append((20, 25, 'PK-POP-06'))
    return p

PARTS = [side(), bottom(), countertop(), front(), partition(), rail()]

# ---------- DXF ----------
def write_part_dxf(p, path):
    doc = ezdxf.new('R2010')
    doc.units = ezdxf.units.MM
    doc.layers.add('CUT', color=1)
    doc.layers.add('DRILL', color=5)
    doc.layers.add('TEXT', color=8)
    msp = doc.modelspace()
    for pts, closed in p.cuts:
        msp.add_lwpolyline(pts, format='xyb', close=closed, dxfattribs={'layer': 'CUT'})
    for x, y, d in p.holes:
        msp.add_circle((x, y), d / 2.0, dxfattribs={'layer': 'DRILL'})
    for x, y, t in p.texts:
        msp.add_text(t, dxfattribs={'layer': 'TEXT', 'height': 8}).set_placement((x, y))
    doc.saveas(path)

def pack(parts_list):
    """Полочный раскрой с поворотом на 90°; возвращает листы [(x, y, w, h, part, rot)]."""
    items = []
    for p in parts_list:
        for k in range(p.qty):
            items.append((p, k))
    items.sort(key=lambda it: -max(it[0].w, it[0].h))
    sheets = []
    def new_sheet():
        sheets.append({'placed': [], 'shelves': []})   # shelf: [y0, height, x_used]
        return sheets[-1]
    cur = new_sheet()
    for p, k in items:
        placed = False
        for s in sheets:
            for sh in s['shelves']:
                for rot in (False, True):
                    w, h = (p.w, p.h) if not rot else (p.h, p.w)
                    if h <= sh[1] and sh[2] + w <= SHEET[0]:
                        s['placed'].append((sh[2], sh[0], w, h, p, rot, k))
                        sh[2] += w
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        if placed:
            continue
        # новая полка на листе, где есть место по высоте
        for s in sheets:
            used = sum(sh[1] for sh in s['shelves'])
            for rot in (False, True):
                w, h = (p.w, p.h) if not rot else (p.h, p.w)
                if w <= SHEET[0] and used + h <= SHEET[1]:
                    y0 = used
                    s['shelves'].append([y0, h, w])
                    s['placed'].append((0, y0, w, h, p, rot, k))
                    placed = True
                    break
            if placed:
                break
        if not placed:
            s = new_sheet()
            w, h = p.w, p.h
            s['shelves'].append([0, h, w])
            s['placed'].append((0, 0, w, h, p, False, k))
    return sheets

def write_nest(sheets):
    for i, s in enumerate(sheets, 1):
        doc = ezdxf.new('R2010')
        doc.units = ezdxf.units.MM
        doc.layers.add('CUT', color=1)
        doc.layers.add('DRILL', color=5)
        doc.layers.add('TEXT', color=8)
        msp = doc.modelspace()
        msp.add_lwpolyline([(0, 0), (SHEET[0], 0), (SHEET[0], SHEET[1]), (0, SHEET[1])],
                           close=True, dxfattribs={'layer': 'TEXT'})
        for x0, y0, w, h, p, rot, k in s['placed']:
            def tr(x, y):
                if rot:
                    return (x0 + y, y0 + x)
                return (x0 + x, y0 + y)
            for pts, closed in p.cuts:
                q = [(*tr(x, y), b) for x, y, b in pts]
                msp.add_lwpolyline(q, format='xyb', close=closed, dxfattribs={'layer': 'CUT'})
            for x, y, d in p.holes:
                msp.add_circle(tr(x, y), d / 2.0, dxfattribs={'layer': 'DRILL'})
            msp.add_text(f'{p.code}-{k+1}', dxfattribs={'layer': 'TEXT', 'height': 10}).set_placement(tr(20, 20))
        doc.saveas(os.path.join(OUT, f'PK-POP-NEST_sheet{i}.dxf'))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for p in PARTS:
        write_part_dxf(p, os.path.join(OUT, f'{p.code}_{p.name.split(" (")[0].replace(" ", "_").lower()}.dxf'))
    sheets = pack(PARTS)
    write_nest(sheets)
    area = sum(p.w * p.h * p.qty for p in PARTS) / 1e6
    print(f'деталей: {sum(p.qty for p in PARTS)}, площадь {area:.2f} м², листов {len(sheets)} ({SHEET[0]:.0f}×{SHEET[1]:.0f})')
    for s in sheets:
        for x0, y0, w, h, p, rot, k in s['placed']:
            print(f'  {p.code}-{k+1}: x={x0:.0f} y={y0:.0f} {w:.0f}×{h:.0f}{" ↻" if rot else ""}')
