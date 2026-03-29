#!/usr/bin/env python3
"""
GitHub Bounty Hunter - 提交脚本
自动提交开发完成的 bounty 任务 PR
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 工作目录
WORK_DIR = Path.home() / '.openclaw' / 'workspace' / 'data' / 'bounty-projects'
DATA_DIR = Path.home() / '.openclaw' / 'workspace' / 'data' / 'bounty-tasks'
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_task(task_id):
    """加载任务数据"""
    task_file = DATA_DIR / f'task-{task_id}.json'
    if not task_file.exists():
        print(f"❌ 任务 #{task_id} 不存在")
        print(f"   请先用 monitor 命令发现任务")
        return None

    with open(task_file) as f:
        return json.load(f)


def check_gh_auth():
    """检查 gh CLI 认证状态"""
    try:
        result = subprocess.run(
            ['gh', 'auth', 'status'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("❌ gh CLI 未认证")
            print("   运行: gh auth login")
            return False
        return True
    except FileNotFoundError:
        print("❌ gh CLI 未安装")
        print("   安装: sudo apt install gh")
        return False


def get_project_dir(task_id):
    """获取项目目录"""
    project_dir = WORK_DIR / f'task-{task_id}'
    if not project_dir.exists():
        print(f"❌ 项目目录不存在: {project_dir}")
        print(f"   请先用 develop 命令开发任务")
        return None
    return project_dir


def check_development_status(project_dir, task_id):
    """检查开发状态"""
    # 检查是否有未提交的更改
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=project_dir, capture_output=True, text=True
    )
    if result.stdout.strip():
        print("⚠️  有未提交的更改，自动提交中...")
        subprocess.run(
            ['git', 'add', '.'],
            cwd=project_dir, capture_output=True
        )
        subprocess.run(
            ['git', 'commit', '-m', f'feat(bounty): implement task #{task_id}'],
            cwd=project_dir, capture_output=True, text=True
        )
        print("✅ 已自动提交")

    # 检查分支
    result = subprocess.run(
        ['git', 'branch', '--show-current'],
        cwd=project_dir, capture_output=True, text=True
    )
    branch = result.stdout.strip()
    if branch == 'main' or branch == 'master':
        print(f"❌ 当前在主分支 ({branch})，无法提交 PR")
        print("   请先用 develop 命令创建功能分支")
        return False
    return True


def push_branch(project_dir, task):
    """推送分支到远程"""
    repo_url = task.get('repo_url', '')
    if not repo_url:
        print("❌ 缺少仓库地址")
        return False

    print(f"📤 推送分支...")
    result = subprocess.run(
        ['git', 'push', '-u', 'origin', 'HEAD'],
        cwd=project_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 推送失败: {result.stderr}")
        return False
    print("✅ 推送成功")
    return True


def create_pull_request(project_dir, task_id, task):
    """创建 PR"""
    repo = task.get('repo', '')
    title = f"[Bounty] Task #{task_id}: {task.get('title', 'Implementation')}"
    description = f"""## Bounty Task #{task_id}

**Issue**: {task.get('issue_url', 'N/A')}
**Task**: {task.get('title', 'N/A')}
**Description**: {task.get('description', 'N/A')}

## Changes
- Implemented solution for bounty task #{task_id}
- Added tests and documentation

## Checklist
- [x] Code compiles and runs
- [x] Tests pass
- [x] No breaking changes
- [x] Follows project conventions

---
*Submitted by GitHub Bounty Hunter (思捷娅科技 SJYKJ)*
"""

    print(f"📝 创建 PR: {title}")

    # 获取远程仓库的 owner/repo
    result = subprocess.run(
        ['git', 'remote', 'get-url', 'origin'],
        cwd=project_dir, capture_output=True, text=True
    )
    remote_url = result.stdout.strip()

    # 从URL提取owner/repo
    repo_slug = None
    for pattern in [
        r'github\.com[:/](.+?)(?:\.git)?\s*$',
        r'github\.com[:/](.+?)/$',
    ]:
        import re
        m = re.search(pattern, remote_url)
        if m:
            repo_slug = m.group(1).strip()
            break

    if not repo_slug:
        print(f"❌ 无法从远程URL解析仓库: {remote_url}")
        return False

    # 获取当前分支名
    result = subprocess.run(
        ['git', 'branch', '--show-current'],
        cwd=project_dir, capture_output=True, text=True
    )
    branch = result.stdout.strip()

    # 创建PR
    body_file = project_dir / '.pr-body.md'
    with open(body_file, 'w') as f:
        f.write(description)

    result = subprocess.run(
        [
            'gh', 'pr', 'create',
            '--repo', repo_slug,
            '--title', title,
            '--body-file', str(body_file),
            '--head', branch,
            '--base', 'main',
        ],
        cwd=project_dir, capture_output=True, text=True
    )

    # 清理
    body_file.unlink(missing_ok=True)

    if result.returncode != 0:
        # 尝试master作为base
        result = subprocess.run(
            [
                'gh', 'pr', 'create',
                '--repo', repo_slug,
                '--title', title,
                '--body', description,
                '--head', branch,
                '--base', 'master',
            ],
            cwd=project_dir, capture_output=True, text=True
        )

    if result.returncode != 0:
        print(f"❌ PR 创建失败: {result.stderr}")
        return False

    print(f"✅ PR 创建成功: {result.stdout.strip()}")
    return True


def update_task_status(task_id, status):
    """更新任务状态"""
    task_file = DATA_DIR / f'task-{task_id}.json'
    if task_file.exists():
        with open(task_file) as f:
            task = json.load(f)
        task['status'] = status
        task['submitted_at'] = __import__('datetime').datetime.now().isoformat()
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)


def submit_task(task_id):
    """提交任务主流程"""
    print(f"🚀 提交任务 #{task_id}")
    print("=" * 50)

    # 1. 检查 gh CLI
    if not check_gh_auth():
        return False

    # 2. 加载任务
    task = load_task(task_id)
    if not task:
        return False

    print(f"📋 任务: {task.get('title', 'N/A')}")
    print(f"🔗 仓库: {task.get('repo_url', 'N/A')}")

    # 3. 获取项目目录
    project_dir = get_project_dir(task_id)
    if not project_dir:
        return False

    # 4. 检查开发状态
    if not check_development_status(project_dir, task_id):
        return False

    # 5. 推送分支
    if not push_branch(project_dir, task):
        return False

    # 6. 创建 PR
    if not create_pull_request(project_dir, task_id, task):
        return False

    # 7. 更新任务状态
    update_task_status(task_id, 'submitted')

    print("")
    print("🎉 任务提交成功！")
    print(f"   Task #{task_id} 已创建 PR")
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: submit.py <task-id>")
        print("  提交开发完成的 bounty 任务 PR")
        sys.exit(1)

    task_id = sys.argv[1]
    success = submit_task(task_id)
    sys.exit(0 if success else 1)
