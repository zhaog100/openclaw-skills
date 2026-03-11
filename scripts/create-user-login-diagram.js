/**
 * 用户登录用例图生成脚本
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function createUserLoginDiagram() {
  console.log('喏，官家！开始创建用户登录用例图！\n');

  const plantumlCode = `@startuml
left to right direction
actor 用户 as User
actor 管理员 as Admin

package 用户登录系统 {
  usecase "用户登录" as UC1
  usecase "输入用户名密码" as UC2
  usecase "验证身份" as UC3
  usecase "忘记密码" as UC4
  usecase "重置密码" as UC5
  usecase "管理员登录" as UC6
  usecase "查看登录日志" as UC7
}

User --> UC1
UC1 ..> UC2 : include
UC1 ..> UC3 : include
User --> UC4
UC4 ..> UC5 : extend

Admin --> UC6
UC6 ..> UC3 : include
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

  console.log('生成的PlantUML代码:');
  console.log(plantumlCode);
  console.log('');

  // 使用PlantUML在线编辑器
  const browser = await puppeteer.launch({
    headless: 'new'
  });

  const page = await browser.newPage();

  try {
    // 访问PlantUML在线编辑器
    console.log('1. 访问PlantUML在线编辑器...');
    await page.goto('http://www.plantuml.com/plantuml/uml/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 在编辑器中输入代码
    console.log('2. 输入PlantUML代码...');
    await page.evaluate((code) => {
      const textarea = document.querySelector('textarea');
      if (textarea) {
        textarea.value = code;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }, plantumlCode);

    // 等待图表生成
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 截图
    console.log('3. 截图图表...');
    const screenshotPath = './user-login-usecase-diagram.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    console.log('='.repeat(60));
    console.log('用户登录用例图创建完成');
    console.log('='.repeat(60));
    console.log(`📸 图表位置: ${screenshotPath}`);
    console.log(`📄 代码位置: diagrams/user-login-usecase.puml`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 创建失败:', error.message);

    // 保存错误截图
    try {
      await page.screenshot({ path: './user-login-error.png' });
      console.log('错误截图已保存: ./user-login-error.png');
    } catch (e) {
      console.log('截图失败');
    }
  } finally {
    await browser.close();
  }
}

// 运行
createUserLoginDiagram().catch(console.error);
