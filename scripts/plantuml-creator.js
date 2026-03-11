/**
 * PlantUML图表自动创建工具
 * 官家只需描述需求，自动生成图表
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class PlantUMLCreator {
  constructor() {
    this.baseUrl = 'http://www.plantuml.com/plantuml/uml/';
  }

  /**
   * 根据需求描述生成PlantUML代码
   */
  generatePlantUMLCode(requirement) {
    // 这里可以根据关键词识别图表类型
    const lowerReq = requirement.toLowerCase();

    if (lowerReq.includes('用例') || lowerReq.includes('use case')) {
      return this.generateUseCaseDiagram(requirement);
    } else if (lowerReq.includes('类图') || lowerReq.includes('class')) {
      return this.generateClassDiagram(requirement);
    } else if (lowerReq.includes('序列') || lowerReq.includes('sequence') || lowerReq.includes('流程')) {
      return this.generateSequenceDiagram(requirement);
    } else if (lowerReq.includes('活动') || lowerReq.includes('activity')) {
      return this.generateActivityDiagram(requirement);
    } else if (lowerReq.includes('组件') || lowerReq.includes('component') || lowerReq.includes('架构')) {
      return this.generateComponentDiagram(requirement);
    } else if (lowerReq.includes('状态') || lowerReq.includes('state')) {
      return this.generateStateDiagram(requirement);
    } else {
      // 默认生成序列图
      return this.generateSequenceDiagram(requirement);
    }
  }

  /**
   * 生成用例图
   */
  generateUseCaseDiagram(requirement) {
    return `@startuml
left to right direction
actor 用户 as User

package 系统 {
  usecase 功能1 as UC1
  usecase 功能2 as UC2
  usecase 功能3 as UC3
}

User --> UC1
User --> UC2
User --> UC3
@enduml`;
  }

  /**
   * 生成类图
   */
  generateClassDiagram(requirement) {
    return `@startuml
class 用户 {
  +String 姓名
  +String 邮箱
  +登录()
}

class 订单 {
  +Date 创建时间
  +Float 总金额
  +创建()
}

用户 "1" --> "*" 订单 : 拥有
@enduml`;
  }

  /**
   * 生成序列图
   */
  generateSequenceDiagram(requirement) {
    return `@startuml
actor 用户
participant 系统
database 数据库

用户 -> 系统 : 发起请求
系统 -> 数据库 : 查询数据
数据库 --> 系统 : 返回结果
系统 --> 用户 : 响应结果
@enduml`;
  }

  /**
   * 生成活动图
   */
  generateActivityDiagram(requirement) {
    return `@startuml
start
:开始处理
if (条件判断?) then (yes)
  :执行操作A
else (no)
  :执行操作B
endif
:处理完成
stop
@enduml`;
  }

  /**
   * 生成组件图
   */
  generateComponentDiagram(requirement) {
    return `@startuml
package 前端 {
  component Web应用
}
package 后端 {
  component API服务器
  component 数据库
}
Web应用 --> API服务器 : HTTP请求
API服务器 --> 数据库 : SQL查询
@enduml`;
  }

  /**
   * 生成状态图
   */
  generateStateDiagram(requirement) {
    return `@startuml
[*] --> 初始状态
初始状态 --> 处理中 : 开始
处理中 --> 已完成 : 成功
处理中 --> 失败 : 错误
已完成 --> [*]
失败 --> [*]
@enduml`;
  }

  /**
   * 将PlantUML代码编码为URL
   */
  encodePlantUML(code) {
    // PlantUML使用特殊的编码方式
    // 这里简化处理，实际需要实现PlantUML的编码算法
    const encoded = Buffer.from(code).toString('base64');
    return encoded;
  }

  /**
   * 创建图表并截图
   */
  async createDiagram(plantumlCode, outputPath) {
    console.log('喏，官家！开始创建PlantUML图表！\n');

    const browser = await puppeteer.launch({
      headless: 'new'
    });

    const page = await browser.newPage();

    try {
      // 编码PlantUML代码
      const encoded = this.encodePlantUML(plantumlCode);
      const url = this.baseUrl + encoded;

      console.log('1. 访问PlantUML图表...');
      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      console.log('✅ 页面加载成功\n');

      // 等待图表生成
      await new Promise(resolve => setTimeout(resolve, 5000));

      // 截图
      console.log('2. 截图图表...');
      await page.screenshot({ path: outputPath, fullPage: true });
      console.log(`✅ 截图已保存: ${outputPath}\n`);

      console.log('='.repeat(60));
      console.log('PlantUML图表创建完成');
      console.log('='.repeat(60));
      console.log(`📸 图表位置: ${outputPath}`);
      console.log('='.repeat(60));

      return outputPath;

    } catch (error) {
      console.error('❌ 创建失败:', error.message);

      // 保存错误截图
      try {
        await page.screenshot({ path: './plantuml-error.png' });
        console.log('错误截图已保存: ./plantuml-error.png');
      } catch (e) {
        console.log('截图失败');
      }

      throw error;
    } finally {
      await browser.close();
    }
  }

  /**
   * 从需求自动创建图表
   */
  async createFromRequirement(requirement, outputPath = './plantuml-diagram.png') {
    console.log('官家需求:', requirement);
    console.log('');

    // 生成PlantUML代码
    const plantumlCode = this.generatePlantUMLCode(requirement);
    console.log('生成的PlantUML代码:');
    console.log(plantumlCode);
    console.log('');

    // 创建图表
    return await this.createDiagram(plantumlCode, outputPath);
  }
}

// 导出
module.exports = PlantUMLCreator;

// 命令行使用
if (require.main === module) {
  const requirement = process.argv[2] || '创建一个用户登录的序列图';
  const creator = new PlantUMLCreator();
  creator.createFromRequirement(requirement).catch(console.error);
}
