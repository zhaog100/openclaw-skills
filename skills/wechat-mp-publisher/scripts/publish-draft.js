/**
 * 发布草稿到公众号（试水）
 */

const fs = require('fs');

async function publishDraft() {
  console.log('📤 开始发布草稿...');
  
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
  try {
    console.log('🔑 获取 access_token...');
    const tokenUrl = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
    const tokenResponse = await fetch(tokenUrl);
    const tokenData = await tokenResponse.json();
    
    if (!tokenData.access_token) {
      throw new Error(`获取 access_token 失败: ${JSON.stringify(tokenData)}`);
    }
    
    const accessToken = tokenData.access_token;
    console.log('✅ access_token 获取成功');
    
    // 草稿 ID（首篇商贸测评）
    const draftMediaId = 'YGrcogg5iY1LHx0FipDcIB-Pa7UA0_mJZ9pzr2qveX928m0ZwcfAO8qPcmfOXcCR';
    
    // 尝试发布 API
    const publishUrl = `https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=${accessToken}`;
    
    console.log('📤 尝试发布...');
    const publishResponse = await fetch(publishUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        media_id: draftMediaId
      })
    });
    
    const publishData = await publishResponse.json();
    
    if (publishData.errcode === 0) {
      console.log(`✅ 发布成功！`);
      console.log(`📄 文章 ID: ${publishData.msg_id}`);
      return { 
        success: true, 
        message: '发布成功', 
        msgId: publishData.msg_id 
      };
    } else {
      console.log(`⚠️ 发布 API 返回: ${JSON.stringify(publishData)}`);
      console.log(`💡 可能需要手动在公众号后台发布`);
      return { 
        success: false, 
        message: `发布 API 返回: ${JSON.stringify(publishData)}`,
        needManualPublish: true 
      };
    }
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    return { success: false, message: error.message };
  }
}

publishDraft().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
