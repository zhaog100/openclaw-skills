#!/bin/bash
# ============================================================
# Pre-Commit Check Script v1.0
# 技能提交前自动检查：版本号 / 敏感信息 / 版权 / 分支唯一性
# 用法: bash scripts/pre-commit-check.sh [技能目录]
# 示例: bash scripts/pre-commit-check.sh skills/github-bounty-hunter
# ============================================================

SKILL_DIR="${1:-.}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
ERRORS=0

echo "============================================"
echo "🔍 提交前检查: $SKILL_DIR"
echo "============================================"
echo ""

# ---------- 1. 版本号一致性 ----------
echo "1️⃣ 版本号一致性"
if [ -f "$SKILL_DIR/SKILL.md" ] && [ -f "$SKILL_DIR/package.json" ]; then
    SKILL_VER=$(grep -m1 '^version:' "$SKILL_DIR/SKILL.md" | awk '{print $2}' | tr -d '[:space:]')
    PKG_VER=$(grep '"version"' "$SKILL_DIR/package.json" | head -1 | sed 's/.*: *"//;s/".*//')
    
    if [ "$SKILL_VER" = "$PKG_VER" ]; then
        echo -e "   ✅ SKILL.md=$SKILL_VER, package.json=$PKG_VER"
    else
        echo -e "   ❌ 不一致: SKILL.md=$SKILL_VER vs package.json=$PKG_VER"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "   ⚠️  缺少 SKILL.md 或 package.json（跳过）"
fi
echo ""

# ---------- 2. 敏感信息扫描 ----------
echo "2️⃣ 敏感信息扫描"
SENSITIVE_PATTERNS=(
    "zhaog100"
    "ghp_[A-Za-z0-9]\{36,\}"
    "gho_[A-Za-z0-9]\{36,\}"
    "sk-[A-Za-z0-9]\{20,\}"
    "0x[a-fA-F0-9]\{40\}"
    "AKIA[0-9A-Z]\{16\}"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    MATCHES=$(grep -rn "$pattern" "$SKILL_DIR" \
        --include="*.md" --include="*.sh" --include="*.py" --include="*.js" --include="*.json" \
        --exclude-dir=node_modules --exclude-dir=.git 2>/dev/null)
    if [ -n "$MATCHES" ]; then
        echo -e "   ❌ 检测到敏感模式: $pattern"
        echo "$MATCHES" | head -3 | sed 's/^/      /'
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ] || ! grep -q "❌ 检测到敏感模式" <<< "$(grep -rn "zhaog100\|ghp_\|gho_\|sk-\|0x[a-fA-F0-9]\{40\}" "$SKILL_DIR" 2>/dev/null)"; then
    echo -e "   ✅ 未发现敏感信息"
fi
echo ""

# ---------- 3. 版权信息检查 ----------
echo "3️⃣ 版权信息检查"
MISSING_COPYRIGHT=0
for f in $(find "$SKILL_DIR" -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.js" 2>/dev/null | grep -v node_modules); do
    if ! grep -qi "copyright\|license\|MIT\|版权" "$f" 2>/dev/null; then
        echo -e "   ❌ 缺少版权: $f"
        MISSING_COPYRIGHT=$((MISSING_COPYRIGHT + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $MISSING_COPYRIGHT -eq 0 ]; then
    echo -e "   ✅ 所有文件都有版权头"
fi
echo ""

# ---------- 4. 分支唯一性 ----------
echo "4️⃣ 分支唯一性"
if git rev-parse --is-inside-work-tree &>/dev/null; then
    BRANCH=$(git -C "$SKILL_DIR" branch --show-current 2>/dev/null || git branch --show-current)
    echo -e "   📌 当前分支: $BRANCH"
    
    # 检查是否在 main/master 上
    if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
        echo -e "   ⚠️  正在 $BRANCH 分支上，建议创建功能分支"
    else
        echo -e "   ✅ 功能分支: $BRANCH"
    fi
else
    echo -e "   ⚠️  不在 git 仓库中（跳过）"
fi
echo ""

# ---------- 总结 ----------
echo "============================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 全部通过！可以提交${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS 个问题需要修复${NC}"
    exit 1
fi
