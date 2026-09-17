#!/bin/bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# check_gmail_payments.sh - Gmail付款通知监控脚本

SECRETS_FILE="$HOME/.openclaw/secrets/gmail.env"
LOG_FILE="$HOME/.openclaw/workspace/logs/gmail_payment_monitor.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "📧 开始检查Gmail付款通知..."

# 加载凭据
if [ -f "$SECRETS_FILE" ]; then
    export $(grep -v '^#' "$SECRETS_FILE" | xargs)
    log "用户: $GMAIL_USER"
else
    echo "⚠️ 凭据文件不存在"; exit 1
fi

# Python脚本检查（优化版）
timeout 25 python3 << 'PYEOF'
import imaplib, email, sys, os
from email.header import decode_header
from datetime import datetime, timedelta

user = os.environ.get('GMAIL_USER', '')
password = os.environ.get('GMAIL_PASS', '')
lookback_hours = int(os.environ.get('LOOKBACK_HOURS', '12'))  # 缩短到12小时
keywords = ['bounty', 'rtc', 'payment', 'paid']  # 只保留最相关的4个

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993, timeout=10)
    mail.login(user, password)
    mail.select('INBOX')
    
    since_date = (datetime.now() - timedelta(hours=lookback_hours)).strftime('%d-%b-%Y')
    found = []
    
    for kw in keywords:
        status, msgs = mail.search(None, f'SUBJECT "{kw}" SINCE {since_date}')
        if status == 'OK' and msgs[0]:
            ids = msgs[0].split()
            # 只检查最近10封
            for mid in ids[-10:]:
                status, data = mail.fetch(mid, '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    subj = decode_header(msg['Subject'])[0]
                    if isinstance(subj[0], bytes):
                        subj = subj[0].decode(subj[1] or 'utf-8')
                    else:
                        subj = subj[0]
                    if subj not in found:
                        found.append(str(subj))
    
    mail.logout()
    
    if not found:
        print(f"✅ 过去{lookback_hours}小时内无付款相关邮件")
    else:
        print(f"📬 找到 {len(found)} 封付款相关邮件：")
        for i, subj in enumerate(found[-5:], 1):
            print(f"{i}. {subj[:80]}")
except Exception as e:
    print(f"⚠️ 检查失败: {e}")
PYEOF

log "✅ 检查完成"
