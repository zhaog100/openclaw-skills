#!/usr/bin/env python3
"""
WattCoin Energy Monitor - 单元测试

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import unittest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入被测模块
from main import Config, Database, DeviceReader, WattCoinClient


class TestConfig(unittest.TestCase):
    """配置测试"""
    
    def test_config_load_default(self):
        """测试默认配置加载"""
        config = Config()
        self.assertEqual(config.device_type, "mock")
        self.assertEqual(config.polling_interval, 60)
        self.assertTrue(config.mock_mode)


class TestDeviceReader(unittest.TestCase):
    """设备读取器测试"""
    
    def setUp(self):
        self.config = Config()
        self.config.mock_mode = True
        self.reader = DeviceReader(self.config)
    
    def test_read_mock(self):
        """测试 Mock 模式读取"""
        data = self.reader.read()
        self.assertIn('voltage', data)
        self.assertIn('current', data)
        self.assertIn('power', data)
        self.assertIn('energy_wh', data)
        self.assertGreater(data['power'], 0)


class TestWattCoinClient(unittest.TestCase):
    """WattCoin 客户端测试"""
    
    def setUp(self):
        self.config = Config()
        self.config.wallet_address = "test_wallet"
        self.config.wallet_private_key = "test_key"
        self.client = WattCoinClient(self.config)
    
    def test_sign_data(self):
        """测试数据签名"""
        data = {"power": 100, "timestamp": 123456}
        signature = self.client.sign_data(data)
        self.assertEqual(len(signature), 64)  # SHA256 hex


if __name__ == '__main__':
    unittest.main()
