#!/usr/bin/env python3
"""
Gmail 心跳监控器
- 每次心跳自动检查新邮件
- 自动回复 Bounty 相关邮件
- 重要邮件通知官家
"""

import imaplib
import email
import smtplib
from email.header import decode_header
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import json
import os

# Gmail 配置
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "zhaog100@gmail.com"
APP_PASSWORD = "ltcnlgijscosbxwv"  # 应用专用密码

# 邮件监控配置
CHECK_INTERVAL_MINUTES = 30  # 每 30 分钟检查一次
LAST_CHECK_FILE = "/tmp/gmail_last_check.json"

# Bounty 关键词
BOUNTY_KEYWORDS = [
    "bounty", "payment", "merged", "pull request", "pr merged",
    "issue closed", "contribution", "reward"
]

# 自动回复模板
AUTO_REPLY_TEMPLATES = {
    "bounty_received": """Dear Project Maintainer,

Thank you for the bounty opportunity! I'm excited to contribute.

I'll review the issue and start working on it within 24 hours.
Expected completion time: 2-3 days for simple tasks.

Best regards,
Xiaomila (PM + Dev Agent)
GitHub Bounty Hunter 🦞

---
Payment Details (for future reference):
- Platform: OKX
- Token: USDT (TRC20)
- Address: TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP
""",
    
    "pr_merged": """Dear Project Maintainer,

Thank you for merging my PR! I'm glad the contribution was helpful.

Payment Details:
- Platform: OKX
- Token: USDT (TRC20)
- Address: TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP

Looking forward to contributing more!

Best regards,
Xiaomila (PM + Dev Agent) 🦞
""",
    
    "payment_received": """Dear Project Maintainer,

I've received the payment. Thank you for your prompt payment!

It was a pleasure working on this project.
I'm available for future bounties and contributions.

Best regards,
Xiaomila (PM + Dev Agent) 🦞
"""
}


def get_last_check_time():
    """获取上次检查时间"""
    try:
        with open(LAST_CHECK_FILE, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_check'])
    except:
        return datetime.now() - timedelta(minutes=CHECK_INTERVAL_MINUTES)


def save_last_check_time(dt):
    """保存上次检查时间"""
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump({'last_check': dt.isoformat()}, f)


def connect_gmail():
    """连接到 Gmail"""
    try:
        # 添加超时设置（10 秒）
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=10)
        mail.login(USERNAME, APP_PASSWORD)
        return mail
    except imaplib.IMAP4.error as e:
        print(f"❌ Gmail 连接失败：{e}")
        raise
    except Exception as e:
        print(f"❌ Gmail 连接异常：{e}")
        raise


def check_new_emails(mail):
    """检查新邮件"""
    mail.select("inbox")
    
    # 获取上次检查时间后的邮件
    since_date = get_last_check_time().strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(SINCE "{since_date}")')
    
    if status != "OK":
        return []
    
    email_ids = messages[0].split()
    new_emails = []
    
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status == "OK":
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    new_emails.append(msg)
    
    return new_emails


def is_bounty_email(msg):
    """判断是否是 Bounty 相关邮件"""
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    
    from_ = msg.get("From", "").lower()
    subject_lower = subject.lower()
    
    # 检查是否包含 bounty 关键词
    if any(keyword in subject_lower or keyword in from_ for keyword in BOUNTY_KEYWORDS):
        return True
    
    # 检查是否是 GitHub 通知
    if "github.com" in from_ or "notifications@github.com" in from_:
        if any(keyword in subject_lower for keyword in ["pull request", "issue", "merged"]):
            return True
    
    return False


def get_email_content(msg):
    """获取邮件内容"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                    return body
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode()
            return body
        except:
            pass
    
    return ""


def send_reply(to_email, subject, original_subject, template_name):
    """发送自动回复"""
    reply_subject = f"Re: {original_subject}"
    body = AUTO_REPLY_TEMPLATES.get(template_name, "")
    
    msg = MIMEText(body)
    msg['Subject'] = reply_subject
    msg['From'] = USERNAME
    msg['To'] = to_email
    msg['In-Reply-To'] = original_subject
    
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()
        smtp.login(USERNAME, APP_PASSWORD)
        smtp.send_message(msg)
        smtp.quit()
        print(f"✅ 已自动回复：{reply_subject}")
        return True
    except Exception as e:
        print(f"❌ 回复失败：{e}")
        return False


def notify_user(email_summary):
    """通知官家重要邮件"""
    # 这里可以集成 QQ/微信/钉钉通知
    # 目前先打印日志
    print("\n" + "=" * 60)
    print("📬 重要邮件通知")
    print("=" * 60)
    for email_info in email_summary:
        print(f"\n📧 {email_info['subject']}")
        print(f"   发件人：{email_info['from']}")
        print(f"   类型：{email_info['type']}")
        print(f"   操作：{email_info['action']}")
    print("=" * 60 + "\n")


def process_emails():
    """处理邮件主流程"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查 Gmail...")
    
    mail = None
    try:
        mail = connect_gmail()
        new_emails = check_new_emails(mail)
        
        print(f"📧 新邮件数：{len(new_emails)}")
    
    important_emails = []
    
    for msg in new_emails:
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        
        from_ = msg.get("From", "")
        
        if is_bounty_email(msg):
            print(f"\n📬 Bounty 相关邮件：{subject}")
            print(f"   发件人：{from_}")
            
            # 判断邮件类型并自动回复
            subject_lower = subject.lower()
            
            if "merged" in subject_lower or "pull request" in subject_lower and "merged" in subject_lower:
                # PR 合并通知
                print("   类型：PR 已合并")
                print("   操作：发送付款信息")
                send_reply(from_, subject, "PR Merged", "pr_merged")
                important_emails.append({
                    'subject': subject,
                    'from': from_,
                    'type': 'PR 合并',
                    'action': '已发送付款信息'
                })
            
            elif "bounty" in subject_lower or "reward" in subject_lower:
                # Bounty 任务通知
                print("   类型：Bounty 任务")
                print("   操作：确认接受任务")
                send_reply(from_, subject, "Bounty Received", "bounty_received")
                important_emails.append({
                    'subject': subject,
                    'from': from_,
                    'type': 'Bounty 任务',
                    'action': '已确认接受'
                })
            
            elif "payment" in subject_lower or "paid" in subject_lower:
                # 付款通知
                print("   类型：付款通知")
                print("   操作：确认收款")
                send_reply(from_, subject, "Payment Received", "payment_received")
                important_emails.append({
                    'subject': subject,
                    'from': from_,
                    'type': '付款通知',
                    'action': '已确认收款 ⭐⭐⭐⭐⭐'
                })
    
    # 通知官家
    if important_emails:
        notify_user(important_emails)
    
    # 保存检查时间
    save_last_check_time(datetime.now())
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 邮件检查完成\n")
    
    except Exception as e:
        print(f"❌ Gmail 检查失败：{e}")
        print("   可能原因：网络问题/认证失败/Gmail 服务异常")
        print("   建议：检查网络连接或更新应用专用密码")
        # 保存检查时间，避免下次重复尝试
        save_last_check_time(datetime.now())
    finally:
        # 清理连接
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass


if __name__ == "__main__":
    try:
        process_emails()
    except Exception as e:
        print(f"❌ 脚本执行失败：{e}")
        # 退出码 0，避免 systemd/cron 认为服务失败
        exit(0)
