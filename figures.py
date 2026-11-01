"""SVG figures for the PTA and masking module. All drawn in the house style.
Colours come from CSS custom properties where the SVG is inline, with fallbacks for print."""

INK = "var(--ink, #1d2329)"
BRAND = "var(--brand, #0c0c48)"
RIGHT = "var(--right, #c8102e)"
LEFT = "var(--left, #1f2bd4)"
MUTED = "var(--muted, #5b6670)"
RULE = "var(--rule, #c9d2db)"
FILL = "var(--wash, #e8f8fc)"
FONT = "font-family:inherit"


def _box(x, y, w, h, lines, kind="action"):
    """kind: start, action, decision, end"""
    out = []
    if kind == "decision":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="#fff" stroke="{INK}" stroke-width="1.6" stroke-dasharray="0"/>')
        style = "font-style:italic"
    elif kind == "end":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{BRAND}" stroke="{BRAND}"/>')
        style = "font-weight:700;fill:#fff"
    elif kind == "start":
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{FILL}" stroke="{BRAND}" stroke-width="1.6"/>')
        style = "font-weight:700"
    else:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{RULE}" stroke-width="1.6"/>')
        style = ""
    n = len(lines)
    for i, t in enumerate(lines):
        ty = y + h / 2 + (i - (n - 1) / 2) * 15 + 5
        out.append(f'<text x="{x + w/2}" y="{ty}" text-anchor="middle" font-size="13" style="{FONT};{style}" fill="{INK if kind != "end" else "#fff"}">{t}</text>')
    return "\n".join(out)


