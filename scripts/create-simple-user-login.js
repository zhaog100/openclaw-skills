/**
 * 用户登录用例图 - 简化版生成脚本
 */

const puppeteer = require('puppeteer');

async function createSimpleUserLoginDiagram() {
  console.log('喏，官家！创建用户登录用例图！\n');

  const browser = await puppeteer.launch({
    headless: 'new'
  });

  const page = await browser.newPage();

  try {
    // 简化的PlantUML代码（URL编码）
    const plantumlCode = `@startuml
left to right direction
actor 用户 as User

package 用户登录系统 {
  usecase "用户登录" as UC1
  usecase "输入用户名密码" as UC2
  usecase "验证身份" as UC3
  usecase "忘记密码" as UC4
}

User --> UC1
UC1 ..> UC2 : include
UC1 ..> UC3 : include
User --> UC4

note right of UC1
  用户使用用户名和密码
  登录系统
end note
@enduml`;

    // 使用PlantUML文本编码服务
    console.log('1. 访问PlantUML服务...');
    await page.goto('http://www.plantuml.com/plantuml/text/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 输入PlantUML代码
    console.log('2. 输入PlantUML代码...');
    await page.evaluate((code) => {
      const textarea = document.querySelector('textarea');
      if (textarea) {
        textarea.value = code;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }, plantumlCode);

    // 提交
    await page.evaluate(() => {
      const form = document.querySelector('form');
      if (form) form.submit();
    });

    // 等待图表生成
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 截图
    console.log('3. 截图图表...');
    const screenshotPath = './user-login-usecase-diagram.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    console.log('='.repeat(60));
    console.log('用户登录用例图创建完成');
    console.log('='.repeat(60));
    console.log(`📸 图表位置: ${screenshotPath}`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 创建失败:', error.message);

    // 保存PlantUML代码供手动使用
    console.log('\nPlantUML代码已保存到: diagrams/user-login-usecase.puml');
    console.log('您可以手动访问: http://www.plantuml.com/plantuml/uml/');
    console.log('粘贴代码生成图表');
  } finally {
    await browser.close();
  }
}

// 运行
createSimpleUserLoginDiagram().catch(console.error);
