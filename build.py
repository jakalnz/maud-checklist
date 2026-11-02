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

SITEINFO = {"title": "Clinical Checklist", "version": "0.2 draft", "date": "2026-11-02"}
mod = SITEINFO                     # site-wide version/date used in banners and footers
modules, cards, diffs = [], [], {}
for f in sorted((ROOT / "content").glob("*.yaml")):
    d = yaml.safe_load(f.read_text(encoding="utf-8"))
    m = d["module"]
    m["cards"] = d["cards"]
    modules.append(m)
    for k, v in (d.get("differences") or {}).items():
        assert k not in diffs, f"duplicate difference key {k}"
        diffs[k] = v
modules.sort(key=lambda m: m["order"])
for m in modules:
    for c in m["cards"]:
        c["mod"] = m
        c["dir"] = m["id"]
        cards.append(c)

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
    c["url"] = BASE_URL + c["dir"] + "/" + page_name(c)
    c["qr"] = qr_svg(c["url"])
    c["pods"] = []
    c.setdefault("refs", [])
    for b in c["blocks"]:
        p = b.get("pod")
        b["podlist"] = p if isinstance(p, list) else ([p] if p else [])
        b["pod"] = b["podlist"][0] if b["podlist"] else None
        for k in b["podlist"]:
            if k not in c["pods"]:
                c["pods"].append(k)
    for k in c.get("also_pods") or []:
        if k not in c["pods"]:
            c["pods"].append(k)

FIGS = {k: Markup(fn()) for k, (_, fn) in F.FIGURES.items()}
FIGT = {k: t for k, (t, _) in F.FIGURES.items()}
# Image figures (forms): pages sit one folder down, so paths start with ../
IMAGES = {"adult-history-form": ("UoA Adult History Form", "assets/forms/adult-history-form.png"),
          "child-history-form": ("UoA Child History Form", "assets/forms/child-history-form.jpg")}
for k, (t, p) in IMAGES.items():
    FIGS[k] = Markup(f'<img class="fig" src="../{p}" alt="{t}" loading="lazy">')
    FIGT[k] = t

# Callout icons, drawn as inline SVG so they look the same on screen and in print (Inter lacks these glyphs)
def _ico(body, label):
    return Markup(f'<svg class="ico" viewBox="0 0 16 16" aria-hidden="true" focusable="false">{body}</svg>')
