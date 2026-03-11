/**
 * Bing图像生成工具访问脚本
 * 使用Puppeteer自动化操作
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function accessBingImageCreator() {
  console.log('喏，官家！开始访问Bing图像生成工具！\n');

  const browser = await puppeteer.launch({
    headless: false // 使用非headless模式，便于查看
  });

  const page = await browser.newPage();

  try {
    // 访问Bing图像创建页面
    console.log('1. 访问Bing图像创建页面...');
    await page.goto('https://www.bing.com/images/create?FORM=GENILP', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('✅ 页面加载成功\n');

    // 等待页面完全加载
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 检查是否需要登录
    console.log('2. 检查登录状态...');
    const currentUrl = page.url();

    if (currentUrl.includes('login') || currentUrl.includes('signup')) {
      console.log('⚠️  需要登录Microsoft账户');
      console.log('请在浏览器中手动登录');
      console.log('登录后可以继续操作\n');

      // 等待用户登录
      await page.waitForNavigation({ timeout: 120000 });
    }

    console.log('✅ 登录状态正常\n');

    // 截图当前页面
    console.log('3. 截图当前页面...');
    const screenshotPath = './bing-image-creator.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    // 提取页面信息
    console.log('4. 提取页面信息...');
    const pageInfo = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        hasInputField: !!document.querySelector('input[type="text"], textarea'),
        hasCreateButton: !!document.querySelector('button[type="submit"], button.create'),
        pageText: document.body.innerText.substring(0, 500)
      };
    });

    console.log('页面标题:', pageInfo.title);
    console.log('当前URL:', pageInfo.url);
    console.log('有输入框:', pageInfo.hasInputField);
    console.log('有创建按钮:', pageInfo.hasCreateButton);
    console.log('\n页面预览:');
    console.log(pageInfo.pageText);

    // 保存页面信息
    const infoPath = './bing-image-creator-info.json';
    fs.writeFileSync(infoPath, JSON.stringify(pageInfo, null, 2));
    console.log(`\n✅ 页面信息已保存: ${infoPath}`);

    // 等待用户查看
    console.log('\n浏览器保持打开，您可以手动操作。');
    console.log('完成后关闭浏览器即可。\n');

    // 保持浏览器打开，等待用户手动关闭
    await new Promise(resolve => {
      browser.on('disconnected', resolve);
    });

  } catch (error) {
    console.error('❌ 访问失败:', error.message);

    // 保存错误截图
    try {
      await page.screenshot({ path: './bing-image-error.png' });
      console.log('错误截图已保存: ./bing-image-error.png');
    } catch (e) {
      console.log('截图失败');
    }

    await browser.close();
  }
}

// 运行
accessBingImageCreator().catch(console.error);
