# -*- coding: utf-8 -*-
"""
ПАСИФИК ТУРБО · PK-FLAT-900 — безгибовая (плоская) версия станции, рев. E.

Принцип: ни одного гиба. Все несущие детали — плоские листы AISI 304 1,2 мм,
вырезанные лазером. Сборка «лист в лист»:

  J1  шлиц-стык     — торец горизонтального листа входит в шов между двумя
                      листами боковины: боковина набрана полосами по уровням
                      (плинтус / боковина / стойка / бортик). Шов = слой 1,2 мм.
  J2  шип-паз       — шип листа проходит сквозь паз ответного листа ЗАПОДЛИЦО:
                      выступ шипа = 1,45 мм (толщина + зазор), поэтому снаружи
                      нет штырей, а изнутри — нет шипов над рабочей плоскостью.
  J3  гребень       — верхний фасад входит в вырезы нижнего фасада: спереди
                      плоскость остаётся заподлицо.
  J4  сэндвич       — лоток выдачи: дно + бортики + ложное дно = коробка 30 мм.

Ничего не гнётся, не варится, инструмент не нужен. Чеки Ø4 (16 шт.) —
необязательный замок от люфта при перевозке.

Модуль: геометрия, соединения и спецификация. Единицы — мм.
Шип и паз строятся одной записью в координатах станции, поэтому стык не может
разъехаться. Проверка и отчёт: python3 pk_flat.py
"""
import math

# ------------------------------------------------------------------ габариты
W, D, H = 900.0, 600.0, 1050.0

T = 1.2                  # толщина всех листов
CLR = 0.25               # зазор в пазу (паз = T + CLR)
PIN_D, PIN_L = 4.0, 18.0
TAB_D = T                 # шип заподлицо: проходит лист насквозь и не торчит
COMB_D = 1.2 + 5.6        # гребень F11 → F12: глубокий шип внутри фасадного сэндвича
DENS = 7.93e-3           # г/мм³

PLINTH = 20.0            # плинтус: скрытая зона под дном
BOT_Z0, BOT_Z1 = PLINTH, PLINTH + T          # 20,0 … 21,2 — дно
LOW_BOT = BOT_Z1                              # 21,2 — низ нижней боковины
WORK_Z1 = 850.0                               # верх рабочей плоскости
WORK_Z0 = WORK_Z1 - T                         # 848,8 — низ столешницы
LOW_TOP = WORK_Z0
TOWER_Z1 = 1020.0 - T                         # 1018,8 — верх стойки
DRIP_Z0, DRIP_Z1 = TOWER_Z1, 1020.0           # дно лотка 1018,8 … 1020
RIM_H = 28.8                                  # бортик лотка 1020 … 1048,8
LEDGE_Z0, LEDGE_Z1 = DRIP_Z1 + RIM_H, H       # 1048,8 … 1050 — ложное дно

FRONT_Y0, FRONT_Y1 = 18.8, 20.0               # плоскость фасадов
FRONT_YC = (FRONT_Y0 + FRONT_Y1) / 2.0
TOWER_Y1 = 140.0                              # глубина зоны выдачи
REAR_Y0, REAR_Y1 = 598.8, 600.0
SEP_X = 500.0                                 # перегородка лёд / мойка
SEP_Y0, SEP_Y1 = 40.0, 542.0
SINK = dict(x=535.0, y=250.0, w=300.0, h=240.0, r=12.0)
GNS = [dict(x=48.0 + i * 108.0, y=240.0, w=90.0, h=160.0, r=8.0) for i in range(4)]

AX = {'x': 0, 'y': 1, 'z': 2}


