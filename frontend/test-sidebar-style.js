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

  // Check computed style of sidebar
  const sidebarStyle = await page.evaluate(() => {
    const sidebar = document.querySelector('.el-aside');
    if (sidebar) {
      const computed = window.getComputedStyle(sidebar);
      return {
        backgroundColor: computed.backgroundColor,
        background: computed.background,
        className: sidebar.className,
        inlineStyle: sidebar.getAttribute('style')
      };
    }
    return null;
  });

  console.log('Sidebar computed style:', sidebarStyle);

  await browser.close();
})();
