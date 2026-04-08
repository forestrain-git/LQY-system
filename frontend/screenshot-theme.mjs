import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('Navigating to login page...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle', timeout: 60000 });
  
  // Wait for the login form to be visible
  await page.waitForSelector('.login-form, form, input', { timeout: 10000 });
  
  console.log('Taking screenshot of login page...');
  await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/1-login-theme.png', fullPage: true });
  
  // Try to login
  try {
    const usernameInput = await page.locator('input[type="text"], input[name="username"], input[placeholder*="用户名"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"]').first();
    const submitButton = await page.locator('button[type="submit"], button:has-text("登录"), .el-button--primary').first();
    
    if (await usernameInput.isVisible() && await passwordInput.isVisible()) {
      await usernameInput.fill('admin');
      await passwordInput.fill('admin123');
      await submitButton.click();
      
      console.log('Waiting for dashboard...');
      await page.waitForTimeout(3000);
      
      console.log('Taking screenshot of dashboard...');
      await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/2-dashboard-theme.png', fullPage: true });
      
      // Navigate to AI Assistant
      const aiMenu = await page.locator('.el-menu-item:has-text("AI助手"), a:has-text("AI助手"), [data-route*="ai"]').first();
      if (await aiMenu.isVisible()) {
        await aiMenu.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/3-ai-assistant-theme.png', fullPage: true });
      }
    }
  } catch (e) {
    console.log('Could not complete login:', e.message);
  }
  
  console.log('Screenshots saved!');
  await browser.close();
})();
