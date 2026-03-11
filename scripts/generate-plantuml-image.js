const puppeteer = require('puppeteer');
const zlib = require('zlib');

// PlantUML编码函数
function encode64(data) {
  let r = "";
  for (let i = 0; i < data.length; i += 3) {
    if (i + 2 === data.length) {
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i + 1), 0);
    } else if (i + 1 === data.length) {
      r += append3bytes(data.charCodeAt(i), 0, 0);
    } else {
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i + 1), data.charCodeAt(i + 2));
    }
  }
  return r;
}

function append3bytes(b1, b2, b3) {
  const c1 = b1 >> 2;
  const c2 = ((b1 & 0x3) << 4) | (b2 >> 4);
  const c3 = ((b2 & 0xF) << 2) | (b3 >> 6);
  const c4 = b3 & 0x3F;
  return encode6bit(c1 & 0x3F) +
         encode6bit(c2 & 0x3F) +
         encode6bit(c3 & 0x3F) +
         encode6bit(c4 & 0x3F);
}

function encode6bit(b) {
  if (b < 10) return String.fromCharCode(48 + b);
  b -= 10;
  if (b < 26) return String.fromCharCode(65 + b);
  b -= 26;
  if (b < 26) return String.fromCharCode(97 + b);
  b -= 26;
  if (b === 0) return '-';
  if (b === 1) return '_';
  return '?';
}

// 压缩并编码PlantUML代码
function compressAndEncode(text) {
  const compressed = zlib.deflateRawSync(text, { level: 9 });
  return encode64(String.fromCharCode.apply(null, compressed));
}

async function generateDiagram() {
  console.log('喏，官家！开始生成PlantUML图表！\n');

  const plantumlCode = `@startuml
left to right direction
skinparam packageStyle rectangle

actor 用户 as User
actor 管理员 as Admin

rectangle "用户登录系统" {
  usecase "用户登录" as UC1
  usecase "输入用户名密码" as UC2
  usecase "验证身份" as UC3
  usecase "忘记密码" as UC4
  usecase "重置密码" as UC5
  usecase "管理员登录" as UC6
  usecase "查看登录日志" as UC7
}

User --> UC1
UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
User --> UC4
UC4 ..> UC5 : <<extend>>

Admin --> UC6
UC6 ..> UC3 : <<include>>
Admin --> UC7

note right of UC1
  用户使用用户名和密码
  登录系统
end note

note right of UC3
  系统验证用户身份
  支持多种认证方式
end note
@enduml`;

  try {
    // 编码PlantUML代码
    console.log('1. 编码PlantUML代码...');
    const encoded = compressAndEncode(plantumlCode);
    console.log('✅ 编码完成\n');

    // 构建图片URL
    const imageUrl = `http://www.plantuml.com/plantuml/png/${encoded}`;
    console.log('2. 图片URL:');
    console.log(imageUrl);
    console.log('');

    // 使用Puppeteer下载图片
    const browser = await puppeteer.launch({
      headless: 'new'
    });

    const page = await browser.newPage();

    console.log('3. 下载图片...');
    await page.goto(imageUrl, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 截图图片
    const screenshotPath = 'Z:\\OpenClaw\\user-login-usecase-diagram.png';
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log(`✅ 图片已保存: ${screenshotPath}\n`);

    await browser.close();

    console.log('='.repeat(60));
    console.log('PlantUML图表生成成功！');
    console.log('='.repeat(60));
    console.log(`📸 图片位置: ${screenshotPath}`);
    console.log(`🌐 在线查看: ${imageUrl}`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    console.log('\n备用方案：使用PlantUML在线编辑器');
    console.log('1. 访问: http://www.plantuml.com/plantuml/uml/');
    console.log('2. 粘贴代码');
    console.log('3. 点击PNG下载');
  }
}

// 运行
generateDiagram().catch(console.error);
