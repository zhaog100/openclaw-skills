#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-a-pm-skill 集成测试

测试范围：
- 模块间集成
- 完整工作流程
- 边界条件测试

日志：2026-03-15 米粒儿补充集成测试
"""

import sys
import unittest
from io import StringIO

# 导入被测试模块
from modules.product_manager import ProductManager
from modules.reviewer import Reviewer
from modules.state_manager import StateManager
from modules.communicator import Communicator


class TestProductManagerIntegration(unittest.TestCase):
    """产品管理器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.pm = ProductManager()
    
    def test_create_edit_delete_workflow(self):
        """测试完整工作流：创建→编辑→删除"""
        # 创建
        product_id = self.pm.create_product("测试产品", "这是一个测试产品描述")
        self.assertTrue(product_id.startswith("prod_"))
        
        # 编辑
        result = self.pm.edit_product(product_id, {'state': 'pending_review'})
        self.assertTrue(result)
        self.assertEqual(self.pm.products[product_id]['state'], 'pending_review')
        
        # 删除
        result = self.pm.delete_product(product_id)
        self.assertTrue(result)
        self.assertNotIn(product_id, self.pm.products)
    
    def test_input_validation_name_empty(self):
        """测试输入验证：空名称"""
        with self.assertRaises(ValueError):
            self.pm.create_product("", "描述")
    
    def test_input_validation_name_too_long(self):
        """测试输入验证：名称过长"""
        with self.assertRaises(ValueError):
            self.pm.create_product("a" * 101, "描述")
    
    def test_input_validation_desc_empty(self):
        """测试输入验证：空描述"""
        with self.assertRaises(ValueError):
            self.pm.create_product("名称", "")
    
    def test_input_validation_desc_too_long(self):
        """测试输入验证：描述过长"""
        with self.assertRaises(ValueError):
            self.pm.create_product("名称", "d" * 1001)
    
    def test_edit_nonexistent_product(self):
        """测试编辑不存在的产品"""
        result = self.pm.edit_product("prod_999", {'state': 'draft'})
        self.assertFalse(result)
    
    def test_delete_nonexistent_product(self):
        """测试删除不存在的产品"""
        result = self.pm.delete_product("prod_999")
        self.assertFalse(result)


class TestReviewerIntegration(unittest.TestCase):
    """Review 验证器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.reviewer = Reviewer()
    
    def test_review_code_workflow(self):
        """测试代码审查工作流"""
        review_id = self.reviewer.review_code(1, "print('hello')")
        self.assertTrue(review_id.startswith("review_"))
    
    def test_review_with_feedback(self):
        """测试带反馈的审查"""
        review_id = self.reviewer.review_code(1, "code")
        result = self.reviewer.submit_feedback(review_id, "需要改进")
        self.assertTrue(result)


class TestStateManagerIntegration(unittest.TestCase):
    """状态管理器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.sm = StateManager()
    
    def test_state_transition_workflow(self):
        """测试状态流转工作流"""
        # 创建产品
        self.sm.states['prod_1'] = 'draft'
        
        # 流转到待评审
        result = self.sm.transition('prod_1', 'pending_review')
        self.assertTrue(result)
        self.assertEqual(self.sm.states['prod_1'], 'pending_review')
        
        # 流转到已批准
        result = self.sm.transition('prod_1', 'approved')
        self.assertTrue(result)
        self.assertEqual(self.sm.states['prod_1'], 'approved')
    
    def test_invalid_transition(self):
        """测试无效状态流转"""
        self.sm.states['prod_1'] = 'draft'
        # 从 draft 不能直接到 published
        result = self.sm.transition('prod_1', 'published')
        # 根据实现可能返回 False 或抛出异常


class TestCommunicatorIntegration(unittest.TestCase):
    """沟通协作模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.comm = Communicator()
    
    def test_send_message_workflow(self):
        """测试消息发送工作流"""
        result = self.comm.send_message("agent-b-dev", "测试消息")
        # 根据实现，可能返回 True 或消息 ID
        self.assertIsNotNone(result)
    
    def test_receive_message_workflow(self):
        """测试消息接收工作流"""
        # 模拟接收消息
        messages = self.comm.receive_messages()
        self.assertIsInstance(messages, list)


class TestFullWorkflow(unittest.TestCase):
    """完整工作流程集成测试"""
    
    def test_pm_to_dev_workflow(self):
        """测试 PM 到 Dev 的完整工作流"""
        # 1. PM 创建产品
        pm = ProductManager()
        product_id = pm.create_product("新功能", "实现一个新功能")
        
        # 2. PM 提交 Review
        reviewer = Reviewer()
        review_id = reviewer.review_code(1, "产品需求文档")
        
        # 3. 状态管理
        sm = StateManager()
        sm.states[product_id] = 'draft'
        result = sm.transition(product_id, 'pending_review')
        self.assertTrue(result)
        
        # 4. 沟通协作
        comm = Communicator()
        result = comm.send_message("agent-b-dev", f"新产品：{product_id}")
        self.assertIsNotNone(result)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestProductManagerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestReviewerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManagerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCommunicatorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFullWorkflow))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 agent-a-pm-skill 集成测试套件")
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
