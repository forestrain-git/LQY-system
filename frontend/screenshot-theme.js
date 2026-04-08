const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/theme-verification.png', fullPage: true });
  
  console.log('Screenshot saved to theme-verification.png');
  
  await browser.close();
})();
