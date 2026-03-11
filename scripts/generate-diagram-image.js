const puppeteer = require('puppeteer');
const fs = require('fs');

async function generatePlantUMLDiagram() {
  console.log('喏，官家！开始生成用户登录用例图！\n');

  const plantumlCode = `@startuml 用户登录用例图
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

User --> UC1 : 使用
UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
User --> UC4 : 使用
UC4 ..> UC5 : <<extend>>

Admin --> UC6 : 使用
UC6 ..> UC3 : <<include>>
Admin --> UC7 : 使用

note right of UC1
  用户使用用户名和密码
  登录系统
end note

note right of UC3
  系统验证用户身份
  支持多种认证方式
end note

note bottom of UC7
  管理员查看所有用户
  的登录历史记录
end note
@enduml`;

  const browser = await puppeteer.launch({
    headless: 'new'
  });

  const page = await browser.newPage();

  try {
    // 访问PlantUML在线编辑器
    console.log('1. 访问PlantUML在线服务...');
    await page.goto('http://www.plantuml.com/plantuml/uml/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 等待页面加载
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 尝试找到文本输入框并输入代码
    console.log('2. 输入PlantUML代码...');
    const textareaHandle = await page.$('textarea');
    if (textareaHandle) {
      await textareaHandle.click({ clickCount: 3 }); // 全选
      await textareaHandle.type(plantumlCode);
      console.log('✅ 代码已输入\n');
    }

    // 等待图表生成
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 截图
    console.log('3. 截图图表...');
    const screenshotPath = 'C:\\Users\\zhaog\\.openclaw\\workspace\\user-login-usecase-diagram.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 图表已保存: ${screenshotPath}\n`);

    // 保存到Z盘
    const zpath = 'Z:\\OpenClaw\\user-login-usecase-diagram.png';
    fs.copyFileSync(screenshotPath, zpath);
    console.log(`✅ 已复制到: ${zpath}\n`);

    console.log('='.repeat(60));
    console.log('用户登录用例图生成完成');
    console.log('='.repeat(60));
    console.log(`📸 图表位置: ${screenshotPath}`);
    console.log(`📂 Z盘位置: ${zpath}`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

// 运行
generatePlantUMLDiagram().catch(console.error);
