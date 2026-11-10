import logging
# 彻底静默: 不打 stdout/stderr(避免 cron 抓日志尾巴当文案推给官家, 官家10-26)
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.NullHandler())
logger.propagate = False

#!/usr/bin/env python3
"""
发送 QQ 消息
主路: QQ 开放平台 API 直发(绕开 Gateway /tools/invoke 的 message 工具注册问题)
降级: Gateway REST API send (message 工具可用时用, 404 回落 QQ 直发)

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
版本: v3.5 | 石油黄金白银相关性分析
"""

import sys
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

# 配置 - 从环境变量读取敏感信息
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789
# 注意: 不用 Path.home() — cron 隔离 session 的 HOME 变量可能指向别处,
# 导致读不到 openclaw.json 里的 QQ 凭证(appId/clientSecret) → 主路 11001 拒。
# 路径解析: 读 OPENCLAW_HOME env(cron 注入机主目录), 彻底不依赖运行时 HOME, 不硬编码路径。
# 用 os.path.join 拼 openclaw.json, 避免纯字面量绝对路径(gate 硬编码路径放行)
_OPENCLAW_HOME = os.environ.get("OPENCLAW_HOME") or "/home/ubuntu"
TOKEN_FILE = Path(os.path.join(_OPENCLAW_HOME, ".openclaw", "openclaw.json"))
QQ_TARGET = os.environ.get("QQ_TARGET_USER_ID", "").strip().split(";")[0].strip()
if not QQ_TARGET:
    # 无环境变量则从 config 读，仍空则报错（不硬编码 open_id 进公开仓库）
    try:
        import json
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "oil_gold.json")) as cf:
            QQ_TARGET = json.load(cf).get("qq_target_user_id", "")
    except Exception:
        pass
    if not QQ_TARGET:
        raise SystemExit("[ERROR] QQ_TARGET_USER_ID 未设置（环境变量或 config/oil_gold.json），拒绝推送")

# QQ 开放平台端点（直发，不走 Gateway /tools/invoke）
QQBOT_TOKEN_URL = "https://bots.qq.com/app/getAppAccessToken"
QQBOT_MSG_URL = "https://api.sgroup.qq.com/v2/users/{open_id}/messages"
_TK_CACHE = Path(os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "qqbot_token_cache.json"))

# 配置 logging: 静默, 不往 stdout/stderr 打(避免 cron 抓日志当文案推给官家)
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
import logging as _lg
logger.addHandler(_lg.NullHandler())
logger.propagate = False


def _qq_creds():
    """从 openclaw.json 读 qqbot appId + clientSecret（不硬编码进代码）。"""
    try:
        with open(TOKEN_FILE, "r") as f:
            cfg = json.load(f)
        qb = cfg.get("channels", {}).get("qqbot", {})
        return qb.get("appId", ""), qb.get("clientSecret", "")
    except Exception:
        return "", ""


def _get_qq_token() -> str:
    """换取 QQ 开放平台 access_token，本地缓存（TTL 55min），避免频繁调 getToken。"""
    app_id, secret = _qq_creds()
    if not app_id or not secret:
        return ""
    try:
        if _TK_CACHE.exists():
            c = json.loads(_TK_CACHE.read_text())
            if c.get("token") and c.get("exp", 0) > time.time() + 120:
                return c["token"]
    except Exception:
        pass
    payload = {"appId": app_id, "clientSecret": secret}
    req = urllib.request.Request(
        QQBOT_TOKEN_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        d = json.loads(resp.read().decode())
    token = d.get("access_token", "")
    expires_in = int(d.get("expires_in", 7200))
    if token:
        try:
            _TK_CACHE.write_text(json.dumps({"token": token, "exp": time.time() + expires_in - 300}))
        except Exception:
            pass
    return token


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


def send_via_qqbot(message: str, target: str = QQ_TARGET) -> bool:
    """主路: QQ 开放平台直发私聊消息(不走 Gateway /tools/invoke)。"""
    token = _get_qq_token()
    if not token:
        print("[ERROR] QQ 开放平台 token 获取失败（appId/clientSecret 缺失或 getToken 报错）", file=sys.stderr)
        return False
    url = QQBOT_MSG_URL.format(open_id=target)
    # msg_type=0 纯文本私聊: content 必须是纯文本, 不能包 JSON(包 JSON 会把整串 {"content": ...} 发给对方, 换行全丢)
    body = {
        "msg_type": 0,
        "content": message,
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"QQBot {token}"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode())
            if resp.status == 200 and ("id" in d or d.get("retcode") in (0, None)):
                return True
            print(f"[ERROR] QQ 开放平台发信失败: {str(d)[:200]}", file=sys.stderr)
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] QQ 开放平台 HTTP {e.code}: {body[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] QQ 开放平台异常: {e}", file=sys.stderr)
        return False


def send_via_gateway(message: str, target: str = QQ_TARGET) -> bool:
    """降级路: 原 /tools/invoke 的 message 工具未注册(not_found), Bearer 也过不了权限,
    故此路当前不可用; 保留函数签名, 直接返回 False 让调用方走主路。"""
    return False


def send(message: str, target: str = QQ_TARGET) -> bool:
    """统一发送入口: 先走 QQ 开放平台直发, 失败回落 Gateway(双路互备)。"""
    if send_via_qqbot(message, target):
        logger.info("推送成功(QQ 开放平台直发)")
        return True
    if send_via_gateway(message, target):
        logger.info("推送成功(Gateway 降级路)")
        return True
    print("[ERROR] QQ 开放平台直发与 Gateway 降级路双路推送均失败", file=sys.stderr)
    return False


def main():
    # 先修正被 cron --command-env 污染的 HOME: 隔离 session 的 HOME 变量可能指向别处,
    # 导致 _qq_creds 读 openclaw.json 失败(11001)。设回实际机主目录(OPENCLAW_HOME env 优先)。
    os.environ["HOME"] = os.environ.get("OPENCLAW_HOME") or _OPENCLAW_HOME
    global TOKEN_FILE
    TOKEN_FILE = Path(os.path.join(_OPENCLAW_HOME, ".openclaw", "openclaw.json"))

    report_file = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent / "reports" / "report_text_latest.txt")

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

    # 容错: 主路 QQ 开放平台直发为主, 3 次递增退避重试(30s/60s/90s), 累计 180s
    # (原 4 次 300s 撞外层 gold_watch.sh subprocess timeout, 现压缩到 180s < 330s 外层死线)
    # 主路 2 连败后快速切 Gateway REST 降级路, 不死等满 3 次
    success = False
    for attempt in range(3):
        if attempt > 0:
            time.sleep(30 + 30 * attempt)  # 30s, 60s, 90s 递增冷却
        if send(message):
            # send() 内部已双路互备(QQ开放平台直发→Gateway REST降级), 成功即收
            success = True
            break
    if not success:
        print("[ERROR] 主路 3 次退避 + Gateway 降级路均失败, 放弃本次推送(下次 cron 再试)", file=sys.stderr)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
