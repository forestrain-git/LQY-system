import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(2000);

  // Get all el-select elements and their HTML
  const selectInfo = await page.evaluate(() => {
    const selects = document.querySelectorAll('.el-select');
    return Array.from(selects).map((select, index) => {
      const wrapper = select.querySelector('.el-select__wrapper');
      const inputWrapper = select.querySelector('.el-input__wrapper');
      const firstChild = select.firstElementChild;

      return {
        index,
        className: select.className,
        firstChildClass: firstChild?.className || 'none',
        firstChildTag: firstChild?.tagName || 'none',
        hasWrapper: !!wrapper,
        hasInputWrapper: !!inputWrapper,
        wrapperClasses: wrapper?.className || 'N/A',
        inputWrapperClasses: inputWrapper?.className || 'N/A'
      };
    });
  });

  console.log('Select elements:', JSON.stringify(selectInfo, null, 2));

  // Get computed style of the wrapper
  const wrapperStyle = await page.evaluate(() => {
    const select = document.querySelector('.el-select');
    if (select) {
      const wrapper = select.querySelector('.el-select__wrapper') || select.firstElementChild;
      if (wrapper) {
        const style = window.getComputedStyle(wrapper);
        return {
          tag: wrapper.tagName,
          class: wrapper.className,
          backgroundColor: style.backgroundColor,
          background: style.background,
          boxShadow: style.boxShadow
        };
      }
    }
    return null;
  });

  console.log('Wrapper style:', wrapperStyle);

  await browser.close();
})();
