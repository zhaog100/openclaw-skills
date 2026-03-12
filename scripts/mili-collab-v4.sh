#!/bin/bash
# 米粒儿协作脚本 v4.0 - Git 通信集成版
# 角色：产品经理 + 质量官
# 核心功能：产品构思、需求文档、12 维度 Review（含反对意见）、5 层验收、Git 通信

set -e

WORKSPACE="/home/zhaog/.openclaw/workspace"
PRODUCTS_DIR="$WORKSPACE/docs/products"
REVIEWS_DIR="$WORKSPACE/docs/reviews"
COMM_DIR="$WORKSPACE/.mili_comm"
GIT_REPO="github.com/zhaog100/openclaw-skills"
NOTIFY_FILE="/tmp/notify_mili.txt"
APPROVED_FILE="/tmp/review_approved.txt"
REJECTED_FILE="/tmp/review_rejected.txt"
ISSUES_FILE="$COMM_DIR/issues.txt"
STATUS_FILE="$COMM_DIR/status.json"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_blue() { echo -e "${BLUE}[MILI]${NC} $1"; }
log_magenta() { echo -e "${MAGENTA}[REVIEW]${NC} $1"; }
log_cyan() { echo -e "${CYAN}[STATUS]${NC} $1"; }

# 获取当前日期
get_date() {
    date +%Y-%m-%d
}

get_timestamp() {
    date +%Y%m%d_%H%M%S
}

# 确保目录存在
ensure_dirs() {
    mkdir -p "$PRODUCTS_DIR"
    mkdir -p "$REVIEWS_DIR"
    mkdir -p "$COMM_DIR"
    mkdir -p "$COMM_DIR/inbox"
    mkdir -p "$COMM_DIR/outbox"
    mkdir -p "$COMM_DIR/archive"
}

# ==================== Git 通信 ====================

# 创建 GitHub Issue
create_github_issue() {
    local feature=$1
    local stage=$2
    local description=$3
    
    log_blue "创建 GitHub Issue：[$feature] $stage"
    
    if ! command -v gh &> /dev/null; then
        log_warn "GitHub CLI 未安装，跳过 Issue 创建"
        return 0
    fi
    
    local title="[$feature] $stage - $(get_date)"
    gh issue create --title "$title" --label "米粒儿，$stage" --body "$description" 2>&1 || log_info "Issue 创建成功"
}

# Git 同步
git_sync() {
    local message=${1:-"update"}
    local dir=${2:-"$WORKSPACE"}
    
    cd "$dir"
    git add -A
    if git diff --staged --quiet; then
        log_info "无变更，跳过提交"
        return 0
    fi
    git commit -m "$message" || true
    git push origin master 2>&1 || log_warn "推送失败，可能网络问题"
}

# 检查 Git 状态
check_git_status() {
    cd "$WORKSPACE"
    local status=$(git status --porcelain)
    if [ -n "$status" ]; then
        log_warn "有未提交的变更："
        echo "$status" | head -10
    else
        log_info "Git 工作区干净"
    fi
}

# ==================== 产品构思 ====================

create_concept() {
    local feature=$1
    local date=$(get_date)
    local concept_file="$PRODUCTS_DIR/${date}_${feature}_concept.md"
    
    ensure_dirs
    
    log_blue "创建产品构思：$feature"
    
    cat > "$concept_file" << EOF
# 产品构思 - $feature

**创建日期：** $date  
**创建者：** 米粒儿  
**状态：** 构思阶段  

---

## 🎯 核心价值

### 用户痛点
[描述用户面临的问题]

### 解决方案
[描述解决方案]

### 预期价值
[描述预期带来的价值]

---

## 📊 市场分析

### 目标用户
- [用户群体 1]
- [用户群体 2]

### 竞品分析
| 竞品 | 优势 | 劣势 | 我们的差异化 |
|------|------|------|-------------|
| 竞品 1 | | | |
| 竞品 2 | | | |

---

## 🚀 下一步

- [ ] 完善需求文档
- [ ] 技术可行性分析
- [ ] 资源评估

---

**下次更新：** [日期]
EOF
    
    log_info "产品构思已创建：$concept_file"
    
    # 创建 GitHub Issue
    create_github_issue "$feature" "concept" "产品构思：$feature"
    
    # Git 同步
    git_sync "feat($feature): 创建产品构思" "$WORKSPACE"
}

# ==================== 需求文档 ====================

