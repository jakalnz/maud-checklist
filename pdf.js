// Renders every print/*.html page in site/ to a matching A4 PDF.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.join(process.cwd(), 'site', 'print');
  const b = await chromium.launch(); const p = await b.newPage();
  await p.emulateMedia({ media: 'print' });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) {
    await p.goto('file://' + path.join(dir, f), { waitUntil: 'networkidle' });
    await p.pdf({ path: path.join(dir, f.replace(/\.html$/, '.pdf')), preferCSSPageSize: true, printBackground: true });
  }
  await b.close();
})();
