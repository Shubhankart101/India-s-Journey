const { chromium } = require('../frontend/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('=== TESTING EMPIRES PAGE ===');
  await page.goto('http://localhost:8080/#/explore/empires-of-ancient-india/empires-of-ancient-india-atlas', { waitUntil: 'networkidle' });
  
  const empireTabs = await page.$$eval('.empires-timeline-strip button', btns => btns.map(b => b.textContent.trim().replace(/\s+/g, ' ')));
  console.log('Empire chips:', empireTabs);

  const historyTab = await page.$('.dossier-tab-btn:has-text("History & Quotes")');
  console.log('History tab button exists:', !!historyTab);
  if (historyTab) {
    await historyTab.click();
    await page.waitForTimeout(400);
    const content = await page.innerText('.dossier-tab-content');
    console.log('Dossier history sample:\n', content.slice(0, 300));
  }

  const articleSections = await page.$$('.subgroup-article-section');
  console.log('Article sections below map count on Empires:', articleSections.length);

  // Test clicking Kushan Empire chip in timeline strip
  const kushanBtn = await page.$('.timeline-chip:has-text("Kushan Empire")');
  if (kushanBtn) {
    console.log('Clicking Kushan Empire timeline chip...');
    await kushanBtn.click();
    await page.waitForTimeout(500);
    const firstSectionHeading = await page.innerText('.subgroup-article-section h2');
    console.log('First article section heading after Kushan click:', firstSectionHeading);
  }

  console.log('\n=== TESTING IVC PAGE ===');
  await page.goto('http://localhost:8080/#/explore/indus-valley-civilisation/the-indus-valley-civilisation-comprehensive-excavation-map', { waitUntil: 'networkidle' });

  const periodPills = await page.$$eval('.indus-periods-strip button', btns => btns.map(b => b.textContent.trim().replace(/\s+/g, ' ')));
  console.log('Period pills:', periodPills);

  const earlyBtn = await page.$('.ips-pill:has-text("Early Harappan")');
  if (earlyBtn) {
    await earlyBtn.click();
    await page.waitForTimeout(400);
    const dossierText = await page.innerText('.indus-site-dossier');
    console.log('IVC dossier after Early Harappan click:\n', dossierText.slice(0, 300));
  }

  const decoderPresent = await page.$('.indus-decoder-container');
  console.log('Decoder component (.indus-decoder-container) rendered on IVC page:', !!decoderPresent);

  const ivcArticleSections = await page.$$('.subgroup-article-section');
  console.log('Article sections below map count on IVC:', ivcArticleSections.length);

  await browser.close();
})();
