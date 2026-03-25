// 获取登录页面结构
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    console.log('访问登录页面...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    console.log('\n=== 页面HTML结构 ===\n');
    const html = await page.content();
    console.log(html.substring(0, 3000));

    console.log('\n=== 输入框元素 ===\n');
    const inputs = await page.locator('input').all();
    console.log(`找到 ${inputs.length} 个input元素`);

    for (let i = 0; i < inputs.length; i++) {
      const input = inputs[i];
      const type = await input.getAttribute('type');
      const placeholder = await input.getAttribute('placeholder');
      const name = await input.getAttribute('name');
      const id = await input.getAttribute('id');
      console.log(`Input ${i + 1}: type=${type}, placeholder=${placeholder}, name=${name}, id=${id}`);
    }

    console.log('\n=== 按钮元素 ===\n');
    const buttons = await page.locator('button').all();
    console.log(`找到 ${buttons.length} 个button元素`);

    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      const text = await button.textContent();
      console.log(`Button ${i + 1}: ${text}`);
    }

    await page.screenshot({ path: '/mnt/hgfs/OpenClaw/test/登录页面截图.png', fullPage: true });
    console.log('\n✅ 截图已保存: /mnt/hgfs/OpenClaw/test/登录页面截图.png');

  } catch (error) {
    console.error('❌ 错误:', error.message);
  } finally {
    await browser.close();
  }
})();
