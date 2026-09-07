#!/usr/bin/env python3
"""
发送QQ消息到指定用户
通过Gateway REST API

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789
TOKEN_FILE = Path.home() / ".openclaw" / "openclaw.json"


def get_gateway_token() -> str:
    """读取Gateway Token"""
    try:
        with open(TOKEN_FILE, "r") as f:
            config = json.load(f)
        token = config.get("gateway", {}).get("auth", {}).get("token", "")
        if not token:
            print("[ERROR] 无法获取Gateway Token", file=sys.stderr)
            return ""
        return token
    except Exception as e:
        print(f"[ERROR] 读取token失败: {e}", file=sys.stderr)
        return ""


def send_qq_message(message: str, target_id: str) -> bool:
    """发送QQ消息"""
    token = get_gateway_token()
    if not token:
        return False

    payload = {
        "tool": "message",
        "action": "send",
        "args": {
            "channel": "qqbot",
            "target": f"qqbot:c2c:{target_id}",
            "message": message
        }
    }

    url = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/tools/invoke"

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("ok") or "result" in result:
                print(f"[INFO] 消息发送成功")
                return True
            else:
                print(f"[ERROR] 发送失败: {result}", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[ERROR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        print(f"[ERROR] 响应: {body}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] 发送异常: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 3:
        print("用法: send_qq_msg.py <消息> <QQ目标ID>", file=sys.stderr)
        sys.exit(1)

    message = sys.argv[1]
    target_id = sys.argv[2]

    success = send_qq_message(message, target_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
