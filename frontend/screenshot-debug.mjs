import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();
  
  // Capture console logs
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  console.log('Navigating to http://localhost:5173/login');
  
  try {
    await page.goto('http://localhost:5173/login', { 
      waitUntil: 'domcontentloaded', 
      timeout: 30000 
    });
    
    console.log('Page loaded, waiting 5 seconds...');
    await page.waitForTimeout(5000);
    
    // Get page content
    const content = await page.content();
    console.log('Page content length:', content.length);
    console.log('Page title:', await page.title());
    
    // Screenshot whatever is there
    await page.screenshot({ path: '/mnt/c/users/administrator/projects/lqy-system/F-cutPictures/debug-page.png', fullPage: true });
    console.log('Screenshot saved to debug-page.png');
    
    // Try to find login elements
    const bodyText = await page.locator('body').textContent();
    console.log('Body text preview:', bodyText.substring(0, 200));
    
  } catch (e) {
    console.error('Error:', e.message);
  }
  
  await browser.close();
})();
