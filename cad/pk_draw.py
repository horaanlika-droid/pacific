# -*- coding: utf-8 -*-
"""Черчёжные примитивы и оформление листа A3 для альбома ПАСИФИК КИТ."""
import math
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas

PW, PH = landscape(A3)          # 1190.55 x 841.89 pt
M = 12 * mm                     # поле

INK = Color(0.09, 0.10, 0.11)
GREY = Color(0.45, 0.46, 0.47)
LIGHT = Color(0.80, 0.81, 0.81)
ACC = Color(0.80, 0.28, 0.13)   # акцент (оранжево-красный)
FILL_TOP = Color(0.94, 0.94, 0.92)
FILL_FRONT = Color(0.86, 0.87, 0.86)
FILL_SIDE = Color(0.72, 0.73, 0.73)
FILL_CUT = Color(1, 1, 1)

FDIR = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FDIR + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', FDIR + 'DejaVuSans-Bold.ttf'))


def txt(c, x, y, s, size=8, font='DV', color=INK, align='l', rot=0):
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if align == 'c':
        c.drawCentredString(0, 0, s)
    elif align == 'r':
        c.drawRightString(0, 0, s)
    else:
        c.drawString(0, 0, s)
    c.restoreState()


def line(c, p1, p2, w=0.4, color=INK, dash=None):
    c.saveState()
    c.setLineWidth(w)
    c.setStrokeColor(color)
    if dash:
        c.setDash(dash, 0)
    c.line(p1[0], p1[1], p2[0], p2[1])
    c.restoreState()


def rect(c, x, y, w, h, stroke=INK, fill=None, lw=0.5, dash=None):
    c.saveState()
    c.setLineWidth(lw)
    if stroke is not None:
        c.setStrokeColor(stroke)
    if fill is not None:
        c.setFillColor(fill)
    if dash:
        c.setDash(dash, 0)
    if fill is not None:
        c.rect(x, y, w, h, stroke=1 if stroke else 0, fill=1)
    else:
        c.rect(x, y, w, h, stroke=1 if stroke else 0, fill=0)
    c.restoreState()


def poly(c, pts, stroke=INK, fill=None, lw=0.5, close=True, dash=None):
    c.saveState()
    c.setLineWidth(lw)
    c.setStrokeColor(stroke)
    if fill is not None:
        c.setFillColor(fill)
    if dash:
        c.setDash(dash, 0)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill is not None else 0)
    c.restoreState()


def arrow(c, tip, d, size=2.2, color=INK):
    """стрелка: tip — остриё, d — единичное направление к острию"""
    px, py = -d[1], d[0]
    base = (tip[0] - d[0] * size * 2.0, tip[1] - d[1] * size * 2.0)
    poly(c, [tip, (base[0] + px * size, base[1] + py * size),
             (base[0] - px * size, base[1] - py * size)], stroke=color, fill=color, lw=0.2)


def dim_h(c, x1, x2, y, label, size=6.5, ext=3.0, above=True, color=INK, off=None):
    if abs(x2 - x1) < 0.6:
        return
    d = (1, 0) if x2 > x1 else (-1, 0)
    line(c, (x1, y), (x2, y), 0.35, color)
    arrow(c, (x2, y), d, 1.8, color)
    arrow(c, (x1, y), (-d[0], 0), 1.8, color)
    tw = pdfmetrics.stringWidth(str(label), 'DV', size)
    cx = (x1 + x2) / 2.0
    yy = y + 1.6 if above else y - 1.6 - size * 0.35
    c.saveState()
    c.setFillColor(white)
    c.rect(cx - tw / 2 - 1.2, yy - 2.2, tw + 2.4, size + 2.4, stroke=0, fill=1)
    c.restoreState()
    txt(c, cx, yy, str(label), size, align='c', color=color)


def dim_v(c, y1, y2, x, label, size=6.5, ext=3.0, left=True, color=INK):
    if abs(y2 - y1) < 0.6:
        return
    d = (0, 1) if y2 > y1 else (0, -1)
    line(c, (x, y1), (x, y2), 0.35, color)
    arrow(c, (x, y2), d, 1.8, color)
    arrow(c, (x, y1), (0, -d[1]), 1.8, color)
    cy = (y1 + y2) / 2.0
    txt(c, x - 2.2 if left else x + 2.2, cy - size * 0.35, str(label), size,
        align='r' if left else 'l', color=color, rot=0)


