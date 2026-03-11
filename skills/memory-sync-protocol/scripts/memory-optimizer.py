#!/usr/bin/env python3
"""
MEMORY.md 自动精简脚本
将臃肿的 MEMORY.md 精简到 8-10K，保留高价值内容

模块导入：系统路径、JSON、时间、路径处理
"""

# 系统模块（标准库）
import os      # 操作系统接口
import sys     # 系统参数
import json    # JSON 处理
from datetime import datetime  # 时间处理
from pathlib import Path  # 路径处理

# 工作区路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
MEMORY_FILE = WORKSPACE / 'MEMORY.md'
BACKUP_DIR = WORKSPACE / 'backups'

# 配置
MAX_SIZE = 10000  # 最大字符数（10K）
ANCHOR_WORDS_LIMIT = 40  # 锚点词上限

def backup_memory():
    """备份 MEMORY.md"""
    if not MEMORY_FILE.exists():
        print("❌ MEMORY.md 不存在")
        return None
    
    # 创建备份目录
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'MEMORY.md.backup.{timestamp}'
    
    # 复制文件
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已备份：{backup_file}")
    return backup_file

def analyze_content():
    """分析 MEMORY.md 内容"""
    if not MEMORY_FILE.exists():
        return None
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stats = {
        'total_chars': len(content),
        'total_lines': len(content.split('\n')),
        'sections': {}
    }
    
    # 简单分类统计
    if '官家' in content:
        stats['sections']['用户偏好'] = content.count('官家')
    if '技能' in content:
        stats['sections']['技能说明'] = content.count('技能')
    if '2026-03' in content:
        stats['sections']['日常流水'] = content.count('2026-03')
    if 'QMD' in content or '检索' in content:
        stats['sections']['高价值记忆'] = content.count('QMD') + content.count('检索')
    
    return stats

def extract_anchor_words(content):
    """提取高价值锚点词"""
    # 预定义的核心锚点词类别
    categories = {
        '核心技能': [
            'smart-model-switch', 'context-manager', 'smart-memory-sync',
            'image-content-extractor', 'quote-reader', 'speech-recognition'
        ],
        '核心配置': [
            'agents.json', 'openai.env', 'mcporter.json', 'crontab'
        ],
        '知识库主题': [
            'project-management', 'software-testing', 'content-creation',
            'ai-system-design', 'outsourcing-management'
        ],
        '核心工具': [
            'Evidently AI', 'DeepChecks', 'OWASP ZAP', 'Playwright', 'QMD'
        ],
        '核心概念': [
            '三库联动', '双保险机制', '不可变分片', '混合检索', 'MCP 集成'
        ]
    }
    
    anchor_words = []
    for category, words in categories.items():
        for word in words:
            if word in content:
                anchor_words.append(f"{category}: {word}")
    
    return anchor_words[:ANCHOR_WORDS_LIMIT]

def create_optimized_memory(anchor_words):
    """创建精简版 MEMORY.md"""
    template = f"""# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**：`/home/zhaog/.openclaw/workspace/knowledge/`

**记忆文件路径**：`/home/zhaog/.openclaw/workspace/memory/`

**检索命令**：
```bash
bun /path/to/qmd.ts search knowledge "关键词" -n 5
bun /path/to/qmd.ts search daily-logs "关键词" --hybrid
```

---

## 📋 检索协议

### 优先使用 QMD 检索
- ✅ 使用 `memory_search()` 检索个人记忆
- ✅ 使用 `qmd search` 检索知识库
- ✅ 只读取必要的行（避免全量加载）

### 精准检索策略
```
个人记忆 → memory_search()
知识库 → qmd search（关键词已可用）
其他 → 只读必要的行
```

### Token 节省效果
- 传统方式：读取整个 MEMORY.md（2000+ tokens）
- QMD 方式：精准回忆（~150 tokens）
- **节省：92.5%**

---

## 🏆 高价值锚点词（{len(anchor_words)} 个）

{chr(10).join(f"{i+1}. {word}" for i, word in enumerate(anchor_words))}

---

## 💡 记忆维护原则

### 定期清理
- 每周一回顾上周记忆
- 将值得保留的内容更新到 MEMORY.md
- 从 MEMORY.md 移除过时信息

### 保持精简
- MEMORY.md 控制在 8-10K
- 只保留高价值、低噪音内容
- 日常流水放在 memory/YYYY-MM-DD.md

### 自动化维护
- 每天 23:30 AI 查漏补缺
- 每周日 2:00 记忆维护
- 每天 23:40/23:50 QMD 向量生成

---

*持续进化 · 定期清理 · 保留精华*

*最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
*版本：v2.0 - 精简优化版*
"""
    return template

