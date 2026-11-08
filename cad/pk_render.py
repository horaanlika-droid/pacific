#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ПАСИФИК КИТ · PK-900 — визуализация: в сборе / в разборе / в чехле.
Строится по той же параметрической геометрии (pk_geom), что и DXF и альбом.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
from matplotlib.font_manager import FontProperties, findfont

import pk_geom as G

AX = [None, None, None]
W, D, H = G.W, G.D, G.H                      # 900 × 600 × 1050
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUT = os.path.join(OUT_DIR, 'ПАСИФИК_КИТ_визуализация.png')

# ---------------------------------------------------------------- материалы
STEEL = np.array([0.815, 0.825, 0.805])
STEEL_WARM = np.array([0.795, 0.800, 0.780])
DARK = np.array([0.40, 0.415, 0.415])
BLACK = np.array([0.13, 0.135, 0.135])
HDPE =np.array([0.26, 0.265, 0.255])
CANVAS = np.array([0.375, 0.368, 0.340])
BG_TOP = '#f4f2ec'
BG_BOT = '#e4e1d8'
ACC = '#b8492a'

L1 = np.array([-0.42, -0.72, 0.78]); L1 /= np.linalg.norm(L1)
L2 = np.array([0.66, -0.30, 0.22]); L2 /= np.linalg.norm(L2)
L3 = np.array([0.10, 0.85, 0.30]); L3 /= np.linalg.norm(L3)


def shade(base, n):
    d = max(0.0, float(n @ L1))
    f = max(0.0, float(n @ L2))
    b = max(0.0, float(n @ L3))
    k = 0.50 + 0.54 * d + 0.16 * f + 0.10 * b
    col = np.clip(base * k, 0.0, 1.0)
    spec = 0.12 * max(0.0, float(n @ L1)) ** 12
    return np.clip(col + spec, 0, 1)


class Scene:
    """накопитель полигонов: всё рисуется одной коллекцией — корректная сортировка"""

    def __init__(self):
        self.faces = []
        self.cols = []
        self.edges = []

    def quad(self, pts, base, edge=None, lw=0.45, alpha=1.0, flat=False, unlit=False):
        p = np.array(pts, float)
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            return
        n /= ln
        col = np.clip(base, 0, 1) if unlit else shade(base, n)
        self.faces.append(p)
        self.cols.append(tuple(col) + (alpha,))
        if edge is None:
            edge = (tuple(col) if flat else tuple(np.clip(col * 0.62, 0, 1))) + (alpha,)
        else:
            edge = tuple(edge) + (alpha,)
        self.edges.append(edge)

    def box(self, x0, x1, y0, y1, z0, z1, base=STEEL, edge=None, lw=0.45, skip=()):
        X = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]
        B = [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        L = [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)]
        R = [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]
        Dn = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
        U = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        for name, pts in (('front', X), ('back', B), ('left', L), ('right', R),
                          ('bottom', Dn), ('top', U)):
            if name in skip:
                continue
            self.quad(pts, base, edge, lw)

    def poly_at(self, pts2d, z, base, edge=None, lw=0.4):
        self.quad([(x, y, z) for x, y in pts2d], base, edge, lw)

    def draw(self, ax):
        if not self.faces:
            return
        pc = Poly3DCollection(self.faces, facecolors=self.cols, edgecolors=self.edges,
                              linewidths=0.45, zsort='average')
        pc.set_antialiased(True)
        ax.add_collection3d(pc)



def ax_ring(ax, pts2d, z, color=(0.34, 0.35, 0.34), lw=0.8):
    if ax is None:
        return
    xs = [p[0] for p in pts2d] + [pts2d[0][0]]
    ys = [p[1] for p in pts2d] + [pts2d[0][1]]
    ax.plot(xs, ys, [z] * len(xs), color=color, lw=lw, zorder=40,
            solid_joinstyle='round')


def floor(ax, x0=-260, x1=1160, y0=-420, y1=760, z=0.0, base=np.array([0.905, 0.90, 0.87])):
    sc = Scene()
    sc.quad([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], base, edge=(0.86, 0.85, 0.82), lw=0.6)
    sc.draw(ax)


