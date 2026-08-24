/*
京东黑色星期五自动抢券脚本 v1.0.1
兼容青龙面板 2.21 (Qinglong Panel)
依赖: got tough-cookie (青龙面板已安装)

环境变量优先级:
1. process.env.JD_COOKIE
2. /ql/data/config/config.sh 或 /ql/config/config.sh
3. /ql/data/env.sh 或 /ql/env.sh
4. 青龙 API (通过 QL_URL 配置) 自动读取

青龙面板配置 (可选):
- QL_URL: 青龙面板地址 (默认 http://localhost:5700)
- QL_USER: 青龙管理员用户名 (默认 admin)
- QL_PASS: 青龙管理员密码 (默认 admin)

cron: 0 20 * * 4 (每周四 20:00)
*/

const got = require('got');
const fs = require('fs');

const COUPON_API_BASE = 'https://api.m.jd.com/client.action';

const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Origin': 'https://pro.m.jd.com',
  'Referer': 'https://pro.m.jd.com/',
  'X-Requested-With': 'com.jingdong.app.mall',
  'Connection': 'keep-alive',
};

// ⚠️ 这些 ID 需要根据实际活动更新
const BLACK_FRIDAY_COUPONS = [
  { couponId: '755461154191', name: '满300减30 平台补贴券' },
  { couponId: '755461154195', name: '满300减30 平台补贴券' },
  { couponId: '755461154199', name: '满300减30 平台补贴券' },
];

function log(level, msg) {
  const ts = new Date().toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'});
  console.log(`[${ts}] [${level}] ${msg}`);
}

function getJDCookies() {
  let envValue = process.env.JD_COOKIE || '';
  
  // Fallback 1: 读取配置文件
  if (!envValue) {
    const paths = ['/ql/data/config/config.sh', '/ql/config/config.sh'];
    for (const p of paths) {
      try {
        if (fs.existsSync(p)) {
          const content = fs.readFileSync(p, 'utf-8');
          const m = content.match(/export\s+JD_COOKIE\s*=\s*["']?([^"'\n]+?)["']?\s*$/m);
          if (m) { envValue = m[1]; break; }
        }
      } catch(e) {}
    }
  }
  
  // Fallback 2: 读取 env.sh
  if (!envValue) {
    const paths = ['/ql/data/env.sh', '/ql/env.sh'];
    for (const p of paths) {
      try {
        if (fs.existsSync(p)) {
          const content = fs.readFileSync(p, 'utf-8');
          const m = content.match(/export\s+JD_COOKIE\s*=\s*["']?([^"'\n]+?)["']?\s*$/m);
          if (m) { envValue = m[1]; break; }
        }
      } catch(e) {}
    }
  }
  
  // Fallback 3: 通过青龙 API 读取（青龙 2.21 推荐方式）
  if (!envValue) {
    try {
      const qlHost = process.env.QL_URL || 'http://localhost:5700';
      const qlUser = process.env.QL_USER || 'admin';
      const qlPass = process.env.QL_PASS || 'admin';
      
      log('INFO', `尝试通过青龙 API 获取 cookie (${qlHost})`);
      
      // 登录获取 token
      const loginResp = got.post(`${qlHost}/api/user/login`, {
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: qlUser, password: qlPass }),
        timeout: 5000,
      });
      const loginData = JSON.parse(loginResp.body);
      
      if (loginData.code === 200 && loginData.data?.token) {
        const token = loginData.data.token;
        
        // 读取环境变量
        const envResp = got.get(`${qlHost}/api/env/list`, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 5000,
        });
        const envData = JSON.parse(envResp.body);
        
        if (envData.code === 200 && envData.data?.data) {
          const cookies = envData.data.data.filter(i => i.name === 'JD_COOKIE' && i.status === 0);
          if (cookies.length > 0) {
            envValue = cookies.map(c => c.value).join('\n');
            log('INFO', `从青龙 API 读取到 ${cookies.length} 个 JD_COOKIE`);
          }
        }
      } else {
        log('WARN', `青龙登录失败: code=${loginData.code}`);
      }
    } catch(e) {
      log('WARN', `青龙 API 读取失败: ${e.message}`);
    }
  }
  
  if (!envValue) {
    log('ERROR', '未找到 JD_COOKIE');
    return [];
  }
  
  return parseCookies(envValue);
}

function parseCookies(envValue) {
  const cookies = [];
  for (const line of envValue.trim().split('\n')) {
    const trimmed = line.trim().replace(/\s*;\s*/g, ';');
    if (!trimmed) continue;
    // 兼容 pt_key=xxx;pt_pin=xxx 格式
    if (trimmed.includes('pt_key=') && trimmed.includes('pt_pin=')) {
      cookies.push(trimmed);
    }
  }
  return cookies;
}

async function fetchCoupon(cookie, couponInfo) {
  const params = new URLSearchParams({
    functionId: 'claimCoupon',
    body: JSON.stringify({
      couponId: couponInfo.couponId,
      couponType: 0,
    }),
    client: 'apple',
    clientVersion: '15.0.0',
    brand: 'apple',
    uuid: 'test_uuid_' + Math.random().toString(36).slice(2, 10),
  });
  
  try {
    const resp = await got.get(`${COUPON_API_BASE}?${params.toString()}`, {
      headers: {
        ...DEFAULT_HEADERS,
        'Cookie': cookie,
      },
      timeout: 10000,
    });
    
    const data = JSON.parse(resp.body);
    const success = data.code === 0 || data.message === 'success' || data.success;
    
    if (success) {
      log('SUCCESS', `${couponInfo.name}: 抢券成功!`);
    } else {
      log('WARN', `${couponInfo.name}: ${data.message || JSON.stringify(data)}`);
    }
    
    return { success, cookie, coupon: couponInfo.name, data };
  } catch(e) {
    log('ERROR', `${couponInfo.name}: 请求失败 - ${e.message}`);
    return { success: false, cookie, coupon: couponInfo.name, error: e.message };
  }
}

async function main() {
  log('INFO', '🖤 京东黑色星期五自动抢券 v1.0.1');
  log('INFO', '⏰ ' + new Date().toLocaleString('zh-CN', {timeZone: 'Asia/Shanghai'}));
  
  const cookies = getJDCookies();
  if (!cookies.length) {
    log('ERROR', '未找到有效 JD_COOKIE');
    process.exit(1);
  }
  
  log('INFO', `找到 ${cookies.length} 个账号`);
  
  const all = [];
  for (let i = 0; i < cookies.length; i++) {
    for (const coupon of BLACK_FRIDAY_COUPONS) {
      all.push(fetchCoupon(cookies[i], coupon));
    }
    if (i < cookies.length - 1) await new Promise(r => setTimeout(r, 2000));
  }
  
  const results = await Promise.all(all);
  const ok = results.filter(r => r.success).length;
  log('INFO', `完成: ${ok}/${results.length} 张成功`);
  
  process.exit(ok > 0 ? 0 : 1);
}

main().catch(e => { log('ERROR', e.message); process.exit(1); });

// MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
