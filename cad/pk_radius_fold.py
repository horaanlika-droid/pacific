# -*- coding: utf-8 -*-
"""
ПАСИФИК ТУРБО · PK-900R (рев. R — радиусная складная в самонесущий кофр).
Точная инженерная геометрия 1:1 с базовой станцией ПАСИФИК ТУРБО PK-900 (900 × 600 × 1050 мм):

Ключевое инженерное решение («кофр-органайзер R80»):
  1) Лицевой блок R1 — это цельновальцованная U-оболочка глубиной 80 мм:
     центральное плоское зеркало 740 × 1008 мм + две скруглённые угловые колонны R80 по краям
     (ширина в сборе ровно 900 мм, глубина ниши за фасадом — 80 мм!).
     На лицевой стороне на границе перехода плоскости в дугу R80 может быть выполнен лёгкий
     декоративный руст (линия касания) либо бесшовный переход вальцовки.
  2) Две ступенчатые боковые стенки R2 (левая) и R3 (правая) длиной по глубине 520 мм
     (80 мм угловой колонны + 520 мм плоского крыла = ровно 600 мм глубины станции!)
     крепятся на скрытых внутренних петлях AISI 304 ровно на линии вертикального шва Y = 80 мм
     (как вертикальный шов на боковине в фото-референсе IMG_7404!).
  3) Складывание без вылета за 900 мм:
     поскольку длина каждого плоского крыла 520 мм < внутренней ширины кофра 896 мм,
     левое крыло складывается внутрь кофра первым слоем (X = 2..522 мм),
     а правое крыло (на петле со смещением 24 мм) ложится поверх него вторым слоем (X = 378..898 мм)!
     Центральная консоль-перегородка R6 (480 × 808 мм) складывается на петле к спинке фасада 0-м слоем.
  4) За сложенными крыльями в ту же нишу укладываются рабочая столешница R5 (896 × 420 × 30 мм)
     и верхний радиусный венец выдачи R4 (900 × 180 × 30 мм).
     Итог — один жёсткий плоский стальной кофр 900 × 135 × 1020 мм (без внешних торчащих углов!).
"""
import math
import pk_geom as G0

# ---------------------------------------------------------------- габариты (соотнесение 1:1 с PK-900)
W, D, H = 900.0, 600.0, 1050.0          # внешний габарит (1:1 с PK-900)
WORK_H = 850.0                          # рабочая столешница на высоте бедра (-200 мм от борта 1050, 1:1 с PK-900)
CORNER_R = 80.0                         # радиус скругления фасадных колонн и венца выдачи

SERVE_D = 180.0                         # глубина полки выдачи (в PK-900 было 140; увеличено до 180 под R80)
WORK_D = D - SERVE_D                    # 420.0 мм — глубина рабочей столешницы (180 + 420 = 600 мм)

PLINTH_H = 12.0                         # теневой плинтус снизу под опоры (1:1 с PK-900)
CAP_H = 30.0                            # высота борта верхнего радиусного венца (1020..1050 мм)
BODY_TOP = H - CAP_H                    # 1020.0 мм — верх колонн R80 и фасада (1:1 с SIDE_TOP в PK-900)
BODY_H = BODY_TOP - PLINTH_H            # 1008.0 мм — чистая высота фасада (= 3×334 + 2×3 в PK-900!)
WORK_FLANGE = 30.0                      # отбортовка рабочей столешницы
WORK_SHELF_Z = WORK_H - WORK_FLANGE     # 820.0 мм — опорная полка столешницы (1:1 с WORK_TOP в PK-900!)

T = 1.2                                 # основная толщина AISI 304 (как в рев. D+ PK-900)
T_PERF = 1.0                            # перфокассета каплеуловителя

