#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redmi K40 Gaming 自动化抓包工具
版本：v1.0.0
作者：米粒儿
"""

import subprocess
import time
import json
import os
from datetime import datetime

class DeviceAutoTool:
    def __init__(self):
        self.device_id = None
        self.cookies = {}

    def check_adb(self):
        """检查ADB连接"""
        print("=" * 60)
        print("Redmi K40 Gaming 自动化抓包工具")
        print("=" * 60)
        print(f"\n【步骤1】检查ADB连接...")

        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')

            devices = []
            for line in lines[1:]:
                if '\t' in line:
                    device_id, status = line.split('\t')
                    if status == 'device':
                        devices.append(device_id)

            if devices:
                self.device_id = devices[0]
                print(f"✅ 找到设备: {self.device_id}")

                # 获取设备信息
                model = subprocess.run(
                    ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.product.model'],
                    capture_output=True, text=True
                ).stdout.strip()

                print(f"   型号: {model}")
                return True
            else:
                print("❌ 未找到设备")
                print("\n请检查：")
                print("1. USB数据线已连接")
                print("2. 手机已开启USB调试")
                print("3. 已授权电脑调试")
                return False

        except FileNotFoundError:
            print("❌ ADB未安装")
            print("\n安装方法：")
            print("Windows: 下载 platform-tools")
            print("Mac: brew install android-platform-tools")
            print("Linux: sudo apt install android-tools-adb")
            return False

    def check_usb_debug(self):
        """检查USB调试是否开启"""
        print(f"\n【步骤2】检查USB调试...")

        if not self.device_id:
            return False

        try:
            # 尝试执行简单命令
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'echo', 'test'],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                print("✅ USB调试正常")
                return True
            else:
                print("❌ USB调试未授权")
                print("\n请在手机上点击「允许USB调试」")
                return False

        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False

    def get_device_info(self):
        """获取设备详细信息"""
        print(f"\n【步骤3】获取设备信息...")

        if not self.device_id:
            return None

        try:
            info = {}

            # 获取设备型号
            info['model'] = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.product.model'],
                capture_output=True, text=True
            ).stdout.strip()

            # 获取Android版本
            info['android'] = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.build.version.release'],
                capture_output=True, text=True
            ).stdout.strip()

            # 获取MIUI版本
            info['miui'] = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.miui.ui.version.name'],
                capture_output=True, text=True
            ).stdout.strip()

            print(f"✅ 设备信息:")
            print(f"   型号: {info['model']}")
            print(f"   Android: {info['android']}")
            print(f"   MIUI: {info['miui']}")

            return info

        except Exception as e:
            print(f"❌ 获取设备信息失败: {e}")
            return None

    def auto_click_douyin(self):
        """自动点击抖音极速版"""
        print(f"\n【步骤4】打开抖音极速版...")

        if not self.device_id:
            return False

        try:
            # 打开抖音极速版
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'am', 'start',
                 '-n', 'com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.splash.SplashActivity'],
                timeout=10
            )

            print("✅ 已打开抖音极速版")
            print("⏰ 等待5秒加载...")
            time.sleep(5)

            return True

        except Exception as e:
            print(f"❌ 打开失败: {e}")
            return False

    def get_cookie_guide(self):
        """获取Cookie指导"""
        print("\n" + "=" * 60)
        print("【手动获取Cookie方法】")
        print("=" * 60)

        print("\n方法1：通过浏览器（最简单）")
        print("1. 打开Chrome浏览器")
        print("2. 按F12 → Application → Cookies")
        print("3. 找到抖音极速版相关Cookie")

        print("\n方法2：通过ADB logcat（推荐）")
        print("1. 手机连接电脑")
        print("2. 打开抖音极速版")
        print("3. 执行命令：adb logcat | grep 'cookie'")
        print("4. 找到Cookie字符串")

        print("\n方法3：使用抓包工具（最准确）")
        print("1. 安装mitmproxy")
        print("2. 手机设置代理")
        print("3. 打开抖音极速版")
        print("4. 查看抓包记录")

        print("\n" + "=" * 60)

    def run(self):
        """主流程"""
        # 检查ADB
        if not self.check_adb():
            return

        # 检查USB调试
        if not self.check_usb_debug():
            return

        # 获取设备信息
        device_info = self.get_device_info()

        # 打开抖音极速版
        if self.auto_click_douyin():
            # 显示获取Cookie指导
            self.get_cookie_guide()

        print("\n" + "=" * 60)
        print("后续版本将支持自动抓包")
        print("当前版本：v1.0.0（基础版）")
        print("=" * 60)

if __name__ == "__main__":
    tool = DeviceAutoTool()
    tool.run()
