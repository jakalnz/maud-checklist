const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();
for (const rm of ['no-preference','reduce']) {
const p=await b.newPage({viewport:{width:1280,height:900}, reducedMotion: rm});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+process.cwd()+'/site/pta/pta-05.html');
const fig=p.locator('#fig-hughson-westlake'); await fig.scrollIntoViewIfNeeded(); await p.waitForTimeout(2500);
const vis=()=>fig.evaluate(e=>[[...e.querySelectorAll('circle[data-i]')].filter(c=>c.style.visibility!=='hidden').length, e.querySelector('.stepcap').textContent]);
console.log(rm,'auto',JSON.stringify(await vis()));
await fig.locator('[data-act=back]').click(); console.log(rm,'back',JSON.stringify(await vis()));
await fig.locator('[data-act=all]').click(); console.log(rm,'all',JSON.stringify(await vis()));
if(rm==='reduce'){await fig.locator('[data-act=play]').click(); await p.waitForTimeout(2000); console.log(rm,'play',JSON.stringify(await vis())); await fig.screenshot({path:'/tmp/hw.png'});}
}
await b.close()})()