FRONT_FACE_W = W - 2.0 * CORNER_R       # 740.0 мм — плоское центральное зеркало фасада
ARC_NEUTRAL = 0.5 * math.pi * (CORNER_R - (1.0 - 0.33) * T)   # 124.40 мм — дуга 90° R80 в развёртке
WING_Y = D - CORNER_R                   # 520.0 мм — глубина откидного плоского крыла (от шва Y=80 до Y=600)
WING_HI_Y = SERVE_D - CORNER_R          # 100.0 мм — участок крыла высотой 1020 мм (под полкой выдачи Y=80..180)
WING_LO_Y = D - SERVE_D                 # 420.0 мм — участок крыла высотой 820 мм (под столешницей Y=180..600)

FOLDED_PACK = (W, 135.0, BODY_TOP)      # 900 × 135 × 1020 мм (стоя) / 900 × 1020 × 135 мм (лёжа)

DEV30, _ = G0._dev(T, 30.0)             # 27.35
DEV25, _ = G0._dev(T, 25.0)             # 22.35
DEV20, _ = G0._dev(T, 20.0)             # 17.35
DEV18, _ = G0._dev(T, 18.0)             # 15.35
DEV15, _ = G0._dev(T, 15.0)             # 12.35
RELIEF = 4.0

# ---------------------------------------------------------------- вырезы столешницы (1:1 с PK-900)
GN_X0, GN_Y0, GN_W, GN_H, GN_R, GN_STEP, GN_N = 48.0, 45.0, 90.0, 160.0, 8.0, 108.0, 4
CUT_GNS = [dict(x=GN_X0 + i * GN_STEP, y=GN_Y0, w=GN_W, h=GN_H, r=GN_R) for i in range(GN_N)]
CUT_SINK = dict(x=535.0, y=45.0, w=300.0, h=240.0, r=12.0)
CUT_SINKS = [CUT_SINK]
SEP_X = 498.5                           # ось перегородки лёд / мойка (1:1 с PK-900)


