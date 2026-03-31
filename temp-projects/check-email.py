#!/usr/bin/env python3
"""
Gmail Inbox Checker
"""
import imaplib
import email
from email.header import decode_header

def check_gmail():
    email_addr = "zhaog100@gmail.com"
    password = "jkkt gwef jpqx bwyn"
    
    print(f"📧 Checking Gmail Inbox...")
    print(f"   Account: {email_addr}\n")
    
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email_addr, password)
        print("✅ Connected!\n")
        
        # Select inbox
        mail.select('inbox')
        
        # Get ALL emails (not just unread)
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            print("❌ Failed to search")
            return
        
        email_ids = messages[0].split()
        print(f"📬 Total emails: {len(email_ids)}")
        print(f"📬 Showing last 10 emails:\n")
        print("=" * 70)
        
        # Show last 10 emails
        for email_id in email_ids[-10:]:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Decode subject
            subject = msg.get('Subject', 'No Subject')
            decoded = decode_header(subject)
            subject = decoded[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8', errors='ignore')
            
            sender = msg.get('From', 'Unknown')
            date = msg.get('Date', 'Unknown')
            
            # Check if unread
            flags = msg_data[0][0].decode('utf-8', errors='ignore')
            is_unread = '\\Seen' not in flags
            
            marker = "🔴" if is_unread else "⚪"
            
            print(f"\n{marker} From: {sender}")
            print(f"   Subject: {subject}")
            print(f"   Date: {date}")
            
            # Get body preview
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True)
                            if body:
                                body = body.decode('utf-8', errors='ignore')
                                preview = body[:200].replace('\n', ' ').strip()
                                print(f"   Preview: {preview}...")
                        except:
                            pass
                        break
        
        mail.logout()
        mail.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_gmail()
