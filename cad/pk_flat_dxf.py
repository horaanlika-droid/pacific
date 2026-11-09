# -*- coding: utf-8 -*-
"""PK-FLAT-900 · экспорт DXF 1:1 (рез) + раскрой на листы."""
import os
import ezdxf
import pk_flat as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'flat', 'cnc')
LAYERS = [('CUT', 7), ('INFO', 3), ('SHEET', 8), ('NEST', 4)]


def _slug(s):
    tbl = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh',
           'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
           'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
           'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y',
           'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', ' ': '_', ':': '', ',': '',
           '-': '_', '(': '', ')': '', '/': '_', '.': '', '×': 'x'}
    out = ''.join(tbl.get(ch, ch) for ch in s.lower().replace('ё', 'e'))
    return ''.join(ch for ch in out if ch.isalnum() or ch == '_')[:44]


def new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.MM
    doc.header['$INSUNITS'] = 4
    doc.header['$LUNITS'] = 2
    for name, color in LAYERS:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    return doc


def draw_part(msp, p, ox=0.0, oy=0.0, label=True, layer='CUT', rot=0):
    def T(x, y):
        return (ox + y, oy + x) if rot else (ox + x, oy + y)

    msp.add_lwpolyline([T(x, y) for x, y in p.outline()], close=True,
                       dxfattribs={'layer': layer})
    for c in p.cuts:
        msp.add_lwpolyline([T(x, y) for x, y in c], close=True,
                           dxfattribs={'layer': layer})
    if not label:
        return
    b = p.bbox()
    y = b[1] - 26
    msp.add_text('%s  %s   %d шт.' % (p.code, p.name, p.qty), height=9,
                 dxfattribs={'layer': 'INFO'}).set_placement((b[0], y))
    msp.add_text('AISI 304, t=%.1f мм   %dx%d мм   %.2f кг/шт   рез + зачистка кромок'
                 % (p.t, p.w, p.h, p.mass() / p.qty), height=6,
                 dxfattribs={'layer': 'INFO'}).set_placement((b[0], y - 14))
    msp.add_text('БЕЗ ГИБОВ. Сборка «лист в лист»: шипы заподлицо 1,2 мм '
                 '(только гребень F11→F12 — 6,8), пазы 1,45 мм (t+0,25). '
                 'Внутренние углы пазов скруглить R0,5.', height=5.2,
                 dxfattribs={'layer': 'INFO'}).set_placement((b[0], y - 25))
    msp.add_text('PK-FLAT-900 · рев. E · 09.11.2026 · координаты — проекция станции, мм', height=5,
                 dxfattribs={'layer': 'INFO'}).set_placement((b[0], y - 34))


def export_parts():
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for p in F.sheet_parts():
        doc = new_doc()
        msp = doc.modelspace()
        draw_part(msp, p)
        path = os.path.join(OUT, 'PK-FLAT-%s_%s.dxf' % (p.code, _slug(p.name)))
        doc.saveas(path)
        paths.append(path)
    return paths


# ------------------------------------------------------------------ раскрой
SHEETS = [('S1', 1250.0, 2500.0), ('S2', 1250.0, 2500.0)]

# Раскладка задана вручную (лист, код, x, y, поворот 0/90) и проверяется ниже:
# детали крупные, автоматический полочный укладчик их не собирает.
LAYOUT = {
    'S1': [('F11', 12, 12, 0), ('F13', 12, 862, 0), ('F5', 12, 1696, 0),
           ('F12', 12, 2302, 0),
           ('F3', 920, 12, 0), ('F3', 920, 197, 0),
           ('F4', 920, 382, 0), ('F4', 920, 419, 0),
           ('F7', 920, 456, 90), ('F10', 1068, 12, 90),
           ('F1', 1196, 12, 90), ('F1', 1068, 918, 90),
           ('F8', 1196, 620, 90), ('F8', 1196, 1526, 90)],
    'S2': [('F2', 12, 12, 0), ('F2', 628, 12, 0),
           ('F14', 12, 856, 0), ('F6', 12, 1700, 0)],
}
EDGE = 12.0


