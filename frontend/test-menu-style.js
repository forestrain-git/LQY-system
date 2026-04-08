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
  await page.waitForTimeout(1000);

  // Check el-menu computed style
  const menuStyle = await page.evaluate(() => {
    const menu = document.querySelector('.el-menu');
    if (menu) {
      const computed = window.getComputedStyle(menu);
      return {
        backgroundColor: computed.backgroundColor,
        className: menu.className
      };
    }
    return null;
  });

  console.log('Menu computed style:', menuStyle);

  await browser.close();
})();
