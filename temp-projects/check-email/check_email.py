#!/usr/bin/env python3
"""
Gmail Email Checker - Simple version
"""

import imaplib
import email
from email.header import decode_header
import os

def get_config():
    """Read Gmail config from .env"""
    env_path = os.path.expanduser('~/.openclaw/workspace/.env')
    config = {}
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                if key == 'GMAIL_ADDRESS':
                    config['email'] = value
                elif key == 'GMAIL_APP_PASSWORD':
                    config['password'] = value
    
    return config

def decode_header_value(value):
    """Decode email header"""
    if value is None:
        return ""
    
    decoded = decode_header(value)
    result = []
    
    for part, encoding in decoded:
        if isinstance(part, bytes):
            part = part.decode(encoding or 'utf-8', errors='ignore')
        result.append(part)
    
    return ''.join(result)

def get_email_preview(msg):
    """Get email body preview"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True)
                    if body:
                        body = body.decode('utf-8', errors='ignore')
                        return body[:150].replace('\n', ' ').strip()
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True)
            if body:
                body = body.decode('utf-8', errors='ignore')
                return body[:150].replace('\n', ' ').strip()
        except:
            pass
    
    return ""

def check_emails(limit=10):
    """Check recent emails"""
    print("📧 Checking Gmail...")
    print()
    
    config = get_config()
    
    if not config.get('email') or not config.get('password'):
        print("❌ Gmail configuration not found")
        return
    
    print(f"Account: {config['email']}")
    print()
    
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(config['email'], config['password'])
        
        # Select inbox
        mail.select('inbox')
        
        # Search for emails
        status, messages = mail.search(None, 'ALL')
        
        if status != 'OK':
            print("❌ Failed to search emails")
            return
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print("📭 No emails found")
            return
        
        # Get recent emails
        recent_ids = email_ids[-limit:][::-1]  # Most recent first
        
        print(f"📬 Recent {len(recent_ids)} emails:")
        print("=" * 70)
        
        # Important keywords
        important_keywords = [
            'urgent', 'important', 'security', 'bounty',
            'payment', 'github', 'pull request', 'merge',
            'claude-builders', 'openclaw'
        ]
        
        for idx, email_id in enumerate(recent_ids, 1):
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Get headers
            subject = decode_header_value(msg.get('Subject', 'No Subject'))
            sender = decode_header_value(msg.get('From', 'Unknown'))
            date = msg.get('Date', 'Unknown')
            
            # Get body preview
            body = get_email_preview(msg)
            
            # Check if important
            is_important = any(
                kw in subject.lower() or kw in body.lower()
                for kw in important_keywords
            )
            
            # Display
            icon = '🔴' if is_important else '⚪'
            print(f"\n{idx}. {icon} {subject}")
            print(f"   From: {sender[:50]}")
            print(f"   Date: {date}")
            
            if is_important:
                print(f"   ⚠️ IMPORTANT")
            
            if body:
                print(f"   Preview: {body}...")
            
            print("-" * 70)
        
        # Close connection
        mail.close()
        mail.logout()
        
        print(f"\n✅ Checked {len(recent_ids)} emails")
        print(f"🔴 Important emails need attention")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        print("   Check your email and app password")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_emails(limit=10)
