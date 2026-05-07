/**
 * 微信公众号商贸主题草稿创建脚本
 * 
 * 功能：创建商贸转型主题的公众号草稿
 * 作者：小米椒 🌶️‍🔥
 * 版本：v1.6.0 (重试机制 + 配置参数化 + 增强日志)
 * 
 * 依赖：
 *   npm install
 * 
 * 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const { chromium } = require('playwright');

// ==================== 配置 ====================
const CONFIG = {
  // 封面图尺寸（微信标准 900×383）
  coverSize: { width: 900, height: 383 },
  
  // 超时设置（毫秒）
  timeout: {
    token: 10000,      // access_token 获取
    upload: 30000,     // 封面上传
    draft: 20000       // 草稿创建
  },
  
  // 重试设置
  retries: {
    maxAttempts: 3,     // 最大重试次数
    delayMs: 1000       // 重试延迟（递增）
  },
  
  // 浏览器设置
  browser: {
    headless: true,
    timeout: 60000
  },
  
  // 默认路径
  defaultCredentialsPath: './secrets/wechat-mp-credentials.json',
  defaultOutputDir: './output'
};

// Node.js 版本判断
const nodeVersion = process.version.match(/^v(\d+)/)[1];
const useNativeFetch = parseInt(nodeVersion) >= 18;

// 微信API错误码映射
const WECHAT_ERROR_CODES = {
  40001: 'AppSecret错误或AppSecret不属于这个公众号',
  40002: '不合法的凭证类型',
  40013: '不合法的AppID',
  40014: '不合法的access_token',
  41001: '缺少access_token参数',
  41002: '缺少appid参数',
  41004: '缺少secret参数',
  41006: '缺少media参数',
  41008: '缺少media_id参数',
  41010: '缺少content参数',
  41012: '缺少标题',
  42001: 'access_token超时',
  42007: '用户修改微信密码，access_token失效',
  43001: '需要GET请求',
  43002: '需要POST请求',
  43003: '需要HTTPS请求',
  44001: '多媒体文件为空',
  45001: '多媒体文件大小超过限制(10MB)',
  45002: '消息内容超过限制(60000字节)',
  45003: '标题字段超过限制',
  45004: '描述字段超过限制',
  45009: '接口调用超过限制',
  45011: 'API功能未被授权',
  46001: '不存在菜单数据',
  50001: '公众账号/小程序已经注册',
  50009: '系统内部异常'
};

// ==================== 工具函数 ====================

/**
 * 处理微信API错误
 */
function handleWechatError(errcode, errmsg) {
  const knownError = WECHAT_ERROR_CODES[errcode];
  if (knownError) {
    return `微信API错误 [${errcode}]: ${knownError} (${errmsg || '无详细描述'})`;
  }
  return `微信API错误 [${errcode}]: ${errmsg || '未知错误'}`;
}

/**
 * HTTP请求封装（兼容Node.js 18+原生fetch和node-fetch，带超时）
 */
