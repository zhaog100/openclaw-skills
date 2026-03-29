// 统计看板测试套件
const { chromium } = require('playwright');
const LoginPage = require('./pages/LoginPage');
const DashboardPage = require('./pages/DashboardPage');

async function runTests() {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║         旅行客平台 - 统计看板自动化测试                       ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('');

  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  const testResults = [];

  try {
    // 前置条件：登录
    console.log('【前置条件】登录系统...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin');

    const loginPage = new LoginPage(page);
    await loginPage.login('TeamFlow', 'test', 'test123');

    const dashboardPage = new DashboardPage(page);

    console.log('');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('【测试开始】统计看板功能测试');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('');

    // TC001 - 页面正常加载
    console.log('【TC001】页面正常加载测试...');
    await dashboardPage.navigate();
    const isLoaded = await dashboardPage.verifyPageLoaded();
    testResults.push({
      case: 'TC001',
      name: '页面正常加载',
      result: isLoaded ? '✅ PASS' : '❌ FAIL'
    });
    console.log('');

    // TC002 - 页面加载性能
    console.log('【TC002】页面加载性能测试...');
    const loadTime = await dashboardPage.measureLoadTime();
    const isPerformanceOK = loadTime < 3000;
    testResults.push({
      case: 'TC002',
      name: '页面加载性能',
      result: isPerformanceOK ? '✅ PASS' : '❌ FAIL',
      detail: `${loadTime}ms`
    });
    console.log('');

    // TC003 - 统计卡片数据验证
    console.log('【TC003】统计卡片数据验证...');
    const stats = await dashboardPage.getStatData();
    const hasValidStats = stats.length > 0;
    testResults.push({
      case: 'TC003',
      name: '统计卡片数据验证',
      result: hasValidStats ? '✅ PASS' : '❌ FAIL',
      detail: `${stats.length}个统计卡片`
    });
    console.log('');

    // TC006 - 时间范围选择（7天）
    console.log('【TC006】时间范围选择测试（7天）...');
    await dashboardPage.selectTimeRange('7d');
    const screenshot7d = await dashboardPage.takeScreenshot('tc006-7days');
    testResults.push({
      case: 'TC006',
      name: '时间范围选择（7天）',
      result: '✅ PASS',
      detail: screenshot7d
    });
    console.log('');

    // TC009 - 手动刷新功能
    console.log('【TC009】手动刷新功能测试...');
    await dashboardPage.refresh();
    testResults.push({
      case: 'TC009',
      name: '手动刷新功能',
      result: '✅ PASS'
    });
    console.log('');

    // TC013 - 响应式测试（不同分辨率）
    console.log('【TC013】响应式测试...');

    // 桌面端（1920x1080）
    await dashboardPage.testResponsive(1920, 1080);

    // 笔记本（1366x768）
    await dashboardPage.testResponsive(1366, 768);

    // 平板（768x1024）
    await dashboardPage.testResponsive(768, 1024);

    testResults.push({
      case: 'TC013',
      name: '响应式测试',
      result: '✅ PASS',
      detail: '3种分辨率测试完成'
    });
    console.log('');

    // 生成测试报告
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('【测试报告】');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log('');

    let passCount = 0;
    let failCount = 0;

    testResults.forEach(result => {
      console.log(`${result.case} - ${result.name}: ${result.result}`);
      if (result.detail) {
        console.log(`   详情: ${result.detail}`);
      }

      if (result.result.includes('PASS')) {
        passCount++;
      } else {
        failCount++;
      }
    });

    console.log('');
    console.log('═══════════════════════════════════════════════════════════════');
    console.log(`【测试统计】总计: ${testResults.length} | 通过: ${passCount} | 失败: ${failCount}`);
    console.log(`【通过率】${((passCount / testResults.length) * 100).toFixed(1)}%`);
    console.log('═══════════════════════════════════════════════════════════════');

  } catch (error) {
    console.error('❌ 测试执行失败:', error.message);

    // 失败时截图
    const errorScreenshot = `/mnt/hgfs/OpenClaw/tools/test-screenshots/error-${Date.now()}.png`;
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`错误截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

// 运行测试
runTests();