ICON = {
    "stop": _ico('<path d="M5.2 1h5.6L15 5.2v5.6L10.8 15H5.2L1 10.8V5.2z" fill="currentColor"/>', "Stop"),
    "rule": _ico('<path d="M8 1.2 14.8 8 8 14.8 1.2 8z" fill="currentColor"/>', "Rule"),
    "note": _ico('<circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.6"/><rect x="7.2" y="7" width="1.6" height="5" fill="currentColor"/><circle cx="8" cy="4.9" r="1" fill="currentColor"/>', "Note"),
    "flag": _ico('<path d="M3 1.5v13" stroke="currentColor" stroke-width="1.6"/><path d="M3.8 2h9l-2.2 3.2 2.2 3.3h-9z" fill="currentColor"/>', "Red flag"),
    "say":  _ico('<path d="M2 2.5h12v8H7l-3.5 3v-3H2z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>', "Say"),
}

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
          {% for s in b.steps %}<li>{{ s|safe }}{% if loop.last and b.pod %}{% if medium == 'site' %}<a class="pod-mark" href="#pod-{{ b.pod }}" title="Differs from NZ or international guidance: see Points of difference">≠</a>{% else %}<span class="pod-mark" title="Differs from NZAS BPG">≠</span>{% endif %}{% endif %}</li>{% endfor %}
        </ol>
        {% if b.rule %}<div class="rule">{{ b.rule|safe }}</div>{% endif %}
        {% if b.example %}<p class="example">{{ b.example|safe }}</p>{% endif %}
        {% if b.stop %}<div class="callout stop" style="margin:6px 0 0 2.2em"><span class="lbl">{{ icon.stop }}Stop</span>{{ b.stop|safe }}</div>{% endif %}
      </section>
      {% endfor %}
{% endmacro %}
{% macro card(c, medium) %}
<article class="card" id="card-{{ c.id|lower }}">
  <header class="card-head">
    <div class="head-shape"><span class="card-id">{{ c.id }}</span>
    <h2 class="card-title">{{ c.title }}</h2></div>
    <div class="card-mode"><b>{{ 'Procedure' if c.mode == 'READ-DO' else 'Guide' }}</b>{{ 'Follow the steps in order' if c.mode == 'READ-DO' else 'Cover every point; order can vary' }}</div>
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
        {% if n.kind == 'stop' %}<div class="callout stop"><span class="lbl">{{ icon.stop }}Stop</span>{{ n.text|safe }}</div>
        {% elif n.kind == 'rule' %}<div class="callout rule-note"><span class="lbl">{{ icon.rule }}Rule</span>{{ n.text|safe }}</div>
        {% elif n.kind == 'flag' %}<div class="callout flag"><span class="lbl">{{ icon.flag }}Red flag</span>{{ n.text|safe }}</div>
        {% else %}<div class="callout note"><span class="lbl">{{ icon.note }}Note</span>{{ n.text|safe }}</div>{% endif %}
      {% endfor %}
      {% if c.script and medium == 'print' %}
      <div class="callout note"><span class="lbl">{{ icon.say }}Say</span>{% for s in c.script %}<br>{{ s }}{% endfor %}</div>
      {% endif %}
      
    </aside>
  </div>
  <footer class="card-foot">
    <div>
      {{ c.mod.title }} · Card {{ c.id }} · v{{ mod.version }} · {{ mod.date }} · from March 2026 checklist §{{ c.source }}{% if c.mod.standard %}<br>{{ c.mod.standard }}{% endif %}<br>
      {% if c.pods %}<span style="color:var(--pod)"><b>≠</b> Differs from NZ or international guidance. </span>{% endif %}
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
  <div id="navlist">
  {% for m in modules %}<h2>{{ m.title }}</h2>
  <ol>
  {% for c in m.cards %}<li data-k="{{ (c.id ~ ' ' ~ c.title ~ ' ' ~ m.title ~ ' ' ~ (c.blocks|map(attribute='title')|join(' ')))|lower }}"><a href="{{ up }}{{ c.dir }}/{{ c.id|lower }}.html"{% if cur and cur.id == c.id %} aria-current="page"{% endif %}><span>{{ c.id }}</span><span>{{ c.title }}</span></a></li>{% endfor %}
  </ol>{% endfor %}
  </div>
  <h2>For reviewers</h2>
  <ol><li><a href="{{ up }}review.html"{% if review %} aria-current="page"{% endif %}><span>Log</span><span>Errors and points of difference</span></a></li>
  <li><a href="{{ up }}print/cards.pdf"><span>PDF</span><span>Print cards</span></a></li>
  <li><a href="{{ up }}ptf-editing.html"><span>PTFs</span><span>How to add tips</span></a></li>
  <li><a href="{{ up }}review-copies.html"{% if owners %} aria-current="page"{% endif %}><span>Edit</span><span>Download a module to edit in Word</span></a></li></ol>
</details></nav>
<main id="main"><div class="measure">
{{ body }}
</div></main></div>
<script>
if(matchMedia('(max-width:900px)').matches){document.getElementById('navd').open=false}
const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();document.querySelectorAll('#navlist li').forEach(li=>{li.hidden=v&&!li.dataset.k.includes(v)})});
document.querySelectorAll('figure.stepper').forEach(f=>{
  const steps=JSON.parse(f.dataset.steps), n=steps.length, cap=f.querySelector('.stepcap'), play=f.querySelector('[data-act=play]');
  let k=n-1, timer=null;
  const show=i=>{k=Math.max(0,Math.min(n-1,i));
    f.querySelectorAll('[data-i]').forEach(e=>e.style.visibility=(+e.dataset.i<=k)?'visible':'hidden');
    f.querySelectorAll('.final').forEach(e=>e.style.visibility=(k>=n-1)?'visible':'hidden');
    cap.textContent='Step '+(k+1)+' of '+n+': '+steps[k];};
  const stop=()=>{clearInterval(timer);timer=null;play.textContent='Play';};
  const start=()=>{if(k>=n-1)show(0);play.textContent='Pause';timer=setInterval(()=>{if(k>=n-1){stop();return;}show(k+1);},1800);};
  f.querySelector('.stepctl').addEventListener('click',e=>{const a=e.target.dataset.act;if(!a)return;
    if(a==='play'){timer?stop():start();}
    else{stop(); if(a==='next')show(k+1); else if(a==='back')show(k-1); else {show(n-1);cap.textContent='All steps shown. Press Play to step through it.';}}});
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
    const io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting){io.disconnect();show(0);start();}}),{threshold:.5});io.observe(f);}
});
document.querySelectorAll('a.pod-mark').forEach(a=>a.addEventListener('click',()=>{const d=document.getElementById('layer-pod');if(d)d.open=true}));
</script>
</body></html>"""

T["page"] = r"""{% from 'card' import card with context %}
<p class="crumbs"><a href="../index.html#mod-{{ c.dir }}">{{ c.mod.title }}</a> / {{ c.id }}</p>
{{ card(c, 'site') }}
<p class="src" style="margin-top:6px">The box above is the print card, word for word. <a href="../print/{{ c.dir }}.pdf">Print this module</a> · <a href="../print/cards.pdf">Print all cards</a>.</p>

