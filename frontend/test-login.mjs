import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();
  
  console.log('Testing login with demo mode...');
  
  // Go to login
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  
  // Fill in credentials
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'admin123');
  
  // Click login
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);
  
  // Check if we're on dashboard
  const url = page.url();
  console.log('Current URL:', url);
  
  if (url.includes('/login')) {
    console.log('❌ Login failed - still on login page');
    await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/login-failed.png' });
  } else {
    console.log('✅ Login successful - redirected to:', url);
    await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/dashboard-after-login.png', fullPage: false, clip: { x: 0, y: 0, width: 1440, height: 900 } });
  }
  
  await browser.close();
})();
