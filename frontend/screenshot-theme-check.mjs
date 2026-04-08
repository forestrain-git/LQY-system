import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Get computed styles
  const styles = await page.evaluate(() => {
    const body = document.body;
    const computed = window.getComputedStyle(body);
    return {
      backgroundColor: computed.backgroundColor,
      color: computed.color
    };
  });
  
  console.log('Current styles:', styles);
  
  // Also get CSS variables
  const vars = await page.evaluate(() => {
    const root = document.documentElement;
    const computed = window.getComputedStyle(root);
    return {
      bgBase: computed.getPropertyValue('--bg-base').trim(),
      bgElevated: computed.getPropertyValue('--bg-elevated').trim(),
      textPrimary: computed.getPropertyValue('--text-primary').trim(),
      colorPrimary: computed.getPropertyValue('--color-primary').trim()
    };
  });
  
  console.log('CSS Variables:', vars);
  
  await browser.close();
})();
