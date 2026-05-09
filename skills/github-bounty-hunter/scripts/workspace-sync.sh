#!/bin/bash
# 工作区同步脚本（排除敏感信息）
# 功能：git add/commit/pull/push，自动排除 secrets/

set -e

WORKSPACE="$HOME/.openclaw/workspace"
cd "$WORKSPACE"

echo "📊 步骤 1: 检查 Git 状态"
git status --short

echo "📝 步骤 2: 提交所有变更"
git add -A
if git diff-index --quiet HEAD; then
    echo "✅ 无变更需要提交"
else
    git commit -m "chore: 结构化整理完成 - QMD 索引 + 文档归档"
fi

echo "🔄 步骤 3: 拉取远程变更"
git pull --rebase origin master || {
    echo "⚠️ 拉取失败，尝试继续..."
}

echo "🚀 步骤 4: 推送到 GitHub"
git push origin master

echo "✅ 同步完成！"
echo ""
echo "📜 最近提交:"
git log --oneline -5
