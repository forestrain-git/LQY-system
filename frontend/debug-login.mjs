import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Capture console logs
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  
  console.log('Filling username...');
  await page.fill('input[type="text"]', 'admin');
  
  console.log('Filling password...');
  await page.fill('input[type="password"]', 'admin123');
  
  console.log('Clicking login button...');
  await page.click('button[type="submit"]');
  
  await page.waitForTimeout(3000);
  
  // Check for error message
  const errorVisible = await page.locator('.error-message').isVisible().catch(() => false);
  console.log('Error visible:', errorVisible);
  
  if (errorVisible) {
    const errorText = await page.locator('.error-message').textContent();
    console.log('Error message:', errorText);
  }
  
  // Check current URL
  console.log('Current URL:', page.url());
  
  await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/login-debug.png' });
  console.log('Screenshot saved');
  
  await browser.close();
})();