def _arrow(points, label=None, lx=None, ly=None, anchor="start"):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    s = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.4" marker-end="url(#ah)"/>'
    if label:
        s += f'<text x="{lx}" y="{ly}" font-size="12" font-weight="700" text-anchor="{anchor}" style="{FONT}" fill="{INK}">{label}</text>'
    return s


def _svg(w, h, body, title, desc):
    return f'''<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d" class="fig">
<title>{title}</title><desc>{desc}</desc>
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>
{body}
</svg>'''


def plateau_flow():
    W = 560
    b = []
    cx = 270
    b.append(_box(cx - 130, 10, 260, 46, ["Set initial masking in NTE", "AC<tspan baseline-shift='sub' font-size='9'>NTE</tspan> + 10 dB (+ OEF for BC)"], "start"))
    b.append(_arrow([(cx, 56), (cx, 82)]))
    b.append(_box(cx - 130, 82, 260, 40, ["Present tone to test ear"]))
    b.append(_arrow([(cx, 122), (cx, 146)]))
    b.append(_box(cx - 130, 146, 260, 46, ["Response?"], "decision"))
    b.append(_arrow([(cx - 130, 169), (90, 169), (90, 214)], "No", 100, 162))
    b.append(_box(10, 214, 160, 46, ["Raise tone 5 dB", "until response"]))
    b.append(_arrow([(170, 237), (cx - 90, 237), (cx - 90, 300)]))
    b.append(_arrow([(cx, 192), (cx + 130 - 40, 192), (cx + 90, 214)], "Yes", cx + 20, 208))
    b.append(_box(cx + 10, 214, 220, 46, ["Threshold held across", "20 dB of masking?"], "decision"))
    b.append(_arrow([(cx + 120, 260), (cx + 120, 300)], "Yes", cx + 128, 286))
    b.append(_box(cx + 30, 300, 180, 40, ["Accept masked threshold"], "end"))
    b.append(_box(cx - 170, 300, 160, 40, ["Raise masking 10 dB"]))
    b.append(_arrow([(cx + 10, 237), (cx - 10, 237), (cx - 10, 270), (cx - 60, 270), (cx - 60, 300)], "No", cx - 6, 230, "end"))
    b.append(_arrow([(cx - 170, 320), (2, 320), (2, 102), (cx - 130, 102)]))
    b.append(f'<text x="20" y="372" font-size="11.5" style="{FONT}" fill="{MUTED}">If the response disappears as masking rises, stop: overmasking. Accept a short plateau.</text>')
    return _svg(W, 384, "\n".join(b), "Plateau masking decision flow",
                "Set initial masking and present the tone. If there is no response, raise the tone 5 dB until there is one, then raise masking 10 dB. If there is a response and the threshold has held across 20 dB of masking, accept it; otherwise raise masking 10 dB and present again.")


def step_flow(bc=False):
    W = 560
    b = []
    start = ["Set masking to", "AC<tspan baseline-shift='sub' font-size='9'>NTE</tspan> + 30 dB" + (" + OEF" if bc else "")]
    b.append(_box(150, 10, 240, 46, start, "start"))
    b.append(_arrow([(270, 56), (270, 80)]))
    b.append(_box(150, 80, 240, 40, ["Recheck " + ("BC" if bc else "AC") + " threshold"]))
    b.append(_arrow([(270, 120), (270, 144)]))
    b.append(_box(150, 144, 240, 46, ["Response?"], "decision"))
    b.append(_arrow([(390, 167), (470, 167), (470, 200)], "Yes", 400, 160))
    b.append(_box(390, 200, 160, 40, ["Accept threshold"], "end"))
    b.append(_arrow([(270, 190), (270, 216)], "No", 278, 208))
    b.append(_box(150, 216, 240, 40, ["Raise tone until response"]))
    b.append(_arrow([(270, 256), (270, 280)]))
    b.append(_box(150, 280, 240, 46, ["Shift ≤ 15 dB?"], "decision"))
    b.append(_arrow([(390, 303), (470, 303), (470, 336)], "Yes", 400, 296))
    b.append(_box(390, 336, 160, 40, ["Accept threshold"], "end"))
    b.append(_arrow([(270, 326), (270, 352)], "No", 278, 344))
    b.append(_box(150, 352, 240, 40, ["Raise masking 20 dB, recheck"]))
    b.append(_arrow([(270, 392), (270, 416)]))
    b.append(_box(150, 416, 240, 46, ["Shift ≤ 10 dB, or", "no response at limit?"], "decision"))
    b.append(_arrow([(390, 439), (470, 439), (470, 472)], "Yes", 400, 432))
    b.append(_box(390, 472, 160, 40, ["Accept threshold"], "end"))
    b.append(_arrow([(150, 439), (40, 439), (40, 372), (150, 372)], "No: repeat", 44, 456))
    return _svg(W, 520, "\n".join(b), ("BC" if bc else "AC") + " step masking decision flow",
                "Set initial masking. Recheck. If there is a response, accept. If not, raise the tone until there is. If the shift is 15 dB or less, accept. Otherwise raise masking 20 dB and recheck; accept when the shift is 10 dB or less or there is no response at the limit, otherwise repeat.")


def plateau_graph():
    # masking level x (0-100), threshold y (dB HL), plateau shape
    W, H = 560, 330
    x0, y0, x1, y1 = 70, 280, 530, 30
    def X(m): return x0 + (m / 100) * (x1 - x0)
    def Y(t): return y0 - ((t - 0) / 100) * (y0 - y1)
    pts = [(10, 30), (20, 30), (30, 40), (40, 50), (50, 60), (60, 60), (70, 60), (80, 60), (90, 70), (100, 80)]
    path = "M" + " L".join(f"{X(m):.1f},{Y(t):.1f}" for m, t in pts)
    b = [f'<rect x="{X(25)}" y="{y1}" width="{X(48)-X(25)}" height="{y0-y1}" fill="{FILL}"/>',
         f'<rect x="{X(48)}" y="{y1}" width="{X(83)-X(48)}" height="{y0-y1}" fill="#e3f0e6"/>',
         f'<rect x="{X(83)}" y="{y1}" width="{X(100)-X(83)}" height="{y0-y1}" fill="#fbe9e7"/>']
    for g in range(0, 101, 20):
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(g)}" y2="{Y(g)}" stroke="{RULE}" stroke-width="0.8"/>')
        b.append(f'<text x="{x0-8}" y="{Y(g)+4}" text-anchor="end" font-size="11" fill="{MUTED}" style="{FONT}">{g}</text>')
        b.append(f'<text x="{X(g)}" y="{y0+18}" text-anchor="middle" font-size="11" fill="{MUTED}" style="{FONT}">{g}</text>')
    b.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{INK}"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}"/>')
    b.append(f'<text x="{(x0+x1)/2}" y="{H-4}" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">Masking level in non-test ear (dB EM)</text>')
    b.append(f'<text transform="translate(16,{(y0+y1)/2}) rotate(-90)" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">Test-ear threshold (dB HL)</text>')
    for lab, a, c in (("Undermasking", 10, 36), ("Plateau", 48, 65), ("Overmasking", 83, 91)):
        b.append(f'<text x="{X((a+c)/2 if lab!="Undermasking" else 30)}" y="{y1+16}" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}" style="{FONT}">{lab}</text>')
    for i in range(1, len(pts)):
        (m0, t0), (m1, t1) = pts[i-1], pts[i]
        b.append(f'<line data-i="{i}" x1="{X(m0):.1f}" y1="{Y(t0):.1f}" x2="{X(m1):.1f}" y2="{Y(t1):.1f}" stroke="{RIGHT}" stroke-width="3" stroke-linecap="round"/>')
    for i, (m, t) in enumerate(pts):
        b.append(f'<circle data-i="{i}" cx="{X(m):.1f}" cy="{Y(t):.1f}" r="6" fill="#fff" stroke="{RIGHT}" stroke-width="2.4"/>')
    b.append(f'<text data-i="6" x="{X(65)}" y="{Y(60)-14}" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">True threshold: 60 dB HL</text>')
    return _svg(W, H, "\n".join(b), "The masking function",
                "As masking rises, the test-ear threshold first rises with it (undermasking), then stays at 60 dB HL across 20 to 30 dB of masking (the plateau), then rises again as masking crosses to the test ear (overmasking).")


