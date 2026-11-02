"""SVG figures for transducer artefacts: insert leaks, patent grommets with inserts and
collapsing canals. Web only (not in PRINT_FIGS). Standing waves are covered by the
interactive demo in assets/demos/standing-waves.html instead of a figure.

Drop-in companion to figures.py: same palette, same helpers, same 560-wide viewBox.
Register by merging FIGURES below into figures.FIGURES (see bottom of file).

Graphs are SCHEMATIC unless a caption names a data source. The grommet band follows
the range reported by Voss et al. (2000, Ear Hear 21:265-274); the other curves show
the direction and frequency region of the effect, not measured values."""

import math
from figures import INK, BRAND, RIGHT, LEFT, MUTED, RULE, FONT, _svg

AZURE = "var(--brand-2, #1f2bd4)"
WASH = "var(--wash, #f1f1f5)"
STOP = "var(--stop, #b3261e)"
STOP_WASH = "var(--stop-wash, #fdeceb)"
FOAM = "#f4d35e"          # same foam yellow as insert_depth()
SKIN = "#f6e3d6"
SKIN_EDGE = "#b98b73"
FREQS = [125, 250, 500, 1000, 2000, 4000, 8000]
FLAB = ["125", "250", "500", "1k", "2k", "4k", "8k"]


def _t(x, y, s, size=12, anchor="start", weight=None, fill=INK, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}"{w} '
            f'fill="{fill}" style="{FONT}" {extra}>{s}</text>')


def _fx(f, x0, x1):
    return x0 + (math.log2(f / 125) / 6) * (x1 - x0)


def _change_graph(x0, y0, x1, y1, ymin, title_y, note=None):
    """Axes for 'change in ear-canal SPL' (0 at top, negative downward). Returns (parts, X, Y)."""
    def X(f): return _fx(f, x0, x1)
    def Y(d): return y1 + (d / ymin) * (y0 - y1)   # d = 0 .. ymin (negative)
    b = []
    for d in range(0, ymin - 1, -10):
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(d):.1f}" y2="{Y(d):.1f}" stroke="{RULE}" stroke-width="{1.2 if d == 0 else 0.8}"/>')
        b.append(_t(x0 - 8, Y(d) + 4, f"{d:+d}" if d else "0", 11, "end", fill=MUTED))
    for f, lab in zip(FREQS, FLAB):
        b.append(f'<line x1="{X(f):.1f}" x2="{X(f):.1f}" y1="{y1}" y2="{y0}" stroke="{RULE}" stroke-width="0.5"/>')
        b.append(_t(X(f), y0 + 16, lab, 11, "middle", fill=MUTED))
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}"/>')
    b.append(_t((x0 + x1) / 2, y0 + 32, "Frequency (Hz)", 12, "middle"))
    b.append(f'<text transform="translate({x0-38},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">{title_y}</text>')
    if note:
        b.append(_t(x1, y1 - 8, note, 11, "end", fill=MUTED, extra='font-style="italic"'))
    return b, X, Y


def _canal(ox, top, bot, entrance, tm, label=True):
    """Horizontal canal: concha flare left of `entrance`, eardrum at `tm`."""
    b = [
        # skin either side of the canal
        f'<path d="M{ox},{top-34} L{entrance-30},{top-34} Q{entrance-6},{top-30} {entrance},{top} L{tm+12},{top} L{tm+12},{top-34} Z" fill="{SKIN}"/>',
        f'<path d="M{ox},{bot+34} L{entrance-30},{bot+34} Q{entrance-6},{bot+30} {entrance},{bot} L{tm+12},{bot} L{tm+12},{bot+34} Z" fill="{SKIN}"/>',
        f'<path d="M{ox},{top-34} L{entrance-30},{top-34} Q{entrance-6},{top-30} {entrance},{top} L{tm},{top}" fill="none" stroke="{SKIN_EDGE}" stroke-width="2"/>',
        f'<path d="M{ox},{bot+34} L{entrance-30},{bot+34} Q{entrance-6},{bot+30} {entrance},{bot} L{tm},{bot}" fill="none" stroke="{SKIN_EDGE}" stroke-width="2"/>',
        # eardrum, slanted
        f'<line x1="{tm-8}" y1="{top}" x2="{tm+6}" y2="{bot}" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>',
    ]
    if label:
        b.append(_t(tm + 10, bot + 50, "eardrum", 10.5, "end", fill=MUTED))
        b.append(_t(entrance, top - 42, "canal entrance", 10.5, "middle", fill=MUTED))
        b.append(f'<line x1="{entrance}" y1="{top-36}" x2="{entrance}" y2="{bot+4}" stroke="{BRAND}" stroke-width="1" stroke-dasharray="3 3"/>')
    return b


