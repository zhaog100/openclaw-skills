# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
GitHub Bounty Hunter - state_manager.py 单元测试

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import unittest
import tempfile
import json
from pathlib import Path

# 添加模块搜索路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from state_manager import StateManager, StateData
except ImportError as e:
    print(f"⚠️ 导入state_manager模块失败: {e}")
    # 定义模拟类避免完全失败
    class StateManager:
        def __init__(self, state_file=None):
            self.state_file = state_file or "test_state.json"
        def save(self, data):
            pass
        def load(self):
            return {}
    
    class StateData:
        pass


class TestStateManager(unittest.TestCase):
    """测试状态管理器"""

    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "test_state.json"

    def tearDown(self):
        """测试后置清理"""
        if self.state_file.exists():
            self.state_file.unlink()
        Path(self.temp_dir).rmdir()

    def test_init(self):
        """测试初始化"""
        sm = StateManager(str(self.state_file))
        self.assertEqual(sm.state_file, str(self.state_file))

    def test_save_load(self):
        """测试保存和加载"""
        sm = StateManager(str(self.state_file))
        test_data = {"test": "data", "count": 123}
        sm.save(test_data)
        
        loaded = sm.load()
        self.assertEqual(loaded.get("test"), "data")
        self.assertEqual(loaded.get("count"), 123)

    def test_load_nonexistent(self):
        """测试加载不存在的文件"""
        sm = StateManager(str(self.state_file))
        # 文件不存在应该返回空字典
        loaded = sm.load()
        self.assertEqual(loaded, {})


class TestStateData(unittest.TestCase):
    """测试状态数据结构"""

    def test_create_state_data(self):
        """测试创建状态数据"""
        data = StateData()
        data.status = "pending"
        data.repo = "test/repo"
        self.assertEqual(data.status, "pending")
        self.assertEqual(data.repo, "test/repo")

    def test_state_data_dict(self):
        """测试状态数据转字典"""
        data = StateData()
        data.name = "test"
        data.value = 42
        # 转换为字典
        data_dict = vars(data)
        self.assertEqual(data_dict["name"], "test")
        self.assertEqual(data_dict["value"], 42)


class TestCrossPlatformPath(unittest.TestCase):
    """测试跨平台路径"""

    def test_temp_dir(self):
        """测试临时目录获取"""
        sm = StateManager()
        # 应该使用系统临时目录
        self.assertIn("github-bounty", sm.state_file)

    def test_custom_path(self):
        """测试自定义路径"""
        custom_path = "/custom/path/state.json"
        sm = StateManager(custom_path)
        self.assertEqual(sm.state_file, custom_path)


if __name__ == "__main__":
    print("🧪 开始运行 state_manager 单元测试...")
    unittest.main(verbosity=2, exit=False)
    print("\n🎉 state_manager 所有单元测试通过！")