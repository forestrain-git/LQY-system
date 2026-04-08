import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const themesDir = '/mnt/c/users/administrator/projects/awesome-design-md/design-md';
const themes = fs.readdirSync(themesDir).filter(f => {
  const stat = fs.statSync(path.join(themesDir, f));
  return stat.isDirectory();
});

console.log(`Found ${themes.length} themes`);
console.log('Themes:', themes.join(', '));

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
      console.log(`⚠️  No preview for ${themeName}`);
      await browser.close();
      return null;
    }

    const fileUrl = 'file://' + filePath;
    await page.goto(fileUrl, { waitUntil: 'networkidle' });

    // 提取颜色变量
    const colors = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      const bodyStyle = getComputedStyle(document.body);

      // 辅助函数：获取CSS变量值
      const getVar = (name) => style.getPropertyValue(name)?.trim() || '';

      // 获取背景色
      const bgPage = getVar('--bg-page') || bodyStyle.backgroundColor;

      // 检测是否为深色主题
      let isDark = true;
      if (bgPage) {
        const rgb = bgPage.match(/\d+/g);
        if (rgb) {
          const [r, g, b] = rgb.map(Number);
          isDark = (r + g + b) / 3 < 128;
        }
      }

      return {
        // 背景色
        bgPage: bgPage,
        bgSurface: getVar('--bg-surface') || getVar('--bg-secondary') || bgPage,
        bgCard: getVar('--bg-card') || getVar('--bg-elevated') || getVar('--surface') || '',
        bgHover: getVar('--bg-hover') || getVar('--hover') || '',
        bgSidebar: getVar('--bg-sidebar') || getVar('--bg-surface') || bgPage,

        // 文字色
        textPrimary: getVar('--text-primary') || getVar('--foreground') || bodyStyle.color,
        textSecondary: getVar('--text-secondary') || getVar('--muted-foreground') || '',
        textMuted: getVar('--text-tertiary') || getVar('--text-muted') || getVar('--muted') || '',

        // 强调色
        primary: getVar('--brand') || getVar('--color-primary') || getVar('--primary') || '',
        secondary: getVar('--accent') || getVar('--color-secondary') || getVar('--secondary') || '',
        success: getVar('--success') || getVar('--color-success') || '',
        warning: getVar('--warning') || getVar('--color-warning') || '',
        danger: getVar('--danger') || getVar('--error') || getVar('--color-danger') || '',

        // 边框
        borderColor: getVar('--border-primary') || getVar('--border-color') || getVar('--border') || '',
        divider: getVar('--border-secondary') || getVar('--divider') || getVar('--border-primary') || '',

        isDark
      };
    });

    await browser.close();

    // 检查提取到的颜色数量
    const definedColors = Object.entries(colors).filter(([key, value]) => {
      if (key === 'isDark') return false;
      return value && value !== '';
    }).length;

    console.log(`✓ ${themeName}: ${definedColors}/15 colors extracted`);

    return { name: themeName, colors };
  } catch (e) {
    console.error(`❌ Error extracting ${themeName}:`, e.message);
    await browser.close();
    return null;
  }
}

// 提取所有主题
async function extractAll() {
  const results = [];

  // 处理所有58个主题
  for (const theme of themes) {
    const data = await extractThemeColors(theme);
    if (data && data.colors.bgPage) {
      results.push(data);
    }
  }

  // 按提取到的颜色数量排序（完整性）
  results.sort((a, b) => {
    const aCount = Object.values(a.colors).filter(v => v && v !== '').length;
    const bCount = Object.values(b.colors).filter(v => v && v !== '').length;
    return bCount - aCount;
  });

  // 保存完整结果
  fs.writeFileSync('/mnt/c/users/administrator/projects/lqy-system/frontend/extracted-themes-complete.json',
    JSON.stringify(results, null, 2));

  // 生成主题统计
  const stats = results.map(r => {
    const defined = Object.entries(r.colors).filter(([key, value]) => {
      if (key === 'isDark') return false;
      return value && value !== '';
    }).map(([key]) => key);
    return `${r.name}: ${defined.length} colors (${defined.slice(0, 5).join(', ')}...)`;
  });

  fs.writeFileSync('/mnt/c/users/administrator/projects/lqy-system/frontend/extraction-stats.txt',
    stats.join('\n'));

  console.log(`\n✅ Extracted ${results.length} themes successfully`);
  console.log('Results saved to extracted-themes-complete.json');
  console.log('Stats saved to extraction-stats.txt');
}

extractAll().catch(console.error);
