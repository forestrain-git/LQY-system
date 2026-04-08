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

  // Get DOM structure of sidebar
  const domInfo = await page.evaluate(() => {
    const sidebar = document.querySelector('.el-aside.sidebar');
    if (sidebar) {
      return {
        tagName: sidebar.tagName,
        className: sidebar.className,
        childCount: sidebar.children.length,
        firstChild: {
          tagName: sidebar.children[0]?.tagName,
          className: sidebar.children[0]?.className,
          style: sidebar.children[0]?.getAttribute('style')
        }
      };
    }
    return null;
  });

  console.log('Sidebar DOM:', domInfo);

  await browser.close();
})();
