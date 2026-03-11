/**
 * AIHubMix模型自动检查脚本
 * 爬取AIHubMix官网模型列表，对比现有配置，发现新模型
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 当前已配置的AIHubMix模型（14个）
const CONFIGURED_MODELS = [
  'coding-glm-5-free',
  'gemini-3.1-flash-image-preview-free',
  'gemini-3-flash-preview-free',
  'gpt-4.1-free',
  'gpt-4.1-mini-free',
  'gpt-4o-free',
  'glm-4.7-flash-free',
  'coding-glm-4.7-free',
  'step-3.5-flash-free',
  'coding-minimax-m2.1-free',
  'coding-glm-4.6-free',
  'coding-minimax-m2-free',
  'kimi-for-coding-free',
  'mimo-v2-flash-free'
];

async function checkAIHubMixModels() {
  console.log('喏，官家！开始检查AIHubMix官网新模型！\n');

  const browser = await chromium.launch({
    headless: false // 调试时可见
  });

  const page = await browser.newPage();

  try {
    // 访问AIHubMix官网
    console.log('访问AIHubMix官网...');
    await page.goto('https://aihubmix.com', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // 等待页面加载
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // 尝试找到模型列表页面
    console.log('查找模型列表...');

    // 尝试不同的可能路径
    const possibleUrls = [
      'https://aihubmix.com/models',
      'https://aihubmix.com/pricing',
      'https://aihubmix.com/docs',
      'https://aihubmix.com/api'
    ];

    let modelsPage = null;
    for (const url of possibleUrls) {
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
        await page.waitForTimeout(2000);
        const content = await page.content();
        if (content.includes('model') || content.includes('gpt') || content.includes('glm')) {
          modelsPage = url;
          console.log(`  找到模型页面: ${url}`);
          break;
        }
      } catch (error) {
        console.log(`  跳过: ${url}`);
      }
    }

    if (!modelsPage) {
      console.log('  未找到模型列表页面，停留在首页');
      await page.goto('https://aihubmix.com', { waitUntil: 'networkidle' });
    }

    // 截图保存
    const screenshotPath = './aihubmix-screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`  截图已保存: ${screenshotPath}`);

    // 提取页面文本内容
    const pageText = await page.evaluate(() => {
      return document.body.innerText;
    });

    // 保存页面文本
    const textPath = './aihubmix-page-text.txt';
    fs.writeFileSync(textPath, pageText);
    console.log(`  页面文本已保存: ${textPath}`);

    // 提取可能的模型名称
    const modelPatterns = [
      /gpt-[\d.]+(?:-free)?/gi,
      /glm-[\d.]+(?:-free)?/gi,
      /gemini-[\d.]+(?:-free)?/gi,
      /minimax-[\w]+(?:-free)?/gi,
      /coding-[\w-]+(?:-free)?/gi,
      /[\w-]+-free/gi
    ];

    const foundModels = new Set();
    modelPatterns.forEach(pattern => {
      const matches = pageText.match(pattern);
      if (matches) {
        matches.forEach(model => foundModels.add(model.toLowerCase()));
      }
    });

    const foundModelsList = Array.from(foundModels).sort();
    console.log(`\n发现 ${foundModelsList.length} 个可能的模型名称:`);
    foundModelsList.forEach(model => console.log(`  - ${model}`));

    // 对比现有配置
    const newModels = foundModelsList.filter(model =>
      !CONFIGURED_MODELS.includes(model) &&
      model.includes('-free') // 只关注免费模型
    );

    // 生成报告
    const report = {
      timestamp: new Date().toISOString(),
      foundModels: foundModelsList,
      configuredModels: CONFIGURED_MODELS,
      newModels: newModels,
      newModelsCount: newModels.length
    };

    const reportPath = './aihubmix-models-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n报告已保存: ${reportPath}`);

    // 输出结果
    console.log('\n' + '='.repeat(60));
    if (newModels.length > 0) {
      console.log('🎉 发现新模型！');
      console.log('新增免费模型:');
      newModels.forEach(model => console.log(`  ✨ ${model}`));
      console.log('\n请将新模型信息提供给AI Agent进行配置更新。');
    } else {
      console.log('✅ 未发现新模型，配置已是最新。');
    }
    console.log('='.repeat(60));

    return report;

  } catch (error) {
    console.error('检查失败:', error.message);
    console.log('\n可能的原因:');
    console.log('  1. 网站需要登录');
    console.log('  2. 页面结构变化');
    console.log('  3. 反爬机制');
    console.log('\n建议:');
    console.log('  - 手动访问官网查看新模型');
    console.log('  - 使用持久化Chrome Profile');
    console.log('  - 调整等待时间和选择器');

    // 保存错误截图
    try {
      await page.screenshot({ path: './aihubmix-error.png' });
      console.log('错误截图已保存: ./aihubmix-error.png');
    } catch (e) {
      console.log('截图失败');
    }

    return null;
  } finally {
    await browser.close();
  }
}

// 运行
checkAIHubMixModels().catch(console.error);
