================================================================================
米粒儿优化版Review脚本（完整代码）
双向思考策略 - 方案B+D落地实施
================================================================================

#!/bin/bash
# 米粒儿优化版Review脚本
# 整合方案B（独立文档）+ 方案D（自动化流程）+ 双向思考策略

set -e

echo "🌾 === 米粒儿优化版Review工作流程 ==="
echo "我是米粒儿，现在开始详细Review小米粒的技能！"
echo "💡 已启用双向思考策略"
echo ""

# ===== 步骤1：检查Review请求 =====
echo "=== 步骤1：检查Review请求 ==="
if [ -f /tmp/notify_mili.txt ]; then
    echo "✅ 发现小米粒的Review请求："
    cat /tmp/notify_mili.txt
    SKILL_NAME=$(cat /tmp/notify_mili.txt | awk '{print $4}')
    echo ""
    echo "📋 待Review技能：$SKILL_NAME"
else
    echo "❌ 没有小米粒的Review请求"
    echo ""
    echo "手动检查Git分支："
    git branch -r | grep feature/
    echo ""
    read -p "请输入要Review的技能名称: " SKILL_NAME
fi

# ===== 步骤2：读取小米粒的自检清单（新增）⭐ =====
echo ""
echo "=== 步骤2：读取小米粒的自检清单 ==="
SELF_CHECK_FILE="/tmp/self_review_checklist.md"
if [ -f "$SELF_CHECK_FILE" ]; then
    echo "✅ 发现小米粒的自检清单："
    echo "================================"
    cat "$SELF_CHECK_FILE"
    echo "================================"
    echo ""
    
    # 提取关键信息
    echo "💡 小米粒的提示："
    grep -A 10 "给米粒儿的提示" "$SELF_CHECK_FILE" | head -15 || echo "无提示"
    echo ""
else
    echo "⚠️  未找到小米粒的自检清单"
    echo "建议：小米粒应该先创建自检清单"
    echo ""
fi

# ===== 步骤3：准备Review环境 =====
echo ""
echo "=== 步骤3：准备Review环境 ==="
cd /root/.openclaw/workspace
git fetch origin
git checkout feature/$SKILL_NAME 2>/dev/null || {
    echo "❌ 分支不存在，切换到master"
    git checkout master
}
echo "✅ Review环境准备完成"

# ===== 步骤4：代码分析 =====
echo ""
echo "=== 步骤4：代码分析 ==="
echo "📊 文件变更统计："
git diff --stat master...feature/$SKILL_NAME 2>/dev/null || echo "无差异或已在master"

echo ""
echo "📄 代码差异（前50行）："
git diff master...feature/$SKILL_NAME 2>/dev/null | head -50

# ===== 步骤5：创建Review文档 =====
echo ""
echo "=== 步骤5：创建Review文档 ==="
REVIEW_DIR="/root/.openclaw/workspace/reviews"
mkdir -p "$REVIEW_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REVIEW_FILE="$REVIEW_DIR/${SKILL_NAME}_${TIMESTAMP}.md"

# 基于模板创建
cp /root/.openclaw/workspace/.clawhub/review_template.md "$REVIEW_FILE"

# 自动填充基本信息
sed -i "s/\[技能名称\]/$SKILL_NAME/g" "$REVIEW_FILE"
sed -i "s/\[YYYY-MM-DD HH:MM:SS\]/$(date '+%Y-%m-%d %H:%M:%S')/g" "$REVIEW_FILE"

echo "✅ Review文档已创建："
echo "   $REVIEW_FILE"

# ===== 步骤6：交互式Review（优化版）⭐ =====
echo ""
echo "=== 步骤6：交互式Review（双向思考）==="
echo "📝 请输入Review信息："
echo ""

# 代码质量评估
read -p "1. 代码质量评分（1-5星）: " CODE_QUALITY
read -p "2. 主要优点（用逗号分隔）: " PROS
read -p "3. 需要改进（用逗号分隔）: " CONS

