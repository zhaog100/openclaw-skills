#!/bin/bash
# 米粒儿增强版Review脚本
# 整合方案B（独立文档）+ 方案D（自动化流程）

set -e

echo "🌾 === 米粒儿增强版Review工作流程 ==="
echo "我是米粒儿，现在开始详细Review小米粒的技能！"
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

# ===== 步骤2：准备Review环境 =====
echo ""
echo "=== 步骤2：准备Review环境 ==="
cd /root/.openclaw/workspace
git fetch origin
git checkout feature/$SKILL_NAME 2>/dev/null || {
    echo "❌ 分支不存在，切换到master"
    git checkout master
}
echo "✅ Review环境准备完成"

# ===== 步骤3：代码分析 =====
echo ""
echo "=== 步骤3：代码分析 ==="
echo "📊 文件变更统计："
git diff --stat master...feature/$SKILL_NAME 2>/dev/null || echo "无差异或已在master"

echo ""
echo "📄 代码差异："
git diff master...feature/$SKILL_NAME 2>/dev/null | head -50

# ===== 步骤4：创建Review文档 =====
echo ""
echo "=== 步骤4：创建Review文档 ==="
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

# ===== 步骤5：交互式Review =====
echo ""
echo "=== 步骤5：交互式Review ==="
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

# ===== 步骤6：更新Review文档 =====
echo ""
echo "=== 步骤6：更新Review文档 ==="

# 替换占位符
sed -i "s/\[观察点1\]/$PROS/g" "$REVIEW_FILE"
sed -i "s/\[优点1\]/$GOOD_POINTS/g" "$REVIEW_FILE"
sed -i "s/\[需要改进\]/$CONS/g" "$REVIEW_FILE"
sed -i "s/\[技术点1\]/$KEY_POINTS/g" "$REVIEW_FILE"
sed -i "s/\[风险1\]/$RISKS/g" "$REVIEW_FILE"
sed -i "s/\[建议1\]/$SHORT_IMPROVEMENTS/g" "$REVIEW_FILE"
sed -i "s/X\/5星/${CODE_QUALITY}\/5星/g" "$REVIEW_FILE"

echo "✅ Review文档已更新"

# ===== 步骤7：做出决定 =====
echo ""
echo "=== 步骤7：Review决定 ==="

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

# 切回master
git checkout master 2>/dev/null

echo ""
echo "✅ 米粒儿Review工作流程完成"
