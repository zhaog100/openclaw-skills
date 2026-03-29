// 页面对象模型 - 统计看板页面
class DashboardPage {
  constructor(page) {
    this.page = page;

    // 菜单导航
    this.menuDashboard = 'text=统计看板';

    // 数据展示元素
    this.statCards = '.stat-card, [data-test="stat-card"], .card:has(.number)';
    this.charts = 'canvas, svg, [data-test="chart"]';

    // 功能按钮
    this.refreshButton = 'button:has-text("刷新"), button:has-text("Refresh")';
    this.exportButton = 'button:has-text("导出"), button:has-text("Export")';
    this.timeSelector = 'select, [data-test="time-selector"], [role="combobox"]';

    // 时间范围选项
    this.timeRange7Days = 'text=最近7天, text=7天, option[value="7d"]';
    this.timeRange30Days = 'text=最近30天, text=30天, option[value="30d"]';
    this.timeRange90Days = 'text=最近90天, text=90天, option[value="90d"]';
  }

  // 导航到统计看板
  async navigate() {
    console.log('导航到统计看板...');
    await this.page.click(this.menuDashboard);
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(3000);
    console.log('页面加载完成');
  }

  // 验证页面加载
  async verifyPageLoaded() {
    console.log('验证页面加载...');

    // 检查URL
    const url = this.page.url();
    console.log(`当前URL: ${url}`);

    // 检查统计卡片
    const cards = await this.page.$$(this.statCards);
    console.log(`找到 ${cards.length} 个统计卡片`);

    // 检查图表
    const charts = await this.page.$$(this.charts);
    console.log(`找到 ${charts.length} 个图表`);

    // 返回验证结果
    const urlValid = url.includes('statisticsDashboard');
    const hasCards = cards.length > 0;
    const hasCharts = charts.length > 0;

    console.log(`URL验证: ${urlValid ? '✅' : '❌'}`);
    console.log(`卡片验证: ${hasCards ? '✅' : '❌'}`);
    console.log(`图表验证: ${hasCharts ? '✅' : '❌'}`);

    return urlValid && hasCards && hasCharts;
  }

  // 刷新数据
  async refresh() {
    console.log('刷新数据...');
    const refreshBtn = await this.page.$(this.refreshButton);
    if (refreshBtn) {
      await refreshBtn.click();
      await this.page.waitForTimeout(3000);
      console.log('数据刷新完成');
    } else {
      console.log('未找到刷新按钮');
    }
  }

  // 选择时间范围
  async selectTimeRange(range) {
    console.log(`选择时间范围: ${range}...`);

    const timeSelectorElement = await this.page.$(this.timeSelector);
    if (timeSelectorElement) {
      await timeSelectorElement.click();
      await this.page.waitForTimeout(1000);

      // 根据范围选择对应选项
      const optionMap = {
        '7d': this.timeRange7Days,
        '30d': this.timeRange30Days,
        '90d': this.timeRange90Days
      };

      const optionSelector = optionMap[range];
      if (optionSelector) {
        const option = await this.page.$(optionSelector);
        if (option) {
          await option.click();
          await this.page.waitForTimeout(2000);
          console.log('时间范围选择完成');
        }
      }
    } else {
      console.log('未找到时间选择器');
    }
  }

  // 获取统计数据
  async getStatData() {
    console.log('获取统计数据...');
    const cards = await this.page.$$(this.statCards);
    const stats = [];

    for (const card of cards) {
      const title = await card.$eval('.title, h3, h4', el => el.textContent).catch(() => '');
      const value = await card.$eval('.number, .value, p', el => el.textContent).catch(() => '');

      stats.push({ title, value });
    }

    console.log(`获取到 ${stats.length} 个统计数据`);
    return stats;
  }

  // 导出数据
  async exportData(format = 'excel') {
    console.log(`导出数据（格式: ${format}）...`);

    const exportBtn = await this.page.$(this.exportButton);
    if (exportBtn) {
      // 监听下载事件
      const [download] = await Promise.all([
        this.page.waitForEvent('download', { timeout: 10000 }).catch(() => null),
        exportBtn.click()
      ]);

      if (download) {
        const fileName = download.suggestedFilename();
        console.log(`文件下载: ${fileName}`);
        return fileName;
      }
    } else {
      console.log('未找到导出按钮');
    }

    return null;
  }

  // 截图
  async takeScreenshot(name = 'dashboard') {
    const screenshotPath = `/mnt/hgfs/OpenClaw/tools/test-screenshots/${name}-${Date.now()}.png`;
    await this.page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`截图保存: ${screenshotPath}`);
    return screenshotPath;
  }

  // 性能测试
  async measureLoadTime() {
    console.log('测量页面加载时间...');
    const startTime = Date.now();

    await this.navigate();

    const loadTime = Date.now() - startTime;
    console.log(`页面加载时间: ${loadTime}ms`);

    return loadTime;
  }

  // 响应式测试
  async testResponsive(width, height) {
    console.log(`测试响应式布局: ${width}x${height}...`);

    await this.page.setViewportSize({ width, height });
    await this.page.waitForTimeout(1000);

    const screenshot = await this.takeScreenshot(`responsive-${width}x${height}`);

    // 检查是否有横向滚动条
    const hasHorizontalScroll = await this.page.evaluate(() => {
      return document.body.scrollWidth > document.body.clientWidth;
    });

    console.log(`横向滚动条: ${hasHorizontalScroll ? '存在' : '不存在'}`);

    return {
      screenshot,
      hasHorizontalScroll
    };
  }
}

module.exports = DashboardPage;