# 功能测试
echo ""
echo "功能测试："
if [ -f /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh ]; then
    echo "执行测试脚本..."
    bash /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh
    read -p "4. 功能测试通过？(y/n): " TEST_OK
else
    echo "⚠️  未找到测试脚本"
    read -p "4. 手动测试通过？(y/n): " TEST_OK
fi

# 技术要点
echo ""
read -p "5. 关键技术点（用逗号分隔）: " KEY_POINTS
read -p "6. 风险点（用逗号分隔）: " RISKS

# 改进建议
echo ""
read -p "7. 短期改进建议（用逗号分隔）: " SHORT_IMPROVEMENTS
read -p "8. 长期改进建议（用逗号分隔）: " LONG_IMPROVEMENTS

# 学习要点
echo ""
read -p "9. 小米粒做得好的地方（用逗号分隔）: " GOOD_POINTS
read -p "10. 需要改进的地方（用逗号分隔）: " IMPROVEMENT_POINTS

# 给小米粒的建议
echo ""
read -p "11. 技术建议（用逗号分隔）: " TECH_SUGGESTIONS
read -p "12. 协作建议（用逗号分隔）: " COLLAB_SUGGESTIONS

# ===== 步骤7：考虑小米粒的疑问（新增）⭐ =====
echo ""
echo "=== 步骤7：考虑小米粒的疑问 ==="
if [ -f "$SELF_CHECK_FILE" ]; then
    echo "📋 回答小米粒的疑问："
    grep -A 10 "疑问点" "$SELF_CHECK_FILE" | tail -10 || echo "无疑问"
    echo ""
    read -p "回答小米粒的疑问（用逗号分隔）: " ANSWER_DOUBTS
else
    ANSWER_DOUBTS="无"
fi

# ===== 步骤8：更新Review文档 =====
echo ""
echo "=== 步骤8：更新Review文档 ==="

# 替换占位符
sed -i "s/\[观察点1\]/$PROS/g" "$REVIEW_FILE"
sed -i "s/\[优点1\]/$GOOD_POINTS/g" "$REVIEW_FILE"
sed -i "s/\[需要改进\]/$CONS/g" "$REVIEW_FILE"
sed -i "s/\[技术点1\]/$KEY_POINTS/g" "$REVIEW_FILE"
sed -i "s/\[风险1\]/$RISKS/g" "$REVIEW_FILE"
sed -i "s/\[建议1\]/$SHORT_IMPROVEMENTS/g" "$REVIEW_FILE"
sed -i "s/X\/5星/${CODE_QUALITY}\/5星/g" "$REVIEW_FILE"

# 添加回答小米粒的疑问（新增）⭐
if [ "$ANSWER_DOUBTS" != "无" ]; then
    echo "" >> "$REVIEW_FILE"
    echo "## 💬 回答小米粒的疑问" >> "$REVIEW_FILE"
    echo "" >> "$REVIEW_FILE"
    echo "$ANSWER_DOUBTS" | tr ',' '\n' | while read doubt; do
        echo "- $doubt" >> "$REVIEW_FILE"
    done
fi

echo "✅ Review文档已更新"

# ===== 步骤9：做出决定 =====
echo ""
echo "=== 步骤9：Review决定 ==="

if [ "$TEST_OK" = "y" ]; then
    echo ""
    echo "✅ Review通过"
    
    # 更新Review文档
    sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/✅ 批准发布/g" "$REVIEW_FILE"
    
    # 创建批准文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review通过 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/review_approved.txt
    
    # 提交到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review通过

Review思路：
- 代码质量：$CODE_QUALITY/5星
- 优点：$PROS
- 改进：$CONS
- 详细Review：reviews/${SKILL_NAME}_${TIMESTAMP}.md

Reviewed-by: 米粒儿"
    
    # 推送
    git push origin feature/$SKILL_NAME 2>/dev/null || git push origin master
    
    # 通知小米粒
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review通过 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/notify_xiaomi.txt
    
    echo ""
    echo "✅ Review通过！"
    echo "📄 详细Review：$REVIEW_FILE"
    echo "✅ 已通知小米粒"
