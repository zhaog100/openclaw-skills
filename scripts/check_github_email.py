#!/usr/bin/env python3
"""检查Gmail中未读的GitHub通知邮件，输出最近的通知摘要"""
import imaplib
import email
import os
import sys
from datetime import datetime, timedelta

# 读取凭证
env_file = os.path.expanduser("~/.openclaw/secrets/gmail.env")
user = pass_ = None
with open(env_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith("GMAIL_USER="): user = line.split("=",1)[1]
        elif line.startswith("GMAIL_PASS="): pass_ = line.split("=",1)[1]

if not user or not pass_:
    print("ERROR: Gmail凭证未配置")
    sys.exit(1)

m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pass_)
m.select("INBOX")

# 搜索最近12小时的GitHub邮件
since = (datetime.utcnow() - timedelta(hours=12)).strftime("%d-%b-%Y")
status, msgs = m.search(None, f'(FROM "notifications@github.com" SINCE {since})')
ids = msgs[0].split()

if not ids:
    print("NO_UNREAD")
    m.logout()
    sys.exit(0)

# 读取最近10封
recent = ids[-10:]
notifications = []
for eid in reversed(recent):
    status, data = m.fetch(eid, "(RFC822)")
    msg = email.message_from_bytes(data[0][1])
    subject = str(email.header.make_header(email.header.decode_header(msg["Subject"])))
    date = msg["Date"] or ""
    # 提取body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")[:500]
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")[:500] if msg.get_payload(decode=True) else ""

    notifications.append({"subject": subject, "date": date, "body": body.strip()})

for n in notifications:
    print(f"📧 {n['subject']}")
    print(f"   {n['date']}")
    if n['body']:
        print(f"   {n['body'][:200]}")
    print()

m.logout()