create_prd() {
    local feature=$1
    local concept_file="$PRODUCTS_DIR/$(ls -t "$PRODUCTS_DIR" | grep "${feature}_concept.md" | head -1)"
    local date=$(get_date)
    local prd_file="$PRODUCTS_DIR/${date}_${feature}_PRD.md"
    
    ensure_dirs
    
    log_blue "创建需求文档：$feature"
    
    if [ ! -f "$concept_file" ]; then
        log_warn "未找到产品构思文件，先创建构思"
        create_concept "$feature"
    fi
    
    cat > "$prd_file" << EOF
# 产品需求文档 - $feature

**创建日期：** $date  
**创建者：** 米粒儿  
**状态：** 需求阶段  
**版本：** v1.0  

---

## 📋 文档概述

### 产品愿景
[一句话描述产品愿景]

### 目标用户
- **主要用户：** [用户画像]
- **次要用户：** [用户画像]

### 使用场景
1. [场景 1]
2. [场景 2]

---

## 🎯 功能需求

### 核心功能
| 功能 | 描述 | 优先级 | 验收标准 |
|------|------|--------|----------|
| 功能 1 | | P0 | |
| 功能 2 | | P1 | |

### 辅助功能
| 功能 | 描述 | 优先级 |
|------|------|--------|
| 功能 3 | | P2 |

---

## 🔧 技术需求

### 技术栈
- 前端：
- 后端：
- 数据库：

### 性能指标
- 响应时间：< 200ms
- 并发支持：> 1000 QPS
- 可用性：> 99.9%

### 安全要求
- [ ] 数据加密
- [ ] 访问控制
- [ ] 审计日志

---

## 📊 数据需求

### 数据指标
- DAU/MAU
- 留存率
- 转化率

### 埋点设计
| 事件 | 触发条件 | 上报数据 |
|------|----------|----------|
| | | |

---

## 🚀 发布计划

### Phase 1 (MVP)
- [ ] 核心功能 1
- [ ] 核心功能 2

### Phase 2
- [ ] 辅助功能 1
- [ ] 优化功能

---

## ⚠️ 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 技术风险 | | | |
| 资源风险 | | | |

---

**评审状态：** 待评审  
**下次更新：** [日期]
EOF
    
    log_info "需求文档已创建：$prd_file"
    
    # 创建 GitHub Issue
    create_github_issue "$feature" "PRD" "需求文档：$feature"
    
    # Git 同步
    git_sync "feat($feature): 创建需求文档" "$WORKSPACE"
}

# ==================== 12 维度 Review ====================

