const { chromium } = require('playwright');

async function visitTraveler() {
  console.log('🚀 启动旅行客平台访问...');
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  try {
    // 访问登录页面
    console.log('📱 访问登录页面...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    await page.waitForTimeout(3000);
    
    // 截图1：登录页
    await page.screenshot({ 
      path: '/tmp/traveler-01-login.png',
      fullPage: true
    });
    console.log('✅ 登录页截图完成');
    
    // 查找租户下拉框并选择
    console.log('🏢 选择租户 TeamFlow...');
    const selectElement = await page.locator('select').first();
    if (await selectElement.isVisible()) {
      await selectElement.selectOption({ label: 'TeamFlow' });
      console.log('✅ 已选择 TeamFlow');
      await page.waitForTimeout(1000);
    } else {
      console.log('⚠️ 未找到租户下拉框');
    }
    
    // 填写登录信息
    console.log('📝 填写登录信息...');
    const usernameInput = page.locator('input[type="text"], input[placeholder*="账号"], input[placeholder*="用户名"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    
    await usernameInput.fill('test');
    await passwordInput.fill('test123');
    console.log('✅ 登录信息填写完成');
    
    await page.waitForTimeout(1000);
    
    // 截图2：填写后
    await page.screenshot({ 
      path: '/tmp/traveler-02-filled.png',
      fullPage: true
    });
    console.log('✅ 填写后截图完成');
    
    // 点击登录
    console.log('🔑 点击登录...');
    const loginButton = page.locator('button:has-text("登录"), button[type="submit"]').first();
    await loginButton.click();
    
    // 等待登录成功
    console.log('⏳ 等待登录成功...');
    await page.waitForURL('**/#/**', { timeout: 15000 });
    await page.waitForTimeout(5000);
    
    // 截图3：首页
    await page.screenshot({ 
      path: '/tmp/traveler-03-home.png',
      fullPage: true
    });
    console.log('✅ 首页截图完成');
    
    // 获取所有菜单
    console.log('📋 获取菜单结构...');
    const menuItems = await page.locator('[class*="menu"] a, [class*="nav"] a, [class*="sidebar"] a').allTextContents();
    console.log('菜单项：', menuItems.filter(m => m.trim()).slice(0, 15));
    
    // 获取页面URL
    const currentUrl = page.url();
    console.log('🌐 当前URL：', currentUrl);
    
    // 获取页面标题
    const title = await page.title();
    console.log('📄 页面标题：', title);
    
    // 保存页面HTML
    const html = await page.content();
    require('fs').writeFileSync('/tmp/traveler-page.html', html);
    console.log('✅ 页面HTML已保存');
    
    // 尝试截图侧边栏
    const sidebar = page.locator('[class*="sidebar"], [class*="menu"], [class*="nav"]').first();
    if (await sidebar.isVisible()) {
      await sidebar.screenshot({ path: '/tmp/traveler-04-sidebar.png' });
      console.log('✅ 侧边栏截图完成');
    }
    
    console.log('\n✨ 访问完成！');
    console.log('📸 截图文件：');
    console.log('  - /tmp/traveler-01-login.png');
    console.log('  - /tmp/traveler-02-filled.png');
    console.log('  - /tmp/traveler-03-home.png');
    console.log('  - /tmp/traveler-04-sidebar.png');
    console.log('  - /tmp/traveler-page.html');
    
  } catch (error) {
    console.error('❌ 访问失败：', error.message);
    
    // 失败时截图
    await page.screenshot({ 
      path: '/tmp/traveler-error.png',
      fullPage: true
    });
    console.log('❌ 错误截图已保存：/tmp/traveler-error.png');
    
    // 保存错误HTML
    const html = await page.content();
    require('fs').writeFileSync('/tmp/traveler-error.html', html);
    console.log('❌ 错误HTML已保存：/tmp/traveler-error.html');
    
    throw error;
  } finally {
    await browser.close();
  }
}

visitTraveler().catch(console.error);
