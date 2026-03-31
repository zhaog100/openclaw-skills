#!/usr/bin python3
"""
Full Email Content Reader
"""

import imaplib
import email
from email.header import decode_header

def get_full_email_content(email_addr, password):
    """Get full email content"""
    print(f"📧 读取完整邮件内容...")
    print(f"   账户: {email_addr}\n")
    
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email_addr, password)
        
        # Select inbox
        mail.select('inbox')
        
        # Get recent emails
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        if not email_ids:
            print("📭 收件箱为空")
            return
        
        print(f"📬 找到 {len(email_ids)} 封邮件")
        print("=" * 80)
        
        # Read last 3 emails with full content
        for i, range(3):
            email_id = email_ids[-(i+1)]
            
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get subject
            subject_parts = decode_header(msg.get('Subject', ''))
            subject = ''
            for part, subject_parts:
                if isinstance(part, bytes):
                    subject += part.decode('utf-8', errors='ignore')
                else:
                    subject += str(part)
            
            # Get sender
            from_parts = decode_header(msg.get('From', ''))
            sender = ''
            for part in from_parts:
                if isinstance(part, bytes):
                    sender += part.decode('utf-8', errors='ignore')
                else:
                    sender += str(part)
            
            # Get date
            date = msg.get('Date', '')
            
            print(f"\n{'=' * 80}")
            print(f"📧 邮件 #{i}")
            print(f"{'=' * 80}")
            print(f"发件人: {sender}")
            print(f"主题: {subject}")
            print(f"日期: {date}")
            
            # Get body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    except:
                        pass
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                except:
                    pass
            
            # Show body (first 1000 chars)
            print(f"\n内容预览 (前1000字符):")
            print("-" * 80)
            print(body[:1000])
            
            # Mark as seen (optional)
            # mail.store(email_id, '+FLAGS', '\\Seen')
            
        mail.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"详细信息: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    email_addr = "zhaog100@gmail.com"
    password = "jkkt gwef jpqx bwyn"
    
    get_full_email_content(email_addr, password)