async function httpRequest(url, options = {}) {
  const timeout = options.timeout || CONFIG.timeout.upload;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    if (useNativeFetch) {
      const response = await fetch(url, { ...options, signal: controller.signal });
      return response;
    } else {
      const nodeFetch = require('node-fetch');
      const response = await nodeFetch(url, { ...options, signal: controller.signal });
      return response;
    }
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * HTTP请求封装（带重试机制）
 */
async function httpRequestWithRetry(url, options = {}, retries = CONFIG.retries.maxAttempts) {
  const lastError = null;
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`  📡 请求中... (${attempt}/${retries})`);
      const response = await httpRequest(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response;
    } catch (error) {
      lastError = error;
      console.log(`  ⚠️ 请求失败: ${error.message}`);
      
      if (attempt < retries) {
        const delay = CONFIG.retries.delayMs * attempt;
        console.log(`  ⏳ ${delay/1000}秒后重试...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}

// ==================== 内容模板 ====================

const CONTENT_TEMPLATE = {
  cover: {
    title: '[标题]',
    subtitle: '[副标题]'
  },
  article: {
    title: '[文章标题]',
    author: '[作者名称]',
    digest: '[文章摘要]',
    content: '[文章正文HTML]'
  }
};

// ==================== 主函数 ====================

async function publishBusinessDraft(options = {}) {
  const {
    credentialsPath = CONFIG.defaultCredentialsPath,
    outputDir = CONFIG.defaultOutputDir
  } = options;

  console.log('🎯 开始创建商贸主题草稿...');
  console.log(`📦 Node.js: ${process.version} | Fetch: ${useNativeFetch ? '原生' : 'node-fetch'}`);
  
  const resolvedCredentialsPath = path.isAbsolute(credentialsPath) 
    ? credentialsPath 
    : path.resolve(process.cwd(), credentialsPath);
  
  if (!fs.existsSync(resolvedCredentialsPath)) {
    throw new Error(`凭证文件不存在: ${resolvedCredentialsPath}`);
  }
  
  const credentials = JSON.parse(fs.readFileSync(resolvedCredentialsPath, 'utf8'));
  
  if (!credentials.account || !credentials.account.appId || !credentials.account.appSecret) {
    throw new Error('凭证文件格式错误，缺少必要的字段');
  }
  
  const { appId, appSecret } = credentials.account;
  console.log(`🔐 AppID: ${appId.substring(0, 8)}****`);
  
  let browser;
  
  try {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    console.log(`\n🖼️ 生成商贸主题封面图 (${CONFIG.coverSize.width}×${CONFIG.coverSize.height})...`);
    browser = await chromium.launch({
      headless: CONFIG.browser.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
      timeout: CONFIG.browser.timeout
    });
    
    const context = await browser.newContext({ viewport: CONFIG.coverSize });
    const page = await context.newPage();
    
    const coverHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body { margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; }
          .container { text-align: center; color: white; padding: 40px; }
          h1 { font-size: 42px; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
          p { font-size: 20px; opacity: 0.9; }
          .emoji { font-size: 50px; margin-bottom: 15px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="emoji">📦</div>
          <h1>${CONTENT_TEMPLATE.cover.title}</h1>
          <p>${CONTENT_TEMPLATE.cover.subtitle}</p>
        </div>
      </body>
      </html>
    `;
    
    await page.setContent(coverHtml);
    const coverPath = path.join(outputDir, 'business-cover.png');
    await page.screenshot({ path: coverPath, fullPage: true });
    
    const fileSize = fs.statSync(coverPath).size;
    console.log(`✅ 封面图已保存: ${coverPath} (${(fileSize/1024).toFixed(1)} KB)`);
    
    await browser.close().catch(err => console.warn('浏览器关闭异常:', err.message));
    browser = null;
    console.log('🌐 浏览器已关闭');
    
    console.log('\n🔑 获取 access_token...');
    const tokenUrl = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
    console.log(`📡 API: token (超时: ${CONFIG.timeout.token/1000}s)`);
    
    const tokenResponse = await httpRequestWithRetry(tokenUrl, { timeout: CONFIG.timeout.token });
    const tokenData = await tokenResponse.json();
    
    if (!tokenData.access_token) {
      const errorMsg = handleWechatError(tokenData.errcode, tokenData.errmsg);
      throw new Error(`获取 access_token 失败: ${errorMsg}`);
    }
    
    const accessToken = tokenData.access_token;
    console.log(`✅ access_token 获取成功 (长度: ${accessToken.length})`);
    
    console.log(`\n📤 上传封面图...`);
    console.log(`📡 API: material/add_material (超时: ${CONFIG.timeout.upload/1000}s)`);
    const uploadUrl = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;
    
    const form = new FormData();
    form.append('media', fs.createReadStream(coverPath), {
      filename: 'business-cover.png',
      contentType: 'image/png'
    });
    
    const uploadResponse = await httpRequestWithRetry(uploadUrl, {
      method: 'POST',
      body: form,
      headers: form.getHeaders(),
      timeout: CONFIG.timeout.upload
    });
    
    const uploadData = await uploadResponse.json();
    
    if (uploadData.media_id) {
      console.log(`✅ 封面上传成功! Media ID: ${uploadData.media_id.substring(0, 8)}****`);
      
      console.log(`\n📤 创建草稿文章...`);
      console.log(`📡 API: draft/add (超时: ${CONFIG.timeout.draft/1000}s)`);
      const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
      
      const articleData = {
        articles: [{
          title: CONTENT_TEMPLATE.article.title,
          thumb_media_id: uploadData.media_id,
          author: CONTENT_TEMPLATE.article.author,
          digest: CONTENT_TEMPLATE.article.digest,
          content: CONTENT_TEMPLATE.article.content,
          content_source_url: '',
          need_open_comment: 1,
          only_fans_can_comment: 0
        }]
      };
      
      const draftResponse = await httpRequestWithRetry(draftUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(articleData),
        timeout: CONFIG.timeout.draft
      });
      
      const draftData = await draftResponse.json();
      
      if (draftData.media_id) {
        console.log(`✅ 草稿创建成功!`);
        console.log(`📄 Media ID: ${draftData.media_id.substring(0, 8)}****`);
        console.log(`🔗 链接: https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftData.media_id}&token=&lang=zh_CN`);
        console.log(`\n📝 请到公众号后台「草稿箱」查看并完善内容`);
        
        return { 
          success: true, 
          message: '商贸主题草稿创建成功',
          mediaId: draftData.media_id,
          draftUrl: `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftData.media_id}&token=&lang=zh_CN`
        };
      } else {
        const errorMsg = handleWechatError(draftData.errcode, draftData.errmsg);
        console.error(`❌ 草稿创建失败: ${errorMsg}`);
        return { success: false, message: errorMsg };
      }
    } else {
      const errorMsg = handleWechatError(uploadData.errcode, uploadData.errmsg);
      console.error(`❌ 封面上传失败: ${errorMsg}`);
      return { success: false, message: errorMsg };
    }
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close().catch(err => console.warn('浏览器关闭异常:', err.message));
      console.log('🌐 浏览器已关闭');
    }
  }
}

// ==================== 入口 ====================

async function main() {
  const args = process.argv.slice(2);
  const options = {
    credentialsPath: args[0] || CONFIG.defaultCredentialsPath,
    outputDir: args[1] || CONFIG.defaultOutputDir
  };
  
  const result = await publishBusinessDraft(options);
  
  console.log('\n=== 商贸草稿创建结果 ===');
  console.log(JSON.stringify(result, null, 2));
  
  if (result.success) {
    console.log('\n🎉 商贸主题公众号草稿创建成功!');
    console.log('📱 请前往公众号后台查看草稿箱');
  } else {
    console.log('\n❌ 商贸草稿创建失败，请检查错误信息并重试');
  }
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { publishBusinessDraft, CONTENT_TEMPLATE, CONFIG, WECHAT_ERROR_CODES, handleWechatError };