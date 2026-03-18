#!/bin/bash
# GitHub Bounty付款邮件检查脚本
# 每小时检查一次，发现付款邮件立即通知

GMAIL_USER="zhaog100@gmail.com"
GMAIL_PASS=$(grep GMAIL_PASS /root/.openclaw/secrets/gmail.env 2>/dev/null | cut -d= -f2)
LOG_FILE="/tmp/gmail_payment_check.log"
STATE_FILE="/tmp/gmail_payment_seen_ids.txt"

if [ -z "$GMAIL_PASS" ]; then
    echo "$(date): ERROR - Gmail password not found" >> "$LOG_FILE"
    exit 1
fi

# 关键词列表
KEYWORDS="payment|paid|bounty|reward|payout|merged|congratulations|algora"

python3 << PYEOF
import imaplib, email, json, os
from email.header import decode_header

try:
    m = imaplib.IMAP4_SSL('imap.gmail.com')
    m.login('$GMAIL_USER', '$GMAIL_PASS')
    m.select('INBOX')
    
    # 搜索最近1天的GitHub通知邮件
    import datetime
    since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d-%b-%Y')
    status, msgs = m.search(None, f'(FROM "github.com" SINCE {since})')
    
    ids = msgs[0].split()
    seen = set()
    if os.path.exists('$STATE_FILE'):
        with open('$STATE_FILE') as f:
            seen = set(line.strip() for line in f if line.strip())
    
    new_payments = []
    for eid in reversed(ids):
        eid_str = eid.decode()
        if eid_str in seen:
            continue
        
        st, data = m.fetch(eid, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if not data or not data[0]:
            continue
        msg = email.message_from_bytes(data[0][1])
        subj_raw = decode_header(msg['Subject'] or '')
        subj = ''
        for s, enc in subj_raw:
            if isinstance(s, bytes):
                subj += s.decode(enc or 'utf-8', errors='replace')
            else:
                subj += s
        
        # 检查是否包含付款相关关键词
        import re
        if re.search(r'(payment|paid|bounty|reward|payout|algora|merged.*congratulations)', subj, re.I):
            new_payments.append(f"[{msg['Date'][:25]}] {subj[:100]}")
            seen.add(eid_str)
    
    if new_payments:
        msg = "💰 GitHub Bounty付款通知！\n\n" + "\n".join(new_payments)
        print(f"$(date): FOUND PAYMENTS - {len(new_payments)} emails")
        # 保存已读ID
        with open('$STATE_FILE', 'w') as f:
            for sid in seen:
                f.write(sid + '\n')
    else:
        print(f"$(date): No payment emails found")
    
    m.logout()
except Exception as e:
    print(f"$(date): Error - {e}")
PYEOF