# ================================================================ R1 · ФАСАД-КОФР С КОЛОННАМИ R80
def front_shell_r80():
    """
    Цельновальцованный лицевой кофр R1:
      - левый петлевой фланец 25 мм (на отметке Y = 80 мм, несёт петли левого крыла R2)
      - левая вальцованная колонна R80 (90°, длина развёртки 124,4 мм)
      - плоский центральный фасад 740 мм (с верхней полкой 25 мм и нижней полкой 20 мм)
      - правая вальцованная колонна R80 (90°, длина развёртки 124,4 мм)
      - правый петлевой фланец 25 мм (на отметке Y = 80 мм, несёт петли правого крыла R3)
    Полная ширина развёртки: 22.35 + 124.40 + 740.0 + 124.40 + 22.35 = 1033.5 мм (входит в стандартный лист 1250 мм!).
    """
    x_l_arc0 = DEV25
    x_face0 = x_l_arc0 + ARC_NEUTRAL            # 146.75
    x_face1 = x_face0 + FRONT_FACE_W            # 886.75
    x_r_arc1 = x_face1 + ARC_NEUTRAL            # 1011.15
    fw = x_r_arc1 + DEV25                       # 1033.50 мм (< 1250 мм листа!)

    y0 = DEV20                                  # 17.35 (нижняя полка только на прямом участке 740 мм)
    y1 = y0 + BODY_H                            # 1025.35
    fh = y1 + DEV25                             # 1047.70 мм

    # Контур: полки 20 (снизу) и 25 (сверху) формуются только на плоском участке 740 мм,
    # чтобы дуги R80 чисто прокатывались на трёхвалковых вальцах без деформации полок!
    outline = [
        (x_face0 + 4.0, 0.0),
        (x_face1 - 4.0, 0.0),
        (x_face1 - 4.0, y0),
        (fw, y0),
        (fw, y1),
        (x_face1 - 4.0, y1),
        (x_face1 - 4.0, fh),
        (x_face0 + 4.0, fh),
        (x_face0 + 4.0, y1),
        (0.0, y1),
        (0.0, y0),
        (x_face0 + 4.0, y0),
    ]
    cuts = []
    # По 3 отверстия Ø6.2 в левом и правом петлевых фланцах (на шве Y = 80 мм, как на референсе!)
    for px in (DEV25 / 2.0, x_r_arc1 + DEV25 / 2.0):
        for hz in (140.0, 504.0, 868.0):
            cuts.append(dict(type='circle', cx=px, cy=y0 + hz, r=3.1))
    # 2 паза в верхней полке под передние зацепы венца R4
    for px in (x_face0 + 150.0, x_face1 - 150.0):
        cuts.append(dict(type='poly', pts=G0.obround_pts(px, y1 + DEV25 / 2.0, 28.0, 10.0)))

    bends = [
        dict(p1=(x_l_arc0, y0), p2=(x_l_arc0, y1), ang=90, note='левый петлевой фланец 25 внутрь (шов Y=80 мм)'),
        dict(p1=(x_face0, y0), p2=(x_face0, y1), ang=0, note='граница вальцовки левой колонны R80'),
        dict(p1=(x_face1, y0), p2=(x_face1, y1), ang=0, note='граница вальцовки правой колонны R80'),
        dict(p1=(x_r_arc1, y0), p2=(x_r_arc1, y1), ang=90, note='правый петлевой фланец 25 внутрь (шов Y=80 мм)'),
        dict(p1=(x_face0 + 4.0, y0), p2=(x_face1 - 4.0, y0), ang=90, note='нижняя полка фасада 20 внутрь'),
        dict(p1=(x_face0 + 4.0, y1), p2=(x_face1 - 4.0, y1), ang=90, note='верхняя полка фасада 25 внутрь'),
    ]
    notes = [
        'Цельная U-оболочка 900 × 80 × 1008 мм: плоский фасад 740 мм плавно переходит в скруглённые колонны R80.',
        'Вертикальный стык с боковыми крыльями проходит ровно на глубине Y = 80 мм (как шов на боковине референса!).',
        'В сложенном виде работает жёстким внешним защитным кофром для всех внутренних деталей.'
    ]
    return G0.Part('R1', 'Фасад-кофр цельногнутый с колоннами R80',
                   'AISI 304, вальцовка R80 + гибка', T, 1, fw, fh, outline, cuts, bends, notes)


