#!/usr/bin/env python3
"""
通过 Gateway REST API 发送 QQ 消息
绕过 CLI 不支持 qqbot 频道的问题

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# 配置
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789
TOKEN_FILE = Path.home() / ".openclaw" / "openclaw.json"
QQ_TARGET = "C099848DC9A60BF60A7BE31626822790"


def get_gateway_token() -> str:
    """读取 Gateway Token"""
    try:
        with open(TOKEN_FILE, "r") as f:
            config = json.load(f)
        token = config.get("gateway", {}).get("auth", {}).get("token", "")
        if not token:
            print("[ERROR] 无法获取 Gateway Token", file=sys.stderr)
            return ""
        return token
    except Exception as e:
        print(f"[ERROR] 读取 token 失败: {e}", file=sys.stderr)
        return ""


def send_via_gateway(message: str, target: str = QQ_TARGET) -> bool:
    """通过 Gateway REST API 发送消息"""
    token = get_gateway_token()
    if not token:
        return False

    # 构造请求 body
    payload = {
        "tool": "message",
        "action": "send",
        "args": {
            "channel": "qqbot",
            "target": f"qqbot:c2c:{target}",
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
    report_file = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt"

    # 读取报告
    try:
        with open(report_file, "r") as f:
            message = f.read().strip()
    except FileNotFoundError:
        print(f"[ERROR] 报告文件不存在: {report_file}", file=sys.stderr)
        sys.exit(1)

    if not message:
        print("[ERROR] 报告内容为空", file=sys.stderr)
        sys.exit(1)

    success = send_via_gateway(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
