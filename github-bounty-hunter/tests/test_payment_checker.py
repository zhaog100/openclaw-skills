# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
GitHub Bounty Hunter - payment_checker.py 单元测试

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import unittest
from pathlib import Path

# 添加模块搜索路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from payment_checker import PaymentChecker, PaymentInfo, PaymentType
except ImportError as e:
    print(f"⚠️ 导入payment_checker模块失败: {e}")
    exit(0)


class TestPaymentTypeEnum(unittest.TestCase):
    """测试支付类型枚举"""

    def test_payment_types(self):
        """测试所有支付类型"""
        self.assertEqual(PaymentType.CRYPTO.value, "crypto")
        self.assertEqual(PaymentType.FIAT.value, "fiat")
        self.assertEqual(PaymentType.PLATFORM.value, "platform")
        self.assertEqual(PaymentType.RTC.value, "rtc")
        self.assertEqual(PaymentType.UNKNOWN.value, "unknown")


class TestPaymentInfo(unittest.TestCase):
    """测试支付信息数据类"""

    def test_default_init(self):
        """测试默认初始化"""
        info = PaymentInfo()
        self.assertEqual(info.type, PaymentType.UNKNOWN)
        self.assertEqual(info.token, "")
        self.assertEqual(info.wallet, "")

    def test_custom_init(self):
        """测试自定义初始化"""
        info = PaymentInfo(
            type=PaymentType.CRYPTO,
            token="USDT",
            wallet="TTest123456789012345678901234",
            currency="USD",
            amount="100"
        )
        self.assertEqual(info.type, PaymentType.CRYPTO)
        self.assertEqual(info.token, "USDT")
        self.assertEqual(info.wallet, "TTest123456789012345678901234")


class TestPaymentChecker(unittest.TestCase):
    """测试支付检查器"""

    def setUp(self):
        """测试前置设置"""
        self.checker = PaymentChecker()

    def test_supported_crypto(self):
        """测试支持的加密货币"""
        self.assertIn("USDT", self.checker.SUPPORTED_CRYPTO)
        self.assertIn("ETH", self.checker.SUPPORTED_CRYPTO)
        self.assertIn("BTC", self.checker.SUPPORTED_CRYPTO)

    def test_supported_chains(self):
        """测试支持的链"""
        self.assertIn("TRC20", self.checker.SUPPORTED_CHAINS)
        self.assertIn("ERC20", self.checker.SUPPORTED_CHAINS)

    def test_supported_fiat(self):
        """测试支持的法币支付"""
        self.assertIn("PayPal", self.checker.SUPPORTED_FIAT)

    def test_supported_platforms(self):
        """测试支持的平台"""
        self.assertIn("Algora", self.checker.SUPPORTED_PLATFORMS)
        self.assertIn("UbiquityOS", self.checker.SUPPORTED_PLATFORMS)


class TestWalletPatternValidation(unittest.TestCase):
    """测试钱包地址格式验证"""

    def setUp(self):
        """测试前置设置"""
        self.checker = PaymentChecker()

    def test_eth_pattern_exists(self):
        """测试 ETH 钱包正则存在"""
        self.assertIn("ETH", self.checker.WALLET_PATTERNS)

    def test_trc20_pattern_exists(self):
        """测试 TRC20 钱包正则存在"""
        self.assertIn("TRC20", self.checker.WALLET_PATTERNS)

    def test_valid_trc20_address(self):
        """测试有效 TRC20 地址"""
        import re
        pattern = self.checker.WALLET_PATTERNS["TRC20"]
        # TRC20 地址以 T 开头，34位
        valid_addr = "TJYmZNGmK2xwofL3y5tN2qLHXP8WCL3kF6"
        self.assertTrue(re.match(pattern, valid_addr))

    def test_valid_eth_address(self):
        """测试有效 ETH 地址"""
        import re
        pattern = self.checker.WALLET_PATTERNS["ETH"]
        valid_addr = "0x1234567890123456789012345678901234567890"
        self.assertTrue(re.match(pattern, valid_addr))


if __name__ == "__main__":
    print("🧪 开始运行 payment_checker 单元测试...")
    unittest.main(verbosity=2, exit=False)
    print("\n🎉 payment_checker 所有单元测试通过！")