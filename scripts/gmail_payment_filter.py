#!/usr/bin/env python3
"""
Gmail 付款邮件自动标记工具
- 搜索付款相关邮件
- 自动添加 "Payment" 标签
- 可定期运行（通过 cron）
"""

import imaplib
import email
from email.header import decode_header
import os
import sys
from datetime import datetime, timedelta

# 配置
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASS = os.getenv('GMAIL_PASS')
PAYMENT_LABEL = 'Payment'  # 标签名称
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'  # 默认 dry-run 模式

# 付款关键词
PAYMENT_KEYWORDS = [
    'payment', 'paid', 'payout', 'transfer',
    'bounty reward', 'reward sent', 'congratulations',
    'rtc', 'usdt', 'eth', 'btc'
]

# 排除关键词（GitHub 通知等）
EXCLUDE_SENDERS = [
    'notifications@github.com',
    'noreply@github.com',
    'newsletter@',
    'promo@',
    'marketing@'
]


def decode_subject(subject):
    """解码邮件标题"""
    if not subject:
        return "N/A"
    try:
        decoded = decode_header(subject)
        result = []
        for part, charset in decoded:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='ignore'))
            else:
                result.append(part)
        return ''.join(result)
    except:
        return subject


def is_payment_email(subject, from_addr):
    """判断是否是付款邮件"""
    subject_lower = subject.lower()
    from_lower = from_addr.lower()
    
    # 排除 GitHub 通知等
    for exclude in EXCLUDE_SENDERS:
        if exclude in from_lower:
            return False
    
    # 检查是否包含付款关键词
    for keyword in PAYMENT_KEYWORDS:
        if keyword in subject_lower:
            return True
    
    return False


def create_or_get_label(mail, label_name):
    """创建或获取标签"""
    try:
        # 尝试创建标签（如果已存在会报错，忽略即可）
        mail.create(label_name)
        print(f"✅ 标签 '{label_name}' 已创建")
    except:
        print(f"ℹ️  标签 '{label_name}' 已存在")
    
    return label_name


def main():
    print("📧 Gmail 付款邮件自动标记工具")
    print("=" * 60)
    print(f"模式: {'DRY RUN（仅预览）' if DRY_RUN else '实际执行'}")
    print()
    
    if not GMAIL_USER or not GMAIL_PASS:
        print("❌ 未配置 Gmail 凭证")
        return 1
    
    try:
        # 连接 Gmail
        print("🔄 连接 Gmail IMAP...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com', timeout=15)
        mail.login(GMAIL_USER, GMAIL_PASS)
        print("✅ 登录成功\n")
        
        # 选择收件箱
        mail.select('INBOX')
        
        # 创建/获取标签
        if not DRY_RUN:
            create_or_get_label(mail, PAYMENT_LABEL)
        
        # 搜索最近 30 天的邮件
        since_date = (datetime.now() - timedelta(days=30)).strftime('%d-%b-%Y')
        print(f"🔍 搜索 {since_date} 以来的邮件...\n")
        
        # 搜索所有邮件
        status, messages = mail.search(None, f'SINCE {since_date}')
        email_ids = messages[0].split()
        print(f"📬 总邮件数: {len(email_ids)}\n")
        
        # 检查每封邮件
        payment_count = 0
        marked_count = 0
        
        for i, email_id in enumerate(email_ids, 1):
            try:
                # 获取邮件头
                status, msg_data = mail.fetch(email_id, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        headers = response_part[1].decode('utf-8', errors='ignore')
                        lines = headers.split('\n')
                        
                        subject = next((l.split(': ', 1)[1] for l in lines if l.startswith('Subject:')), 'N/A')
                        from_ = next((l.split(': ', 1)[1] for l in lines if l.startswith('From:')), 'N/A')
                        date = next((l.split(': ', 1)[1] for l in lines if l.startswith('Date:')), 'N/A')
                        
                        subject = decode_subject(subject)
                        
                        # 检查是否是付款邮件
                        if is_payment_email(subject, from_):
                            payment_count += 1
                            
                            if DRY_RUN:
                                # 仅预览
                                print(f"[{payment_count}] {subject}")
                                print(f"   From: {from_}")
                                print(f"   Date: {date}")
                                print(f"   Action: Will mark with '{PAYMENT_LABEL}' label\n")
                            else:
                                # 实际标记
                                try:
                                    mail.store(email_id, '+X-GM-LABELS', f'({PAYMENT_LABEL})')
                                    marked_count += 1
                                    print(f"✅ [{marked_count}] Marked: {subject}")
                                except Exception as e:
                                    print(f"⚠️  Failed to mark: {subject} - {e}")
            
            except Exception as e:
                continue
            
            # 进度提示
            if i % 100 == 0:
                print(f"⏳ 已处理 {i}/{len(email_ids)} 封邮件...")
        
        # 总结
        print("\n" + "=" * 60)
        if DRY_RUN:
            print(f"🔍 DRY RUN 完成：")
            print(f"  - 搜索到 {payment_count} 封付款相关邮件")
            print(f"  - 这些邮件将被标记为 '{PAYMENT_LABEL}'")
            print(f"\n💡 要实际执行，请设置环境变量：")
            print(f"  export DRY_RUN=false")
            print(f"  然后重新运行此脚本")
        else:
            print(f"✅ 执行完成：")
            print(f"  - 搜索到 {payment_count} 封付款相关邮件")
            print(f"  - 已标记 {marked_count} 封邮件")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
