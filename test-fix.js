const { chromium } = require('playwright');

(async () => {
  console.log('Starting browser...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  try {
    console.log('Navigating to http://localhost:8080...');
    await page.goto('http://localhost:8080', { timeout: 30000, waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    const content = await page.content();
    console.log('\n=== PAGE INFO ===');
    console.log('Page HTML length:', content.length);
    console.log('Page title:', await page.title());
    
    // Check if #app has any children
    const appInfo = await page.evaluate(() => {
      const app = document.getElementById('app');
      return {
        found: !!app,
        childrenCount: app ? app.children.length : 0,
        innerText: app ? app.innerText.substring(0, 200) : 'N/A'
      };
    });
    console.log('\n=== APP ELEMENT ===');
    console.log('#app found:', appInfo.found);
    console.log('#app children count:', appInfo.childrenCount);
    console.log('#app innerText preview:', appInfo.innerText);
    
    // Check for errors
    const errors = await page.evaluate(() => {
      return window.errors || [];
    });
    
    if (appInfo.childrenCount > 0) {
      console.log('\n✅ SUCCESS: Frontend is rendering correctly!');
    } else {
      console.log('\n❌ FAIL: Frontend still showing white screen');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'frontend-fixed.png', fullPage: true });
    console.log('\n=== SCREENSHOT ===');
    console.log('Screenshot saved to frontend-fixed.png');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  await browser.close();
})();