# ================================================================ R2 / R3 · КРЫЛО БОКОВОЕ СКЛАДНОЕ (520 ММ)
def folding_wing(mirror=False):
    """
    Плоское ступенчатое боковое крыло глубиной 520 мм (от вертикального шва Y = 80 до тыла Y = 600 мм):
      - участок Y = 80..180 (100 мм): высота до отм. 1020 мм (несёт верхний венец выдачи R4)
      - участок Y = 180..600 (420 мм): высота до отм. 820 мм (несёт рабочую столешницу R5 на высоте 850 мм)
    Поскольку длина крыла 520 мм, при складывании на 90° внутрь кофра шириной 900 мм крыло ложится
    ПОЛНОСТЬЮ внутри габарита 900 мм с запасом 380 мм!
    """
    x_front = DEV25
    x_step = x_front + WING_HI_Y                # 22.35 + 100.0 = 122.35
    x_rear = x_step + WING_LO_Y                 # 122.35 + 420.0 = 542.35
    fw = x_rear + DEV30                         # 569.70 мм

    y0 = DEV18                                  # 15.35 мм — нижняя опорная полка
    y_lo = y0 + (WORK_SHELF_Z - PLINTH_H)       # 15.35 + 808 = 823.35 (отм. 820)
    y_hi = y0 + BODY_H                          # 15.35 + 1008 = 1023.35 (отм. 1020)
    fh = y_hi + DEV25                           # 1045.70 мм

    outline = [
        (x_front + 2.0, 0.0),
        (x_rear, 0.0),
        (x_rear, y0),
        (fw, y0),
        (fw, y_lo),
        (x_rear, y_lo),
        (x_rear, y_lo + DEV30),
        (x_step + 3.0, y_lo + DEV30),
        (x_step + 3.0, y_lo),
        (x_step, y_lo),
        (x_step, fh),
        (x_front + 2.0, fh),
        (x_front + 2.0, y_hi),
        (0.0, y_hi),
        (0.0, y0),
        (x_front + 2.0, y0),
    ]
    cuts = []
    for hz in (140.0, 504.0, 868.0):
        cuts.append(dict(type='circle', cx=x_front / 2.0, cy=y0 + hz, r=3.1))
    for sx in (x_step + 90.0, x_rear - 90.0):
        cuts.append(dict(type='poly', pts=G0.obround_pts(sx, y_lo + DEV30 / 2.0, 24.0, 9.0)))
    for sz in (95.0, 620.0):
        cuts.append(dict(type='poly', pts=G0.obround_pts(x_rear + DEV30 / 2.0, y0 + sz, 9.0, 28.0)))
    for cx, cy in ((x_front, y0), (x_rear, y0), (x_rear, y_lo), (x_step, y_lo), (x_front, y_hi)):
        cuts.append(dict(type='circle', cx=cx, cy=cy, r=RELIEF / 2))

    bends = [
        dict(p1=(x_front, y0), p2=(x_front, y_hi), ang=90, note='передний петлевой фланец 25 внутрь (шов Y=80)'),
        dict(p1=(x_rear, y0), p2=(x_rear, y_lo), ang=90, note='задняя отбортовка 30 внутрь'),
        dict(p1=(x_front + 2.0, y0), p2=(x_rear, y0), ang=90, note='нижняя опорная полка 18 внутрь'),
        dict(p1=(x_front + 2.0, y_hi), p2=(x_step, y_hi), ang=90, note='верхняя полка 25 под венец выдачи (отм. 1020)'),
        dict(p1=(x_step + 3.0, y_lo), p2=(x_rear, y_lo), ang=90, note='опорная полка 30 под столешницу (отм. 820)'),
        dict(p1=(x_front + 8.0, y0 + 480.0), p2=(x_rear - 6.0, y0 + 480.0), ang=90, note='горизонтальное ребро жёсткости'),
        dict(p1=(x_front + 8.0, y0 + 498.0), p2=(x_rear - 6.0, y0 + 498.0), ang=90, note='горизонтальное ребро жёсткости'),
    ]

    if mirror:
        def _mx(pt):
            return (fw - pt[0], pt[1])
        outline = [_mx(p) for p in outline][::-1]
        cuts = [dict(type='circle', cx=fw - c['cx'], cy=c['cy'], r=c['r'])
                if c['type'] == 'circle' else
                dict(type='poly', pts=[_mx(q) for q in c['pts']][::-1]) for c in cuts]
        bends = [dict(p1=_mx(b['p1']), p2=_mx(b['p2']), ang=b['ang'], note=b['note']) for b in bends]

    notes = [
        'Плоское ступенчатое крыло 520 мм (без сложной вальцовки: весь радиус R80 сосредоточен в детали R1!).',
        'На 3 скрытых петлях из AISI 304 складывается на 90° внутрь ниши кофра R1 без выступа за габарит 900 мм.'
    ]
    return G0.Part('R2' if not mirror else 'R3',
                   'Крыло боковое складное левое (520×1008/808)' if not mirror else 'Крыло боковое складное правое (520×1008/808)',
                   'AISI 304, шлиф. Scotch-Brite', T, 1, fw, fh, outline, cuts, bends, notes)