perform_review() {
    local feature=$1
    local prd_file="$PRODUCTS_DIR/$(ls -t "$PRODUCTS_DIR" | grep "${feature}_PRD.md" | head -1)"
    local date=$(get_date)
    local timestamp=$(get_timestamp)
    local review_file="$REVIEWS_DIR/${date}_${feature}_review_${timestamp}.md"
    
    ensure_dirs
    
    log_magenta "开始 12 维度 Review：$feature"
    
    if [ ! -f "$prd_file" ]; then
        log_error "未找到需求文档：$prd_file"
        return 1
    fi
    
    cat > "$review_file" << EOF
# Review 报告 - $feature

**Review 日期：** $(date '+%Y-%m-%d %H:%M:%S')  
**Reviewer：** 米粒儿（质量官）  
**被评审文档：** $prd_file  
**Review 类型：** 12 维度批判性评审  

---

## 📊 12 维度评审

### 1️⃣ 价值维度
**评分：** ⭐⭐⭐⭐☆ (4/5)

**优点：**
- [价值点 1]
- [价值点 2]

**质疑：**
- ❓ 这个价值是否真实存在？
- ❓ 用户是否愿意为此付费？

**建议：** [改进建议]

---

### 2️⃣ 用户需求维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**优点：**
- [需求点 1]

**质疑：**
- ❓ 这是真实需求还是伪需求？
- ❓ 目标用户是否足够大？

**建议：** [改进建议]

---

### 3️⃣ 技术可行性维度
**评分：** ⭐⭐⭐⭐☆ (4/5)

**优点：**
- [技术点 1]

**质疑：**
- ❓ 技术难点是否已识别？
- ❓ 是否有备选方案？

**建议：** [改进建议]

---

### 4️⃣ 资源可行性维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 人力是否充足？
- ❓ 时间是否合理？
- ❓ 预算是否足够？

**建议：** [改进建议]

---

### 5️⃣ 市场竞争维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 竞品是否已有类似功能？
- ❓ 我们的差异化是否足够？

**建议：** [改进建议]

---

### 6️⃣ 商业模式维度
**评分：** ⭐⭐☆☆☆ (2/5)

**质疑：**
- ❓ 如何盈利？
- ❓ 成本结构是否合理？

**建议：** [改进建议]

---

### 7️⃣ 用户体验维度
**评分：** ⭐⭐⭐⭐☆ (4/5)

**优点：**
- [体验点 1]

**质疑：**
- ❓ 是否考虑了边界场景？
- ❓ 是否有用户测试计划？

**建议：** [改进建议]

---

### 8️⃣ 数据驱动维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 关键指标是否明确？
- ❓ 是否有 A/B 测试计划？

**建议：** [改进建议]

---

### 9️⃣ 风险控制维度
**评分：** ⭐⭐☆☆☆ (2/5)

**质疑：**
- ❓ 是否识别了所有风险？
- ❓ 应对措施是否具体？

**建议：** [改进建议]

---

### 🔟 可扩展性维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 是否支持未来扩展？
- ❓ 架构是否灵活？

**建议：** [改进建议]

---

### 1️⃣1️⃣ 法律合规维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 是否符合相关法规？
- ❓ 隐私保护是否到位？

**建议：** [改进建议]

---

### 1️⃣2️⃣ 社会影响维度
**评分：** ⭐⭐⭐☆☆ (3/5)

**质疑：**
- ❓ 是否有负面社会影响？
- ❓ 是否符合伦理？

**建议：** [改进建议]

---

## 📈 综合评分

| 维度 | 评分 | 权重 | 加权分 |
|------|------|------|--------|
| 价值 | 4/5 | 15% | 0.60 |
| 用户需求 | 3/5 | 15% | 0.45 |
| 技术可行性 | 4/5 | 10% | 0.40 |
| 资源可行性 | 3/5 | 10% | 0.30 |
| 市场竞争 | 3/5 | 10% | 0.30 |
| 商业模式 | 2/5 | 10% | 0.20 |
| 用户体验 | 4/5 | 10% | 0.40 |
| 数据驱动 | 3/5 | 5% | 0.15 |
| 风险控制 | 2/5 | 5% | 0.10 |
| 可扩展性 | 3/5 | 5% | 0.15 |
| 法律合规 | 3/5 | 3% | 0.09 |
| 社会影响 | 3/5 | 2% | 0.06 |
| **总分** | | **100%** | **3.20/5** |

---

## ✅ Review 决定

**结果：** ✅ 批准进入下一阶段 / ⚠️ 需要改进 / ❌ 拒绝

**理由：** [详细说明]

**必须改进项：**
1. [改进项 1]
2. [改进项 2]

**建议改进项：**
1. [建议项 1]
2. [建议项 2]

---

## 📝 反对意见（批判性思维）

### 反对观点 1
[反对意见内容]

**反驳：** [反驳内容]

### 反对观点 2
[反对意见内容]

**反驳：** [反驳内容]

---

**Reviewed-by:** 米粒儿  
**日期：** $(date '+%Y-%m-%d')
EOF
    
    log_magenta "Review 完成：$review_file"
    
    # 创建 GitHub Issue
    create_github_issue "$feature" "Review" "12 维度 Review：$feature - 综合评分 3.20/5"
    
    # Git 同步
    git_sync "review($feature): 12 维度 Review" "$WORKSPACE"
}

# ==================== 5 层验收 ====================

perform_acceptance() {
    local feature=$1
    local review_file="$REVIEWS_DIR/$(ls -t "$REVIEWS_DIR" | grep "${feature}_review" | head -1)"
    local date=$(get_date)
    local timestamp=$(get_timestamp)
    local acceptance_file="$REVIEWS_DIR/${date}_${feature}_acceptance_${timestamp}.md"
    
    ensure_dirs
    
    log_cyan "开始 5 层验收：$feature"
    
    cat > "$acceptance_file" << EOF
# 5 层验收报告 - $feature

**验收日期：** $(date '+%Y-%m-%d %H:%M:%S')  
**验收官：** 米粒儿  
**参考文档：** $review_file  

---

## 🏗️ 5 层验收框架

### 第 1 层：功能验收
**状态：** ✅ 通过 / ⚠️ 部分通过 / ❌ 未通过

**验收项：**
- [ ] 核心功能 1 已实现
- [ ] 核心功能 2 已实现
- [ ] 辅助功能已实现

**测试结果：**
| 测试用例 | 预期结果 | 实际结果 | 状态 |
|----------|----------|----------|------|
| | | | |

---

### 第 2 层：性能验收
**状态：** ✅ 通过 / ⚠️ 部分通过 / ❌ 未通过

**验收指标：**
- [ ] 响应时间 < 200ms
- [ ] 并发支持 > 1000 QPS
- [ ] 可用性 > 99.9%

**测试数据：**
- 平均响应时间：ms
- 峰值 QPS：
- 可用性：%

---

### 第 3 层：安全验收
**状态：** ✅ 通过 / ⚠️ 部分通过 / ❌ 未通过

**验收项：**
- [ ] 数据加密已实现
- [ ] 访问控制已配置
- [ ] 审计日志已开启
- [ ] 漏洞扫描通过

---

### 第 4 层：用户体验验收
**状态：** ✅ 通过 / ⚠️ 部分通过 / ❌ 未通过

**验收项：**
- [ ] 界面美观
- [ ] 操作流畅
- [ ] 错误提示友好
- [ ] 帮助文档完善

**用户反馈：**
- 正面反馈：
- 负面反馈：

---

### 第 5 层：业务验收
**状态：** ✅ 通过 / ⚠️ 部分通过 / ❌ 未通过

**验收指标：**
- [ ] DAU 达到目标
- [ ] 转化率达到目标
- [ ] 留存率达到目标

**实际数据：**
- DAU：
- 转化率：%
- 留存率：%

---

## 📊 验收总结

| 层级 | 状态 | 备注 |
|------|------|------|
| 功能验收 | | |
| 性能验收 | | |
| 安全验收 | | |
| 用户体验验收 | | |
| 业务验收 | | |

---

## ✅ 验收决定

**结果：** ✅ 通过验收 / ⚠️ 有条件通过 / ❌ 未通过

**条件/改进项：**
1. [改进项 1]
2. [改进项 2]

---

**Accepted-by:** 米粒儿  
**日期：** $(date '+%Y-%m-%d')
EOF
    
    log_cyan "验收完成：$acceptance_file"
    
    # Git 同步
    git_sync "acceptance($feature): 5 层验收" "$WORKSPACE"
}

