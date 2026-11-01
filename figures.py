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
    b.append(f'<path class="draw" d="{path}" fill="none" stroke="{RIGHT}" stroke-width="3" stroke-linejoin="round"/>')
    for i, (m, t) in enumerate(pts):
        b.append(f'<circle class="pt" style="--i:{i}" cx="{X(m):.1f}" cy="{Y(t):.1f}" r="6" fill="#fff" stroke="{RIGHT}" stroke-width="2.4"/>')
    b.append(f'<text x="{X(65)}" y="{Y(60)-14}" text-anchor="middle" font-size="12" fill="{INK}" style="{FONT}">True threshold: 60 dB HL</text>')
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
    path = "M" + " L".join(f"{X(i):.1f},{Y(d):.1f}" for i, (d, r) in enumerate(seq))
    b.append(f'<path class="draw" d="{path}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    for i, (d, r) in enumerate(seq):
        asc = i > 0 and seq[i - 1][0] < d
        fill = BRAND if r else "#fff"
        b.append(f'<circle class="pt" style="--i:{i}" cx="{X(i):.1f}" cy="{Y(d):.1f}" r="7" fill="{fill}" stroke="{BRAND}" stroke-width="2"/>')
        if r and asc:
            b.append(f'<text class="pt" style="--i:{i}" x="{X(i):.1f}" y="{Y(d)+24:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="{BRAND}" style="{FONT}">ascending</text>')
    b.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(20)}" y2="{Y(20)}" stroke="{RIGHT}" stroke-width="2"/>')
    b.append(f'<text x="{x0+6}" y="{Y(20)-6}" text-anchor="start" font-size="12" font-weight="700" fill="{RIGHT}" style="{FONT}">Threshold 20 dB HL</text>')
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


FIGURES = {
    "plateau-flow": ("Plateau masking", plateau_flow),
    "plateau-graph": ("The masking function", plateau_graph),
    "step-flow-ac": ("AC step masking", lambda: step_flow(False)),
    "step-flow-bc": ("BC step masking", lambda: step_flow(True)),
    "hughson-westlake": ("Finding threshold: 10 down, 5 up", hughson_westlake),
    "insert-depth": ("Insert earphone depth", insert_depth),
    "symbols": ("NZ audiometric symbols", symbols),
    "cross-hearing": ("Why we mask: cross-hearing", cross_hearing),
}
ANIMATED = {"plateau-graph", "hughson-westlake"}
PRINT_FIGS = {"plateau-flow", "step-flow-ac", "step-flow-bc", "symbols"}
