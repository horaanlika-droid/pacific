"""План фанерных деталей PK-POP-03 и 07 с внутренними резами."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf
from ezdxf import path
import pk_popup as P

fig, axes = plt.subplots(2, 1, figsize=(14, 9), constrained_layout=True)
for ax, part, title in zip(axes, [P.countertop(), P.tray()], [
        'PK-POP-03 · рабочая столешница · фанера 12 мм',
        'PK-POP-07 · плита выдачи · фанера 12 мм']):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for i, (pts, closed) in enumerate(part.cuts):
        entity = msp.add_lwpolyline(pts, format='xyb', close=closed)
        coords = [(v.x, v.y) for v in path.make_path(entity).flattening(0.1)]
        ax.add_patch(plt.Polygon(coords, closed=closed, facecolor='#d2b48c' if i == 0 else 'white', edgecolor='#262626', linewidth=0.65))
    for x, y, d in part.holes:
        ax.add_patch(plt.Circle((x, y), d / 2, color='#2861a3'))
    ax.set_aspect('equal')
    ax.set_xlim(-15, part.w + 15)
    ax.set_ylim(-20, part.h + 20)
    ax.set_xlabel('мм'); ax.set_ylabel('мм')
    ax.set_title(title, loc='left', fontsize=13, fontweight='bold')
    ax.grid(alpha=.15)
fig.suptitle('Вид сверху: белым показаны сквозные вырезы в фанере; синим — сверление', fontsize=14)
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'docs', 'popup', 'PK-POP-900_otverstiya.png'), dpi=150)
