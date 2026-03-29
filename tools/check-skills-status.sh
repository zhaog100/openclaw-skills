#!/bin/bash
# 检查所有技能的启用状态

echo "========================================="
echo "🔍 本地技能启用状态检查"
echo "========================================="
echo ""

skills_dir="$HOME/.openclaw/workspace/skills"
cd "$skills_dir" || exit 1

# 获取所有定时任务
cron_tasks=$(crontab -l 2>/dev/null)

echo "📋 已启用的技能（有定时任务）："
echo ""

# 检查每个技能
for skill_dir in */; do
  skill_name=${skill_dir%/}

  if [ -f "$skill_name/package.json" ]; then
    name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill_name/package.json" | grep -o '"[^"]*"$' | tr -d '"')
    version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill_name/package.json" | grep -o '"[^"]*"$' | tr -d '"')

    # 检查是否有定时任务
    has_cron=0
    if echo "$cron_tasks" | grep -q "$skill_name\|$name"; then
      has_cron=1
    fi

    # 检查是否有运行中的进程
    has_process=0
    if ps aux | grep -v grep | grep -q "$skill_name\|$name"; then
      has_process=1
    fi

    if [ $has_cron -eq 1 ] || [ $has_process -eq 1 ]; then
      echo "✅ $name v$version"
      [ $has_cron -eq 1 ] && echo "   定时任务：✅"
      [ $has_process -eq 1 ] && echo "   进程运行：✅"
      echo ""
    fi
  fi
done

echo ""
echo "⏸️ 未启用的技能（无定时任务）："
echo ""

for skill_dir in */; do
  skill_name=${skill_dir%/}

  if [ -f "$skill_name/package.json" ]; then
    name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill_name/package.json" | grep -o '"[^"]*"$' | tr -d '"')
    version=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill_name/package.json" | grep -o '"[^"]*"$' | tr -d '"')

    # 检查是否有定时任务
    has_cron=0
    if echo "$cron_tasks" | grep -q "$skill_name\|$name"; then
      has_cron=1
    fi

    # 检查是否有运行中的进程
    has_process=0
    if ps aux | grep -v grep | grep -q "$skill_name\|$name"; then
      has_process=1
    fi

    if [ $has_cron -eq 0 ] && [ $has_process -eq 0 ]; then
      desc=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$skill_name/package.json" | head -1 | grep -o '"[^"]*"$' | tr -d '"' | cut -c1-60)
      echo "⏸️ $name v$version"
      echo "   $desc"
      echo ""
    fi
  fi
done

echo "========================================="
echo "✅ 检查完成"
echo "========================================="
