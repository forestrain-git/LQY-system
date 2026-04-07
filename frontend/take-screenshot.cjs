const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  console.log('启动 Edge 浏览器...');

  // 使用 Windows 的 Edge
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  try {
    // 截图告警中心
    console.log('访问告警中心...');
    await page.goto('http://localhost:5173/alerts', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    await page.waitForTimeout(3000);

    const alertPath = path.join(__dirname, '..', 'f-cutpictures', 'alert-current.png');
    await page.screenshot({ path: alertPath, fullPage: false });
    console.log('✓ 告警中心截图:', alertPath);

    // 截图设备管理
    console.log('访问设备管理...');
    await page.goto('http://localhost:5173/devices', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    await page.waitForTimeout(3000);

    const devicePath = path.join(__dirname, '..', 'f-cutpictures', 'device-current.png');
    await page.screenshot({ path: devicePath, fullPage: false });
    console.log('✓ 设备管理截图:', devicePath);

  } catch (e) {
    console.error('✗ 截图失败:', e.message);
  }

  await browser.close();
  console.log('完成！');
})();
