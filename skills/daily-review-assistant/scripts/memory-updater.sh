# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# =============================================================================
# 记忆更新器 (Memory Updater) - 优化版
# =============================================================================
set -e
# 版本：v2.0
# 创建时间：2026-05-09
# 创建者：小米辣
# 用途：自动更新 MEMORY.md 和 daily log，智能提炼经验教训
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"
_CURRENT_LOG_FILE="$CFG_LOGS_DIR/memory-updater.log"

# 更新今日日志
update_daily_log() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "📝 更新今日日志：$daily_log"
    
    if [ ! -f "$daily_log" ]; then
        cat > "$daily_log" << EOF
# $date 工作记录

## 身份确认
- **小米辣** 🌶️ | **GitHub**: $CFG_GITHUB_USERNAME
- **远程仓库**: origin → ${GITHUB_USERNAME:-xiaomila}/skills
- **检查时间**: $(date '+%Y-%m-%d %H:%M')

## 今日完成

### 上午


### 下午


## 📊 今日统计

- **工作时长**: 小时
- **Git 提交**: 个
- **完成任务**: 个

## 📝 学习笔记

### 今日学到的新知识


### 遇到的问题及解决方案


### 代码质量提升点


## 💡 经验教训

### 技术经验


### 流程优化


### 其他教训


## 🎯 明日计划


---

*更新时间：$(date '+%Y-%m-%d %H:%M')*
*更新者：小米辣 (AI 助手)*
EOF
        log_info "  ✅ 创建今日日志模板"
    else
        log_info "  ✅ 今日日志已存在"
        
        # 确保日志包含必要的章节
        ensure_daily_log_structure "$daily_log"
    fi
}

# 确保日志结构完整
ensure_daily_log_structure() {
    local daily_log="$1"
    
    log_info "  🔧 检查日志结构完整性..."
    
    # 检查并添加学习笔记章节
    if ! grep -q "## 📝 学习笔记" "$daily_log"; then
        sed -i '/## 🎯 明日计划/i\
## 📝 学习笔记\
\
### 今日学到的新知识\
\
### 遇到的问题及解决方案\
\
### 代码质量提升点\
' "$daily_log"
        log_info "  ✅ 添加学习笔记章节"
    fi
    
    # 检查并添加经验教训章节
    if ! grep -q "## 💡 经验教训" "$daily_log"; then
        sed -i '/## 📝 学习笔记/a\
## 💡 经验教训\
\
### 技术经验\
\
### 流程优化\
\
### 其他教训\
' "$daily_log"
        log_info "  ✅ 添加经验教训章节"
    fi
    
    # 检查并添加财务状态章节
    if ! grep -q "## 💰 财务状态" "$daily_log"; then
        sed -i '/## 📊 今日统计/a\
## 💰 财务状态\
\
### Bounty收益\
\
### 待收款项目\
' "$daily_log"
        log_info "  ✅ 添加财务状态章节"
    fi
}

# 更新 MEMORY.md
update_memory_file() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "📝 更新 MEMORY.md"
    
    if [ ! -f "$CFG_MEMORY_FILE" ]; then
        cat > "$CFG_MEMORY_FILE" << 'EOF'
# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**: knowledge/

**记忆文件路径**: memory/

---

## 📋 核心教训

### 项目选择经验
- 不是所有bounty项目都会付款，需要验证实际支付记录
- 项目是否接受外部贡献者很重要（如la-tanda-web教训）
- 中小型活跃项目 > 大型项目

### 技术经验
- OpenClaw三层配置：openclaw.json + models.json + auth-profiles.json
- Docker Buildx可显著提升构建性能
- Git历史清理需要使用git-filter-repo

### 流程优化
- 高质量PR比数量重要
- 定期检查和更新记忆系统
- 查漏补缺机制很重要

---

## 💡 高价值锚点词

### 项目经验
- **la-tanda-web**: 19个PR全部CLOSED，不接受外部贡献者 ❌
- **RustChain**: 付款问题，承诺160 RTC实际给25 RTC ⚠️
- **homelab-stack**: 高质量项目，维护者响应积极 ✅

### 技术锚点
- **LongCat**: 需要正确配置端点 `/openai`
- **Git LFS**: 大文件管理，配置后需定期清理

### 财务锚点
- **待收款**: 约$830 USD + 202 RTC
- **已关闭**: RustChain多个PR付款未到账
- **进行中**: homelab-stack PR待审核

---

## 📊 PR统计

| 状态 | 数量 | 备注 |
|------|------|------|
| Open | ~300 | 包含多个高价值任务 |
| Merged | ~15 | 质量优先 |
| Closed | ~200+ | 包含主动关闭和项目关闭 |

---

## 🔑 重要联系人和资源

### 项目维护者
- **Scottcjn**: RustChain，需要催款跟进
- **homelab-stack**: 维护者响应积极

### 钱包信息
- **RTC**: RTC2f0e423eafe70cb9394fd11ff4d11bd515d
- **USDT**: 待配置

---

## 🎯 待办事项

- [ ] RustChain催款跟进
- [ ] 高价值PR审核状态监控
- [ ] 知识库定期更新
- [ ] 系统性能优化

---

## 📈 近期重要事件

### 2026-05-09
- la-tanda-web 19个PR全部CLOSED
- PR #125 CodeRabbit review paused

