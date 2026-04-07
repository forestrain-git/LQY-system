import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(async () => {
  console.log('启动浏览器...');
  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  // 截图告警中心页面
  console.log('正在访问告警中心...');
  await page.goto('http://localhost:5173/alerts', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  // 等待页面加载
  await page.waitForTimeout(3000);

  const alertScreenshotPath = path.join(__dirname, '..', 'f-cutpictures', 'alert-center-auto.png');
  await page.screenshot({ path: alertScreenshotPath, fullPage: true });
  console.log('告警中心截图已保存:', alertScreenshotPath);

  // 截图设备管理页面
  console.log('正在访问设备管理...');
  await page.goto('http://localhost:5173/devices', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  await page.waitForTimeout(3000);

  const deviceScreenshotPath = path.join(__dirname, '..', 'f-cutpictures', 'device-manage-auto.png');
  await page.screenshot({ path: deviceScreenshotPath, fullPage: true });
  console.log('设备管理截图已保存:', deviceScreenshotPath);

  await browser.close();
  console.log('截图完成！');
})();
