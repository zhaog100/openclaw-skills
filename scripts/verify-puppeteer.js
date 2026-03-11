/**
 * Puppeteer 安装验证脚本
 */

const puppeteer = require('puppeteer');

(async () => {
  try {
    console.log('喏，官家！开始验证Puppeteer安装...\n');

    // 启动浏览器
    console.log('1. 启动浏览器...');
    const browser = await puppeteer.launch({
      headless: 'new'
    });
    console.log('   ✅ 浏览器启动成功\n');

    // 打开新页面
    console.log('2. 打开新页面...');
    const page = await browser.newPage();
    console.log('   ✅ 新页面创建成功\n');

    // 访问测试页面
    console.log('3. 访问测试页面（example.com）...');
    await page.goto('https://example.com', {
      waitUntil: 'networkidle2'
    });
    console.log('   ✅ 页面加载成功\n');

    // 获取页面标题
    console.log('4. 获取页面标题...');
    const title = await page.title();
    console.log(`   ✅ 页面标题: ${title}\n`);

    // 截图
    console.log('5. 截图测试...');
    await page.screenshot({ path: './puppeteer-test.png' });
    console.log('   ✅ 截图已保存: ./puppeteer-test.png\n');

    // 关闭浏览器
    console.log('6. 关闭浏览器...');
    await browser.close();
    console.log('   ✅ 浏览器关闭成功\n');

    console.log('='.repeat(60));
    console.log('✅ Puppeteer安装验证成功！');
    console.log('='.repeat(60));
    console.log('\n功能测试:');
    console.log('  ✅ 浏览器启动');
    console.log('  ✅ 页面访问');
    console.log('  ✅ 标题获取');
    console.log('  ✅ 截图功能');
    console.log('\n💡 Puppeteer已就绪，可以使用！');

  } catch (error) {
    console.error('❌ 验证失败:', error.message);
    console.log('\n可能的原因:');
    console.log('  1. Chromium下载失败');
    console.log('  2. 依赖缺失');
    console.log('  3. 权限问题');
    console.log('\n建议运行: npm install puppeteer');
  }
})();
