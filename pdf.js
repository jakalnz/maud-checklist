const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/site/print/cards.html', { waitUntil: 'networkidle' });
  await p.emulateMedia({ media: 'print' }); await p.pdf({ path: 'site/print/cards.pdf', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