<details class="layer" open><summary>Why <span class="hint">the reason behind each block</span></summary><div class="layer-body">
{% for b in c.blocks if b.why %}<div class="why-item"><h4>{{ b.title }}</h4><p>{{ b.why|safe }}</p></div>{% endfor %}
{% if c.script %}<div class="why-item"><h4>What to say</h4><ul>{% for s in c.script %}<li>{{ s }}</li>{% endfor %}</ul></div>{% endif %}
</div></details>

{% if c.figures or c.media_planned %}
<details class="layer" open><summary>See it <span class="hint">diagrams, animations and video</span></summary><div class="layer-body">
{% for f in c.figures or [] %}{% if f in steps %}<figure id="fig-{{ f }}" class="stepper" data-steps='{{ steps[f]|tojson|forceescape }}'>{{ figs[f] }}<figcaption>{{ figt[f] }}</figcaption>
<p class="stepcap" aria-live="polite">Press Play to step through it.</p>
<div class="stepctl"><button type="button" data-act="play">Play</button><button type="button" data-act="back" aria-label="Previous step">Back</button><button type="button" data-act="next" aria-label="Next step">Next</button><button type="button" data-act="all">Show all</button></div></figure>
{% else %}<figure id="fig-{{ f }}">{{ figs[f] }}<figcaption>{{ figt[f] }}</figcaption></figure>{% endif %}{% endfor %}
{% if c.media_planned %}<p class="src">Media still to make:</p><ul class="planned">{% for m in c.media_planned %}<li>{{ m }}</li>{% endfor %}</ul>{% endif %}
</div></details>{% endif %}

{% if c.sim or c.demos %}<details class="layer" open><summary>Try it <span class="hint">{{ 'interactive demos and the simulator' if c.demos else 'practise in the simulator' }}</span></summary>
{% for d in c.demos or [] %}<div class="layer-body try">
<a class="btn" href="../{{ d.url }}">Open the {{ d.name }}</a><span>{{ d.label }}</span>
</div>{% endfor %}
{% if c.sim %}<div class="layer-body try">
<a class="btn" href="{{ c.sim.url }}" target="_blank" rel="noopener">Open the {{ c.sim.name }}</a><span>{{ c.sim.label }}</span>
</div>{% endif %}</details>{% endif %}

<details class="layer" open id="ptf"><summary>PTF tips <span class="hint">advice from our clinical teachers</span></summary><div class="layer-body">
<div class="ptf"><span class="who">From the Professional Teaching Fellows</span>
{% if c.ptf %}<ul>{% for t in c.ptf %}<li>{{ t.text|safe }}{% if t.who %} <span class="initials">{{ t.who }}</span>{% endif %}</li>{% endfor %}</ul>{% else %}<p>No tips yet for this protocol.</p>{% endif %}
<p class="ptf-edit"><a href="{{ c.ptf_edit }}" target="_blank" rel="noopener">Edit these tips</a> · <a href="../ptf-editing.html">How PTFs add tips</a></p></div>
</div></details>

{% if c.check %}<details class="layer"><summary>Check yourself <span class="hint">{{ c.check|length }} question{{ 's' if c.check|length > 1 }}</span></summary><div class="layer-body">
{% for x in c.check %}<div class="qa"><p><b>Q{{ loop.index }}.</b> {{ x.q|safe }}</p><details><summary>Show answer</summary><p>{{ x.a|safe }}</p></details></div>{% endfor %}
</div></details>{% endif %}

