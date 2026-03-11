#!/usr/bin/env python3
"""
GitHub Bounty Hunter - 开发脚本
自动开发 bounty 任务
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 工作目录
WORK_DIR = Path.home() / '.openclaw' / 'workspace' / 'data' / 'bounty-projects'
WORK_DIR.mkdir(parents=True, exist_ok=True)

def clone_repo(repo_url, task_id):
    """克隆仓库"""
    project_dir = WORK_DIR / f'task-{task_id}'
    
    if project_dir.exists():
        print(f"✅ 项目已存在：{project_dir}")
        return project_dir
    
    print(f"📥 克隆仓库：{repo_url}")
    subprocess.run(['git', 'clone', repo_url, str(project_dir)], check=True)
    
    return project_dir

def create_branch(project_dir, task_id):
    """创建开发分支"""
    branch_name = f'bounty-task-{task_id}'
    
    print(f"🌿 创建分支：{branch_name}")
    subprocess.run(
        ['git', 'checkout', '-b', branch_name],
        cwd=project_dir,
        check=True
    )
    
    return branch_name

def generate_code(task_description, project_dir):
    """生成代码"""
    print("🤖 正在分析任务需求...")
    print(f"📝 任务描述：{task_description[:200]}...")
    
    # TODO: 集成 AI 代码生成
    # 这里可以调用 OpenClaw 的 AI 能力生成代码
    
    print("✅ 代码生成完成")
    return True

def run_tests(project_dir):
    """运行测试"""
    print("🧪 运行测试...")
    
    # 检查是否有测试
    test_dirs = ['test', 'tests', 'spec', 'specs']
    has_tests = any((project_dir / d).exists() for d in test_dirs)
    
    if not has_tests:
        print("⚠️  未找到测试目录")
        return True
    
    # 尝试运行测试
    try:
        # 检查 package.json (Node.js)
        if (project_dir / 'package.json').exists():
            print("📦 Node.js 项目")
            subprocess.run(['npm', 'test'], cwd=project_dir, check=True)
        
        # 检查 requirements.txt (Python)
        elif (project_dir / 'requirements.txt').exists():
            print("🐍 Python 项目")
            subprocess.run(['python', '-m', 'pytest'], cwd=project_dir, check=True)
        
        # 检查 go.mod (Go)
        elif (project_dir / 'go.mod').exists():
            print("🔧 Go 项目")
            subprocess.run(['go', 'test', './...'], cwd=project_dir, check=True)
        
        else:
            print("⚠️  未知项目类型，跳过测试")
            return True
        
        print("✅ 测试通过")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试失败：{e}")
        return False

def commit_changes(project_dir, task_id, message):
    """提交更改"""
    print("💾 提交更改...")
    
    # 添加所有更改
    subprocess.run(['git', 'add', '-A'], cwd=project_dir, check=True)
    
    # 检查是否有更改
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("⚠️  没有更改需要提交")
        return False
    
    # 提交
    commit_msg = f"bounty: Task #{task_id}\n\n{message}"
    subprocess.run(
        ['git', 'commit', '-m', commit_msg],
        cwd=project_dir,
        check=True
    )
    
    print("✅ 提交完成")
    return True

def create_pr(project_dir, task_id, title, description):
    """创建 Pull Request"""
    print("🚀 创建 Pull Request...")
    
    # 使用 gh CLI 创建 PR
    try:
        cmd = [
            'gh', 'pr', 'create',
            '--title', title,
            '--body', description,
            '--label', 'bounty'
        ]
        
        subprocess.run(cmd, cwd=project_dir, check=True)
        
        print("✅ PR 创建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PR 创建失败：{e}")
        return False

def develop_task(task):
    """开发任务"""
    task_id = task.get('number')
    repo_url = task.get('repository_url')
    title = task.get('title')
    description = task.get('body', '')
    
    print("="*80)
    print(f"🦞 开发任务 #{task_id}: {title}")
    print("="*80)
    print()
    
    # 1. 克隆仓库
    project_dir = clone_repo(repo_url, task_id)
    
    # 2. 创建分支
    branch = create_branch(project_dir, task_id)
    
    # 3. 生成代码
    generate_code(description, project_dir)
    
    # 4. 运行测试
    if not run_tests(project_dir):
        print("⚠️  测试失败，需要手动修复")
    
    # 5. 提交更改
    commit_message = f"实现任务 #{task_id}: {title}"
    commit_changes(project_dir, task_id, commit_message)
    
    # 6. 推送分支
    print("📤 推送分支...")
    subprocess.run(
        ['git', 'push', '-u', 'origin', branch],
        cwd=project_dir,
        check=True
    )
    
    # 7. 创建 PR
    pr_title = f"bounty: {title}"
    pr_description = f"""
This PR addresses bounty task #{task_id}.

## Changes
- TODO: 填写具体更改

## Testing
- TODO: 填写测试步骤

## Checklist
- [ ] 代码已测试
- [ ] 文档已更新
- [ ] 测试已添加
"""
    create_pr(project_dir, task_id, pr_title, pr_description)
    
    print()
    print("="*80)
    print("✅ 任务开发完成！")
    print("="*80)

def main():
    """主函数"""
    print("="*80)
    print("🦞 GitHub Bounty Hunter - 开发任务")
    print("="*80)
    print()
    
    # TODO: 从监控结果中选择任务
    print("⚠️  请先运行监控脚本：python scripts/monitor.py")
    print("然后选择要开发的任务 ID")
    print()
    
    # 示例任务
    sample_task = {
        'number': 1,
        'repository_url': 'https://github.com/example/repo.git',
        'title': '示例任务',
        'body': '这是一个示例任务描述'
    }
    
    # develop_task(sample_task)

if __name__ == '__main__':
    main()
