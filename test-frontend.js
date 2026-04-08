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
        innerHTML: app ? app.innerHTML.substring(0, 500) : 'N/A'
      };
    });
    console.log('\n=== APP ELEMENT ===');
    console.log('#app found:', appInfo.found);
    console.log('#app children count:', appInfo.childrenCount);
    console.log('#app innerHTML (first 500 chars):', appInfo.innerHTML);
    
    // Check if there are any visible elements
    const bodyContent = await page.evaluate(() => {
      return document.body.innerText || 'No text content';
    });
    console.log('\n=== BODY CONTENT ===');
    console.log('Body text content (first 500 chars):', bodyContent.substring(0, 500));
    
    // Check for white screen indicators
    const styles = await page.evaluate(() => {
      const app = document.getElementById('app');
      if (app) {
        const computed = window.getComputedStyle(app);
        return {
          backgroundColor: computed.backgroundColor,
          display: computed.display,
          visibility: computed.visibility,
          minHeight: computed.minHeight
        };
      }
      return null;
    });
    console.log('\n=== APP STYLES ===');
    console.log('App styles:', styles);
    
    // Take screenshot
    await page.screenshot({ path: 'frontend-current.png', fullPage: true });
    console.log('\n=== SCREENSHOT ===');
    console.log('Screenshot saved to frontend-current.png');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  await browser.close();
})();
