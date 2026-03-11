#!/bin/bash
# 米粒儿工作流程增强版 - ClawHub协作（智能体B）
# 米粒儿负责Review小米粒的技能，并记录详细思路

echo "🌾 === 米粒儿工作流程增强版（智能体B）==="
echo "我是米粒儿，和小姐姐一起管理ClawHub！"

# 步骤1：检查Review请求
if [ -f /tmp/notify_mili.txt ]; then
    echo "✅ 发现小米粒的Review请求："
    cat /tmp/notify_mili.txt
    SKILL_NAME=$(cat /tmp/notify_mili.txt | awk '{print $4}')
else
    echo "❌ 没有小米粒的Review请求"
    git branch -r | grep feature/
    read -p "请输入要Review的技能名称: " SKILL_NAME
fi

# 步骤2：切换分支
cd /root/.openclaw/workspace
git fetch origin
git checkout feature/$SKILL_NAME
echo "✅ 米粒儿已切换到分支：feature/$SKILL_NAME"

# 步骤3：Review代码
echo ""
echo "=== 米粒儿开始Review ==="
echo "Review时间：$(date '+%Y-%m-%d %H:%M:%S')"
git diff master...feature/$SKILL_NAME > /tmp/code_diff.txt

echo ""
echo "📊 代码分析："
echo "1. 文件变更统计："
git diff --stat master...feature/$SKILL_NAME

echo ""
read -p "代码检查通过？(y/n): " CODE_OK
read -p "代码质量评价（1-5星）: " CODE_QUALITY
read -p "主要优点（用逗号分隔）: " PROS
read -p "需要改进（用逗号分隔）: " CONS

# 步骤4：测试功能
echo ""
echo "=== 功能测试 ==="
if [ -f /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh ]; then
    bash /root/.openclaw/workspace/skills/$SKILL_NAME/test.sh
    read -p "功能测试通过？(y/n): " TEST_OK
else
    echo "⚠️  未找到测试脚本"
    read -p "手动测试通过？(y/n): " TEST_OK
fi

# 步骤5：创建详细Review文档
REVIEW_FILE="/root/.openclaw/workspace/reviews/${SKILL_NAME}_$(date +%Y%m%d_%H%M%S).md"
mkdir -p /root/.openclaw/workspace/reviews

cat > "$REVIEW_FILE" << REVIEW_EOF
# 米粒儿Review详情 - $SKILL_NAME

**Review时间**：$(date '+%Y-%m-%d %H:%M:%S')  
**技能名称**：$SKILL_NAME  
**Review者**：米粒儿  

---

## 📊 Review结果

**最终决定**：$([ "$CODE_OK" = "y" ] && [ "$TEST_OK" = "y" ] && echo "✅ 批准发布" || echo "❌ 拒绝发布")

---

## 🧠 Review思路

### 1. 代码质量评估
**评分**：⭐⭐⭐⭐⭐ ($CODE_QUALITY/5星)

**优点**：
$PROS

**待改进**：
$CONS

**技术决策**：
- 批准/拒绝原因：[详细说明]
- 关键技术点：[列出]
- 风险点：[列出]

---

### 2. 功能实现评估
**测试结果**：$([ "$TEST_OK" = "y" ] && echo "✅ 通过" || echo "❌ 失败")

**评估**：
- 功能是否符合预期
- 测试覆盖是否充分
- 性能是否达标

---

## 💡 技术要点

### 关键技术点
1. [技术点1]
2. [技术点2]
3. [技术点3]

### 风险点
1. ⚠️ [风险1]
2. ⚠️ [风险2]
3. ⚠️ [风险3]

---

## 📝 改进建议

### 短期改进（下个版本）
1. [建议1]
2. [建议2]
3. [建议3]

### 长期改进（未来）
1. [建议1]
2. [建议2]
3. [建议3]

---

## 🎓 学习要点

### 小米粒做得好的地方
1. ✅ [优点1]
2. ✅ [优点2]
3. ✅ [优点3]

### 需要改进的地方
1. ⚠️ [改进1]
2. ⚠️ [改进2]
3. ⚠️ [改进3]

---

## 🤝 给小米粒的建议

### 技术建议
1. [建议1]
2. [建议2]
3. [建议3]

### 协作建议
1. [建议1]
2. [建议2]
3. [建议3]

---

## 📊 Review总结

**总体评价**：⭐⭐⭐⭐⭐ ($CODE_QUALITY/5星)

**优点**：
$PROS

**待改进**：
$CONS

**批准原因**：
- [原因1]
- [原因2]
- [原因3]

---

*Review完成时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*Review文档：$REVIEW_FILE*
REVIEW_EOF

echo ""
echo "✅ Review文档已创建：$REVIEW_FILE"

# 步骤6：做出决定
if [ "$CODE_OK" = "y" ] && [ "$TEST_OK" = "y" ]; then
    echo ""
    echo "=== 米粒儿Review通过 ==="
    
    # 创建批准文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review通过 | $SKILL_NAME | 小米粒可以发布" > /tmp/review_approved.txt
    
    # 提交Review文档到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review通过

Review思路：
- 代码质量：$CODE_QUALITY/5星
- 优点：$PROS
- 改进：$CONS

详细Review：reviews/${SKILL_NAME}_*.md

Reviewed-by: 米粒儿"
    git push origin feature/$SKILL_NAME
    
    # 通知小米粒
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review通过 | $SKILL_NAME | 详细Review见：$REVIEW_FILE" > /tmp/notify_xiaomi.txt
    
    echo "✅ Review通过！已通知小米粒"
    echo "📄 详细Review：$REVIEW_FILE"
else
    echo ""
    echo "=== 米粒儿Review拒绝 ==="
    
    # 创建拒绝文件
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 需要修改" > /tmp/review_rejected.txt
    
    # 提交Review文档到Git
    git add reviews/
    git commit -m "review: $SKILL_NAME Review拒绝

Review思路：
- 代码质量：$CODE_QUALITY/5星
- 问题：$CONS
- 建议：查看详细Review文档

详细Review：reviews/${SKILL_NAME}_*.md

Reviewed-by: 米粒儿"
    git push origin feature/$SKILL_NAME
    
    # 通知小米粒
    echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review拒绝 | $SKILL_NAME | 详细Review见：$REVIEW_FILE" > /tmp/notify_xiaomi.txt
    
    echo "❌ Review未通过，已通知小米粒"
    echo "📄 详细Review：$REVIEW_FILE"
fi

git checkout master
echo ""
echo "✅ 米粒儿工作流程完成"
