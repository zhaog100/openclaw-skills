#!/bin/bash
# 米粒儿协作脚本 v3.1 - 社区启发增强版
# 角色：产品经理 + 质量官
# 功能：产品构思、需求文档、并行分析、12维度Review（含反对意见）、5层验收、系统状态检查

set -e

# ==================== 配置 ====================
WORKSPACE="/root/.openclaw/workspace"
PRODUCTS_DIR="$WORKSPACE/docs/products"
REVIEWS_DIR="$WORKSPACE/docs/reviews"
TEMPLATES_DIR="$WORKSPACE/.clawhub"
COMM_DIR="$WORKSPACE/.mili_comm"
GIT_REPO="github.com/zhaog100/openclaw-skills"
NOTIFY_FILE="/tmp/notify_mili.txt"
APPROVED_FILE="/tmp/review_approved.txt"
REJECTED_FILE="/tmp/review_rejected.txt"
RELEASE_FILE="/tmp/release_approved.txt"
SYSTEM_STATUS_FILE="/tmp/system_status.txt"
ISSUES_FILE="$COMM_DIR/issues.txt"
STATUS_FILE="$COMM_DIR/status.json"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_blue() { echo -e "${BLUE}[MILI]${NC} $1"; }

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
    mkdir -p "$COMM_DIR"
    mkdir -p "$COMM_DIR/inbox"
    mkdir -p "$COMM_DIR/outbox"
    mkdir -p "$COMM_DIR/archive"
    
    if [ ! -f "$ISSUES_FILE" ]; then
        echo "# 双米粒Issue记录" > "$ISSUES_FILE"
        echo "# 格式：issue_[功能名]=[issue-number]" >> "$ISSUES_FILE"
        echo "# 创建时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$ISSUES_FILE"
    fi
    
    if [ ! -f "$STATUS_FILE" ]; then
        echo '{}' > "$STATUS_FILE"
    fi
}

# ==================== Git通信函数 ====================

# 创建GitHub Issue
create_github_issue() {
    local feature=$1
    local stage=$2
    local body_file=$3
    
    if [ ! -f "$body_file" ]; then
        log_error "文件不存在：$body_file"
        return 1
    fi
    
    log_blue "创建GitHub Issue：[$feature] $stage"
    
    cd "$WORKSPACE"
    
    if ! command -v gh &> /dev/null; then
        log_warn "GitHub CLI未安装，跳过Issue创建"
        return 0
    fi
    
    local issue_url=$(gh issue create \
        --title "[$feature] $stage - $(date '+%Y-%m-%d %H:%M')" \
        --body-file "$body_file" \
        --label "米粒儿,$stage" \
        2>&1)
    
    if [[ "$issue_url" == https://* ]]; then
        local issue_number=$(echo "$issue_url" | grep -oP 'issues/\K[0-9]+')
        log_info "Issue创建成功：#$issue_number"
        log_info "URL：$issue_url"
        
        # 记录Issue编号
        echo "issue_$feature=$issue_number" >> "$ISSUES_FILE"
        
        return 0
    else
        log_warn "Issue创建失败，但不影响流程"
        return 0
    fi
}

# 评论GitHub Issue
comment_github_issue() {
    local feature=$1
    local message=$2
    
    if ! command -v gh &> /dev/null; then
        log_warn "GitHub CLI未安装，跳过Issue评论"
        return 0
    fi
    
    local issue_number=$(grep "issue_$feature=" "$ISSUES_FILE" 2>/dev/null | tail -1 | cut -d'=' -f2)
    
    if [ -n "$issue_number" ]; then
        log_blue "评论Issue：#$issue_number"
        cd "$WORKSPACE"
        gh issue comment "$issue_number" --body "$message" 2>/dev/null || log_warn "Issue评论失败"
    else
        log_warn "未找到Issue编号"
    fi
}

# Git同步
git_sync() {
    local action=$1
    local message=${2:-"update"}
    
    cd "$WORKSPACE"
    
    case "$action" in
        pull)
            log_blue "Git拉取最新代码..."
            git pull origin master 2>/dev/null || log_warn "Git拉取失败"
            ;;
        push)
            log_blue "Git推送代码..."
            git add -A
            git commit -m "$message" 2>/dev/null || log_warn "没有变更需要提交"
            git push origin master 2>/dev/null || log_warn "Git推送失败"
            ;;
    esac
}

