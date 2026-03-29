# CHANGELOG Generator Skill

**用途**: 从git历史自动生成结构化CHANGELOG.md

---

## 功能

- ✅ 获取上次tag到现在的所有commits
- ✅ 自动分类: Added / Fixed / Changed / Removed
- ✅ 生成标准CHANGELOG格式
- ✅ 支持语义化版本控制

---

## 使用方法

### 方式1: OpenClaw命令
```
/generate-changelog
```

### 方式2: Bash脚本
```bash
bash changelog.sh
```

---

## 实现逻辑

```python
#!/usr/bin/env python3
"""
自动生成CHANGELOG
"""
import subprocess
import re
from datetime import datetime
from collections import defaultdict

def get_commits_since_last_tag():
    """获取上次tag后的所有commits"""
    try:
        # 获取最后一个tag
        last_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # 获取commits
        commits = subprocess.check_output(
            ['git', 'log', f'{last_tag}..HEAD', '--pretty=format:%s|%b'],
            stderr=subprocess.DEVNULL
        ).decode().strip().split('\n')
        
        return last_tag, commits
    except:
        # 如果没有tag，获取所有commits
        commits = subprocess.check_output(
            ['git', 'log', '--pretty=format:%s|%b', '-50']
        ).decode().strip().split('\n')
        return None, commits

def categorize_commit(message):
    """分类commit消息"""
    message_lower = message.lower()
    
    # Added (新功能)
    if any(word in message_lower for word in ['add', 'create', 'implement', 'introduce', 'support']):
        return 'Added', message
    
    # Fixed (修复)
    elif any(word in message_lower for word in ['fix', 'repair', 'resolve', 'correct', 'patch']):
        return 'Fixed', message
    
    # Changed (变更)
    elif any(word in message_lower for word in ['update', 'change', 'modify', 'improve', 'refactor', 'optimize']):
        return 'Changed', message
    
    # Removed (移除)
    elif any(word in message_lower for word in ['remove', 'delete', 'deprecate', 'drop']):
        return 'Removed', message
    
    # 默认为Changed
    else:
        return 'Changed', message

def generate_changelog():
    """生成CHANGELOG"""
    last_tag, commits = get_commits_since_last_tag()
    
    # 分类commits
    categories = defaultdict(list)
    for commit_line in commits:
        if not commit_line.strip():
            continue
        
        parts = commit_line.split('|')
        message = parts[0].strip()
        
        category, formatted_msg = categorize_commit(message)
        categories[category].append(formatted_msg)
    
    # 生成CHANGELOG内容
    changelog = []
    changelog.append("# Changelog\n")
    
    # 新版本
    version = "Unreleased" if not last_tag else f"Next after {last_tag}"
    changelog.append(f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n")
    
    # 按类别输出
    for category in ['Added', 'Changed', 'Fixed', 'Removed']:
        if categories[category]:
            changelog.append(f"\n### {category}\n")
            for msg in categories[category]:
                # 清理和格式化消息
                clean_msg = msg.strip()
                if clean_msg:
                    changelog.append(f"- {clean_msg}\n")
    
    return ''.join(changelog)

if __name__ == '__main__':
    print(generate_changelog())
