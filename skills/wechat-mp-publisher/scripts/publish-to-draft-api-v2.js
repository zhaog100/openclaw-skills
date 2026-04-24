/**
 * 使用 API 发布文章到草稿箱（不需要封面图）
 */

const fs = require('fs');

async function publishToDraftAPI() {
  console.log('📝 开始发布文章到草稿箱...');
  
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
    
    // 创建草稿（不使用 thumb_media_id）
    console.log('📤 创建草稿文章...');
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
    
    // 文章数据（不包含 thumb_media_id）
    const articleData = {
      articles: [{
        title: '缓解焦虑的 5 个呼吸法',
        author: '心灵的寻光之旅',
        digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑。每天只需 5-10 分钟，就能显著改善焦虑症状。',
        content: `
          <h1>缓解焦虑的 5 个呼吸法</h1>
          <p>在这个快节奏的时代，焦虑似乎成了现代人的标配。工作压力、生活琐事、人际关系...每一个都可能成为压垮我们的最后一根稻草。但你知道吗？最简单有效的缓解焦虑方法，就藏在你的每一次呼吸中。</p>
          
          <h2>为什么呼吸能缓解焦虑？</h2>
          <p>当我们感到焦虑时，身体会进入"战斗或逃跑"模式，呼吸变得急促浅薄。这种呼吸模式会向大脑发送危险信号，进一步加剧焦虑感。而深长缓慢的呼吸则能激活副交感神经系统，告诉身体"现在很安全"，从而降低心率、血压和压力激素水平。</p>
          
          <blockquote>💡 关键要点：每天只需 5-10 分钟的专注呼吸练习，就能显著改善焦虑症状。关键是坚持！</blockquote>
          
          <h2>5 个实用呼吸法</h2>
          
          <h3>1. 腹式呼吸（基础版）</h3>
          <p>仰卧或坐直，一手放在腹部。吸气时让腹部鼓起（4 秒），呼气时腹部收缩（6 秒）。重复 5-10 分钟。</p>
          
          <h3>2. 4-7-8 呼吸法</h3>
          <p>用鼻子吸气 4 秒，屏住呼吸 7 秒，用嘴呼气 8 秒。这个比例能快速平静神经系统，适合睡前练习。</p>
          
          <h3>3. 交替鼻孔呼吸</h3>
          <p>用右手拇指按住右鼻孔，左鼻孔吸气；然后无名指按住左鼻孔，右鼻孔呼气。再右鼻孔吸气，左鼻孔呼气。重复 5-10 轮。</p>
          
          <h3>4. 箱式呼吸</h3>
          <p>吸气 4 秒 → 屏息 4 秒 → 呼气 4 秒 → 屏息 4 秒。像画一个正方形一样，非常适合工作间隙快速恢复平静。</p>
          
          <h3>5. 蜂鸣呼吸</h3>
          <p>用鼻子深吸气，呼气时发出"嗡嗡"声，像蜜蜂一样。这种振动感能按摩喉部，释放紧张情绪。</p>
          
          <h2>实践建议</h2>
          <ul>
            <li><strong>最佳时间</strong>：早晨起床后、工作间隙、睡前</li>
            <li><strong>环境要求</strong>：安静、通风良好的空间</li>
            <li><strong>注意事项</strong>：不要强迫自己，循序渐进</li>
            <li><strong>搭配建议</strong>：可以配合轻柔音乐或香薰</li>
            <li><strong>坚持秘诀</strong>：设置手机提醒，养成习惯</li>
          </ul>
          
          <h2>结语</h2>
          <p>呼吸是我们与生俱来的能力，也是最强大的自我疗愈工具。从今天开始，每天给自己 5 分钟，专注于呼吸，感受内心的平静。记住，你不是一个人在战斗，每一次深呼吸都是对自己的温柔拥抱。</p>
          
          <blockquote>⚠️ 温馨提示：如果焦虑症状严重或持续，请务必寻求专业心理咨询师的帮助。呼吸法是辅助工具，不能替代专业治疗。</blockquote>
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
      console.log(`✅ 草稿创建成功！`);
      console.log(`📄 Media ID: ${draftData.media_id}`);
      console.log(`🔗 可在公众号后台「草稿箱」中查看`);
      
      return { 
        success: true, 
        message: '草稿创建成功', 
        mediaId: draftData.media_id 
      };
    } else {
      console.error(`❌ 草稿创建失败: ${JSON.stringify(draftData)}`);
      
      // 尝试更简单的内容格式
      console.log('🔄 尝试简化内容格式...');
      const simpleArticleData = {
        articles: [{
          title: '缓解焦虑的 5 个呼吸法',
          author: '心灵的寻光之旅',
          digest: '5 个简单有效的呼吸法，帮你快速缓解焦虑',
          content: `<h1>缓解焦虑的 5 个呼吸法</h1><p>5 个简单有效的呼吸法，帮你快速缓解焦虑。每天只需 5-10 分钟，就能显著改善焦虑症状。</p><p>详细内容请关注我们的完整文章...</p>`,
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

publishToDraftAPI().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