def shadow(ax, x0, x1, y0, y1, k=1.0, z=0.4):
    """мягкая тень: несколько полупрозрачных рамок со сдвигом по свету"""
    for i, (grow, a) in enumerate(((26, 0.055), (14, 0.06), (4, 0.07))):
        dx, dy = -18 - grow * 0.6, -14 - grow * 0.4
        pts = [(x0 - grow + dx * k, y0 - grow + dy * k, z),
               (x1 + grow + dx * k, y0 - grow + dy * k, z),
               (x1 + grow + dx * k, y1 + grow + dy * k, z),
               (x0 - grow + dx * k, y1 + grow + dy * k, z)]
        ax.add_collection3d(Poly3DCollection([pts], facecolors=[(0.18, 0.17, 0.15, a)],
                                             edgecolors='none', zsort='min'))


def tube(ax, pts, lw=3.4, color=(0.30, 0.31, 0.31), zorder=30):
    xs, ys, zs = zip(*pts)
    ax.plot(xs, ys, zs, color=color, lw=lw, solid_capstyle='round',
            solid_joinstyle='round', zorder=zorder)


def arc(cx, cy, z, r, a0, a1, n=14):
    t = np.linspace(np.radians(a0), np.radians(a1), n)
    return [(cx + r * np.cos(v), cy, z + r * np.sin(v)) for v in t]


# ---------------------------------------------------------------- станция
ST = dict(
    wall_t=1.5, wall_fl=(30, 30, 40, 15),      # перед / зад / верх / низ
    block_t=1.2, blk_z=((12, 346), (349, 683), (686, 1020)),
    top=(820, 850), tray=(1028, 1050),
)


def wall(sc, side, offx=0.0, dz=0.0, y=(0, D), z=(0, 1020)):
    """ступенчатая боковая стенка: передняя стойка 140×1020 + рабочая часть 460×820"""
    t = ST['wall_t']
    if side == 'L':
        x0, x1 = 0 + offx, t + offx
        fx1 = x0 + 30
    else:
        x0, x1 = W - t + offx, W + offx
        fx1 = x0 - 30
    y0, ym, y1 = y[0], 140.0, y[1]
    z0, zlo, zhi = z[0] + dz, 820.0 + dz, z[1] + dz
    bot = 15
    # монолитная L-образная пластина (без вертикального шва на y = 140)
    sc.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, zlo),
             (x0, ym, zlo), (x0, ym, zhi), (x0, y0, zhi)], STEEL)
    sc.quad([(x1, y0, z0), (x1, y0, zhi), (x1, ym, zhi),
             (x1, ym, zlo), (x1, y1, zlo), (x1, y1, z0)], STEEL)
    sc.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, zhi), (x0, y0, zhi)], STEEL)      # перед
    sc.quad([(x0, y1, z0), (x0, y1, zlo), (x1, y1, zlo), (x1, y1, z0)], STEEL)      # зад
    sc.quad([(x0, y0, zhi), (x1, y0, zhi), (x1, ym, zhi), (x0, ym, zhi)], STEEL)    # верх стойки
    sc.quad([(x0, ym, zlo), (x1, ym, zlo), (x1, ym, zhi), (x0, ym, zhi)], STEEL)    # уступ
    sc.quad([(x0, ym, zlo), (x1, ym, zlo), (x1, y1, zlo), (x0, y1, zlo)], STEEL)    # полка 820
    if side == 'L':
        sc.box(x1, fx1, y0, y0 + 1.2, z0, zhi, STEEL)                               # перед. отбортовка
        sc.box(x1, fx1, y1 - 1.2, y1, z0, zlo, STEEL)                               # задняя
        sc.box(x1, x0 + bot, y0, y1, z0, z0 + 1.2, STEEL)                           # низ
    else:
        sc.box(fx1, x0, y0, y0 + 1.2, z0, zhi, STEEL)
        sc.box(fx1, x0, y1 - 1.2, y1, z0, zlo, STEEL)
        sc.box(x0 - bot, x0, y0, y1, z0, z0 + 1.2, STEEL)