{% if c.pods %}<details class="layer" id="layer-pod"><summary>Points of difference <span class="hint">where NZ or international guidance differs</span></summary><div class="layer-body">
{% for k in c.pods %}{% set d = diffs[k] %}<div class="pod-box" id="pod-{{ k }}"><h4>≠ {{ d.title }}</h4><dl><dt>We teach</dt><dd>{{ d.ours }}</dd><dt>{{ d.label or 'Guideline' }}</dt><dd>{{ d.bpg }}</dd><dt>Why</dt><dd>{{ d.why }}</dd><dt>Status</dt><dd><span class="status">{{ d.status }}</span></dd></dl></div>{% endfor %}
</div></details>{% endif %}

{% if c.fixes %}<details class="layer"><summary>Changes from March 2026 <span class="hint">for reviewers</span></summary><div class="layer-body"><ul class="fixes">{% for f in c.fixes %}<li>{{ f }}</li>{% endfor %}</ul></div></details>{% endif %}

{% if c.refs %}<details class="layer"><summary>References</summary><div class="layer-body"><ul class="refs">{% for r in c.refs %}<li>{{ r }}</li>{% endfor %}</ul></div></details>{% endif %}

<nav class="pager" aria-label="Previous and next">
{% if prev %}<a href="../{{ prev.dir }}/{{ prev.id|lower }}.html">← {{ prev.id }} {{ prev.title }}</a>{% else %}<span></span>{% endif %}
{% if nxt %}<a href="../{{ nxt.dir }}/{{ nxt.id|lower }}.html">{{ nxt.id }} {{ nxt.title }} →</a>{% endif %}
</nav>
"""

T["home"] = r"""
<div class="hero-shape"><img class="hero-logo" src="assets/uoa-logo-reversed.png" alt="Waipapa Taumata Rau University of Auckland"><p>Master of Audiology</p><h1>Clinical Checklist</h1></div>
<p class="home-lead">Each protocol has a print card with the steps, and a teaching page that adds the reasons, diagrams, simulator practice and tips from our clinical teachers. The steps are the same in both.</p>
<div class="legend">
  <div class="callout stop"><span class="lbl">{{ icon.stop }}Stop</span>Safety concern or contraindication. Pause and decide whether, and how, to go on.</div>
  <div class="callout rule-note"><span class="lbl">{{ icon.rule }}Rule</span>A decision rule you apply every time.</div>
  <div class="callout note"><span class="lbl">{{ icon.note }}Note</span>Useful detail to know while you test.</div>
  <div class="pod-box" style="margin:0"><b style="color:var(--pod)">≠ Point of difference</b><br>We teach this differently from NZ (NZAS, UNHSEIP) or international (BSA, AAA) guidance.</div>
  <div class="ptf"><b>PTF tip</b><br>Advice from our Professional Teaching Fellows.</div>
</div>
{% for m in modules %}
<section class="module" id="mod-{{ m.id }}">
<h2>{{ m.title }}</h2>
{% if m.standard %}<p class="std">{{ m.standard }}</p>{% endif %}<p class="src">From the March 2026 checklist §{{ m.source }} · <a href="print/{{ m.id }}.pdf">Print this module</a> · <a href="edit/{{ m.id }}.docx">Edit in Word</a></p>
<ul class="cardlist">{% for c in m.cards %}<li><a href="{{ c.dir }}/{{ c.id|lower }}.html"><span class="cid">{{ c.id }}</span><span>{{ c.title }}</span><span class="mode">{{ 'Procedure' if c.mode == 'READ-DO' else 'Guide' }}</span></a></li>{% endfor %}</ul>
</section>
{% endfor %}
<p class="src" style="margin-top:20px">Not yet included: hearing aid fitting, diagnostic ABR and impression taking (possible later modules).</p>
"""

T["review"] = r"""
<h1 style="color:var(--brand)">Review log</h1>
<p>Everything this draft changed from the March 2026 checklist, and every place it differs from NZAS best practice guidelines. Reviewer for now: MS.</p>
<h2>Points of difference</h2>
<table class="reviewtbl"><thead><tr><th>Topic</th><th>We teach</th><th>Guideline</th><th>Status</th></tr></thead><tbody>
{% for k, d in diffs.items() %}<tr id="pod-{{ k }}"><td><b>{{ d.title }}</b>{% if d.cards %}<br><span class="src">{{ d.cards }}</span>{% endif %}</td><td>{{ d.ours }}</td><td>{{ d.bpg }}</td><td>{{ d.status }}</td></tr>{% endfor %}
</tbody></table>
<h2>Errors fixed and wording changes</h2>
<table class="reviewtbl"><thead><tr><th>Card</th><th>Change</th></tr></thead><tbody>
{% for c in cards %}{% for f in c.fixes or [] %}<tr><td><a href="{{ c.dir }}/{{ c.id|lower }}.html">{{ c.id }}</a></td><td>{{ f }}</td></tr>{% endfor %}{% endfor %}
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

