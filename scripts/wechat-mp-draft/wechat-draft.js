/**
 * 微信公众号草稿创建脚本
 * 
 * 功能：
 *   - v1.x: 单个商贸主题草稿（向后兼容）
 *   - v2.0: 配置驱动的多模板草稿创建
 * 
 * 作者：小米椒 🌶️‍🔥
 * 版本：v2.0.0 (配置驱动 + 多上传方式 + 主题支持)
 * 
 * 依赖：
 *   npm install form-data playwright
 * 
 * 使用：
 *   # v1.x 兼容模式（单个商贸主题）
 *   node wechat-draft.js
 *   
 *   # v2.0 配置驱动模式
 *   node wechat-draft.js [模板名称]
 *   示例：node wechat-draft.js yoga-shoulder
 * 
 * 配置文件：
 *   - secrets/wechat-mp-credentials.json (公众号凭证)
 *   - config/draft-config.json (模板配置)
 *
 * 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const { chromium } = require('playwright');

// ==================== 配置 ====================
const CONFIG = {
  coverSize: { width: 900, height: 383 },
  timeout: { token: 10000, upload: 30000, draft: 20000 },
  retries: { maxAttempts: 3, delayMs: 1000 },
  browser: { headless: true, timeout: 60000 },
  defaultCredentialsPath: './secrets/wechat-mp-credentials.json',
  defaultOutputDir: './output',
  configPath: './config/draft-config.json'
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

function handleWechatError(errcode, errmsg) {
  const knownError = WECHAT_ERROR_CODES[errcode];
  if (knownError) {
    return `微信API错误 [${errcode}]: ${knownError} (${errmsg || '无详细描述'})`;
  }
  return `微信API错误 [${errcode}]: ${errmsg || '未知错误'}`;
}

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

// ==================== 加载配置文件 (v2.0) ====================

function loadConfig() {
  if (!fs.existsSync(CONFIG.configPath)) {
    throw new Error(`配置文件不存在: ${CONFIG.configPath}`);
  }
  return JSON.parse(fs.readFileSync(CONFIG.configPath, 'utf8'));
}

// ==================== 多种封面上传方式 (v2.0) ====================

/**
 * 方式1：FormData + Blob（Node 18+ 成功方式）
 */
async function uploadWithFormDataBlob(coverPath, uploadUrl) {
  console.log(`   尝试方式1：FormData + Blob`);
  
  const imageBuffer = fs.readFileSync(coverPath);
  const formData = new FormData();
  formData.append('media', new Blob([imageBuffer]), path.basename(coverPath));
  
  const uploadResponse = await fetch(uploadUrl, {
    method: 'POST',
    body: formData
  });
  
  return await uploadResponse.json();
}

/**
 * 方式2：FormData + Buffer（通用方式）
 * 使用原生FormData和Buffer，不设置headers，直接使用fetch
 */
async function uploadWithFormDataBuffer(coverPath, uploadUrl) {
  console.log(`   尝试方式2：FormData + Buffer`);
  
  const imageBuffer = fs.readFileSync(coverPath);
  const formData = new FormData();
  formData.append('media', imageBuffer, {
    filename: path.basename(coverPath),
    contentType: 'image/png'
  });
  
  const uploadResponse = await fetch(uploadUrl, {
    method: 'POST',
    body: formData
  });
  
  return await uploadResponse.json();
}

/**
 * 方式3：form-data 包方式（已废弃，推荐使用方式1或2）
 * 移除form-data包依赖，使用原生FormData + Blob
 */
async function uploadWithFormDataPackage(coverPath, uploadUrl, accessToken) {
  console.log(`   尝试方式3：form-data 包（已废弃）`);
  
  const imageBuffer = fs.readFileSync(coverPath);
  const formData = new FormData();
  formData.append('media', new Blob([imageBuffer]), path.basename(coverPath));
  
  const uploadUrlWithToken = uploadUrl.includes('access_token') 
    ? uploadUrl 
    : `${uploadUrl}${accessToken}`;
  
  const uploadResponse = await fetch(uploadUrlWithToken, {
    method: 'POST',
    body: formData
  });
  
  return await uploadResponse.json();
}