def block(sc, z0, z1, dy=0.0, dz=0.0, face=STEEL, see_back=True):
    t = ST['block_t']
    sc.box(0, W, dy, dy + t, z0 + dz, z1 + dz, face)
    if see_back:
        sc.box(0, W, dy + t, dy + t + 20, z0 + dz + 1.2, z0 + dz + 1.2 + 1.2, face * 0.94)  # низ 20
        sc.box(0, W, dy + t, dy + t + 25, z1 + dz - 1.2, z1 + dz, face * 1.02)               # верх 25


def top_face(sc, x0, x1, y0, y1, z, holes, base, unlit=False):
    """верхняя грань с прямоугольными вырезами: сетка по границам вырезов"""
    xs = sorted({x0, x1, *[h[0] for h in holes], *[h[1] for h in holes]})
    ys = sorted({y0, y1, *[h[2] for h in holes], *[h[3] for h in holes]})
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if any(h[0] <= cx <= h[1] and h[2] <= cy <= h[3] for h in holes):
                continue
            sc.quad([(xs[i], ys[j], z), (xs[i + 1], ys[j], z),
                     (xs[i + 1], ys[j + 1], z), (xs[i], ys[j + 1], z)],
                    base, flat=True, unlit=unlit)


def worktop(sc, dz=0.0, dy=0.0, show_holes=True, show_basin=True, c_=None):
    z0, z1 = ST['top'][0] + dz, ST['top'][1] + dz
    y0, y1 = 140 + dy, D + dy
    sc.box(0, W, y0, y1, z0, z1, STEEL_WARM, skip=('top', 'bottom'))
    if not show_holes:
        sc.quad([(0, y0, z1), (W, y0, z1), (W, y1, z1), (0, y1, z1)], STEEL_WARM)
        return
    rects = []
    for key in ('CUT_SINK', 'CUT_ICE'):
        c = getattr(G, key)
        rects.append((c['x'], c['x'] + c['w'], c['y'] + 110 + dy, c['y'] + c['h'] + 110 + dy))
    c = G.CUT_PLUMB
    rects.append((c['x'], c['x'] + c['w'], c['y'] + 110 + dy, c['y'] + c['h'] + 110 + dy))
    top_face(sc, 0, W, y0, y1, z1, rects, STEEL_WARM)
    # кромка выреза (толщина листа 30)
    edge = np.array([0.60, 0.615, 0.605])
    for (hx0, hx1, hy0, hy1) in rects:
        sc.quad([(hx0, hy0, z1), (hx0, hy0, z0), (hx1, hy0, z0), (hx1, hy0, z1)], edge)      # перед
        sc.quad([(hx0, hy1, z1), (hx1, hy1, z1), (hx1, hy1, z0), (hx0, hy1, z0)], edge)      # зад
        sc.quad([(hx0, hy0, z1), (hx0, hy1, z1), (hx0, hy1, z0), (hx0, hy0, z0)], edge)      # лево
        sc.quad([(hx1, hy0, z1), (hx1, hy1, z1), (hx1, hy1, z0), (hx1, hy0, z0)], edge)      # право
    # круги — тёмные пятна на поверхности
    for key in ('CUT_TAP', 'CUT_RINSE', 'CUT_CABLE'):
        c = getattr(G, key)
        cx, cy, r = c['cx'], c['cy'] + 110 + dy, c['d'] / 2
        a = np.linspace(0, 2 * np.pi, 24)
        sc.poly_at([(cx + r * np.cos(v), cy + r * np.sin(v)) for v in a], z1 + 0.4,
                   np.array([0.30, 0.31, 0.31]), edge=(0.26, 0.27, 0.27), lw=0.5)
    if show_basin:
        basin(sc, G.CUT_SINK, dz, dy, full=(dz > 0))
        basin(sc, G.CUT_ICE, dz, dy, depth=215, full=(dz > 0))