def _waves(x, y, n, gap=14, r=22, colour=AZURE, cls="pt"):
    return [f'<path class="{cls}" style="--i:{i}" d="M{x+i*gap},{y-r} Q{x+i*gap+r*0.55},{y} {x+i*gap},{y+r}" fill="none" stroke="{colour}" stroke-width="2" stroke-linecap="round"/>' for i in range(n)]


# ---------------------------------------------------------------- 1. insert leak
def insert_leak():
    W, H = 560, 500
    b = []
    for i, (title, sub, leak) in enumerate((
            ("Sealed", "Right size, fully expanded, flush or deeper", False),
            ("Leaking", "Too small, too shallow, or not left to expand", True))):
        ox = 10 + i * 280
        top, bot, ent, tm = 92, 142, ox + 70, ox + 250
        b += _canal(ox, top, bot, ent, tm)
        if not leak:
            b.append(f'<rect x="{ent}" y="{top}" width="58" height="{bot-top}" rx="7" fill="{FOAM}" stroke="{INK}" stroke-width="1.2"/>')
            b.append(f'<line x1="{ent}" y1="{(top+bot)/2}" x2="{ox+6}" y2="{(top+bot)/2}" stroke="{INK}" stroke-width="3"/>')
            b += _waves(ent + 74, (top + bot) / 2, 6, 15, 20)
            b.append(_t(ent + 116, top + 74, "all of the sound stays in", 10.5, "middle", fill=AZURE))
            b.append(_t(ent + 116, top + 87, "the canal", 10.5, "middle", fill=AZURE))
        else:
            # tip too small and shallow: gaps above and below
            b.append(f'<rect x="{ent-26}" y="{top+9}" width="50" height="{bot-top-18}" rx="7" fill="{FOAM}" stroke="{INK}" stroke-width="1.2"/>')
            b.append(f'<line x1="{ent-26}" y1="{(top+bot)/2}" x2="{ox+6}" y2="{(top+bot)/2}" stroke="{INK}" stroke-width="3"/>')
            b += _waves(ent + 46, (top + bot) / 2, 6, 15, 20)
            for yy, dy in ((top + 4, -1), (bot - 4, 1)):
                b.append(f'<path class="draw" d="M{ent+30},{yy} L{ent-34},{yy} Q{ent-48},{yy} {ent-58},{yy+dy*22}" fill="none" stroke="{STOP}" stroke-width="2.4" marker-end="url(#ahr)"/>')
            b.append(_t(ent - 66, bot + 52, "low frequencies escape", 10.5, "start", weight=700, fill=STOP))
        b.append(_t(ox + 140, 24, title, 14, "middle", 700, BRAND if not leak else STOP))
        b.append(_t(ox + 140, 222, sub, 11.5, "middle", fill=MUTED))
    # graph
    gb, X, Y = _change_graph(80, 440, 530, 270, -30, "Ear-canal SPL vs sealed fit (dB)", "Schematic")
    b += gb
    leak = [(125, -22), (250, -14), (500, -6), (1000, -2), (2000, -0.5), (4000, 0), (8000, 0)]
    path = "M" + " L".join(f"{X(f):.1f},{Y(d):.1f}" for f, d in leak)
    area = path + f" L{X(8000):.1f},{Y(0):.1f} L{X(125):.1f},{Y(0):.1f} Z"
    b.append(f'<path d="{area}" fill="{STOP_WASH}"/>')
    b.append(f'<path class="draw" d="{path}" fill="none" stroke="{STOP}" stroke-width="3" stroke-linejoin="round"/>')
    b.append(f'<line x1="{X(125)}" x2="{X(8000)}" y1="{Y(0)}" y2="{Y(0)}" stroke="{BRAND}" stroke-width="2.4"/>')
    b.append(_t(X(8000) - 4, Y(0) + 15, "sealed", 11.5, "end", 700, BRAND))
    b.append(_t(X(500) + 6, Y(-14), "leak: less sound below ~1 kHz", 11.5, "start", 700, STOP))
    b.append(_t(X(500) + 6, Y(-14) + 15, "= false low-frequency 'conductive' loss", 11.5, "start", fill=INK))
    b.append(_t(10, H - 8, "Bigger leak, bigger effect, reaching higher in frequency. Works like a hearing-aid vent.", 11.5, fill=MUTED))
    body = "\n".join(b).replace('marker-end="url(#ahr)"', 'marker-end="url(#ahr)"')
    body = (f'<defs><marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{STOP}"/></marker></defs>') + body
    return _svg(W, H, body, "A leaking insert loses low frequencies",
                "Left: a correctly sized foam tip, fully expanded and flush with the canal entrance, seals the canal. Right: a tip that is too small or too shallow leaves a gap; low-frequency sound escapes through it. Graph, schematic: with a leak the sound level in the canal falls below about 1 kHz, most at 125 and 250 Hz, and is unchanged at high frequencies. This mimics a low-frequency conductive loss.")


