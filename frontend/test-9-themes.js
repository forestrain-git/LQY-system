import { chromium } from 'playwright';

const themes = [
  { name: 'linear', label: 'Linear' },
  { name: 'vercel', label: 'Vercel' },
  { name: 'supabase', label: 'Supabase' },
  { name: 'raycast', label: 'Raycast' },
  { name: 'apple', label: 'Apple' },
  { name: 'spotify', label: 'Spotify' },
  { name: 'stripe', label: 'Stripe' },
  { name: 'notion', label: 'Notion' },
  { name: 'cursor', label: 'Cursor' }
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const theme of themes) {
    console.log(`Testing ${theme.name}...`);

    await page.goto('http://localhost:5173/alerts', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    await page.waitForTimeout(1500);

    // Click on theme switcher to open dropdown
    await page.click('.theme-preview');
    await page.waitForTimeout(500);

    // Click on the theme
    await page.click(`text=${theme.label}`);
    await page.waitForTimeout(1500);

    const screenshotPath = `/mnt/c/users/administrator/projects/lqy-system/f-cutpictures/theme-${theme.name}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`✓ ${theme.name} saved`);
  }

  await browser.close();
  console.log('\nAll 9 themes captured!');
})();
