import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(2000);

  // Check if our styles are in the document
  const styleInfo = await page.evaluate(() => {
    const styles = document.querySelectorAll('style');
    const ourStyle = Array.from(styles).find(s => s.textContent.includes('el-select__wrapper'));
    return {
      totalStyles: styles.length,
      hasOurStyle: !!ourStyle,
      ourStyleContent: ourStyle ? ourStyle.textContent.substring(0, 500) : 'Not found'
    };
  });

  console.log('Style info:', styleInfo);

  // Try force applying style
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
      .el-select__wrapper {
        background-color: #21262d !important;
        box-shadow: 0 0 0 1px #30363d inset !important;
      }
    `;
    document.head.appendChild(style);
  });

  await page.waitForTimeout(500);

  // Check style after force apply
  const newStyle = await page.evaluate(() => {
    const select = document.querySelector('.el-select');
    if (select) {
      const wrapper = select.querySelector('.el-select__wrapper');
      if (wrapper) {
        const style = window.getComputedStyle(wrapper);
        return {
          backgroundColor: style.backgroundColor
        };
      }
    }
    return null;
  });

  console.log('After force apply:', newStyle);

  await browser.close();
})();
