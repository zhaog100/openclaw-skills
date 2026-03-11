/**
 * Moltbook自动检查脚本
 * 使用API和Puppeteer双重方案
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 加载凭证
const credentialsPath = path.join(__dirname, '../.moltbook/credentials.json');
const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));

const API_KEY = credentials.api_key;
const AGENT_ID = credentials.agent_id;
const PROFILE_URL = credentials.profile_url;

console.log('喏，官家！开始Moltbook自动检查！\n');
console.log('Agent:', credentials.agent_name);
console.log('ID:', AGENT_ID);
console.log('API Key:', API_KEY.substring(0, 20) + '...');
console.log('');

// ============================================
// 方法1: 尝试API访问
// ============================================

async function tryAPIAccess() {
  console.log('📝 方法1: 尝试API访问...\n');

  const endpoints = [
    {
      name: 'Home API',
      url: 'https://www.moltbook.com/api/v1/home',
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    },
    {
      name: 'Agent Profile API',
      url: `https://www.moltbook.com/api/v1/agents/${AGENT_ID}`,
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    },
    {
      name: 'Notifications API',
      url: 'https://www.moltbook.com/api/v1/notifications',
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    }
  ];

  for (const endpoint of endpoints) {
    console.log(`尝试: ${endpoint.name}`);
    console.log(`URL: ${endpoint.url}`);

    try {
      const result = await makeRequest(endpoint.url, endpoint.headers);
      console.log('✅ 成功！');
      console.log(JSON.stringify(result, null, 2));
      return result;
    } catch (error) {
      console.log(`❌ 失败: ${error.message}`);
    }
    console.log('');
  }

  return null;
}

// ============================================
// 方法2: 使用Puppeteer爬取
// ============================================

async function scrapeWithPuppeteer() {
  console.log('\n📝 方法2: 使用Puppeteer爬取...\n');

  try {
    const puppeteer = require('puppeteer');

    const browser = await puppeteer.launch({
      headless: 'new'
    });

    const page = await browser.newPage();

    // 访问个人主页
    console.log('访问:', PROFILE_URL);
    await page.goto(PROFILE_URL, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 等待页面加载
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 提取信息
    const data = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        // 尝试提取排名
        ranking: document.querySelector('[class*="ranking"]')?.textContent || '未找到',
        // 尝试提取评论数
        comments: document.querySelector('[class*="comment"]')?.textContent || '未找到',
        // 尝试提取通知
        notifications: document.querySelector('[class*="notification"]')?.textContent || '未找到',
        // 页面文本（用于调试）
        pageText: document.body.innerText.substring(0, 500)
      };
    });

    console.log('\n✅ 爬取成功！');
    console.log('页面标题:', data.title);
    console.log('排名:', data.ranking);
    console.log('评论:', data.comments);
    console.log('通知:', data.notifications);
    console.log('\n页面预览:');
    console.log(data.pageText);

    // 截图
    const screenshotPath = './moltbook-check.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`\n📸 截图已保存: ${screenshotPath}`);

    await browser.close();

    return data;

  } catch (error) {
    console.log('❌ Puppeteer爬取失败:', error.message);
    return null;
  }
}

// ============================================
// 辅助函数
// ============================================

function makeRequest(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);

    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ...headers
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve({ raw: data });
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('请求超时'));
    });

    req.end();
  });
}

// ============================================
// 主函数
// ============================================

async function main() {
  console.log('='.repeat(60));
  console.log('Moltbook自动检查');
  console.log('='.repeat(60));
  console.log('');

  // 尝试方法1: API
  let result = await tryAPIAccess();

  // 如果API失败，尝试方法2: Puppeteer
  if (!result) {
    result = await scrapeWithPuppeteer();
  }

  // 生成报告
  if (result) {
    const report = {
      timestamp: new Date().toISOString(),
      agent: credentials.agent_name,
      agent_id: AGENT_ID,
      data: result,
      status: 'success'
    };

    const reportPath = './moltbook-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n✅ 报告已保存: ${reportPath}`);
  } else {
    console.log('\n❌ 所有方法都失败，需要手动检查');
    console.log('\n手动检查链接:', PROFILE_URL);
  }

  console.log('\n' + '='.repeat(60));
  console.log('检查完成');
  console.log('='.repeat(60));
}

// 运行
main().catch(console.error);
