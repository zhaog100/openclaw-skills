#!/bin/bash
# ClawHub技能对比脚本
# 创建时间：2026-03-06 19:16
# 功能：对比本地技能和ClawHub上的技能，找出差异

SKILLS_DIR="/root/.openclaw/workspace/skills"
OUTPUT_FILE="/root/.openclaw/workspace/logs/clawhub-comparison.md"

# 确保输出目录存在
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 清空输出文件
> "$OUTPUT_FILE"

echo "# ClawHub vs 本地技能对比报告" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "生成时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 获取ClawHub上的技能列表
echo "## 📊 ClawHub技能列表" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

clawhub_list=$(clawhub list 2>&1)
echo '```' >> "$OUTPUT_FILE"
echo "$clawhub_list" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 获取本地技能列表
echo "## 📂 本地技能列表" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

local_skills=$(ls -1 "$SKILLS_DIR" | grep -v "^\.")
echo '```' >> "$OUTPUT_FILE"
echo "$local_skills" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 对比版本
echo "## 🔄 版本对比" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 定义本地技能版本（从SKILL.md中提取）
declare -A local_versions

for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        skill_file="$skill_dir/SKILL.md"
        
        if [ -f "$skill_file" ]; then
            # 尝试从SKILL.md中提取版本号
            version=$(grep -iE "^version:|^metadata:" "$skill_file" | head -1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" || echo "未知")
            local_versions["$skill_name"]="$version"
        else
            local_versions["$skill_name"]="无SKILL.md"
        fi
    fi
done

# 对比每个技能
echo "| 技能名称 | ClawHub版本 | 本地版本 | 状态 |" >> "$OUTPUT_FILE"
echo "|---------|------------|---------|------|" >> "$OUTPUT_FILE"

# 处理ClawHub上的技能
while IFS= read -r line; do
    if [ -n "$line" ]; then
        skill_name=$(echo "$line" | awk '{print $1}')
        clawhub_version=$(echo "$line" | awk '{print $2}')
        local_version="${local_versions[$skill_name]:-不存在}"
        
        if [ "$local_version" = "$clawhub_version" ]; then
            status="✅ 同步"
        elif [ "$local_version" = "不存在" ]; then
            status="⚠️ 本地缺失"
        elif [ "$local_version" = "未知" ] || [ "$local_version" = "无SKILL.md" ]; then
            status="⚠️ 无法对比"
        else
            status="🔄 需更新"
        fi
        
        echo "| $skill_name | $clawhub_version | $local_version | $status |" >> "$OUTPUT_FILE"
        
        # 从本地技能列表中移除已处理的技能
        unset "local_versions[$skill_name]"
    fi
done <<< "$clawhub_list"

# 处理本地有但ClawHub没有的技能
for skill_name in "${!local_versions[@]}"; do
    local_version="${local_versions[$skill_name]}"
    echo "| $skill_name | 不存在 | $local_version | 🆕 本地独有 |" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"

# 统计信息
echo "## 📊 统计信息" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

clawhub_count=$(echo "$clawhub_list" | wc -l)
local_count=$(ls -1 "$SKILLS_DIR" | grep -v "^\." | wc -l)

echo "**ClawHub技能数**：$clawhub_count" >> "$OUTPUT_FILE"
echo "**本地技能数**：$local_count" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 详细对比
echo "## 📝 详细对比" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        skill_file="$skill_dir/SKILL.md"
        
        if [ -f "$skill_file" ]; then
            echo "### $skill_name" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 提取描述
            description=$(grep -iE "^description:" "$skill_file" | head -1 | sed 's/description: //' || echo "无描述")
            echo "**描述**：$description" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 文件数量
            file_count=$(find "$skill_dir" -type f | wc -l)
            echo "**文件数**：$file_count" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            echo "---" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    fi
done

echo "对比完成！报告已保存到：$OUTPUT_FILE"
cat "$OUTPUT_FILE"
