#!/bin/bash
# =============================================================================
# 每日数据复盘脚本
# 用途: 汇总当日各平台运营数据，生成复盘报告
# 时间: 每天 20:30 执行
# =============================================================================

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/intel"
LOG_FILE="$WORKSPACE/logs/data-review.log"
TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')
REPORT_FILE="$REPORT_DIR/数据复盘.md"

echo "[$TODAY $NOW] 开始每日数据复盘..." | tee -a "$LOG_FILE"

# 确保目录存在
mkdir -p "$REPORT_DIR"
mkdir -p "$WORKSPACE/logs"

# 生成复盘报告
cat > "$REPORT_FILE" << EOF
# 📝 ${TODAY} 每日数据复盘

**日期**: ${TODAY}
**复盘时间**: ${NOW}
**维护**: 小米椒 🌶️🔥

---

## 📊 今日已发布内容数据

**状态**: 待官家补充实际数据

| 平台 | 发布数 | 状态 | 说明 |
|------|--------|------|------|
| 小红书 | - | 待统计 | - |
| 微博 | - | 待统计 | - |
| 视频号 | - | 待统计 | - |

**数据统计**：
- 总发布数：待统计
- 总阅读数：待统计
- 总点赞数：待统计
- 总收藏数：待统计
- 总评论数：待统计

---

## 🔍 数据分析

### 热点采集状态
EOF

# 检查今日热点采集
HOTSPOT_FILE="$REPORT_DIR/热点选题.md"
if [ -f "$HOTSPOT_FILE" ]; then
    HOTSPOT_DATE=$(head -5 "$HOTSPOT_FILE" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1)
    if [ "$HOTSPOT_DATE" = "$TODAY" ]; then
        echo "- ✅ 热点采集已完成 ($HOTSPOT_FILE)" >> "$REPORT_FILE"
    else
        echo "- ⚠️ 热点采集文件日期不匹配 (文件: $HOTSPOT_DATE, 今日: $TODAY)" >> "$REPORT_FILE"
    fi
else
    echo "- ❌ 热点采集文件不存在" >> "$REPORT_FILE"
fi

# 检查石油黄金分析
echo "" >> "$REPORT_FILE"
echo "## 📈 石油黄金分析状态" >> "$REPORT_FILE"
HOURLY_LOG="/logs/oil-gold-hourly.log"
DAILY_LOG="/logs/oil-gold-daily.log"
if [ -f "$HOURLY_LOG" ]; then
    LAST_HOURLY=$(tail -3 "$HOURLY_LOG" 2>/dev/null | head -1)
    echo "- 最近一次分析: $LAST_HOURLY" >> "$REPORT_FILE"
else
    echo "- ⚠️ 暂无分析日志" >> "$REPORT_FILE"
fi

# 检查公考信息采集
echo "" >> "$REPORT_FILE"
echo "## 🎓 公考信息采集状态" >> "$REPORT_FILE"
EXAM_FILE="$WORKSPACE/reports/exam-info-chengdu-${TODAY}.md"
if [ -f "$EXAM_FILE" ]; then
    echo "- ✅ 成都公考信息已采集" >> "$REPORT_FILE"
else
    echo "- ℹ️ 今日无公考信息采集（可能非执行日）" >> "$REPORT_FILE"
fi

# 添加待办提醒
echo "" >> "$REPORT_FILE"
echo "## 📋 待办提醒" >> "$REPORT_FILE"
if [ -f "$REPORT_DIR/运营待办.md" ]; then
    P0_COUNT=$(grep -c "^\- \[ \]" "$REPORT_DIR/运营待办.md" 2>/dev/null || echo "0")
    echo "- 运营待办: ${P0_COUNT} 项未完成" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "_自动生成 by data-review.sh | ${TODAY} ${NOW}_" >> "$REPORT_FILE"

echo "[$TODAY $NOW] 数据复盘完成 ✅" | tee -a "$LOG_FILE"
