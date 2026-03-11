#!/usr/bin/env python3
"""
青龙面板批量添加任务脚本
使用方法：python3 qinglong_batch_add.py
"""

import requests
import json
import sys

# 青龙面板配置
QL_URL = "http://43.133.55.138:5700"
USERNAME = ""  # 填写用户名
PASSWORD = ""  # 填写密码

# 京东任务列表（11个核心任务）
JD_TASKS = [
    {
        "name": "京东领京豆",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_beanSign.js",
        "schedule": "30 6 * * *"
    },
    {
        "name": "Cookie检查",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_CheckCK.js",
        "schedule": "0 7 * * *"
    },
    {
        "name": "京豆变化通知",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_bean_change.js",
        "schedule": "0 7 * * *"
    },
    {
        "name": "每日任务",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_daily.js",
        "schedule": "10 8 * * *"
    },
    {
        "name": "每日签到",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_dailysign.js",
        "schedule": "20 8 * * *"
    },
    {
        "name": "通用签到",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_sign.js",
        "schedule": "30 8 * * *"
    },
    {
        "name": "农场浇水",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_XinFarm_water.js",
        "schedule": "0 6,12,18 * * *"
    },
    {
        "name": "水果任务",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_fruit_new.js",
        "schedule": "30 7 * * *"
    },
    {
        "name": "种豆",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_plantBean.js",
        "schedule": "0 8 * * *"
    },
    {
        "name": "领京豆首页",
        "command": "/ql/scripts/jd_wrapper.sh node /ql/scripts/jd_faker2/jd_bean_home.js",
        "schedule": "0 7,13,19 * * *"
    },
    {
        "name": "京东优惠券",
        "command": "/ql/scripts/jd_wrapper.sh python3 /ql/scripts/jd_coupon_auto.py",
        "schedule": "30 9 * * *"
    }
]

def get_token():
    """获取登录token"""
    url = f"{QL_URL}/api/user/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()

        if result.get("code") == 200:
            token = result.get("data", {}).get("token")
            print(f"✅ 登录成功")
            return token
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def add_cron(token, task):
    """添加定时任务"""
    url = f"{QL_URL}/api/crons"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=task, headers=headers, timeout=10)
        result = response.json()

        if result.get("code") == 200:
            print(f"✅ {task['name']} - 添加成功")
            return True
        else:
            print(f"❌ {task['name']} - 添加失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ {task['name']} - 添加异常: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("青龙面板批量添加任务工具")
    print("=" * 60)

    # 检查配置
    if not USERNAME or not PASSWORD:
        print("\n❌ 请先配置用户名和密码")
        print("编辑脚本，填写 USERNAME 和 PASSWORD")
        sys.exit(1)

    # 获取token
    print("\n步骤1: 登录青龙面板...")
    token = get_token()
    if not token:
        sys.exit(1)

    # 批量添加任务
    print(f"\n步骤2: 批量添加 {len(JD_TASKS)} 个任务...")
    success = 0
    failed = 0

    for task in JD_TASKS:
        if add_cron(token, task):
            success += 1
        else:
            failed += 1

    # 总结
    print("\n" + "=" * 60)
    print(f"添加完成: ✅ {success} 个成功, ❌ {failed} 个失败")
    print("=" * 60)

    if success == len(JD_TASKS):
        print("\n🎉 所有任务添加成功！")
        print("💡 建议：登录Web界面验证任务是否正确加载")
        print(f"🔗 URL: {QL_URL}")

if __name__ == "__main__":
    main()
