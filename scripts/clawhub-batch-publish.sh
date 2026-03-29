#!/bin/bash
# ClawHub 批量发布脚本
# 自动打包、发布多个技能到 ClawHub

set -e

echo "🌾 === 小米辣 ClawHub 批量发布助手 ==="
echo ""

# 配置区
SKILLS_DIR="/home/zhaog/.openclaw/workspace/skills"
OUTPUT_DIR="/home/zhaog/.openclaw/workspace/output"
PUBLISH_LOG="$OUTPUT_DIR/publish-log-$(date +%Y%m%d-%H%M%S).md"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 初始化发布日志
cat > "$PUBLISH_LOG" << EOF
# ClawHub 批量发布日志

**发布时间：** $(date '+%Y-%m-%d %H:%M:%S')  
**发布工具：** 小米辣批量发布脚本 v1.0  
**发布模式：** 批量自动发布

---

## 发布列表

EOF

echo "📋 请选择发布模式："
echo "1. 发布所有技能"
echo "2. 发布指定技能（手动输入名称）"
echo "3. 发布最近修改的技能（24 小时内）"
echo ""
read -p "请输入选项 (1-3): " MODE

# 技能列表数组
declare -a SKILLS_TO_PUBLISH

case $MODE in
    1)
        echo ""
        echo "📦 扫描所有技能..."
        for skill_path in "$SKILLS_DIR"/*/; do
            if [ -d "$skill_path" ] && [ -f "$skill_path/SKILL.md" ]; then
                skill_name=$(basename "$skill_path")
                # 跳过归档和隐藏目录
                if [[ "$skill_name" != "_archived" ]] && [[ "$skill_name" != "."* ]]; then
                    SKILLS_TO_PUBLISH+=("$skill_name")
                fi
            fi
        done
        ;;
    
    2)
        echo ""
        echo "请输入技能名称（用空格分隔，例如：context-manager smart-model-switch）："
        read -p "> " INPUT_SKILLS
        SKILLS_TO_PUBLISH=($INPUT_SKILLS)
        ;;
    
    3)
        echo ""
        echo "🔍 查找最近 24 小时内修改的技能..."
        while IFS= read -r skill_path; do
            skill_name=$(basename "$skill_path")
            SKILLS_TO_PUBLISH+=("$skill_name")
        done < <(find "$SKILLS_DIR" -maxdepth 2 -name "SKILL.md" -mtime -1 -exec dirname {} \; | sort -u)
        ;;
    
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "✅ 待发布技能列表："
for i in "${!SKILLS_TO_PUBLISH[@]}"; do
    echo "   $((i+1)). ${SKILLS_TO_PUBLISH[$i]}"
done
echo ""

read -p "确认发布？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ 发布已取消"
    exit 0
fi

# 发布统计
TOTAL=${#SKILLS_TO_PUBLISH[@]}
SUCCESS=0
FAILED=0
SKIPPED=0

echo ""
echo "================================"
echo "🚀 开始批量发布（共 $TOTAL 个技能）"
echo "================================"
echo ""

# 遍历技能列表
for skill_name in "${SKILLS_TO_PUBLISH[@]}"; do
    skill_path="$SKILLS_DIR/$skill_name"
    
    echo ""
    echo -e "${BLUE}=== 发布技能：$skill_name ===${NC}"
    
    # 检查技能目录
    if [ ! -d "$skill_path" ]; then
        echo -e "${RED}❌ 技能目录不存在：$skill_path${NC}"
        FAILED=$((FAILED + 1))
        echo "**$skill_name** | ❌ 失败 | 目录不存在" >> "$PUBLISH_LOG"
        continue
    fi
    
    # 检查 SKILL.md
    if [ ! -f "$skill_path/SKILL.md" ]; then
        echo -e "${RED}❌ SKILL.md 缺失${NC}"
        FAILED=$((FAILED + 1))
        echo "**$skill_name** | ❌ 失败 | SKILL.md 缺失" >> "$PUBLISH_LOG"
        continue
    fi
    
    # 检查 package.json
    if [ ! -f "$skill_path/package.json" ]; then
        echo -e "${YELLOW}⚠️  package.json 缺失，尝试创建...${NC}"
        cat > "$skill_path/package.json" << EOF
{
  "name": "$skill_name",
  "version": "1.0.0",
  "description": "Auto-generated package.json",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["openclaw", "skill"],
  "author": "小米辣",
  "license": "MIT"
}
EOF
        echo "✅ package.json 已创建"
    fi
    
    # 获取版本号
    version=$(grep -o '"version": *"[^"]*"' "$skill_path/package.json" | cut -d'"' -f4)
    if [ -z "$version" ]; then
        version="1.0.0"
    fi
    
    # 打包技能
    echo "📦 打包技能..."
    tarball_name="${skill_name}-v${version}.tar.gz"
    tarball_path="$OUTPUT_DIR/$tarball_name"
    
    # 排除不必要的文件
    tar -czf "$tarball_path" \
        --exclude='node_modules' \
        --exclude='logs' \
        --exclude='*.log' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -C "$SKILLS_DIR" "$skill_name"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 打包失败${NC}"
        FAILED=$((FAILED + 1))
        echo "**$skill_name** | ❌ 失败 | 打包失败" >> "$PUBLISH_LOG"
        continue
    fi
    
    echo "✅ 打包完成：$tarball_path"
    
    # 检查文件大小
    file_size=$(du -h "$tarball_path" | cut -f1)
    echo "📊 文件大小：$file_size"
    
    # 发布到 ClawHub
    echo "🚀 发布到 ClawHub..."
    
    # 使用 clawnet publish 命令
    if command -v clawnet &> /dev/null; then
        publish_output=$(clawnet publish "$tarball_path" 2>&1) || true
        
        if echo "$publish_output" | grep -q "published\|success\|成功"; then
            echo -e "${GREEN}✅ 发布成功${NC}"
            SUCCESS=$((SUCCESS + 1))
            
            # 提取 ClawHub ID
            clawhub_id=$(echo "$publish_output" | grep -o 'k[a-z0-9]\{32\}' | head -1)
            
            echo "**$skill_name** | ✅ 成功 | v$version | $file_size | ID: $clawhub_id" >> "$PUBLISH_LOG"
        else
            echo -e "${YELLOW}⚠️  发布可能需要手动处理${NC}"
            echo "$publish_output" | tail -5
            SKIPPED=$((SKIPPED + 1))
            echo "**$skill_name** | ⚠️ 跳过 | 需要手动发布 | $file_size" >> "$PUBLISH_LOG"
        fi
    else
        echo -e "${YELLOW}⚠️  clawnet 命令未找到，跳过发布${NC}"
        SKIPPED=$((SKIPPED + 1))
        echo "**$skill_name** | ⚠️ 跳过 | clawnet 未安装 | $file_size" >> "$PUBLISH_LOG"
    fi
    
    # 清理 tarball（可选）
    # rm "$tarball_path"
done

echo ""
echo "================================"
echo "📊 发布统计"
echo "================================"
echo -e "总数：${TOTAL}"
echo -e "${GREEN}成功：${SUCCESS}${NC}"
echo -e "${YELLOW}跳过：${SKIPPED}${NC}"
echo -e "${RED}失败：${FAILED}${NC}"
echo ""

# 更新发布日志
cat >> "$PUBLISH_LOG" << EOF

---

## 发布统计

- **总数：** $TOTAL
- **成功：** $SUCCESS
- **跳过：** $SKIPPED
- **失败：** $FAILED

---

**日志生成时间：** $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo "📄 发布日志：$PUBLISH_LOG"
echo ""
echo "🌾 批量发布完成！"
