/**
 * 微信公众号 API 连接测试脚本
 * 测试 AppID 和 AppSecret 是否有效
 */

const fs = require('fs');
const path = require('path');

async function testAPIConnection() {
  console.log('🔐 开始测试微信公众号 API 连接...');
  
  // 读取凭证
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
  console.log(`📱 AppID: ${appId}`);
  console.log(`🔑 AppSecret: ${appSecret.substring(0, 4)}****${appSecret.substring(appSecret.length - 4)}`);
  
  try {
    // 获取 access_token
    const tokenUrl = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
    console.log(`🌐 请求 access_token...`);
    
    const response = await fetch(tokenUrl);
    const data = await response.json();
    
    if (data.access_token) {
      console.log(`✅ access_token 获取成功！`);
      console.log(`📝 Token 前 10 位：${data.access_token.substring(0, 10)}...`);
      console.log(`⏰ 有效期：${data.expires_in} 秒`);
      
      // 测试获取用户信息（需要额外权限）
      // 这里只测试 token 是否有效
      
      console.log('\n✅ API 连接测试通过！');
      console.log('🚀 现在可以开始自动发布文章！');
      
      return { success: true, message: 'API 连接成功' };
    } else {
      console.error(`❌ access_token 获取失败：${JSON.stringify(data)}`);
      return { success: false, message: data.errmsg || 'Token 获取失败' };
    }
  } catch (error) {
    console.error(`❌ API 连接测试失败：${error.message}`);
    return { success: false, message: error.message };
  }
}

// 执行测试
testAPIConnection().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