T["owners"] = r"""
<h1 style="color:var(--brand)">Edit a module in Word</h1>
<p>Download a module, make your changes in Word, and send it back to MS. You do not need a GitHub account for this.</p>
<ol class="steps cont" style="max-width:68ch">
  <li>Download the Word file for the module you want to review.</li>
  <li>Turn on <b>Track Changes</b> (Review tab) before you edit, so MS can see what you changed.</li>
  <li>Edit any step, value or explanation directly, or add a comment.</li>
  <li>Add your advice for students under <b>Your PTF tips</b> at the end of each card. Put your initials after each tip if you would like credit.</li>
  <li>Email the file back to MS. Your changes are checked and added to the site and print cards.</li>
</ol>
<table class="reviewtbl" style="margin-top:16px"><thead><tr><th>Module</th><th>Cards</th><th>Download</th></tr></thead><tbody>
{% for m in modules %}<tr><td><a href="index.html#mod-{{ m.id }}"><b>{{ m.title }}</b></a></td><td>{{ m.cards|map(attribute='id')|join(', ') }}</td><td style="white-space:nowrap"><a href="edit/{{ m.id }}.docx">Word</a> · <a href="edit/{{ m.id }}.md">Markdown</a></td></tr>{% endfor %}
<tr><td><b>Everything</b></td><td>All {{ cards|length }} cards</td><td style="white-space:nowrap"><a href="edit/all.docx">Word</a> · <a href="edit/all.md">Markdown</a></td></tr>
</tbody></table>
<p class="src" style="margin-top:10px">The files are made fresh from the site every time it is updated, so always download a new copy before you start.</p>
"""

T["print"] = r"""{% from 'card' import card with context %}<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><title>MAud Clinical Checklist · {{ ptitle }} · print cards</title>
<link rel="stylesheet" href="../assets/style.css"></head>
<body class="print">
<section class="cover">
  <div class="cover-shape">
    <img class="cover-logo" src="../assets/uoa-logo-reversed.png" alt="Waipapa Taumata Rau University of Auckland">
    <p style="font-weight:500;font-size:11pt;margin:0;opacity:.9">Master of Audiology</p>
    <h1 style="font-size:30pt;margin:5mm 0 2mm">Clinical Checklist</h1>
    <p style="font-size:16pt;margin:0;font-weight:500">{{ ptitle }}</p>
    <p style="font-size:9pt;margin:4mm 0 0;opacity:.85">Print cards · version {{ mod.version }} · {{ mod.date }}</p>
  </div>
  <div>
    <h2 style="color:var(--brand);font-size:13pt">How to use these cards</h2>
    <p style="max-width:150mm">One protocol per page. <b>Procedure</b> cards are followed in order. <b>Guide</b> cards list every point to cover, in an order that suits the patient. Scan the QR code on any card for the reasons, diagrams and simulator practice.</p>
    <div class="legend" style="max-width:170mm">
      <div class="callout stop"><span class="lbl">{{ icon.stop }}Stop</span>Safety concern or contraindication: pause and decide.</div>
      <div class="callout rule-note"><span class="lbl">{{ icon.rule }}Rule</span>Decision rule.</div>
      <div class="callout note"><span class="lbl">{{ icon.note }}Note</span>Useful detail while you test.</div>
      <div class="callout" style="border-left-color:var(--pod);background:var(--pod-wash)"><span class="lbl" style="color:var(--pod)">≠</span>Differs from NZ or international guidance; see teaching page.</div>
    </div>
    {% if pcards|length > 14 %}<ol style="columns:3;font-size:8pt;padding:0;margin-top:4mm">{% for m in modules %}<li style="list-style:none;break-inside:avoid;margin-bottom:2mm"><b style="color:var(--brand)">{{ m.title }}</b><br>{{ m.cards|map(attribute='id')|join(', ') }}</li>{% endfor %}</ol>
    {% else %}<ol style="columns:2;font-size:9pt;padding:0;margin-top:6mm">{% for c in pcards %}<li style="list-style:none;break-inside:avoid"><b style="color:var(--brand)">{{ c.id }}</b> {{ c.title }}</li>{% endfor %}</ol>{% endif %}
  </div>
  <div class="cover-foot"><p style="font-size:6.5pt;color:var(--muted);max-width:110mm;margin:0">DRAFT for review, built from the Clinical Checklist March 2026. Not yet approved for clinical teaching. © Section of Audiology, The University of Auckland.</p><svg class="unaunahi" viewBox="0 0 300 150" aria-hidden="true"><circle cx="150" cy="190" r="150" fill="#cecedb"/><circle cx="150" cy="210" r="130" fill="#6d6d91"/><circle cx="150" cy="230" r="110" fill="var(--brand)"/></svg></div>
</section>
{% for c in pcards %}{{ card(c, 'print') }}
{% for f in c.figures or [] %}{% if f in print_figs and f != 'symbols' %}
<article class="card flowpage"><header class="card-head"><div class="head-shape"><span class="card-id">{{ c.id }}</span><h2 class="card-title">{{ figt[f] }}: decision flow</h2></div><div class="card-mode"><b>Back of card</b>Same rules as the front</div></header>
<div class="fig-wrap">{{ figs[f] }}</div>
<footer class="card-foot"><div>{{ c.mod.title }} · Card {{ c.id }} (flowchart) · v{{ mod.version }} · {{ mod.date }}</div></footer></article>
{% endif %}{% endfor %}{% endfor %}
</body></html>"""

