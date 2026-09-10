import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
通过 QQ 开放平台 API 发送消息
直接调用 HTTP API，绕过 openclaw CLI

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
版本: v3.4 | 石油黄金白银相关性分析
"""

import sys
import json
import os
import urllib.request
import urllib.error
import time
from pathlib import Path

# 配置 - 从环境变量读取敏感信息
QQ_API_BASE = "https://api.sgroup.qq.com"
APP_ID = os.environ.get("QQ_APP_ID", "")
APP_SECRET = os.environ.get("QQ_APP_SECRET", "")
TARGET_USER_ID = os.environ.get("QQ_TARGET_USER_ID", "")

# Token 缓存
_token_cache = None
_token_expire = 0


def get_access_token() -> str:
    """获取 QQ Bot AccessToken"""
    global _token_cache, _token_expire
    
    # 检查缓存
    if _token_cache and time.time() < _token_expire:
        return _token_cache
    
    # 获取新 token
    url = f"{QQ_API_BASE}/oauth2/access_token"
    params = {
        "appid": APP_ID,
        "client_secret": APP_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(f"{url}?{query}", method="GET")
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("access_token"):
                _token_cache = result["access_token"]
                _token_expire = time.time() + result.get("expires_in", 7200) - 300
                logger.info(f"[INFO] 获取 token 成功，有效期 {result.get('expires_in', 'unknown')}s")
                return _token_cache
            else:
                logger.info(f"[ERROR] 获取 token 失败: {result}", file=sys.stderr)
                return ""
    except urllib.error.HTTPError as e:
        logger.info(f"[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        logger.info(f"[ERROR] 响应: {e.read().decode('utf-8')}", file=sys.stderr)
        return ""
    except Exception as e:
        logger.info(f"[ERROR] 获取 token 异常: {e}", file=sys.stderr)
        return ""


def send_c2c_message(access_token: str, message: str, user_id: str = TARGET_USER_ID) -> bool:
    """发送私聊消息 (C2C)"""
    url = f"{QQ_API_BASE}/v2/users/{user_id}/messages"
    
    payload = {
        "msg_type": 0,
        "content": message
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"QQBot {access_token}"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("id"):
                logger.info(f"[INFO] 消息发送成功: id={result.get('id')}")
                return True
            else:
                logger.info(f"[ERROR] 发送失败: {result}", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        logger.info(f"[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        logger.info(f"[ERROR] 响应: {body}", file=sys.stderr)
        return False
    except Exception as e:
        logger.info(f"[ERROR] 发送异常: {e}", file=sys.stderr)
        return False


def main():
    report_file = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt"

    # 读取报告
    try:
        with open(report_file, "r") as f:
            message = f.read().strip()
    except FileNotFoundError:
        logger.info(f"[ERROR] 报告文件不存在: {report_file}", file=sys.stderr)
        sys.exit(1)

    if not message:
        logger.info("[ERROR] 报告内容为空", file=sys.stderr)
        sys.exit(1)

    # 获取 token 并发送
    token = get_access_token()
    if not token:
        sys.exit(1)

    success = send_c2c_message(token, message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
