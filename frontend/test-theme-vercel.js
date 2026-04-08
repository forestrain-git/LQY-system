import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(2000);

  // Click on theme switcher to open dropdown
  await page.click('.theme-preview');
  await page.waitForTimeout(500);

  // Click on Vercel theme (light)
  await page.click('text=Vercel');
  await page.waitForTimeout(1000);

  const screenshotPath = '/mnt/c/users/administrator/projects/lqy-system/f-cutpictures/theme-vercel.png';
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.log('Vercel theme screenshot saved:', screenshotPath);

  await browser.close();
})();