env = Environment(loader=DictLoader(T), autoescape=select_autoescape(default=False))
for m in modules:
    m["pod_count"] = len({k for c in m["cards"] for k in c["pods"]})
# Step-through animations are off (steps={}); captions stay in F.STEPS for later use.
common = dict(steps={}, icon=ICON, mod=mod, modules=modules, cards=cards, diffs=diffs, figs=FIGS, figt=FIGT, animated=F.ANIMATED, print_figs=F.PRINT_FIGS)

if SITE.exists(): shutil.rmtree(SITE)
SITE.mkdir()
for m in modules: (SITE / m["id"]).mkdir()
(SITE / "print").mkdir()
shutil.copytree(ROOT / "assets", SITE / "assets")
shutil.copytree(ROOT / "fonts", SITE / "assets/fonts")
(SITE / ".nojekyll").write_text("")

def shell(body, title, desc, up, cur=None, review=False, owners=False):
    return env.get_template("shell").render(body=Markup(body), title=title, desc=desc, up=up, cur=cur, review=review, owners=owners, **common)

(SITE / "index.html").write_text(shell(env.get_template("home").render(**common), "Clinical Checklist", "MAud clinical protocols: print cards and teaching pages.", ""))
(SITE / "ptf-editing.html").write_text(shell(env.get_template("ptfhelp").render(**common), "How PTFs add tips", "How Professional Teaching Fellows edit PTF tips.", ""))
(SITE / "review.html").write_text(shell(env.get_template("review").render(**common), "Review log", "Errors fixed and points of difference.", "", review=True))
(SITE / "review-copies.html").write_text(shell(env.get_template("owners").render(**common), "Edit a module in Word", "Download a module to edit in Word.", "", owners=True))
for i, c in enumerate(cards):
    body = env.get_template("page").render(c=c, prev=cards[i-1] if i else None, nxt=cards[i+1] if i+1 < len(cards) else None, **common)
    (SITE / c["dir"] / page_name(c)).write_text(shell(body, f"{c['id']} {c['title']}", c["purpose"], "../", cur=c))

# PTF tip files: create an empty one for any card that has none, so "Edit these tips" always works
for c in cards:
    f = ROOT / "content/ptf" / (c["id"].lower() + ".md")
    if not f.exists():
        f.write_text(f"""# PTF tips: {c['id']} {c['title']}

<!--
How to edit (no coding needed):
- One tip per line, starting with a dash and a space: "- ".
- Keep each tip to one or two short sentences, in your own voice.
- Add your initials in brackets at the end if you want credit, e.g. (AS).
- Lines that do not start with "- " are ignored, so this note is safe to leave.
-->
""", encoding="utf-8")