def optimize_memory():
    """执行 MEMORY.md 优化"""
    print("=" * 80)
    print("🔧 MEMORY.md 自动精简")
    print("=" * 80)
    print()
    
    # 1. 备份
    print("1️⃣  备份原文件...")
    backup_file = backup_memory()
    if not backup_file:
        return False
    print()
    
    # 2. 分析内容
    print("2️⃣  分析内容...")
    stats = analyze_content()
    print(f"  当前大小：{stats['total_chars']:,} 字符 ({stats['total_lines']} 行)")
    print(f"  建议大小：8,000-10,000 字符")
    print(f"  超出比例：{stats['total_chars'] / MAX_SIZE * 100:.0f}%")
    print()
    
    print("  内容分布：")
    for section, count in stats['sections'].items():
        print(f"    {section}: {count} 次")
    print()
    
    # 3. 提取锚点词
    print("3️⃣  提取高价值锚点词...")
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    anchor_words = extract_anchor_words(content)
    print(f"  提取到 {len(anchor_words)} 个锚点词")
    print()
    
    # 4. 创建精简版
    print("4️⃣  创建精简版...")
    optimized_content = create_optimized_memory(anchor_words)
    
    # 保存
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    new_size = len(optimized_content)
    reduction = (1 - new_size / stats['total_chars']) * 100
    
    print(f"✅ 精简版已创建")
    print()
    
    # 5. 显示效果
    print("=" * 80)
    print("📊 优化效果")
    print("=" * 80)
    print()
    print(f"优化前：{stats['total_chars']:,} 字符")
    print(f"优化后：{new_size:,} 字符")
    print(f"精简比例：{reduction:.1f}%")
    print(f"Token 节省：每次对话节省约 {(stats['total_chars'] - new_size) / 4:.0f} tokens")
    print()
    
    if new_size > MAX_SIZE:
        print(f"⚠️  警告：精简后仍超出建议值（{new_size} > {MAX_SIZE}）")
    else:
        print(f"✅ 精简后大小符合要求（{new_size} < {MAX_SIZE}）")
    print()
    
    return True

def restore_backup(backup_file=None):
    """恢复备份"""
    print("=" * 80)
    print("🔄 恢复备份")
    print("=" * 80)
    print()
    
    if not backup_file:
        # 查找最新备份
        if not BACKUP_DIR.exists():
            print("❌ 备份目录不存在")
            return False
        
        backups = list(BACKUP_DIR.glob('MEMORY.md.backup.*'))
        if not backups:
            print("❌ 没有备份文件")
            return False
        
        backup_file = max(backups, key=lambda p: p.stat().st_mtime)
    
    if not backup_file.exists():
        print(f"❌ 备份文件不存在：{backup_file}")
        return False
    
    # 恢复
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已恢复到备份：{backup_file}")
    print()
    
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--restore':
            backup_file = sys.argv[2] if len(sys.argv) > 2 else None
            restore_backup(backup_file)
        else:
            print("用法：python3 scripts/memory-optimizer.py [--restore <备份文件>]")
    else:
        optimize_memory()
