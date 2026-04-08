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

  // Check all child elements of sidebar
  const childElements = await page.evaluate(() => {
    const sidebar = document.querySelector('.el-aside');
    if (sidebar) {
      const children = sidebar.querySelectorAll('*');
      return Array.from(children).slice(0, 5).map(child => {
        const computed = window.getComputedStyle(child);
        return {
          tagName: child.tagName,
          className: child.className,
          backgroundColor: computed.backgroundColor,
          width: computed.width,
          height: computed.height
        };
      });
    }
    return null;
  });

  console.log('Child elements:', JSON.stringify(childElements, null, 2));

  await browser.close();
})();
