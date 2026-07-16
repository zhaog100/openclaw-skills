#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东黑色星期五自动抢券脚本
兼容青龙面板 (Qinglong Panel) 环境
版本: v1.0.1
作者: 小米椒 (xiaomijiao)
日期: 2026-07-03

功能:
- 自动领取京东优惠券（黑色星期五专题）
- 支持多账号
- 支持青龙面板环境变量 JD_COOKIE
- 日志输出到 stdout（青龙面板可捕获）

环境要求:
- Python 3.8+
- requests 库
- 青龙面板 2.x

使用方法:
1. 在青龙面板 → 环境变量 → 添加:
   名称: JD_COOKIE
   值: pt_key=xxx;pt_pin=yyy; (多个用换行分隔)

2. 在青龙面板 → 定时任务 → 添加:
   名称: 黑色星期五抢券
   时间: 0 20 * * 4 (每周四 20:00)
   脚本: python3 /ql/data/scripts/jd-black-friday/jd_black_friday.py

3. 脚本会自动:
   - 读取 JD_COOKIE 环境变量
   - 解析每个账号的 pt_key 和 pt_pin
   - 调用京东优惠券接口领取
   - 输出领取结果

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ============================================================
# 配置
# ============================================================

# 京东优惠券接口（黑色星期五专题）
# 注意: 这些 URL 需要根据实际情况调整
COUPON_API_BASE = "https://api.m.jd.com/client.action"
COUPON_PAGE_URL = "https://pro.m.jd.com/mall/active/3byJ3jB2fGbBQ9tYvJ7vJ7vJ7vJ/index.html"

# 请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://pro.m.jd.com",
    "Referer": "https://pro.m.jd.com/",
    "X-Requested-With": "com.jingdong.app.mall",
    "Connection": "keep-alive",
}

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================
# 日志设置
# ============================================================

def setup_logging():
    """设置日志输出到 stdout（青龙面板可捕获）"""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================
# Cookie 解析
# ============================================================

def parse_jd_cookies(env_value: str) -> List[Dict[str, str]]:
    """
    解析 JD_COOKIE 环境变量
    支持格式:
    - pt_key=xxx;pt_pin=yyy;
    - pt_key=xxx; pt_pin=yyy;
    - 多行（每行一个账号）
    """
    cookies = []
    if not env_value:
        return cookies

    # 按行分割，支持多账号
    lines = env_value.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 移除多余空格
        line = ';'.join([p.strip() for p in line.split(';') if p.strip()])

        pt_key = None
        pt_pin = None

        parts = line.split(';')
        for part in parts:
            part = part.strip()
            if part.startswith('pt_key='):
                pt_key = part.split('=', 1)[1]
            elif part.startswith('pt_pin='):
                pt_pin = part.split('=', 1)[1]

        if pt_key and pt_pin:
            cookies.append({
                'pt_key': pt_key,
                'pt_pin': pt_pin,
                'raw': f'pt_key={pt_key};pt_pin={pt_pin};'
            })
            logger.info(f"解析到账号: pt_pin={pt_pin}")
        else:
            logger.warning(f"跳过无效 Cookie 行: {line[:50]}...")

    return cookies


def get_jd_cookies() -> List[Dict[str, str]]:
    """从环境变量获取 JD Cookie"""
    # 青龙面板环境变量
    env_value = os.environ.get('JD_COOKIE', '')

    # 如果环境变量为空，尝试从配置文件读取
    if not env_value:
        config_paths = [
            '/ql/data/config/config.sh',
            '/ql/config/config.sh',
        ]
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        for line in f:
                            if line.strip().startswith('export JD_COOKIE='):
                                env_value = line.strip().split('=', 1)[1].strip('"').strip("'")
                                break
                except Exception as e:
                    logger.warning(f"读取配置文件 {path} 失败: {e}")
                if env_value:
                    break

    if not env_value:
        logger.error("未找到 JD_COOKIE 环境变量或配置文件")
        return []

    return parse_jd_cookies(env_value)

# ============================================================
# 京东优惠券领取
# ============================================================

