import { chromium } from 'playwright';

const themes = ['midnight', 'mint', 'purple', 'sunset', 'cyber'];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const theme of themes) {
    await page.goto('http://localhost:5173/alerts', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    await page.waitForTimeout(1500);

    // Click on theme switcher to open dropdown
    await page.click('.theme-preview');
    await page.waitForTimeout(500);

    // Click on the theme
    await page.click(`text=${theme === 'midnight' ? '午夜深海' : theme === 'mint' ? '薄荷晨露' : theme === 'purple' ? '紫霞秘境' : theme === 'sunset' ? '暖阳橙光' : '赛博霓虹'}`);
    await page.waitForTimeout(1000);

    const screenshotPath = `/mnt/c/users/administrator/projects/lqy-system/f-cutpictures/theme-${theme}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`${theme} theme screenshot saved:`, screenshotPath);
  }

  await browser.close();
})();