### 2026-05-08
- 系统性整理完成
- QMD向量库配置完成

### 2026-05-07
- la-tanda-web 3个PR提交
- 系统维护完成

---

*持续进化 · 定期清理 · 保留精华*
*最后更新：<!-- 最后更新标记 -->*
EOF
        log_info "  ✅ 创建 MEMORY.md"
    fi
    
    if [ -f "$daily_log" ]; then
        local today_tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 今日完成任务：$today_tasks 个"
        
        # 智能提炼重要内容到MEMORY.md
        extract_important_content "$daily_log" "$date"
        
        if [ "$today_tasks" -gt 0 ] 2>/dev/null; then
            update_memory_timestamp "$date"
        fi
    fi
}

# 智能提炼重要内容
extract_important_content() {
    local daily_log="$1"
    local date="$2"
    local memory_file="$CFG_MEMORY_FILE"
    
    log_info "  🧠 智能提炼重要内容..."
    
    # 提取项目相关的重要经验
    local project_lessons=$(grep -A 3 -B 3 "la-tanda-web\|RustChain\|homelab-stack\|ubiquity-os" "$daily_log" 2>/dev/null | grep -i "教训\|问题\|经验\|注意" | head -5)
    
    if [ -n "$project_lessons" ]; then
        log_info "  📋 发现项目经验教训"
        
        # 确保MEMORY.md有今日的项目经验记录
        if ! grep -q "### $date 项目经验" "$memory_file"; then
            # 添加到项目经验部分
            local insert_line=$(grep -n "### 项目经验" "$memory_file" | head -1 | cut -d: -f1)
            if [ -n "$insert_line" ]; then
                sed -i "${insert_line}a\\
\\
### $date 项目经验\\
" "$memory_file"
                log_info "  ✅ 添加项目经验记录"
            fi
        fi
    fi
    
    # 提取技术经验
    local tech_lessons=$(grep -A 2 -B 2 "技术\|配置\|工具\|脚本" "$daily_log" 2>/dev/null | grep -i "教训\|优化\|提升" | head -5)
    
    if [ -n "$tech_lessons" ]; then
        log_info "  🔧 发现技术经验"
        
        if ! grep -q "### $date 技术经验" "$memory_file"; then
            local insert_line=$(grep -n "### 技术经验" "$memory_file" | head -1 | cut -d: -f1)
            if [ -n "$insert_line" ]; then
                sed -i "${insert_line}a\\
\\
### $date 技术经验\\
" "$memory_file"
                log_info "  ✅ 添加技术经验记录"
            fi
        fi
    fi
    
    # 提取财务相关信息
    local financial_info=$(grep -i "bounty\|收益\|付款\|USDT\|RTC" "$daily_log" 2>/dev/null | head -5)
    
    if [ -n "$financial_info" ]; then
        log_info "  💰 发现财务相关信息"
        
        # 更新财务锚点词
        update_financial_anchors "$financial_info" "$date"
    fi
}

# 更新财务锚点词
update_financial_anchors() {
    local financial_info="$1"
    local date="$2"
    local memory_file="$CFG_MEMORY_FILE"
    
    log_info "  💎 更新财务锚点词..."
    
    # 提取金额信息
    local amounts=$(echo "$financial_info" | grep -oP '\$\d+|\d+\s*(USDT|RTC)' | head -5)
    
    if [ -n "$amounts" ]; then
        log_info "  📊 发现金额信息：$amounts"
        
        # 添加到财务锚点部分
        if ! grep -q "### $date 财务更新" "$memory_file"; then
            local insert_line=$(grep -n "### 财务锚点" "$memory_file" | head -1 | cut -d: -f1)
            if [ -n "$insert_line" ]; then
                sed -i "${insert_line}a\\
\\
### $date 财务更新\\
- 发现金额：$amounts\\
" "$memory_file"
                log_info "  ✅ 添加财务更新"
            fi
        fi
    fi
}

# 更新MEMORY.md时间戳
update_memory_timestamp() {
    local date="$1"
    local memory_file="$CFG_MEMORY_FILE"
    
    log_info "  ⏰ 更新时间戳..."
    
    local timestamp="*最后更新：$(date '+%Y-%m-%d %H:%M') HKT*"
    
    if grep -q "最后更新标记" "$memory_file"; then
        sed -i "s/<!-- 最后更新标记 -->/$timestamp/" "$memory_file"
    else
        echo "" >> "$memory_file"
        echo "$timestamp" >> "$memory_file"
    fi
    
    log_info "  ✅ 时间戳已更新"
}

# 生成报告
generate_update_report() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新报告                                          ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  今日日志：$([ -f "$daily_log" ] && echo '✅ 已创建' || echo '⚠️ 未创建')"
    log_info "║  MEMORY.md: $([ -f "$CFG_MEMORY_FILE" ] && echo '✅ 已更新' || echo '⚠️ 未更新')"
    log_info "║  内容提炼：$(grep -c "### $date" "$CFG_MEMORY_FILE" 2>/dev/null || echo '0') 条"
    log_info "╚════════════════════════════════════════════════════════╝"
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新器 v2.0 - 小米辣                                ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    update_daily_log "$date"
    update_memory_file "$date"
    generate_update_report "$date"
    
    log_info "✅ 记忆更新完成！"
}

main "$@"