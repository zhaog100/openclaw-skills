#!/bin/bash
# 小米粒协作脚本 v3.0 - 统一整合版
# 角色：开发者 + 测试者
# 功能：并行分析、开发实现、开发前自检、Review后思考、Git管理、ClawHub发布

set -e

# ==================== 配置 ====================
WORKSPACE="/root/.openclaw/workspace"
PRODUCTS_DIR="$WORKSPACE/docs/products"
REVIEWS_DIR="$WORKSPACE/docs/reviews"
TEMPLATES_DIR="$WORKSPACE/.clawhub"
GIT_REPO="github.com/zhaog100/openclaw-skills"
NOTIFY_FILE="/tmp/notify_mili.txt"
APPROVED_FILE="/tmp/review_approved.txt"
REJECTED_FILE="/tmp/review_rejected.txt"
RELEASE_FILE="/tmp/release_approved.txt"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_blue() { echo -e "${PURPLE}[XIAOMI]${NC} $1"; }

# ==================== 工具函数 ====================

# 获取当前日期
get_date() {
    date +%Y-%m-%d
}

# 确保目录存在
ensure_dirs() {
    mkdir -p "$PRODUCTS_DIR"
    mkdir -p "$REVIEWS_DIR"
    mkdir -p "$TEMPLATES_DIR"
}

# 检查Git状态
check_git() {
    cd "$WORKSPACE"
    if [ -d ".git" ]; then
        log_info "Git仓库就绪"
        return 0
    else
        log_error "Git仓库未初始化"
        return 1
    fi
}

# 检查验收批准
check_approval() {
    if [ -f "$APPROVED_FILE" ]; then
        log_blue "收到米粒儿的验收批准："
        cat "$APPROVED_FILE"
        echo
        return 0
    else
        log_warn "没有验收批准，请先完成Review和5层验收"
        log_info "米粒儿运行：bash scripts/mili_product_v3.sh $1 accept"
        return 1
    fi
}

# ==================== 并行分析（技术角度）====================

analyze_tech() {
    local feature_name=$1
    local date=$(get_date)
    local prd_file="$PRODUCTS_DIR/${date}_${feature_name}_prd.md"
    
    if [ ! -f "$prd_file" ]; then
        log_error "PRD文档不存在，请先让米粒儿创建PRD"
        log_info "米粒儿运行：bash scripts/mili_product_v3.sh $feature_name prd"
        return 1
    fi
    
    log_blue "并行分析（技术角度）：$feature_name"
    
    # 追加分析到PRD
    cat >> "$prd_file" <<EOF

---

## 9. 小米粒分析（技术角度）

**分析时间**：$(date '+%Y-%m-%d %H:%M:%S')

### 9.1 技术可行性分析
- **实现难度**：[低/中/高]
- **技术栈**：[技术选择]
- **依赖库**：[依赖列表]

### 9.2 性能影响分析
- **响应时间**：[预估]
- **资源占用**：[预估]
- **并发能力**：[预估]

### 9.3 兼容性分析
- **系统兼容**：[兼容性]
- **版本兼容**：[兼容性]
- **向后兼容**：[兼容性]

### 9.4 技术风险
- **技术风险1**：[风险 + 应对]
- **技术风险2**：[风险 + 应对]

### 9.5 给米粒儿的建议
1. [建议1]
2. [建议2]
3. [建议3]

---

## 10. 综合方案

**方案时间**：$(date '+%Y-%m-%d %H:%M:%S')

### 10.1 最终方案
[综合米粒儿和小米粒的分析，形成最终方案]

### 10.2 实现计划
1. [步骤1]
2. [步骤2]
3. [步骤3]

### 10.3 验收标准
- [ ] [标准1]
- [ ] [标准2]
- [ ] [标准3]

---

*分析时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*状态：技术方案确定，可以开始开发*
EOF
    
    log_info "技术分析已添加到PRD：$prd_file"
    log_blue "下一步：开始开发实现"
    log_blue "运行：bash $0 $feature_name dev"
}

# ==================== 开发实现 ====================

dev() {
    local feature_name=$1
    local date=$(get_date)
    
    log_blue "开发实现：$feature_name"
    
    # 检查Git
    if ! check_git; then
        return 1
    fi
    
    # 创建feature分支
    cd "$WORKSPACE"
    local branch_name="feature/${date}_${feature_name}"
    
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        log_warn "分支已存在：$branch_name"
        log_info "切换到现有分支..."
        git checkout "$branch_name"
    else
        log_info "创建新分支：$branch_name"
        git checkout -b "$branch_name"
    fi
    
    log_blue "开始开发..."
    log_blue "开发完成后，运行："
    log_blue "bash $0 $feature_name check（开发前自检）"
}

# ==================== 开发前自检 ====================

