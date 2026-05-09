#!/usr/bin/env python3
"""
监控 PR 审核状态脚本
定期检查高价值 PR 的审核进展
"""

import os
import sys
import subprocess
from datetime import datetime

def run_gh_command(cmd):
    """执行 gh 命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_ubiquityos_prs():
    """检查 UbiquityOS PR 状态"""
    print("📊 检查 UbiquityOS PR 状态...")
    
    # 查询 OPEN PR
    success, stdout, stderr = run_gh_command(
        'gh api "search/issues?q=org:ubiquity-os+author:zhaog100+type:pr+state:open&per_page=5" --jq \'.items[] | \"\\(.html_url) | \\(..title) | \\(..updated_at)\"\''
    )
    
    if success:
        open_prs = stdout.strip().split('\n') if stdout.strip() else []
        print(f"  OPEN PR: {len(open_prs)} 个")
        for pr in open_prs[:3]:  # 只显示前3个
            print(f"    - {pr}")
    else:
        print(f"  ❌ 查询失败: {stderr}")
    
    # 查询 MERGED PR
    success, stdout, stderr = run_gh_command(
        'gh api "search/issues?q=org:ubiquity-os+author:zhaog100+type:pr+is:merged&per_page=3" --jq \'.items[] | \"\\(.html_url) | \\(..title)\"\''
    )
    
    if success:
        merged_prs = stdout.strip().split('\n') if stdout.strip() else []
        print(f"  MERGED PR: {len(merged_prs)} 个")
    
    return len(open_prs) if 'open_prs' in locals() else 0

def check_rustchain_pr():
    """检查 RustChain #2890 状态"""
    print("\n📊 检查 RustChain #2890...")
    
    success, stdout, stderr = run_gh_command(
        'gh pr view 186 --json state,title,updatedAt,url 2>&1'
    )
    
    if success:
        print(f"  {stdout}")
    else:
        print(f"  ❌ 查询失败: {stderr}")

def check_midnightntwrk_issue():
    """检查 midnightntwrk #205 状态"""
    print("\n📊 检查 midnightntwrk #205...")
    
    success, stdout, stderr = run_gh_command(
        'gh api "repos/midnightntwrk/contributor-hub/issues/205" --jq \'"状态: \\(..state) | 标题: \\(..title) | 更新: \\(..updated_at)"\' 2>&1'
    )
    
    if success:
        print(f"  {stdout}")
    else:
        print(f"  ❌ 查询失败: {stderr}")

def check_maintainer_activity():
    """检查维护者活动"""
    print("\n📊 检查 gentlementlegen 活动...")
    
    success, stdout, stderr = run_gh_command(
        'gh api "users/gentlementlegen/events?per_page=3" --jq \'.[] | \"\\(..type) | \\(..repo.name) | \\(..created_at)\"\' 2>&1'
    )
    
    if success and stdout.strip():
        activities = stdout.strip().split('\n')
        print(f"  最近活动:")
        for activity in activities:
            print(f"    - {activity}")
    else:
        print(f"  ❌ 查询失败: {stderr}")

def main():
    print(f"\n🔍 PR 审核状态监控 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 60)
    
    # 检查各项状态
    open_count = check_ubiquityos_prs()
    check_rustchain_pr()
    check_midnightntwrk_issue()
    check_maintainer_activity()
    
    print("\n" + "=" * 60)
    print(f"📋 总结:")
    print(f"  - UbiquityOS OPEN PR: {open_count} 个")
    print(f"  - 总价值: $10,680+")
    print(f"  - 到账: $0 ⚠️")
    print(f"  - 状态: 等待人工审核")
    
if __name__ == '__main__':
    main()
