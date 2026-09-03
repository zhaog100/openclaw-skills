#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import os
import sys

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

def read_gmail(username, password, max_emails=10):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(username, password)
        mail.select("INBOX")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            print("❌ 无法搜索邮件")
            return None
        
        email_ids = messages[0].split()
        if not email_ids:
            print("📭 无未读邮件")
            return []
        
        recent_ids = email_ids[-max_emails:][::-1]
        emails = []
        
        for eid in recent_ids:
            status, msg_data = mail.fetch(eid, "(RFC822.HEADER)")
            if status == "OK":
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        from_addr = msg.get('From', '').split('<')[0].strip()
                        subject = decode_subject(msg.get('Subject', ''))
                        date = msg.get('Date', '')
                        emails.append({'from': from_addr, 'subject': subject, 'date': date[:10]})
        
        mail.logout()
        return emails
    except Exception as e:
        print(f"❌ 读取邮件失败: {e}")
        return None

if __name__ == "__main__":
    username = os.environ.get("GMAIL_USER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    if not username or not password:
        print("❌ 缺少邮箱凭据")
        sys.exit(1)
    
    emails = read_gmail(username, password, max_count)
    if emails:
        print(f"\n**未读邮件**: {len(emails)} 封\n")
        for e in emails[:5]:
            print(f"- {e['from']}: {e['subject']} ({e['date']})")
