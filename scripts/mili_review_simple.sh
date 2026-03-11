#!/bin/bash
# 米粒儿Review脚本 - 简化版
# 基于模板创建详细Review文档

echo "🌾 === 米粒儿Review工作流程 ==="
echo "我是米粒儿，现在开始Review小米粒的技能！"

# 步骤1：检查Review请求
if [ -f /tmp/notify_mili.txt ]; then
    echo "✅ 发现小米粒的Review请求："
    cat /tmp/notify_mili.txt
    SKILL_NAME=$(cat /tmp/notify_mili.txt | awk '{print $4}')
    echo ""
    echo "待Review技能：$SKILL_NAME"
else
    echo "❌ 没有小米粒的Review请求"
    echo "手动检查Git分支："
    git branch -r | grep feature/
    read -p "请输入要Review的技能名称: " SKILL_NAME
fi

# 步骤2：切换分支
cd /root/.openclaw/workspace
git fetch origin
git checkout feature/$SKILL_NAME 2>/dev/null || git checkout master
echo "✅ 已准备Review环境"

# 步骤3：创建Review文档
REVIEW_DIR="/root/.openclaw/workspace/reviews"
mkdir -p "$REVIEW_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REVIEW_FILE="$REVIEW_DIR/${SKILL_NAME}_${TIMESTAMP}.md"

echo ""
echo "📝 开始创建Review文档..."
echo "Review文件：$REVIEW_FILE"
echo ""

# 复制模板
cp /root/.openclaw/workspace/.clawhub/review_template.md "$REVIEW_FILE"

# 自动填充基本信息
sed -i "s/\[技能名称\]/$SKILL_NAME/g" "$REVIEW_FILE"
sed -i "s/\[YYYY-MM-DD HH:MM:SS\]/$(date '+%Y-%m-%d %H:%M:%S')/g" "$REVIEW_FILE"

echo "✅ Review文档模板已创建"
echo ""
echo "📄 请编辑Review文档："
echo "   $REVIEW_FILE"
echo ""
echo "💡 提示："
echo "1. 填写Review思路"
echo "2. 记录技术要点"
echo "3. 提供改进建议"
echo "4. 给小米粒学习建议"
echo ""

# 询问是否现在编辑
read -p "现在编辑Review文档？(y/n): " EDIT_NOW
if [ "$EDIT_NOW" = "y" ]; then
    ${EDITOR:-nano} "$REVIEW_FILE"
fi

# 步骤4：读取Review结果
echo ""
echo "📊 Review结果："
read -p "批准发布？(y/n): " APPROVE

if [ "$APPROVE" = "y" ]; then
    # 更新Review文档
    sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/✅ 批准发布/g" "$REVIEW_FILE"
    
    # 创建批准文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review通过 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/review_approved.txt
    
    # 提交到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review通过

Review思路：见 reviews/${SKILL_NAME}_${TIMESTAMP}.md

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
    # 更新Review文档
    sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/❌ 拒绝发布/g" "$REVIEW_FILE"
    
    # 创建拒绝文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/review_rejected.txt
    
    # 提交到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review拒绝

Review思路：见 reviews/${SKILL_NAME}_${TIMESTAMP}.md

Reviewed-by: 米粒儿"
    
    # 推送
    git push origin feature/$SKILL_NAME 2>/dev/null || git push origin master
    
    # 通知小米粒
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 详细Review：$REVIEW_FILE" > /tmp/notify_xiaomi.txt
    
    echo ""
    echo "❌ Review拒绝"
    echo "📄 详细Review：$REVIEW_FILE"
    echo "✅ 已通知小米粒"
fi

# 切回master
git checkout master 2>/dev/null

echo ""
echo "✅ 米粒儿Review工作流程完成"