# ================================================================ R4 + R4.1 · ВЕНЕЦ ВЫДАЧИ РАДИУСНЫЙ + ПЕРФОКАССЕТА
def serve_cap():
    plate_w, plate_d = W, SERVE_D
    fw = DEV30 + plate_w + DEV30
    fh = DEV30 + plate_d + DEV30
    x0, y0 = DEV30, DEV30

    pts = [(x0 + CORNER_R, 0.0), (x0 + plate_w - CORNER_R, 0.0), (x0 + plate_w - CORNER_R, y0)]
    cx_r, cy_r = x0 + plate_w - CORNER_R, y0 + CORNER_R
    for i in range(1, 9):
        a = math.radians(-90.0 + 90.0 * i / 8.0)
        pts.append((cx_r + CORNER_R * math.cos(a), cy_r + CORNER_R * math.sin(a)))
    pts += [(fw, y0 + CORNER_R), (fw, y0 + plate_d), (x0 + plate_w, y0 + plate_d),
            (x0 + plate_w, fh), (x0, fh), (x0, y0 + plate_d),
            (0.0, y0 + plate_d), (0.0, y0 + CORNER_R), (x0, y0 + CORNER_R)]
    cx_l, cy_l = x0 + CORNER_R, y0 + CORNER_R
    for i in range(1, 9):
        a = math.radians(180.0 + 90.0 * i / 8.0)
        pts.append((cx_l + CORNER_R * math.cos(a), cy_l + CORNER_R * math.sin(a)))

    win_w, win_d = 680.0, 104.0
    cuts = [dict(type='poly', name='Окно перфокассеты выдачи 680×104 R10',
                 pts=G0.rrect_pts(x0 + (plate_w - win_w) / 2.0,
                                  y0 + (plate_d - win_d) / 2.0, win_w, win_d, 10.0, 8))]
    bends = [
        dict(p1=(x0 + CORNER_R, y0), p2=(x0 + plate_w - CORNER_R, y0), ang=90, note='передний борт 30 мм'),
        dict(p1=(x0, y0 + plate_d), p2=(x0 + plate_w, y0 + plate_d), ang=90, note='тыльный борт 30 мм'),
        dict(p1=(x0, y0 + CORNER_R), p2=(x0, y0 + plate_d), ang=90, note='левый борт 30 мм'),
        dict(p1=(x0 + plate_w, y0 + CORNER_R), p2=(x0 + plate_w, y0 + plate_d), ang=90, note='правый борт 30 мм'),
    ]
    notes = [
        'Скруглённая крышка-замок («cap-lock») 900 × 180 × 30 мм на отметке 1050 мм.',
        'Надевается сверху на кофр R1 и раскрытые крылья R2/R3, запирая прямой угол 90° корпуса.'
    ]
    return G0.Part('R4', 'Венец зоны выдачи радиусный R80 (900×180)',
                   'AISI 304, шлиф. Scotch-Brite', T, 1, fw, fh, pts, cuts, bends, notes)


def perf_insert():
    pw, pd = 700.0, 124.0
    fw, fh = pw, DEV15 + pd + DEV15
    outline = [(0.0, 0.0), (fw, 0.0), (fw, fh), (0.0, fh)]
    cuts = []
    cx_mid = fw / 2.0
    for r in range(4):
        yy = DEV15 + 18.0 + r * 29.0
        x = 22.0
        while x + 32.0 <= fw - 22.0:
            if not (cx_mid - 145.0 < x + 16.0 < cx_mid + 145.0 and 1 <= r <= 2):
                cuts.append(dict(type='poly', pts=G0.obround_pts(x + 16.0, yy, 32.0, 2.8)))
            x += 38.0
    dx_logo = cx_mid - (G0.LOGO_X0 + G0.LOGO_W / 2.0)
    dy_logo = (fh / 2.0) - (G0.TRAY_FLAT_H / 2.0)
    for lc in G0.logo_cuts():
        cuts.append(dict(type='poly', name=lc.get('name', ''),
                         pts=[(px + dx_logo, py + dy_logo) for px, py in lc['pts']]))
    bends = [
        dict(p1=(0.0, DEV15), p2=(fw, DEV15), ang=90, note='бортик 15 мм'),
        dict(p1=(0.0, DEV15 + pd), p2=(fw, DEV15 + pd), ang=90, note='бортик 15 мм'),
    ]
    notes = ['Съёмная заподлицо перфорированная кассета с логотипом ПАСИФИК ТУРБО (или глухая вставка под кофе/поп-ап).']
    return G0.Part('R4.1', 'Кассета перфорированная выдачи (ПАСИФИК ТУРБО)',
                   'AISI 304, перфорация', T_PERF, 1, fw, fh, outline, cuts, bends, notes)


