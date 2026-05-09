#!/usr/bin/env node
/**
 * 京东待评价商品获取工具 v1.0
 * 使用Playwright浏览器自动化
 */
const { chromium } = require('playwright');
const fs = require('fs');

async function getPendingOrders(cookie, username) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`账号: ${username}`);
  console.log('='.repeat(60));
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    // 完整的浏览器headers
    extraHTTPHeaders: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Sec-Fetch-User': '?1',
      'Cache-Control': 'max-age=0'
    }
  });
  
  // 设置Cookie
  const cookies = [];
  cookie.split(';').forEach(c => {
    const [name, ...values] = c.trim().split('=');
    if (name && values.length > 0) {
      cookies.push({
        name: name.trim(),
        value: values.join('=').trim(),
        domain: '.jd.com',
        path: '/'
      });
    }
  });
  
  await context.addCookies(cookies);
  console.log('✅ Cookie已设置');
  
  const page = await context.newPage();
  
  // 注入强化的反检测脚本
  await page.addInitScript(() => {
    // 隐藏webdriver属性
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    });
    
    // 模拟真实的plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
        { name: 'Native Client', filename: 'internal-nacl-plugin' }
      ]
    });
    
    // 模拟真实的languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en-US', 'en']
    });
    
    // 模拟真实的platform
    Object.defineProperty(navigator, 'platform', {
      get: () => 'Win32'
    });
    
    // 隐藏自动化特征
    window.chrome = {
      runtime: {}
    };
    
    // 覆盖permissions查询
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  });
  
  try {
    // 先访问京东首页建立session
    console.log('🏠 访问京东首页...');
    await page.goto('https://www.jd.com', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    await page.waitForTimeout(2000);
    console.log('✅ 首页加载完成');
    
    // 再访问订单页面
    console.log('📱 访问订单页面...');
    await page.goto('https://order.jd.com/center/list.action', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    await page.waitForTimeout(5000); // 增加等待时间
    
    // 截图保存当前页面
    const screenshotPath = `/tmp/jd_page_${username}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 页面截图: ${screenshotPath}`);
    
    // 检查登录状态（更严格）
    const currentUrl = page.url();
    console.log(`📍 当前URL: ${currentUrl}`);
    
    // 检查是否被重定向到登录页
    if (currentUrl.includes('passport.jd.com') || currentUrl.includes('login')) {
      console.log('❌ 未登录或Cookie已过期（被重定向到登录页）');
      console.log('💡 建议: 重新获取Cookie');
      await browser.close();
      return [];
    }
    
    // 检查是否有登录按钮
    const loginBtn = await page.$('a[href*="login"], .login-btn, [class*="login"]');
    if (loginBtn) {
      const btnText = await loginBtn.textContent();
      if (btnText && btnText.includes('登录')) {
        console.log('❌ 未登录或Cookie已过期（检测到登录按钮）');
        console.log('💡 建议: 重新获取Cookie');
        await browser.close();
        return [];
      }
    }
    
    // 检查用户名显示
    const usernameEl = await page.$('[class*="username"], [class*="user-name"], .nickname');
    if (usernameEl) {
      const displayName = await usernameEl.textContent();
      console.log(`✅ 登录成功: ${displayName.trim()}`);
    } else {
      console.log('✅ 登录成功');
    }
    
    // 点击"待评价"标签
    console.log('🔍 查找待评价订单...');
    const pendingTab = await page.$('text=待评价');
    if (pendingTab) {
      await pendingTab.click();
      await page.waitForTimeout(3000);
    }
    
    // 获取订单列表（多种选择器尝试）
    const orders = await page.evaluate(() => {
      const items = [];
      
      // 尝试多种选择器
      const selectors = [
        '.order-tb tbody tr',
        '.order-list .order-item',
        '.order-detail',
        '[class*="order"]',
        'tr[data-orderid]'
      ];
      
      let orderElements = [];
      for (const selector of selectors) {
        orderElements = Array.from(document.querySelectorAll(selector));
        if (orderElements.length > 0) {
          console.log(`使用选择器: ${selector}, 找到 ${orderElements.length} 个元素`);
          break;
        }
      }
      
      orderElements.forEach(order => {
        // 尝试多种方式提取信息
        const nameEl = order.querySelector('[class*="name"] a, .p-name a, a[href*="item"], .goods-name, .product-name');
        const priceEl = order.querySelector('[class*="price"], .p-price, .goods-price');
        const idEl = order.querySelector('[data-orderid], [class*="orderid"], .order-number');
        const statusEl = order.querySelector('[class*="status"], .order-status');
        
        if (nameEl) {
          items.push({
            name: nameEl.textContent.trim(),
            price: priceEl ? priceEl.textContent.trim() : '未知',
            order_id: idEl ? (idEl.getAttribute('data-orderid') || idEl.textContent.trim()) : '未知',
            status: statusEl ? statusEl.textContent.trim() : '待评价',
            url: nameEl.href || ''
          });
        }
      });
      
      // 如果没找到，尝试提取整个页面文本
      if (items.length === 0) {
        const pageText = document.body.innerText;
        if (pageText.includes('待评价') || pageText.includes('订单')) {
          items.push({
            name: '页面包含订单信息（需要进一步解析）',
            price: '未知',
            order_id: '未知',
            status: '需要手动查看',
            url: window.location.href
          });
        }
      }
      
      return items;
    });
    
    if (orders.length > 0) {
      console.log(`\n✅ 找到 ${orders.length} 个待评价商品:\n`);
      orders.forEach((item, i) => {
        console.log(`${i + 1}. ${item.name}`);
        console.log(`   价格: ${item.price}`);
        console.log(`   订单号: ${item.order_id}`);
        if (item.url) {
          console.log(`   链接: ${item.url}`);
        }
        console.log();
      });
    } else {
      console.log('\n✅ 当前没有待评价商品');
      
      // 截图用于调试
      const screenshot = `/tmp/jd_orders_${username}.png`;
      await page.screenshot({ path: screenshot, fullPage: true });
      console.log(`📸 已保存截图: ${screenshot}`);
    }
    
    await browser.close();
    return orders;
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    
    // 截图用于调试
    const screenshot = `/tmp/jd_error_${username}.png`;
    try {
      await page.screenshot({ path: screenshot, fullPage: true });
      console.log(`📸 已保存错误截图: ${screenshot}`);
    } catch (e) {}
    
    await browser.close();
    return [];
  }
}

async function main() {
  console.log('📦 京东待评价商品获取工具 v1.0');
  console.log('='.repeat(60));
  
  // 读取Cookie
  const envFile = '/root/.openclaw/workspace/qinglong/config/env.sh';
  const envContent = fs.readFileSync(envFile, 'utf8');
  const match = envContent.match(/export JD_COOKIE="([^"]+)"/);
  
  if (!match) {
    console.log('❌ 未找到JD_COOKIE');
    return;
  }
  
  const cookie = match[1];
  const accounts = cookie.split('&');
  
  console.log(`✅ 成功加载京东Cookie`);
  console.log(`👥 检测到 ${accounts.length} 个账号`);
  
  let totalOrders = 0;
  
  for (const account of accounts) {
    const pinMatch = account.match(/pt_pin=([^;]+)/);
    if (pinMatch) {
      const orders = await getPendingOrders(account, pinMatch[1]);
      totalOrders += orders.length;
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log(`✅ 完成! 总共找到 ${totalOrders} 个待评价商品`);
  console.log('='.repeat(60));
}

main().catch(console.error);
