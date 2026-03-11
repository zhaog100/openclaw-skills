#!/bin/bash
# 米粒儿工作流程 - ClawHub协作（智能体B）
# 米粒儿负责Review小米粒的技能

echo "🌾 === 米粒儿工作流程（智能体B）==="
echo "我是米粒儿，和小姐姐一起管理ClawHub！"

if [ -f /tmp/notify_mili.txt ]; then
    echo "✅ 发现小米粒的新Review请求："
    cat /tmp/notify_mili.txt
    SKILL_NAME=$(cat /tmp/notify_mili.txt | awk '{print $4}')
else
    echo "❌ 没有小米粒的Review请求"
    echo "手动检查Git分支："
    git branch -r | grep feature/
    read -p "请输入要Review的技能名称: " SKILL_NAME
fi

cd /root/.openclaw/workspace
git fetch origin
git checkout feature/$SKILL_NAME
echo "✅ 米粒儿已切换到分支：feature/$SKILL_NAME"

echo "=== 米粒儿Review小米粒的代码 ==="
git diff master...feature/$SKILL_NAME
read -p "代码检查通过？(y/n): " CODE_OK

if [ -f /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh ]; then
    bash /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh
    read -p "功能测试通过？(y/n): " TEST_OK
else
    echo "⚠️  未找到测试脚本"
    read -p "手动测试通过？(y/n): " TEST_OK
fi

if [ "$CODE_OK" = "y" ] && [ "$TEST_OK" = "y" ]; then
    echo "$(date) | 米粒儿 | Review通过 | $SKILL_NAME | 小姐姐可以发布" > /tmp/review_approved.txt
    echo "$(date) | 米粒儿 | Review通过 | $SKILL_NAME | 代码和测试通过" >> /root/.openclaw/workspace/logs/clawhub_operations.log
    git add /root/.openclaw/workspace/logs/clawhub_operations.log
    git commit -m "chore: 米粒儿Review通过 - 小姐姐的 $SKILL_NAME"
    git push origin feature/$SKILL_NAME
    echo "$(date) | 米粒儿 | Review通过 | $SKILL_NAME | 小姐姐可以发布" > /tmp/notify_xiaomi.txt
    echo "✅ 米粒儿Review通过！已通知小姐姐"
else
    echo "$(date) | 米粒儿 | Review拒绝 | $SKILL_NAME | 需要修改" > /tmp/review_rejected.txt
    read -p "请输入需要修改的问题: " ISSUES
    echo "$(date) | 米粒儿 | Review问题 | $SKILL_NAME | $ISSUES" >> /tmp/review_rejected.txt
    echo "❌ Review未通过，已通知小姐姐需要修改"
fi

git checkout master
echo "✅ 米粒儿工作流程完成"