PRINT.mkdir(exist_ok=True)
(SITE / "print" / "cards.html").write_text(env.get_template("print").render(pcards=cards, ptitle="All protocols", **common))
for m in modules:
    (SITE / "print" / f"{m['id']}.html").write_text(env.get_template("print").render(pcards=m["cards"], ptitle=m["title"], **common))
print("built", len(modules), "modules,", len(cards), "cards")

# ---------- Review copies for PTFs: Markdown + Word, one per module and one for everything
import subprocess
def md_text(s):
    s = str(s)
    s = re.sub(r"<sub>(.*?)</sub>", lambda m: "~" + m.group(1).replace(" ", "\\ ") + "~", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)

def md_table(v):
    head = [md_text(h) for h in v["header"]]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in v["rows"]:
        out.append("| " + " | ".join(md_text(x) for x in r) + " |")
    return "\n".join(out)

def module_md(mods, title):
    L = [f"---\ntitle: \"MAud Clinical Checklist: {title}\"\nsubtitle: \"Review copy for PTFs, version {SITEINFO['version']} ({SITEINFO['date']})\"\n---\n",
         "**How to review:** turn on Track Changes, then edit any wording, step or value directly. "
         "Add advice for students under *Your PTF tips* at the end of each card, with your initials if you would like credit. "
         "Email the file back to MS.\n"]
    for m in mods:
        L.append(f"# {m['title']}\n")
        for c in m["cards"]:
            mode = "Procedure" if c["mode"] == "READ-DO" else "Guide"
            L.append(f"## {c['id']} {md_text(c['title'])}\n")
            L.append(f"*{mode}. From March 2026 checklist section {c['source']}.*\n")
            L.append(f"**Purpose:** {md_text(c['purpose'])}\n")
            if c.get("when"):
                L.append("**When:**\n\n" + "\n".join(f"- {md_text(w)}" for w in c["when"]) + "\n")
            for b in c["blocks"]:
                L.append(f"### {md_text(b['title'])}\n")
                L.append("\n".join(f"{i}. {md_text(s)}" for i, s in enumerate(b["steps"], 1)) + "\n")
                if b.get("rule"): L.append(f"**Rule:** {md_text(b['rule']).strip()}\n")
                if b.get("example"): L.append(f"**Example:** {md_text(b['example'])}\n")
                if b.get("stop"): L.append(f"**Stop:** {md_text(b['stop'])}\n")
                if b.get("why"): L.append(f"**Why:** {md_text(b['why'])}\n")
                for pk in b.get("podlist") or []:
                    d = diffs[pk]
                    L.append(f"**Point of difference ({md_text(d['title'])}):** We teach: {md_text(d['ours'])} Guideline: {md_text(d['bpg'])} Status: {md_text(d['status'])}\n")
            for v in c.get("values") or []:
                L.append(f"**{md_text(v['caption'])}** (source: {md_text(v['source'])})\n\n" + md_table(v) + "\n")
                if v.get("note"): L.append(f"*{md_text(v['note'])}*\n")
            if c.get("notes"):
                lab = {"stop": "Stop", "rule": "Rule", "flag": "Red flag"}
                L.append("**Notes:**\n\n" + "\n".join(f"- *{lab.get(n['kind'], 'Note')}:* {md_text(n['text'])}" for n in c["notes"]) + "\n")
            if c.get("script"):
                L.append("**What to say:**\n\n" + "\n".join(f"- {md_text(s)}" for s in c["script"]) + "\n")
            if c["ptf"]:
                L.append("**Current PTF tips:**\n\n" + "\n".join(f"- {md_text(t['text'])}" + (f" ({t['who']})" if t["who"] else "") for t in c["ptf"]) + "\n")
            L.append("**Your PTF tips:**\n\n- \n\n**Other comments on this card:**\n\n- \n")
            L.append("\\newpage\n" if False else "")
    return "\n".join(L)

EDIT = SITE / "edit"
EDIT.mkdir()
ref = ROOT / "assets" / "reference.docx"
jobs = [(m["id"], [m], m["title"]) for m in modules] + [("all", modules, "All modules")]
for name, mods, title in jobs:
    md = EDIT / f"{name}.md"
    md.write_text(module_md(mods, title), encoding="utf-8")
    cmd = ["pandoc", str(md), "-o", str(EDIT / f"{name}.docx")]
    if ref.exists(): cmd += ["--reference-doc", str(ref)]
    subprocess.run(cmd, check=True)
print("review copies:", len(jobs))
