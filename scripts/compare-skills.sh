#!/bin/bash
# 技能对比分析脚本
# 创建时间：2026-03-06
# 功能：读取所有技能的SKILL.md，提取功能描述，对比重复功能

SKILLS_DIR="/root/.openclaw/workspace/skills"
OUTPUT_FILE="/root/.openclaw/workspace/logs/skills-comparison.md"

# 确保日志目录存在
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 清空输出文件
> "$OUTPUT_FILE"

echo "# 技能对比分析报告" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "生成时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 遍历所有技能目录
for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        skill_md="$skill_dir/SKILL.md"

        echo "## $skill_name" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"

        if [ -f "$skill_md" ]; then
            # 提取name、description、summary
            echo "### 元数据" >> "$OUTPUT_FILE"
            echo "\`\`\`" >> "$OUTPUT_FILE"
            grep -E "^(name|description|summary):" "$skill_md" | head -5 >> "$OUTPUT_FILE"
            echo "\`\`\`" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"

            # 提取前10行功能描述
            echo "### 功能描述（前10行）" >> "$OUTPUT_FILE"
            echo "\`\`\`" >> "$OUTPUT_FILE"
            tail -n +5 "$skill_md" | head -10 >> "$OUTPUT_FILE"
            echo "\`\`\`" >> "$OUTPUT_FILE"
        else
            echo "⚠️ SKILL.md 不存在" >> "$OUTPUT_FILE"
        fi

        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "✅ 技能对比分析完成！"
echo "📄 报告路径：$OUTPUT_FILE"