def hughson_westlake():
    seq = [(35, 1), (25, 0), (30, 1), (20, 0), (25, 1), (15, 0), (20, 1), (10, 0), (15, 0), (20, 1)]
    W, H = 560, 260
    x0, x1, y0, y1 = 60, 530, 220, 24
    def X(i): return x0 + 20 + i * ((x1 - x0 - 40) / (len(seq) - 1))
    def Y(d): return y1 + (d - 0) / 40 * (y0 - y1)  # dB HL increases downward, audiogram style
    b = []
    for d in range(0, 41, 5):
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(d)}" y2="{Y(d)}" stroke="{RULE}" stroke-width="{1 if d % 10 == 0 else 0.5}"/>')
        b.append(f'<text x="{x0-8}" y="{Y(d)+4}" text-anchor="end" font-size="11" fill="{MUTED}" style="{FONT}">{d}</text>')
    b.append(f'<text transform="translate(18,{(y0+y1)/2}) rotate(-90)" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">Level (dB HL)</text>')
    for i in range(1, len(seq)):
        b.append(f'<line data-i="{i}" x1="{X(i-1):.1f}" y1="{Y(seq[i-1][0]):.1f}" x2="{X(i):.1f}" y2="{Y(seq[i][0]):.1f}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    b.append(f'<line class="final" x1="{x0}" x2="{x1}" y1="{Y(20)}" y2="{Y(20)}" stroke="{RIGHT}" stroke-width="2"/>')
    b.append(f'<text class="final" x="{x0+6}" y="{Y(20)-6}" text-anchor="start" font-size="12" font-weight="700" fill="{RIGHT}" style="{FONT}">Threshold 20 dB HL</text>')
    for i, (d, r) in enumerate(seq):
        asc = i > 0 and seq[i - 1][0] < d
        fill = BRAND if r else "#fff"
        b.append(f'<circle data-i="{i}" cx="{X(i):.1f}" cy="{Y(d):.1f}" r="7" fill="{fill}" stroke="{BRAND}" stroke-width="2"/>')
        if r and asc:
            b.append(f'<text data-i="{i}" x="{X(i):.1f}" y="{Y(d)+24:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="{BRAND}" style="{FONT}">ascending</text>')
    b.append(f'<text x="{x0}" y="{H-6}" font-size="11.5" fill="{MUTED}" style="{FONT}">Filled = response. Only ascending responses count. Louder is lower, as on an audiogram.</text>')
    return _svg(W, H, "\n".join(b), "Finding threshold with 10-down 5-up",
                "Ten presentations: responses at 35, 30, 25, 20 and 20; misses at 25, 20, 15, 10 and 15. Two ascending responses at 20 dB HL give a threshold of 20 dB HL.")


def insert_depth():
    W, H = 560, 210
    b = []
    labels = [("Shallow", -14, "Use supra-aural values"), ("Intermediate (flush)", 0, "Insert values apply"), ("Deep", 14, "Insert values apply")]
    for i, (lab, off, note) in enumerate(labels):
        ox = 20 + i * 180
        # canal walls
        b.append(f'<path d="M{ox},40 L{ox+60},40 L{ox+60},70 L{ox+160},70" fill="none" stroke="{INK}" stroke-width="2"/>')
        b.append(f'<path d="M{ox},150 L{ox+60},150 L{ox+60},120 L{ox+160},120" fill="none" stroke="{INK}" stroke-width="2"/>')
        b.append(f'<line x1="{ox+156}" y1="66" x2="{ox+156}" y2="124" stroke="{MUTED}" stroke-width="3"/>')
        b.append(f'<text x="{ox+64}" y="34" font-size="10.5" fill="{MUTED}" style="{FONT}">canal entrance</text>')
        tx = ox + 60 + off
        b.append(f'<rect x="{tx}" y="74" width="34" height="42" rx="6" fill="#f4d35e" stroke="{INK}" stroke-width="1.2"/>')
        b.append(f'<line x1="{tx}" y1="95" x2="{tx-40}" y2="95" stroke="{INK}" stroke-width="3"/>')
        b.append(f'<line x1="{ox+60}" y1="64" x2="{ox+60}" y2="128" stroke="{BRAND}" stroke-width="1" stroke-dasharray="3 3"/>')
        b.append(f'<text x="{ox+80}" y="176" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}" style="{FONT}">{lab}</text>')
        b.append(f'<text x="{ox+80}" y="194" text-anchor="middle" font-size="11.5" fill="{MUTED}" style="{FONT}">{note}</text>')
    return _svg(W, H, "\n".join(b), "Insert earphone depth",
                "Three foam tip positions relative to the ear canal entrance: shallow, with the outer edge outside the entrance; intermediate, flush with the entrance; deep, fully inside. Insert IAA and OEF values apply at intermediate depth or deeper.")


def symbols():
    # NZ symbol set, redrawn
    W, H = 560, 300
    rows = [("Air conduction, unmasked", "o", "x"), ("Air conduction, masked", "O", "X"),
            ("Bone conduction, unmasked", "<", ">"), ("Bone conduction, masked", "[", "]"),
            ("Acoustic reflex, ipsilateral", "I", "I"), ("Acoustic reflex, contralateral", "Q", "Z")]
    b = [f'<text x="380" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="{RIGHT}" style="{FONT}">Right</text>',
         f'<text x="480" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="{LEFT}" style="{FONT}">Left</text>']
    def sym(k, x, y, c):
        if k == "o": return f'<circle cx="{x}" cy="{y}" r="8" fill="#fff" stroke="{c}" stroke-width="2"/>'
        if k == "O": return f'<circle cx="{x}" cy="{y}" r="8" fill="{c}"/>'
        if k == "x": return f'<path d="M{x-7},{y-7} L{x+7},{y+7} M{x+7},{y-7} L{x-7},{y+7}" stroke="{c}" stroke-width="2"/>'
        if k == "X": return f'<path d="M{x-8},{y-8} L{x+6},{y+6} M{x+6},{y-8} L{x-8},{y+6} M{x-6},{y-6} L{x+8},{y+8} M{x+8},{y-6} L{x-6},{y+8}" stroke="{c}" stroke-width="1.6"/>'
        if k == "<": return f'<path d="M{x+6},{y-9} L{x-6},{y} L{x+6},{y+9}" fill="none" stroke="{c}" stroke-width="2"/>'
        if k == ">": return f'<path d="M{x-6},{y-9} L{x+6},{y} L{x-6},{y+9}" fill="none" stroke="{c}" stroke-width="2"/>'
        if k == "[": return f'<path d="M{x+6},{y-9} L{x-6},{y} L{x+6},{y+9} Z" fill="none" stroke="{c}" stroke-width="2"/>'
        if k == "]": return f'<path d="M{x-6},{y-9} L{x+6},{y} L{x-6},{y+9} Z" fill="none" stroke="{c}" stroke-width="2"/>'
        if k == "I": return f'<path d="M{x-6},{y-8} L{x+6},{y-8} M{x},{y-8} L{x},{y+8} M{x-6},{y+8} L{x+6},{y+8}" stroke="{c}" stroke-width="2"/>'
        if k == "Q": return f'<rect x="{x-9}" y="{y-9}" width="18" height="18" fill="none" stroke="{c}" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="6" fill="none" stroke="{c}" stroke-width="1.6"/>'
        if k == "Z": return f'<rect x="{x-9}" y="{y-9}" width="18" height="18" fill="none" stroke="{c}" stroke-width="1.6"/><path d="M{x-9},{y-9} L{x+9},{y+9} M{x+9},{y-9} L{x-9},{y+9}" stroke="{c}" stroke-width="1.6"/>'
    for i, (lab, r, l) in enumerate(rows):
        y = 52 + i * 38
        b.append(f'<line x1="10" x2="550" y1="{y+19}" y2="{y+19}" stroke="{RULE}"/>')
        b.append(f'<text x="14" y="{y+5}" font-size="13" fill="{INK}" style="{FONT}">{lab}</text>')
        b.append(sym(r, 380, y, RIGHT)); b.append(sym(l, 480, y, LEFT))
    b.append(f'<text x="14" y="{H-12}" font-size="11.5" fill="{MUTED}" style="{FONT}">No response: add a downward arrow to the symbol. Soundfield: S. Redrawn from March 2026 Figure 3.</text>')
    return _svg(W, H, "\n".join(b), "NZ audiometric symbols", "Right ear in red, left in blue. AC unmasked: open circle and cross. AC masked: filled circle and double cross. BC unmasked: open angle brackets. BC masked: closed triangles. Reflexes: ipsilateral I-beam; contralateral boxed circle (right) and boxed cross (left).")


def cross_hearing():
    W, H = 560, 230
    b = []
    def bar(x, top, h, colour, label, val):
        return (f'<rect x="{x}" y="{top}" width="70" height="{h}" fill="{colour}" opacity="0.9"/>'
                f'<text x="{x+35}" y="{top-8}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{INK}" style="{FONT}">{val}</text>'
                f'<text x="{x+35}" y="206" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">{label}</text>')
    base = 190
    s = 1.6
    b.append(f'<line x1="20" x2="540" y1="{base}" y2="{base}" stroke="{INK}"/>')
    b.append(bar(60, base - 70 * s, 70 * s, RIGHT, "Tone in right (test) ear", "70 dB HL"))
    b.append(f'<path d="M140,{base-70*s+10} C220,{base-70*s} 260,{base-10*s-30} 300,{base-10*s-6}" fill="none" stroke="{INK}" stroke-width="1.4" marker-end="url(#ah)"/>')
    b.append(f'<text x="200" y="{base-70*s+2}" font-size="12" fill="{INK}" style="{FONT}">minus IAA 60 dB (insert, 1 kHz)</text>')
    b.append(bar(300, base - 10 * s, 10 * s, MUTED, "Reaches left cochlea", "10 dB"))
    b.append(bar(430, base - 5 * s, 5 * s, LEFT, "Left BC threshold", "5 dB HL"))
    b.append(f'<text x="20" y="226" font-size="12" fill="{INK}" style="{FONT}">10 dB reaches a cochlea that hears 5 dB: the left ear could respond. 70 − 5 = 65 ≥ 60, so mask.</text>')
    return _svg(W, H + 6, "\n".join(b), "Why we mask", "A 70 dB HL tone in the right ear loses 60 dB crossing the head, arriving at 10 dB. The left cochlea's threshold is 5 dB HL, so it could hear the tone. Masking is needed.")



def tymp_types():
    """Eight tympanogram types on the ASHA (1990) adult norm box."""
    import math
    W, H = 600, 560
    pw, ph = 170, 100
    types = [("A", 10, 1.0, 40, None), ("A-shallow", -20, 0.18, 60, None), ("A-deep", 20, 1.8, 25, None),
             ("C", -160, 1.0, 40, None), ("C-shallow", -230, 0.2, 60, None), ("C-deep", -240, 1.7, 25, None),
             ("B-low", None, 0.12, None, "low"), ("B-high", None, 1.6, None, "high")]
    notes = {"A": "Normal", "A-shallow": "Y < 0.3", "A-deep": "Y > 1.4", "C": "MEP < −100", "C-shallow": "MEP < −100, Y < 0.3",
             "C-deep": "MEP < −100, Y > 1.4", "B-low": "No peak, ECV 0.6–1.5", "B-high": "No peak, ECV > 1.5*"}
    b = []
    for i, (name, mep, y, w, flat) in enumerate(types):
        col, row = i % 3, i // 3
        ox, oy = 30 + col * 190, 20 + row * 175
        X = lambda p: ox + (p + 400) / 600 * pw
        Y = lambda v: oy + ph - v / 2.0 * ph
        b.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="#fff" stroke="{RULE}"/>')
        b.append(f'<rect x="{X(-100)}" y="{Y(1.4)}" width="{X(100)-X(-100)}" height="{Y(0.3)-Y(1.4)}" fill="{FILL}" stroke="{MUTED}" stroke-dasharray="3 2"/>')
        b.append(f'<line x1="{X(0)}" x2="{X(0)}" y1="{oy}" y2="{oy+ph}" stroke="{MUTED}" stroke-width="0.8"/>')
        pts = []
        for p in range(-400, 201, 5):
            if flat:
                v = y + (0.02 * math.sin(p / 120))
            else:
                v = 0.04 + (y - 0.04) / (1 + ((p - mep) / (w / 2)) ** 2)
            pts.append(f"{X(p):.1f},{Y(v):.1f}")
        colour = BRAND if name.startswith("A") else (LEFT if name.startswith("B") else RIGHT)
        b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" stroke-width="2.4"/>')
        b.append(f'<text x="{ox}" y="{oy+ph+18}" font-size="14" font-weight="700" fill="{INK}" style="{FONT}">{name}</text>')
        b.append(f'<text x="{ox}" y="{oy+ph+34}" font-size="11.5" fill="{MUTED}" style="{FONT}">{notes[name]}</text>')
        for p in (-400, -200, 0, 200):
            b.append(f'<text x="{X(p)}" y="{oy+ph+-2+12}" font-size="0" fill="none">.</text>')
    b.append(f'<text x="410" y="400" font-size="11.5" fill="{INK}" style="{FONT}">Each panel: −400 to +200 daPa,</text>')
    b.append(f'<text x="410" y="416" font-size="11.5" fill="{INK}" style="{FONT}">0 to 2.0 mmho. Shaded box:</text>')
    b.append(f'<text x="410" y="432" font-size="11.5" fill="{INK}" style="{FONT}">MEP −100 to +100 daPa,</text>')
    b.append(f'<text x="410" y="448" font-size="11.5" fill="{INK}" style="{FONT}">Y 0.3 to 1.4 mmho (ASHA 1990).</text>')
    b.append(f'<text x="410" y="472" font-size="11.5" fill="{MUTED}" style="{FONT}">* ECV also depends on probe depth;</text>')
    b.append(f'<text x="410" y="488" font-size="11.5" fill="{MUTED}" style="{FONT}">a true B-high is usually well</text>')
    b.append(f'<text x="410" y="504" font-size="11.5" fill="{MUTED}" style="{FONT}">over 2.5 cm³ in adults.</text>')
    return _svg(W, 540, "\n".join(b), "Tympanogram types",
                "Eight tympanogram types plotted against the adult norm box: A, A-shallow and A-deep peak inside the pressure range with normal, low or high admittance; C, C-shallow and C-deep peak below −100 daPa; B-low and B-high are flat, with normal or large ear canal volume.")


def art_pathway():
    W, H = 600, 260
    b = []
    def node(x, y, w, h, t, c=INK, fill="#fff"):
        lines = t.split("|")
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2 if w < 90 else 10}" fill="{fill}" stroke="{c}" stroke-width="1.8"/>'
        for i, ln in enumerate(lines):
            s += f'<text x="{x+w/2}" y="{y+h/2+5+(i-(len(lines)-1)/2)*14}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{c}" style="{FONT}">{ln}</text>'
        return s
    # right side (red), left side (blue)
    b.append(node(20, 170, 60, 44, "ME", RIGHT)); b.append(node(100, 170, 60, 44, "IE", RIGHT))
    b.append(node(190, 120, 70, 40, "CN", RIGHT)); b.append(node(180, 30, 100, 50, "SOC +|VII nucleus", RIGHT))
    b.append(node(520, 170, 60, 44, "ME", LEFT)); b.append(node(440, 170, 60, 44, "IE", LEFT))
    b.append(node(340, 120, 70, 40, "CN", LEFT)); b.append(node(320, 30, 100, 50, "SOC +|VII nucleus", LEFT))
    a = lambda d, c: f'<path d="{d}" fill="none" stroke="{c}" stroke-width="1.8" marker-end="url(#ah)"/>'
    b.append(a("M80,192 L98,192", INK)); b.append(a("M160,185 C175,175 185,160 195,155", INK))
    b.append(a("M520,192 L502,192", INK)); b.append(a("M440,185 C425,175 415,160 405,155", INK))
    b.append(a("M225,120 L228,82", RIGHT)); b.append(a("M375,120 L372,82", LEFT))
    b.append(a("M250,125 L330,80", MUTED)); b.append(a("M350,125 L270,80", MUTED))
    b.append(a("M180,50 C90,45 50,100 48,166", RIGHT)); b.append(a("M420,50 C510,45 550,100 552,166", LEFT))
    b.append(f'<text x="166" y="210" font-size="11.5" fill="{INK}" style="{FONT}">VIII</text><text x="410" y="210" font-size="11.5" fill="{INK}" style="{FONT}">VIII</text>')
    b.append(f'<text x="70" y="70" font-size="11.5" fill="{INK}" style="{FONT}">VII</text><text x="512" y="70" font-size="11.5" fill="{INK}" style="{FONT}">VII</text>')
    b.append(f'<text x="20" y="245" font-size="13" font-weight="700" fill="{RIGHT}" style="{FONT}">Right ear</text><text x="580" y="245" text-anchor="end" font-size="13" font-weight="700" fill="{LEFT}" style="{FONT}">Left ear</text>')
    b.append(f'<text x="300" y="245" text-anchor="middle" font-size="11" fill="{MUTED}" style="{FONT}">Grey arrows: crossed (contralateral) pathways</text>')
    return _svg(W, H, "\n".join(b), "Acoustic reflex pathway",
                "Sound enters the middle ear (ME) and inner ear (IE), travels along the VIII nerve to the cochlear nucleus (CN), then to the superior olivary complex and facial (VII) nucleus on both sides. The VII nerve then contracts the stapedius muscle in each middle ear. Redrawn after Emanuel (2009).")


