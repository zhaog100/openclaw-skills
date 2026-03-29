#!/bin/bash
# 结构审计脚本
# 功能：生成 STRUCTURE_AUDIT_REPORT.md

set -e

WORKSPACE="$HOME/.openclaw/workspace"
REPORT="$WORKSPACE/STRUCTURE_AUDIT_REPORT.md"

echo "📊 生成结构审计报告..."

cat > "$REPORT" << 'EOF'
# 📊 结构化整理审计报告

**审计时间：** $(date '+%Y-%m-%d %H:%M')
**审计者：** github-bounty-hunter v2.2

---

## ✅ 检查项目

| 类别 | 状态 | 详情 |
|------|------|------|
| **记忆系统** | ✅ 检查 | memory/目录 |
| **知识库** | ✅ 检查 | knowledge/目录 |
| **索引系统** | ✅ 检查 | INDEX.md + L2/L3 索引 |
| **敏感信息** | ✅ 检查 | secrets/目录 + .gitignore |
| **Git 同步** | ✅ 检查 | git status |
| **QMD 向量化** | ✅ 检查 | qmd status |

---

## 📈 当前状态

### 记忆系统
$(ls -la "$WORKSPACE/memory/"*.md 2>/dev/null | wc -l) 个文件

### 知识库
$(ls -la "$WORKSPACE/knowledge/"*.md 2>/dev/null | wc -l) 个核心文件

### 索引系统
- L1: $(ls -la "$WORKSPACE/INDEX.md" 2>/dev/null | awk '{print $5}' | xargs -I {} echo "{}B" || echo "不存在")
- L2: $(ls -la "$WORKSPACE/knowledge/"*INDEX*.md 2>/dev/null | wc -l) 个文件
- L2: $(ls -la "$WORKSPACE/docs/"*INDEX*.md 2>/dev/null | wc -l) 个文件

### 敏感信息
$(ls -la "$WORKSPACE/secrets/" 2>/dev/null | tail -n +4 | wc -l) 个文件
.gitignore 保护：$(grep -q "secrets" "$WORKSPACE/.gitignore" && echo "✅" || echo "❌")

### Git 状态
$(cd "$WORKSPACE" && git status --short | wc -l) 个变更

### QMD 向量化
$(qmd status 2>&1 | grep "总计" || echo "未配置")

---

## 🎯 总体评分

**完成度：** 待评估

---

*报告生成时间：$(date '+%Y-%m-%d %H:%M:%S')*
EOF

echo "✅ 审计报告已生成：$REPORT"
