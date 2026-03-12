#!/bin/bash
# 米粒儿 Review 脚本自动化增强版
# 在原有基础上增加自动化检查、模板生成、批量处理功能

set -e

echo "🌾 === 米粒儿 Review 脚本自动化增强版 ==="
echo "双向思考策略 + 自动化检查 + 批量处理"
echo ""

# ===== 配置区 =====
REVIEWS_DIR="/home/zhaog/.openclaw/workspace/reviews"
TEMPLATES_DIR="/home/zhaog/.openclaw/workspace/scripts/templates"
SELF_CHECK_FILE="/tmp/self_review_checklist.md"
SUPPLEMENT_FILE="/tmp/review_supplement.md"

# ===== 函数定义 =====

# 自动检查函数
auto_check() {
    local skill_name=$1
    local skill_path="/home/zhaog/.openclaw/workspace/skills/$skill_name"
    
    echo "=== 自动化检查：$skill_name ==="
    
    # 1. 检查 SKILL.md
    if [ -f "$skill_path/SKILL.md" ]; then
        echo "✅ SKILL.md 存在"
    else
        echo "❌ SKILL.md 缺失"
        return 1
    fi
    
    # 2. 检查 package.json
    if [ -f "$skill_path/package.json" ]; then
        echo "✅ package.json 存在"
        # 检查必要字段
        if grep -q '"name"' "$skill_path/package.json"; then
            echo "  ✅ name 字段存在"
        else
            echo "  ❌ name 字段缺失"
        fi
        if grep -q '"version"' "$skill_path/package.json"; then
            echo "  ✅ version 字段存在"
        else
            echo "  ❌ version 字段缺失"
        fi
    else
        echo "❌ package.json 缺失"
    fi
    
    # 3. 检查 README.md
    if [ -f "$skill_path/README.md" ]; then
        echo "✅ README.md 存在"
    else
        echo "⚠️  README.md 缺失（建议添加）"
    fi
    
    # 4. 检查测试脚本
    if [ -f "$skill_path/test.sh" ]; then
        echo "✅ test.sh 存在"
    else
        echo "⚠️  test.sh 缺失（建议添加）"
    fi
    
    # 5. 检查 .gitignore
    if [ -f "$skill_path/.gitignore" ]; then
        echo "✅ .gitignore 存在"
    else
        echo "⚠️  .gitignore 缺失（建议添加）"
    fi
    
    # 6. 检查代码规范
    echo ""
    echo "代码规范检查："
    if [ -d "$skill_path/scripts" ]; then
        local script_count=$(find "$skill_path/scripts" -name "*.sh" | wc -l)
        echo "  📄 Shell 脚本数：$script_count"
    fi
    if [ -d "$skill_path/core" ]; then
        local py_count=$(find "$skill_path/core" -name "*.py" | wc -l)
        echo "  🐍 Python 文件数：$py_count"
    fi
    
    # 7. 检查敏感信息
    echo ""
    echo "敏感信息检查："
    if grep -r "API_KEY\|api_key\|secret\|token" "$skill_path" --include="*.js" --include="*.py" --include="*.sh" | grep -v ".env.example" | head -5; then
        echo "  ⚠️  发现可能的敏感信息，请确认已添加到 .gitignore"
    else
        echo "  ✅ 未发现明显敏感信息"
    fi
    
    echo ""
}