def pi_function():
    W, H = 560, 300
    x0, x1, y0, y1 = 70, 530, 250, 30
    X = lambda d: x0 + d / 100 * (x1 - x0)
    Y = lambda p: y0 - p / 100 * (y0 - y1)
    pts = [(25, 10), (35, 40), (45, 76), (55, 94), (65, 94), (90, 94)]
    b = []
    for g in range(0, 101, 20):
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(g)}" y2="{Y(g)}" stroke="{RULE}" stroke-width="0.8"/><text x="{x0-8}" y="{Y(g)+4}" text-anchor="end" font-size="11" fill="{MUTED}" style="{FONT}">{g}</text>')
        b.append(f'<text x="{X(g)}" y="{y0+18}" text-anchor="middle" font-size="11" fill="{MUTED}" style="{FONT}">{g}</text>')
    b.append(f'<text x="{(x0+x1)/2}" y="{H-6}" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">Presentation level (dB HL)</text>')
    b.append(f'<text transform="translate(18,{(y0+y1)/2}) rotate(-90)" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">Phonemes correct (%)</text>')
    for i in range(1, len(pts)):
        (d0, p0), (d1, p1) = pts[i-1], pts[i]
        b.append(f'<line data-i="{i}" x1="{X(d0):.1f}" y1="{Y(p0):.1f}" x2="{X(d1):.1f}" y2="{Y(p1):.1f}" stroke="{RIGHT}" stroke-width="3" stroke-linecap="round"/>')
    for i, (d, p) in enumerate(pts):
        b.append(f'<circle data-i="{i}" cx="{X(d):.1f}" cy="{Y(p):.1f}" r="6" fill="#fff" stroke="{RIGHT}" stroke-width="2.4"/>')
    b.append(f'<g class="final"><line x1="{x0}" x2="{X(37)}" y1="{Y(47)}" y2="{Y(47)}" stroke="{BRAND}" stroke-dasharray="4 3"/><line x1="{X(37)}" x2="{X(37)}" y1="{Y(47)}" y2="{y0}" stroke="{BRAND}" stroke-dasharray="4 3"/>')
    b.append(f'<text x="{X(40)+6}" y="{Y(30)}" font-size="12" font-weight="700" fill="{BRAND}" style="{FONT}">HPL ≈ 37 dB HL (half of 94%)</text></g>')
    b.append(f'<text data-i="3" x="{X(55)}" y="{Y(94)-14}" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}" style="{FONT}">PI max 94% at 55 dB HL</text>')
    b.append(f'<text data-i="5" x="{X(90)}" y="{Y(94)+22}" text-anchor="end" font-size="11.5" fill="{MUTED}" style="{FONT}">No rollover at 90 dB HL</text>')
    return _svg(W, H, "\n".join(b), "A performance-intensity function",
                "Scores rise from 10% at 25 dB HL to a maximum of 94% at 55 dB HL and stay there at 65 and 90 dB HL. Half of 94% is 47%, reached at about 37 dB HL: the half-peak level.")

