/**
 * 上传封面图并发布优化版文章到草稿箱
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function publishWithCoverOptimized() {
  console.log('🖼️ 开始创建封面图并发布文章...');
  
  // 读取凭证
  const credentialsPath = '/root/.openclaw/workspace/secrets/wechat-mp-credentials.json';
  const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
  
  const { appId, appSecret } = credentials.account;
  
  let browser;
  let context;
  
  try {
    // 创建封面图
    console.log('🖼️ 启动浏览器创建封面图...');
    browser = await chromium.launch({
      headless: false,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ],
      timeout: 60000
    });
    
    context = await browser.newContext({
      viewport: { width: 900, height: 500 }
    });
    
    const page = await context.newPage();
    
    // 创建精美的封面图 HTML
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
            font-size: 48px;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
          }
          p {
            font-size: 24px;
            opacity: 0.9;
          }
          .emoji {
            font-size: 60px;
            margin-bottom: 20px;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="emoji">🧘‍♀️</div>
          <h1>缓解焦虑的 5 个呼吸法</h1>
          <p>心灵的寻光之旅 | 每天 5 分钟，找回内心平静</p>
        </div>
      </body>
      </html>
    `;
    
    await page.setContent(coverHtml);
    
    // 截图保存封面图
    const coverPath = '/tmp/wechat-cover-optimized.png';
    await page.screenshot({ path: coverPath, fullPage: true });
    console.log(`🖼️ 封面图已保存：${coverPath}`);
    
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
    console.log('📤 上传封面图...');
    const uploadUrl = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;
    
    // 读取图片文件并创建 FormData
    const imageBuffer = fs.readFileSync(coverPath);
    
    // 使用 fetch 上传
    const formData = new FormData();
    formData.append('media', new Blob([imageBuffer]), 'cover-optimized.png');
    
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      body: formData
    });
    
    const uploadData = await uploadResponse.json();
    
    if (uploadData.media_id) {
      console.log(`✅ 封面图上传成功！`);
      console.log(`📄 Media ID: ${uploadData.media_id}`);
      
      // 创建优化版草稿
      console.log('📤 创建优化版草稿文章...');
      const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
      
      const articleData = {
        articles: [{
          title: '缓解焦虑的 5 个呼吸法｜每天 5 分钟，找回内心平静',
          thumb_media_id: uploadData.media_id,
          author: '心灵的寻光之旅',
          digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑。每天只需 5-10 分钟，就能显著改善焦虑症状。',
          content: `
            <h1 style="text-align: center; color: #667eea; font-size: 24px; padding: 20px;">🧘‍♀️ 缓解焦虑的 5 个呼吸法</h1>
            
            <p style="text-align: center; color: #999; font-size: 14px; margin-bottom: 30px;">心灵的寻光之旅 | 每天 5 分钟，找回内心平静</p>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; margin: 20px 0; text-align: center;">
              <p style="color: white; font-size: 18px; font-style: italic; margin: 0;">"呼吸是连接身体与心灵的桥梁，当你学会正确呼吸，焦虑自然消散。"</p>
            </div>
            
            <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">🌊 为什么呼吸能缓解焦虑？</h2>
            
            <p>在这个快节奏的时代，焦虑似乎成了现代人的标配。工作压力、生活琐事、人际关系...每一个都可能成为压垮我们的最后一根稻草。</p>
            
            <p>但你知道吗？<strong>最简单有效的缓解焦虑方法，就藏在你的每一次呼吸中。</strong></p>
            
            <img src="https://images.unsplash.com/photo-1506126613408-eca07ce2f58f?w=680&h=400&fit=crop" alt="瑜伽冥想" style="width: 100%; border-radius: 8px; margin: 20px 0;" />
            
            <p>当我们感到焦虑时，身体会进入"战斗或逃跑"模式，呼吸变得急促浅薄。这种呼吸模式会向大脑发送危险信号，进一步加剧焦虑感。</p>
            
            <p>而<strong>深长缓慢的呼吸</strong>则能激活副交感神经系统，告诉身体"现在很安全"，从而降低心率、血压和压力激素水平。</p>
            
            <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
              <p style="margin: 0;"><strong>💡 关键要点：</strong>每天只需 5-10 分钟的专注呼吸练习，就能显著改善焦虑症状。<strong>关键是坚持！</strong></p>
            </div>
            
            <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">🧘‍♀️ 5 个实用呼吸法</h2>
            
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 25px; border-radius: 12px; margin: 20px 0;">
              <h3 style="color: #764ba2; margin-top: 0;">1️⃣ 腹式呼吸（基础版）</h3>
              <p>仰卧或坐直，一手放在腹部。吸气时让腹部鼓起（<strong>4 秒</strong>），呼气时腹部收缩（<strong>6 秒</strong>）。重复 5-10 分钟。</p>
              <img src="https://images.unsplash.com/photo-1544367567-0f2f0b525680?w=680&h=300&fit=crop" alt="腹式呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
            </div>
            
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 25px; border-radius: 12px; margin: 20px 0;">
              <h3 style="color: #764ba2; margin-top: 0;">2️⃣ 4-7-8 呼吸法</h3>
              <p>用鼻子吸气 <strong>4 秒</strong> → 屏住呼吸 <strong>7 秒</strong> → 用嘴呼气 <strong>8 秒</strong>。</p>
              <p>这个比例能快速平静神经系统，<strong>适合睡前练习</strong>。</p>
              <img src="https://images.unsplash.com/photo-1531353826977-0e775953ec74?w=680&h=300&fit=crop" alt="睡前呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
            </div>
            
            <div style="background: linear-gradient(135deg, #e0c3fc 0%, #8c52ff 100%); padding: 25px; border-radius: 12px; margin: 20px 0;">
              <h3 style="color: white; margin-top: 0;">3️⃣ 交替鼻孔呼吸</h3>
              <p>用右手拇指按住右鼻孔，左鼻孔吸气；然后无名指按住左鼻孔，右鼻孔呼气。再右鼻孔吸气，左鼻孔呼气。重复 5-10 轮。</p>
              <img src="https://images.unsplash.com/photo-1510894347713-fc4ed9353c39?w=680&h=300&fit=crop" alt="交替呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
            </div>
            
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 12px; margin: 20px 0;">
              <h3 style="color: white; margin-top: 0;">4️⃣ 箱式呼吸</h3>
              <p>吸气 <strong>4 秒</strong> → 屏息 <strong>4 秒</strong> → 呼气 <strong>4 秒</strong> → 屏息 <strong>4 秒</strong>。</p>
              <p>像画一个正方形一样，<strong>非常适合工作间隙快速恢复平静</strong>。</p>
              <img src="https://images.unsplash.com/photo-1552190728-491386dbbf65?w=680&h=300&fit=crop" alt="箱式呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
            </div>
            
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 25px; border-radius: 12px; margin: 20px 0;">
              <h3 style="color: white; margin-top: 0;">5️⃣ 蜂鸣呼吸</h3>
              <p>用鼻子深吸气，呼气时发出"嗡嗡"声，像蜜蜂一样。这种振动感能按摩喉部，<strong>释放紧张情绪</strong>。</p>
              <img src="https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?w=680&h=300&fit=crop" alt="蜂鸣呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
            </div>
            
            <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">📋 实践建议</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 20px 0;">
              <ul style="margin: 0; padding-left: 20px;">
                <li style="margin: 10px 0;"><strong>⏰ 最佳时间</strong>：早晨起床后、工作间隙、睡前</li>
                <li style="margin: 10px 0;"><strong>🏠 环境要求</strong>：安静、通风良好的空间</li>
                <li style="margin: 10px 0;"><strong>⚠️ 注意事项</strong>：不要强迫自己，循序渐进</li>
                <li style="margin: 10px 0;"><strong>🎵 搭配建议</strong>：可以配合轻柔音乐或香薰</li>
                <li style="margin: 10px 0;"><strong>📱 坚持秘诀</strong>：设置手机提醒，养成习惯</li>
              </ul>
            </div>
            
            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=680&h=400&fit=crop" alt="平静时刻" style="width: 100%; border-radius: 8px; margin: 20px 0;" />
            
            <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">💝 结语</h2>
            
            <p>呼吸是我们与生俱来的能力，也是最强大的自我疗愈工具。</p>
            
            <p>从今天开始，每天给自己 <strong>5 分钟</strong>，专注于呼吸，感受内心的平静。</p>
            
            <p>记住，你不是一个人在战斗，<strong>每一次深呼吸都是对自己的温柔拥抱</strong>。</p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0;">
              <p style="margin: 0;"><strong>⚠️ 温馨提示：</strong>如果焦虑症状严重或持续，请务必寻求专业心理咨询师的帮助。呼吸法是辅助工具，不能替代专业治疗。</p>
            </div>
            
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin: 30px 0;">
              <p style="color: white; font-size: 16px; margin: 0;">🧘‍♀️ 心灵的寻光之旅</p>
              <p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 10px 0;">光明瑜伽之旅，心灵的寻光之路</p>
              <p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 0;">关注我们，开启您的光明心灵之旅！</p>
            </div>
          `,
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
        console.log(`✅ 优化版草稿创建成功！`);
        console.log(`📄 Media ID: ${draftData.media_id}`);
        console.log(`🔗 可在公众号后台「草稿箱」中查看`);
        
        return { 
          success: true, 
          message: '优化版草稿创建成功', 
          mediaId: draftData.media_id 
        };
      } else {
        console.error(`❌ 草稿创建失败: ${JSON.stringify(draftData)}`);
        return { 
          success: false, 
          message: `草稿创建失败: ${JSON.stringify(draftData)}` 
        };
      }
    } else {
      console.error(`❌ 封面图上传失败: ${JSON.stringify(uploadData)}`);
      return { 
        success: false, 
        message: `封面图上传失败: ${JSON.stringify(uploadData)}` 
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

publishWithCoverOptimized().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
