#!/bin/bash
# demo-skill - 双米粒协作系统演示技能
# 版本：v1.0.0
# 创建者：小米粒
# 创建时间：2026-03-12
#
# 版权声明：
# MIT License
# Copyright (c) 2026 思捷娅科技
# 免费使用、修改和重新分发时，需注明出处。
# GitHub: https://github.com/zhaog100/openclaw-skills

set -e

# 版本信息
VERSION="1.0.0"
AUTHOR="思捷娅科技"
CREATED="2026-03-12"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示欢迎信息
show_welcome() {
    cat << 'EOF'
🌾 demo-skill - 双米粒协作系统演示
========================================

欢迎体验双米粒协作系统！

【可用命令】
  demo-skill         显示此欢迎信息
  demo-skill status  显示系统状态
  demo-skill info    显示技能信息
  demo-skill help    显示帮助文档

【协作流程】
  1. 米粒儿创建PRD → 2. 小米粒技术设计 → 3. 小米粒开发 →
  4. 双向Review → 5. 发布到ClawHub

【版本】v1.0.0
【创建者】小米粒
EOF
}

# 显示系统状态
show_status() {
    echo -e "${BLUE}📊 双米粒协作系统状态${NC}"
    echo "========================================"
    echo ""

    # 检查Git状态
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Git仓库：正常${NC}"
        echo "   分支：$(git branch --show-current)"
        echo "   提交：$(git log -1 --oneline)"
    else
        echo -e "${YELLOW}⚠️  Git仓库：未找到${NC}"
    fi

    echo ""

    # 检查GitHub CLI
    if command -v gh &> /dev/null; then
        echo -e "${GREEN}✅ GitHub CLI：正常${NC}"
        echo "   版本：$(gh --version | head -1)"
    else
        echo -e "${YELLOW}⚠️  GitHub CLI：未安装${NC}"
    fi

    echo ""

    # 检查ClawHub CLI
    if command -v clawhub &> /dev/null; then
        echo -e "${GREEN}✅ ClawHub CLI：正常${NC}"
    else
        echo -e "${YELLOW}⚠️  ClawHub CLI：未安装${NC}"
    fi

    echo ""
    echo "【协作流程】"
    echo "  1. ✅ 米粒儿完成PRD"
    echo "  2. ✅ 小米粒技术设计"
    echo "  3. ⏳ 小米粒开发实现（当前）"
    echo "  4. ⏳ 双向Review"
    echo "  5. ⏳ 发布到ClawHub"
}

# 显示技能信息
show_info() {
    cat << 'EOF'
📦 demo-skill 技能信息
========================================

【基本信息】
  名称：demo-skill
  版本：v1.0.0
  创建者：小米粒
  创建时间：2026-03-12

【技术栈】
  语言：Bash 4.0+
  依赖：无（纯本地执行）
  网络：无需网络请求

【功能列表】
  1. demo-skill         显示欢迎信息
  2. demo-skill status  显示系统状态
  3. demo-skill info    显示技能信息
  4. demo-skill help    显示帮助文档

【发布信息】
  ClawHub ID：待发布
  GitHub Issue：#2

【许可证】
  MIT License
EOF
}

# 显示帮助文档
show_help() {
    cat << 'EOF'
📚 demo-skill 帮助文档
========================================

【命令详解】

1. demo-skill
   功能：显示欢迎信息和可用命令
   示例：demo-skill
   输出：欢迎信息 + 4个可用命令

2. demo-skill status
   功能：显示双米粒协作系统状态
   示例：demo-skill status
   输出：
     - Git仓库状态
     - GitHub CLI状态
     - ClawHub CLI状态
     - 协作流程进度

3. demo-skill info
   功能：显示技能元信息
   示例：demo-skill info
   输出：
     - 基本信息（名称、版本、创建者）
     - 技术栈（语言、依赖、网络）
     - 功能列表
     - 发布信息

4. demo-skill help
   功能：显示此帮助文档
   示例：demo-skill help
   输出：详细帮助 + 协作流程

---

【双米粒协作流程】

步骤1️⃣  米粒儿创建PRD
  - 编写产品需求文档
  - 创建GitHub Issue
  - Git提交并推送

步骤2️⃣  小米粒技术设计
  - 查询Issue
  - 创建技术设计文档
  - 评论Issue（技术设计完成）

步骤3️⃣  小米粒开发实现
  - 编写代码
  - 编写测试
  - 自检（质疑清单）

步骤4️⃣  双向Review
  - 米粒儿12维度Review
  - 小米粒回应质疑
  - 米粒儿5层验收

步骤5️⃣  发布到ClawHub
  - 小米粒发布
  - 生成Package ID
  - 关闭Issue

---

【技术架构】

┌─────────────────┐
│   demo-skill    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───┴───┐ ┌───┴───┐
│ Bash  │ │  Git  │
└───────┘ └───────┘

【无外部依赖】
- ❌ API Key
- ❌ 网络请求
- ❌ 数据库
- ❌ 第三方库

---

【常见问题】

Q1: 这个技能有什么用？
A1: 演示双米粒协作系统的完整工作流程

Q2: 需要配置什么？
A2: 无需配置，开箱即用

Q3: 支持哪些平台？
A3: Linux/macOS（Bash 4.0+）

Q4: 如何安装？
A4: clawhub install demo-skill

---

【联系方式】

GitHub Issue：https://github.com/zhaog100/openclaw-skills/issues/2
创建者：小米粒
创建时间：2026-03-12
EOF
}

# 主命令解析
main() {
    local command="${1:-}"

    case "$command" in
        ""|welcome)
            show_welcome
            ;;
        status)
            show_status
            ;;
        info)
            show_info
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "❌ 未知命令：$command"
            echo ""
            echo "可用命令："
            echo "  demo-skill         显示欢迎信息"
            echo "  demo-skill status  显示系统状态"
            echo "  demo-skill info    显示技能信息"
            echo "  demo-skill help    显示帮助文档"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
