/**
 * 发布瑜伽版呼吸法文章（使用瑜伽相关图片，无渐变背景框）
 */

const fs = require('fs');

async function publishYogaBreathingArticle() {
  console.log('📝 开始发布瑜伽版呼吸法文章...');
  
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
    
    // 上传的瑜伽图片
    const uploadedImages = [
      { name: 'yoga_cover', url: 'http://mmbiz.qpic.cn/sz_mmbiz_jpg/HAlvqFvKMpgNd2y8fJfmCLnRGCv46IdkHWa8ukn7nbibwNANT6TNmsfTLGrVOZlzIfvBDibt85yl4l0LPv9iaX3PJzdeb120BBRKkzz1qr6HNU/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcIMmIq5ey-4AJf7KijUjjDNzhFPx-Q167sv3eVZXwhVNj' },
      { name: 'yoga_breath1', url: 'http://mmbiz.qpic.cn/mmbiz_jpg/HAlvqFvKMphENdDqAdBxQsdZibMmmJG55bbqaSgk3LRP0g3HCT6ERkQCuia7AhmwfP8gp0Gib34icmM7tE1m3eJvlxnVkBtPSyWEj0vyA2KvgaI/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcIE3PThEtcvlivh29eFNrYk7zb1P5Blj6XRuA0AaGGwCb' },
      { name: 'yoga_breath2', url: 'http://mmbiz.qpic.cn/sz_mmbiz_jpg/HAlvqFvKMphPoW6fpz8bVcQ5eJM0PkZkvVzMVcgEbFnicibcYpvqkpibtFVxCTLr0l8dtxaUQtrXNFs2x9XUWKDDxs3TSMBOibfzwqPt0BC8EMA/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcINeOq6cAZBIdklFdW0HAWugvbUcoaELnu8Ixtjwi6qVt' },
      { name: 'yoga_breath3', url: 'http://mmbiz.qpic.cn/sz_mmbiz_jpg/HAlvqFvKMphzoO76I6fbIjbkGibib3d1mfWXYUub3icxmelYTK6J2l35icIwt7I5pn2iaTLOvf53589P791d83xXnvWSV9iclIWsiabQiaLVRjvEwW8/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcICJZ3QGQ1M7mnaZ4Vz9SeJAGWFrftkpPf-xv057KrRMw' },
      { name: 'yoga_breath4', url: 'http://mmbiz.qpic.cn/mmbiz_jpg/HAlvqFvKMpju87kqx5mjjfcaicm9IQfkRxh8iaUkjGF7LdiaSVkSHOApRuO5DXKbHTibmN0OplGakkscMgOTMCjeZlOfJV7zh4tk0gwUdqaqdNE/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcIL2GNaRU5YkXrmYb18YUPdDHpRcRfZLT3ERg1PG7iX6c' },
      { name: 'yoga_breath5', url: 'http://mmbiz.qpic.cn/mmbiz_jpg/HAlvqFvKMphBzBYGvks3I3kvM45ia1Qpf2yJFa7lmibzgM2yjzLH5REDhZ4rKZznSDVZFFAwS06SDmdXzDPTqLP6Jytk1ksicBp39MIUNsAOiaI/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcILaDMyBEOAJ1RlRKeYAJvUXM3J9DAG5PRqflkCrXS-IY' },
      { name: 'yoga_conclusion', url: 'http://mmbiz.qpic.cn/sz_mmbiz_jpg/HAlvqFvKMpiaGHj0DSRRNtIRVPumCx8wyFrAKpRSicxgJaro136YxT1LFSJDyzzPLdLVic8aaWNfFOZjS6alsUwJSicJsRzHZQIhbgglDVnD1o8/0?wx_fmt=jpeg', mediaId: 'YGrcogg5iY1LHx0FipDcIDBo6B0P2aUUVVCNrIC2qBY751jjzZHyhtIJFIozIri5' }
    ];
    
    const coverImage = uploadedImages.find(img => img.name === 'yoga_cover');
    
    // 瑜伽版内容 - 无渐变背景框，使用瑜伽图片
    const articleData = {
      articles: [{
        title: '缓解焦虑的 5 个呼吸法｜每天 5 分钟，找回内心平静',
        thumb_media_id: coverImage?.mediaId || '',
        author: '心灵的寻光之旅',
        digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑。每天只需 5-10 分钟，就能显著改善焦虑症状。',
        content: `
          <h1 style="text-align: center; color: #667eea; font-size: 24px; padding: 20px;">🧘‍♀️ 缓解焦虑的 5 个呼吸法</h1>
          
          <p style="text-align: center; color: #999; font-size: 14px; margin-bottom: 30px;">心灵的寻光之旅 | 每天 5 分钟，找回内心平静</p>
          
          <p style="text-align: center; font-size: 16px; color: #666; font-style: italic; margin: 20px 0;">"呼吸是连接身体与心灵的桥梁，当你学会正确呼吸，焦虑自然消散。"</p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">🌊 为什么呼吸能缓解焦虑？</h2>
          
          <p>在这个快节奏的时代，焦虑似乎成了现代人的标配。工作压力、生活琐事、人际关系...每一个都可能成为压垮我们的最后一根稻草。</p>
          
          <p>但你知道吗？<strong>最简单有效的缓解焦虑方法，就藏在你的每一次呼吸中。</strong></p>
          
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath1')?.url || ''}" alt="瑜伽冥想" style="width: 100%; border-radius: 8px; margin: 20px 0;" />
          
          <p>当我们感到焦虑时，身体会进入"战斗或逃跑"模式，呼吸变得急促浅薄。这种呼吸模式会向大脑发送危险信号，进一步加剧焦虑感。</p>
          
          <p>而<strong>深长缓慢的呼吸</strong>则能激活副交感神经系统，告诉身体"现在很安全"，从而降低心率、血压和压力激素水平。</p>
          
          <p style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;"><strong>💡 关键要点：</strong>每天只需 5-10 分钟的专注呼吸练习，就能显著改善焦虑症状。<strong>关键是坚持！</strong></p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">🧘‍♀️ 5 个实用呼吸法</h2>
          
          <h3 style="color: #764ba2;">1️⃣ 腹式呼吸（基础版）</h3>
          <p>仰卧或坐直，一手放在腹部。吸气时让腹部鼓起（<strong>4 秒</strong>），呼气时腹部收缩（<strong>6 秒</strong>）。重复 5-10 分钟。</p>
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath1')?.url || ''}" alt="腹式呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
          
          <h3 style="color: #764ba2;">2️⃣ 4-7-8 呼吸法</h3>
          <p>用鼻子吸气 <strong>4 秒</strong> → 屏住呼吸 <strong>7 秒</strong> → 用嘴呼气 <strong>8 秒</strong>。</p>
          <p>这个比例能快速平静神经系统，<strong>适合睡前练习</strong>。</p>
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath2')?.url || ''}" alt="睡前呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
          
          <h3 style="color: #764ba2;">3️⃣ 交替鼻孔呼吸</h3>
          <p>用右手拇指按住右鼻孔，左鼻孔吸气；然后无名指按住左鼻孔，右鼻孔呼气。再右鼻孔吸气，左鼻孔呼气。重复 5-10 轮。</p>
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath3')?.url || ''}" alt="交替呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
          
          <h3 style="color: #764ba2;">4️⃣ 箱式呼吸</h3>
          <p>吸气 <strong>4 秒</strong> → 屏息 <strong>4 秒</strong> → 呼气 <strong>4 秒</strong> → 屏息 <strong>4 秒</strong>。</p>
          <p>像画一个正方形一样，<strong>非常适合工作间隙快速恢复平静</strong>。</p>
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath4')?.url || ''}" alt="箱式呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
          
          <h3 style="color: #764ba2;">5️⃣ 蜂鸣呼吸</h3>
          <p>用鼻子深吸气，呼气时发出"嗡嗡"声，像蜜蜂一样。这种振动感能按摩喉部，<strong>释放紧张情绪</strong>。</p>
          <img src="${uploadedImages.find(img => img.name === 'yoga_breath5')?.url || ''}" alt="蜂鸣呼吸" style="width: 100%; border-radius: 8px; margin: 15px 0;" />
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">📋 实践建议</h2>
          
          <ul style="padding-left: 20px;">
            <li style="margin: 10px 0;"><strong>⏰ 最佳时间</strong>：早晨起床后、工作间隙、睡前</li>
            <li style="margin: 10px 0;"><strong>🏠 环境要求</strong>：安静、通风良好的空间</li>
            <li style="margin: 10px 0;"><strong>⚠️ 注意事项</strong>：不要强迫自己，循序渐进</li>
            <li style="margin: 10px 0;"><strong>🎵 搭配建议</strong>：可以配合轻柔音乐或香薰</li>
            <li style="margin: 10px 0;"><strong>📱 坚持秘诀</strong>：设置手机提醒，养成习惯</li>
          </ul>
          
          <img src="${uploadedImages.find(img => img.name === 'yoga_conclusion')?.url || ''}" alt="平静时刻" style="width: 100%; border-radius: 8px; margin: 20px 0;" />
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">💝 结语</h2>
          
          <p>呼吸是我们与生俱来的能力，也是最强大的自我疗愈工具。</p>
          
          <p>从今天开始，每天给自己 <strong>5 分钟</strong>，专注于呼吸，感受内心的平静。</p>
          
          <p>记住，你不是一个人在战斗，<strong>每一次深呼吸都是对自己的温柔拥抱</strong>。</p>
          
          <p style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;"><strong>⚠️ 温馨提示：</strong>如果焦虑症状严重或持续，请务必寻求专业心理咨询师的帮助。呼吸法是辅助工具，不能替代专业治疗。</p>
          
          <p style="text-align: center; padding: 20px; color: #667eea; font-size: 16px;">🧘‍♀️ 心灵的寻光之旅<br>光明瑜伽之旅，心灵的寻光之路</p>
        `,
        content_source_url: '',
        need_open_comment: 1,
        only_fans_can_comment: 0
      }]
    };
    
    // 构建 draft/add API URL
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
    
    console.log('📤 创建瑜伽版草稿...');
    const draftResponse = await fetch(draftUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(articleData)
    });
    
    const draftData = await draftResponse.json();
    
    if (draftData.media_id) {
      console.log(`✅ 瑜伽版草稿创建成功！`);
      console.log(`📄 Media ID: ${draftData.media_id}`);
      console.log(`🔗 可在公众号后台「草稿箱」中查看`);
      
      return { 
        success: true, 
        message: '瑜伽版草稿创建成功', 
        mediaId: draftData.media_id 
      };
    } else {
      console.error(`❌ 草稿创建失败: ${JSON.stringify(draftData)}`);
      return { 
        success: false, 
        message: `草稿创建失败: ${JSON.stringify(draftData)}` 
      };
    }
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    return { success: false, message: error.message };
  }
}

publishYogaBreathingArticle().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
