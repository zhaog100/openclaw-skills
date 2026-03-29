# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""多渠道通知服务"""
import hmac
import hashlib
import base64
import time
import json
from typing import Optional

import httpx

from api.config import settings


async def send_webhook(url: str, message: str) -> bool:
    """通用 Webhook 推送"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"text": message, "timestamp": int(time.time())})
            resp.raise_for_status()
            return True
    except Exception:
        return False


async def send_to_wecom(webhook_url: Optional[str] = None, content: str = "") -> bool:
    """企业微信机器人 Webhook"""
    url = webhook_url or settings.notify.wecom_webhook
    if not url:
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"msgtype": "text", "text": {"content": content}})
            resp.raise_for_status()
            return resp.json().get("errcode") == 0
    except Exception:
        return False


async def send_to_dingtalk(webhook_url: Optional[str] = None, content: str = "") -> bool:
    """钉钉机器人 Webhook（含签名验证）"""
    url = webhook_url or settings.notify.dingtalk_webhook
    if not url:
        return False
    try:
        timestamp = str(int(time.time() * 1000))
        secret = ""
        # 如 URL 含 secret 参数则提取
        if "secret=" in url:
            secret = url.split("secret=")[1]
            sign_str = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                secret.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256
            ).digest()
            sign = base64.urlsafe_b64encode(hmac_code).decode("utf-8")
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}timestamp={timestamp}&sign={sign}"

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json={"msgtype": "text", "text": {"content": content}})
            resp.raise_for_status()
            return resp.json().get("errcode") == 0
    except Exception:
        return False
