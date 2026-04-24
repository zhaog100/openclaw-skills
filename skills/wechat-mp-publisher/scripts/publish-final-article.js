/**
 * 发布《寻光·归途》收官之作
 */

const fs = require('fs');

async function publishFinalArticle() {
  console.log('📝 开始发布收官之作《寻光·归途》...');
  
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
    
    // 构建 draft/add API URL
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${accessToken}`;
    
    // 收官之作内容
    const articleData = {
      articles: [{
        title: '寻光·归途 | 算法囚徒的江湖修行与代码重生',
        thumb_media_id: 'YGrcogg5iY1LHx0FipDcIFtF0chU_FoNXtQDHxGiRqEPPxKYA8ai8teItNVOmQmp', // 使用呼吸法文章的封面
        author: '心灵的寻光之旅',
        digest: '从IT到网约车、外卖、茶叶店，再回到IT——一段35+中年人的真实江湖修行路',
        content: `
          <h1 style="text-align: center; color: #667eea; font-size: 24px; padding: 20px;">寻光·归途 | 算法囚徒的江湖修行与代码重生</h1>
          
          <p style="text-align: center; color: #999; font-size: 14px; margin-bottom: 30px;">心灵的寻光之旅 | 一段35+中年人的真实江湖修行</p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">一、序章：帕丽湾的电流与断点人生</h2>
          
          <p>凌晨一点半的帕丽湾充电站，电流声如白噪音般灌满车厢。手机屏幕亮着——距离那遥不可及的520元补贴，还差37单。旁边“菜秧秧批发市场”的灯牌在夜色中泛着微光，像极了我这段断点续传的人生。</p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">二、轨迹：一场都市“铁人三项”的修行</h2>
          
          <p>五个月前，我是写字楼里敲代码的IT人；三个月前，我在茶叶店背诵普洱的山头与年份；一个月前，我穿梭于楼宇间送外卖；而现在，我握着方向盘，在成都的脉络上划出无数看不见的轨迹。朋友戏称我完成了“滴滴+茶叶+外卖”的都市铁人三项——我去其二，却仿佛走完了普通人半生的职业抛物线。</p>
          
          <p>《算法囚徒日记》里写过：“系统用补贴编织童话，我用里程兑换清醒。”当空调吞掉续航，当陌生人的故事填满沉默的行程，我才真正读懂那份写在《静居寺随记》中的感悟：“所有打工人的疲惫都成了刺向彼此的钝刀——我们明明共享生存的辙痕。”接送过机场里攥着破产文件的企业主，载过九眼桥边哭花妆的年轻女孩，后视镜里折叠着整座城市的得意与失意。</p>
          
          <p>2025年2月，我推开了那扇“算法之门”。从软件公司裸辞的那一刻，我不再是那个困在代码围城里的35+中年人，而是一头扎进滚滚红尘，去修习生活这门最真实的“显学”。</p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">三、寻光：在烟火江湖中重写生存代码</h2>
          
          <p>在方向盘的方寸之间，我在网约车江湖里修习了一百零八种姿势；在茶叶的浮沉香气中，摸索人生的新航向；在外卖疾驰的风里，学会在奔跑中停下来思考。我触摸到了这座钢铁城市最真实的肌理——那是所有打工人共享的生存辙痕，我们常在颠簸中互为“钝刀”，却又在深夜里成为彼此路上唯一的光。</p>
          
          <p>最难熬的是午后三点，阳光把车厢烤成移动的桑拿房。关空调能多跑三十公里，开空调则要面对充电桩前更久的等待——这多像《艰难转身》里的隐喻：中年人的选择，往往不是在好与更好之间，而是在各种损耗中，挑选尚能承受的那一种。</p>
          
          <p>可奇妙的是，当我在玉林路接过一束乘客落下的向日葵，当创业老板在挂电话前说“兄弟，路上慢点”，当发现菜秧市场里真有年轻人在认真挑选番茄苗……这些瞬间像暗房里的显影液，让《星辰大海》中的句子突然变得具体：“方向盘转动的每一度，都可能对准微光。”</p>
          
          <h2 style="color: #667eea; border-left: 4px solid #667eea; padding-left: 12px;">四、归途：带着修好的算法重返星辰大海</h2>
          
          <p>如今，我重回IT行业，重拾代码。但那个曾被算法困住的囚徒，已永远留在了来时的风雨里。归来不是轮回，而是突围——我带回了满身的江湖烟火气，把乘客的故事、茶叶的温度、街巷的喘息，都编译成人生系统里无法删去的注释。</p>
          
          <p>充电桩的屏幕又一次变绿。拔枪的瞬间忽然明白：人生没有无用的里程，所有绕过的路，都是灵魂在自主“补电”。 那些在帕丽湾数过的星星、在茶叶店沏过的时光、在送餐路上吹过的风，都已悄然重写了我内心的代码。</p>
          
          <p>方向盘上的人生，从未离开星辰大海的航道。它只是需要偶尔驶入烟火深处，让算法在人间校准，让光在辗转中显影。</p>
          
          <p style="font-weight: bold; font-size: 18px; text-align: center; margin: 30px 0; color: #667eea;">车轮还在转。</p>
          
          <p>但这一次，我既是司机，也是乘客；是程序员，也是自己人生的产品经理。这段寻光之旅教会我的，或许正是：真正的突围，从来不是离开哪里，而是无论身在何处，都能修好属于自己的那行代码。</p>
          
          <p style="text-align: center; padding: 20px; color: #667eea; font-size: 16px;">🧘‍♀️ 心灵的寻光之旅<br>光明瑜伽之旅，心灵的寻光之路</p>
        `,
        content_source_url: '',
        need_open_comment: 1,
        only_fans_can_comment: 0
      }]
    };
    
    console.log('📤 创建收官之作草稿...');
    const draftResponse = await fetch(draftUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(articleData)
    });
    
    const draftData = await draftResponse.json();
    
    if (draftData.media_id) {
      console.log(`✅ 收官之作草稿创建成功！`);
      console.log(`📄 Media ID: ${draftData.media_id}`);
      console.log(`🔗 可在公众号后台「草稿箱」中查看`);
      
      return { 
        success: true, 
        message: '收官之作草稿创建成功', 
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

publishFinalArticle().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