class JDCouponGrabber:
    """京东优惠券领取器"""

    def __init__(self, cookie: Dict[str, str]):
        self.cookie = cookie
        self.pt_pin = cookie['pt_pin']
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.headers['Cookie'] = cookie['raw']

    def _get_millisecond_timestamp(self) -> str:
        """获取毫秒时间戳"""
        return str(int(time.time() * 1000))

    def _build_coupon_url(self, coupon_id: str, role_id: str = "") -> str:
        """
        构建优惠券领取 URL
        注意: 实际 URL 需要根据京东最新接口调整
        """
        # 基础参数
        params = {
            "functionId": "grabCoupon",
            "appid": "jd_mp",
            "client": "android",
            "clientVersion": "12.0.0",
            "uuid": "88888",
            "body": json.dumps({
                "couponId": coupon_id,
                "roleId": role_id,
                "actId": "black_friday_2026",
            }),
            "_t": self._get_millisecond_timestamp(),
        }

        # 构建 URL
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{COUPON_API_BASE}?{query}"

    def grab_coupon(self, coupon_id: str, role_id: str = "") -> Tuple[bool, str]:
        """
        领取指定优惠券
        返回: (是否成功, 消息)
        """
        url = self._build_coupon_url(coupon_id, role_id)

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()

            data = resp.json()

            # 解析响应
            if data.get('code') == '0' or data.get('subCode') == '0':
                return True, f"✅ 优惠券 {coupon_id} 领取成功"
            elif data.get('subCode') == '10':
                return False, f"⏰ 优惠券 {coupon_id} 已领取过"
            elif data.get('subCode') == '17':
                return False, f"❌ 优惠券 {coupon_id} 已抢光"
            elif data.get('subCode') == '32':
                return False, f"❌ 优惠券 {coupon_id} 领取失败（风控）"
            else:
                msg = data.get('msg', data.get('subMsg', '未知错误'))
                return False, f"❌ 优惠券 {coupon_id} 领取失败: {msg}"

        except requests.exceptions.Timeout:
            return False, f"⏰ 优惠券 {coupon_id} 请求超时"
        except requests.exceptions.RequestException as e:
            return False, f"❌ 优惠券 {coupon_id} 网络错误: {str(e)[:50]}"
        except json.JSONDecodeError:
            return False, f"❌ 优惠券 {coupon_id} 响应解析失败"
        except Exception as e:
            return False, f"❌ 优惠券 {coupon_id} 异常: {str(e)[:50]}"

    def grab_black_friday_coupons(self) -> List[Tuple[bool, str]]:
        """
        领取黑色星期五优惠券
        注意: 以下 coupon_id 和 role_id 需要根据实际情况更新
        """
        results = []

        # 黑色星期五优惠券列表
        # ⚠️ 这些 ID 是示例，需要根据实际活动更新
        coupons = [
            # (coupon_id, role_id, 描述)
            ("755461154191", "", "满300减30 平台补贴券"),
            ("755461154195", "", "满300减30 平台补贴券"),
            ("755461154199", "", "满300减30 平台补贴券"),
        ]

        logger.info(f"开始领取黑色星期五优惠券，共 {len(coupons)} 张")

        for coupon_id, role_id, desc in coupons:
            logger.info(f"正在领取: {desc} ({coupon_id})")
            success, msg = self.grab_coupon(coupon_id, role_id)
            results.append((success, f"[{self.pt_pin}] {msg}"))
            logger.info(msg)

            # 避免请求过快
            time.sleep(1)

        return results


# ============================================================
# 主函数
# ============================================================

def main():
    """主入口"""
    logger.info("=" * 60)
    logger.info("🖤 京东黑色星期五自动抢券脚本 v1.0.1")
    logger.info("=" * 60)
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 获取 Cookie
    cookies = get_jd_cookies()
    if not cookies:
        logger.error("❌ 未找到有效的 JD_COOKIE，退出")
        sys.exit(1)

    logger.info(f"共找到 {len(cookies)} 个账号")

    # 2. 逐个账号抢券
    all_results = []
    for i, cookie in enumerate(cookies, 1):
        logger.info(f"\n{'='*40}")
        logger.info(f"【账号 {i}/{len(cookies)}】pt_pin={cookie['pt_pin']}")
        logger.info(f"{'='*40}")

        grabber = JDCouponGrabber(cookie)
        results = grabber.grab_black_friday_coupons()
        all_results.extend(results)

        # 账号间延迟
        if i < len(cookies):
            time.sleep(2)

    # 3. 输出汇总
    logger.info(f"\n{'='*60}")
    logger.info("📊 抢券结果汇总")
    logger.info(f"{'='*60}")

    success_count = sum(1 for s, _ in all_results if s)
    fail_count = len(all_results) - success_count

    for success, msg in all_results:
        logger.info(msg)

    logger.info(f"\n总计: {len(all_results)} 张优惠券")
    logger.info(f"✅ 成功: {success_count} 张")
    logger.info(f"❌ 失败: {fail_count} 张")
    logger.info(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 4. 返回状态码
    if fail_count == 0:
        logger.info("🎉 全部领取成功！")
        sys.exit(0)
    elif success_count > 0:
        logger.warning("⚠️ 部分领取成功")
        sys.exit(0)
    else:
        logger.error("❌ 全部领取失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