# ------------------------------------------------------------------ примитивы
def rrect_pts(x0, y0, w, h, r=0.0, seg=8):
    r = min(r, w / 2.0, h / 2.0)
    if r <= 0.01:
        return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    pts = []
    for cx, cy, a0 in ((x0 + w - r, y0 + r, -90), (x0 + w - r, y0 + h - r, 0),
                       (x0 + r, y0 + h - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle_pts(cx, cy, r, seg=32):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def _poly_area(p):
    a = 0.0
    for i in range(len(p)):
        x1, y1 = p[i]
        x2, y2 = p[(i + 1) % len(p)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def _poly_len(p):
    L, n = 0.0, len(p)
    for i in range(n):
        x1, y1 = p[i]
        x2, y2 = p[(i + 1) % n]
        L += math.hypot(x2 - x1, y2 - y1)
    return L


# ------------------------------------------------------------------ логотип
SPORT_GLYPHS = {
    'П': ('11111', '10001', '10001', '10001', '10001', '10001', '10001'),
    'А': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'С': ('01111', '10000', '10000', '10000', '10000', '10000', '01111'),
    'И': ('10001', '10011', '10101', '10101', '11001', '10001', '10001'),
    'Ф': ('00100', '11111', '10101', '10101', '11111', '00100', '00100'),
    'К': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'Т': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'У': ('10001', '10001', '01010', '00100', '00100', '01000', '10000'),
    'Р': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'Б': ('11111', '10000', '10000', '11110', '10001', '10001', '11110'),
    'О': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
}
LOGO_CELL, LOGO_GAP, LOGO_SHEAR = 3.2, 0.45, 0.26
LOGO_WORD = 'ПАСИФИК ТУРБО'
LOGO_W = (sum(3 if ch == ' ' else 6 for ch in LOGO_WORD) - 1) * (LOGO_CELL + LOGO_GAP)


def logo_contours(cx, cy):
    """Трафарет «ПАСИФИК ТУРБО» с центром (cx, cy)."""
    cuts = []
    x0 = cx - LOGO_W / 2.0
    y0 = cy - 3.5 * (LOGO_CELL + LOGO_GAP)
    cursor = 0.0
    cell = LOGO_CELL
    for ch in LOGO_WORD:
        if ch == ' ':
            cursor += 3 * (cell + LOGO_GAP)
            continue
        for row, glyph_row in enumerate(SPORT_GLYPHS[ch]):
            for col, bit in enumerate(glyph_row):
                if bit != '1':
                    continue
                x = x0 + cursor + col * (cell + LOGO_GAP) + LOGO_SHEAR * (6 - row)
                y = y0 + (6 - row) * (cell + LOGO_GAP)
                cuts.append([(x, y), (x + cell, y), (x + cell, y + cell), (x, y + cell)])
        cursor += 6 * (cell + LOGO_GAP)
    for dy in (3.2, 5.8):                       # две скоростные полосы
        cuts.append(rrect_pts(x0 + 30.0, y0 - dy, LOGO_W - 60.0, 1.3, 0.65))
    for i in range(3):                          # три штриха перед надписью
        cuts.append(rrect_pts(x0 - 18.0 + i * 4.0, cy + (i - 1) * 4.0, 1.3, 9.0, 0.65))
    return cuts


# ------------------------------------------------------------------ деталь
class Part(object):
    """Плоская деталь в координатах станции.

    axes  — две оси станции, лежащие в плоскости детали (u, v);
    orig  — координаты станции для локального (0,0) детали;
    n0    — координата станции наружной плоскости по третьей (нормальной) оси.
    """

    def __init__(self, code, name, t, qty, axes, orig, n0, w, h, note='',
                 mat=None, rod=False):
        self.code, self.name, self.t, self.qty = code, name, t, qty
        self.axes, self.orig, self.n0 = axes, orig, n0
        self.norm = [a for a in 'xyz' if a not in axes][0]
        self.w, self.h = w, h
        self.note = note
        self.mat = mat or 'AISI 304, шлиф. Scotch-Brite'
        self.rod = rod
        self.feats = {'bottom': [], 'right': [], 'top': [], 'left': []}
        self.cuts = []
        self.joint_log = []

    # -------- локальные / станционные координаты --------
    def loc_u(self, s):
        return s - self.orig[0]

    def loc_v(self, s):
        return s - self.orig[1]

    def box_u(self):
        return self.orig[0], self.orig[0] + self.w

    def box_v(self):
        return self.orig[1], self.orig[1] + self.h

    # -------- шип --------
    def tab(self, edge, center_st, width, depth=TAB_D):
        """Шип по кромке; center_st — центр вдоль оси кромки в координатах станции."""
        ax_e, ax_d, sign = self._edge_axes(edge)
        c = center_st - self.orig[0 if ax_e == AX[self.axes[0]] else 1]
        self.feats[edge].append((c, width, depth, 'tab', ''))
        b0, b1 = self.box_v() if ax_d == AX[self.axes[1]] else self.box_u()
        base = b0 if sign < 0 else b1
        box = [None, None, None]
        box[AX[self.axes[0]] if ax_e == AX[self.axes[0]] else AX[self.axes[1]]] = \
            (center_st - width / 2.0, center_st + width / 2.0)
        box[ax_d] = (base, base + sign * depth) if sign > 0 else (base + depth * sign, base)
        box[AX[self.norm]] = (self.n0, self.n0 + self.t)
        box[ax_d] = tuple(sorted(box[ax_d]))
        return box

    def _edge_axes(self, edge):
        au, av = AX[self.axes[0]], AX[self.axes[1]]
        return {'bottom': (au, av, -1), 'top': (au, av, +1),
                'left': (av, au, -1), 'right': (av, au, +1)}[edge]

    # -------- паз под чужой шип --------
    def slot_for(self, box, note=''):
        au, av = AX[self.axes[0]], AX[self.axes[1]]
        u0 = box[au][0] - self.orig[0] - CLR / 2.0
        u1 = box[au][1] - self.orig[0] + CLR / 2.0
        v0 = box[av][0] - self.orig[1] - CLR / 2.0
        v1 = box[av][1] - self.orig[1] + CLR / 2.0
        cu0, cu1 = max(u0, 0.0), min(u1, self.w)
        cv0, cv1 = max(v0, 0.0), min(v1, self.h)
        if cu1 - cu0 < 0.9 or cv1 - cv0 < 0.9:
            raise ValueError('%s: паз не пересекает лист (%.2f × %.2f)' %
                             (self.code, cu1 - cu0, cv1 - cv0))
        open_edges = []
        if u0 <= 0.0:
            open_edges.append('left')
        if u1 >= self.w:
            open_edges.append('right')
        if v0 <= 0.0:
            open_edges.append('bottom')
        if v1 >= self.h:
            open_edges.append('top')
        if len(open_edges) == 1:
            e = open_edges[0]
            if e == 'left':
                self.feats['left'].append(((cv0 + cv1) / 2.0, cv1 - cv0, cu1, 'notch', note))
            elif e == 'right':
                self.feats['right'].append(((cv0 + cv1) / 2.0, cv1 - cv0, self.w - cu0, 'notch', note))
            elif e == 'bottom':
                self.feats['bottom'].append(((cu0 + cu1) / 2.0, cu1 - cu0, cv1, 'notch', note))
            else:
                self.feats['top'].append(((cu0 + cu1) / 2.0, cu1 - cu0, self.h - cv0, 'notch', note))
        elif len(open_edges) == 0:
            r = min(cu1 - cu0, cv1 - cv0) / 2.0
            self.cuts.append(rrect_pts(cu0, cv0, cu1 - cu0, cv1 - cv0, r))
        else:
            raise ValueError('%s: паз выходит на две кромки (%s)' % (self.code, open_edges))
        self.joint_log.append(note)

    # -------- вырезы --------
    def cut(self, pts):
        self.cuts.append(list(pts))

    def cut_rrect(self, x, y, w, h, r=0.0):
        self.cut(rrect_pts(x, y, w, h, r))

    def cut_circle(self, cx, cy, r):
        self.cut(circle_pts(cx, cy, r))

    # -------- контур --------
    def outline(self):
        w, h = self.w, self.h

        def edge(p0, p1, out, items):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy)
            ux, uy = dx / L, dy / L

            def P(s, t):
                return (p0[0] + ux * s + out[0] * t, p0[1] + uy * s + out[1] * t)

            pts = []
            for (c, wd, dp, kind, _n) in sorted(items, key=lambda q: q[0]):
                pos = c - wd / 2.0
                pts.append(P(pos, 0.0))
                if kind == 'tab':
                    pts += [P(pos, dp), P(pos + wd, dp), P(pos + wd, 0.0)]
                else:
                    pts += [P(pos, -dp), P(pos + wd, -dp), P(pos + wd, 0.0)]
            pts.append(P(L, 0.0))
            return pts

        def conv(name, items):
            res = []
            for (c, wd, dp, kind, n) in items:
                if name in ('bottom', 'right'):
                    res.append((c, wd, dp, kind, n))
                elif name == 'top':
                    res.append((w - c, wd, dp, kind, n))
                else:
                    res.append((h - c, wd, dp, kind, n))
            return res

        pts = []
        pts += edge((0, 0), (w, 0), (0, -1), conv('bottom', self.feats['bottom']))
        pts += edge((w, 0), (w, h), (1, 0), conv('right', self.feats['right']))
        pts += edge((w, h), (0, h), (0, 1), conv('top', self.feats['top']))
        pts += edge((0, h), (0, 0), (-1, 0), conv('left', self.feats['left']))
        return pts

    # -------- свойства --------
    def area(self):
        a = _poly_area(self.outline())
        for c in self.cuts:
            a -= _poly_area(c)
        return a

    def mass(self):
        if self.rod:
            return self.qty * math.pi / 4.0 * PIN_D ** 2 * PIN_L * DENS / 1000.0
        return self.area() * self.t * DENS / 1000.0 * self.qty

    def cut_len(self):
        return self.qty * (_poly_len(self.outline()) +
                           sum(_poly_len(c) for c in self.cuts))

    def bbox(self):
        pts = self.outline()
        return (min(p[0] for p in pts), min(p[1] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts))

    def check(self):
        """Кромочные элементы: не ближе 6 мм к углу и не пересекаются."""
        msgs = []
        for name, items in self.feats.items():
            for (c, wd, dp, kind, _n) in items:
                if kind == 'tab':
                    continue
                if c - wd / 2.0 < 6.0 or c + wd / 2.0 > (self.w if name in ('bottom', 'top') else self.h) - 6.0:
                    msgs.append('%s: %s-паз у самой кромки (%.1f)' % (self.code, name, c))
            srt = sorted([(c - wd / 2.0, c + wd / 2.0) for (c, wd, _d, _k, _n) in items])
            for a, b in zip(srt, srt[1:]):
                if b[0] < a[1] + 3.0:
                    msgs.append('%s: пазы на кромке %s ближе 3 мм' % (self.code, name))
        return msgs


# ------------------------------------------------------------------ детали
def build():
    P = {}

    # --- боковины: 4 полосы, швы совпадают с горизонтальными листами
    P['F1'] = Part('F1', 'Плинтус боковины', T, 2, ('y', 'z'), (0.0, 0.0), 0.0,
                   600.0, PLINTH,
                   'u = y, v = z. Стоит на полу; шипы — в дно F5.')
    P['F2'] = Part('F2', 'Боковина нижняя', T, 2, ('y', 'z'), (0.0, LOW_BOT), 0.0,
                   600.0, LOW_TOP - LOW_BOT,
                   'u = y, v = z − 21,2. Верх — в шов столешницы, зад — шипы в F13.')
    P['F3'] = Part('F3', 'Стойка боковины', T, 2, ('y', 'z'), (0.0, WORK_Z1), 0.0,
                   TOWER_Y1, TOWER_Z1 - WORK_Z1,
                   'u = y, v = z − 850. Стоит на столешнице, сверху — дно лотка.')
    P['F4'] = Part('F4', 'Бортик боковины (лоток)', T, 2, ('y', 'z'), (0.0, DRIP_Z1), 0.0,
                   TOWER_Y1, RIM_H,
                   'u = y, v = z − 1020. Торец лотка; несёт ложное дно F10.')

    P['F5'] = Part('F5', 'Дно', T, 1, ('x', 'y'), (0.0, 0.0), BOT_Z0, W, D,
                   'u = x, v = y. Торцы — в шов F1/F2; пазы под фасад и перегородку.')
    P['F6'] = Part('F6', 'Столешница', T, 1, ('x', 'y'), (0.0, FRONT_Y0), WORK_Z0,
                   W, D - FRONT_Y0,
                   'u = x, v = y − 18,8. Вырезы GN 1/9 ×4 и мойки GN 1/2; торцы — в шов.')
    P['F7'] = Part('F7', 'Дно лотка выдачи', T, 1, ('x', 'y'), (0.0, 0.0), DRIP_Z0,
                   W, TOWER_Y1,
                   'u = x, v = y. Дренаж Ø30; пазы под бортики и стойки.')
    P['F8'] = Part('F8', 'Бортик лотка (перед/зад)', T, 2, ('x', 'z'), (T, DRIP_Z1),
                   FRONT_Y0, W - 2 * T, RIM_H,
                   'u = x − 1,2, v = z − 1020. Одинаковые; ставятся спереди и сзади.')
    P['F10'] = Part('F10', 'Ложное дно лотка (перфорация, логотип)', T, 1, ('x', 'y'),
                    (T, FRONT_Y1), LEDGE_Z0, W - 2 * T, TOWER_Y1 - FRONT_Y1,
                    'u = x − 1,2, v = y − 20. Лежит на бортиках; снимается за пальцевые вырезы.')
    P['F11'] = Part('F11', 'Фасад нижний', T, 1, ('x', 'z'), (T, LOW_BOT), FRONT_Y0,
                    W - 2 * T, LOW_TOP - LOW_BOT,
                    'u = x − 1,2, v = z − 21,2. Два шлица 3 мм — «три блока», лист целый.')
    P['F12'] = Part('F12', 'Фасад верхний (барьер)', T, 1, ('x', 'z'), (T, WORK_Z1),
                    FRONT_Y0, W - 2 * T, TOWER_Z1 - WORK_Z1,
                    'u = x − 1,2, v = z − 850. Стоит на столешнице, сверху — дно лотка.')
    P['F13'] = Part('F13', 'Задняя панель', T, 1, ('x', 'z'), (0.0, LOW_BOT), REAR_Y0,
                    W, LOW_TOP - LOW_BOT,
                    'u = x, v = z − 21,2. Диаграмма жёсткости; садится на шипы боковин.')
    P['F14'] = Part('F14', 'Перегородка лёд / мойка', T, 1, ('y', 'z'), (SEP_Y0, LOW_BOT),
                    SEP_X, SEP_Y1 - SEP_Y0, LOW_TOP - LOW_BOT,
                    'u = y − 40, v = z − 21,2. Делит зону льда (4 × GN 1/9) и мойку GN 1/2.')
    P['F15'] = Part('F15', 'Чека Ø4 × 18', PIN_D, 16, ('x', 'z'), (0.0, 0.0), 0.0,
                    PIN_L, PIN_D,
                    'Пруток AISI 304 Ø4, отрезка 18 мм. Необязательный замок шипов.',
                    mat='AISI 304, пруток Ø4', rod=True)

    f1, f2, f3, f4, f5, f6, f7, f8, f10, f11, f12 = (
        P[k] for k in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F10',
                       'F11', 'F12'))
    f13, f14 = P['F13'], P['F14']

    # ---------------- вырезы ----------------
    for g in GNS:
        f6.cut_rrect(g['x'], g['y'] - FRONT_Y0, g['w'], g['h'], g['r'])
    f6.cut_rrect(SINK['x'], SINK['y'] - FRONT_Y0, SINK['w'], SINK['h'], SINK['r'])

    f7.cut_circle(60.0, 70.0, 15.0)                       # дренаж Ø30

    for z in (352.0, 686.0):                              # два шлица фасада
        f11.cut_rrect(25.0, z - LOW_BOT - 1.5, f11.w - 50.0, 3.0, 1.5)

    for v in (9.0, 21.0, 89.0, 101.0):                    # перфорация ложного дна
        u = 16.0
        while u + 40.0 <= f10.w - 12.0:
            f10.cut_rrect(u, v, 40.0, 3.0, 1.5)
            u += 52.0
    for c in logo_contours(f10.w / 2.0, 60.0):
        f10.cut(c)
    for u in (70.0, f10.w - 70.0):
        f10.cut_circle(u, 60.0, 14.0)

    # ---------------- соединения ----------------
    joints = []

    def join(a, a_edge, b, center, width, note, box=None, depth=TAB_D):
        if box is None:
            box = a.tab(a_edge, center, width, depth)
        b.slot_for(box, note)
        joints.append(dict(a=a.code, b=b.code, center=center, width=width, note=note))
        return box

    # плинтус → дно
    for y in (95.0, 535.0):
        join(f1, 'top', f5, y, 30.0, 'плинтус F1 — дно F5')
    # боковина → столешница
    join(f2, 'top', f6, 100.0, 30.0, 'боковина F2 — столешница F6')
    # боковина → задняя панель (шип выходит за заднюю панель)
    for z in (280.0, 700.0):
        join(f2, 'right', f13, z, 26.0, 'боковина F2 — задняя панель F13')
    # стойка → дно лотка
    join(f3, 'top', f7, 70.0, 20.0, 'стойка F3 — дно лотка F7')
    # фасад нижний → дно
    for x in (150.0, 450.0, 750.0):
        join(f11, 'bottom', f5, x, 32.0, 'фасад F11 — дно F5')
    # фасад нижний → столешница (сверху), фасад верхний → столешница (снизу)
    for x in (150.0, 450.0, 750.0):
        box = join(f11, 'top', f6, x, 32.0, 'фасад F11 — столешница F6',
                   depth=COMB_D)
        join(f11, 'top', f12, x, 32.0, 'гребень F11 — F12', box=box)
    for x in (250.0, 500.0, 800.0):
        join(f12, 'bottom', f6, x, 32.0, 'фасад F12 — столешница F6')
    # бортики лотка → дно лотка
    for x in (100.0, 450.0, 800.0):
        join(f8, 'bottom', f7, x, 20.0, 'бортик F8/F9 — дно лотка F7')
    # перегородка → дно
    for y in (120.0, 420.0):
        join(f14, 'bottom', f5, y, 26.0, 'перегородка F14 — дно F5')

    return P, joints


def check_fit(tol=0.3):
    """Шипы не должны входить в объём чужих деталей (кроме ответного паза)."""
    P, joints = build()
    vol = {}
    for k, p in P.items():
        if p.rod:
            continue
        ax = AX[p.axes[0]], AX[p.axes[1]]
        b = [None, None, None]
        b[ax[0]] = p.box_u()
        b[ax[1]] = p.box_v()
        b[AX[p.norm]] = (p.n0, p.n0 + p.t)
        vol[k] = b
    partners = set()
    for j in joints:
        partners.add((j['a'], j['b']))
        partners.add((j['b'], j['a']))
    bad = []
    for k, p in P.items():
        if p.rod:
            continue
        for edge, items in p.feats.items():
            for (c, wd, dp, kind, _n) in items:
                if kind != 'tab':
                    continue
                b = p.tab(edge, c if False else c, wd, dp)
                # tab() уже добавил запись в feats — откатываем
                p.feats[edge].pop()
                for k2, b2 in vol.items():
                    if k2 == k or (k, k2) in partners:
                        continue
                    ov = 1.0
                    for ax in range(3):
                        lo = max(b[ax][0], b2[ax][0])
                        hi = min(b[ax][1], b2[ax][1])
                        ov *= max(0.0, hi - lo)
                    if ov > tol * tol * tol:
                        bad.append('%s.%s → %s (%.1f мм³)' % (p.code, edge, k2, ov))
    return bad


# ------------------------------------------------------------------ отчёт
def parts():
    P, _ = build()
    return [P[k] for k in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8',
                           'F10', 'F11', 'F12', 'F13', 'F14', 'F15')]


