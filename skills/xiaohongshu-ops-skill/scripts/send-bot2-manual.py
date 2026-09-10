#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot2操作手册推送脚本
通过bot2发送操作手册和FAQ给官家
"""

import sys
from datetime import datetime

def send_manual():
    """通过bot2发送操作手册"""
    logger.info(f"=== 推送操作手册到bot2 ===")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info()
    logger.info("📢 推送内容:")
    logger.info("1. 商贸模式使用说明")
    logger.info("   - 文件路径: /root/.openclaw/workspace/intel/商贸模式使用说明.md")
    logger.info("   - 包含: 助手功能/常用操作/定时推送/常见问题")
    logger.info()
    logger.info("2. 商贸模式常用操作")
    logger.info("   - 文件路径: /root/.openclaw/workspace/intel/商贸模式常用操作.md")
    logger.info("   - 包含: 6个常用操作/快速指令速查/常见问题FAQ")
    logger.info()
    logger.info("3. 商贸模式状态更新")
    logger.info("   - 文件路径: /root/.openclaw/workspace/intel/商贸模式状态更新.md")
    logger.info("   - 包含: 已完成工作/当前模式/定时任务/下一步")
    logger.info()
    logger.info("目标: bot2通道 (QQ bot2: 1903724446)")
    logger.info()
    logger.info("推送方式: 通过OpenClaw cron job执行，等待bot2推送到官家QQ")

    return True

def main():
    success = send_manual()
    if success:
        logger.info("\n✅ 推送脚本执行成功")
        logger.warning("⚠️  实际推送需要通过cron job执行，等待bot2推送...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
