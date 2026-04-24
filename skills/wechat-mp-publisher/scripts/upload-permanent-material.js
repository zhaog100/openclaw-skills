/**
 * 微信公众号永久素材上传脚本（适用于订阅号）
 * 上传图文消息作为永久素材
 */

const fs = require('fs');
const path = require('path');

async function uploadPermanentMaterial(htmlFilePath, title) {
  console.log(`📝 开始上传永久素材：${title}`);
  
  // 读取凭证
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
  // 读取 HTML 内容并提取纯文本摘要
  const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
  
  // 简化内容提取（实际项目中应该用更完善的 HTML 解析）
  const extractTextFromHTML = (html) => {
    // 移除 HTML 标签，保留基本文本
    return html.replace(/<[^>]*>/g, ' ')
               .replace(/\s+/g, ' ')
               .trim()
               .substring(0, 200) + '...';
  };
  
  const contentSummary = extractTextFromHTML(htmlContent);
  
  try {
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
    
    // 创建图文素材数据
    console.log('📤 准备图文素材数据...');
    const articles = [{
      title: title,
      thumb_media_id: '', // 订阅号可以为空
      author: '心灵的寻光之旅',
      digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑',
      show_cover_pic: 0,
      content: `<h1>${title}</h1><p>5 个简单有效的呼吸法，帮你快速缓解焦虑：</p><ol><li>腹式呼吸</li><li>4-7-8 呼吸法</li><li>交替鼻孔呼吸</li><li>箱式呼吸</li><li>蜂鸣呼吸</li></ol><p>详细内容和实践指导请关注我们的完整文章...</p>`,
      content_source_url: '',
      need_open_comment: 1,
      only_fans_can_comment: 0
    }];
    
    const materialData = {
      articles: articles
    };
    
    // 上传永久图文素材
    console.log('📤 上传永久图文素材...');
    const uploadUrl = `https://api.weixin.qq.com/cgi-bin/material/add_news?access_token=${accessToken}`;
    
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(materialData)
    });
    
    const uploadData = await uploadResponse.json();
    
    if (uploadData.media_id) {
      console.log(`✅ 永久素材上传成功！`);
      console.log(`📄 Media ID: ${uploadData.media_id}`);
      console.log(`🔗 可在公众号后台「素材管理」→「图文消息」中查看`);
      
      return { 
        success: true, 
        message: '永久素材上传成功', 
        mediaId: uploadData.media_id 
      };
    } else {
      console.error(`❌ 上传失败: ${JSON.stringify(uploadData)}`);
      return { 
        success: false, 
        message: `上传失败: ${JSON.stringify(uploadData)}` 
      };
    }
  } catch (error) {
    console.error(`❌ 上传失败: ${error.message}`);
    return { success: false, message: error.message };
  }
}

// 从命令行参数获取文件路径和标题
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('用法: node upload-permanent-material.js <html文件路径> <文章标题>');
  process.exit(1);
}

const htmlFilePath = args[0];
const title = args[1];

uploadPermanentMaterial(htmlFilePath, title).then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
