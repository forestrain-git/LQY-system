import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const themesDir = '/mnt/c/users/administrator/projects/awesome-design-md/design-md';
const themes = fs.readdirSync(themesDir).filter(f => {
  const stat = fs.statSync(path.join(themesDir, f));
  return stat.isDirectory();
});

console.log(`Found ${themes.length} themes`);

// 提取CSS变量的函数
async function extractThemeColors(themeName) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // 尝试读取 preview-dark.html 或 preview.html
    const darkPath = path.join(themesDir, themeName, 'preview-dark.html');
    const lightPath = path.join(themesDir, themeName, 'preview.html');

    let filePath = fs.existsSync(darkPath) ? darkPath : lightPath;

    if (!fs.existsSync(filePath)) {
      console.log(`No preview for ${themeName}`);
      await browser.close();
      return null;
    }

    const fileUrl = 'file://' + filePath;
    await page.goto(fileUrl, { waitUntil: 'networkidle' });

    // 提取颜色变量
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      const bodyStyle = getComputedStyle(document.body);

      return {
        // 背景色
        bgPage: style.getPropertyValue('--bg-page') || bodyStyle.backgroundColor,
        bgSurface: style.getPropertyValue('--bg-surface'),
        bgCard: style.getPropertyValue('--bg-card'),
        bgHover: style.getPropertyValue('--bg-hover'),

        // 文字色
        textPrimary: style.getPropertyValue('--text-primary'),
        textSecondary: style.getPropertyValue('--text-secondary'),
        textMuted: style.getPropertyValue('--text-tertiary') || style.getPropertyValue('--text-muted'),

        // 强调色
        primary: style.getPropertyValue('--brand') || style.getPropertyValue('--color-primary'),
        secondary: style.getPropertyValue('--accent'),
        success: style.getPropertyValue('--success'),
        warning: style.getPropertyValue('--warning'),
        danger: style.getPropertyValue('--danger'),

        // 边框
        borderColor: style.getPropertyValue('--border-primary') || style.getPropertyValue('--border-color'),

        // 检测是否为深色主题
        isDark: (() => {
          const bg = bodyStyle.backgroundColor;
          if (!bg) return true;
          const rgb = bg.match(/\d+/g);
          if (!rgb) return true;
          const [r, g, b] = rgb.map(Number);
          return (r + g + b) / 3 < 128;
        })()
      };
    });

    await browser.close();
    return { name: themeName, colors };
  } catch (e) {
    console.error(`Error extracting ${themeName}:`, e.message);
    await browser.close();
    return null;
  }
}

// 批量提取前10个主题
async function extractBatch() {
  const results = [];
  const batch = themes.slice(0, 15); // 先提取15个

  for (const theme of batch) {
    console.log(`Extracting ${theme}...`);
    const data = await extractThemeColors(theme);
    if (data && data.colors.bgPage) {
      results.push(data);
    }
  }

  // 保存结果
  fs.writeFileSync('/mnt/c/users/administrator/projects/lqy-system/frontend/extracted-themes.json',
    JSON.stringify(results, null, 2));
  console.log('Saved to extracted-themes.json');
}

extractBatch().catch(console.error);
