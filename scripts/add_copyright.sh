#!/bin/bash
# 新技能版权保护自动添加脚本
# 用法：bash scripts/add_copyright.sh <技能名>
# 作者：小米粒
# 版本：v1.0.0

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}用法：bash scripts/add_copyright.sh <技能名>${NC}"
    echo "示例：bash scripts/add_copyright.sh my-new-skill"
    exit 1
fi

SKILL_NAME="$1"
SKILL_DIR="skills/$SKILL_NAME"

# 检查技能是否存在
if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${YELLOW}❌ 技能目录不存在：$SKILL_DIR${NC}"
    echo "请先创建技能目录"
    exit 1
fi

echo -e "${BLUE}🌾 开始为 $SKILL_NAME 添加版权保护...${NC}"
echo ""

# 版权声明内容（SKILL.md和README.md）
COPYRIGHT_SECTION='

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 米粒儿 (miliger)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

**商业使用授权**：
- 小微企业（<10人）：¥999/年
- 中型企业（10-50人）：¥4,999/年
- 大型企业（>50人）：¥19,999/年
- 企业定制版：¥99,999一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)
'

# 主脚本版权注释
SCRIPT_COPYRIGHT='#!/bin/bash
# <技能名> - <技能描述>
# 版本：v1.0.0
# 创建者：米粒儿 (miliger)
# 创建时间：'$(date +%Y-%m-%d)'
#
# 版权声明：
# MIT License
# Copyright (c) 2026 米粒儿 (miliger)
# 免费使用、修改和重新分发时，需注明出处。
# GitHub: https://github.com/zhaog100/openclaw-skills
# ClawHub: https://clawhub.com

set -e
'

# package.json 版权字段
PACKAGE_COPYRIGHT='{
  "name": "<技能名>",
  "version": "1.0.0",
  "description": "<技能描述>",
  "author": "米粒儿 (miliger)",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/zhaog100/openclaw-skills"
  }
}
'

# 1. 更新 SKILL.md
SKILL_MD="$SKILL_DIR/SKILL.md"
if [ -f "$SKILL_MD" ]; then
    if grep -q "许可证与版权声明" "$SKILL_MD" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  SKILL.md - 已有版权声明，跳过${NC}"
    else
        echo "$COPYRIGHT_SECTION" >> "$SKILL_MD"
        echo -e "${GREEN}✅ SKILL.md - 已添加版权声明${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  SKILL.md - 文件不存在${NC}"
fi

# 2. 更新 README.md
README_MD="$SKILL_DIR/README.md"
if [ -f "$README_MD" ]; then
    if grep -q "许可证与版权声明" "$README_MD" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  README.md - 已有版权声明，跳过${NC}"
    else
        echo "$COPYRIGHT_SECTION" >> "$README_MD"
        echo -e "${GREEN}✅ README.md - 已添加版权声明${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  README.md - 文件不存在${NC}"
fi

# 3. 更新 package.json
PACKAGE_JSON="$SKILL_DIR/package.json"
if [ -f "$PACKAGE_JSON" ]; then
    # 检查是否有license字段
    if grep -q '"license"' "$PACKAGE_JSON" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  package.json - 已有license字段，跳过${NC}"
    else
        # 添加license和author字段（简单实现）
        sed -i 's/{/{\n  "author": "米粒儿 (miliger)",\n  "license": "MIT",/' "$PACKAGE_JSON" 2>/dev/null || true
        echo -e "${GREEN}✅ package.json - 已添加版权字段${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  package.json - 文件不存在${NC}"
fi

# 4. 查找主脚本并添加版权注释
MAIN_SCRIPTS=$(find "$SKILL_DIR" -maxdepth 1 -name "*.sh" -type f 2>/dev/null)
if [ -n "$MAIN_SCRIPTS" ]; then
    for script in $MAIN_SCRIPTS; do
        if grep -q "Copyright (c) 2026 米粒儿" "$script" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  $(basename $script) - 已有版权注释，跳过${NC}"
        else
            # 在文件开头添加版权注释（简化版）
            sed -i '1i\# 版权声明：MIT License | Copyright (c) 2026 米粒儿 (miliger) | GitHub: https://github.com/zhaog100/openclaw-skills' "$script" 2>/dev/null || true
            echo -e "${GREEN}✅ $(basename $script) - 已添加版权注释${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠️  未找到.sh脚本文件${NC}"
fi

echo ""
echo -e "${GREEN}✅ 版权保护添加完成！${NC}"
echo ""
echo "📋 已添加的版权保护："
echo "  - ✅ MIT License"
echo "  - ✅ 版权声明（需注明出处）"
echo "  - ✅ 商业授权条款（¥999/¥4,999/¥19,999/¥99,999）"
echo ""
echo "📂 下一步："
echo "  1. git add skills/$SKILL_NAME/"
echo "  2. git commit -m \"feat($SKILL_NAME): 添加完整版权保护\""
echo "  3. git push origin master"
