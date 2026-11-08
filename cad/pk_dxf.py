# -*- coding: utf-8 -*-
"""Экспорт DXF 1:1 для лазерной резки + раскройные листы."""
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment
import pk_geom as G

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dxf')

LAYERS = [('CUT', 7), ('BEND', 1), ('INFO', 3), ('SHEET', 8)]


def new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.MM
    doc.header['$INSUNITS'] = 4
    for name, color in LAYERS:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    doc.layers.get('BEND').dxf.linetype = 'DASHED'
    return doc


def add_outline(msp, pts, layer='CUT'):
    msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': layer})


def add_cut(msp, c):
    if c['type'] == 'circle':
        msp.add_circle((c['cx'], c['cy']), c['r'], dxfattribs={'layer': 'CUT'})
    else:
        msp.add_lwpolyline(c['pts'], close=True, dxfattribs={'layer': 'CUT'})


def part_dxf(part, extra_open=None, path=None):
    doc = new_doc()
    msp = doc.modelspace()
    add_outline(msp, part.outline)
    for c in part.cuts:
        add_cut(msp, c)
    for poly in (extra_open or []):
        msp.add_lwpolyline(poly, close=False, dxfattribs={'layer': 'CUT'})
    for b in part.bends:
        msp.add_line(b['p1'], b['p2'], dxfattribs={'layer': 'BEND'})
    # паспорт детали
    y = -40
    msp.add_text('%s  %s' % (part.code, part.name),
                 height=12, dxfattribs={'layer': 'INFO'}).set_placement((0, y))
    msp.add_text('Материал: %s   Толщина %.1f мм' % (part.mat, part.t),
                 height=8, dxfattribs={'layer': 'INFO'}).set_placement((0, y - 18))
    msp.add_text('Развёртка %.1f x %.1f мм   Масса %.2f кг   Кол-во %d' %
                 (part.flat_w, part.flat_h, part.mass(), part.qty),
                 height=8, dxfattribs={'layer': 'INFO'}).set_placement((0, y - 32))
    msp.add_text('Слой BEND — линии гиба, R1,0 внутр., K=0,33. Слой CUT — рез.',
                 height=6, dxfattribs={'layer': 'INFO'}).set_placement((0, y - 46))
    path = path or os.path.join(OUT, '%s_%s.dxf' % (part.code, _slug(part.name)))
    doc.saveas(path)
    return path


def _slug(s):
    tbl = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh', 'з': 'z',
           'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
           'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
           'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
           ' ': '_', ':': '', ',': '', '-': '_'}
    s = s.lower().replace('ё', 'e')
    out = ''.join(tbl.get(ch, ch) for ch in s)
    return ''.join(ch for ch in out if ch.isalnum() or ch == '_')[:40]


# ------------------------------------------------------------------ узлы
def extra_parts():
    """вспомогательные детали, не относящиеся к металлической стойке"""
    docs = []

    # E8.x — перегородки чехла
    for code, w, h in G.DIVIDERS:
        cuts = [dict(type='poly', pts=G.obround_pts(w / 2, h - 45, 110, 26)),
                dict(type='poly', pts=G.obround_pts(w / 2, 45, 110, 26))]
        p = G.Part(code, 'Перегородка чехла', 'HDPE 3 мм', 3.0, 1, w, h,
                   G.rrect_pts(0, 0, w, h, 15, 8), cuts, [], [], dens=0.95)
        docs.append(p)
    return docs


def nesting():
    """Листы раскроя: (название, толщина, W, H, [(part, x, y, rot)])"""
    e1, e2, e3, e4, e5, e6, e7, e9 = G.all_parts()
    sheets = [
        ('S1', 1.5, 1250, 2500, [(e1, 30, 30, 0), (e2, 30, 1125, 0), (e7, 700, 30, 90),
                                 (e9, 700, 1125, 0)]),
        ('S2', 1.2, 1250, 1200, [(e3, 30, 30, 0), (e4, 30, 415, 0), (e5, 30, 800, 0)]),
        ('S3', 1.0, 1000, 500, [(e6, 30, 30, 0)]),
    ]
    doc = new_doc()
    msp = doc.modelspace()
    ox = 0.0
    for name, t, W, H, items in sheets:
        msp.add_lwpolyline([(ox, 0), (ox + W, 0), (ox + W, H), (ox, H)],
                           close=True, dxfattribs={'layer': 'SHEET'})
        msp.add_text('%s  AISI304 %.1f мм  %d x %d' % (name, t, W, H), height=20,
                     dxfattribs={'layer': 'INFO'}).set_placement((ox + 20, H + 30))
        for part, x, y, rot in items:
            pts = [(ox + x + px, y + py) for (px, py) in
                   ([(qx, qy) for qx, qy in part.outline] if rot == 0 else
                    [(qy, part.flat_w - qx) for qx, qy in part.outline])]
            add_outline(msp, pts)
            msp.add_text(part.code, height=14, dxfattribs={'layer': 'INFO'}).set_placement(
                (ox + x + 20, y + 20))
        ox += W + 200
    path = os.path.join(OUT, 'PK-NEST_all_sheets.dxf')
    doc.saveas(path)
    return path, sheets


def build():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for part in G.all_parts():
        extra = getattr(part, 'hooks', []) + getattr(part, 'tabs', [])
        made.append(part_dxf(part, extra))
    for part in extra_parts():
        made.append(part_dxf(part))
    nest_path, sheets = nesting()
    made.append(nest_path)
    # индекс
    with open(os.path.join(OUT, 'INDEX.txt'), 'w', encoding='utf-8') as f:
        f.write('ПАСИФИК ТУРБО — комплект DXF (мм, 1:1, слой CUT = рез, BEND = гиб)\n')
        f.write('=' * 78 + '\n')
        for p in G.all_parts() + extra_parts():
            f.write('%-6s %-40s %6.1f x %6.1f  t=%.1f  %5.2f кг  %s\n' %
                    (p.code, p.name, p.flat_w, p.flat_h, p.t, p.mass(),
                     _slug(p.name)))
        f.write('\nРаскрой:\n')
        for name, t, W, H, items in sheets:
            f.write('  %s  AISI304 %.1f мм  %d x %d: %s\n' %
                    (name, t, W, H, ', '.join(i[0].code for i in items)))
    return made


if __name__ == '__main__':
    files = build()
    print('\n'.join(files))
    print('готово:', len(files), 'файлов')