def nest():
    P, _ = F.build()
    out = []
    for name, sw, sh in SHEETS:
        placed, used = [], 0.0
        for code, x, y, rot in LAYOUT[name]:
            p = P[code]
            w, h = (p.w, p.h) if rot == 0 else (p.h, p.w)
            if x < EDGE or y < EDGE or x + w > sw - EDGE + 1e-6 or y + h > sh - EDGE + 1e-6:
                raise ValueError('%s/%s: выходит за лист' % (name, code))
            for (c2, x2, y2, w2, h2) in placed:
                if x < x2 + w2 and x2 < x + w and y < y2 + h2 and y2 < y + h:
                    raise ValueError('%s: %s перекрывает %s' % (name, code, c2))
            placed.append((code, x, y, w, h))
            used += p.area()
        out.append(dict(name=name, w=sw, h=sh, items=[
            (P[c], x, y, rot, w, h) for (c, x, y, w, h) in placed], used=used))
    # все ли детали разложены
    need = {}
    for p in F.sheet_parts():
        need[p.code] = need.get(p.code, 0) + p.qty
    got = {}
    for s in out:
        for (p, x, y, rot, w, h) in s['items']:
            got[p.code] = got.get(p.code, 0) + 1
    if need != got:
        raise ValueError('раскладка не совпадает со спецификацией: %s / %s' % (need, got))
    return out


def export_nest():
    os.makedirs(OUT, exist_ok=True)
    res = []
    for s in nest():
        doc = new_doc()
        msp = doc.modelspace()
        msp.add_lwpolyline([(0, 0), (s['w'], 0), (s['w'], s['h']), (0, s['h'])],
                           close=True, dxfattribs={'layer': 'SHEET'})
        for (p, x, y, rot, w, h) in s['items']:
            if rot:
                msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                                   close=True, dxfattribs={'layer': 'NEST'})
            draw_part(msp, p, x, y, label=True, rot=rot)
        used = s['used'] / 1e6
        msp.add_text('PK-FLAT-900 · %s · AISI 304 · t=1,2 мм · лист %d×%d · зазор %d мм'
                     % (s['name'], s['w'], s['h'], 8), height=12,
                     dxfattribs={'layer': 'INFO'}).set_placement((EDGE, s['h'] - 30))
        msp.add_text('Детали: %d · площадь деталей %.2f м² · заполнение %.0f %% · '
                     'контуры 1:1, слой CUT — рез, слой INFO — подписи'
                     % (len(s['items']), used,
                        100.0 * used / (s['w'] * s['h'] / 1e6)), height=7,
                     dxfattribs={'layer': 'INFO'}).set_placement((EDGE, s['h'] - 46))
        path = os.path.join(OUT, 'PK-FLAT-NEST_%s.dxf' % s['name'].lower())
        doc.saveas(path)
        res.append((s, path, used))
    return res


def index_text():
    ps = F.sheet_parts()
    area = sum(p.area() * p.qty for p in ps)
    mass = sum(p.mass() for p in F.parts())
    cutl = sum(p.cut_len() for p in ps)
    L = ['ПАСИФИК ТУРБО — PK-FLAT-900 «ПАЗ» · рев. E · безгибовая версия',
         'AISI 304 · t = 1,2 мм · мм, 1:1 · слой CUT — рез, INFO — подписи',
         '=' * 78, '']
    for p in ps:
        L.append('%-4s %-42s %6.1f × %-6.1f t=%.1f  %d шт.  %5.2f кг  %s'
                 % (p.code, p.name, p.w, p.h, p.t, p.qty, p.mass() / p.qty,
                    _slug(p.name)))
    L += ['', 'Гибов: 0 · сварки: 0 · чеки Ø4×18: 16 шт. (необязательно)',
          'Площадь листа: %.2f м² · масса металла: %.1f кг · длина реза: %.1f м'
          % (area / 1e6, mass, cutl / 1000.0), '',
          'Раскрой (предварительный, проверить в CAM цеха):']
    for s, path, used in export_nest():
        L.append('  %s  %4.0f × %4.0f: %d дет., %.2f м², заполнение %.0f %%'
                 % (s['name'], s['w'], s['h'], len(s['items']), used,
                    100.0 * used / (s['w'] * s['h'] / 1e6)))
    L += ['', 'Допуски: паз = t + 0,25 мм (1,45). Шип 8 мм. Зазор по контуру 0,2 мм на сторону.',
          'Внутренние углы пазов и шлицев — скруглить R0,5 (разгрузка от трещин).',
          'Кромки притупить: 0,3×45° или скотч-брайт; фасад и столешницу — 400→600.',
          'Деталь = проекция станции: x — ширина, y — глубина от передней плоскости,',
          'z — высота от пола; поэтому на стыке координаты деталей совпадают.',
          '']
    return '\n'.join(L)


def main():
    paths = export_parts()
    (s1, p1, u1), (s2, p2, u2) = export_nest()
    with open(os.path.join(OUT, 'INDEX.txt'), 'w') as f:
        f.write(index_text())
    print('DXF: %d деталей + 2 листа раскроя' % len(paths))
    print('S1: %.2f м²  S2: %.2f м²' % (u1, u2))
    print(OUT)


if __name__ == '__main__':
    main()
