#!/usr/bin/env python3
"""Build the MAud Clinical Checklist from one source.
   content/*.yaml  ->  site/ (GitHub Pages)  +  print/cards.html (-> PDF)
"""
import io, shutil, pathlib, yaml, qrcode, qrcode.image.svg
from jinja2 import Environment, DictLoader, select_autoescape
from markupsafe import Markup
import figures as F

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
PRINT = ROOT / "print"
BASE_URL = "https://jakalnz.github.io/maud-checklist/"   # change when the repo moves
REPO = "jakalnz/maud-checklist"                          # GitHub owner/repo for "Edit these tips" links
BRANCH = "main"

data = yaml.safe_load((ROOT / "content/pta-masking.yaml").read_text())
mod = data["module"]
cards = data["cards"]
diffs = data["differences"]

def qr_svg(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    buf = io.BytesIO(); img.save(buf)
    s = buf.getvalue().decode()
    s = s[s.index("<svg"):]
    return Markup(s.replace("<svg", '<svg class="qr" role="img" aria-label="QR code to the teaching page"', 1))

def page_name(c): return c["id"].lower() + ".html"

import re, html
def load_ptf(cid):
    f = ROOT / "content/ptf" / (cid.lower() + ".md")
    if not f.exists(): return []
    text = re.sub(r"<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S)
    tips = []
    for line in text.splitlines():
        if line.startswith("- ") and line[2:].strip():
            t = line[2:].strip()
            m = re.search(r"\(([A-Za-z]{1,4})\)\s*$", t)
            who = m.group(1).upper() if m else ""
            if m: t = t[:m.start()].rstrip()
            tips.append({"text": html.escape(t), "who": who})
    return tips

for c in cards:
    c["ptf"] = load_ptf(c["id"])
    c["ptf_edit"] = f"https://github.com/{REPO}/edit/{BRANCH}/content/ptf/{c['id'].lower()}.md"
    c["url"] = BASE_URL + "pta/" + page_name(c)
    c["qr"] = qr_svg(c["url"])
    c["pods"] = []
    for b in c["blocks"]:
        if b.get("pod") and b["pod"] not in c["pods"]:
            c["pods"].append(b["pod"])

FIGS = {k: Markup(fn()) for k, (_, fn) in F.FIGURES.items()}
FIGT = {k: t for k, (t, _) in F.FIGURES.items()}

T = {}
T["card"] = r"""
{% macro valtables(c, wide) %}{% for v in c.get('values') or [] %}{% if ((v.header|length > 6) or v.place == 'steps') == wide %}
      <div class="valwrap">
        <table class="vals"><caption>{{ v.caption }}</caption>
          <thead><tr>{% for h in v.header %}<th scope="col">{{ h }}</th>{% endfor %}</tr></thead>
          <tbody>{% for r in v.rows %}<tr>{% for x in r %}{% if loop.first %}<th scope="row">{{ x }}</th>{% else %}<td>{{ x }}</td>{% endif %}{% endfor %}</tr>{% endfor %}</tbody>
        </table>
        {% if v.note %}<p class="vals-note">{{ v.note }}</p>{% endif %}
        <p class="src">Source: {{ v.source }}</p>
      </div>
{% endif %}{% endfor %}{% endmacro %}
{% macro blocks(c, medium, side) %}      {% for b in c.blocks if (b.side or False) == side %}
      <section class="block">
        <h3>{{ b.title }}</h3>
        <ol class="steps" start="1">
          {% for s in b.steps %}<li>{{ s|safe }}{% if loop.last and b.pod %}{% if medium == 'site' %}<a class="pod-mark" href="#pod-{{ b.pod }}" title="Differs from NZAS BPG: see Points of difference">≠</a>{% else %}<span class="pod-mark" title="Differs from NZAS BPG">≠</span>{% endif %}{% endif %}</li>{% endfor %}
        </ol>
        {% if b.rule %}<div class="rule"><span class="ico" aria-hidden="true">=</span><span>{{ b.rule|safe }}</span></div>{% endif %}
        {% if b.example %}<p class="example">{{ b.example|safe }}</p>{% endif %}
        {% if b.stop %}<div class="callout stop" style="margin:6px 0 0 2.2em"><span class="lbl">⬣ Stop</span>{{ b.stop|safe }}</div>{% endif %}
      </section>
      {% endfor %}
{% endmacro %}
{% macro card(c, medium) %}
<article class="card" id="card-{{ c.id|lower }}">
  <header class="card-head">
    <div class="head-shape"><span class="card-id">{{ c.id }}</span>
    <h2 class="card-title">{{ c.title }}</h2></div>
    <div class="card-mode"><b>{{ 'Read and do' if c.mode == 'READ-DO' else 'Do, then confirm' }}</b>{{ 'Follow step by step' if c.mode == 'READ-DO' else 'Do from memory, then check' }}</div>
  </header>
  <p class="card-purpose">{{ c.purpose|safe }}</p>
  <div class="card-body">
    <div class="card-steps">
      {% if c.when %}<ul class="card-when">{% for w in c.when %}<li>{{ w|safe }}</li>{% endfor %}</ul>{% endif %}
      {% set ns = namespace(n=0) %}
      {{ blocks(c, medium, False) }}
      <div style="margin-top:12px">{{ valtables(c, True) }}</div>
      {% if medium == 'print' and 'symbols' in (c.figures or []) %}<div style="margin-top:10px">{{ figs['symbols'] }}</div>{% endif %}
    </div>
    <aside class="card-side">
      {% if c.blocks|selectattr('side')|list %}<div>{{ blocks(c, medium, True) }}</div>{% endif %}
      {{ valtables(c, False) }}
      {% for n in c.notes or [] %}
        {% if n.kind == 'stop' %}<div class="callout stop"><span class="lbl">⬣ Stop</span>{{ n.text|safe }}</div>
        {% elif n.kind == 'rule' %}<div class="callout rule-note"><span class="lbl">= Rule</span>{{ n.text|safe }}</div>
        {% else %}<div class="callout note"><span class="lbl">ⓘ Note</span>{{ n.text|safe }}</div>{% endif %}
      {% endfor %}
      {% if c.script and medium == 'print' %}
      <div class="callout note"><span class="lbl">“ Say</span>{% for s in c.script %}<br>{{ s }}{% endfor %}</div>
      {% endif %}
      
    </aside>
  </div>
  <footer class="card-foot">
    <div>
      {{ mod.title }} · Card {{ c.id }} · v{{ mod.version }} · {{ mod.date }} · from March 2026 checklist §{{ c.source }}<br>
      {% if c.pods %}<span style="color:var(--pod)"><b>≠</b> Differs from NZAS BPG. </span>{% endif %}
      {% if medium == 'print' %}Scan for explanation, video and practice.{% endif %}
    </div>
    {% if medium == 'print' %}{{ c.qr }}{% endif %}
  </footer>
</article>
{% endmacro %}
"""

T["shell"] = r"""{% from 'card' import card with context %}<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · MAud Clinical Checklist</title>
<meta name="description" content="{{ desc }}">
<link rel="stylesheet" href="{{ up }}assets/style.css">
<link rel="icon" href="{{ up }}assets/favicon.svg">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><a href="{{ up }}index.html">MAud Clinical Checklist</a><span class="sub">University of Auckland · Master of Audiology</span></div>
<div class="draft-banner">Version {{ mod.version }} for review. Built from the March 2026 checklist; not yet approved for clinical teaching.</div>
<div class="shell">
<nav class="index" aria-label="Protocols"><details id="navd" open><summary class="navsum">All protocols</summary>
  <label for="q" class="src">Search protocols</label>
  <input id="q" type="search" placeholder="e.g. plateau, OEF, bone" autocomplete="off">
  <h2>{{ mod.title }}</h2>
  <ol id="navlist">
  {% for c in cards %}<li data-k="{{ (c.id ~ ' ' ~ c.title ~ ' ' ~ (c.blocks|map(attribute='title')|join(' ')))|lower }}"><a href="{{ up }}pta/{{ c.id|lower }}.html"{% if cur and cur.id == c.id %} aria-current="page"{% endif %}><span>{{ c.id }}</span><span>{{ c.title }}</span></a></li>{% endfor %}
  </ol>
  <h2>For reviewers</h2>
  <ol><li><a href="{{ up }}review.html"{% if review %} aria-current="page"{% endif %}><span>Log</span><span>Errors and points of difference</span></a></li>
  <li><a href="{{ up }}print/cards.pdf"><span>PDF</span><span>Print cards</span></a></li>
  <li><a href="{{ up }}ptf-editing.html"><span>PTFs</span><span>How to add tips</span></a></li></ol>
</details></nav>
<main id="main"><div class="measure">
{{ body }}
</div></main></div>
<script>
if(matchMedia('(max-width:900px)').matches){document.getElementById('navd').open=false}
const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();document.querySelectorAll('#navlist li').forEach(li=>{li.hidden=v&&!li.dataset.k.includes(v)})});
document.querySelectorAll('.replay').forEach(b=>b.addEventListener('click',()=>{const f=document.getElementById(b.dataset.for);f.classList.remove('anim');void f.offsetWidth;f.classList.add('anim')}));
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('anim');io.unobserve(e.target)}}),{threshold:.4});
document.querySelectorAll('[data-animate]').forEach(el=>io.observe(el));
document.querySelectorAll('a.pod-mark').forEach(a=>a.addEventListener('click',()=>{const d=document.getElementById('layer-pod');if(d)d.open=true}));
</script>
</body></html>"""

T["page"] = r"""{% from 'card' import card with context %}
<p class="crumbs"><a href="../index.html">{{ mod.title }}</a> / {{ c.id }}</p>
{{ card(c, 'site') }}
<p class="src" style="margin-top:6px">The box above is the print card, word for word. <a href="../print/cards.pdf">Print the card set</a>.</p>

<details class="layer" open><summary>Why <span class="hint">the reason behind each block</span></summary><div class="layer-body">
{% for b in c.blocks if b.why %}<div class="why-item"><h4>{{ b.title }}</h4><p>{{ b.why|safe }}</p></div>{% endfor %}
{% if c.script %}<div class="why-item"><h4>What to say</h4><ul>{% for s in c.script %}<li>{{ s }}</li>{% endfor %}</ul></div>{% endif %}
</div></details>

{% if c.figures or c.media_planned %}
<details class="layer" open><summary>See it <span class="hint">diagrams, animations and video</span></summary><div class="layer-body">
{% for f in c.figures or [] %}<figure id="fig-{{ f }}"{% if f in animated %} data-animate{% endif %}>{{ figs[f] }}<figcaption>{{ figt[f] }}</figcaption>{% if f in animated %}<button class="replay" data-for="fig-{{ f }}" type="button">Replay animation</button>{% endif %}</figure>{% endfor %}
{% if c.media_planned %}<p class="src">Media still to make:</p><ul class="planned">{% for m in c.media_planned %}<li>{{ m }}</li>{% endfor %}</ul>{% endif %}
</div></details>{% endif %}

{% if c.sim %}<details class="layer" open><summary>Try it <span class="hint">practise in the simulator</span></summary><div class="layer-body try">
<a class="btn" href="{{ c.sim.url }}" target="_blank" rel="noopener">Open the {{ c.sim.name }}</a><span>{{ c.sim.label }}</span>
</div></details>{% endif %}

<details class="layer" open id="ptf"><summary>PTF tips <span class="hint">advice from our clinical teachers</span></summary><div class="layer-body">
<div class="ptf"><span class="who">From the Professional Teaching Fellows</span>
{% if c.ptf %}<ul>{% for t in c.ptf %}<li>{{ t.text|safe }}{% if t.who %} <span class="initials">{{ t.who }}</span>{% endif %}</li>{% endfor %}</ul>{% else %}<p>No tips yet for this protocol.</p>{% endif %}
<p class="ptf-edit"><a href="{{ c.ptf_edit }}" target="_blank" rel="noopener">Edit these tips</a> · <a href="../ptf-editing.html">How PTFs add tips</a></p></div>
</div></details>

{% if c.check %}<details class="layer"><summary>Check yourself <span class="hint">{{ c.check|length }} question{{ 's' if c.check|length > 1 }}</span></summary><div class="layer-body">
{% for x in c.check %}<div class="qa"><p><b>Q{{ loop.index }}.</b> {{ x.q|safe }}</p><details><summary>Show answer</summary><p>{{ x.a|safe }}</p></details></div>{% endfor %}
</div></details>{% endif %}

{% if c.pods %}<details class="layer" id="layer-pod"><summary>Points of difference <span class="hint">where NZAS guidance differs</span></summary><div class="layer-body">
{% for k in c.pods %}{% set d = diffs[k] %}<div class="pod-box" id="pod-{{ k }}"><h4>≠ {{ d.title }}</h4><dl><dt>We teach</dt><dd>{{ d.ours }}</dd><dt>NZAS BPG</dt><dd>{{ d.bpg }}</dd><dt>Why</dt><dd>{{ d.why }}</dd><dt>Status</dt><dd><span class="status">{{ d.status }}</span></dd></dl></div>{% endfor %}
</div></details>{% endif %}

{% if c.fixes %}<details class="layer"><summary>Changes from March 2026 <span class="hint">for reviewers</span></summary><div class="layer-body"><ul class="fixes">{% for f in c.fixes %}<li>{{ f }}</li>{% endfor %}</ul></div></details>{% endif %}

{% if c.refs %}<details class="layer"><summary>References</summary><div class="layer-body"><ul class="refs">{% for r in c.refs %}<li>{{ r }}</li>{% endfor %}</ul></div></details>{% endif %}

<nav class="pager" aria-label="Previous and next">
{% if prev %}<a href="{{ prev.id|lower }}.html">← {{ prev.id }} {{ prev.title }}</a>{% else %}<span></span>{% endif %}
{% if nxt %}<a href="{{ nxt.id|lower }}.html">{{ nxt.id }} {{ nxt.title }} →</a>{% endif %}
</nav>
"""

T["home"] = r"""
<div class="hero-shape"><img class="hero-logo" src="assets/uoa-logo-reversed.png" alt="Waipapa Taumata Rau University of Auckland"><p>Master of Audiology Clinical Checklist</p><h1>{{ mod.title }}</h1></div>
<p class="home-lead">Each protocol has a print card with the steps, and a teaching page that adds the reasons, diagrams, simulator practice and tips from our clinical teachers. The steps are the same in both.</p>
<div class="legend">
  <div class="callout stop"><span class="lbl">⬣ Stop</span>Safety or contraindication. Do not go on.</div>
  <div class="callout rule-note"><span class="lbl">= Rule</span>A decision formula you apply every time.</div>
  <div class="callout note"><span class="lbl">ⓘ Note</span>Practical detail for the bench.</div>
  <div class="pod-box" style="margin:0"><b style="color:var(--pod)">≠ Point of difference</b><br>We teach this differently from the NZAS guideline.</div>
  <div class="ptf"><b>PTF tip</b><br>Advice from our Professional Teaching Fellows.</div>
</div>
<h2>Protocols</h2>
<ul class="cardlist">{% for c in cards %}<li><a href="pta/{{ c.id|lower }}.html"><span class="cid">{{ c.id }}</span><span>{{ c.title }}</span><span class="mode">{{ 'Read and do' if c.mode == 'READ-DO' else 'Do, then confirm' }}</span></a></li>{% endfor %}</ul>
<p class="src" style="margin-top:20px">Modules still to build from the March 2026 checklist: case history, otoscopy, classification and referral, speech audiometry and masking, immittance, OAE, feedback and management, paediatric testing, infection control.</p>
"""

T["review"] = r"""
<h1 style="color:var(--brand)">Review log: {{ mod.title }}</h1>
<p>Everything this draft changed from the March 2026 checklist, and every place it differs from NZAS best practice guidelines. Reviewer for now: MS.</p>
<h2>Points of difference</h2>
<table class="reviewtbl"><thead><tr><th>Topic</th><th>We teach</th><th>NZAS BPG</th><th>Status</th></tr></thead><tbody>
{% for k, d in diffs.items() %}<tr id="pod-{{ k }}"><td><b>{{ d.title }}</b></td><td>{{ d.ours }}</td><td>{{ d.bpg }}</td><td>{{ d.status }}</td></tr>{% endfor %}
</tbody></table>
<h2>Errors fixed and wording changes</h2>
<table class="reviewtbl"><thead><tr><th>Card</th><th>Change</th></tr></thead><tbody>
{% for c in cards %}{% for f in c.fixes or [] %}<tr><td><a href="pta/{{ c.id|lower }}.html">{{ c.id }}</a></td><td>{{ f }}</td></tr>{% endfor %}{% endfor %}
</tbody></table>
"""

T["ptfhelp"] = r"""
<h1 style="color:var(--brand)">How PTFs add tips</h1>
<p>PTF tips live in one short text file per protocol. You edit them in your web browser; no coding is needed. Your change goes live a few minutes after it is approved.</p>
<h2>Once only</h2>
<ol class="steps cont" style="max-width:68ch">
  <li>Create a free account at <a href="https://github.com/signup">github.com</a> using your university email.</li>
  <li>Send your GitHub username to MS, who will add you to the checklist as an editor.</li>
</ol>
<h2>Each time</h2>
<ol class="steps cont" style="max-width:68ch">
  <li>Open the protocol page and go to <b>PTF tips</b>.</li>
  <li>Select <b>Edit these tips</b>. The tips file opens in GitHub's editor.</li>
  <li>Add, change or delete lines. Each tip is one line starting with a dash and a space: <code>- </code></li>
  <li>To be credited, add your initials in brackets at the end, for example <code>(AS)</code>.</li>
  <li>Select <b>Commit changes</b>, write a few words about what you changed, and choose <b>Propose changes</b> (or <b>Commit</b> if you have been given direct access).</li>
  <li>MS reviews and approves. The site rebuilds itself and the tip appears on the page.</li>
</ol>
<h2>Writing a good tip</h2>
<ul style="max-width:68ch">
  <li>One or two short sentences, in your own voice.</li>
  <li>Something a student would not get from the steps: a common mistake, what to watch for, a habit that helps.</li>
  <li>Tips are advice, not rules. If it changes a step, raise it with MS instead so the print card changes too.</li>
</ul>
<h2>All tip files</h2>
<ul class="cardlist">{% for c in cards %}<li><a href="{{ c.ptf_edit }}" target="_blank" rel="noopener"><span class="cid">{{ c.id }}</span><span>{{ c.title }}</span><span class="mode">{{ c.ptf|length }} tip{{ 's' if c.ptf|length != 1 }}</span></a></li>{% endfor %}</ul>
"""

T["print"] = r"""{% from 'card' import card with context %}<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><title>MAud Clinical Checklist · {{ mod.title }} · print cards</title>
<link rel="stylesheet" href="../assets/style.css"></head>
<body class="print">
<section class="cover">
  <div class="cover-shape">
    <img class="cover-logo" src="../assets/uoa-logo-reversed.png" alt="Waipapa Taumata Rau University of Auckland">
    <p style="font-weight:500;font-size:11pt;margin:0;opacity:.9">Master of Audiology</p>
    <h1 style="font-size:30pt;margin:5mm 0 2mm">Clinical Checklist</h1>
    <p style="font-size:16pt;margin:0;font-weight:500">{{ mod.title }}</p>
    <p style="font-size:9pt;margin:4mm 0 0;opacity:.85">Print cards · version {{ mod.version }} · {{ mod.date }}</p>
  </div>
  <div>
    <h2 style="color:var(--brand);font-size:13pt">How to use these cards</h2>
    <p style="max-width:150mm">One protocol per page. <b>Read and do</b> cards are followed step by step. <b>Do, then confirm</b> cards are done from memory and checked at a pause. Scan the QR code on any card for the reasons, diagrams and simulator practice.</p>
    <div class="legend" style="max-width:170mm">
      <div class="callout stop"><span class="lbl">⬣ Stop</span>Safety or contraindication.</div>
      <div class="callout rule-note"><span class="lbl">= Rule</span>Decision formula.</div>
      <div class="callout note"><span class="lbl">ⓘ Note</span>Practical detail.</div>
      <div class="callout" style="border-left-color:var(--pod);background:var(--pod-wash)"><span class="lbl" style="color:var(--pod)">≠</span>Differs from NZAS BPG; see teaching page.</div>
    </div>
    <ol style="columns:2;font-size:10.5pt">{% for c in cards %}<li style="list-style:none"><b style="color:var(--brand)">{{ c.id }}</b> {{ c.title }}</li>{% endfor %}</ol>
  </div>
  <div class="cover-foot"><p style="font-size:6.5pt;color:var(--muted);max-width:110mm;margin:0">DRAFT for review, built from the Clinical Checklist March 2026 (sections 4–5). Not yet approved for clinical teaching. © Section of Audiology, The University of Auckland.</p><svg class="unaunahi" viewBox="0 0 300 150" aria-hidden="true"><circle cx="150" cy="190" r="150" fill="#cecedb"/><circle cx="150" cy="210" r="130" fill="#6d6d91"/><circle cx="150" cy="230" r="110" fill="var(--brand)"/></svg></div>
</section>
{% for c in cards %}{{ card(c, 'print') }}
{% for f in c.figures or [] %}{% if f in print_figs and f != 'symbols' %}
<article class="card flowpage"><header class="card-head"><div class="head-shape"><span class="card-id">{{ c.id }}</span><h2 class="card-title">{{ figt[f] }}: decision flow</h2></div><div class="card-mode"><b>Back of card</b>Same rules as the front</div></header>
<div class="fig-wrap">{{ figs[f] }}</div>
<footer class="card-foot"><div>{{ mod.title }} · Card {{ c.id }} (flowchart) · v{{ mod.version }} · {{ mod.date }}</div></footer></article>
{% endif %}{% endfor %}{% endfor %}
</body></html>"""

env = Environment(loader=DictLoader(T), autoescape=select_autoescape(default=False))
common = dict(mod=mod, cards=cards, diffs=diffs, figs=FIGS, figt=FIGT, animated=F.ANIMATED, print_figs=F.PRINT_FIGS)

if SITE.exists(): shutil.rmtree(SITE)
(SITE / "pta").mkdir(parents=True)
(SITE / "print").mkdir()
shutil.copytree(ROOT / "assets", SITE / "assets")
shutil.copytree(ROOT / "fonts", SITE / "assets/fonts")
(SITE / ".nojekyll").write_text("")

def shell(body, title, desc, up, cur=None, review=False):
    return env.get_template("shell").render(body=Markup(body), title=title, desc=desc, up=up, cur=cur, review=review, **common)

(SITE / "index.html").write_text(shell(env.get_template("home").render(**common), mod.get("title"), "MAud clinical protocols: print cards and teaching pages.", ""))
(SITE / "ptf-editing.html").write_text(shell(env.get_template("ptfhelp").render(**common), "How PTFs add tips", "How Professional Teaching Fellows edit PTF tips.", ""))
(SITE / "review.html").write_text(shell(env.get_template("review").render(**common), "Review log", "Errors fixed and points of difference.", "", review=True))
for i, c in enumerate(cards):
    body = env.get_template("page").render(c=c, prev=cards[i-1] if i else None, nxt=cards[i+1] if i+1 < len(cards) else None, **common)
    (SITE / "pta" / page_name(c)).write_text(shell(body, f"{c['id']} {c['title']}", c["purpose"], "../", cur=c))

PRINT.mkdir(exist_ok=True)
(SITE / "print" / "cards.html").write_text(env.get_template("print").render(**common))
print("built", len(cards), "cards")
