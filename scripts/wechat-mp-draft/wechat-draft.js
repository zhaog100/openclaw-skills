/**
 * 微信公众号商贸主题草稿创建脚本
 * 
 * 功能：创建商贸转型主题的公众号草稿
 * 作者：小米椒 🌶️‍🔥
 * 版本：v1.4.0 (微信API错误码处理 + FormData兼容性)
 * 
 * 依赖：
 *   npm install playwright form-data node-fetch
 * 
 * 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const { chromium } = require('playwright');

// Node.js 版本判断
const nodeVersion = process.version.match(/^v(\d+)/)[1];
const useNativeFetch = parseInt(nodeVersion) >= 18;

// 微信API错误码映射（常见错误）
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

/**
 * 处理微信API错误
 * @param {number} errcode - 错误码
 * @param {string} errmsg - 错误信息
 * @returns {string} 格式化的错误描述
 */
function handleWechatError(errcode, errmsg) {
  const knownError = WECHAT_ERROR_CODES[errcode];
  if (knownError) {
    return `微信API错误 [${errcode}]: ${knownError} (${errmsg || '无详细描述'})`;
  }
  return `微信API错误 [${errcode}]: ${errmsg || '未知错误'}`;
}

/**
 * HTTP请求封装（兼容Node.js 18+原生fetch和node-fetch）
 */
async function httpRequest(url, options = {}) {
  if (useNativeFetch) {
    const response = await fetch(url, options);
    return response;
  } else {
    const nodeFetch = require('node-fetch');
    const response = await nodeFetch(url, options);
    return response;
  }
}

// 内容模板（具体文案需用户填充）
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

async function publishBusinessDraft(options = {}) {
  const {
    credentialsPath = './secrets/wechat-mp-credentials.json',
    outputDir = './output'
  } = options;

  console.log('🎯 开始创建商贸主题草稿...');
  console.log(`📦 Node.js 版本: ${process.version}`);
  
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
    
    console.log('🖼️ 生成商贸主题封面图...');
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
      timeout: 60000
    });
    
    const context = await browser.newContext({ viewport: { width: 900, height: 500 } });
    const page = await context.newPage();
    
    const coverHtml = \`
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
          <h1>\${CONTENT_TEMPLATE.cover.title}</h1>
          <p>\${CONTENT_TEMPLATE.cover.subtitle}</p>
        </div>
      </body>
      </html>
    \`;
    
    await page.setContent(coverHtml);
    const coverPath = path.join(outputDir, 'business-cover.png');
    await page.screenshot({ path: coverPath, fullPage: true });
    console.log(\`🖼️ 商贸封面图已保存：\${coverPath}\`);
    
    await browser.close();
    console.log('🌐 浏览器已关闭');
    
    console.log('🔑 获取 access_token...');
    const tokenUrl = \`https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=\${appId}&secret=\${appSecret}\`;
    
    const tokenResponse = await httpRequest(tokenUrl);
    const tokenData = await tokenResponse.json();
    
    if (!tokenData.access_token) {
      const errorMsg = handleWechatError(tokenData.errcode, tokenData.errmsg);
      throw new Error(\`获取 access_token 失败: \${errorMsg}\`);
    }
    
    const accessToken = tokenData.access_token;
    console.log('✅ access_token 获取成功');
    
    console.log('📤 上传商贸主题封面图...');
    const uploadUrl = \`https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=\${accessToken}&type=image\`;
    
    const form = new FormData();
    form.append('media', fs.createReadStream(coverPath), {
      filename: 'business-cover.png',
      contentType: 'image/png'
    });
    
    const uploadResponse = await httpRequest(uploadUrl, {
      method: 'POST',
      body: form,
      headers: form.getHeaders()
    });
    
    const uploadData = await uploadResponse.json();
    
    if (uploadData.media_id) {
      console.log(\`✅ 商贸封面图上传成功！\`);
      console.log(\`📄 Media ID: \${uploadData.media_id.substring(0, 8)}****\`);
      
      console.log('📤 创建商贸主题草稿文章...');
      const draftUrl = \`https://api.weixin.qq.com/cgi-bin/draft/add?access_token=\${accessToken}\`;
      
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
      
      const draftResponse = await httpRequest(draftUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(articleData)
      });
      
      const draftData = await draftResponse.json();
      
      if (draftData.media_id) {
        console.log(\`✅ 商贸主题草稿创建成功！\`);
        console.log(\`📄 Media ID: \${draftData.media_id.substring(0, 8)}****\`);
        console.log(\`🔗 草稿链接: https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=\${draftData.media_id}&token=&lang=zh_CN\`);
        console.log(\`📝 请到公众号后台「草稿箱」查看并完善内容\`);
        
        return { 
          success: true, 
          message: '商贸主题草稿创建成功',
          mediaId: draftData.media_id,
          draftUrl: \`https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=\${draftData.media_id}&token=&lang=zh_CN\`
        };
      } else {
        const errorMsg = handleWechatError(draftData.errcode, draftData.errmsg);
        console.error(\`❌ \${errorMsg}\`);
        return { success: false, message: errorMsg };
      }
    } else {
      const errorMsg = handleWechatError(uploadData.errcode, uploadData.errmsg);
      console.error(\`❌ \${errorMsg}\`);
      return { success: false, message: errorMsg };
    }
  } catch (error) {
    console.error(\`❌ 发布失败: \${error.message}\`);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

async function main() {
  const args = process.argv.slice(2);
  const options = {
    credentialsPath: args[0] || './secrets/wechat-mp-credentials.json',
    outputDir: args[1] || './output'
  };
  
  const result = await publishBusinessDraft(options);
  
  console.log('\n=== 商贸草稿创建结果 ===');
  console.log(JSON.stringify(result, null, 2));
  
  if (result.success) {
    console.log('\n🎉 商贸主题公众号草稿创建成功！');
    console.log('📱 请前往公众号后台查看草稿箱');
  } else {
    console.log('\n❌ 商贸草稿创建失败，请检查错误信息并重试');
  }
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { publishBusinessDraft, CONTENT_TEMPLATE, WECHAT_ERROR_CODES, handleWechatError };