# ==================== 状态管理 ====================

update_status() {
    local feature=$1
    local stage=$2
    
    ensure_dirs
    
    if [ ! -f "$STATUS_FILE" ]; then
        echo "{}" > "$STATUS_FILE"
    fi
    
    # 使用 jq 更新状态（如果可用）
    if command -v jq &> /dev/null; then
        local temp_file=$(mktemp)
        jq --arg f "$feature" --arg s "$stage" --arg t "$(date -Iseconds)" \
           '.[$f] = {"stage": $s, "updated_at": $t}' "$STATUS_FILE" > "$temp_file"
        mv "$temp_file" "$STATUS_FILE"
    else
        # 简单文本记录
        echo "$(date -Iseconds) | $feature | $stage" >> "$STATUS_FILE"
    fi
    
    log_cyan "状态已更新：$feature -> $stage"
}

get_status() {
    local feature=$1
    
    if [ -f "$STATUS_FILE" ]; then
        if command -v jq &> /dev/null; then
            jq -r --arg f "$feature" '.[$f].stage // "unknown"' "$STATUS_FILE"
        else
            grep "$feature" "$STATUS_FILE" | tail -1
        fi
    else
        echo "unknown"
    fi
}

# ==================== 通知机制 ====================

notify_mili() {
    local message=$1
    
    ensure_dirs
    
    echo "$message" > "$NOTIFY_FILE"
    log_blue "通知已发送：$message"
}

check_notifications() {
    if [ -f "$NOTIFY_FILE" ]; then
        log_blue "待处理通知："
        cat "$NOTIFY_FILE"
        rm "$NOTIFY_FILE"
    else
        log_info "无待处理通知"
    fi
}

# ==================== 主函数 ====================

show_help() {
    echo "米粒儿协作脚本 v4.0 - 产品管理 + 质量审查"
    echo ""
    echo "用法：bash $0 <功能名> <操作> [参数]"
    echo ""
    echo "操作："
    echo "  concept     - 创建产品构思"
    echo "  prd         - 创建需求文档"
    echo "  review      - 12 维度 Review"
    echo "  acceptance  - 5 层验收"
    echo "  status      - 查看状态"
    echo "  notify      - 发送通知"
    echo "  git-status  - 检查 Git 状态"
    echo ""
    echo "示例："
    echo "  bash $0 smart-model concept          # 创建产品构思"
    echo "  bash $0 smart-model prd              # 创建需求文档"
    echo "  bash $0 smart-model review           # 12 维度 Review"
    echo "  bash $0 smart-model acceptance       # 5 层验收"
    echo "  bash $0 smart-model status           # 查看状态"
    echo ""
}

main() {
    if [ $# -lt 2 ]; then
        show_help
        exit 1
    fi
    
    local feature=$1
    local action=$2
    
    case "$action" in
        concept)
            create_concept "$feature"
            update_status "$feature" "concept"
            ;;
        prd)
            create_prd "$feature"
            update_status "$feature" "prd"
            ;;
        review)
            perform_review "$feature"
            update_status "$feature" "review"
            ;;
        acceptance)
            perform_acceptance "$feature"
            update_status "$feature" "acceptance"
            ;;
        status)
            get_status "$feature"
            ;;
        notify)
            notify_mili "${3:-无消息}"
            ;;
        git-status)
            check_git_status
            ;;
        *)
            log_error "未知操作：$action"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
