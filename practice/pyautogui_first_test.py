#!/usr/bin/env python3
"""
PyAutoGUI第一个测试脚本 - 记事本自动化测试

前提条件：
1. PyAutoGUI已安装
2. 系统支持GUI（不是纯命令行环境）
"""

import pyautogui
import time
import sys

def test_notepad():
    """测试记事本自动化"""

    # 安全设置
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5

    print("=" * 50)
    print("PyAutoGUI记事本测试")
    print("=" * 50)

    # 练习1：获取屏幕尺寸
    print("\n练习1：获取屏幕尺寸")
    width, height = pyautogui.size()
    print(f"✅ 屏幕尺寸: {width}x{height}")

    # 练习2：获取鼠标位置
    print("\n练习2：获取鼠标位置")
    x, y = pyautogui.position()
    print(f"✅ 当前鼠标位置: ({x}, {y})")

    # 练习3：启动记事本（Windows/Linux）
    print("\n练习3：启动记事本")
    try:
        if sys.platform == 'win32':
            # Windows
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.typewrite('notepad')
            pyautogui.press('enter')
        else:
            # Linux
            pyautogui.hotkey('ctrl', 'alt', 't')  # 打开终端
            time.sleep(2)
            pyautogui.typewrite('gedit &', interval=0.1)  # 或者 gnome-text-editor
            pyautogui.press('enter')

        time.sleep(3)
        print("✅ 记事本已启动")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return

    # 练习4：输入文本
    print("\n练习4：输入文本")
    test_text = "Hello World! 这是PyAutoGUI测试。"
    try:
        pyautogui.typewrite(test_text, interval=0.05)
        print(f"✅ 已输入文本: {test_text}")
    except Exception as e:
        print(f"❌ 输入失败: {e}")

    time.sleep(1)

    # 练习5：全选和复制
    print("\n练习5：全选和复制")
    try:
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        print("✅ 已全选并复制")
    except Exception as e:
        print(f"❌ 操作失败: {e}")

    time.sleep(1)

    # 练习6：截图
    print("\n练习6：截图")
    try:
        screenshot_path = '/tmp/pyautogui_test_screenshot.png'
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        print(f"✅ 截图已保存: {screenshot_path}")
    except Exception as e:
        print(f"❌ 截图失败: {e}")

    # 练习7：关闭记事本
    print("\n练习7：关闭记事本")
    try:
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1)
        # 不保存
        if sys.platform == 'win32':
            pyautogui.press('tab')  # 选择"不保存"
            pyautogui.press('enter')
        print("✅ 记事本已关闭")
    except Exception as e:
        print(f"❌ 关闭失败: {e}")

    print("\n🎉 所有练习完成！")

def test_basic_operations():
    """测试基本操作（不需要GUI）"""

    print("=" * 50)
    print("PyAutoGUI基本操作测试")
    print("=" * 50)

    # 练习1：安全设置
    print("\n练习1：安全设置")
    print(f"✅ FAILSAFE: {pyautogui.FAILSAFE}")
    print(f"✅ PAUSE: {pyautogui.PAUSE}")

    # 练习2：屏幕信息
    print("\n练习2：屏幕信息")
    try:
        width, height = pyautogui.size()
        print(f"✅ 屏幕尺寸: {width}x{height}")
    except Exception as e:
        print(f"❌ 获取屏幕尺寸失败: {e}")
        print("   （可能是因为没有GUI环境）")

    # 练习3：位置信息
    print("\n练习3：位置信息")
    try:
        x, y = pyautogui.position()
        print(f"✅ 当前鼠标位置: ({x}, {y})")
    except Exception as e:
        print(f"❌ 获取鼠标位置失败: {e}")
        print("   （可能是因为没有GUI环境）")

    # 练习4：计算
    print("\n练习4：移动计算")
    try:
        # 计算移动到屏幕中心的时间
        width, height = pyautogui.size()
        center_x, center_y = width / 2, height / 2
        print(f"✅ 屏幕中心坐标: ({center_x}, {center_y})")
        print(f"   移动到中心命令: pyautogui.moveTo({center_x}, {center_y}, duration=1)")
    except Exception as e:
        print(f"❌ 计算失败: {e}")

    print("\n🎉 基本操作测试完成！")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='PyAutoGUI测试脚本')
    parser.add_argument('--basic', action='store_true', help='只测试基本操作（不需要GUI）')
    parser.add_argument('--notepad', action='store_true', help='测试记事本自动化（需要GUI）')

    args = parser.parse_args()

    if args.basic:
        test_basic_operations()
    elif args.notepad:
        test_notepad()
    else:
        print("请选择测试模式：")
        print("  --basic  : 测试基本操作（不需要GUI）")
        print("  --notepad: 测试记事本自动化（需要GUI）")
        print("\n示例：")
        print("  python3 pyautogui_first_test.py --basic")
        print("  python3 pyautogui_first_test.py --notepad")