check() {
    local feature_name=$1
    local date=$(get_date)
    local self_check_file="$REVIEWS_DIR/${date}_${feature_name}_self_check.md"
    
    ensure_dirs
    
    log_blue "开发前自检：$feature_name"
    
    cat > "$self_check_file" <<EOF
# 开发自检报告 - $feature_name

**自检日期**：$date  
**自检者**：小米粒  
**状态**：自检中

---

## 1. 代码质量自检

### 1.1 代码结构清晰
✅ / ⚠️ / ❌  
[自评...]

### 1.2 命名规范
✅ / ⚠️ / ❌  
[自评...]

### 1.3 注释完整
✅ / ⚠️ / ❌  
[自评...]

### 1.4 无明显bug
✅ / ⚠️ / ❌  
[自评...]

---

## 2. 功能实现自检

### 2.1 功能完整
✅ / ⚠️ / ❌  
[自评...]

### 2.2 测试通过
✅ / ⚠️ / ❌  
[自评...]

### 2.3 边界情况处理
✅ / ⚠️ / ❌  
[自评...]

### 2.4 错误处理
✅ / ⚠️ / ❌  
[自评...]

---

## 3. 文档完整性自检

### 3.1 SKILL.md完整
✅ / ⚠️ / ❌  
[自评...]

### 3.2 package.json准确
✅ / ⚠️ / ❌  
[自评...]

### 3.3 使用说明清晰
✅ / ⚠️ / ❌  
[自评...]

### 3.4 示例代码提供
✅ / ⚠️ / ❌  
[自评...]

---

## 4. 潜在风险评估

### 4.1 无安全风险
✅ / ⚠️ / ❌  
[自评...]

### 4.2 无性能问题
✅ / ⚠️ / ❌  
[自评...]

### 4.3 无兼容性问题
✅ / ⚠️ / ❌  
[自评...]

### 4.4 无依赖问题
✅ / ⚠️ / ❌  
[自评...]

---

## 5. 给米粒儿的提示

### 重点Review哪里
1. [提示1]
2. [提示2]

### 有什么疑问
1. [疑问1]
2. [疑问2]

### 需要什么建议
1. [建议需求1]
2. [建议需求2]

---

## 6. 自检总结

**自检结果**：✅ 通过 / ⚠️ 基本通过 / ❌ 需修改

**总体评价**：[评价]

**改进计划**：[计划]

---

*自检时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*状态：等待米粒儿Review*
EOF
    
    log_info "自检文档已创建：$self_check_file"
    
    # 通知米粒儿
    echo "feature=$feature_name" > "$NOTIFY_FILE"
    echo "date=$date" >> "$NOTIFY_FILE"
    echo "self_check_file=$self_check_file" >> "$NOTIFY_FILE"
    echo "time=$(date '+%Y-%m-%d %H:%M:%S')" >> "$NOTIFY_FILE"
    
    log_blue "已通知米粒儿Review请求"
    log_blue "米粒儿运行：bash scripts/mili_product_v3.sh $feature_name review"
}

# ==================== Review后思考 ====================

think() {
    local feature_name=$1
    local date=$(get_date)
    local review_file="$REVIEWS_DIR/${date}_${feature_name}_review.md"
    
    if [ ! -f "$review_file" ]; then
        log_error "Review文档不存在，请先等待米粒儿完成Review"
        log_info "米粒儿运行：bash scripts/mili_product_v3.sh $feature_name review"
        return 1
    fi
    
    log_blue "Review后思考：$feature_name"
    
    # 读取Review文档
    log_blue "读取米粒儿的Review..."
    cat "$review_file"
    echo
    
    # 追加思考到Review文档
    cat >> "$review_file" <<EOF

---

## 小米粒的Review后思考

**思考时间**：$(date '+%Y-%m-%d %H:%M:%S')

### 1. Review完整性评估

**米粒儿考虑全面吗？**  
[评估...]

**有遗漏的技术点吗？**  
[分析...]

**有更好的实现方式吗？**  
[思考...]

**需要补充什么信息吗？**  
[补充...]

### 2. 思路补充（如有遗漏）

**遗漏的点**：[点1]  
**为什么重要**：[原因]  
**补充建议**：[建议]

**遗漏的点**：[点2]  
**为什么重要**：[原因]  
**补充建议**：[建议]

### 3. 不同意见（如有）

**不同意哪个点**：[点]  
**理由**：[理由]  
**建议如何讨论**：[建议]

### 4. 学习收获

**从Review中学到的**：
1. [收获1]
2. [收获2]
3. [收获3]

### 5. 自我反思

**做得好的地方**：
- [优点1]
- [优点2]

**需要改进的地方**：
- [改进1]
- [改进2]

---

*思考时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*状态：双向思考完成*
EOF
    
    log_info "Review后思考已添加到Review文档"
    log_blue "下一步：等待米粒儿的5层验收"
    log_blue "米粒儿运行：bash scripts/mili_product_v3.sh $feature_name accept"
}

# ==================== Git提交 ====================

