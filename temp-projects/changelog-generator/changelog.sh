#!/bin/bash
# CHANGELOG Generator - Bash版本
# 用途: 从git历史自动生成CHANGELOG.md

set -e

echo "📝 Generating CHANGELOG.md from git history..."

# 获取最后一个tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# 生成CHANGELOG
cat > CHANGELOG.md << 'HEADER'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

HEADER

# 添加版本信息
if [ -n "$LAST_TAG" ]; then
    echo "" >> CHANGELOG.md
    echo "## [Unreleased] - $(date +%Y-%m-%d)" >> CHANGELOG.md
    COMMITS_RANGE="$LAST_TAG..HEAD"
else
    echo "" >> CHANGELOG.md
    echo "## [Initial] - $(date +%Y-%m-%d)" >> CHANGELOG.md
    COMMITS_RANGE="HEAD"
fi

# 分类并添加commits
echo "" >> CHANGELOG.md
echo "### Added" >> CHANGELOG.md
git log $COMMITS_RANGE --pretty=format:"- %s" --grep="^[Aa]dd\|^[Cc]reate\|^[Ii]mplement\|^[Ii]ntroduce\|^[Ss]upport" >> CHANGELOG.md 2>/dev/null || true

echo "" >> CHANGELOG.md
echo "" >> CHANGELOG.md
echo "### Changed" >> CHANGELOG.md
git log $COMMITS_RANGE --pretty=format:"- %s" --grep="^[Uu]pdate\|^[Cc]hange\|^[Mm]odify\|^[Ii]mprove\|^[Rr]efactor\|^[Oo]ptimize" >> CHANGELOG.md 2>/dev/null || true

echo "" >> CHANGELOG.md
echo "" >> CHANGELOG.md
echo "### Fixed" >> CHANGELOG.md
git log $COMMITS_RANGE --pretty=format:"- %s" --grep="^[Ff]ix\|^[Rr]epair\|^[Rr]esolve\|^[Cc]orrect\|^[Pp]atch" >> CHANGELOG.md 2>/dev/null || true

echo "" >> CHANGELOG.md
echo "" >> CHANGELOG.md
echo "### Removed" >> CHANGELOG.md
git log $COMMITS_RANGE --pretty=format:"- %s" --grep="^[Rr]emove\|^[Dd]elete\|^[Dd]eprecate\|^[Dd]rop" >> CHANGELOG.md 2>/dev/null || true

echo "" >> CHANGELOG.md

echo "✅ CHANGELOG.md generated successfully!"
echo ""
echo "Preview:"
head -30 CHANGELOG.md