# 更新状态
update_status() {
    local feature=$1
    local stage=$2
    
    if command -v python3 &> /dev/null; then
        python3 <<EOF
import json
import os

status_file = '$STATUS_FILE'
if os.path.exists(status_file):
    with open(status_file, 'r') as f:
        status = json.load(f)
else:
    status = {}

status['$feature'] = {
    'status': '$stage',
    'last_update': '$(date '+%Y-%m-%d %H:%M:%S')',
    'updater': '米粒儿'
}

with open(status_file, 'w') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)
EOF
    fi
}

# 检查Git状态
check_git_status() {
    log_blue "检查Git状态..."
    cd "$WORKSPACE"
    
    # 检查是否有未提交的变更
    if ! git diff-index --quiet HEAD --; then
        log_warn "发现未提交的变更"
        git status --short
        return 1
    fi
    
    # 检查是否有未推送的提交
    local ahead=$(git rev-list --count origin/master..HEAD 2>/dev/null || echo "0")
    if [ "$ahead" != "0" ]; then
        log_warn "有 $ahead 个未推送的提交"
        return 1
    fi
    
    log_info "Git状态正常"
    return 0
}

# 检查网络连接
check_network() {
    log_blue "检查网络连接..."
    
    if ping -c 1 github.com &> /dev/null; then
        log_info "网络连接正常"
        return 0
    else
        log_warn "网络连接异常"
        return 1
    fi
}

