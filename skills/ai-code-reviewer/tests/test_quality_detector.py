#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检测器测试

**版本**：v1.0
**创建时间**：2026-03-15 23:45
**创建者**：小米粒（Dev 代理）🌾
"""

import unittest
import sys
import os

# 添加 lib 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'core'))

from quality_detector import CodeQualityDetector


class TestCodeQualityDetector(unittest.TestCase):
    """代码质量检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = CodeQualityDetector()
        self.test_code = '''
# 测试代码
def test_function():
    password = "admin123"
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    very_long_line_that_exceeds_120_characters_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
'''
    
    def test_detect_security_issues(self):
        """测试安全问题检测"""
        issues = self.detector._check_security(self.test_code, 'test.py')
        self.assertGreater(len(issues), 0)
        
        # 检查是否检测到硬编码密码
        password_issues = [i for i in issues if i.get('subtype') == 'hardcoded_password']
        self.assertGreater(len(password_issues), 0)
    
    def test_detect_standards_issues(self):
        """测试规范问题检测"""
        # 使用实际代码测试
        test_code = '''
def test():
    ''' + 'x' * 150 + '''
'''
        issues = self.detector._check_standards(test_code, 'test.py')
        self.assertGreater(len(issues), 0)
        
        # 检查是否检测到行长度问题
        line_length_issues = [i for i in issues if i.get('subtype') == 'line_length']
        self.assertGreater(len(line_length_issues), 0)
    
    def test_file_not_found(self):
        """测试文件不存在"""
        with self.assertRaises(FileNotFoundError):
            self.detector.detect('non_existent_file.py')


if __name__ == '__main__':
    unittest.main()
