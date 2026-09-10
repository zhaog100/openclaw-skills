#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import sys
import os

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
            return []
        
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
        
        mail.logout()
        return emails
    except Exception as e:
        logger.error(f"读取邮件失败: {e}")
        return None

if __name__ == "__main__":
    env_file = "/home/ubuntu/.openclaw/workspace/skills/daily-review-assistant/.env"
    
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
    
    emails = read_gmail(username, password, max_count, full_content)
    
    if emails:
        logger.info(f"\n**未读邮件**: {len(emails)} 封\n")
        for e in emails[:3]:
            logger.info(f"**{e['subject']}**")
            logger.info(f"- 发件人: {e['from']}")
            logger.info(f"- 时间: {e['date']}")
            if full_content and e.get('body'):
                logger.info(f"\n**内容:**\n{e['body'][:400]}...")
            logger.info("---")
