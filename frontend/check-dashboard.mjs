import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();
  
  // Inject auth token to bypass login
  await page.goto('http://localhost:5173/login');
  await page.evaluate(() => {
    localStorage.setItem('auth-token', 'mock-token-for-testing');
  });
  
  // Navigate to dashboard
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  await page.screenshot({ 
    path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/dashboard-themed.png', 
    fullPage: false,
    clip: { x: 0, y: 0, width: 1440, height: 900 }
  });
  
  console.log('Dashboard screenshot saved!');
  await browser.close();
})();
