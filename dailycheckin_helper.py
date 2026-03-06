#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dailycheckin配置助手和优化器
作者：米粒儿 🌾
功能：
1. 验证配置文件格式
2. 检查Cookie有效性
3. 提供友好的错误提示
4. 生成配置模板
"""

import json
import os
import sys
from pathlib import Path


class DailyCheckinHelper:
    """dailycheckin配置助手"""

    # 各平台配置要求
    PLATFORM_REQUIREMENTS = {
        "ALIYUN": {
            "name": "阿里云盘",
            "required_fields": ["refresh_token"],
            "optional_fields": ["name"],
            "get_cookie_guide": "访问 https://www.aliyundrive.com 登录后，从浏览器开发者工具获取 refresh_token"
        },
        "BAIDUWP": {
            "name": "百度网盘",
            "required_fields": ["cookie"],
            "optional_fields": ["name"],
            "get_cookie_guide": "访问 https://pan.baidu.com 登录后，从浏览器Cookie中提取 BDUSS 值"
        },
        "BILIBILI": {
            "name": "B站",
            "required_fields": ["cookie"],
            "optional_fields": ["name"],
            "required_cookie_keys": ["SESSDATA", "bili_jct", "DedeUserID"],
            "get_cookie_guide": "访问 https://www.bilibili.com 登录后，从浏览器Cookie中提取 SESSDATA, bili_jct, DedeUserID"
        },
        "IQIYI": {
            "name": "爱奇艺",
            "required_fields": ["cookie"],
            "optional_fields": ["name"],
            "required_cookie_keys": ["P00001", "P00002", "P00003"],
            "get_cookie_guide": "访问 https://www.iqiyi.com 登录后，从浏览器Cookie中提取 P00001, P00002, P00003"
        },
        "SMZDM": {
            "name": "什么值得买",
            "required_fields": ["cookie"],
            "optional_fields": ["name"],
            "get_cookie_guide": "访问 https://www.smzdm.com 登录后，从浏览器Cookie中提取完整cookie字符串"
        },
        "TIEBA": {
            "name": "百度贴吧",
            "required_fields": ["cookie"],
            "optional_fields": ["name"],
            "required_cookie_keys": ["BDUSS", "STOKEN"],
            "get_cookie_guide": "访问 https://tieba.baidu.com 登录后，从浏览器Cookie中提取 BDUSS, STOKEN"
        }
    }

    def __init__(self, config_path="/ql/config/config.json"):
        self.config_path = config_path
        self.config = {}
        self.errors = []
        self.warnings = []
        self.valid_accounts = []

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self.errors.append(f"❌ 配置文件不存在: {self.config_path}")
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ 配置文件JSON格式错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ 读取配置文件失败: {e}")
            return False

    def validate_platform_config(self, platform_key, accounts):
        """验证单个平台的配置"""
        if not accounts:
            return

        platform_info = self.PLATFORM_REQUIREMENTS.get(platform_key)
        if not platform_info:
            self.warnings.append(f"⚠️  未知平台: {platform_key}")
            return

        platform_name = platform_info["name"]

        for idx, account in enumerate(accounts, 1):
            account_name = account.get("name", f"账号{idx}")

            # 检查占位符
            if any("你的" in str(v) or "xxx" in str(v).lower() for v in account.values()):
                self.warnings.append(
                    f"⚠️  [{platform_name}] {account_name}: 配置为占位符，将跳过"
                )
                continue

            # 检查必需字段
            missing_fields = []
            for field in platform_info["required_fields"]:
                if field not in account or not account[field]:
                    missing_fields.append(field)

            if missing_fields:
                self.errors.append(
                    f"❌ [{platform_name}] {account_name}: 缺少必需字段 {', '.join(missing_fields)}"
                )
                continue

            # 检查Cookie中的必需键（如果有要求）
            if "required_cookie_keys" in platform_info and "cookie" in account:
                cookie_str = account["cookie"]
                missing_keys = []
                for key in platform_info["required_cookie_keys"]:
                    if key not in cookie_str:
                        missing_keys.append(key)

                if missing_keys:
                    self.errors.append(
                        f"❌ [{platform_name}] {account_name}: Cookie中缺少 {', '.join(missing_keys)}"
                    )
                    continue

            # 配置有效
            self.valid_accounts.append(f"✅ [{platform_name}] {account_name}")

    def validate_all(self):
        """验证所有配置"""
        if not self.load_config():
            return False

        for platform_key, accounts in self.config.items():
            if isinstance(accounts, list):
                self.validate_platform_config(platform_key, accounts)

        return len(self.errors) == 0

    def print_report(self):
        """打印验证报告"""
        print("\n" + "="*60)
        print("📊 dailycheckin配置验证报告")
        print("="*60)

        if self.valid_accounts:
            print("\n✅ 有效配置:")
            for account in self.valid_accounts:
                print(f"  {account}")

        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  {error}")

        print("\n" + "="*60)
        print(f"📊 统计:")
        print(f"  有效账号: {len(self.valid_accounts)}")
        print(f"  警告: {len(self.warnings)}")
        print(f"  错误: {len(self.errors)}")
        print("="*60)

    def generate_template(self, output_path=None):
        """生成配置模板"""
        template = {}
        for platform_key, platform_info in self.PLATFORM_REQUIREMENTS.items():
            example_account = {"name": f"{platform_info['name']}账号1"}

            if "refresh_token" in platform_info["required_fields"]:
                example_account["refresh_token"] = f"你的{platform_info['name']}refresh_token"
            elif "cookie" in platform_info["required_fields"]:
                if "required_cookie_keys" in platform_info:
                    keys = platform_info["required_cookie_keys"]
                    example_account["cookie"] = "; ".join([f"{k}=你的{k}" for k in keys])
                else:
                    example_account["cookie"] = f"你的{platform_info['name']}cookie"

            template[platform_key] = [example_account]

        output = output_path or "/ql/config/config_template.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

        print(f"✅ 配置模板已生成: {output}")

    def print_get_cookie_guide(self):
        """打印获取Cookie的指南"""
        print("\n" + "="*60)
        print("📖 如何获取各平台Cookie")
        print("="*60)

        for platform_key, platform_info in self.PLATFORM_REQUIREMENTS.items():
            print(f"\n【{platform_info['name']}】")
            print(f"  方法: {platform_info['get_cookie_guide']}")
            if "required_cookie_keys" in platform_info:
                print(f"  必需: {', '.join(platform_info['required_cookie_keys'])}")

        print("\n" + "="*60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="dailycheckin配置助手")
    parser.add_argument("--config", default="/ql/config/config.json", help="配置文件路径")
    parser.add_argument("--template", action="store_true", help="生成配置模板")
    parser.add_argument("--guide", action="store_true", help="显示获取Cookie指南")
    parser.add_argument("--validate", action="store_true", help="验证配置")

    args = parser.parse_args()

    helper = DailyCheckinHelper(config_path=args.config)

    if args.template:
        helper.generate_template()
    elif args.guide:
        helper.print_get_cookie_guide()
    elif args.validate:
        helper.validate_all()
        helper.print_report()
    else:
        # 默认：验证 + 显示报告
        print("🔍 正在验证配置...")
        helper.validate_all()
        helper.print_report()

        if helper.errors:
            print("\n💡 建议:")
            print("  1. 运行 --guide 查看获取Cookie指南")
            print("  2. 运行 --template 生成配置模板")
            sys.exit(1)


if __name__ == "__main__":
    main()