def basin(sc, c, dz, dy, depth=170, full=False):
    """углубление под вырез: тёмные внутренние грани + дно"""
    x0, x1 = c['x'], c['x'] + c['w']
    y0, y1 = c['y'] + 110 + dy, c['y'] + c['h'] + 110 + dy
    zt = ST['top'][1] + dz - 30
    zb = zt - depth
    sc.quad([(x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb)],
            np.array([0.37, 0.38, 0.38]), unlit=True, flat=True)                     # дно
    sc.quad([(x0, y0, zt), (x0, y1, zt), (x0, y1, zb), (x0, y0, zb)],
            np.array([0.56, 0.57, 0.57]), unlit=True, flat=True)                     # левая
    sc.quad([(x0, y1, zt), (x1, y1, zt), (x1, y1, zb), (x0, y1, zb)],
            np.array([0.45, 0.46, 0.46]), unlit=True, flat=True)                     # задняя
    if full:
        sc.quad([(x1, y0, zt), (x1, y0, zb), (x1, y1, zb), (x1, y1, zt)],
                np.array([0.60, 0.61, 0.61]), unlit=True, flat=True)                 # правая
        sc.quad([(x0, y0, zt), (x0, y0, zb), (x1, y0, zb), (x1, y0, zt)],
                np.array([0.50, 0.51, 0.51]), unlit=True, flat=True)                 # передняя


def tray(sc, dz=0.0, dy=0.0, decks=True, apron=True):
    """зона выдачи: приподнятый лоток на верхней плоскости бара"""
    z0, z1 = ST['tray'][0] + dz, ST['tray'][1] + dz
    sc.box(0, W, dy, dy + 140, z0 - 8, z0, STEEL * 0.80, skip=('top', 'bottom', 'back'))
    sc.box(0, W, dy, dy + 22, z0, z1, STEEL, skip=('bottom', 'back', 'top'))
    sc.box(0, W, dy + 118, dy + 140, z0, z1, STEEL, skip=('bottom', 'front', 'top'))
    if apron:
        sc.box(0, W, dy + 132, dy + 140, ST['top'][1] + dz - 4, z0 + 1.2,
               STEEL * 0.97, skip=('top', 'bottom', 'front', 'back'))
    zdeck = z1 - 8
    nx = 9
    for ix in range(nx):
        xa, xb = ix * W / nx, (ix + 1) * W / nx
        # верхние и внутренние грани бортов лотка разбиты по X (flat=True — без швов)
        sc.quad([(xa, dy, z1), (xb, dy, z1),
                 (xb, dy + 22, z1), (xa, dy + 22, z1)], STEEL, flat=True)
        sc.quad([(xa, dy + 22, z1), (xb, dy + 22, z1),
                 (xb, dy + 22, zdeck), (xa, dy + 22, zdeck)], STEEL * 0.92, flat=True)
        sc.quad([(xa, dy + 118, z1), (xb, dy + 118, z1),
                 (xb, dy + 140, z1), (xa, dy + 140, z1)], STEEL, flat=True)
        sc.quad([(xa, dy + 118, zdeck), (xb, dy + 118, zdeck),
                 (xb, dy + 118, z1), (xa, dy + 118, z1)], STEEL * 0.92, flat=True)
        sc.quad([(xa, dy + 22, zdeck), (xb, dy + 22, zdeck),
                 (xb, dy + 118, zdeck), (xa, dy + 118, zdeck)], STEEL, flat=True)
        if apron:
            sc.quad([(xa, dy + 140, ST['top'][1] + dz - 4), (xb, dy + 140, ST['top'][1] + dz - 4),
                     (xb, dy + 140, z0 + 1.2), (xa, dy + 140, z0 + 1.2)], STEEL * 0.97, flat=True)
    if decks:
        for row in range(5):
            yy = dy + 30 + row * 18
            for k in range(18):
                xx = 12 + k * 50 + (25 if row % 2 else 0)
                if xx + 40 > W - 10:
                    continue
                sc.quad([(xx, yy, zdeck + 0.8), (xx + 40, yy, zdeck + 0.8),
                         (xx + 40, yy + 3, zdeck + 0.8), (xx, yy + 3, zdeck + 0.8)],
                        np.array([0.30, 0.31, 0.31]))