# ================================================================ R5 · СТОЛЕШНИЦА РАБОЧАЯ (850 ММ)
def worktop_r():
    pw = W - 2.0 * T - 1.6              # 896.0 мм
    pd = WORK_D                         # 420.0 мм
    fw, fh = DEV30 + pw + DEV30, DEV30 + pd + DEV30
    outline = G0.cross_outline(0.0, 0.0, pw, pd, DEV30, DEV30, DEV30, DEV30)

    def _f(x, y):
        return DEV30 + x - T, DEV30 + y

    cuts = []
    for i, g in enumerate(CUT_GNS, 1):
        x, y = _f(g['x'], g['y'])
        cuts.append(dict(type='poly', name='Отсек GN 1/9 #%d 90×160 R8' % i,
                         pts=G0.rrect_pts(x, y, g['w'], g['h'], g['r'], 6)))
    for s in CUT_SINKS:
        x, y = _f(s['x'], s['y'])
        cuts.append(dict(type='poly', name='Отсек мойки GN 1/2 300×240 R12',
                         pts=G0.rrect_pts(x, y, s['w'], s['h'], s['r'], 6)))
    for cx, cy in ((0.0, 0.0), (pw, 0.0), (0.0, pd), (pw, pd)):
        cuts.append(dict(type='circle', cx=DEV30 + cx, cy=DEV30 + cy, r=RELIEF / 2))

    ribs = []
    for xa, xb in ((8.0, SEP_X - 28.0), (SEP_X + 28.0, pw - 8.0)):
        for yy in (305.0, 305.0 + G0.RIB_W):
            ribs.append(dict(p1=(DEV30 + xa, DEV30 + yy), p2=(DEV30 + xb, DEV30 + yy), ang=90,
                             note='ребро жёсткости 15 мм вниз'))
    bends = [
        dict(p1=(DEV30, DEV30), p2=(DEV30 + pw, DEV30), ang=90, note='передняя отбортовка 30'),
        dict(p1=(DEV30, DEV30 + pd), p2=(DEV30 + pw, DEV30 + pd), ang=90, note='задняя отбортовка 30'),
        dict(p1=(DEV30, DEV30), p2=(DEV30, DEV30 + pd), ang=90, note='левая отбортовка 30'),
        dict(p1=(DEV30 + pw, DEV30), p2=(DEV30 + pw, DEV30 + pd), ang=90, note='правая отбортовка 30'),
    ] + ribs
    notes = [
        'Уровень 850 мм (высота бедра), 4 × GN 1/9 + мойка GN 1/2 без крана — 100% преемственность с PK-900.',
        'Садится сверху на полки 820 мм крыльев R2/R3 и опирается по центру на поворотную консоль R6.'
    ]
    return G0.Part('R5', 'Столешница рабочая 896×420 (4×GN 1/9 + GN 1/2)',
                   'AISI 304, шлиф. Scotch-Brite', T, 1, fw, fh, outline, cuts, bends, notes)