commit() {
    local feature_name=$1
    local date=$(get_date)
    
    if ! check_git; then
        return 1
    fi
    
    log_blue "Git提交：$feature_name"
    
    cd "$WORKSPACE"
    
    # 检查当前分支
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    log_info "当前分支：$current_branch"
    
    # 添加所有变更
    log_info "添加变更..."
    git add -A
    
    # 提交
    local commit_msg="feat($feature_name): 开发完成 - $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_msg"
    
    log_info "已提交：$commit_msg"
    log_blue "下一步：等待米粒儿的5层验收后发布"
}

# ==================== 发布 ====================

publish() {
    local feature_name=$1
    local date=$(get_date)
    local skill_dir="$WORKSPACE/skills/$feature_name"
    
    # 检查验收批准
    if ! check_approval "$feature_name"; then
        return 1
    fi
    
    log_blue "发布到ClawHub：$feature_name"
    
    # 检查技能目录
    if [ ! -d "$skill_dir" ]; then
        log_error "技能目录不存在：$skill_dir"
        return 1
    fi
    
    # 检查必要文件
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        log_error "SKILL.md不存在"
        return 1
    fi
    
    if [ ! -f "$skill_dir/package.json" ]; then
        log_error "package.json不存在"
        return 1
    fi
    
    # 读取版本号
    local version=$(grep '"version"' "$skill_dir/package.json" | cut -d'"' -f4)
    log_info "当前版本：$version"
    
    # 提示确认
    log_warn "即将发布 $feature_name v$version 到ClawHub"
    read -p "确认发布？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warn "取消发布"
        return 1
    fi
    
    # 合并到master
    log_info "合并到master分支..."
    cd "$WORKSPACE"
    git checkout master
    git merge "feature/${date}_${feature_name}" --no-ff -m "Merge feature/$feature_name"
    
    # 发布到ClawHub
    log_info "发布到ClawHub..."
    cd "$skill_dir"
    local package_id=$(clawhub publish "$skill_dir" --slug "$feature_name" --version "$version" 2>&1 | grep -oP 'Package ID: \K[a-z0-9]+' || echo "")
    
    if [ -z "$package_id" ]; then
        log_error "ClawHub发布失败"
        return 1
    fi
    
    log_info "ClawHub发布成功！Package ID: $package_id"
    
    # 更新文档
    local review_file="$REVIEWS_DIR/${date}_${feature_name}_review.md"
    if [ -f "$review_file" ]; then
        cat >> "$review_file" <<EOF

---

## 发布记录

**发布时间**：$(date '+%Y-%m-%d %H:%M:%S')  
**发布版本**：v$version  
**ClawHub Package ID**：$package_id  
**ClawHub 链接**：https://clawhub.com/skills/$feature_name  
**GitHub Release**：待创建

---

*发布时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*状态：发布成功*
EOF
    fi
    
    # Git推送
    log_info "推送到GitHub..."
    cd "$WORKSPACE"
    git push origin master
    git push origin "feature/${date}_${feature_name}"
    
    # 创建GitHub Release
    log_info "创建GitHub Release..."
    gh release create "v$version-$feature_name" \
        --title "Release v$version - $feature_name" \
        --notes "详见Review文档：$review_file" \
        2>/dev/null || log_warn "GitHub Release创建失败（可能已存在）"
    
    # 清理通知文件
    rm -f "$NOTIFY_FILE" "$APPROVED_FILE" "$REJECTED_FILE" "$RELEASE_FILE"
    
    log_info "发布完成！"
    log_blue "Package ID: $package_id"
    log_blue "ClawHub: https://clawhub.com/skills/$feature_name"
}

# ==================== 主函数 ====================

usage() {
    echo "小米粒协作脚本 v3.0"
    echo ""
    echo "用法：bash $0 <功能名> <操作>"
    echo ""
    echo "操作："
    echo "  analyze   - 并行分析（技术角度）"
    echo "  dev       - 开发实现"
    echo "  check     - 开发前自检"
    echo "  think     - Review后思考"
    echo "  commit    - Git提交"
    echo "  publish   - 发布到ClawHub"
    echo ""
    echo "示例："
    echo "  bash $0 example-skill analyze"
    echo "  bash $0 example-skill dev"
    echo "  bash $0 example-skill check"
    echo "  bash $0 example-skill think"
    echo "  bash $0 example-skill commit"
    echo "  bash $0 example-skill publish"
}

main() {
    if [ $# -lt 2 ]; then
        usage
        exit 1
    fi
    
    local feature_name=$1
    local action=$2
    
    log_blue "================================"
    log_blue "小米粒协作脚本 v3.0"
    log_blue "功能：$feature_name"
    log_blue "操作：$action"
    log_blue "================================"
    
    case "$action" in
        analyze)
            analyze_tech "$feature_name"
            ;;
        dev)
            dev "$feature_name"
            ;;
        check)
            check "$feature_name"
            ;;
        think)
            think "$feature_name"
            ;;
        commit)
            commit "$feature_name"
            ;;
        publish)
            publish "$feature_name"
            ;;
        *)
            log_error "未知操作：$action"
            usage
            exit 1
            ;;
    esac
}

main "$@"
