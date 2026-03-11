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
  console.log('喏，官家！开始生成系统架构组件图！\n');

  const plantumlCode = `@startuml 系统架构组件图
!define RECTANGLE rectangle

skinparam componentStyle rectangle

package "前端层" {
  [Web应用] as WebApp
  [移动应用] as MobileApp
  [小程序] as MiniApp
}

package "API网关" {
  [API Gateway] as Gateway
}

package "业务服务层" {
  [用户服务] as UserService
  [订单服务] as OrderService
  [支付服务] as PaymentService
  [通知服务] as NotificationService
}

package "数据访问层" {
  [数据库访问] as DAO
  [缓存服务] as CacheService
}

package "数据存储层" {
  database "MySQL数据库" as MySQL
  database "Redis缓存" as Redis
}

package "第三方服务" {
  [支付宝] as Alipay
  [微信支付] as WeChatPay
  [邮件服务] as EmailService
  [短信服务] as SMSService
}

' 前端到网关
WebApp --> Gateway : HTTPS
MobileApp --> Gateway : HTTPS
MiniApp --> Gateway : HTTPS

' 网关到服务
Gateway --> UserService : REST API
Gateway --> OrderService : REST API
Gateway --> PaymentService : REST API
Gateway --> NotificationService : REST API

' 服务到数据访问
UserService --> DAO : JDBC
OrderService --> DAO : JDBC
PaymentService --> DAO : JDBC
NotificationService --> DAO : JDBC

UserService --> CacheService : Redis
OrderService --> CacheService : Redis

' 数据访问到存储
DAO --> MySQL : TCP/IP
CacheService --> Redis : TCP/IP

' 支付服务到第三方
PaymentService --> Alipay : HTTPS
PaymentService --> WeChatPay : HTTPS

' 通知服务到第三方
NotificationService --> EmailService : SMTP
NotificationService --> SMSService : HTTPS

note right of Gateway
  **API网关**
  - 负载均衡
  - 认证授权
  - 限流熔断
  - 日志记录
end note

note right of UserService
  **用户服务**
  - 用户注册
  - 用户登录
  - 用户信息管理
  - 权限管理
end note

note right of OrderService
  **订单服务**
  - 订单创建
  - 订单查询
  - 订单状态管理
  - 订单统计
end note

note right of PaymentService
  **支付服务**
  - 支付处理
  - 支付查询
  - 退款处理
  - 支付回调
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
    const screenshotPath = 'Z:\\OpenClaw\\system-architecture-diagram.png';
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log(`✅ 图片已保存: ${screenshotPath}\n`);

    // 保存源代码
    const fs = require('fs');
    const codePath = 'Z:\\OpenClaw\\system-architecture.puml';
    fs.writeFileSync(codePath, plantumlCode, 'utf8');
    console.log(`✅ 代码已保存: ${codePath}\n`);

    await browser.close();

    console.log('='.repeat(60));
    console.log('系统架构组件图生成成功！');
    console.log('='.repeat(60));
    console.log(`📸 图片位置: ${screenshotPath}`);
    console.log(`📄 代码位置: ${codePath}`);
    console.log(`🌐 在线查看: ${imageUrl}`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 生成失败:', error.message);
  }
}

// 运行
generateDiagram().catch(console.error);
