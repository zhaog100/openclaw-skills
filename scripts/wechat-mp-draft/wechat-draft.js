/**
 * 微信公众号商贸主题草稿创建脚本
 * 
 * 功能：创建商贸转型主题的公众号草稿
 * 作者：小米椒 🌶️‍🔥
 * 版本：v1.2.0 (内容已脱敏)
 * 
 * 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

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
  
  // 解析凭证路径（支持绝对/相对路径）
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
  
  // 敏感信息脱敏检查
  console.log(`🔐 AppID: ${appId.substring(0, 8)}****`);
  
  let browser;
  
  try {
    // 确保输出目录存在
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 创建商贸主题封面图
    console.log('🖼️ 生成商贸主题封面图...');
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ],
      timeout: 60000
    });
    
    const context = await browser.newContext({
      viewport: { width: 900, height: 500 }
    });
    
    const page = await context.newPage();
    
    // 创建商贸主题封面图 HTML（模板）
    const coverHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
          }
          .container {
            text-align: center;
            color: white;
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
          <div class="emoji">📦</div>
          <h1>${CONTENT_TEMPLATE.cover.title}</h1>
          <p>${CONTENT_TEMPLATE.cover.subtitle}</p>
        </div>
      </body>
      </html>
    `;
    
    await page.setContent(coverHtml);
    
    // 截图保存封面图
    const coverPath = path.join(outputDir, 'business-cover.png');
    await page.screenshot({ path: coverPath, fullPage: true });
    console.log(`🖼️ 商贸封面图已保存：${coverPath}`);
    
    await browser.close();
    console.log('🌐 浏览器已关闭');
    
    // 获取 access_token
    console.log('🔑 获取 access_token...');
    const tokenUrl = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
    
    const tokenResponse = await fetch(tokenUrl);
    const tokenData = await tokenResponse.json();
    
    if (!tokenData.access_token) {
      throw new Error(`获取 access_token 失败: ${JSON.stringify(tokenData)}`);
    }
    
    const accessToken = tokenData.access_token;
    console.log('✅ access_token 获取成功');
    
    // 上传封面图
    console.log('📤 上传商贸主题封面图...');
    const uploadUrl = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;
    
    // 读取图片文件并创建 FormData
    const imageBuffer = fs.readFileSync(coverPath);
    
    // 使用 Node.js 内置 FormData（Node 18+）
    const { FormData } = await import('formdata');
    const formData = new FormData();
    formData.append('media', new Blob([imageBuffer]), 'business-cover.png');
    
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      body: formData
    });
    
    const uploadData = await uploadResponse.json();
    
    if (uploadData.media_id) {
      console.log(`✅ 商贸封面图上传成功！`);
      console.log(`📄 Media ID: ${uploadData.media_id.substring(0, 8)}****`);
      
      // 创建商贸主题草稿
      console.log('📤 创建商贸主题草稿文章...');
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
      
      const draftResponse = await fetch(draftUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(articleData)
      });
      
      const draftData = await draftResponse.json();
      
      if (draftData.media_id) {
        console.log(`✅ 商贸主题草稿创建成功！`);
        console.log(`📄 Media ID: ${draftData.media_id.substring(0, 8)}****`);
        console.log(`🔗 草稿链接: https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftData.media_id}&token=&lang=zh_CN`);
        console.log(`📝 请到公众号后台「草稿箱」查看并完善内容`);
        
        return { 
          success: true, 
          message: '商贸主题草稿创建成功',
          mediaId: draftData.media_id,
          draftUrl: `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&appmsgid=${draftData.media_id}&token=&lang=zh_CN`
        };
      } else {
        console.error(`❌ 草稿创建失败: ${draftData.errmsg || '未知错误'} (错误代码: ${draftData.errcode || 'N/A'})`);
        return { 
          success: false, 
          message: `草稿创建失败: ${draftData.errmsg || '未知错误'}` 
        };
      }
    } else {
      console.error(`❌ 商贸封面图上传失败: ${uploadData.errmsg || '未知错误'} (错误代码: ${uploadData.errcode || 'N/A'})`);
      return { 
        success: false, 
        message: `商贸封面图上传失败: ${uploadData.errmsg || '未知错误'}` 
      };
    }
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

// 主函数入口
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
    console.log('✏️  可以继续编辑完善内容');
    console.log('🚀  准备好后可以直接发布');
  } else {
    console.log('\n❌ 商贸草稿创建失败，请检查错误信息并重试');
  }
  
  process.exit(result.success ? 0 : 1);
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(console.error);
}

// 导出以便其他模块调用
module.exports = { publishBusinessDraft, CONTENT_TEMPLATE };