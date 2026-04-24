/**
 * 使用浏览器自动化发布文章到草稿箱
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function publishToDraftBrowser() {
  console.log('📝 开始发布文章到草稿箱...');
  
  // 读取 session
  const sessionPath = '/tmp/wechat-mp-session.json';
  if (!fs.existsSync(sessionPath)) {
    console.error('❌ Session 文件不存在');
    return { success: false, message: 'Session 文件不存在' };
  }
  
  const sessionCookies = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
  
  let browser;
  let context;
  
  try {
    console.log('🌐 启动浏览器...');
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
      viewport: { width: 1280, height: 720 }
    });
    
    // 设置 cookies
    console.log('🍪 设置 session cookies...');
    await context.addCookies(sessionCookies);
    
    const page = await context.newPage();
    
    // 导航到公众号主页
    console.log('🌐 导航到公众号主页...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/home', { 
      waitUntil: 'domcontentloaded', 
      timeout: 60000 
    });
    
    const currentUrl = page.url();
    console.log('📍 当前 URL:', currentUrl);
    
    if (!currentUrl.includes('/cgi-bin/home') && !currentUrl.includes('/cgi-bin/bizhome')) {
      console.log('⚠️ 未登录，需要重新登录');
      return { success: false, message: '未登录' };
    }
    
    // 导航到新建图文消息页面
    console.log('📝 导航到新建图文消息页面...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/operate_appmsg?sub=operate_appmsg&t=advanced-response&lang=zh_CN', { 
      waitUntil: 'domcontentloaded', 
      timeout: 60000 
    });
    
    await page.waitForLoadState('domcontentloaded');
    
    // 截图
    const screenshotPath = '/tmp/wechat-draft-page.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存：${screenshotPath}`);
    
    // 填写文章标题
    console.log('✏️ 填写文章标题...');
    try {
      await page.fill('#title', '缓解焦虑的 5 个呼吸法');
      console.log('✅ 标题已填写');
    } catch (e) {
      console.log('⚠️ 标题填写失败:', e.message);
    }
    
    // 填写摘要
    console.log('✏️ 填写摘要...');
    try {
      await page.fill('#digest', '5 个简单有效的呼吸法，帮你快速缓解焦虑。每天只需 5-10 分钟，就能显著改善焦虑症状。');
      console.log('✅ 摘要已填写');
    } catch (e) {
      console.log('⚠️ 摘要填写失败:', e.message);
    }
    
    // 填写正文内容
    console.log('✏️ 填写正文内容...');
    const articleContent = `
      <h1>缓解焦虑的 5 个呼吸法</h1>
      <p>在这个快节奏的时代，焦虑似乎成了现代人的标配。工作压力、生活琐事、人际关系...每一个都可能成为压垮我们的最后一根稻草。但你知道吗？最简单有效的缓解焦虑方法，就藏在你的每一次呼吸中。</p>
      
      <h2>为什么呼吸能缓解焦虑？</h2>
      <p>当我们感到焦虑时，身体会进入"战斗或逃跑"模式，呼吸变得急促浅薄。这种呼吸模式会向大脑发送危险信号，进一步加剧焦虑感。而深长缓慢的呼吸则能激活副交感神经系统，告诉身体"现在很安全"，从而降低心率、血压和压力激素水平。</p>
      
      <blockquote>💡 关键要点：每天只需 5-10 分钟的专注呼吸练习，就能显著改善焦虑症状。关键是坚持！</blockquote>
      
      <h2>5 个实用呼吸法</h2>
      
      <h3>1. 腹式呼吸（基础版）</h3>
      <p>仰卧或坐直，一手放在腹部。吸气时让腹部鼓起（4秒），呼气时腹部收缩（6秒）。重复 5-10 分钟。</p>
      
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
    `;
    
    // 尝试填写编辑器内容
    try {
      // 查找编辑器 iframe 或 textarea
      const editorFrame = page.frameLocator('#ueditor_0');
      if (editorFrame) {
        await editorFrame.fill('body', articleContent);
        console.log('✅ 正文已填写');
      }
    } catch (e) {
      console.log('⚠️ 正文填写失败:', e.message);
    }
    
    // 截图查看当前状态
    const finalScreenshotPath = '/tmp/wechat-draft-filled.png';
    await page.screenshot({ path: finalScreenshotPath, fullPage: true });
    console.log(`📸 最终截图已保存：${finalScreenshotPath}`);
    
    // 保存草稿
    console.log('💾 保存草稿...');
    try {
      // 查找保存草稿按钮
      const saveDraftButton = page.locator('button:has-text("保存草稿")');
      if (await saveDraftButton.isVisible()) {
        await saveDraftButton.click();
        console.log('✅ 草稿已保存');
      }
    } catch (e) {
      console.log('⚠️ 草稿保存失败:', e.message);
    }
    
    // 最终截图
    const finalFinalScreenshotPath = '/tmp/wechat-draft-saved.png';
    await page.screenshot({ path: finalFinalScreenshotPath, fullPage: true });
    console.log(`📸 最终截图已保存：${finalFinalScreenshotPath}`);
    
    return { 
      success: true, 
      message: '草稿操作完成',
      screenshots: [screenshotPath, finalScreenshotPath, finalFinalScreenshotPath]
    };
    
  } catch (error) {
    console.error('❌ 发布失败:', error.message);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

publishToDraftBrowser().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