# 检查系统状态
check_system() {
    log_blue "================================"
    log_blue "系统状态检查"
    log_blue "================================"
    
    local git_ok=true
    local network_ok=true
    local all_ok=true
    
    # 检查Git
    if ! check_git_status; then
        git_ok=false
        all_ok=false
    fi
    
    # 检查网络
    if ! check_network; then
        network_ok=false
        all_ok=false
    fi
    
    # 保存系统状态
    cat > "$SYSTEM_STATUS_FILE" <<EOF
git_ok=$git_ok
network_ok=$network_ok
check_time=$(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    if $all_ok; then
        log_info "系统状态检查通过"
        return 0
    else
        log_warn "系统状态检查发现问题，但不影响协作"
        return 0
    fi
}

# 检查通知文件
check_notify() {
    if [ -f "$NOTIFY_FILE" ]; then
        log_blue "收到小米粒的Review请求："
        cat "$NOTIFY_FILE"
        echo
        return 0
    else
        log_warn "没有待处理的Review请求"
        return 1
    fi
}

# ==================== 产品构思 ====================

create_concept() {
    local feature_name=$1
    local date=$(get_date)
    local concept_file="$PRODUCTS_DIR/${date}_${feature_name}_concept.md"
    
    ensure_dirs
    
    log_blue "创建产品构思：$feature_name"
    
    cat > "$concept_file" <<EOF
# 产品构思 - $feature_name

**创建日期**：$date  
**创建者**：米粒儿  
**状态**：构思阶段

---

## 🎯 核心价值

**用户痛点**：[用户遇到的问题]

**解决方案**：[如何解决这个问题]

**预期价值**：[带来的价值]

---

## 💡 功能设计

### 核心功能
1. [功能1]
2. [功能2]
3. [功能3]

### 扩展功能
- [扩展功能1]
- [扩展功能2]

---

## 🎭 用户场景

**场景1**：[描述场景]
- 触发条件：[条件]
- 用户操作：[操作]
- 预期结果：[结果]

**场景2**：[描述场景]
- 触发条件：[条件]
- 用户操作：[操作]
- 预期结果：[结果]

---

## 📊 成功指标

| 指标 | 目标 | 度量方法 |
|------|------|---------|
| 使用率 | [目标] | [方法] |
| 满意度 | [目标] | [方法] |
| 性能 | [目标] | [方法] |

---

## ⚠️ 风险评估

**技术风险**：[风险评估]

**用户体验风险**：[风险评估]

**兼容性风险**：[风险评估]

---

## 📅 时间计划

- [ ] 需求细化（1天）
- [ ] 技术评审（1天）
- [ ] 开发实现（2-3天）
- [ ] 测试验收（1天）
- [ ] 发布上线（1天）

---

*创建时间：$date*  
*下一步：编写PRD文档*
EOF
    
    log_info "产品构思已创建：$concept_file"
    
    # 创建GitHub Issue（Git通信）
    create_github_issue "$feature_name" "concept" "$concept_file"
    
    # 更新状态
    update_status "$feature_name" "concept"
    
    # Git同步
    git_sync push "feat($feature_name): 产品构思"
    
    log_blue "下一步：bash $0 $feature_name prd"
}

# ==================== 需求文档 ====================

create_prd() {
    local feature_name=$1
    local date=$(get_date)
    local prd_file="$PRODUCTS_DIR/${date}_${feature_name}_prd.md"
    
    ensure_dirs
    
    log_blue "编写需求文档：$feature_name"
    
    cat > "$prd_file" <<EOF
# 产品需求文档（PRD）- $feature_name

**文档版本**：v1.0  
**创建日期**：$date  
**创建者**：米粒儿  
**状态**：需求阶段

---

## 1. 需求概述

### 1.1 背景
[项目背景]

### 1.2 目标
[项目目标]

### 1.3 范围
**包含**：
- [功能1]
- [功能2]

**不包含**：
- [功能3]
- [功能4]

---

## 2. 功能需求

### 2.1 核心功能

**功能1：[功能名称]**
- 描述：[功能描述]
- 输入：[输入]
- 输出：[输出]
- 验收标准：[标准]

**功能2：[功能名称]**
- 描述：[功能描述]
- 输入：[输入]
- 输出：[输出]
- 验收标准：[标准]

### 2.2 扩展功能
[扩展功能描述]

---

## 3. 技术需求

### 3.1 性能要求
- 响应时间：< [X]秒
- 并发用户：[X]个
- 可用性：>[X]%

### 3.2 安全要求
[安全要求]

### 3.3 兼容性要求
[兼容性要求]

---

## 4. 验收标准

### 4.1 功能验收
- [ ] 所有功能按需求实现
- [ ] 测试覆盖率 > [X]%
- [ ] 所有测试通过

### 4.2 性能验收
- [ ] 响应时间符合要求
- [ ] 并发处理正常

### 4.3 文档验收
- [ ] SKILL.md完整
- [ ] README.md清晰
- [ ] 示例代码提供

---

## 5. 发布标准

### 5.1 ClawHub发布
- [ ] package.json准确
- [ ] SKILL.md完整
- [ ] 版本号规范

### 5.2 Git管理
- [ ] feature分支创建
- [ ] 提交信息规范
- [ ] 合并到master

---

## 6. 风险与依赖

### 6.1 风险
| 风险 | 影响 | 应对措施 |
|------|------|---------|
| [风险1] | [影响] | [措施] |
| [风险2] | [影响] | [措施] |

### 6.2 依赖
| 依赖 | 提供者 | 状态 |
|------|--------|------|
| [依赖1] | [提供者] | [状态] |
| [依赖2] | [提供者] | [状态] |

---

## 7. 时间计划

| 阶段 | 开始 | 结束 | 负责人 |
|------|------|------|--------|
| 需求评审 | $date | +1天 | 米粒儿 |
| 技术设计 | +2天 | +3天 | 小米粒 |
| 开发实现 | +4天 | +6天 | 小米粒 |
| 测试验收 | +7天 | +8天 | 米粒儿 |
| 发布上线 | +9天 | +9天 | 小米粒 |

---

*创建时间：$date*  
*下一步：GitHub Issues讨论*
EOF
    
    log_info "需求文档已创建：$prd_file"
    
    # 创建GitHub Issue（如果concept阶段未创建）
    if [ ! -f "$ISSUES_FILE" ] || ! grep -q "issue_$feature_name=" "$ISSUES_FILE"; then
        create_github_issue "$feature_name" "prd" "$prd_file"
    fi
    
    # 更新状态
    update_status "$feature_name" "prd"
    
    # Git同步
    git_sync push "feat($feature_name): 需求文档"
    
    log_blue "下一步："
    log_blue "1. 官家审核PRD"
    log_blue "2. bash $0 $feature_name analyze（并行分析）"
}

# ==================== 并行分析（产品角度）====================

analyze_product() {
    local feature_name=$1
    local date=$(get_date)
    local prd_file="$PRODUCTS_DIR/${date}_${feature_name}_prd.md"
    
    if [ ! -f "$prd_file" ]; then
        log_error "PRD文档不存在，请先创建PRD"
        log_info "运行：bash $0 $feature_name prd"
        return 1
    fi
    
    log_blue "并行分析（产品角度）：$feature_name"
    
    # 追加分析到PRD
    cat >> "$prd_file" <<EOF

---

## 8. 米粒儿分析（产品角度）

**分析时间**：$(date '+%Y-%m-%d %H:%M:%S')

### 8.1 用户体验分析
- **易用性**：[分析]
- **学习曲线**：[分析]
- **错误处理**：[分析]

### 8.2 产品价值分析
- **核心价值**：[分析]
- **竞争优势**：[分析]
- **市场定位**：[分析]

### 8.3 边界情况分析
- **极端场景1**：[场景 + 处理建议]
- **极端场景2**：[场景 + 处理建议]
- **异常流程**：[分析]

### 8.4 风险评估
- **用户接受度风险**：[评估]
- **使用频率风险**：[评估]
- **依赖风险**：[评估]

### 8.5 给小米粒的建议
1. [建议1]
2. [建议2]
3. [建议3]

---

*分析时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*等待小米粒的技术分析...*
EOF
    
    log_info "产品分析已添加到PRD：$prd_file"
    log_blue "下一步：等待小米粒的技术分析"
    log_blue "小米粒运行：bash scripts/xiaomi_dev_v3.sh $feature_name analyze"
}

# ==================== 12维度Review ====================

review() {
    local feature_name=$1
    local date=$(get_date)
    local review_file="$REVIEWS_DIR/${date}_${feature_name}_review.md"
    local self_check_file="$REVIEWS_DIR/${date}_${feature_name}_self_check.md"
    
    ensure_dirs
    
    # 检查是否有Review请求
    if ! check_notify; then
        log_warn "请先等待小米粒的开发自检"
        log_info "小米粒运行：bash scripts/xiaomi_dev_v3.sh $feature_name check"
        return 1
    fi
    
    # 检查自检文档是否存在
    if [ ! -f "$self_check_file" ]; then
        log_error "找不到自检文档：$self_check_file"
        log_info "请确认小米粒已完成开发自检"
        return 1
    fi
    
    log_blue "开始12维度Review：$feature_name"
    
    # 读取自检文档
    log_blue "读取小米粒的自检文档..."
    cat "$self_check_file"
    echo
    
    # 创建Review文档
    cat > "$review_file" <<EOF
# Review报告 - $feature_name

**Review日期**：$date  
**Review者**：米粒儿  
**Review对象**：小米粒

---

## Review结果

- **状态**：⏳ Review进行中
- **总体评价**：待评估
- **星级**：待定

---

## 12维度Review

### 代码质量（4维度）

**1. 代码结构清晰**  
✅ / ⚠️ / ❌  
[评价...]

**2. 命名规范一致**  
✅ / ⚠️ / ❌  
[评价...]

**3. 注释文档完整**  
✅ / ⚠️ / ❌  
[评价...]

**4. 无明显性能问题**  
✅ / ⚠️ / ❌  
[评价...]

### 功能实现（3维度）

**5. 功能完整实现**  
✅ / ⚠️ / ❌  
[评价...]

**6. 测试覆盖充分**  
✅ / ⚠️ / ❌  
[评价...]

**7. 错误处理完善**  
✅ / ⚠️ / ❌  
[评价...]

### 最佳实践（3维度）

**8. 遵循最佳实践**  
✅ / ⚠️ / ❌  
[评价...]

**9. 安全性考虑**  
✅ / ⚠️ / ❌  
[评价...]

**10. 可维护性**  
✅ / ⚠️ / ❌  
[评价...]

### ClawHub发布（2维度）

**11. package.json准确**  
✅ / ⚠️ / ❌  
[评价...]

**12. SKILL.md完整**  
✅ / ⚠️ / ❌  
[评价...]

---

## Review思路

### 技术要点
1. [要点1]
2. [要点2]
3. [要点3]

### 风险点
1. [风险1]
2. [风险2]

### 亮点
1. [亮点1]
2. [亮点2]

---

## 13. 反对意见（必填）⭐⭐⭐⭐⭐

**启发来源**：Dev.to文章 "Your AI code reviewer has no one to disagree with"

### 米粒儿的反对意见
1. [反对点1：为什么这个方案不够好？]
2. [反对点2：有什么潜在风险？]
3. [反对点3：是否有更好的实现方式？]

### 为什么这些反对意见重要
[解释为什么这些反对意见值得关注...]

### 可能的解决方案
1. [方案1：如何解决反对点1？]
2. [方案2：如何解决反对点2？]
3. [方案3：如何解决反对点3？]

---

## 14. 系统约束检查

**启发来源**："The Four-Party Problem"（四方问题）

### Git状态
- ✅ / ⚠️ / ❌ [状态：是否有冲突？是否需要合并？]

### ClawHub配额
- ✅ / ⚠️ / ❌ [状态：是否有发布配额？]

### 网络依赖
- ✅ / ⚠️ / ❌ [状态：是否依赖外部API？网络是否稳定？]

### API限流风险
- ✅ / ⚠️ / ❌ [评估：是否可能触发限流？备用方案？]

---

## 改进建议

### 短期（发布前必须修复）
- [ ] [建议1]
- [ ] [建议2]

### 长期（后续优化）
- [ ] [建议3]
- [ ] [建议4]

---

## 学习要点

### 优点（值得保持）
1. [优点1]
2. [优点2]

### 需要改进
1. [改进1]
2. [改进2]

---

## 给小米粒的建议

### 技术方面
1. [建议1]
2. [建议2]

### 协作方面
1. [建议1]
2. [建议2]

---

## 等待双向思考

⏳ 等待小米粒的Review后思考...  
小米粒运行：bash scripts/xiaomi_dev_v3.sh $feature_name think

---

*Review时间：$(date '+%Y-%m-%d %H:%M:%S')*  
*状态：等待双向思考*
EOF
    
    log_info "Review文档已创建：$review_file"
    
    # 评论GitHub Issue（Git通信）
    comment_github_issue "$feature_name" "Review完成，✅ 批准发布"
    
    # 更新状态
    update_status "$feature_name" "review"
    
    # Git同步
    git_sync push "feat($feature_name): Review通过"
    
    log_blue "请完成Review评价后，运行："
    log_blue "bash $0 $feature_name accept（5层验收）"
}

# ==================== 5层验收 ====================

accept() {
    local feature_name=$1
    local date=$(get_date)
    local review_file="$REVIEWS_DIR/${date}_${feature_name}_review.md"
    
    if [ ! -f "$review_file" ]; then
        log_error "Review文档不存在，请先完成Review"
        log_info "运行：bash $0 $feature_name review"
        return 1
    fi
    
    log_blue "开始5层质量验收：$feature_name"
    
    # 检查Review是否已完成
    if grep -q "状态：⏳ Review进行中" "$review_file"; then
        log_error "Review尚未完成，请先完成12维度评价"
        log_info "编辑文件：$review_file"
        return 1
    fi
    
    # 检查Review结果
    if grep -q "状态：❌ 拒绝" "$review_file"; then
        log_error "Review结果为拒绝，需要小米粒修改"
        echo "rejected" > "$REJECTED_FILE"
        return 1
    fi
    
    # 追加5层验收到Review文档
    cat >> "$review_file" <<EOF

---

## 5层质量验收

### Layer 1: 需求完整性
✅ / ❌  
[验收结果...]

### Layer 2: 设计合理性
✅ / ❌  
[验收结果...]

### Layer 3: 代码质量
✅ / ❌  
[验收结果...]

### Layer 4: 功能完整性
✅ / ❌  
[验收结果...]

### Layer 5: 用户体验
✅ / ❌  
[验收结果...]

---

## 验收结果

- **状态**：✅ 批准发布 / ❌ 需要修改
- **验收时间**：$(date '+%Y-%m-%d %H:%M:%S')
- **验收者**：米粒儿

---

*验收时间：$(date '+%Y-%m-%d %H:%M:%S')*
EOF
    
    # 通知小米粒
    echo "approved" > "$APPROVED_FILE"
    echo "feature=$feature_name" >> "$APPROVED_FILE"
    echo "date=$date" >> "$APPROVED_FILE"
    echo "review_file=$review_file" >> "$APPROVED_FILE"
    
    # 评论GitHub Issue（Git通信）
    comment_github_issue "$feature_name" "5层验收完成，✅ 批准发布"
    
    # 更新状态
    update_status "$feature_name" "accept"
    
    # Git同步
    git_sync push "feat($feature_name): 5层验收通过"
    
    log_info "5层验收已完成"
    log_blue "已通知小米粒验收结果"
    log_blue "小米粒运行：bash scripts/xiaomi_dev_v3.sh $feature_name publish"
}

# ==================== 主函数 ====================

usage() {
    echo "米粒儿协作脚本 v3.0"
    echo ""
    echo "用法：bash $0 <功能名> <操作>"
    echo ""
    echo "操作："
    echo "  concept   - 创建产品构思"
    echo "  prd       - 编写需求文档"
    echo "  analyze   - 并行分析（产品角度）"
    echo "  review    - 12维度Review"
    echo "  accept    - 5层质量验收"
    echo ""
    echo "示例："
    echo "  bash $0 example-skill concept"
    echo "  bash $0 example-skill prd"
    echo "  bash $0 example-skill analyze"
    echo "  bash $0 example-skill review"
    echo "  bash $0 example-skill accept"
}

main() {
    if [ $# -lt 2 ]; then
        usage
        exit 1
    fi
    
    local feature_name=$1
    local action=$2
    
    log_blue "================================"
    log_blue "米粒儿协作脚本 v3.0"
    log_blue "功能：$feature_name"
    log_blue "操作：$action"
    log_blue "================================"
    
    case "$action" in
        concept)
            create_concept "$feature_name"
            ;;
        prd)
            create_prd "$feature_name"
            ;;
        analyze)
            analyze_product "$feature_name"
            ;;
        review)
            review "$feature_name"
            ;;
        accept)
            accept "$feature_name"
            ;;
        *)
            log_error "未知操作：$action"
            usage
            exit 1
            ;;
    esac
}

main "$@"
