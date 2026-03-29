#!/bin/bash
# 技能深度去重分析脚本
# 创建时间：2026-03-06 18:59
# 功能：全面对比所有技能，找出重复功能，提供合并建议

SKILLS_DIR="/root/.openclaw/workspace/skills"
OUTPUT_FILE="/root/.openclaw/workspace/logs/skills-deep-dedup.md"

# 确保输出目录存在
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 清空输出文件
> "$OUTPUT_FILE"

echo "# 技能深度去重分析报告" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "生成时间：$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 1. 统计所有技能
echo "## 📊 技能总览" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

total_skills=$(ls -1 "$SKILLS_DIR" | grep -v "^\." | wc -l)
echo "**总技能数**：$total_skills" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 2. 分析每个技能的核心功能
echo "## 🔍 功能分析" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

declare -A skill_functions
declare -A skill_keywords

for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        skill_file="$skill_dir/SKILL.md"
        
        if [ -f "$skill_file" ]; then
            echo "### $skill_name" >> "$OUTPUT_FILE"
            
            # 提取关键词
            keywords=$(grep -iE "description:|功能|feature|能力" "$skill_file" | head -5 | tr '\n' ' ')
            echo "**描述**：$keywords" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 提取工具/命令
            tools=$(grep -iE "tool|command|bash|script" "$skill_file" | head -5 | tr '\n' ' ')
            echo "**工具**：$tools" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 提取依赖
            deps=$(grep -iE "require|depend|install" "$skill_file" | head -5 | tr '\n' ' ')
            echo "**依赖**：$deps" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 存储功能关键词
            skill_functions["$skill_name"]="$keywords"
            skill_keywords["$skill_name"]=$(echo "$keywords $tools" | tr '[:upper:]' '[:lower:]')
            
            echo "---" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    fi
done

# 3. 对比分析（找出重复功能）
echo "## 🔄 重复功能检测" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 定义功能分类
declare -A categories
categories["browser"]="browser|playwright|puppeteer|selenium|网页|浏览器|自动化"
categories["search"]="search|搜索|find|query|检索"
categories["scrape"]="scrape|爬取|crawl|spider|extract"
categories["github"]="github|git|repo|repository|pr|issue"
categories["cloud"]="cloud|云|tencent|阿里|aws|azure"
categories["knowledge"]="knowledge|知识|qmd|memory|笔记"
categories["automation"]="automation|自动|cron|schedule|定时"

# 检查每个分类
for category in "${!categories[@]}"; do
    pattern="${categories[$category]}"
    matches=""
    
    for skill in "${!skill_keywords[@]}"; do
        keywords="${skill_keywords[$skill]}"
        if echo "$keywords" | grep -qiE "$pattern"; then
            matches="$matches $skill"
        fi
    done
    
    if [ -n "$matches" ]; then
        count=$(echo "$matches" | wc -w)
        if [ $count -gt 1 ]; then
            echo "### $category 类功能" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "**匹配技能**（$count个）：$matches" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            
            # 详细对比
            for skill in $matches; do
                skill_file="$SKILLS_DIR/$skill/SKILL.md"
                if [ -f "$skill_file" ]; then
                    echo "**$skill**：" >> "$OUTPUT_FILE"
                    grep -iE "description:|核心功能|核心能力" "$skill_file" | head -3 >> "$OUTPUT_FILE"
                    echo "" >> "$OUTPUT_FILE"
                fi
            done
            
            echo "---" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    fi
done

# 4. 合并建议
echo "## 💡 合并建议" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 检查浏览器类技能
browser_skills=$(echo "${skill_keywords[@]}" | grep -oE "agent-browser|playwright-scraper" | sort -u | tr '\n' ' ')
if [ -n "$browser_skills" ]; then
    count=$(echo "$browser_skills" | wc -w)
    if [ $count -gt 1 ]; then
        echo "### 浏览器自动化技能" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "**发现重复**：$browser_skills" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "**建议**：" >> "$OUTPUT_FILE"
        echo "- agent-browser：性能优先，适合简单操作" >> "$OUTPUT_FILE"
        echo "- playwright-scraper：功能优先，适合复杂爬取" >> "$OUTPUT_FILE"
        echo "- **合并建议**：保留两个，功能互补" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
fi

# 检查搜索类技能
search_skills=$(echo "${skill_keywords[@]}" | grep -oE "qmd-manager|find-skills|tavily-search" | sort -u | tr '\n' ' ')
if [ -n "$search_skills" ]; then
    count=$(echo "$search_skills" | wc -w)
    if [ $count -gt 1 ]; then
        echo "### 搜索类技能" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "**发现多个搜索技能**：$search_skills" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "**功能对比**：" >> "$OUTPUT_FILE"
        echo "- qmd-manager：本地知识库搜索" >> "$OUTPUT_FILE"
        echo "- find-skills：在线技能发现" >> "$OUTPUT_FILE"
        echo "- tavily-search：AI优化的网页搜索" >> "$OUTPUT_FILE"
        echo "- **合并建议**：保留三个，功能不同" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
fi

# 5. 总结
echo "## 📋 总结" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**分析完成时间**：$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**总技能数**：$total_skills" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "分析完成！报告已保存到：$OUTPUT_FILE"
cat "$OUTPUT_FILE"
