import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(2000);

  // Switch to mint theme
  await page.click('.theme-preview');
  await page.waitForTimeout(500);
  await page.click('text=薄荷晨露');
  await page.waitForTimeout(1500);

  // Verify CSS variables
  const cssVars = await page.evaluate(() => {
    const root = getComputedStyle(document.documentElement);
    return {
      bgSidebar: root.getPropertyValue('--bg-sidebar').trim(),
      bgPrimary: root.getPropertyValue('--bg-primary').trim(),
      textPrimary: root.getPropertyValue('--text-primary').trim()
    };
  });

  console.log('CSS Variables:', cssVars);

  // Take screenshot
  const screenshotPath = '/mnt/c/users/administrator/projects/lqy-system/f-cutpictures/verify-mint.png';
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log('Full screenshot saved:', screenshotPath);

  await browser.close();
})();
