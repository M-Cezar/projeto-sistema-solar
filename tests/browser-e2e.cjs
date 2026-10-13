const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const width of [320, 375, 768, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 720 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      const response = await page.goto('http://127.0.0.1:4173/', {waitUntil:'load'});
      assert.equal(response.status(), 200);
      assert.equal(await page.locator('.sun').count(), 1);
      assert.equal(await page.locator('.earth').count(), 1);
      assert.equal(await page.locator('.moon').count(), 1);
      const result = await page.locator('.container').evaluate(el => {
        const rect = el.getBoundingClientRect();
        const earth = getComputedStyle(document.querySelector('.earth'));
        const moon = getComputedStyle(document.querySelector('.moon'));
        return {left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom,
          viewportWidth: window.innerWidth, viewportHeight: window.innerHeight,
          earthAnimation: earth.animationName, moonAnimation: moon.animationName};
      });
      assert.ok(result.left >= -1 && result.right <= result.viewportWidth + 1,
        'Horizontal overflow at ' + width + ': ' + JSON.stringify(result));
      assert.ok(result.top >= -1 && result.bottom <= result.viewportHeight + 1,
        'Vertical overflow at ' + width + ': ' + JSON.stringify(result));
      assert.equal(result.earthAnimation, 'orbit');
      assert.equal(result.moonAnimation, 'orbit');
      assert.deepEqual(errors, []);
      await context.close();
    }
    const reduced = await browser.newContext({reducedMotion:'reduce'});
    const page = await reduced.newPage();
    await page.goto('http://127.0.0.1:4173/');
    assert.equal(await page.locator('.earth').evaluate(el=>getComputedStyle(el).animationName),'none');
    assert.equal(await page.locator('.moon').evaluate(el=>getComputedStyle(el).animationName),'none');
    await reduced.close();
    console.log('Solar browser acceptance PASS: 4 viewports, live orbit animations, reduced motion');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
