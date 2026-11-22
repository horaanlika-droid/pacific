# -*- coding: utf-8 -*-
"""Экспорт DXF 1:1 для складной радиусной станции ПАСИФИК ТУРБО · PK-900R."""
import os
import ezdxf
import pk_radius_fold as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'radius_fold', 'cnc')
LAYERS = [('CUT', 7), ('BEND', 1), ('ROLL', 5), ('INFO', 3), ('SHEET', 8)]


def new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.MM
    doc.header['$INSUNITS'] = 4
    for name, color in LAYERS:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    doc.layers.get('BEND').dxf.linetype = 'DASHED'
    doc.layers.get('ROLL').dxf.linetype = 'DASHDOT'
    return doc


def _slug(s):
    tbl = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh', 'з': 'z',
           'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
           'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
           'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
           ' ': '_', ':': '', ',': '', '-': '_', '.': '_'}
    s = s.lower().replace('ё', 'e')
    out = ''.join(tbl.get(ch, ch) for ch in s)
    return ''.join(ch for ch in out if ch.isalnum() or ch == '_')[:42]


def export_part(part):
    doc = new_doc()
    msp = doc.modelspace()
    msp.add_lwpolyline(part.outline, close=True, dxfattribs={'layer': 'CUT'})
    for c in part.cuts:
        if c['type'] == 'circle':
            msp.add_circle((c['cx'], c['cy']), c['r'], dxfattribs={'layer': 'CUT'})
        else:
            msp.add_lwpolyline(c['pts'], close=True, dxfattribs={'layer': 'CUT'})
    for b in part.bends:
        lyr = 'ROLL' if b.get('ang', 90) == 0 else 'BEND'
        msp.add_line(b['p1'], b['p2'], dxfattribs={'layer': lyr})
    y = -38
    msp.add_text('%s  %s' % (part.code, part.name), height=11,
                 dxfattribs={'layer': 'INFO'}).set_placement((0, y))
    msp.add_text('Материал: %s   Толщина %.1f мм' % (part.mat, part.t), height=7.5,
                 dxfattribs={'layer': 'INFO'}).set_placement((0, y - 16))
    msp.add_text('Развёртка %.1f × %.1f мм   Масса %.2f кг' %
                 (part.flat_w, part.flat_h, part.mass()), height=7.5,
                 dxfattribs={'layer': 'INFO'}).set_placement((0, y - 30))
    msp.add_text('CUT — рез лазером, BEND — гиб 90° (K=0,33), ROLL — граница вальцовки R80.',
                 height=6.0, dxfattribs={'layer': 'INFO'}).set_placement((0, y - 44))
    fname = 'PK-900R-%s_%s.dxf' % (part.code.replace('.', '_'), _slug(part.name))
    path = os.path.join(OUT, fname)
    doc.saveas(path)
    return path


def export_nesting(parts):
    """Раскрой деталей PK-900R на стандартные листы AISI 304 (2 листа 1250×2500 × 1,2 мм + 1 заготовка 1,0 мм)."""
    r1, r2, r3, r4, r41, r5, r6, r7 = parts
    sheets = [
        ('S1', 1.2, 1250, 2500, [
            (r1, 20, 20, 0),          # 1033.5 × 1047.7
            (r2, 20, 1095, 0),        # 569.7 × 1045.7
            (r3, 615, 1095, 0),       # 569.7 × 1045.7 (615+570=1185 < 1250!)
            (r4, 20, 2170, 0),        # 954.7 × 234.7
        ]),
        ('S2', 1.2, 1250, 1250, [
            (r5, 20, 20, 90),         # 474.7 × 950.7 (повёрнута на 90°)
            (r6, 520, 20, 0),         # 490.0 × 850.7
            (r7, 20, 1005, 0),        # 896.0 × 120.7
        ]),
        ('S3', 1.0, 800, 250, [
            (r41, 25, 25, 0),         # 700.0 × 148.7
        ]),
    ]

    doc = new_doc()
    msp = doc.modelspace()
    ox = 0.0
    for name, t, sw, sh, items in sheets:
        msp.add_lwpolyline([(ox, 0), (ox + sw, 0), (ox + sw, sh), (ox, sh)],
                           close=True, dxfattribs={'layer': 'SHEET'})
        msp.add_text('%s  AISI 304  t=%.1f мм  %d×%d' % (name, t, sw, sh),
                     height=18, dxfattribs={'layer': 'INFO'}).set_placement((ox + 20, sh + 28))
        for part, x, y, rot in items:
            pts = [(ox + x + px, y + py) for (px, py) in
                   (part.outline if rot == 0 else [(qy, part.flat_w - qx) for qx, qy in part.outline])]
            msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT'})
            msp.add_text(part.code, height=14, dxfattribs={'layer': 'INFO'}).set_placement((ox + x + 22, y + 22))
        ox += sw + 220.0
    nest_path = os.path.join(OUT, 'PK-900R-NEST_all_sheets.dxf')
    doc.saveas(nest_path)
    return nest_path, sheets


def build():
    os.makedirs(OUT, exist_ok=True)
    parts = R.all_parts()
    made = [export_part(p) for p in parts]
    nest_path, sheets = export_nesting(parts)
    made.append(nest_path)
    idx_path = os.path.join(OUT, 'INDEX.txt')
    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write('ПАСИФИК ТУРБО · PK-900R — комплект DXF складной радиусной станции (мм, 1:1)\n')
        f.write('=' * 82 + '\n')
        for p in parts:
            f.write('%-5s %-46s %6.1f × %6.1f  t=%.1f  %5.2f кг\n' %
                    (p.code, p.name, p.flat_w, p.flat_h, p.t, p.mass()))
        f.write('\nРаскрой листов:\n')
        for name, t, sw, sh, items in sheets:
            f.write('  %s  AISI 304  %.1f мм  %d × %d: %s\n' %
                    (name, t, sw, sh, ', '.join(it[0].code for it in items)))
    return made


if __name__ == '__main__':
    files = build()
    for fn in files:
        print(fn)
    print('Готово файлов DXF:', len(files))
