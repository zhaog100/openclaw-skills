#!/bin/bash
# 小米粒完整工作流程 - 包含学习Review

set -e

echo "🌾 === 小米粒完整工作流程 ==="

# ===== 步骤1：检查Review结果 =====
echo ""
echo "=== 步骤1：检查Review结果 ==="

if [ -f /tmp/review_approved.txt ]; then
    echo "✅ 发现Review通过通知："
    cat /tmp/review_approved.txt
    APPROVED=true
elif [ -f /tmp/review_rejected.txt ]; then
    echo "❌ 发现Review拒绝通知："
    cat /tmp/review_rejected.txt
    APPROVED=false
else
    echo "⏳ 暂无Review结果"
    echo "请等待米粒儿Review完成"
    exit 0
fi

# ===== 步骤2：读取Review文档 =====
echo ""
echo "=== 步骤2：读取Review文档 ==="

REVIEW_DIR="/root/.openclaw/workspace/reviews"
if [ -d "$REVIEW_DIR" ]; then
    LATEST_REVIEW=$(ls -t "$REVIEW_DIR"/*.md 2>/dev/null | head -1)
    
    if [ -n "$LATEST_REVIEW" ]; then
        echo "📄 最新Review：$(basename $LATEST_REVIEW)"
        echo "================================"
        
        # 显示Review结果
        grep -A 3 "## 📊 Review结果" "$LATEST_REVIEW" || echo "无结果"
        
        echo ""
        echo "💡 学习要点："
        grep -A 10 "## 🎓 学习要点" "$LATEST_REVIEW" | tail -10 || echo "无学习要点"
        
        echo ""
        echo "📝 改进建议："
        grep -A 10 "## 📝 改进建议" "$LATEST_REVIEW" | grep -A 5 "短期改进" | tail -6 || echo "无改进建议"
        
        echo ""
        echo "🤝 给小米粒的建议："
        grep -A 15 "## 🤝 给小米粒的建议" "$LATEST_REVIEW" | tail -15 || echo "无建议"
        
        echo ""
        read -p "查看完整Review？(y/n): " VIEW_FULL
        if [ "$VIEW_FULL" = "y" ]; then
            ${EDITOR:-less} "$LATEST_REVIEW"
        fi
    else
        echo "❌ 没有找到Review文档"
    fi
else
    echo "❌ Review目录不存在"
fi

# ===== 步骤3：根据Review结果采取行动 =====
echo ""
echo "=== 步骤3：根据Review结果采取行动 ==="

if [ "$APPROVED" = true ]; then
    echo "✅ Review通过，开始合并和发布"
    
    # 获取技能名称
    SKILL_NAME=$(cat /tmp/review_approved.txt | awk '{print $4}')
    
    # 切换到master
    cd /root/.openclaw/workspace
    git checkout master
    git pull origin master
    
    # 合并分支
    echo ""
    echo "合并分支 feature/$SKILL_NAME 到 master"
    git merge feature/$SKILL_NAME --no-ff -m "merge: 合并 $SKILL_NAME Review通过

Review评分：$(grep "总体评价" "$LATEST_REVIEW" 2>/dev/null | head -1 || echo "未找到")
Review文档：reviews/${SKILL_NAME}_*.md"
    
    # 推送
    git push origin master
    
    # 询问是否发布到ClawHub
    echo ""
    read -p "发布到ClawHub？(y/n): " PUBLISH
    if [ "$PUBLISH" = "y" ]; then
        cd /root/.openclaw/workspace/skills/$SKILL_NAME
        read -p "版本号（如1.0.0）: " VERSION
        clawhub publish . --slug $SKILL_NAME --version $VERSION --name "$SKILL_NAME"
        
        # 记录操作
        echo "$(date '+%Y-%m-%d %H:%M:%S') | 小米粒 | 发布 | $SKILL_NAME v$VERSION | 成功" >> /root/.openclaw/workspace/logs/clawhub_operations.log
        
        echo "✅ 发布完成！"
        echo "ClawHub链接：https://clawhub.com/skills/$SKILL_NAME"
    fi
    
    # 清理分支
    echo ""
    read -p "删除feature分支？(y/n): " DELETE_BRANCH
    if [ "$DELETE_BRANCH" = "y" ]; then
        git branch -d feature/$SKILL_NAME
        git push origin --delete feature/$SKILL_NAME 2>/dev/null || echo "远程分支已删除或不存在"
        echo "✅ 分支已删除"
    fi
    
    # 清理通知文件
    rm -f /tmp/review_approved.txt /tmp/review_rejected.txt /tmp/notify_xiaomi.txt
    
else
    echo "❌ Review拒绝，需要修改"
    
    # 获取技能名称
    SKILL_NAME=$(cat /tmp/review_rejected.txt | awk '{print $4}')
    
    echo ""
    echo "根据Review建议修改技能："
    echo "1. 查看详细Review了解问题"
    echo "2. 修改代码"
    echo "3. 重新提交Review"
    echo ""
    echo "切换到分支：feature/$SKILL_NAME"
    cd /root/.openclaw/workspace
    git checkout feature/$SKILL_NAME
    
    echo ""
    echo "💡 提示："
    echo "1. 修改技能代码"
    echo "2. 测试功能"
    echo "3. 提交：git add . && git commit -m 'fix: 根据Review修改'"
    echo "4. 推送：git push origin feature/$SKILL_NAME"
    echo "5. 通知米粒儿：bash scripts/xiaomi_agent_a.sh"
fi

echo ""
echo "✅ 小米粒工作流程完成"
