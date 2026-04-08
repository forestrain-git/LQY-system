import { chromium } from 'playwright';

(async () => {
  console.log('Launching Google Chrome...');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  
  const page = await context.newPage();
  
  console.log('Opening login page...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  
  console.log('Chrome is now open!');
  console.log('URL: http://localhost:5173/login');
  console.log('');
  console.log('Test credentials:');
  console.log('  Username: admin');
  console.log('  Password: admin123');
  
  // Keep browser open
  await new Promise(() => {});
})();
