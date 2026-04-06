#!/usr/bin/env python3
"""
Gmail API 邮件检查（使用 OAuth2）
比 IMAP 更稳定，不受网络波动影响

安装依赖：
pip install google-auth google-auth-oauthlib google-api-python-client

首次使用需要授权：
1. 访问 Google Cloud Console
2. 启用 Gmail API
3. 创建 OAuth 2.0 凭证
4. 下载 credentials.json 到 ~/.openclaw/secrets/
5. 运行此脚本进行授权
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("❌ 缺少依赖，请运行：pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SECRETS_DIR = os.path.expanduser('~/.openclaw/secrets')
CREDENTIALS_FILE = os.path.join(SECRETS_DIR, 'gmail_credentials.json')
TOKEN_FILE = os.path.join(SECRETS_DIR, 'gmail_token.json')


def get_gmail_service():
    """获取 Gmail API 服务"""
    creds = None
    
    # 加载现有 token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 如果没有有效凭证，进行授权
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 刷新访问令牌...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ 未找到凭证文件: {CREDENTIALS_FILE}")
                print("\n📝 设置步骤：")
                print("1. 访问 https://console.cloud.google.com")
                print("2. 启用 Gmail API")
                print("3. 创建 OAuth 2.0 凭证（桌面应用）")
                print(f"4. 下载 JSON 并保存为 {CREDENTIALS_FILE}")
                print("5. 重新运行此脚本")
                return None
            
            print("🔐 启动 OAuth 授权流程...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 保存凭证
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print("✅ 凭证已保存")
    
    return build('gmail', 'v1', credentials=creds)


def check_payment_emails(service, days=7):
    """检查付款相关邮件"""
    print(f"\n🔍 搜索最近 {days} 天的付款邮件...\n")
    
    # 计算日期范围
    after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
    
    # 搜索查询
    queries = [
        f'after:{after_date} (payment OR paid OR bounty OR reward OR payout OR transfer)',
        f'after:{after_date} from:github.com (merged OR congratulations)',
    ]
    
    all_messages = set()
    
    for query in queries:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        all_messages.update(msg['id'] for msg in messages)
    
    print(f"📧 发现 {len(all_messages)} 封相关邮件\n")
    
    # 检查每封邮件
    payment_emails = []
    
    for msg_id in list(all_messages)[:20]:  # 只检查前 20 封
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['subject', 'from', 'date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['metadata']['headers']}
        subject = headers.get('subject', '')
        from_ = headers.get('from', '')
        date = headers.get('date', '')
        
        # 检查是否是真实付款
        if any(k in subject.lower() for k in ['payment', 'paid', 'payout', 'transfer']):
            payment_emails.append({
                'subject': subject,
                'from': from_,
                'date': date
            })
            print(f"💰 {subject[:60]}")
            print(f"   From: {from_[:50]}")
            print(f"   Date: {date[:30]}\n")
    
    return payment_emails


def main():
    print("🚀 Gmail API 邮件检查")
    print("=" * 60)
    
    service = get_gmail_service()
    if not service:
        return 1
    
    try:
        # 获取邮箱信息
        profile = service.users().getProfile(userId='me').execute()
        print(f"\n📧 邮箱: {profile['emailAddress']}")
        print(f"📬 邮件总数: {profile['messagesTotal']:,}")
        print(f"📭 未读邮件: {profile['threadsUnread']:,}")
        
        # 检查付款邮件
        payments = check_payment_emails(service, days=7)
        
        print("=" * 60)
        print(f"✅ 检查完成：发现 {len(payments)} 封付款相关邮件")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