def faucet(sc, ax, dz=0.0, dy=0.0):
    cx = G.CUT_TAP['cx']
    cy = G.CUT_TAP['cy'] + 110 + dy
    zb = ST['top'][1] + dz
    pts = [(cx, cy, zb), (cx, cy, zb + 90)]
    pts += [(cx, cy - 10, zb + 118), (cx, cy - 55, zb + 132), (cx, cy - 112, zb + 120),
            (cx, cy - 128, zb + 96), (cx, cy - 128, zb + 78)]
    tube(ax, pts, lw=3.0, color=(0.42, 0.43, 0.42))
    ax.add_collection3d(Poly3DCollection(
        [[(cx - 24, cy - 12, zb + 0.8), (cx + 24, cy - 12, zb + 0.8),
          (cx + 24, cy + 12, zb + 0.8), (cx - 24, cy + 12, zb + 0.8)]],
        facecolors=[(0.55, 0.56, 0.55, 1)], edgecolors='none', zsort='max'))


def rinsser(sc, ax, dz=0.0, dy=0.0):
    cx, cy = G.CUT_RINSE['cx'], G.CUT_RINSE['cy'] + 110 + dy
    zb = ST['top'][1] + dz
    tube(ax, [(cx, cy, zb), (cx, cy, zb + 55), (cx + 4, cy - 26, zb + 92),
              (cx + 4, cy - 52, zb + 40)], lw=2.6, color=(0.42, 0.43, 0.42))


# ---------------------------------------------------------------- сцены
def scene_assembled(sc, dz=0.0):
    wall(sc, 'L')
    wall(sc, 'R')
    for (z0, z1) in ST['blk_z']:
        block(sc, z0, z1, see_back=False)
    worktop(sc, c_=AX[0])
    tray(sc)


def scene_exploded(sc, e=1.0):
    """e — коэффициент разлёта; детали помечены номерами 1…8"""
    wall(sc, 'L', offx=-250 * e)
    wall(sc, 'R', offx=+250 * e)
    for i, (z0, z1) in enumerate(ST['blk_z']):
        block(sc, z0, z1, dy=-70 * e - i * 40 * e, dz=-330 * e)
    worktop(sc, dz=+260 * e, c_=AX[1])
    tray(sc, dz=+380 * e, dy=-140 * e, apron=False)


def scene_bag(sc, ax, dz=0.0):
    """чехол открытый сверху, внутри — пакет листов"""
    bw, bd, bh = 1180, 720, 145
    x0, x1 = -140, bw - 140
    y0, y1 = -60, bd - 60
    t = 8
    # дно, стенки (верх открыт)
    sc.box(x0, x1, y0, y1, dz, dz + t, CANVAS)
    sc.box(x0, x1, y0, y0 + t, dz + t, dz + bh, CANVAS)
    sc.box(x0, x1, y1 - t, y1, dz + t, dz + bh, CANVAS)
    sc.box(x0, x0 + t, y0, y1, dz + t, dz + bh, CANVAS)
    sc.box(x1 - t, x1, y0, y1, dz + t, dz + bh, CANVAS)
    # внутренняя облицовка (светлая) — дно + 4 стенки, не сплошная плита
    inner = np.array([0.72, 0.70, 0.64])
    sc.box(x0 + t, x1 - t, y0 + t, y1 - t, dz + t, dz + t + 3, inner, skip=('bottom',))
    sc.box(x0 + t, x1 - t, y0 + t, y0 + t + 3, dz + t, dz + bh - 4, inner)
    sc.box(x0 + t, x1 - t, y1 - t - 3, y1 - t, dz + t, dz + bh - 4, inner)
    sc.box(x0 + t, x0 + t + 3, y0 + t, y1 - t, dz + t, dz + bh - 4, inner)
    sc.box(x1 - t - 3, x1 - t, y0 + t, y1 - t, dz + t, dz + bh - 4, inner)
    # пакет листов: 5 слоёв + 3 перегородки
    zz = dz + t + 5
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # «сэндвич»: слои уменьшаются кверху — видна укладка
    stack = [(1070, 654, 13, 0.815), (1070, 654, 13, 0.815),
             (955, 515, 12, 0.795), (900, 470, 8, 0.47),
             (890, 190, 4, 0.815), (890, 190, 4, 0.815), (890, 190, 4, 0.815),
             (830, 150, 9, 0.50)]
    for (lw_, lh_, th, g) in stack:
        col = np.array([g, g * 1.01, g * 0.99])
        sc.box(cx - lw_ / 2, cx + lw_ / 2, cy - lh_ / 2, cy + lh_ / 2, zz, zz + th, col,
               edge=(0.88, 0.88, 0.86))
        zz += th + 11
    # колёса
    for (wx, wy) in ((x0 + 90, y0), (x1 - 90, y0)):
        for s in (-1, 1):
            tube(ax, [(wx, wy + s * 2, dz + 38), (wx, wy + s * 2, dz + 38)], lw=0)
    return dict(x0=x0, x1=x1, y0=y0, y1=y1, bh=bh)


