#!/bin/bash
# =============================================================================
# 热点采集脚本 - 百度热搜
# =============================================================================
# 用法: hotspot-collector.sh [输出文件路径]
# 输出: intel/热点选题.md
# 数据源: 百度热搜（无需API key）
# =============================================================================

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
OUTPUT="${1:-$WORKSPACE/intel/热点选题.md}"
TODAY=$(date +%Y-%m-%d)
WEEKDAY=$(date +%A | sed 's/Monday/周一/;s/Tuesday/周二/;s/Wednesday/周三/;s/Thursday/周四/;s/Friday/周五/;s/Saturday/周六/;s/Sunday/周日/')
NOW=$(date '+%H:%M')

echo "=== 热点采集开始 ==="
echo "时间: $TODAY $NOW"
echo "数据源: 百度热搜"

# 采集百度热搜
TEMP_FILE=$(mktemp)
echo "正在采集百度热搜..."

# 使用curl直接抓取百度热搜JSON接口
curl -s --max-time 15 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Accept: application/json, text/plain, */*" \
  "https://top.baidu.com/api/board?platform=wise&tab=realtime" \
  > "$TEMP_FILE"

# 检查是否成功
if [ ! -s "$TEMP_FILE" ]; then
  echo "❌ 采集失败：无法获取数据"
  rm -f "$TEMP_FILE"
  exit 1
fi

# 解析JSON并生成Markdown
echo "正在解析数据..."

cat > "$OUTPUT" << HEADER
# 📰 每日热点选题推荐
**日期**: $TODAY（$WEEKDAY）
**更新时间**: $NOW
**数据来源**: 百度热搜

---

## 🔥 今日全网热点概览

| # | 热点话题 | 热度 | 标签 |
|---|---------|------|------|
HEADER

# 使用jq解析JSON并格式化输出
if command -v jq &> /dev/null; then
  jq -r '.data.cards[0].content[0].content[] | 
    select(.word != null) | 
    "| \(.index // 0) | \(.word) | \(.hotTag // "-") | \(.labelTagName // "-") |"' \
    "$TEMP_FILE" | head -20 >> "$OUTPUT"
else
  echo "❌ 需要安装jq工具"
  rm -f "$TEMP_FILE"
  exit 1
fi

# 添加运营分析部分
cat >> "$OUTPUT" << ANALYSIS

---

## 🎯 运营分析

### 热点分类统计
- **社会民生**：待分析
- **娱乐八卦**：待分析  
- **科技数码**：待分析
- **健康养生**：待分析

### 适配建议
1. **首选方向**：[待补充]
2. **备选方向**：[待补充]
3. **风险提示**：避免涉及敏感话题

### 选品关联
- **养生类**：午睡、健康、运动相关热点
- **办公类**：打工人、加班、效率相关热点

---

## 📋 待官家确认

- [ ] 今日是否追热点？
- [ ] 确认选品方向
- [ ] 内容形式（笔记/视频）

---

*自动采集于 $TODAY $NOW*
ANALYSIS

# 清理临时文件
rm -f "$TEMP_FILE"

# 确保文件权限
chmod 644 "$OUTPUT"

echo "✅ 热点采集完成"
echo "输出: $OUTPUT"
echo "条目: $(grep -c '^| [0-9]' "$OUTPUT" || echo 0)"
