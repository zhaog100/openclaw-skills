#!/bin/bash
# Git智能合并脚本
# 创建时间：2026-03-11
# 用途：自动检测冲突并智能合并

set -e

echo "=== Git智能合并脚本 ==="

# 1. 检查Git状态
if [[ -n $(git status --short) ]]; then
    echo "⚠️ 有未提交的更改，先提交"
    git add -A
    git commit -m "chore: 自动提交（智能合并前）"
fi

# 2. 获取远程更新
echo "📥 获取远程更新..."
git fetch origin

# 3. 检查是否需要合并
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ 本地与远程同步，无需合并"
    exit 0
fi

# 4. 检查冲突
echo "🔍 检查冲突..."
CONFLICTS=$(git diff --name-only HEAD origin/master | wc -l)

if [ "$CONFLICTS" -eq 0 ]; then
    echo "✅ 无冲突，直接合并"
    git merge origin/master --no-edit
    echo "✅ 合并完成"
    exit 0
fi

echo "⚠️ 发现 $CONFLICTS 个冲突文件"

# 5. 尝试自动合并
echo "🔄 尝试自动合并..."
git merge origin/master --no-edit || {
    echo "⚠️ 自动合并失败，需要手动处理"
    
    # 6. 检查冲突标记
    CONFLICT_FILES=$(grep -r "<<<<<<" . --include="*.md" --include="*.json" -l 2>/dev/null || echo "")
    
    if [ -n "$CONFLICT_FILES" ]; then
        echo "⚠️ 以下文件有冲突标记："
        echo "$CONFLICT_FILES"
        
        # 7. 按文件类型处理
        for file in $CONFLICT_FILES; do
            echo "处理冲突文件：$file"
            
            case "$file" in
                *.md)
                    echo "Markdown文件：需要手动合并"
                    echo "建议：保留双方优点，删除冲突标记"
                    ;;
                *.json)
                    echo "JSON文件：使用本地版本"
                    git checkout --ours "$file"
                    git add "$file"
                    ;;
            esac
        done
        
        echo "❌ 请手动解决Markdown文件冲突"
        echo "解决后运行：git add . && git commit"
        exit 1
    fi
}

echo "✅ 智能合并完成"