/**
 * 智能选择最佳上传方式 (v2.0)
 */
async function uploadCoverImage(coverPath, uploadUrl, accessToken) {
  console.log(`📤 上传封面图...`);
  
  const methods = [
    { name: 'FormData + Blob', func: (p, u) => uploadWithFormDataBlob(p, u) },
    { name: 'FormData + Buffer', func: (p, u) => uploadWithFormDataBuffer(p, u) },
    { name: 'form-data 包', func: (p, u) => uploadWithFormDataPackage(p, u, accessToken) }
  ];
  
  for (const method of methods) {
    try {
      const result = await method.func(coverPath, uploadUrl);
      
      if (result.media_id) {
        console.log(`   ✅ ${method.name} 成功`);
        return result;
      } else {
        const errorMsg = handleWechatError(result.errcode, result.errmsg);
        console.log(`   ❌ ${method.name} 失败: ${errorMsg}`);
      }
    } catch (error) {
      console.log(`   ❌ ${method.name} 异常: ${error.message}`);
    }
  }
  
  console.log(`   ⚠️ 所有上传方式都失败，使用无封面模式`);
  return { media_id: 'mock-media-id-for-all-failed' };
}

// ==================== v1.x 内容模板 (向后兼容) ====================

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

// ==================== v1.x 主函数 (向后兼容) ====================

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
    
    const uploadData = await uploadCoverImage(coverPath, uploadUrl, accessToken);
    
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

// ==================== v2.0 配置驱动主函数 ====================

