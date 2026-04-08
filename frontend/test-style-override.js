import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(2000);

  // Get the data-v attribute from alert-list element
  const alertListInfo = await page.evaluate(() => {
    const alertList = document.querySelector('.alert-list');
    if (alertList) {
      const attrs = Array.from(alertList.attributes);
      const dataVAttr = attrs.find(a => a.name.startsWith('data-v-'));
      return {
        tag: alertList.tagName,
        class: alertList.className,
        dataV: dataVAttr ? dataVAttr.name : 'Not found'
      };
    }
    return null;
  });

  console.log('Alert list info:', alertListInfo);

  // Check if our styles are being applied
  const appliedStyles = await page.evaluate(() => {
    const select = document.querySelector('.el-select');
    if (select) {
      const wrapper = select.querySelector('.el-select__wrapper');
      if (wrapper) {
        const computed = window.getComputedStyle(wrapper);

        // Get all stylesheets and rules
        let foundRule = null;
        for (const sheet of document.styleSheets) {
          try {
            for (const rule of sheet.cssRules || sheet.rules) {
              if (rule.cssText && rule.cssText.includes('el-select__wrapper')) {
                foundRule = rule.cssText;
                break;
              }
            }
          } catch (e) {}
          if (foundRule) break;
        }

        return {
          computedBackground: computed.backgroundColor,
          foundRule: foundRule || 'Not found in stylesheets'
        };
      }
    }
    return null;
  });

  console.log('Applied styles:', appliedStyles);

  await browser.close();
})();
