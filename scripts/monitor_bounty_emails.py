#!/usr/bin/env python3
"""
监控付款邮件脚本
检查 Gmail 中是否有付款相关邮件
"""

import os
import sys
import imaplib
import time
from datetime import datetime

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查付款邮件...")
    
    # 读取凭证
    with open('/home/zhaog/.openclaw/workspace/.env', 'r') as f:
        for line in f:
            if 'GMAIL' in line and '=' in line:
                key, value = line.strip().split('=', 1)
                if key == 'GMAIL_ADDRESS':
                    user = value
                elif key == 'GMAIL_APP_PASSWORD':
                    password = value
    
    try:
        # 连接 Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        mail.login(user, password)
        mail.select("INBOX")
        
        # 搜索未读邮件
        status, messages = mail.search(None, "UNSEEN")
        unread_ids = messages[0].split()
        
        if len(unread_ids) == 0:
            print("  ✅ 无未读邮件")
            return
            
        print(f"  📬 发现 {len(unread_ids)} 封未读邮件")
        
        # 检查付款相关邮件
        payment_count = 0
        for email_id in unread_ids[-10:]:  # 只检查最近10封
            try:
                status, msg_data = mail.fetch(email_id, "(BODY[HEADER.FIELDS (SUBJECT FROM)])")
                header = msg_data[0][1].decode('utf-8', errors='ignore')
                
                # 检查付款关键词
                payment_keywords = ['payment', 'payout', 'bounty', 'reward', 'ubiquity', 'rustchain', 'midnight']
                if any(keyword in header.lower() for keyword in payment_keywords):
                    payment_count += 1
                    print(f"  💰 付款相关: {header.split('Subject: ')[1].split('\r\n')[0] if 'Subject: ' in header else 'N/A'}")
                    
            except Exception as e:
                continue
        
        if payment_count > 0:
            print(f"  ⚠️  发现 {payment_count} 封付款相关邮件，请及时查看！")
        else:
            print("  ✅ 无付款相关邮件")
            
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")

if __name__ == '__main__':
    main()