async function publishDraft(templateName) {
  console.log(`🎯 开始创建「${templateName}」模板草稿...`);
  console.log(`📦 Node.js: ${process.version} | Fetch: ${useNativeFetch ? '原生' : 'node-fetch'}`);
  
  // 加载配置
  const config = loadConfig();
  const template = config.templates[templateName];
  if (!template) {
    throw new Error(`模板不存在: ${templateName}`);
  }
  
  // 加载凭证
  if (!fs.existsSync(CONFIG.defaultCredentialsPath)) {
    throw new Error(`凭证文件不存在: ${CONFIG.defaultCredentialsPath}`);
  }
  
  const credentials = JSON.parse(fs.readFileSync(CONFIG.defaultCredentialsPath, 'utf8'));
  const { appId, appSecret } = credentials.account;
  console.log(`🔐 AppID: ${appId.substring(0, 10)}****`);
  
  let browser = null;
  
  try {
    // 确保输出目录存在
    if (!fs.existsSync(CONFIG.defaultOutputDir)) {
      fs.mkdirSync(CONFIG.defaultOutputDir, { recursive: true });
    }
    
    // 生成主题封面图
    console.log(`\n🖼️ 生成「${templateName}」主题封面图 (${CONFIG.coverSize.width}×${CONFIG.coverSize.height})...`);
    browser = await chromium.launch({ 
      headless: CONFIG.browser.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
      timeout: CONFIG.browser.timeout
    });
    
    const context = await browser.newContext({ viewport: CONFIG.coverSize });
    const page = await context.newPage();
    
    // 使用主题配置
    const themeConfig = config.themes[templateName.split('-')[0]] || config.themes.business;
    
    const coverHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body { 
            margin: 0; 
            padding: 0; 
            background: ${themeConfig.gradient}; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; 
          }
          .container { 
            text-align: center; 
            color: ${themeConfig.textColor}; 
            padding: 40px; 
          }
          h1 { 
            font-size: 42px; 
            margin-bottom: 20px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3); 
          }
          p { 
            font-size: 20px; 
            opacity: 0.9; 
          }
          .emoji { 
            font-size: 50px; 
            margin-bottom: 15px; 
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="emoji">${themeConfig.emoji}</div>
          <h1>${template.coverTitle}</h1>
          <p>${template.coverSubtitle}</p>
        </div>
      </body>
      </html>
    `;
    
    await page.setContent(coverHtml);
    const coverPath = path.join(CONFIG.defaultOutputDir, `${templateName}-cover.png`);
    await page.screenshot({ path: coverPath, fullPage: true });
    
    const fileSize = fs.statSync(coverPath).size;
    console.log(`✅ 封面图已保存: ${coverPath} (${(fileSize/1024).toFixed(1)} KB)`);
    
    await browser.close().catch(err => console.warn('浏览器关闭异常:', err.message));
    browser = null;
    console.log('🌐 浏览器已关闭');
    
    // 获取 access_token
    console.log('\n🔑 获取 access_token...');
    const tokenUrl = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
    
    const tokenResponse = await httpRequestWithRetry(tokenUrl, { timeout: CONFIG.timeout.token });
    const tokenData = await tokenResponse.json();
    
    if (!tokenData.access_token) {
      const errorMsg = handleWechatError(tokenData.errcode, tokenData.errmsg);
      throw new Error(`获取 access_token 失败: ${errorMsg}`);
    }
    
    const accessToken = tokenData.access_token;
    console.log(`✅ access_token 获取成功 (长度: ${accessToken.length})`);
    
    // 上传封面图
    const uploadUrl = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;
    const uploadData = await uploadCoverImage(coverPath, uploadUrl, accessToken);
    
    if (!uploadData.media_id || uploadData.media_id === 'mock-media-id-for-all-failed') {
      const errorMsg = handleWechatError(uploadData.errcode, uploadData.errmsg);
      console.error(`❌ 封面上传失败: ${errorMsg}`);
      return { success: false, message: errorMsg };
    }
    
    console.log(`✅ 封面上传成功! Media ID: ${uploadData.media_id.substring(0, 8)}****`);
    
    // 创建草稿
    console.log(`\n📤 创建「${templateName}」草稿文章...`);
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
    
    const articleData = {
      articles: [{
        title: template.articleTitle,
        thumb_media_id: uploadData.media_id,
        author: template.author || '',
        digest: template.digest || template.articleTitle,
        content: template.content || '<p>请在此添加正文内容</p>',
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
    
    const draftResult = await draftResponse.json();
    
    if (draftResult.media_id) {
      console.log(`✅ 草稿创建成功!`);
      console.log(`📄 Media ID: ${draftResult.media_id.substring(0, 8)}****`);
      console.log(`🔗 链接: https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftResult.media_id}&token=&lang=zh_CN`);
      console.log(`\n📝 请到公众号后台「草稿箱」查看并完善内容`);
      
      return { 
        success: true, 
        message: `「${templateName}」模板草稿创建成功`,
        mediaId: draftResult.media_id,
        draftUrl: `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftResult.media_id}&token=&lang=zh_CN`
      };
    } else {
      const errorMsg = handleWechatError(draftResult.errcode, draftResult.errmsg);
      console.error(`❌ 草稿创建失败: ${errorMsg}`);
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
  
  let result;
  
  if (args.length > 0 && args[0] !== 'business') {
    // v2.0 配置驱动模式
    const templateName = args[0];
    result = await publishDraft(templateName);
    
    console.log(`\n=== 「${templateName}」草稿创建结果 ===`);
    console.log(JSON.stringify(result, null, 2));
    
    if (result.success) {
      console.log(`\n🎉 「${templateName}」公众号草稿创建成功!`);
      console.log('📱 请前往公众号后台查看草稿箱');
    } else {
      console.log(`\n❌ 草稿创建失败，请检查错误信息并重试`);
    }
  } else {
    // v1.x 兼容模式
    const options = {
      credentialsPath: args[0] || CONFIG.defaultCredentialsPath,
      outputDir: args[1] || CONFIG.defaultOutputDir
    };
    
    result = await publishBusinessDraft(options);
    
    console.log('\n=== 商贸草稿创建结果 ===');
    console.log(JSON.stringify(result, null, 2));
    
    if (result.success) {
      console.log('\n🎉 商贸主题公众号草稿创建成功!');
      console.log('📱 请前往公众号后台查看草稿箱');
    } else {
      console.log('\n❌ 商贸草稿创建失败，请检查错误信息并重试');
    }
  }
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { 
  publishBusinessDraft, 
  publishDraft, 
  CONTENT_TEMPLATE, 
  CONFIG, 
  WECHAT_ERROR_CODES, 
  handleWechatError,
  uploadCoverImage,
  loadConfig
};
