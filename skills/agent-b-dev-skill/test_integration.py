#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-b-dev-skill 集成测试

测试范围：
- 模块间集成
- 完整工作流程
- 边界条件测试

日志：2026-03-15 米粒儿补充集成测试
"""

import sys
import unittest

# 导入被测试模块
from modules.tech_designer import TechDesigner
from modules.developer import Developer
from modules.publisher import Publisher
from modules.communicator import Communicator


class TestTechDesignerIntegration(unittest.TestCase):
    """技术设计师集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.designer = TechDesigner()
    
    def test_create_design_workflow(self):
        """测试技术设计工作流"""
        design_id = self.designer.create_design("prod_1", "微服务架构")
        self.assertTrue(design_id.startswith("design_"))
    
    def test_design_with_risk_assessment(self):
        """测试带风险评估的设计"""
        design_id = self.designer.create_design("prod_1", "架构")
        result = self.designer.add_risk_assessment(design_id, "技术风险")
        self.assertTrue(result)


class TestDeveloperIntegration(unittest.TestCase):
    """开发实现模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dev = Developer()
    
    def test_code_development_workflow(self):
        """测试代码开发工作流"""
        code_id = self.dev.write_code("design_1", "Python 实现")
        self.assertIsNotNone(code_id)
    
    def test_unit_test_workflow(self):
        """测试单元测试工作流"""
        test_result = self.dev.run_unit_tests("code_1")
        self.assertIsInstance(test_result, dict)


class TestPublisherIntegration(unittest.TestCase):
    """集成发布模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.pub = Publisher()
    
    def test_publish_workflow(self):
        """测试发布工作流"""
        # 准备发布
        prep_result = self.pub.prepare_release("code_1")
        self.assertIsInstance(prep_result, dict)
        
        # 执行发布
        publish_result = self.pub.execute_release("code_1")
        self.assertTrue(publish_result)


class TestCommunicatorIntegration(unittest.TestCase):
    """沟通协作模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.comm = Communicator()
    
    def test_send_message_workflow(self):
        """测试消息发送工作流"""
        result = self.comm.send_message("agent-a-pm", "开发完成")
        self.assertIsNotNone(result)


class TestFullWorkflow(unittest.TestCase):
    """完整工作流程集成测试"""
    
    def test_design_to_publish_workflow(self):
        """测试从设计到发布的完整工作流"""
        # 1. 技术设计
        designer = TechDesigner()
        design_id = designer.create_design("prod_1", "架构设计")
        
        # 2. 开发实现
        developer = Developer()
        code_id = developer.write_code(design_id, "代码实现")
        
        # 3. 单元测试
        test_result = developer.run_unit_tests(code_id)
        
        # 4. 发布准备
        publisher = Publisher()
        prep_result = publisher.prepare_release(code_id)
        
        # 5. 执行发布
        publish_result = publisher.execute_release(code_id)
        self.assertTrue(publish_result)
        
        # 6. 通知 PM
        comm = Communicator()
        result = comm.send_message("agent-a-pm", f"发布完成：{code_id}")
        self.assertIsNotNone(result)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestTechDesignerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDeveloperIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPublisherIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCommunicatorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFullWorkflow))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 agent-b-dev-skill 集成测试套件")
    print("=" * 50)
    print("")
    
    success = run_tests()
    
    print("")
    print("=" * 50)
    if success:
        print("✅ 所有集成测试通过！")
        sys.exit(0)
    else:
        print("❌ 有集成测试失败！")
        sys.exit(1)
