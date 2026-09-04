#!/usr/bin/env python3
"""
直接通过 Gateway WebSocket sessions.send 发送 QQ 消息
绕过 CLI 不支持 qqbot 通道的问题

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import json
import asyncio
import uuid
from pathlib import Path

try:
    import websockets
except ImportError:
    print("[ERROR] 需要安装 websockets: pip install websockets", file=sys.stderr)
    sys.exit(1)

# 配置
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789
TOKEN_FILE = Path.home() / ".openclaw" / "openclaw.json"
QQ_TARGET = "C099848DC9A60BF60A7BE31626822790"


async def send_message(message: str) -> bool:
    """通过 Gateway WebSocket 发送消息"""
    # 读取 token
    try:
        with open(TOKEN_FILE, "r") as f:
            config = json.load(f)
        token = config.get("gateway", {}).get("auth", {}).get("token", "")
    except Exception as e:
        print(f"[ERROR] 读取 token 失败: {e}", file=sys.stderr)
        return False

    if not token:
        print("[ERROR] 无法获取 Gateway Token", file=sys.stderr)
        return False

    ws_url = f"ws://{GATEWAY_HOST}:{GATEWAY_PORT}/rpc"

    try:
        async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
            # 等待 challenge
            print("[INFO] 等待连接挑战...")
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            challenge = json.loads(raw)
            
            if challenge.get("event") != "connect.challenge":
                print(f"[ERROR] 期望 challenge: {challenge}", file=sys.stderr)
                return False
            
            nonce = challenge["payload"]["nonce"]
            ts = challenge["payload"]["ts"]
            print(f"[INFO] 收到 challenge")

            # 发送 connect
            connect_id = str(uuid.uuid4())
            connect_msg = {
                "type": "req",
                "id": connect_id,
                "method": "connect",
                "params": {
                    "minProtocol": 4,
                    "maxProtocol": 4,
                    "client": {
                        "id": "cli",
                        "version": "1.0.0",
                        "platform": "linux",
                        "mode": "operator"
                    },
                    "role": "operator",
                    "scopes": ["operator.write"],
                    "auth": {"token": token},
                    "locale": "zh-CN",
                    "userAgent": "oil-gold-cron/1.0",
                    "device": {
                        "id": f"device-{uuid.uuid4().hex[:12]}",
                        "publicKey": "test",
                        "signature": nonce,
                        "signedAt": int(ts / 1000),
                        "nonce": nonce
                    }
                }
            }
            await ws.send(json.dumps(connect_msg))

            # 等待响应
            response = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            if not response.get("ok"):
                print(f"[ERROR] 连接失败: {response}", file=sys.stderr)
                return False
            
            print("[INFO] Gateway 连接成功")

            # 发送消息到 QQ Bot 会话
            # 使用 sessions.send 直接发送到 qqbot 会话
            send_msg = {
                "type": "req",
                "id": str(uuid.uuid4()),
                "method": "sessions.send",
                "params": {
                    "sessionKey": f"agent:main:qqbot:c2c:{QQ_TARGET.lower()}",
                    "message": f"[系统自动推送]\n{message}"
                }
            }
            await ws.send(json.dumps(send_msg))
            
            # 等待响应
            response = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            if response.get("ok"):
                print(f"[INFO] 消息已提交: {response}")
                return True
            else:
                print(f"[ERROR] 发送失败: {response}", file=sys.stderr)
                return False

    except Exception as e:
        print(f"[ERROR] WebSocket 异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    report_file = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt"

    try:
        with open(report_file, "r") as f:
            message = f.read().strip()
    except FileNotFoundError:
        print(f"[ERROR] 报告文件不存在: {report_file}", file=sys.stderr)
        sys.exit(1)

    if not message:
        print("[ERROR] 报告内容为空", file=sys.stderr)
        sys.exit(1)

    success = asyncio.run(send_message(message))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
