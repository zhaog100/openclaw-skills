/**
 * 下载瑜伽相关图片并上传到微信媒体服务器
 */

const fs = require('fs');
const https = require('https');
const http = require('http');

async function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(filepath);
    
    client.get(url, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        // 处理重定向
        downloadImage(response.headers.location, filepath).then(resolve).catch(reject);
        return;
      }
      
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(filepath, () => {});
      reject(err);
    });
  });
}

async function uploadImageToWechat(accessToken, imagePath) {
  const fileBuffer = fs.readFileSync(imagePath);
  const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
  
  // 构建 multipart/form-data
  const body = Buffer.concat([
    Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="media"; filename="image.jpg"\r\nContent-Type: image/jpeg\r\n\r\n`),
    fileBuffer,
    Buffer.from(`\r\n--${boundary}--\r\n`)
  ]);
  
  const response = await fetch(`https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`, {
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': body.length
    },
    body: body
  });
  
  const result = await response.json();
  return result;
}

async function processYogaImages() {
  console.log('📸 开始下载瑜伽相关图片...');
  
  // 读取凭证
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
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
    
    // 瑜伽相关图片 URL（从 Pexels）
    const yogaImages = [
      { name: 'yoga_cover', url: 'https://images.pexels.com/photos/3771120/pexels-photo-3771120.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_breath1', url: 'https://images.pexels.com/photos/3763897/pexels-photo-3763897.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_breath2', url: 'https://images.pexels.com/photos/3763901/pexels-photo-3763901.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_breath3', url: 'https://images.pexels.com/photos/3763903/pexels-photo-3763903.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_breath4', url: 'https://images.pexels.com/photos/3763905/pexels-photo-3763905.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_breath5', url: 'https://images.pexels.com/photos/3763907/pexels-photo-3763907.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' },
      { name: 'yoga_conclusion', url: 'https://images.pexels.com/photos/3763909/pexels-photo-3763909.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1' }
    ];
    
    const uploadedImages = [];
    
    for (const img of yogaImages) {
      console.log(`📥 下载 ${img.name}...`);
      const localPath = `/tmp/${img.name}.jpg`;
      
      try {
        await downloadImage(img.url, localPath);
        console.log(`✅ 下载成功: ${img.name}`);
        
        console.log(`📤 上传 ${img.name} 到微信...`);
        const uploadResult = await uploadImageToWechat(accessToken, localPath);
        
        if (uploadResult.media_id) {
          console.log(`✅ 上传成功: ${img.name} - media_id: ${uploadResult.media_id}`);
          uploadedImages.push({
            name: img.name,
            url: uploadResult.url,
            mediaId: uploadResult.media_id
          });
        } else {
          console.error(`❌ 上传失败: ${img.name} - ${JSON.stringify(uploadResult)}`);
        }
      } catch (error) {
        console.error(`❌ 处理 ${img.name} 失败: ${error.message}`);
      }
    }
    
    console.log('\n📊 上传结果汇总:');
    console.log(JSON.stringify(uploadedImages, null, 2));
    
    return uploadedImages;
  } catch (error) {
    console.error(`❌ 处理失败: ${error.message}`);
    return [];
  }
}

processYogaImages().then(results => {
  console.log(JSON.stringify(results));
  process.exit(results.length > 0 ? 0 : 1);
});