FIGURES = {
    "plateau-flow": ("Plateau masking", plateau_flow),
    "plateau-graph": ("The masking function", plateau_graph),
    "step-flow-ac": ("AC step masking", lambda: step_flow(False)),
    "step-flow-bc": ("BC step masking", lambda: step_flow(True)),
    "hughson-westlake": ("Finding threshold: 10 down, 5 up", hughson_westlake),
    "insert-depth": ("Insert earphone depth", insert_depth),
    "symbols": ("NZ audiometric symbols", symbols),
    "cross-hearing": ("Why we mask: cross-hearing", cross_hearing),
    "tymp-types": ("Tympanogram types", tymp_types),
    "art-pathway": ("Acoustic reflex pathway (redrawn after Emanuel, 2009)", art_pathway),
    "pi-function": ("A performance-intensity function", pi_function),
}
ANIMATED = {"plateau-graph", "hughson-westlake", "pi-function"}
# Step captions for the step-through animations (one per data-i step)
STEPS = {
    "hughson-westlake": [
        "35 dB HL: response. Go down 10 dB.",
        "25 dB HL: no response. Go up 5 dB.",
        "30 dB HL: response on the way up (1st ascending response). Go down 10 dB.",
        "20 dB HL: no response. Go up 5 dB.",
        "25 dB HL: response on the way up. Go down 10 dB.",
        "15 dB HL: no response. Go up 5 dB.",
        "20 dB HL: response on the way up (1st at 20). Go down 10 dB.",
        "10 dB HL: no response. Go up 5 dB.",
        "15 dB HL: no response. Go up 5 dB.",
        "20 dB HL: response on the way up (2nd at 20), and none lower. Threshold is 20 dB HL.",
    ],
    "plateau-graph": [
        "Masking 10 dB: threshold 30 dB HL.",
        "Masking 20 dB: still 30 dB HL. The masking is too low to reach the non-test cochlea yet.",
        "Masking 30 dB: threshold rises to 40. The non-test ear was hearing the tone: undermasking.",
        "Masking 40 dB: rises to 50. Still undermasked: keep going.",
        "Masking 50 dB: rises to 60.",
        "Masking 60 dB: stays at 60. The plateau has started.",
        "Masking 70 dB: still 60. Steady over 20 dB of masking: 60 dB HL is the true threshold.",
        "Masking 80 dB: still 60. You can stop at a 20 dB plateau; this point is shown for the full picture.",
        "Masking 90 dB: rises to 70. Masking is now crossing back to the test ear: overmasking.",
        "Masking 100 dB: rises to 80. Overmasking.",
    ],
    "pi-function": [
        "25 dB HL: 10% of phonemes correct.",
        "35 dB HL: 40%.",
        "45 dB HL: 76%. Scores climb steeply in the middle of the curve.",
        "55 dB HL: 94%. The best score, at the lowest level that gives it: PI max.",
        "65 dB HL: still 94%.",
        "90 dB HL: still 94%, so no rollover. Half of 94% is 47%, reached at about 37 dB HL: the half-peak level.",
    ],
}
PRINT_FIGS = {"plateau-flow", "step-flow-ac", "step-flow-bc", "symbols", "tymp-types"}