# ================================================================ R6 · КОНСОЛЬ-ПЕРЕГОРОДКА ПОВОРОТНАЯ + R7 ЦАРГА
def support_partition():
    pw = 490.0                          # укладывается внутрь ниши кофра 0-м слоем на петлях к спинке R1
    ph = WORK_SHELF_Z - PLINTH_H        # 808.0 мм
    fw, fh = pw, DEV20 + ph + DEV25
    outline = [(0.0, 0.0), (fw, 0.0), (fw, fh), (0.0, fh)]
    cuts = [dict(type='poly', pts=G0.obround_pts(x, DEV20 + ph / 2.0, 44.0, 12.0)) for x in (130.0, 360.0)]
    for cx, cy in ((0.0, DEV20), (fw, DEV20), (0.0, DEV20 + ph), (fw, DEV20 + ph)):
        cuts.append(dict(type='circle', cx=cx, cy=cy, r=RELIEF / 2))
    xm = fw / 2.0
    bends = [
        dict(p1=(0.0, DEV20), p2=(fw, DEV20), ang=90, note='нижняя лапа 20 мм'),
        dict(p1=(0.0, DEV20 + ph), p2=(fw, DEV20 + ph), ang=90, note='верхняя полка 25 мм под столешницу R5'),
        dict(p1=(xm - 9.0, DEV20), p2=(xm - 9.0, DEV20 + ph), ang=90, note='вертикальное ребро жёсткости'),
        dict(p1=(xm + 9.0, DEV20), p2=(xm + 9.0, DEV20 + ph), ang=90, note='вертикальное ребро жёсткости'),
    ]
    notes = ['На двух внутренних петлях откидывается на X = 498,5 мм (между зоной льда и мойкой), неся центр столешницы.']
    return G0.Part('R6', 'Консоль-перегородка поворотная (лёд / мойка)',
                   'AISI 304, шлиф. Scotch-Brite', T, 1, fw, fh, outline, cuts, bends, notes)


def bottom_tie():
    pw, ph = W - 2.0 * T - 1.6, 90.0
    fw, fh = pw, DEV18 + ph + DEV18
    outline = [(0.0, 0.0), (fw, 0.0), (fw, fh), (0.0, fh)]
    bends = [
        dict(p1=(0.0, DEV18), p2=(fw, DEV18), ang=90, note='отбортовка 18 мм'),
        dict(p1=(0.0, DEV18 + ph), p2=(fw, DEV18 + ph), ang=90, note='отбортовка 18 мм'),
    ]
    notes = ['Замыкает нижний тыльный контур 900 мм в пазах задних отбортовок крыльев R2 и R3.']
    return G0.Part('R7', 'Царга тыльная нижняя (замок базы 900 мм)',
                   'AISI 304, шлиф. Scotch-Brite', T, 1, fw, fh, outline, [], bends, notes)


def all_parts():
    return [
        front_shell_r80(),
        folding_wing(False),
        folding_wing(True),
        serve_cap(),
        perf_insert(),
        worktop_r(),
        support_partition(),
        bottom_tie(),
    ]


def summary():
    parts = all_parts()
    sheet_mass = sum(p.mass() for p in parts)
    hw_mass = 0.85
    return dict(
        parts=parts,
        sheet_mass=sheet_mass,
        total_mass=sheet_mass + hw_mass,
        assembled=(W, D, H),
        folded=FOLDED_PACK,
    )


if __name__ == '__main__':
    s = summary()
    print('ПАСИФИК ТУРБО · PK-900R (радиусная складная кофр-станция)')
    print('=' * 80)
    for p in s['parts']:
        print('%-5s %-47s %6.1f × %6.1f мм  t=%.1f  %5.2f кг' %
              (p.code, p.name, p.flat_w, p.flat_h, p.t, p.mass()))
    print('-' * 80)
    print('Масса металла AISI 304:  %.2f кг' % s['sheet_mass'])
    print('Полная масса с петлями:  %.2f кг (в базовой PK-900 рев. D+: 29,7 кг)' % s['total_mass'])
    print('Габарит в работе:        900 × 600 × 1050 мм (выдача 1050 / рабочая 850)')
    print('Габарит в сложении:      900 × 135 × 1020 мм (объём 0,124 м³, как чехол PK-900, но без сумки!)')