# ---------------------------------------------------------------- 2. grommet with inserts
def insert_grommet():
    W, H = 560, 520
    b = []
    top, bot, ent, tm = 108, 158, 120, 360
    b += _canal(10, top, bot, ent, tm)
    # middle ear cavity + mastoid air cells
    b.append(f'<path d="M{tm+4},{top-40} C{tm+80},{top-60} {tm+110},{top-10} {tm+100},{(top+bot)/2} C{tm+110},{bot+20} {tm+70},{bot+50} {tm+6},{bot+40} Z" fill="#e6f6fb" stroke="{MUTED}" stroke-width="1.4"/>')
    for (cx, cy, r) in ((tm + 120, top - 52, 13), (tm + 146, top - 66, 10), (tm + 150, top - 40, 12), (tm + 170, top - 58, 9),
                        (tm + 132, top - 24, 9), (tm + 174, top - 30, 11), (tm + 192, top - 48, 8)):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e6f6fb" stroke="{MUTED}" stroke-width="1.2"/>')
    b.append(f'<path d="M{tm+90},{top-30} L{tm+114},{top-40}" stroke="{MUTED}" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<path d="M{tm+90},{top-30} L{tm+114},{top-40}" stroke="#e6f6fb" stroke-width="3.5" stroke-linecap="round"/>')
    b.append(_t(tm + 70, bot + 66, "middle ear", 10.5, "middle", fill=MUTED))
    b.append(_t(tm + 160, top - 82, "mastoid air cells", 10.5, "middle", fill=MUTED))
    # grommet through the eardrum
    gy = (top + bot) / 2
    b.append(f'<rect x="{tm-10}" y="{gy-6}" width="22" height="12" rx="2" fill="{BRAND}"/>')
    b.append(_t(tm - 30, top - 14, "patent grommet", 11, "end", 700, BRAND))
    b.append(f'<path d="M{tm-28},{top-18} Q{tm},{top-18} {tm},{gy-8}" fill="none" stroke="{BRAND}" stroke-width="1.2"/>')
    # sealed insert
    b.append(f'<rect x="{ent}" y="{top}" width="58" height="{bot-top}" rx="7" fill="{FOAM}" stroke="{INK}" stroke-width="1.2"/>')
    b.append(f'<line x1="{ent}" y1="{gy}" x2="16" y2="{gy}" stroke="{INK}" stroke-width="3"/>')
    b += _waves(ent + 74, gy, 7, 15, 20)
    # pressure spreading into the larger volume
    b.append(f'<path class="draw" d="M{tm+14},{gy} C{tm+50},{gy} {tm+60},{gy-20} {tm+80},{gy-36}" fill="none" stroke="{STOP}" stroke-width="2.4" marker-end="url(#ahr)"/>')
    b.append(f'<path class="draw" d="M{tm+14},{gy} C{tm+40},{gy} {tm+52},{gy+16} {tm+62},{gy+28}" fill="none" stroke="{STOP}" stroke-width="2.4" marker-end="url(#ahr)"/>')
    b.append(_t(14, 26, "The insert now drives the canal, middle ear and mastoid together:", 12.5, weight=700))
    b.append(_t(14, 42, "a much larger air volume, so less pressure at low frequencies.", 12.5))
    b.append(_t(14, 238, "Same physics as the large ear-canal volume on the tympanogram.", 11.5, fill=MUTED))
    # graph with Voss et al. (2000) range
    gb, X, Y = _change_graph(80, 450, 530, 268, -30, "Ear-canal SPL vs normal ear (dB)",
                             "Range after Voss et al. (2000), inserts")
    b += gb
    upper = [(250, -5), (500, -3), (1000, -1), (2000, 0), (4000, 0), (8000, 0)]
    lower = [(250, -25), (500, -16), (1000, -6), (2000, -2), (4000, -1), (8000, -1)]
    band = ("M" + " L".join(f"{X(f):.1f},{Y(d):.1f}" for f, d in upper) + " L" +
            " L".join(f"{X(f):.1f},{Y(d):.1f}" for f, d in reversed(lower)) + " Z")
    b.append(f'<path d="{band}" fill="{STOP_WASH}" stroke="{STOP}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    b.append(f'<line x1="{X(125)}" x2="{X(8000)}" y1="{Y(0)}" y2="{Y(0)}" stroke="{BRAND}" stroke-width="2.4"/>')
    b.append(_t(X(8000) - 4, Y(0) + 15, "normal ear", 11.5, "end", 700, BRAND))
    b.append(_t(X(250) + 8, Y(-27), "−5 to −25 dB below 500 Hz", 11.5, "start", 700, STOP))
    b.append(_t(X(1000) + 10, Y(-12), "AC looks worse than the ear is.", 11.5, "start", fill=INK))
    b.append(_t(X(1000) + 10, Y(-12) + 15, "Check low frequencies with supra-aurals.", 11.5, "start", fill=INK))
    b.append(_t(10, H - 8, "Mastoid bowls and TM perforations do the same, and bowls can also reduce higher frequencies.", 11.5, fill=MUTED))
    body = (f'<defs><marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{STOP}"/></marker></defs>') + "\n".join(b)
    return _svg(W, H, body, "Inserts with a patent grommet",
                "A sealed foam insert in a canal with a patent grommet. Through the grommet the insert is coupled to the middle ear and mastoid air cells, a much larger air volume, so it produces less sound pressure at low frequencies. Graph: Voss et al. (2000) measured ear-canal pressure in ears with tympanostomy tubes and perforations 5 to 25 dB below normal at frequencies under 500 Hz, with little change above 1 kHz.")


# ---------------------------------------------------------------- 4. collapsing canal
def collapsing_canal():
    W, H = 560, 500
    b = []
    # two cross-sections, top row
    for i, (title, collapsed) in enumerate((("Canal open", False), ("Collapsed under cushion", True))):
        ox = 10 + i * 280
        cy = 120
        tm = ox + 250
        ent = ox + 90
        # cartilaginous outer third vs bony inner
        if not collapsed:
            topw = f"M{ox+40},{cy-70} Q{ent-10},{cy-60} {ent},{cy-25} L{tm},{cy-25}"
            botw = f"M{ox+40},{cy+70} Q{ent-10},{cy+60} {ent},{cy+25} L{tm},{cy+25}"
        else:
            topw = f"M{ox+52},{cy-50} Q{ent-14},{cy-26} {ent+4},{cy-3} Q{ent+30},{cy-3} {ent+56},{cy-25} L{tm},{cy-25}"
            botw = f"M{ox+52},{cy+50} Q{ent-14},{cy+26} {ent+4},{cy+3} Q{ent+30},{cy+3} {ent+56},{cy+25} L{tm},{cy+25}"
        for d in (topw, botw):
            sgn = -1 if d is topw else 1
            b.append(f'<path d="{d} L{tm+12},{cy+sgn*25} L{tm+12},{cy+sgn*80} L{ox+40},{cy+sgn*80} Z" fill="{SKIN}"/>')
            b.append(f'<path d="{d}" fill="none" stroke="{SKIN_EDGE}" stroke-width="2"/>')
        b.append(f'<line x1="{tm-8}" y1="{cy-25}" x2="{tm+6}" y2="{cy+25}" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>')
        # cartilage / bone boundary
        bx = ent + 70
        b.append(f'<line x1="{bx}" y1="{cy-78}" x2="{bx}" y2="{cy-28}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
        b.append(f'<line x1="{bx}" y1="{cy+28}" x2="{bx}" y2="{cy+78}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
        b.append(_t((ent + bx) / 2 - 6, cy + 96, "cartilage", 10, "middle", fill=MUTED))
        b.append(_t((bx + tm) / 2, cy + 96, "bone", 10, "middle", fill=MUTED))
        b.append(_t(ox + 140, 22, title, 14, "middle", 700, BRAND if not collapsed else STOP))
        if collapsed:
            b.append(f'<rect x="{ox+6}" y="{cy-82}" width="34" height="164" rx="14" fill="{INK}"/>')
            for yy in (cy - 46, cy + 46):
                b.append(f'<path d="M{ox+44},{yy} L{ox+70},{yy + (14 if yy < cy else -14)}" stroke="{STOP}" stroke-width="2.4" marker-end="url(#ahr)"/>')
            b.append(_t(ent + 30, cy - 36, "slit", 11, "middle", 700, STOP))
        else:
            b += _waves(ent + 40, cy, 5, 16, 16)
    # mini audiogram (right ear symbols), schematic
    x0, x1, y1, y0 = 80, 360, 262, 470
    fr = [250, 500, 1000, 2000, 4000, 8000]
    def X(f): return x0 + 26 + (math.log2(f / 250) / 5) * (x1 - x0 - 44)
    def Y(d): return y1 + (d + 10) / 80 * (y0 - y1)   # -10 .. 70 dB HL, louder is lower
    for d in range(-10, 71, 10):
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(d):.1f}" y2="{Y(d):.1f}" stroke="{RULE}" stroke-width="0.8"/>')
        b.append(_t(x0 - 8, Y(d) + 4, str(d), 10.5, "end", fill=MUTED))
    for f, lab in zip(fr, ["250", "500", "1k", "2k", "4k", "8k"]):
        b.append(_t(X(f), y1 - 6, lab, 10.5, "middle", fill=MUTED))
    b.append(f'<text transform="translate({x0-34},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" font-size="11.5" fill="{INK}" style="{FONT}">dB HL</text>')
    supra = [10, 15, 20, 35, 45, 50]
    ins = [10, 10, 10, 15, 15, 20]
    bc = [5, 5, 5, 10, 10]
    ps = "M" + " L".join(f"{X(f):.1f},{Y(d):.1f}" for f, d in zip(fr, supra))
    pi = "M" + " L".join(f"{X(f):.1f},{Y(d):.1f}" for f, d in zip(fr, ins))
    b.append(f'<path class="draw" d="{ps}" fill="none" stroke="{RIGHT}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(f'<path class="draw" d="{pi}" fill="none" stroke="{RIGHT}" stroke-width="2"/>')
    for f, d in zip(fr, supra):
        b.append(f'<circle cx="{X(f):.1f}" cy="{Y(d):.1f}" r="6" fill="#fff" stroke="{RIGHT}" stroke-width="2" stroke-dasharray="3 2"/>')
    for f, d in zip(fr, ins):
        b.append(f'<circle cx="{X(f):.1f}" cy="{Y(d):.1f}" r="6" fill="#fff" stroke="{RIGHT}" stroke-width="2"/>')
    for f, d in zip(fr[:-1], bc):
        x, y = X(f) - 15, Y(d)
        b.append(f'<path d="M{x+5},{y-8} L{x-5},{y} L{x+5},{y+8}" fill="none" stroke="{RIGHT}" stroke-width="2"/>')
    b.append(_t((x0 + x1) / 2, y0 + 20, "Schematic, right ear", 11, "middle", fill=MUTED, extra='font-style="italic"'))
    # legend / reading
    lx = 380
    b.append(f'<line x1="{lx}" x2="{lx+26}" y1="276" y2="276" stroke="{RIGHT}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(_t(lx + 32, 280, "supra-aural", 11.5))
    b.append(f'<line x1="{lx}" x2="{lx+26}" y1="296" y2="296" stroke="{RIGHT}" stroke-width="2"/>')
    b.append(_t(lx + 32, 300, "inserts", 11.5))
    b.append(_t(lx + 8, 320, "&lt;", 13, "middle", 700, RIGHT))
    b.append(_t(lx + 32, 320, "bone conduction", 11.5))
    for j, s in enumerate(["A false air-bone", "gap, mostly in the", "high frequencies,", "that disappears", "with inserts."]):
        b.append(_t(lx, 352 + j * 16, s, 12, weight=700 if j == 0 else None, fill=STOP if j == 0 else INK))
    b.append(_t(lx, 446, "Tympanogram normal,", 11, fill=MUTED))
    b.append(_t(lx, 460, "reflexes present.", 11, fill=MUTED))
    body = (f'<defs><marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{STOP}"/></marker></defs>') + "\n".join(b)
    return _svg(W, H, body, "Collapsing ear canal",
                "Left: an open ear canal. Right: a supra-aural cushion presses on the pinna and tragus and the soft cartilaginous outer canal folds into a slit, blocking sound. Schematic audiogram: air conduction under supra-aural headphones is elevated, mostly at 2 to 8 kHz, with normal bone conduction, giving a false air-bone gap. With insert earphones the thresholds return to normal.")


FIGURES = {
    "insert-leak": ("A leaking insert loses low frequencies", insert_leak),
    "insert-grommet": ("Inserts with a patent grommet", insert_grommet),
    "collapsing-canal": ("Collapsing ear canal", collapsing_canal),
}
ANIMATED = set()   # static, like the rest of the site
PRINT_FIGS = set()   # HTML only: print cards carry the wording, not the figures

