"""Презентация попап-версии PK-POP-900 (pptx) + схемы для слайдов.
Запуск: /tmp/pkenv/bin/python cad/pk_popup_deck.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import pk_popup as P

ROOT = os.path.join(os.path.dirname(__file__), '..')
DOCS = os.path.join(ROOT, 'docs', 'popup')
REF = os.path.join(ROOT, 'docs', 'visualization', 'PK-900_predmetnaya_syemka.png')
INK = RGBColor(0x1d, 0x1f, 0x1e)
GREY = RGBColor(0x6b, 0x6f, 0x6d)
ACC = RGBColor(0x9a, 0x3f, 0x22)

sheets = P.pack(P.PARTS)
area_pct = 100 * sum(p.w * p.h * p.qty for p in P.PARTS) / (2 * P.SHEET[0] * P.SHEET[1])
colors = {'PK-POP-01': '#c9cbc8', 'PK-POP-02': '#b8bcb9', 'PK-POP-03': '#dfe1de',
          'PK-POP-04': '#aeb3b0', 'PK-POP-05': '#d3d6d3', 'PK-POP-06': '#9ea4a1', 'PK-POP-07': '#cfd3d0'}

# ---- раскрой
fig, axs = plt.subplots(1, len(sheets), figsize=(7 * len(sheets), 8.6))
for ax, s in zip(axs, sheets):
    ax.add_patch(plt.Rectangle((0, 0), P.SHEET[0], P.SHEET[1], fill=False, ec='k', lw=1.2))
    for x0, y0, w, h, p, rot, k in s['placed']:
        ax.add_patch(plt.Rectangle((x0, y0), w, h, fc=colors[p.code], ec='#333', lw=0.8))
        if h >= 60:
            ax.text(x0 + w / 2, y0 + h / 2, f'{p.code}\n{w:.0f}×{h:.0f}', ha='center', va='center', fontsize=9)
    ax.set_xlim(-20, P.SHEET[0] + 20); ax.set_ylim(-20, P.SHEET[1] + 20)
    ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')
    ax.set_title(f'лист {sheets.index(s) + 1} · {P.SHEET[0]:.0f}×{P.SHEET[1]:.0f} мм · берёза 12 мм', fontsize=11)
fig.tight_layout()
RASKROY = os.path.join(DOCS, 'PK-POP-900_raskroy.png')
fig.savefig(RASKROY, dpi=110)
plt.close(fig)

# ---- профиль станции (боковина + столешница + фасады), мм
fig, ax = plt.subplots(figsize=(9, 6.2))
side = P.side()
pts = [(x, y) for x, y, _ in side.cuts[0][0]]
ax.add_patch(plt.Polygon(pts, fc='#c9cbc8', ec='#222', lw=1.2))
ax.add_patch(plt.Rectangle((140, 838), 460, 12, fc='#eceded', ec='#222', lw=1))   # столешница
ax.add_patch(plt.Rectangle((0, 1038), 140, 12, fc='#eceded', ec='#222', lw=1))    # плита выдачи 12 мм
for z0 in (12, 12 + 334 + 3, 12 + 2 * (334 + 3)):
    ax.add_patch(plt.Rectangle((-18, z0), 12, 334, fc='#aeb3b0', ec='#222', lw=0.8))
ax.annotate('', xy=(600, 1100), xytext=(0, 1100), arrowprops=dict(arrowstyle='<->'))
ax.text(300, 1112, '600', ha='center', fontsize=10)
ax.annotate('', xy=(-40, 1050), xytext=(-40, 0), arrowprops=dict(arrowstyle='<->'))
ax.text(-60, 525, '1050', rotation=90, va='center', fontsize=10)
ax.text(440, 900, 'рабочая плоскость 850\n(боковина 838 + столешница 12)', fontsize=9, color='#333')
ax.text(-70, 1000, 'выдача 1050\n(1038 + плита 12)', fontsize=9, color='#333', ha='right')
ax.set_aspect('equal'); ax.set_xlim(-80, 640); ax.set_ylim(-30, 1130); ax.axis('off')
ax.set_title('Профиль попап-станции, мм (схема, не чертёж)', fontsize=11)
PROFILE = os.path.join(DOCS, 'PK-POP-900_profil.png')
fig.tight_layout(); fig.savefig(PROFILE, dpi=110); plt.close(fig)

# ---- презентация
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]

def text(slide, x, y, w, h, s, size=18, bold=False, color=INK):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    lines = s if isinstance(s, list) else [s]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
        p.space_after = Pt(8)
    return tb

def header(slide, title, sub=None):
    text(slide, 0.6, 0.35, 12, 0.7, title, 30, True)
    if sub:
        text(slide, 0.6, 1.0, 12, 0.5, sub, 14, False, GREY)

def footer(slide, n):
    text(slide, 0.6, 7.0, 12, 0.35, f'ПАСИФИК ТУРБО · PK-POP-900 · черновик · 08.11.2026 · {n}', 10, False, GREY)

def table(slide, x, y, w, rows, colw, size=12):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(0.4 * len(rows)))
    t = shape.table
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i, j); c.text = str(v)
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(size); p.font.bold = (i == 0)
    return shape

n = 0
# 1 титул
s = prs.slides.add_slide(blank); n += 1
text(s, 0.8, 2.2, 11.5, 1.2, 'ПАСИФИК ТУРБО · попап', 44, True)
text(s, 0.8, 3.4, 11.5, 0.8, 'барная станция из берёзовой фанеры 12 мм · PK-POP-900', 22, False, GREY)
text(s, 0.8, 4.3, 11.5, 0.6, 'черновик концепции и раскроя', 16, False, ACC)
footer(s, n)

# 2 идея
s = prs.slides.add_slide(blank); n += 1
header(s, 'Идея', 'та же станция, другой материал и способ сборки')
text(s, 0.8, 1.7, 11.8, 5, [
    '• Тот же объём: 900 × 600 × 1050 мм, зоны выдачи, рабочей и лёд/мойка.',
    '• Материал: берёзовая фанера 12 мм вместо нержавейки 1,2 мм.',
    '• Из фанеры и выдача, и рабочая зона; стальная остаётся только вставка мойки.',
    '• 13 деталей, 2 листа 1220 × 2440 мм; файлы для ЧПУ — в docs/popup/cnc/.',
    '• Складывание (вариант A — откидной, B — телескопический) решим после макета.',
], 20)
footer(s, n)

# 3 параметры
s = prs.slides.add_slide(blank); n += 1
header(s, 'Ключевые параметры')
table(s, 0.8, 1.7, 11.5, [
    ['Параметр', 'Значение'],
    ['Габарит в сборе', '900 × 600 × 1050 мм'],
    ['Выдача (борт)', '1050 мм: боковины 1038 + плита выдачи 12'],
    ['Рабочая плоскость', '850 мм: боковины 838 + столешница 12'],
    ['Материал', 'берёза 12 мм: плита выдачи, столешница, фасады; сталь — вставка мойки'],
    ['Фасад', '3 блока 875 × 334 мм, в каналах боковин, без крепежа'],
    ['Листов', f'2 × 1220 × 2440 мм, использовано ~{area_pct:.0f} % площади'],
], [4.0, 7.5], 16)
footer(s, n)

# 4 состав
s = prs.slides.add_slide(blank); n += 1
header(s, 'Состав деталей')
rows = [['Код', 'Деталь', 'Размер, мм', 'Шт.', 'Примечание']]
for p in P.PARTS:
    rows.append([p.code, p.name, f'{p.w:.0f} × {p.h:.0f}', p.qty, p.note])
table(s, 0.5, 1.5, 12.3, rows, [1.4, 3.1, 1.6, 0.7, 5.5], 12)
footer(s, n)

# 5 раскрой
s = prs.slides.add_slide(blank); n += 1
header(s, 'Раскрой на два листа', 'файлы: docs/popup/cnc/PK-POP-NEST_sheet1.dxf, _sheet2.dxf')
s.shapes.add_picture(RASKROY, Inches(0.6), Inches(1.6), height=Inches(5.3))
footer(s, n)

# 6 конструкция
s = prs.slides.add_slide(blank); n += 1
header(s, 'Конструкция', 'боковины с рейками образуют каналы для фасадов')
s.shapes.add_picture(PROFILE, Inches(0.5), Inches(1.6), height=Inches(4.6))
text(s, 8.6, 1.8, 4.4, 5, [
    '• Боковины — с уступом: 1038 спереди, 838 под столешницей.',
    '• Рейки 1008 × 40 — по две на каждую боковину; канал 12,5 мм для фасада.',
    '• Фасады входят сверху и ставятся на место без крепежа.',
    '• Дно и перегородка — винтами в торец боковин.',
    '• Столешница и плита выдачи — винтами сверху; плита на боковинах.',
], 15)
footer(s, n)

# 7 ограничения
s = prs.slides.add_slide(blank); n += 1
header(s, 'Ограничения фанеры')
text(s, 0.8, 1.6, 11.8, 5.2, [
    '• Мойка — стальная вставка: из фанеры не делается, вода и санитария.',
    '• Выдача: слоты 40 × 7 и трафарет «ПАСИФИК ТУРБО» под фрезу Ø6; влагозащита.',
    '• Плита выдачи без поперечины: проверить прогиб под стаканами.',
    '• Влага: покрыть маслом или лаком; станция на улице — отдельный вопрос.',
    '• Жёсткость: 12 мм берёза под столешницей 60 кг — проверить на образце.',
    '• Механизм складывания в DXF не нанесён: ждём выбор варианта A или B.',
    '• Вставка мойки — сталь: подтвердить до резки (рабочая зона из фанеры).',
], 18)
footer(s, n)

# 8 дальше
s = prs.slides.add_slide(blank); n += 1
header(s, 'Что дальше')
text(s, 0.8, 1.6, 11.8, 5.2, [
    '1. Выбрать вариант складывания: A (откидной) или B (телескопический).',
    '2. Макет 1:5 из картона или фанеры — проверить ход фасадов и габарит.',
    '3. Образец столешницы 12 мм: 60 кг в центр, прогиб не более 1 мм.',
    '4. Фурнитура: навесы, штифты, направляющие — сорт и поставщик.',
    '5. Пробная резка одного листа по DXF, проверка посадки каналов.',
    '6. Цена у мастерской: в этой версии цены не оценивались — нет источников.',
], 18)
footer(s, n)

# 9 референс
s = prs.slides.add_slide(blank); n += 1
header(s, 'Референс: версия из нержавейки', 'попап — тот же объём и зоны, другой материал')
s.shapes.add_picture(REF, Inches(0.6), Inches(1.6), height=Inches(4.9))
footer(s, n)

OUT_PPTX = os.path.join(DOCS, 'PK-POP-900_prezentatsiya.pptx')
prs.save(OUT_PPTX)
print('ok', RASKROY, PROFILE, OUT_PPTX, f'слайдов {n}')