def wheels(sc, ax, x0, x1, y0, dz=0.0):
    for wx in (x0 + 110, x1 - 110):
        a = np.linspace(0, 2 * np.pi, 20)
        pts = [(wx + 36 * np.cos(v), y0 - 14, dz + 38 + 36 * np.sin(v)) for v in a]
        ax.add_collection3d(Poly3DCollection([pts], facecolors=[(0.12, 0.12, 0.12, 1)],
                                             edgecolors=[(0.08, 0.08, 0.08, 1)],
                                             linewidths=0.6, zsort='min'))
        tube(ax, [(wx, y0 - 14, dz + 38), (wx, y0 - 14, dz + 38)], lw=0)


# ---------------------------------------------------------------- камера
def setup(ax, elev=16, azim=-62, zoom=1.0, proj='ortho'):
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type(proj)
    ax.set_axis_off()
    ax.patch.set_alpha(0)
    ax.set_facecolor('none')


def frame(ax, x0, x1, y0, y1, z0, z1, elev=16, azim=-62):
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_zlim(z0, z1)
    ax.set_box_aspect((x1 - x0, y1 - y0, (z1 - z0) * 0.92))
    setup(ax, elev, azim)


def label3d(ax, x, y, z, text, dx=0, dy=0, size=9.5, color='#25262a', weight='bold'):
    x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
    ax.annotate(text, xy=(x2, y2), xytext=(dx, dy), textcoords='offset points',
                ha='center', va='center', fontsize=size, color=color,
                fontweight=weight, zorder=100,
                bbox=dict(boxstyle='circle,pad=0.30', fc='white', ec='#9a9a96', lw=0.7))


def leader3d(ax, x, y, z, x2, y2, z2, color='#8a8a86', lw=0.7):
    ax.plot([x, x2], [y, y2], [z, z2], color=color, lw=lw, ls=(0, (3, 2)), zorder=60)


def labels_exploded(ax):
    """номера деталей на взрыв-схеме (1…7; чехол — на панели 3)"""
    marks = [((-330, 300, 680), '1'), ((1235, 300, 680), '2'),
             ((-105, -85, -150), '3'), ((-105, -145, 190), '4'), ((-105, -185, 520), '5'),
             ((220, -220, 1520), '6'), ((780, 640, 1180), '7')]
    for (p, t) in marks:
        label3d(ax, *p, t, size=10.5)


