#!/usr/bin/env python3
"""
Gmail IMAP 邮件检查（改进版）
- 自动重试机制（3次）
- 更好的超时处理
- 网络不稳定时也能工作
"""

import imaplib
import ssl
import email
from email.header import decode_header
import time
import re
from pathlib import Path

# 配置
GMAIL_ENV = Path.home() / '.openclaw' / 'secrets' / 'gmail.env'
MAX_RETRIES = 3
RETRY_DELAY = 2
IMAP_TIMEOUT = 15


def load_gmail_config():
    """加载 Gmail 配置"""
    if not GMAIL_ENV.exists():
        raise FileNotFoundError(f"未找到配置文件: {GMAIL_ENV}")
    
    config = {}
    with open(GMAIL_ENV) as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value
    
    return config


def connect_gmail_with_retry(email_user, email_pass, retry=0):
    """带重试的 Gmail 连接"""
    try:
        print(f"🔄 连接 Gmail IMAP...（尝试 {retry + 1}/{MAX_RETRIES}）")
        
        # 创建 SSL 上下文
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # 连接 IMAP
        mail = imaplib.IMAP4_SSL(
            'imap.gmail.com',
            993,
            ssl_context=context,
            timeout=IMAP_TIMEOUT
        )
        
        # 登录
        mail.login(email_user, email_pass)
        print("✅ 登录成功！")
        
        return mail
        
    except (imaplib.IMAP4.error, ssl.SSLError, TimeoutError, ConnectionError) as e:
        if retry < MAX_RETRIES - 1:
            print(f"⚠️  连接失败: {e}")
            print(f"⏳ {RETRY_DELAY} 秒后重试...")
            time.sleep(RETRY_DELAY)
            return connect_gmail_with_retry(email_user, email_pass, retry + 1)
        else:
            raise


def check_payment_emails(mail, days=7):
    """检查付款邮件"""
    print(f"\n🔍 搜索最近 {days} 天的付款邮件...\n")
    
    # mail.select('INBOX')  # 已在 main 中选择
    
    # 搜索日期
    since_date = time.strftime('%d-%b-%Y', time.localtime(time.time() - days * 86400))
    
    # 搜索邮件
    status, messages = mail.search(None, f'(SINCE {since_date})')
    if status != 'OK':
        print("❌ 搜索失败")
        return []
    
    email_ids = messages[0].split()
    print(f"📧 最近 {days} 天邮件: {len(email_ids)} 封")
    
    # 检查付款关键词
    payment_keywords = re.compile(
        r'(payment|paid|bounty|reward|payout|transfer|'
        r'congratulations.*merged|merged.*congratulations)',
        re.IGNORECASE
    )
    
    real_payments = []
    
    # 只检查最近 100 封
    for email_id in email_ids[-100:]:
        try:
            status, msg_data = mail.fetch(
                email_id,
                '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])'
            )
            
            if status != 'OK' or not msg_data[0]:
                continue
            
            # 解析邮件头
            headers = email.message_from_bytes(msg_data[0][1])
            subject = str(decode_header(headers.get('Subject', ''))[0][0])
            from_ = str(decode_header(headers.get('From', ''))[0][0])
            date = headers.get('Date', '')
            
            # 检查关键词
            if payment_keywords.search(f"{subject} {from_}"):
                real_payments.append({
                    'subject': subject,
                    'from': from_,
                    'date': date
                })
                
        except Exception as e:
            continue
    
    # 显示结果
    print(f"\n💰 发现 {len(real_payments)} 封付款相关邮件:\n")
    
    for p in real_payments[-10:]:
        print(f"📅 {p['date'][:30]}")
        print(f"   From: {p['from'][:50]}")
        print(f"   Subject: {p['subject'][:70]}")
        print()
    
    return real_payments


def main():
    print("📧 Gmail IMAP 邮件检查（改进版）")
    print("=" * 60)
    
    # 加载配置
    try:
        config = load_gmail_config()
        email_user = config['GMAIL_USER']
        email_pass = config['GMAIL_PASS']
        
        print(f"📧 用户: {email_user}")
        print(f"🔑 密码: {email_pass[:4]}****{email_pass[-4:]} ({len(email_pass)} 字符)\n")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 连接 Gmail
    mail = None
    try:
        mail = connect_gmail_with_retry(email_user, email_pass)
        
        # 选择收件箱
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        total_emails = len(messages[0].split()) if messages[0] else 0
        print(f"📬 收件箱总数: {total_emails:,} 封\n")
        
        # 检查付款邮件
        payments = check_payment_emails(mail, days=7)
        
        print("=" * 60)
        print(f"✅ 检查完成：发现 {len(payments)} 封付款相关邮件")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return 1
    
    finally:
        if mail:
            try:
                mail.logout()
            except:
                pass
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
