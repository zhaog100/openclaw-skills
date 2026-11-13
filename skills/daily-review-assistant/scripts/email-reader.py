# -*- coding: utf-8 -*-
"""版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
#!/usr/bin/env python3
import logging
import imaplib
import email
from email.header import decode_header
import sys
import os

# 配置日志（INFO→stdout，ERROR→stderr）
_logging_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_logging_fh_stdout = logging.StreamHandler(sys.stdout)
_logging_fh_stdout.setFormatter(_logging_fmt)
_logging_fh_stderr = logging.StreamHandler(sys.stderr)
_logging_fh_stderr.setFormatter(_logging_fmt)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(_logging_fh_stdout)
logger.addHandler(_logging_fh_stderr)

def decode_subject(subject):
    if subject:
        decoded = decode_header(subject)
        result = ""
        for part, charset in decoded:
            if isinstance(part, bytes):
                result += part.decode(charset or 'utf-8', errors='ignore')
            else:
                result += part
        return result[:80]
    return "(无主题)"

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                    break
            elif content_type == "text/html" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                    body = body.replace('<br>', '\n').replace('<p>', '\n')
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='ignore')
    return body[:500]

def read_gmail(username, password, max_emails=10, full_content=False):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(username, password)
        mail.select("INBOX")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.error("无法搜索邮件")
            return None
        
        email_ids = messages[0].split()
        if not email_ids:
            logger.info("无未读邮件")
            mail.logout()
            return {"emails": [], "marked": 0, "total_unseen": 0}
        
        recent_ids = email_ids[-max_emails:][::-1]
        emails = []
        
        for eid in recent_ids:
            if full_content:
                status, msg_data = mail.fetch(eid, "(RFC822)")
            else:
                status, msg_data = mail.fetch(eid, "(RFC822.HEADER)")
            
            if status == "OK":
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        from_addr = msg.get('From', '').split('<')[0].strip()
                        subject = decode_subject(msg.get('Subject', ''))
                        date = msg.get('Date', '')
                        
                        email_data = {
                            'from': from_addr,
                            'subject': subject,
                            'date': date[:10],
                            'id': eid.decode()
                        }
                        
                        if full_content:
                            email_data['body'] = get_email_body(msg)
                        
                        emails.append(email_data)
        
        # 标记为已读: 搜到多少 UNSEEN 就标多少(不全依赖 max_emails 截断), 据实回报
        marked = 0
        # 标记目标 = 全部 UNSEEN(不限 5 封), 避免漏标导致"没更新为已读"
        for eid in email_ids:
            try:
                mail.store(eid, '+FLAGS', r'(' + chr(92) + 'Seen)')
                marked += 1
            except Exception as e:
                logger.warning(f"标记已读失败 id={eid}: {e}")
        total_unseen = len(email_ids)
        logger.info(f"UNSEEN 共 {total_unseen} 封, 已标已读 {marked} 封")
        
        mail.logout()
        return {"emails": emails, "marked": marked, "total_unseen": total_unseen}
    except Exception as e:
        logger.error(f"读取邮件失败: {e}")
        return {"emails": [], "marked": 0, "total_unseen": -1}

if __name__ == "__main__":
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "skills", "daily-review-assistant", ".env")
    
    username = ""
    password = ""
    
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GMAIL_USER="):
                    username = line.split("=", 1)[1]
                elif line.startswith("GMAIL_APP_PASSWORD="):
                    password = line.split("=", 1)[1]
    
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    full_content = "--full" in sys.argv
    
    if not username or not password:
        logger.error("缺少邮箱凭据")
        sys.exit(1)
    
    result = read_gmail(username, password, max_count, full_content)
    emails = result.get("emails", []) if isinstance(result, dict) else (result or [])
    marked = result.get("marked", 0) if isinstance(result, dict) else 0
    total_unseen = result.get("total_unseen", 0) if isinstance(result, dict) else 0
    # 据实回报标记情况(供早报动态显示)
    print(f"[已读标记] 未读{total_unseen}封, 已标已读{marked}封")
    
    if emails:
        print(f"\n**未读邮件**: {len(emails)} 封\n")
        for e in emails[:3]:
            print(f"**{e['subject']}**")
            print(f"- 发件人: {e['from']}")
            print(f"- 时间: {e['date']}")
            if full_content and e.get('body'):
                print(f"\n**内容:**\n{e['body'][:400]}...")
            print("---")