# ---------------------------------------------------------------- сборка листа
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    fig = plt.figure(figsize=(16.8, 8.4), dpi=260)
    fig.patch.set_facecolor('#eeebe3')

    # фон-градиент
    axbg = fig.add_axes([0, 0, 1, 1], zorder=0)
    axbg.set_axis_off()
    g = np.linspace(0, 1, 256).reshape(-1, 1)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('bg', ['#f7f5ef', '#e3dfd4'])
    axbg.imshow(g, extent=[0, 1, 0, 1], aspect='auto', cmap=cmap, origin='lower')

    # заголовок
    fp_bold = findfont(FontProperties(family='DejaVu Sans', weight='bold'))
    fig.text(0.030, 0.945, 'ПАСИФИК КИТ', fontsize=27, fontweight='bold', color='#1e1f22')
    fig.text(0.030, 0.903, 'PACIFIC KIT · PK-900', fontsize=10.5, color='#6a6a66')
    fig.text(0.030, 0.870, 'разборная барная станция · 900 × 600 × 1050 мм · 8 элементов · '
                          'сборка без инструмента', fontsize=10.5, color='#4a4a48')
    fig.text(0.972, 0.945, 'визуализация', fontsize=12, color='#6a6a66', ha='right')
    fig.text(0.972, 0.913, 'в сборе · в разборе · в чехле', fontsize=10.5, color='#6a6a66',
             ha='right')
    fig.text(0.972, 0.885, 'рев. B · 08.11.2026', fontsize=9, color='#8a8a86', ha='right')
    fig.add_artist(plt.Line2D([0.030, 0.972], [0.858, 0.858], color='#1e1f22', lw=1.2))

    panels = [(0.016, 0.070, 0.320, 0.735), (0.334, 0.070, 0.320, 0.735),
              (0.652, 0.070, 0.322, 0.735)]
    titles = ['1 · В СБОРЕ', '2 · В РАЗБОРЕ', '3 · В ЧЕХЛЕ']
    subs = ['борт выдачи 1050 мм · рабочая часть опущена на высоту бедра (850 мм)',
            'детали разнесены по осям сборки · нумерация по спецификации',
            'плоский чехол-сумка 1180 × 720 × 145 · укладка «сэндвичем»']

    # ---------- панель 1
    ax1 = fig.add_axes(panels[0], projection='3d', computed_zorder=False)
    AX[0] = ax1
    sc = Scene()
    floor(ax1)
    shadow(ax1, 0, W, 0, D, k=1.0)
    scene_assembled(sc)
    sc.draw(ax1)
    faucet(sc, ax1)
    rinsser(sc, ax1)
    frame(ax1, -190, 1090, -360, 760, -10, 1120, elev=35, azim=-58)

    # ---------- панель 2
    ax2 = fig.add_axes(panels[1], projection='3d', computed_zorder=False)
    AX[1] = ax2
    sc = Scene()
    floor(ax2, x0=-620, x1=1520, y0=-620, y1=980)
    shadow(ax2, -260, 1160, -360, 130, k=1.6, z=0.4)
    scene_exploded(sc, e=1.0)
    sc.draw(ax2)
    frame(ax2, -600, 1500, -640, 1000, -420, 1420, elev=17, azim=-63)
    labels_exploded(ax2)

    # ---------- панель 3
    ax3 = fig.add_axes(panels[2], projection='3d', computed_zorder=False)
    AX[2] = ax3
    sc = Scene()
    floor(ax3, x0=-420, x1=1560, y0=-460, y1=980)
    shadow(ax3, -140, 1040, -60, 660, k=1.4)
    dims = scene_bag(sc, ax3)
    sc.draw(ax3)
    wheels(sc, ax3, dims['x0'], dims['x1'], dims['y0'])
    frame(ax3, -280, 1360, -400, 780, -20, 520, elev=33, azim=-56)

    # ---------- подписи
    for i, (p, t, s) in enumerate(zip(panels, titles, subs)):
        fig.text(p[0] + 0.008, p[1] + p[3] + 0.024, t, fontsize=13, fontweight='bold',
                 color='#1e1f22')
        fig.text(p[0] + 0.008, p[1] + p[3] + 0.008, s, fontsize=8.2, color='#6a6a66')
    fig.text(0.030, 0.020, 'ПАСИФИК КИТ · PK-900 · визуализация по параметрической модели '
                           '(cad/pk_geom.py) · размеры в мм · AISI 304',
             fontsize=7.8, color='#8a8a86')
    fig.text(0.972, 0.020, 'лист визуализации · 1 из 1', fontsize=7.8, color='#8a8a86',
             ha='right')

    fig.savefig(OUT, facecolor=fig.get_facecolor(), bbox_inches=None)
    print('ok', OUT)
    return ax1, ax2, ax3


if __name__ == '__main__':
    main()
