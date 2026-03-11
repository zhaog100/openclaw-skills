#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dailycheckin智能执行器
作者：米粒儿 🌾
功能：
1. 执行前自动验证配置
2. 只执行已配置的平台
3. 提供友好的错误提示
4. 记录执行日志
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class DailyCheckinRunner:
    """dailycheckin智能执行器"""

    def __init__(self, config_path="/ql/config/config.json"):
        self.config_path = config_path
        self.config = {}
        self.enabled_platforms = []

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            print(f"❌ 配置文件不存在: {self.config_path}")
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return False

    def check_platform_configured(self, platform_key, account):
        """检查平台是否已配置（非占位符）"""
        if not account:
            return False

        # 检查是否包含占位符
        for key, value in account.items():
            value_str = str(value)
            if "你的" in value_str or "xxx" in value_str.lower():
                return False

        # 检查必需字段
        if "cookie" in account and len(account["cookie"]) < 20:
            return False
        if "refresh_token" in account and len(account["refresh_token"]) < 20:
            return False

        return True

    def get_enabled_platforms(self):
        """获取已配置的平台列表"""
        if not self.load_config():
            return []

        enabled = []
        for platform_key, accounts in self.config.items():
            if isinstance(accounts, list) and len(accounts) > 0:
                # 检查第一个账号是否已配置
                if self.check_platform_configured(platform_key, accounts[0]):
                    enabled.append(platform_key)

        return enabled

    def run(self):
        """执行签到"""
        print("="*60)
        print(f"🕐 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # 获取已配置的平台
        self.enabled_platforms = self.get_enabled_platforms()

        if not self.enabled_platforms:
            print("❌ 没有已配置的平台，请先配置config.json")
            print("\n💡 运行以下命令获取帮助:")
            print("  python3 /ql/scripts/dailycheckin_helper.py --guide")
            print("  python3 /ql/scripts/dailycheckin_helper.py --template")
            return False

        print(f"\n✅ 已配置的平台: {', '.join(self.enabled_platforms)}")
        print(f"📊 将执行 {len(self.enabled_platforms)} 个平台的签到\n")

        # 执行dailycheckin
        try:
            # 构建include参数
            include_args = ["--include"] + self.enabled_platforms

            # 调用dailycheckin
            cmd = ["dailycheckin"] + include_args
            print(f"🚀 执行命令: {' '.join(cmd)}\n")

            result = subprocess.run(cmd, capture_output=False, text=True)

            if result.returncode == 0:
                print("\n" + "="*60)
                print("✅ 签到执行完成")
                print("="*60)
                return True
            else:
                print("\n" + "="*60)
                print(f"⚠️  签到执行完成（返回码: {result.returncode}）")
                print("="*60)
                return False

        except FileNotFoundError:
            print("❌ dailycheckin未安装")
            print("💡 运行: pip install dailycheckin -U")
            return False
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return False


def main():
    """主函数"""
    runner = DailyCheckinRunner()
    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
