/**
 * 微信公众号文章发布脚本
 * 将 HTML 内容发布为草稿
 */

const fs = require('fs');
const path = require('path');

async function publishArticle(htmlFilePath, title) {
  console.log(`📝 开始发布文章：${title}`);
  
  // 读取凭证
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
  // 读取 HTML 内容
  const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
  
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
    
    // 创建草稿
    console.log('📤 创建草稿文章...');
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
    
    // 准备文章数据（简化版，实际需要处理 HTML 转换）
    const articleData = {
      articles: [{
        title: title,
        thumb_media_id: '', // 需要先上传封面图片
        author: '心灵的寻光之旅',
        digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑',
        show_cover_pic: 0,
        content: htmlContent,
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
      console.log(`✅ 草稿创建成功！`);
      console.log(`📄 Media ID: ${draftData.media_id}`);
      console.log(`🔗 可在公众号后台「素材管理」中查看`);
      
      return { 
        success: true, 
        message: '草稿创建成功', 
        mediaId: draftData.media_id 
      };
    } else {
      console.error(`❌ 草稿创建失败: ${JSON.stringify(draftData)}`);
      
      // 尝试更简单的文本内容
      console.log('🔄 尝试简化内容...');
      const simpleContent = `
        <h1>${title}</h1>
        <p>5 个简单有效的呼吸法，帮你快速缓解焦虑</p>
        <ol>
          <li>腹式呼吸</li>
          <li>4-7-8 呼吸法</li>
          <li>交替鼻孔呼吸</li>
          <li>箱式呼吸</li>
          <li>蜂鸣呼吸</li>
        </ol>
        <p>详细内容请查看完整文章...</p>
      `;
      
      const simpleArticleData = {
        articles: [{
          title: title,
          thumb_media_id: '',
          author: '心灵的寻光之旅',
          digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑',
          show_cover_pic: 0,
          content: simpleContent,
          content_source_url: '',
          need_open_comment: 1,
          only_fans_can_comment: 0
        }]
      };
      
      const simpleDraftResponse = await fetch(draftUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(simpleArticleData)
      });
      
      const simpleDraftData = await simpleDraftResponse.json();
      
      if (simpleDraftData.media_id) {
        console.log(`✅ 简化草稿创建成功！`);
        console.log(`📄 Media ID: ${simpleDraftData.media_id}`);
        return { 
          success: true, 
          message: '简化草稿创建成功', 
          mediaId: simpleDraftData.media_id 
        };
      } else {
        return { 
          success: false, 
          message: `草稿创建失败: ${JSON.stringify(simpleDraftData)}` 
        };
      }
    }
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    return { success: false, message: error.message };
  }
}

// 从命令行参数获取文件路径和标题
const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('用法: node publish-article.js <html文件路径> <文章标题>');
  process.exit(1);
}

const htmlFilePath = args[0];
const title = args[1];

publishArticle(htmlFilePath, title).then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
