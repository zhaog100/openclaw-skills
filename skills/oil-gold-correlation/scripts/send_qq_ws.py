#!/usr/bin/env python3
"""
通过 Gateway WebSocket API 发送 QQ 消息
绕过 CLI 不支持 qqbot 通道的问题

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
版本: v3.3 | 石油黄金白银相关性分析
"""

import sys
import json
import os
import asyncio
import uuid
import hashlib
from pathlib import Path

try:
    import websockets
except ImportError:
    print("[ERROR] 需要安装 websockets: pip install websockets", file=sys.stderr)
    sys.exit(1)

# 配置 - 从环境变量读取敏感信息
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789
TOKEN_FILE = Path.home() / ".openclaw" / "openclaw.json"
QQ_TARGET = os.environ.get("QQ_TARGET_USER_ID", "")


async def send_via_gateway(message: str, target: str = QQ_TARGET) -> bool:
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
    
    # 请求 ID 队列
    request_queue = asyncio.Queue()

    try:
        async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
            # 监听所有消息
            async def listen():
                """接收并分发消息到对应队列"""
                async for raw in ws:
                    msg = json.loads(raw)
                    msg_id = msg.get("id")
                    if msg_id:
                        await request_queue.put(msg)
                    # 忽略没有 id 的事件（如 health）

            listener = asyncio.create_task(listen())
            
            try:
                # 1. 等待 challenge
                print("[INFO] 等待连接挑战...")
                while True:
                    msg = await asyncio.wait_for(request_queue.get(), timeout=10)
                    if msg.get("type") == "event" and msg.get("event") == "connect.challenge":
                        nonce = msg["payload"]["nonce"]
                        ts = msg["payload"]["ts"]
                        print(f"[INFO] 收到 challenge: ts={ts}")
                        break
                    # 忽略其他事件

                # 2. 发送 connect 请求
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
                        "caps": [],
                        "commands": [],
                        "permissions": {},
                        "auth": {"token": token},
                        "locale": "zh-CN",
                        "userAgent": "oil-gold-cron/1.0"
                    }
                }
                await ws.send(json.dumps(connect_msg))
                print("[INFO] 发送 connect 请求...")

                # 3. 等待 connect 响应
                connect_response = None
                while True:
                    msg = await asyncio.wait_for(request_queue.get(), timeout=10)
                    if msg.get("id") == connect_id:
                        connect_response = msg
                        break

                if not connect_response or not connect_response.get("ok"):
                    print(f"[ERROR] 连接失败: {connect_response}", file=sys.stderr)
                    return False
                
                print("[INFO] Gateway 连接成功")

                # 4. 发送消息到当前会话
                send_id = str(uuid.uuid4())
                send_msg = {
                    "type": "req",
                    "id": send_id,
                    "method": "sessions.send",
                    "params": {
                        "sessionKey": "current",
                        "message": f"请通过 message 工具将以下内容发送到 QQ:\n\n{message}"
                    }
                }
                await ws.send(json.dumps(send_msg))
                print("[INFO] 发送消息请求...")

                # 5. 等待发送响应
                send_response = None
                while True:
                    msg = await asyncio.wait_for(request_queue.get(), timeout=30)
                    if msg.get("id") == send_id:
                        send_response = msg
                        break

                if send_response and send_response.get("ok"):
                    print(f"[INFO] 消息已提交处理")
                    return True
                else:
                    print(f"[ERROR] 发送失败: {send_response}", file=sys.stderr)
                    return False

            finally:
                listener.cancel()
                try:
                    await listener
                except asyncio.CancelledError:
                    pass

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

    success = asyncio.run(send_via_gateway(message))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
