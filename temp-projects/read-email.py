#!/usr/bin/env python3
"""
Gmail Inbox Reader
"""
import imaplib
import email
from email.header import decode_header

def read_inbox():
    email_addr = "zhaog100@gmail.com"
    password = "jkkt gwef jpqx bwyn"
    
    print(f"📧 Reading Gmail Inbox...")
    print(f"   Account: {email_addr}\n")
    
    try:
        # Connect
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_addr, password)
        
        print("✅ Connected!\n")
        
        # Select inbox
        mail.select('inbox')
        
        # Get ALL messages
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            print("❌ Search failed")
            return
        
        email_ids = messages[0].split()
        total = len(email_ids)
        
        print(f"📬 Total emails: {total}")
        print(f"📬 Showing last 10 emails:\n")
        print("=" * 70)
        
        # Get last 10 emails
        for email_id in reversed(email_ids[-10:]):
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get subject
            subject = decode_header(msg.get('Subject', ''))[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8', errors='ignore')
            
            # Get sender
            sender = msg.get('From', 'Unknown')
            
            # Get date
            date = msg.get('Date', 'Unknown')
            
            # Check if unread
            flags = msg.get('Flags', '')
            is_unread = 'UNSEEN' in str(flags) if flags else False
            
            marker = "🔴 UNREAD" if is_unread else "⚪ Read"
            
            print(f"\n{marker} From: {sender}")
            print(f"   Subject: {subject}")
            print(f"   Date: {date}")
            
            # Get body for unread emails
            if is_unread:
                if msg.is_multipart():
                    for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            preview = body[:200].replace('\n', ' ')
                            print(f"\n   📝 Content Preview:")
                            print(f"   {preview}...")
                        except:
                            pass
                        break
        
        mail.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    read_inbox()
