"""
运行所有测试
"""

import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_extractor import TestKnowledgeExtractor
from test_relation import TestRelationExtractor
from test_graph import TestKnowledgeGraph


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestRelationExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeGraph))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
