const { chromium } = require('playwright');

(async () => {
  console.log('Starting browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    bypassCSP: true
  });
  const page = await context.newPage();
  
  page.on('console', msg => console.log('CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  try {
    console.log('Navigating to http://localhost:8080 with cache busting...');
    // Add cache-busting query parameter
    await page.goto('http://localhost:8080?t=' + Date.now(), { 
      timeout: 30000, 
      waitUntil: 'networkidle',
      cache: 'no-store'
    });
    await page.waitForTimeout(5000);
    
    const content = await page.content();
    console.log('\n=== PAGE INFO ===');
    console.log('Page HTML length:', content.length);
    console.log('Page title:', await page.title());
    
    // Check for any remaining errors in the last 5 seconds
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    
    // Check if #app has any children
    const appInfo = await page.evaluate(() => {
      const app = document.getElementById('app');
      return {
        found: !!app,
        childrenCount: app ? app.children.length : 0,
        innerText: app ? app.innerText.substring(0, 300) : 'N/A'
      };
    });
    console.log('\n=== APP ELEMENT ===');
    console.log('#app found:', appInfo.found);
    console.log('#app children count:', appInfo.childrenCount);
    console.log('#app innerText preview:', appInfo.innerText);
    
    // Get all console messages
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push(msg.text());
    });
    
    // Check for specific error
    const hasI18nError = consoleMessages.some(msg => msg.includes('$t'));
    
    if (appInfo.childrenCount > 0 && !hasI18nError) {
      console.log('\n✅ SUCCESS: Frontend is rendering correctly WITHOUT i18n errors!');
    } else if (appInfo.childrenCount > 0) {
      console.log('\n⚠️  PARTIAL SUCCESS: Frontend is rendering but still has i18n errors');
    } else {
      console.log('\n❌ FAIL: Frontend still showing white screen');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'frontend-final.png', fullPage: true });
    console.log('\n=== SCREENSHOT ===');
    console.log('Screenshot saved to frontend-final.png');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  await browser.close();
})();
