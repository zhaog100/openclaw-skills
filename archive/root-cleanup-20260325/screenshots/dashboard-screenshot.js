const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ 
    headless: false, // 使用有头模式，方便调试和确保页面加载完整
    args: ['--start-maximized']
  });
  
  const context = await browser.newContext({
    viewport: null, // 使用系统默认视口
    locale: 'zh-CN'
  });
  
  const page = await context.newPage();
  
  try {
    console.log('1. 打开平台...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    // 等待页面加载
    await page.waitForTimeout(2000);
    
    // 检查是否在登录页面
    const hasLoginForm = await page.locator('input[type="text"], input[type="email"], input[placeholder*="账号"], input[placeholder*="用户名"]').count() > 0;
    
    if (hasLoginForm) {
      console.log('2. 检测到登录页面，开始登录...');
      
      // 等待表单元素加载
      await page.waitForSelector('input', { timeout: 10000 });
      
      // 尝试查找并选择租户
      const tenantSelector = await page.locator('select, [class*="tenant"], [class*="team"]').first();
      if (await tenantSelector.count() > 0) {
        console.log('   - 选择租户: TeamFlow');
        await tenantSelector.click();
        await page.waitForTimeout(500);
        
        // 尝试选择TeamFlow选项
        const teamFlowOption = page.locator('option:has-text("TeamFlow"), li:has-text("TeamFlow"), [class*="option"]:has-text("TeamFlow")').first();
        if (await teamFlowOption.count() > 0) {
          await teamFlowOption.click();
          await page.waitForTimeout(500);
        }
      }
      
      // 输入账号
      console.log('   - 输入账号: test');
      const usernameInput = page.locator('input[type="text"], input[type="email"], input[placeholder*="账号"], input[placeholder*="用户名"]').first();
      await usernameInput.fill('test');
      await page.waitForTimeout(300);
      
      // 输入密码
      console.log('   - 输入密码: test123');
      const passwordInput = page.locator('input[type="password"]').first();
      await passwordInput.fill('test123');
      await page.waitForTimeout(300);
      
      // 点击登录按钮
      console.log('   - 点击登录按钮');
      const loginButton = page.locator('button:has-text("登录"), button:has-text("Login"), input[type="submit"], [class*="login"] button').first();
      await loginButton.click();
      
      // 等待登录完成
      console.log('   - 等待登录完成...');
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
        console.log('   - 网络未完全空闲，继续执行...');
      });
    } else {
      console.log('2. 已经登录或无需登录');
    }
    
    // 等待页面稳定
    await page.waitForTimeout(2000);
    
    // 查找并点击"统计看板"菜单
    console.log('3. 查找"统计看板"菜单...');
    const dashboardMenu = page.locator('text=统计看板, [class*="menu"]:has-text("统计看板"), a:has-text("统计看板"), button:has-text("统计看板")').first();
    
    if (await dashboardMenu.count() > 0) {
      console.log('   - 点击"统计看板"菜单');
      await dashboardMenu.click();
      
      // 等待页面加载完成
      console.log('4. 等待统计看板页面加载...');
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
        console.log('   - 网络未完全空闲，继续执行...');
      });
      
      // 额外等待确保图表渲染
      await page.waitForTimeout(2000);
    } else {
      console.log('   - 未找到"统计看板"菜单，尝试查找第一个菜单项');
      const firstMenu = page.locator('[class*="menu"] a, [class*="menu"] button, nav a, nav button').first();
      if (await firstMenu.count() > 0) {
        await firstMenu.click();
        await page.waitForTimeout(3000);
        await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
        await page.waitForTimeout(2000);
      }
    }
    
    // 截图
    console.log('5. 开始截图...');
    const screenshotPath = path.join(__dirname, '统计看板.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`   ✓ 截图已保存: ${screenshotPath}`);
    
    // 分析页面内容
    console.log('\n6. 分析页面内容...');
    const pageTitle = await page.title();
    const pageUrl = page.url();
    console.log(`   - 页面标题: ${pageTitle}`);
    console.log(`   - 当前URL: ${pageUrl}`);
    
    // 获取主要功能区域
    const pageText = await page.locator('body').textContent();
    const menuItems = await page.locator('[class*="menu"] a, [class*="menu"] button, nav a, nav button').allTextContents();
    
    console.log('\n页面功能分析:');
    console.log('='.repeat(50));
    
    // 尝试提取页面结构
    const headings = await page.locator('h1, h2, h3, [class*="title"], [class*="header"]').allTextContents();
    if (headings.length > 0) {
      console.log('主要标题:');
      headings.forEach(h => console.log(`  - ${h.trim()}`));
    }
    
    // 查找图表或数据展示区域
    const charts = await page.locator('[class*="chart"], [class*="graph"], canvas, svg').count();
    if (charts > 0) {
      console.log(`\n检测到 ${charts} 个图表/图形元素`);
    }
    
    // 查找表格
    const tables = await page.locator('table').count();
    if (tables > 0) {
      console.log(`检测到 ${tables} 个数据表格`);
    }
    
    // 查找卡片或统计数字
    const cards = await page.locator('[class*="card"], [class*="stat"], [class*="metric"]').count();
    if (cards > 0) {
      console.log(`检测到 ${cards} 个统计卡片`);
    }
    
    console.log('\n可测试功能点:');
    console.log('='.repeat(50));
    console.log('1. 页面加载性能 - 统计页面加载时间');
    console.log('2. 数据展示 - 检查图表、表格数据是否正确加载');
    console.log('3. 响应式布局 - 不同分辨率下的显示效果');
    console.log('4. 交互功能 - 筛选、排序、导出等操作');
    console.log('5. 数据刷新 - 实时数据更新功能');
    console.log('6. 权限控制 - 不同角色的访问权限');
    
  } catch (error) {
    console.error('执行出错:', error.message);
    const errorScreenshot = path.join(__dirname, 'error-state.png');
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`错误状态截图已保存: ${errorScreenshot}`);
    throw error;
  } finally {
    await browser.close();
    console.log('\n浏览器已关闭');
  }
})();
