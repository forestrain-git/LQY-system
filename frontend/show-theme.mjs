import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('Taking final theme verification screenshot...');
  
  // Go to login
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Login
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  
  // Full dashboard screenshot
  await page.screenshot({ 
    path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/theme-final-result.png', 
    fullPage: false,
    clip: { x: 0, y: 0, width: 1440, height: 900 }
  });
  
  console.log('Final screenshot saved: theme-final-result.png');
  await browser.close();
})();
