#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПАСИФИК ТУРБО · PK-900R — 3D-визуализация складной радиусной станции:
  1 · В СБОРЕ (спереди-справа: монолитный фасад, угловые колонны R80, венец выдачи 1050, рабочая зона 850)
  2 · КИНЕМАТИКА РАСКЛАДЫВАНИЯ (открытие радиусных крыльев на петлях + установка диафрагмы и венца)
  3 · В СЛОЖЕННОМ ПАКЕТЕ (900 × 600 × 135 мм — транспортный кофр со вложенными столешницей и венцом)
"""
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

import pk_radius_fold as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'radius_fold', 'PK-900R_визуализация.png')

W, D, H = R.W, R.D, R.H
CR = R.CORNER_R                     # 80.0

STEEL = np.array([0.825, 0.832, 0.820])
STEEL_CAP = np.array([0.855, 0.860, 0.848])
STEEL_WORK = np.array([0.795, 0.802, 0.788])
DARK_BASIN = np.array([0.38, 0.39, 0.395])
SEAM_COL = (0.32, 0.33, 0.34, 0.9)

L1 = np.array([-0.48, -0.70, 0.65]); L1 /= np.linalg.norm(L1)
L2 = np.array([0.65, -0.35, 0.28]);  L2 /= np.linalg.norm(L2)
L3 = np.array([0.05, 0.88, 0.32]);   L3 /= np.linalg.norm(L3)


def shade(base, n, spec_k=0.16):
    d1 = max(0.0, float(n @ L1))
    d2 = max(0.0, float(n @ L2))
    d3 = max(0.0, float(n @ L3))
    k = 0.48 + 0.50 * d1 + 0.18 * d2 + 0.08 * d3
    col = np.clip(base * k, 0.0, 1.0)
    spec = spec_k * (max(0.0, float(n @ L1)) ** 14)
    return np.clip(col + spec, 0.0, 1.0)


def rot_z(pts, cx, cy, deg):
    if abs(deg) < 1e-6:
        return pts
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y, z in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, z))
    return out


class Scene3D:
    def __init__(self):
        self.faces = []
        self.cols = []
        self.edges = []
        self.lws = []

    def quad(self, pts, base=STEEL, edge=None, lw=0.35, alpha=1.0, smooth=False, unlit=False):
        p = np.array(pts, float)
        if len(p) >= 3:
            n = np.cross(p[1] - p[0], p[2] - p[0])
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                return
            n /= ln
        else:
            return
        col = np.clip(base, 0, 1) if unlit else shade(base, n)
        self.faces.append(p)
        self.cols.append(tuple(col) + (alpha,))
        if smooth:
            ec = tuple(col) + (alpha,)
            lw_use = 0.15
        elif edge is None:
            ec = tuple(np.clip(col * 0.64, 0, 1)) + (alpha,)
            lw_use = lw
        else:
            ec = tuple(edge[:3]) + (edge[3] if len(edge) > 3 else alpha,)
            lw_use = lw
        self.edges.append(ec)
        self.lws.append(lw_use)

    def box(self, x0, x1, y0, y1, z0, z1, base=STEEL, skip=(), lw=0.4):
        faces = dict(
            front=[(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
            back=[(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
            left=[(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
            right=[(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
            bottom=[(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
            top=[(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        )
        for k, pts in faces.items():
            if k not in skip:
                self.quad(pts, base=base, lw=lw)

    def draw(self, ax):
        if not self.faces:
            return
        pc = Poly3DCollection(self.faces, facecolors=self.cols, edgecolors=self.edges,
                              linewidths=self.lws, zsort='average')
        pc.set_antialiased(True)
        ax.add_collection3d(pc)


def add_floor(ax, x0=-240, x1=1140, y0=-360, y1=820, z=0.0):
    sc = Scene3D()
    sc.quad([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)],
            base=np.array([0.905, 0.900, 0.882]), edge=(0.84, 0.835, 0.815), lw=0.5, unlit=True)
    sc.draw(ax)


def add_shadow(ax, x0, x1, y0, y1, z=0.5):
    for grow, a in ((28, 0.05), (15, 0.065), (5, 0.08)):
        dx, dy = -16 - grow * 0.5, -12 - grow * 0.35
        pts = [(x0 - grow + dx, y0 - grow + dy, z),
               (x1 + grow + dx, y0 - grow + dy, z),
               (x1 + grow + dx, y1 + grow + dy, z),
               (x0 - grow + dx, y1 + grow + dy, z)]
        ax.add_collection3d(Poly3DCollection([pts], facecolors=[(0.15, 0.15, 0.14, a)],
                                             edgecolors='none', zsort='min'))


def build_front_panel(sc, dy=0.0, dz=0.0):
    """Цельногнутый фасад-кофр R1: зеркало X=80..820 + скруглённые колонны R80 по краям (до шва Y=80)."""
    x0, x1 = CR, W - CR
    z0, z1 = R.PLINTH_H + dz, R.BODY_TOP + dz
    nx = 8
    for i in range(nx):
        xa = x0 + (x1 - x0) * i / nx
        xb = x0 + (x1 - x0) * (i + 1) / nx
        sc.quad([(xa, dy, z0), (xb, dy, z0), (xb, dy, z1), (xa, dy, z1)],
                base=STEEL, smooth=True, lw=0.2)
    sc.box(x0, x1, dy, dy + 20.0, z0, z0 + 2.0, base=STEEL * 0.9)
    sc.box(x0, x1, dy, dy + 24.0, z1 - 2.0, z1, base=STEEL * 0.95)
    # Вальцованные колонны R80 входят в сам кофр R1 (от Y=0 до шва Y=80 мм!)
    n_seg = 12
    angs_l = np.linspace(-math.pi / 2.0, -math.pi, n_seg + 1)
    for i in range(n_seg):
        a0, a1 = angs_l[i], angs_l[i + 1]
        p0 = (CR + CR * math.cos(a0), CR + CR * math.sin(a0) + dy)
        p1 = (CR + CR * math.cos(a1), CR + CR * math.sin(a1) + dy)
        sc.quad([(p1[0], p1[1], z0), (p0[0], p0[1], z0), (p0[0], p0[1], z1), (p1[0], p1[1], z1)],
                base=STEEL, smooth=(i < n_seg - 1), lw=0.45)
    angs_r = np.linspace(-math.pi / 2.0, 0.0, n_seg + 1)
    for i in range(n_seg):
        a0, a1 = angs_r[i], angs_r[i + 1]
        p0 = (W - CR + CR * math.cos(a0), CR + CR * math.sin(a0) + dy)
        p1 = (W - CR + CR * math.cos(a1), CR + CR * math.sin(a1) + dy)
        sc.quad([(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)],
                base=STEEL, smooth=(i < n_seg - 1), lw=0.45)


def build_radius_wing(sc, side='L', fold_deg=0.0, off=(0.0, 0.0, 0.0)):
    """
    Плоское ступенчатое боковое крыло (R2 левое / R3 правое) длиной 520 мм от шва Y=80 до Y=600.
    Ось скрытой петли находится на шве Y=80 мм (как вертикальный шов на фото референса!).
    """
    ox, oy, oz = off
    z0, z_lo, z_hi = R.PLINTH_H, R.WORK_SHELF_Z, R.BODY_TOP

    if side == 'L':
        hx, hy = 12.0, CR
        deg_rot = -fold_deg
        q1 = [(0, R.SERVE_D, z0), (0, CR, z0), (0, CR, z_hi), (0, R.SERVE_D, z_hi)]
        q2 = [(0, D, z0), (0, R.SERVE_D, z0), (0, R.SERVE_D, z_lo), (0, D, z_lo)]
        q_shelf = [(0, R.SERVE_D, z_lo), (30, R.SERVE_D, z_lo), (30, D, z_lo), (0, D, z_lo)]
        q_rear = [(30, D, z0), (0, D, z0), (0, D, z_lo), (30, D, z_lo)]
        for q in (q1, q2, q_shelf, q_rear):
            qr = [(x + ox, y + oy, z + oz) for x, y, z in rot_z(q, hx, hy, deg_rot)]
            sc.quad(qr, base=STEEL, lw=0.45)
    else:
        hx, hy = W - 26.0, CR
        deg_rot = +fold_deg
        q1 = [(W, CR, z0), (W, R.SERVE_D, z0), (W, R.SERVE_D, z_hi), (W, CR, z_hi)]
        q2 = [(W, R.SERVE_D, z0), (W, D, z0), (W, D, z_lo), (W, R.SERVE_D, z_lo)]
        q_shelf = [(W - 30, R.SERVE_D, z_lo), (W, R.SERVE_D, z_lo), (W, D, z_lo), (W - 30, D, z_lo)]
        q_rear = [(W, D, z0), (W - 30, D, z0), (W - 30, D, z_lo), (W, D, z_lo)]
        q_step = [(W - 2, R.SERVE_D, z_lo), (W, R.SERVE_D, z_lo), (W, R.SERVE_D, z_hi), (W - 2, R.SERVE_D, z_hi)]
        for q in (q1, q2, q_shelf, q_rear, q_step):
            qr = [(x + ox, y + oy, z + oz) for x, y, z in rot_z(q, hx, hy, deg_rot)]
            sc.quad(qr, base=STEEL, lw=0.45)


def build_serve_cap(sc, off=(0.0, 0.0, 0.0), show_perf=True):
    """Верхний радиусный венец выдачи R4 (900 × 180 × 30 мм, отм. 1020..1050) со скруглениями R80 спереди."""
    ox, oy, oz = off
    z0, z1 = R.BODY_TOP + oz, H + oz
    sd = R.SERVE_D
    n_seg = 12

    # Контур верхней крышки со скруглёнными передними углами R80:
    poly2d = [(CR, 0.0), (W - CR, 0.0)]
    for i in range(1, n_seg + 1):
        a = -math.pi / 2.0 + (math.pi / 2.0) * i / n_seg
        poly2d.append((W - CR + CR * math.cos(a), CR + CR * math.sin(a)))
    poly2d += [(W, sd), (0.0, sd)]
    for i in range(n_seg + 1):
        a = math.pi + (math.pi / 2.0) * i / n_seg
        poly2d.append((CR + CR * math.cos(a), CR + CR * math.sin(a)))

    # Боковая обечайка венца высотой 30 мм (формирует характерный поясок-шапку референса!):
    for i in range(len(poly2d) - 1):
        x_a, y_a = poly2d[i]
        x_b, y_b = poly2d[i + 1]
        if math.hypot(x_b - x_a, y_b - y_a) < 0.5:
            continue
        is_curve = (x_a < CR - 0.1 or x_b < CR - 0.1 or x_a > W - CR + 0.1 or x_b > W - CR + 0.1) and (y_a < CR + 0.5 and y_b < CR + 0.5)
        sc.quad([(x_a + ox, y_a + oy, z0), (x_b + ox, y_b + oy, z0),
                 (x_b + ox, y_b + oy, z1), (x_a + ox, y_a + oy, z1)],
                base=STEEL_CAP, smooth=is_curve, lw=0.4)

    # Фартук от рабочей столешницы 850 до низа венца 1020 (закрывает перепад сзади полки выдачи)
    if abs(oz) < 1.0:
        for ix in range(8):
            xa, xb = W * ix / 8.0, W * (ix + 1) / 8.0
            sc.quad([(xa + ox, sd + oy, R.WORK_H), (xb + ox, sd + oy, R.WORK_H),
                     (xb + ox, sd + oy, z0), (xa + ox, sd + oy, z0)],
                    base=STEEL * 0.94, smooth=True)

    # Верхняя плоскость венца (три зоны: левое скругление, центральная рамка + перфокассета, правое скругление)
    # Левый скруглённый сектор X = 0..110
    left_top = [(110.0, 0.0), (110.0, sd), (0.0, sd)]
    for i in range(n_seg + 1):
        a = math.pi + (math.pi / 2.0) * i / n_seg
        left_top.append((CR + CR * math.cos(a), CR + CR * math.sin(a)))
    sc.quad([(x + ox, y + oy, z1) for x, y in left_top], base=STEEL_CAP, lw=0.35)

    # Правый скруглённый сектор X = 790..900
    right_top = [(W - 110.0, 0.0)]
    for i in range(1, n_seg + 1):
        a = -math.pi / 2.0 + (math.pi / 2.0) * i / n_seg
        right_top.append((W - CR + CR * math.cos(a), CR + CR * math.sin(a)))
    right_top += [(W, sd), (W - 110.0, sd)]
    sc.quad([(x + ox, y + oy, z1) for x, y in right_top], base=STEEL_CAP, lw=0.35)

    # Центральная часть X = 110..790: рамка + утопленная на 3 мм кассета каплеуловителя
    sc.quad([(110 + ox, 0 + oy, z1), (W - 110 + ox, 0 + oy, z1),
             (W - 110 + ox, 34 + oy, z1), (110 + ox, 34 + oy, z1)], base=STEEL_CAP, smooth=True)
    sc.quad([(110 + ox, sd - 34 + oy, z1), (W - 110 + ox, sd - 34 + oy, z1),
             (W - 110 + ox, sd + oy, z1), (110 + ox, sd + oy, z1)], base=STEEL_CAP, smooth=True)
    sc.quad([(110 + ox, 34 + oy, z1 - 2.5), (W - 110 + ox, 34 + oy, z1 - 2.5),
             (W - 110 + ox, sd - 34 + oy, z1 - 2.5), (110 + ox, sd - 34 + oy, z1 - 2.5)],
            base=STEEL * 0.96, lw=0.45)

    if show_perf:
        for r_i in range(3):
            yy = 48.0 + r_i * 28.0
            for xx in range(132, int(W - 155), 42):
                if 345 < xx < 525 and r_i == 1:
                    continue
                sc.quad([(xx + ox, yy + oy, z1 - 1.8), (xx + 28 + ox, yy + oy, z1 - 1.8),
                         (xx + 28 + ox, yy + 3.2 + oy, z1 - 1.8), (xx + ox, yy + 3.2 + oy, z1 - 1.8)],
                        base=np.array([0.28, 0.29, 0.30]), unlit=True, smooth=True)


def build_worktop(sc, off=(0.0, 0.0, 0.0)):
    """Рабочая столешница R5 на высоте 850 мм (4 × GN 1/9 + мойка GN 1/2)."""
    ox, oy, oz = off
    y0, y1 = R.SERVE_D + oy, D + oy
    z0, z1 = R.WORK_SHELF_Z + oz, R.WORK_H + oz
    holes = []
    for g in (*R.CUT_GNS, *R.CUT_SINKS):
        holes.append((g['x'] + ox, g['x'] + g['w'] + ox,
                      g['y'] + R.SERVE_D + oy, g['y'] + g['h'] + R.SERVE_D + oy))
    xs = sorted({2.0 + ox, W - 2.0 + ox, *[h[0] for h in holes], *[h[1] for h in holes]})
    ys = sorted({y0, y1, *[h[2] for h in holes], *[h[3] for h in holes]})
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if any(h[0] <= cx <= h[1] and h[2] <= cy <= h[3] for h in holes):
                continue
            sc.quad([(xs[i], ys[j], z1), (xs[i + 1], ys[j], z1),
                     (xs[i + 1], ys[j + 1], z1), (xs[i], ys[j + 1], z1)],
                    base=STEEL_WORK, smooth=True)
    # задний борт столешницы
    sc.quad([(2 + ox, y1, z0), (W - 2 + ox, y1, z0), (W - 2 + ox, y1, z1), (2 + ox, y1, z1)],
            base=STEEL_WORK, lw=0.4)
    # ёмкости GN
    for idx, (hx0, hx1, hy0, hy1) in enumerate(holes):
        depth = 70.0 if idx < 4 else 155.0
        zb = z1 - depth
        sc.quad([(hx0, hy0, zb), (hx1, hy0, zb), (hx1, hy1, zb), (hx0, hy1, zb)],
                base=DARK_BASIN * 0.9, unlit=True)
        sc.quad([(hx0, hy1, z1), (hx1, hy1, z1), (hx1, hy1, zb), (hx0, hy1, zb)],
                base=DARK_BASIN * 1.15, unlit=True)
        sc.quad([(hx0, hy0, z1), (hx0, hy1, z1), (hx0, hy1, zb), (hx0, hy0, zb)],
                base=DARK_BASIN * 1.30, unlit=True)


def build_folded_pack(sc):
    """
    Панель 3: Станция в сложенном транспортном пакете 900 × 135 × 1020 мм (либо 900 × 1020 × 135 мм плашмя).
    Крылья R2/R3 складываются по скрытым петлям на шве Y=80 мм ровно внутрь ниши кофра R1 шириной 900 мм!
    """
    build_front_panel(sc, dy=0.0, dz=0.0)
    # Левое плоское крыло (520 мм) сложено 1-м слоем внутрь кофра (X = 12..532, Y = 76..80)
    sc.box(12.0, 532.0, 76.0, 80.0, R.PLINTH_H, R.WORK_SHELF_Z, base=STEEL * 0.94, lw=0.45)
    # Правое плоское крыло (520 мм) сложено 2-м слоем внутрь кофра (X = 368..888, Y = 94..98)
    sc.box(W - 532.0, W - 12.0, 94.0, 98.0, R.PLINTH_H, R.WORK_SHELF_Z, base=STEEL * 0.90, lw=0.45)
    # Вложенная за крыльями столешница R5 (896 × 420 × 30) и сверху венец R4 (900 × 180 × 30)
    sc.box(4.0, W - 4.0, 102.0, 132.0, 60.0, 480.0, base=STEEL_WORK, lw=0.45)
    sc.box(2.0, W - 2.0, 102.0, 132.0, 515.0, 695.0, base=STEEL_CAP, lw=0.45)
    # Две транспортные стяжки по краям кофра
    strap_col = np.array([0.18, 0.19, 0.20])
    for sx in (185.0, W - 185.0):
        sc.box(sx - 12.0, sx + 12.0, -2.0, 135.0, 10.0, 1022.0, base=strap_col, lw=0.2)


def annotate3d(ax, x, y, z, text, dx=0, dy=0, size=8.8):
    x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
    ax.annotate(text, xy=(x2, y2), xytext=(dx, dy), textcoords='offset points',
                ha='center', va='center', fontsize=size, fontweight='bold', color='#1d1f21',
                zorder=100, bbox=dict(boxstyle='round,pad=0.28', fc='#fbfaf7', ec='#8c8d88', lw=0.7))


def setup_ax(ax, xlim, ylim, zlim, elev=24, azim=-56):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], (zlim[1] - zlim[0]) * 0.94))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type('ortho')
    ax.set_axis_off()
    ax.patch.set_alpha(0)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig = plt.figure(figsize=(18.5, 8.8), dpi=260)
    fig.patch.set_facecolor('#eeebe4')

    axbg = fig.add_axes([0, 0, 1, 1], zorder=0)
    axbg.set_axis_off()
    from matplotlib.colors import LinearSegmentedColormap
    g = np.linspace(0, 1, 256).reshape(-1, 1)
    axbg.imshow(g, extent=[0, 1, 0, 1], aspect='auto',
                cmap=LinearSegmentedColormap.from_list('bg', ['#f7f5f0', '#e4e0d6']), origin='lower')

    # Шапка
    fig.text(0.028, 0.942, 'ПАСИФИК ТУРБО · PK-900R', fontsize=24, fontweight='bold', color='#18191b')
    fig.text(0.028, 0.902, 'СКЛАДНАЯ РАДИУСНАЯ СТАНЦИЯ (AISI 304, R80) В ГАБАРИТАХ БАЗОВОЙ МОДЕЛИ 900 × 600 × 1050 ММ',
             fontsize=10.0, fontweight='bold', color='#525456')
    fig.text(0.028, 0.872, 'цельный фасад без горизонтальных швов · скруглённые колонны R80 · выдача 1050 мм / рабочая зона 850 мм · пакет в сложении 135 мм',
             fontsize=9.5, color='#5e605e')
    fig.text(0.972, 0.942, 'конструктивная схема', fontsize=11.5, color='#5e605e', ha='right')
    fig.text(0.972, 0.910, 'масса ≈ 31,0 кг · сборка 2 мин без инструмента', fontsize=9.8, color='#b8492a', fontweight='bold', ha='right')
    fig.text(0.972, 0.882, '4 × GN 1/9 + мойка GN 1/2 (преемственность с PK-900)', fontsize=8.8, color='#6f706d', ha='right')
    fig.add_artist(plt.Line2D([0.028, 0.972], [0.856, 0.856], color='#18191b', lw=1.2))

    rects = [
        (0.015, 0.075, 0.325, 0.725),
        (0.345, 0.075, 0.335, 0.725),
        (0.685, 0.075, 0.300, 0.725),
    ]
    heads = [
        ('1 · В РАБОТЕ (900 × 600 × 1050 ММ)', 'монолитный фасад 740×1008 · углы R80 · борт выдачи 1050 / столешница 850'),
        ('2 · СХЕМА ТРАНСФОРМАЦИИ (2 МИНУТЫ)', 'крылья R2/R3 раскрываются на скрытых петлях → столешница R5 → замок-венец R4'),
        ('3 · СЛОЖЕННЫЙ КОФР (ТОЛЩИНА 135 ММ)', 'крылья сложены гармошкой за фасад · столешница и венец уложены внутрь'),
    ]

    # --- 1. В СБОРЕ
    ax1 = fig.add_axes(rects[0], projection='3d', computed_zorder=False)
    add_floor(ax1, -180, 1080, -280, 760)
    add_shadow(ax1, 0, W, 0, D)
    sc1 = Scene3D()
    build_front_panel(sc1)
    build_radius_wing(sc1, 'L', fold_deg=0.0)
    build_radius_wing(sc1, 'R', fold_deg=0.0)
    build_worktop(sc1)
    build_serve_cap(sc1, show_perf=True)
    sc1.draw(ax1)
    setup_ax(ax1, (-180, 1080), (-280, 760), (-10, 1140), elev=26, azim=-54)
    annotate3d(ax1, 450, 0, 520, 'R1 · цельный фасад', dy=-6)
    annotate3d(ax1, 860, 40, 680, 'R80', dx=14)
    annotate3d(ax1, 450, 90, 1060, '1050 · выдача R4', dy=12)
    annotate3d(ax1, 720, 420, 860, '850 · рабочая R5', dx=18, dy=10)

    # --- 2. КИНЕМАТИКА РАСКЛАДЫВАНИЯ
    ax2 = fig.add_axes(rects[1], projection='3d', computed_zorder=False)
    add_floor(ax2, -240, 1160, -340, 860)
    add_shadow(ax2, 0, W, 0, D)
    sc2 = Scene3D()
    build_front_panel(sc2)
    build_radius_wing(sc2, 'L', fold_deg=32.0)     # в процессе раскрытия
    build_radius_wing(sc2, 'R', fold_deg=18.0)     # в процессе раскрытия
    # Откидная консоль-перегородка R6 внутри
    sc2.box(R.SEP_X - 1.5, R.SEP_X + 1.5, 65.0, 520.0, 12.0, 815.0, base=STEEL * 0.92)
    # Столешница R5 и венец R4 опускаются сверху (показаны вверху на посадке)
    build_worktop(sc2, off=(0.0, 30.0, 260.0))
    build_serve_cap(sc2, off=(0.0, -30.0, 350.0), show_perf=True)
    sc2.draw(ax2)
    setup_ax(ax2, (-260, 1180), (-360, 880), (-20, 1480), elev=23, azim=-58)
    annotate3d(ax2, 40, 260, 520, 'R2 · поворот 90°', dx=-24)
    annotate3d(ax2, 880, 280, 520, 'R3 · поворот 90°', dx=24)
    annotate3d(ax2, 450, 60, 1420, 'R4 · замок-венец', dy=10)
    annotate3d(ax2, 680, 450, 1120, 'R5 · диафрагма GN', dx=20, dy=6)

    # --- 3. В СЛОЖЕННОМ ВИДЕ (вид со стороны ниши кофра — видна укладка крыльев и столешницы!)
    ax3 = fig.add_axes(rects[2], projection='3d', computed_zorder=False)
    add_floor(ax3, -180, 1080, -260, 520)
    add_shadow(ax3, 0, W, 0, 140)
    sc3 = Scene3D()
    build_folded_pack(sc3)
    sc3.draw(ax3)
    setup_ax(ax3, (-200, 1100), (-320, 560), (-10, 1140), elev=24, azim=42)
    annotate3d(ax3, 450, 65, 1055, 'кофр 900 × 135 × 1020 мм', dy=14, size=8.5)
    annotate3d(ax3, 80, 95, 580, 'крылья R2+R3 + R4 + R5\nвнутри ниши R80', dx=22, size=8.2)

    for (rx, ry, rw, rh), (t1, t2) in zip(rects, heads):
        fig.text(rx + 0.008, ry + rh + 0.025, t1, fontsize=11.5, fontweight='bold', color='#18191b')
        fig.text(rx + 0.008, ry + rh + 0.006, t2, fontsize=8.0, color='#5e605e')

    fig.text(0.028, 0.022,
             'ПАСИФИК ТУРБО · PK-900R · параметрическая модель cad/pk_radius_fold.py · комплектные развёртки docs/radius_fold/cnc/*.dxf · размеры в мм',
             fontsize=8.0, color='#7a7b78')
    fig.text(0.972, 0.022, 'сравнение с PK-900: габарит 1:1 · вырезы GN 1:1 · сборка быстрее в 3 раза',
             fontsize=8.0, color='#7a7b78', ha='right')

    fig.savefig(OUT, facecolor=fig.get_facecolor())
    plt.close(fig)
    print('Saved:', OUT)


if __name__ == '__main__':
    main()
