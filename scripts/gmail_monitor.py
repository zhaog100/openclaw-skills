#!/usr/bin/env python3
"""
Gmail Bounty Monitor - Enhanced Version
Monitors Gmail for bounty-related emails and provides notifications
"""

import json
import imaplib
import smtplib
from datetime import datetime, timedelta
import os
import sys

def load_config():
    """Load configuration from JSON file"""
    try:
        with open('scripts/gmail_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败：{e}")
        return None

def connect_gmail(config):
    """Connect to Gmail with configuration"""
    try:
        mail = imaplib.IMAP4_SSL(
            config['imap_server'],
            config['imap_port']
        )
        mail.login(config['username'], config['app_password'])
        return mail
    except Exception as e:
        print(f"❌ Gmail 连接失败：{e}")
        return None

def check_new_emails(mail):
    """Check for new emails"""
    try:
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN", "RECENT")

        if status != "OK":
            return []

        email_ids = messages[0].split()
        recent_emails = []

        # Limit to last 20 emails to avoid timeout
        for email_id in email_ids[-20:]:
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status == "OK":
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            recent_emails.append(msg)
            except Exception:
                continue

        return recent_emails
    except Exception as e:
        print(f"❌ 邮件检查失败：{e}")
        return []

def is_bounty_email(msg, keywords):
    """Check if email is bounty-related"""
    try:
        subject = str(msg.get("Subject", "")).lower()
        sender = str(msg.get("From", "")).lower()

        return any(keyword in subject or keyword in sender for keyword in keywords)
    except:
        return False

def process_emails():
    """Main email processing function"""
    config = load_config()
    if not config:
        return

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始监控 Gmail...")

    mail = connect_gmail(config)
    if not mail:
        print("❌ 无法连接到 Gmail，请检查网络或认证信息")
        return

    try:
        new_emails = check_new_emails(mail)
        bounty_emails = []

        print(f"📧 发现 {len(new_emails)} 封新邮件")

        for msg in new_emails:
            try:
                subject = str(msg.get("Subject", "No Subject"))
                sender = str(msg.get("From", "Unknown"))

                if is_bounty_email(msg, config.get('bounty_keywords', [])):
                    print(f"\n🎯 发现 Bounty 相关邮件:")
                    print(f"   主题: {subject}")
                    print(f"   发件人: {sender}")

                    # Categorize email type
                    subject_lower = subject.lower()
                    if "merged" in subject_lower or "pull request" in subject_lower:
                        email_type = "PR 合并通知"
                    elif "bounty" in subject_lower or "payment" in subject_lower:
                        email_type = "Bounty/付款通知"
                    else:
                        email_type = "其他重要邮件"

                    print(f"   类型: {email_type}")
                    bounty_emails.append({
                        'subject': subject,
                        'sender': sender,
                        'type': email_type
                    })

            except Exception as e:
                print(f"⚠️ 处理邮件时出错：{e}")
                continue

        if bounty_emails:
            print(f"\n📬 发现 {len(bounty_emails)} 封重要邮件，建议手动检查:")
            for email in bounty_emails:
                print(f"   - {email['type']}: {email['subject']}")
            print("\n💡 建议操作:")
            print("   1. 登录 GitHub 查看相关 PR/Issue")
            print("   2. 确认是否需要回复")
            print("   3. 如需自动回复，请确保 SMTP 已启用")
        else:
            print("✅ 未发现新的 Bounty 相关邮件")

    finally:
        try:
            mail.close()
            mail.logout()
        except:
            pass

if __name__ == "__main__":
    try:
        process_emails()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
    except Exception as e:
        print(f"❌ 脚本执行失败：{e}")
        sys.exit(1)