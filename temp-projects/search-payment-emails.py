#!/usr/bin/env python3
"""
搜索付款相关邮件
"""
import imaplib
import email
from email.header import decode_header

email_addr = "zhaog100@gmail.com"
password = "jkkt gwef jpqx bwyn"

# 付款相关关键词
payment_keywords = [
    "payment", "paid", "payout", "reward", "bounty",
    "$", "dollar", "usd", "eth", "btc", "ltc",
    "wallet", "transaction", "transfer", "转账", "付款"
]

print("=" * 80)
print("🔍 搜索付款相关邮件")
print("=" * 80)
print()

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(email_addr, password)
    
    mail.select('inbox')
    
    # 获取所有邮件
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()
    
    print(f"📬 检查 {len(email_ids)} 封邮件...")
    print()
    
    found_payment_emails = []
    
    # 检查最近 100 封邮件
    for email_id in email_ids[-100:]:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        
        if status != 'OK':
            continue
        
        msg = email.message_from_bytes(msg_data[0][1])
        
        # 获取主题
        subject_parts = decode_header(msg.get('Subject', ''))
        subject = ''.join([p.decode('utf-8') if isinstance(p, bytes) else str(p) for p, _ in subject_parts])
        
        # 获取正文
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
        
        # 检查是否包含付款关键词
        full_text = (subject + " " + body).lower()
        
        for keyword in payment_keywords:
            if keyword.lower() in full_text:
                # 找到了！
                found_payment_emails.append({
                    'id': email_id,
                    'keyword': keyword,
                    'subject': subject,
                    'from': msg.get('From', 'Unknown'),
                    'date': msg.get('Date', 'Unknown'),
                    'body': body[:1000]  # 限制1000字符
                })
                break
    
    mail.close()
    
    # 显示结果
    if found_payment_emails:
        print(f"✅ 找到 {len(found_payment_emails)} 封付款相关邮件")
        print("=" * 80)
        
        for i, email_item in enumerate(found_payment_emails, 1):
            print(f"\n邮件 #{i}")
            print(f"匹配关键词: {email_item['keyword']}")
            print(f"发件人: {email_item['from']}")
            print(f"主题: {email_item['subject']}")
            print(f"日期: {email_item['date']}")
            print("-" * 80)
            print("内容:")
            print(email_item['body'][:500])
            
            if len(email_item['body']) > 500:
                print(f"\n... (还有 {len(email_item['body']) - 500} 字符)")
            
            print("=" * 80)
    else:
        print("❌ 未找到付款相关邮件")
        print()
        print("💡 可能原因:")
        print("  • 付款邮件可能在其他文件夹")
        print("  • 付款可能通过其他平台（GitHub Sponsors, Open Collective）")
        print("  • 付款邮件可能被自动归档")
        print("  • 付款可能在垃圾邮件中")
        print()
        print("🔍 建议:")
        print("  • 检查 Gmail 的 'Payments' 或 'Finance' 标签")
        print("  • 搜索关键词: 'bounty reward', 'payment confirmed'")
        print("  • 检查 GitHub Sponsors 页面")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