def sheet_parts():
    return [p for p in parts() if not p.rod]


def hardware():
    return [p for p in parts() if p.rod]


def report():
    P, joints = build()
    ps = sheet_parts()
    area = sum(p.area() * p.qty for p in ps)
    mass = sum(p.mass() for p in parts())
    cutl = sum(p.cut_len() for p in ps)
    stack = sum(p.t * p.qty for p in ps)
    n = sum(p.qty for p in ps)
    print('PK-FLAT-900 · рев. E · безгибовая версия')
    print('Листовых деталей: %d наименований / %d шт.   Соединений: %d'
          % (len(ps), n, len(joints)))
    print('-' * 84)
    print('%-4s %-40s %10s %3s %8s %8s' %
          ('код', 'деталь', 'мм', 'шт', 'площадь', 'масса'))
    for p in ps:
        b = p.bbox()
        print('%-4s %-40s %4.0f×%-5.0f %3d %8.3f %8.2f' %
              (p.code, p.name[:40], b[2] - b[0], b[3] - b[1], p.qty,
               p.area() * p.qty / 1e6, p.mass()))
    print('-' * 84)
    print('Площадь листа %.2f м² · масса металла %.1f кг · длина реза %.1f м'
          % (area / 1e6, mass, cutl / 1000.0))
    print('Пакет (с прокладками 2 мм): %.0f × %.0f × %.0f мм, %.0f кг'
          % (W + 40, H - 20, stack + 2.0 * n, mass))
    print('Гибов 0 · сварки 0 · крепёж: %d чек Ø4 (необязательно)' % hardware()[0].qty)
    warn = []
    for p in ps:
        warn += p.check()
    print('Проверка кромок: %s' % ('OK' if not warn else '; '.join(warn)))
    clash = check_fit()
    print('Проверка объёмов (шипы): %s'
          % ('OK' if not clash else '; '.join(sorted(set(clash)))))


if __name__ == '__main__':
    report()
