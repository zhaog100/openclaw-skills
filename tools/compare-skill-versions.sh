#!/bin/bash
# ClawHub 技能版本对比脚本

LOCAL_SKILLS=$(cd ~/.openclaw/workspace/skills && for dir in */; do
  skill=${dir%/}
  if [ -f "$skill/package.json" ]; then
    version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill/package.json" | grep -o '"[^"]*"$' | tr -d '"')
    name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill/package.json" | grep -o '"[^"]*"$' | tr -d '"')
    echo "$name|$version|$skill"
  fi
done | sort)

echo "========================================="
echo "🔍 本地技能版本检查"
echo "========================================="
echo ""

echo "$LOCAL_SKILLS" | while IFS='|' read name version dir; do
  echo "技能: $name"
  echo "  本地版本: $version"
  echo "  目录: $dir"
  echo ""
done

echo "========================================="
echo "🌐 正在检查远程版本..."
echo "========================================="
echo "（需要等待API限流解除，约1分钟后）"
echo ""
