# MAud Clinical Checklist — pilot build (v0.1 draft)

One source, two outputs:

- `content/pta-masking.yaml` — the single source for all cards (steps, why, PTF tips, check-yourself, points of difference, fixes)
- `figures.py` — house-style SVG diagrams (flowcharts, masking function, threshold staircase, symbols, insert depth)
- `assets/style.css` — design tokens and styles shared by the site and the print cards
- `build.py` — builds `site/` (GitHub Pages) and `site/print/cards.html`
- `pdf.js` — renders `site/print/cards.pdf` (A4, one card per page) with Playwright/Chromium

## Build

    pip install pyyaml jinja2 qrcode
    python3 build.py
    node pdf.js        # needs: npm i playwright

## Publish

Push the contents of `site/` to a GitHub repo (planned: jakalnz/maud-checklist) and enable Pages.
All internal links are relative, so the site can move to a dedicated MAud account later.
Only `BASE_URL` in build.py (used for the QR codes) needs changing.

## Status

Built from Clinical Checklist March 2026 sections 4–5 only. See `site/review.html` for every change and point of difference awaiting MS sign-off.
Colours: UoA brand palette — Waitematā #0c0c48 (primary), Azure #1f2bd4, Māhina #00caef (decorative only).
Font: Inter, the UoA brand typeface (subset to woff2 from the UoA-supplied OTFs). Print scale: headers Bold 14pt, intro Medium 11pt, subheads Bold 11pt, body Regular 9pt, footer Regular 6.5pt.
