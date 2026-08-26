# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# 发布到 ClawHub 和 GitHub
# =========================================
#
# 功能:
# 1. 敏感信息检查
# 2. 创建 GitHub Release
# 3. 发布到 ClawHub
#
# 用法:
#   ./publish.sh <version>
#
# 示例:
#   ./publish.sh v1.0.0

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="multi-channel-memory"
VERSION="${1:-v1.0.0}"
GITHUB_REPO="${GITHUB_USERNAME:-your_username}/repo-name"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

echo "========================================="
echo "🚀 技能发布脚本 - $SKILL_NAME"
echo "版本：$VERSION"
echo "========================================="
echo ""

# 步骤 1: 敏感信息检查
log_info "步骤 1/4: 敏感信息扫描..."

SENSITIVE_PATTERNS=(
    "token[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]"
    "password[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]"
    "secret[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]"
    "api_key[[:space:]]*=[[:space:]]*['\"][^'\"]+['\"]"
    "1478D4753463307D2E176B905A8B7F5E"
)

FOUND_SENSITIVE=false
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if grep -rE "$pattern" --include="*.py" --include="*.sh" --include="*.md" --include="*.json" . 2>/dev/null | grep -v node_modules | grep -v ".git"; then
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    log_error "发现敏感信息！请先清理后再发布。"
fi

log_success "✅ 敏感信息检查通过"
echo ""

# 步骤 2: Git 提交
log_info "步骤 2/4: Git 提交..."

cd "$WORKSPACE_DIR"
git add -A
if ! git diff --cached --quiet; then
    git commit -m "🚀 发布 $SKILL_NAME $VERSION" || true
    log_success "✅ Git 提交完成"
else
    log_warning "⚠️ 没有新的变更"
fi
echo ""

# 步骤 3: 创建 GitHub Release
log_info "步骤 3/4: 创建 GitHub Release..."

cd "$WORKSPACE_DIR/skills/$SKILL_NAME"

# 打包技能目录
TEMP_DIR="/tmp/$SKILL_NAME-$VERSION"
mkdir -p "$TEMP_DIR"
cp -r . "$TEMP_DIR/"
cd "/tmp"
tar -czf "$SKILL_NAME-$VERSION.tar.gz" "$SKILL_NAME-$VERSION"
rm -rf "$TEMP_DIR"

log_success "✅ 技能包已打包：/tmp/$SKILL_NAME-$VERSION.tar.gz"
echo ""

# 步骤 4: 发布说明
log_info "步骤 4/4: 发布说明"
echo ""
echo "========================================="
echo "📦 发布准备完成！"
echo "========================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 手动创建 GitHub Release:"
echo "   https://github.com/$GITHUB_REPO/releases/new"
echo "   - Tag: $VERSION"
echo "   - Upload: /tmp/$SKILL_NAME-$VERSION.tar.gz"
echo ""
echo "2. 发布到 ClawHub:"
echo "   openclaw skills publish $SKILL_NAME"
echo ""
echo "3. 更新 ClawHub 索引:"
echo "   编辑 knowledge/clawhub-skills-index.md"
echo "   添加技能信息"
echo ""
log_success "🎉 发布准备完成！"
