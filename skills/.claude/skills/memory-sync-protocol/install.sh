#!/bin/bash
# Memory Sync Protocol 安装脚本

set -e

SKILL_NAME="memory-sync-protocol"
SKILL_DIR="$HOME/.openclaw/workspace/skills/$SKILL_NAME"

echo "============================================================"
echo "🚀 安装 $SKILL_NAME"
echo "============================================================"
echo ""

# 1. 检查依赖
echo "1️⃣  检查依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python 3"
    exit 1
fi

if ! command -v bun &> /dev/null; then
    echo "⚠️  建议安装 Bun（用于 QMD 检索）"
    echo "   请访问：https://bun.sh 安装"
fi
echo "✅ 依赖检查通过"
echo ""

# 2. 创建目录
echo "2️⃣  创建目录..."
mkdir -p "$SKILL_DIR"
echo "✅ 目录已创建：$SKILL_DIR"
echo ""

# 3. 复制文件
echo "3️⃣  复制文件..."
cp -r scripts/ "$SKILL_DIR/"
cp -r config/ "$SKILL_DIR/" 2>/dev/null || true
cp -r templates/ "$SKILL_DIR/" 2>/dev/null || true
cp SKILL.md README.md package.json "$SKILL_DIR/"
echo "✅ 文件已复制"
echo ""

# 4. 设置权限
echo "4️⃣  设置权限..."
chmod +x "$SKILL_DIR/scripts/"*.py 2>/dev/null || true
chmod +x "$SKILL_DIR/install.sh" 2>/dev/null || true
echo "✅ 权限已设置"
echo ""

# 5. 安装 Python 依赖
echo "5️⃣  安装 Python 依赖..."
if [ -f "$SKILL_DIR/requirements.txt" ]; then
    pip3 install -r "$SKILL_DIR/requirements.txt"
    echo "✅ Python 依赖已安装"
else
    echo "⚠️  无 Python 依赖"
fi
echo ""

# 6. 配置定时任务
echo "6️⃣  配置定时任务..."
(crontab -l 2>/dev/null | grep -v "$SKILL_NAME"; \
echo "# $SKILL_NAME 定时任务"; \
echo "# 每周日 2:00 记忆维护"; \
echo "0 2 * * 0 $SKILL_DIR/scripts/memory-optimizer.py >> $SKILL_DIR/logs/optimize.log 2>&1"; \
echo "# 每天 23:30 AI 查漏补缺"; \
echo "30 23 * * * $SKILL_DIR/scripts/token-monitor.py >> $SKILL_DIR/logs/monitor.log 2>&1") | crontab -
echo "✅ 定时任务已配置"
echo ""

# 7. 验证安装
echo "7️⃣  验证安装..."
if [ -f "$SKILL_DIR/scripts/memory-optimizer.py" ]; then
    echo "✅ 安装成功！"
    echo ""
    echo "============================================================"
    echo "📚 使用方式"
    echo "============================================================"
    echo ""
    echo "# 运行优化"
    echo "python3 $SKILL_DIR/scripts/memory-optimizer.py"
    echo ""
    echo "# 查看文档"
    echo "cat $SKILL_DIR/README.md"
    echo ""
    echo "# 查看技能说明"
    echo "cat $SKILL_DIR/SKILL.md"
    echo ""
    echo "============================================================"
else
    echo "❌ 安装失败"
    exit 1
fi