def dim_v_rot(c, y1, y2, x, label, size=6.5, color=INK):
    """вертикальный размер с повёрнутым текстом"""
    if abs(y2 - y1) < 0.6:
        return
    d = (0, 1) if y2 > y1 else (0, -1)
    line(c, (x, y1), (x, y2), 0.35, color)
    arrow(c, (x, y2), d, 1.8, color)
    arrow(c, (x, y1), (0, -d[1]), 1.8, color)
    cy = (y1 + y2) / 2.0
    tw = pdfmetrics.stringWidth(str(label), 'DV', size)
    c.saveState()
    c.setFillColor(white)
    c.translate(x, cy)
    c.rotate(90)
    c.rect(-tw / 2 - 1.2, -size * 0.4 - 1.2, tw + 2.4, size + 2.0, stroke=0, fill=1)
    c.restoreState()
    txt(c, x, cy, str(label), size, align='c', color=color, rot=90)


def ext_line(c, p_from, p_to, color=GREY):
    line(c, p_from, p_to, 0.3, color, dash=None)


def leader(c, p1, p2, label=None, size=6.5, color=INK, align='l'):
    line(c, p1, p2, 0.35, color)
    d = (p2[0] - p1[0], p2[1] - p1[1])
    l = math.hypot(*d) or 1
    arrow(c, p1, (-d[0] / l, -d[1] / l), 1.6, color)
    if label:
        tw = pdfmetrics.stringWidth(str(label), 'DV', size)
        off = 2.5 if align == 'l' else -tw - 2.5
        txt(c, p2[0] + off, p2[1] - size * 0.35, str(label), size, color=color,
            align='l' if align == 'l' else 'l')


def bubble(c, x, y, n, r=8, color=INK, fill=white, size=8.5):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.circle(x, y, r, stroke=1, fill=1)
    c.restoreState()
    txt(c, x, y - size * 0.35, str(n), size, font='DVB', align='c', color=color)


def wrap(c, x, y, w, s, size=8, leading=None, font='DV', color=INK, align='l'):
    leading = leading or size * 1.42
    c.setFont(font, size)
    c.setFillColor(color)
    words = s.split()
    lines, cur = [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) <= w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines):
        if align == 'l':
            c.drawString(x, y - i * leading, ln)
        elif align == 'c':
            c.drawCentredString(x, y - i * leading, ln)
        else:
            c.drawRightString(x, y - i * leading, ln)
    return y - len(lines) * leading


def para(c, x, y, w, s, size=8, leading=None, font='DV', color=INK):
    """абзац с поддержкой переводов строк"""
    leading = leading or size * 1.42
    for chunk in s.split('\n'):
        y = wrap(c, x, y, w, chunk, size, leading, font, color)
    return y


# ------------------------------------------------------------------ таблица
def table(c, x, y_top, cols, rows, size=7.2, head_size=7.2, row_h=None,
          head_fill=Color(0.90, 0.90, 0.88), grid=Color(0.62, 0.63, 0.64),
          align=None, pad=3.0, zebra=True):
    """cols — список ширин; rows — список списков строк (первая — шапка)."""
    n = len(cols)
    align = align or ['l'] * n
    row_h = row_h or (size + 4.2)
    # высоты строк с переносом
    heights = []
    for r_i, row in enumerate(rows):
        maxl = 1
        for j, cell in enumerate(row):
            fs = head_size if r_i == 0 else size
            fnt = 'DVB' if r_i == 0 else 'DV'
            wcell = cols[j] - 2 * pad
            lines = 0
            for chunk in str(cell).split('\n'):
                words, cur = chunk.split(), ''
                nl = 1
                for wd in words:
                    t = (cur + ' ' + wd).strip()
                    if pdfmetrics.stringWidth(t, fnt, fs) <= wcell:
                        cur = t
                    else:
                        nl += 1
                        cur = wd
                lines += nl
            maxl = max(maxl, lines)
        heights.append(max(row_h, maxl * (size + 2.6) + 3.0))
    y = y_top
    for r_i, row in enumerate(rows):
        h = heights[r_i]
        y -= h
        if r_i == 0:
            rect(c, x, y, sum(cols), h, stroke=None, fill=head_fill, lw=0)
        elif zebra and r_i % 2 == 0:
            rect(c, x, y, sum(cols), h, stroke=None, fill=Color(0.965, 0.965, 0.955), lw=0)
        cx = x
        for j, cell in enumerate(row):
            fs = head_size if r_i == 0 else size
            fnt = 'DVB' if r_i == 0 else 'DV'
            tx = cx + pad
            if align[j] == 'c':
                tx = cx + cols[j] / 2.0
            elif align[j] == 'r':
                tx = cx + cols[j] - pad
            yy = y + h - pad - fs * 0.85
            c.setFillColor(INK)
            c.setFont(fnt, fs)
            for chunk in str(cell).split('\n'):
                if align[j] == 'c':
                    c.drawCentredString(tx, yy, chunk)
                elif align[j] == 'r':
                    c.drawRightString(tx, yy, chunk)
                else:
                    c.drawString(tx, yy, chunk)
                yy -= fs + 2.6
            cx += cols[j]
        line(c, (x, y), (x + sum(cols), y), 0.35, grid)
    # вертикали
    cx = x
    line(c, (x, y_top), (x, y_top - sum(heights)), 0.5, grid)
    for wd in cols:
        cx += wd
        line(c, (cx, y_top), (cx, y_top - sum(heights)), 0.5, grid)
    return y_top - sum(heights)


