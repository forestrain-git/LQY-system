import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();
  
  console.log('Taking screenshots of themed application...');
  
  // 1. Login Page
  console.log('1. Capturing login page...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ 
    path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/1-login-high-contrast.png', 
    fullPage: true 
  });
  
  // Login with credentials
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  
  // 2. Dashboard
  console.log('2. Capturing dashboard...');
  await page.screenshot({ 
    path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/2-dashboard-high-contrast.png', 
    fullPage: true 
  });
  
  // 3. Device Management
  console.log('3. Capturing device management...');
  const deviceMenu = await page.locator('.el-menu-item:has-text("设备管理")');
  if (await deviceMenu.isVisible().catch(() => false)) {
    await deviceMenu.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/3-devices-high-contrast.png', 
      fullPage: true 
    });
  }
  
  // 4. AI Assistant
  console.log('4. Capturing AI assistant...');
  const aiMenu = await page.locator('.el-menu-item:has-text("AI助手")');
  if (await aiMenu.isVisible().catch(() => false)) {
    await aiMenu.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/4-ai-assistant-high-contrast.png', 
      fullPage: true 
    });
  }
  
  // 5. Safety Management
  console.log('5. Capturing safety management...');
  const safetyMenu = await page.locator('.el-menu-item:has-text("安全管控")');
  if (await safetyMenu.isVisible().catch(() => false)) {
    await safetyMenu.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/5-safety-high-contrast.png', 
      fullPage: true 
    });
  }
  
  console.log('All screenshots saved with high-contrast theme!');
  await browser.close();
})();