# 生成 Review 模板
generate_template() {
    local skill_name=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local review_file="$REVIEWS_DIR/${skill_name}_${timestamp}.md"
    
    mkdir -p "$REVIEWS_DIR"
    
    cat > "$review_file" << EOF
# Review 报告：$skill_name

**Review 时间：** $(date '+%Y-%m-%d %H:%M:%S')  
**Reviewer：** 米粒儿  
**技能版本：** 待填写  
**Review 类型：** 发布前 Review / 功能增强 Review / Bug 修复 Review

---

## 📊 自动化检查结果

待填写...

---

## 🎯 代码质量评估

- **代码质量：** X/5 星
- **代码规范：** X/5 星
- **测试覆盖：** X/5 星
- **文档完整：** X/5 星
- **性能表现：** X/5 星

---

## ✅ 主要优点

- 待填写

---

## ⚠️ 需要改进

- 待填写

---

## 🔑 关键技术点

- 待填写

---

## 🚨 风险点

- 待填写

---

## 💡 改进建议

### 短期（1 周内）
- 待填写

### 长期（1 个月内）
- 待填写

---

## 🌟 小米粒做得好的地方

- 待填写

---

## 📈 需要改进的地方

- 待填写

---

## 💬 技术建议

- 待填写

---

## 🤝 协作建议

- 待填写

---

## 💭 回答小米粒的疑问

待填写...

---

## 🔄 小米粒的补充建议

待填写...

---

## ✅ Review 决定

**结果：** ✅ 批准发布 / ❌ 拒绝发布

**理由：** 待填写

---

**Reviewed-by:** 米粒儿  
**日期：** $(date '+%Y-%m-%d')
EOF
    
    echo "✅ Review 模板已生成：$review_file"
    echo "$review_file"
}

# 批量 Review 函数
batch_review() {
    echo "=== 批量 Review 模式 ==="
    echo ""
    
    # 查找所有待 Review 的技能
    local skills_dir="/home/zhaog/.openclaw/workspace/skills"
    local count=0
    
    for skill_path in "$skills_dir"/*/; do
        if [ -d "$skill_path" ]; then
            local skill_name=$(basename "$skill_path")
            echo ""
            echo "📦 检查技能：$skill_name"
            echo "================================"
            
            # 自动检查
            auto_check "$skill_name"
            
            count=$((count + 1))
        fi
    done
    
    echo ""
    echo "✅ 批量检查完成，共检查 $count 个技能"
}

# ===== 主流程 =====

echo "请选择 Review 模式："
echo "1. 单个技能 Review"
echo "2. 批量技能检查"
echo "3. 生成 Review 模板"
echo ""
read -p "请输入选项 (1-3): " MODE

case $MODE in
    1)
        read -p "请输入技能名称: " SKILL_NAME
        
        # 自动检查
        auto_check "$SKILL_NAME"
        
        # 生成 Review 模板
        REVIEW_FILE=$(generate_template "$SKILL_NAME")
        
        # 读取小米粒的自检清单
        echo ""
        echo "=== 读取小米粒的自检清单 ==="
        if [ -f "$SELF_CHECK_FILE" ]; then
            echo "✅ 发现自检清单："
            cat "$SELF_CHECK_FILE"
            echo ""
        else
            echo "⚠️  未找到自检清单"
        fi
        
        # 交互式 Review
        echo ""
        echo "=== 交互式 Review ==="
        read -p "代码质量评分 (1-5): " RATING
        read -p "Review 决定 (y=通过/n=拒绝): " DECISION
        
        # 更新 Review 文件
        sed -i "s/待填写.../$RATING\/5 星/" "$REVIEW_FILE"
        if [ "$DECISION" = "y" ]; then
            sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/✅ 批准发布/" "$REVIEW_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review 通过 | $SKILL_NAME" > /tmp/review_approved.txt
        else
            sed -i "s/✅ 批准发布 \/ ❌ 拒绝发布/❌ 拒绝发布/" "$REVIEW_FILE"
            echo "$(date '+%Y-%m-%d %H:%M:%S') | 米粒儿 | Review 拒绝 | $SKILL_NAME" > /tmp/review_rejected.txt
        fi
        
        echo ""
        echo "✅ Review 完成！"
        echo "📄 Review 文档：$REVIEW_FILE"
        ;;
    
    2)
        batch_review
        ;;
    
    3)
        read -p "请输入技能名称: " SKILL_NAME
        generate_template "$SKILL_NAME"
        ;;
    
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "🌾 Review 工作流程完成！"