# ------------------------------------------------------------------ лист
TOTAL_PAGES = 14


def sheet(c, title, page, subtitle='', scale='', total=TOTAL_PAGES, note=''):
    c.setFillColor(white)
    c.rect(0, 0, PW, PH, stroke=0, fill=1)
    # рамка
    rect(c, M * 0.6, M * 0.6, PW - 1.2 * M, PH - 1.2 * M, stroke=INK, lw=0.9)
    # шапка
    line(c, (M * 0.6, PH - 22 * mm), (PW - M * 0.6, PH - 22 * mm), 0.5, INK)
    txt(c, M * 0.6 + 4 * mm, PH - 13 * mm, 'ПАСИФИК КИТ', 15, 'DVB')
    txt(c, M * 0.6 + 4 * mm + 60 * mm, PH - 13.2 * mm,
        'мобильная барная станция  ·  900 × 600 × 1050  ·  8 элементов', 8.5, color=GREY)
    txt(c, PW - M * 0.6 - 4 * mm, PH - 12.5 * mm, 'PK-900  ·  рев. B  ·  08.11.2026',
        8, align='r', color=GREY)
    # название листа
    txt(c, M * 0.6 + 4 * mm, PH - 18.5 * mm, title.upper(), 10.5, 'DVB')
    if subtitle:
        txt(c, M * 0.6 + 4 * mm + pdfmetrics.stringWidth(title.upper(), 'DVB', 10.5) + 9 * mm,
            PH - 18.4 * mm, subtitle, 8, color=GREY)
    # подвал
    line(c, (M * 0.6, 14 * mm), (PW - M * 0.6, 14 * mm), 0.5, INK)
    txt(c, M * 0.6 + 4 * mm, 8.5 * mm,
        'ПАСИФИК КИТ · PK-900 · альбом проекта и комплект DXF · размеры в мм · '
        'материал AISI 304', 7, color=GREY)
    txt(c, PW - M * 0.6 - 4 * mm, 8.5 * mm, 'лист %d / %d' % (page, total), 7.5,
        align='r', color=GREY)
    if scale:
        txt(c, PW - M * 0.6 - 4 * mm, 11.6 * mm, 'масштаб ' + scale, 7.5, align='r', color=GREY)
    if note:
        txt(c, M * 0.6 + 4 * mm, 11.6 * mm, note, 7, color=GREY)
    return M * 0.6 + 6 * mm, PH - 26 * mm, PW - 1.2 * M - 12 * mm


def new_canvas(path):
    c = pdfcanvas.Canvas(path, pagesize=(PW, PH))
    c.setTitle('ПАСИФИК КИТ — мобильная барная станция · альбом проекта')
    c.setAuthor('PK-900 project')
    c.setSubject('Разборная барная станция из нержавеющей стали, 8 элементов, плоский чехол')
    return c


# ------------------------------------------------------------------ изометрия
C30 = 0.8660254037844386


def _p3(p):
    # изометрия: камера спереди-справа-сверху (+X, -Y, +Z)
    x, y, z = p
    return ((x + y) * C30, z - 0.5 * x + 0.5 * y)


def _station_bbox(items):
    xs, ys = [], []
    for it in items:
        x0, x1, y0, y1, z0, z1 = it['box']
        ox, oy, oz = it['off']
        for xx in (x0, x1):
            for yy in (y0, y1):
                for zz in (z0, z1):
                    u, v = _p3((xx + ox, yy + oy, zz + oz))
                    xs.append(u)
                    ys.append(v)
    return min(xs), min(ys), max(xs), max(ys)


