#!/usr/bin/env python3
"""
Appium第一个测试脚本 - Android设置应用测试

前提条件：
1. Android模拟器已启动
2. Appium Server已启动（appium命令）
3. UiAutomator2驱动已安装
"""

from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

def test_android_settings():
    """测试Android设置应用"""

    # 配置选项
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'test_emulator'  # 模拟器名称
    options.app_package = 'com.android.settings'  # 设置应用包名
    options.app_activity = '.Settings'  # 设置应用Activity
    options.automation_name = 'UiAutomator2'

    # 连接Appium Server
    print("🔗 连接Appium Server...")
    driver = webdriver.Remote('http://localhost:4723', options=options)

    try:
        print("✅ 连接成功！")

        # 等待应用启动
        time.sleep(2)

        # 练习1：查找"网络和互联网"选项
        print("\n练习1：查找元素")
        try:
            network_option = driver.find_element('xpath', '//*[@text="网络和互联网"]')
            print(f"✅ 找到元素: {network_option.text}")
        except Exception as e:
            print(f"❌ 未找到元素: {e}")

        # 练习2：滑动屏幕
        print("\n练习2：滑动屏幕")
        size = driver.get_window_size()
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2
        start_x = size['width'] / 2

        driver.swipe(start_x, start_y, start_x, end_y, 800)
        print("✅ 向上滑动成功")
        time.sleep(1)

        # 练习3：查找"关于手机"选项
        print("\n练习3：查找关于手机")
        try:
            about_phone = driver.find_element('xpath', '//*[@text="关于手机"]')
            print(f"✅ 找到元素: {about_phone.text}")

            # 点击
            about_phone.click()
            print("✅ 点击成功")
            time.sleep(2)

            # 返回
            driver.back()
            print("✅ 返回成功")
            time.sleep(1)

        except Exception as e:
            print(f"❌ 操作失败: {e}")

        # 练习4：截图
        print("\n练习4：截图")
        screenshot_path = '/tmp/android_settings_screenshot.png'
        driver.save_screenshot(screenshot_path)
        print(f"✅ 截图已保存: {screenshot_path}")

        # 练习5：获取页面源码
        print("\n练习5：获取页面源码")
        page_source = driver.page_source
        with open('/tmp/android_settings_source.xml', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("✅ 页面源码已保存: /tmp/android_settings_source.xml")

        print("\n🎉 所有练习完成！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 关闭连接
        driver.quit()
        print("\n👋 已断开连接")

if __name__ == '__main__':
    print("=" * 50)
    print("Appium Android测试脚本")
    print("=" * 50)
    print("\n前提条件：")
    print("1. Android模拟器已启动")
    print("2. Appium Server已启动（运行：appium）")
    print("3. UiAutomator2驱动已安装（已安装✅）")
    print("\n按Enter键开始测试...")
    input()

    test_android_settings()