else
    echo ""
    echo "❌ Review拒绝"
    
    # 更新Review文档
    sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/❌ 拒绝发布/g" "$REVIEW_FILE"
    
    # 创建拒绝文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/review_rejected.txt
    
    # 提交到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review拒绝

Review思路：
- 代码质量：$CODE_QUALITY/5星
- 问题：$CONS
- 建议：$SHORT_IMPROVEMENTS
- 详细Review：reviews/${SKILL_NAME}_${TIMESTAMP}.md

Reviewed-by: 米粒儿"
    
    # 推送
    git push origin feature/$SKILL_NAME 2>/dev/null || git push origin master
    
    # 通知小米粒
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/notify_xiaomi.txt
    
    echo ""
    echo "❌ Review未通过"
    echo "📄 详细Review：$REVIEW_FILE"
    echo "✅ 已通知小米粒"
fi

# ===== 步骤10：检查小米粒的补充建议（新增）⭐ =====
echo ""
echo "=== 步骤10：检查小米粒的补充建议 ==="
SUPPLEMENT_FILE="/tmp/review_supplement.md"
if [ -f "$SUPPLEMENT_FILE" ]; then
    echo "✅ 发现小米粒的补充建议："
    echo "================================"
    cat "$SUPPLEMENT_FILE"
    echo "================================"
    echo ""
    
    read -p "是否接受小米粒的补充建议？(y/n): " ACCEPT_SUPPLEMENT
    if [ "$ACCEPT_SUPPLEMENT" = "y" ]; then
        echo "✅ 已接受小米粒的补充建议"
        
        # 将补充建议附加到Review文档
        echo "" >> "$REVIEW_FILE"
        echo "---" >> "$REVIEW_FILE"
        echo "" >> "$REVIEW_FILE"
        echo "## 🔄 小米粒的补充建议" >> "$REVIEW_FILE"
        echo "" >> "$REVIEW_FILE"
        cat "$SUPPLEMENT_FILE" >> "$REVIEW_FILE"
        
        # 提交更新
        git add reviews/
        git commit -m "review: 接受小米粒的补充建议

补充建议来自：$SUPPLEMENT_FILE
已附加到：reviews/${SKILL_NAME}_${TIMESTAMP}.md"
        
        git push origin feature/$SKILL_NAME 2>/dev/null || git push origin master
        
        echo "✅ 补充建议已添加到Review文档"
    else
        echo "⚠️  暂不接受补充建议"
    fi
else
    echo "⏳ 暂无小米粒的补充建议"
    echo "💡 小米粒会在收到Review后思考是否需要补充"
fi

# 切回master
git checkout master 2>/dev/null

echo ""
echo "✅ 米粒儿优化版Review工作流程完成"
echo ""
echo "📊 双向思考策略已启用："
echo "✅ 已读取小米粒的自检清单"
echo "✅ 已回答小米粒的疑问"
echo "✅ 已检查小米粒的补充建议"

================================================================================
使用方法
================================================================================

1. 保存脚本到文件：
   bash /root/.openclaw/workspace/scripts/mili_review_optimized.sh

2. 添加执行权限：
   chmod +x /root/.openclaw/workspace/scripts/mili_review_optimized.sh

3. 执行脚本：
   bash /root/.openclaw/workspace/scripts/mili_review_optimized.sh

================================================================================
脚本特点
================================================================================

新增功能（3个步骤）：
1. ✅ 步骤2：读取小米粒的自检清单
2. ✅ 步骤7：考虑小米粒的疑问
3. ✅ 步骤10：检查小米粒的补充建议

双向思考策略：
- 米粒儿了解小米粒的关注点
- 米粒儿回答小米粒的疑问
- 米粒儿接受小米粒的补充建议

优势：
- ✅ 双向沟通机制
- ✅ 互相补充完善
- ✅ 协作效率提升
- ✅ 技术质量提升

================================================================================