def draw_iso(c, items, rect, lw=0.55, pad=6.0, labels=None, accent=None,
             bbox_items=None):
    """items: [dict(code, box=(x0,x1,y0,y1,z0,z1), off=(dx,dy,dz),
                     holes=[(x,y,w,h,r)] , fill=..)] ; rect=(x,y,w,h)"""
    x0r, y0r, w_r, h_r = rect
    bx0, by0, bx1, by1 = _station_bbox(bbox_items or items)
    sc_ = min((w_r - 2 * pad) / (bx1 - bx0), (h_r - 2 * pad) / (by1 - by0))
    ox = x0r + pad - bx0 * sc_ + ((w_r - 2 * pad) - (bx1 - bx0) * sc_) / 2
    oy = y0r + pad - by0 * sc_ + ((h_r - 2 * pad) - (by1 - by0) * sc_) / 2

    def P(p):
        u, v = _p3(p)
        return (ox + u * sc_, oy + v * sc_)

    def face(pts3, fill, stroke=INK):
        poly(c, [P(p) for p in pts3], stroke, fill, lw)

    order = []
    for it in items:
        x0, x1, y0, y1, z0, z1 = it['box']
        oxx, oyy, ozz = it['off']
        T = lambda p, a=oxx, b=oyy, c=ozz: (p[0] + a, p[1] + b, p[2] + c)
        depth = ((x0 + x1) / 2 + oxx) - ((y0 + y1) / 2 + oyy) + ((z0 + z1) / 2 + ozz)
        order.append((depth, it, T))
    order.sort(key=lambda t: t[0])
    for depth, it, T in order:
        if it.get('hide'):
            continue
        x0, x1, y0, y1, z0, z1 = it['box']
        f = it.get('fill')
        ac = (it['code'] == accent)
        ff = ACC if ac else (f or FILL_FRONT)
        fs = ACC if ac else (it.get('fill_side') or FILL_SIDE)
        ft = ACC if ac else (it.get('fill_top') or FILL_TOP)
        step = it.get('step')
        if step:
            ym, zlo = step
            # передняя грань
            if (y1 - y0) > 2.0 or abs(it.get('front', 1)):
                face([T((x0, y0, z0)), T((x1, y0, z0)), T((x1, y0, z1)), T((x0, y0, z1))], ff)
            # вертикальный торец уступа (при взгляде спереди-справа он отвёрнут, но виден сверху в разборе)
            if it.get('show_step_top'):
                face([T((x0, ym, zlo)), T((x1, ym, zlo)), T((x1, y1, zlo)), T((x0, y1, zlo))], ft)
            # правая L-образная грань
            face([T((x1, y0, z0)), T((x1, y1, z0)), T((x1, y1, zlo)),
                  T((x1, ym, zlo)), T((x1, ym, z1)), T((x1, y0, z1))], fs)
            # верхняя грань передней стойки
            face([T((x0, y0, z1)), T((x1, y0, z1)), T((x1, ym, z1)), T((x0, ym, z1))], ft)
        else:
            # передняя грань
            if (y1 - y0) > 2.0 or abs(it.get('front', 1)):
                face([T((x0, y0, z0)), T((x1, y0, z0)), T((x1, y0, z1)), T((x0, y0, z1))], ff)
            # правая грань
            face([T((x1, y0, z0)), T((x1, y1, z0)), T((x1, y1, z1)), T((x1, y0, z1))], fs)
            # верхняя грань
            face([T((x0, y0, z1)), T((x1, y0, z1)), T((x1, y1, z1)), T((x0, y1, z1))], ft)
        # вырезы в верхней плоскости
        for h in (it.get('holes') or []):
            hx, hy, hw, hh, hr = h
            pts = _rrect3(hx, hy, hw, hh, hr, z1)
            poly(c, [P(T(p)) for p in pts], Color(.45, .47, .47), white, lw * 0.8)
        # перфорация-намёк
        if it.get('perf'):
            yy = y0 + 12
            while yy < y1 - 6:
                p1 = P(T((x0 + 24, yy, z1)))
                p2 = P(T((x1 - 24, yy, z1)))
                line(c, p1, p2, 0.3, Color(.52, .54, .53))
                yy += 22
    return (ox, oy, sc_)


def _rrect3(x, y, w, h, r, z):
    import math as _m
    if r <= 0:
        return [(x, y, z), (x + w, y, z), (x + w, y + h, z), (x, y + h, z)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
                       (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for i in range(5):
            a = _m.radians(a0 + 90 * i / 4)
            pts.append((cx + r * _m.cos(a), cy + r * _m.sin(a), z))
    return pts
