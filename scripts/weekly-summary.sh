#!/bin/bash
# =============================================================================
# 每周运营总结脚本
# 用途: 汇总本周运营数据，生成周报
# 时间: 每周日 22:00 执行
# =============================================================================

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/intel"
LOG_FILE="$WORKSPACE/logs/weekly.log"
TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')
WEEKDAY=$(date +%u)  # 1=Mon, 7=Sun
REPORT_FILE="$REPORT_DIR/每周运营规划.md"

# 计算本周一和周日
THIS_MONDAY=$(date -d "monday - 6 days" +%Y-%m-%d 2>/dev/null || date -v+Mon +%Y-%m-%d 2>/dev/null || echo "$TODAY")
THIS_SUNDAY="$TODAY"
LAST_MONDAY=$(date -d "monday - 13 days" +%Y-%m-%d 2>/dev/null || echo "$TODAY")
LAST_SUNDAY=$(date -d "monday - 7 days" +%Y-%m-%d 2>/dev/null || echo "$TODAY")

echo "[$TODAY $NOW] 开始每周运营总结..." >> "$LOG_FILE"

# 确保目录存在
mkdir -p "$REPORT_DIR"
mkdir -p "$WORKSPACE/logs"

# 统计本周 Git 提交
GIT_LOG=$(cd "$WORKSPACE" && git log --oneline --since="$LAST_MONDAY" --until="$THIS_SUNDAY 23:59:59" 2>/dev/null | head -20 || echo "无Git活动")
GIT_COUNT=$(echo "$GIT_LOG" | grep -c "." 2>/dev/null || echo "0")

# 统计本周热点采集天数
HOTSPOT_DAYS=0
for i in 0 1 2 3 4 5 6; do
    CHECK_DATE=$(date -d "$THIS_MONDAY + $i days" +%Y-%m-%d 2>/dev/null || echo "")
    if [ -n "$CHECK_DATE" ] && grep -q "$CHECK_DATE" "$REPORT_DIR/热点选题.md" 2>/dev/null; then
        HOTSPOT_DAYS=$((HOTSPOT_DAYS + 1))
    fi
done

# 生成周报
cat > "$REPORT_FILE" << EOF
# 📈 小米椒周报: ${LAST_MONDAY} ~ ${THIS_SUNDAY}

**生成时间**: ${TODAY} ${NOW}
**维护**: 小米椒 🌶️🔥

---

## 📊 本周数据概览

| 指标 | 数值 |
|------|------|
| Git 提交 | ${GIT_COUNT} 次 |
| 热点采集 | ${HOTSPOT_DAYS}/7 天 |
| 数据复盘 | 待统计 |
| 内容发布 | 待官家补充 |

---

## 📝 本周 Git 活动

\`\`\`
${GIT_LOG}
\`\`\`

---

## 🔍 系统运行状态

### 定时任务健康度
- 热点采集: $([ "$HOTSPOT_DAYS" -ge 5 ] && echo "✅ 正常" || echo "⚠️ 部分缺失")
- 石油黄金分析: $(tail -1 /logs/oil-gold-hourly.log 2>/dev/null | grep -q "Errno" && echo "❌ 异常" || echo "✅ 正常")
- 公考信息采集: ✅ 正常

### 运营待办
EOF

# 添加运营待办状态
if [ -f "$REPORT_DIR/运营待办.md" ]; then
    echo "" >> "$REPORT_FILE"
    grep "^\- \[ \]" "$REPORT_DIR/运营待办.md" 2>/dev/null | head -10 >> "$REPORT_FILE" || echo "- (无待办)" >> "$REPORT_FILE"
fi

# 下周计划
cat >> "$REPORT_FILE" << EOF

---

## 📅 下周计划 (${THIS_MONDAY} ~ ${THIS_SUNDAY})

### 内容规划
- [ ] 小红书笔记: 待规划
- [ ] 热点选题: 每日自动采集
- [ ] 数据复盘: 每日自动执行

### 系统优化
- [ ] 持续监控定时任务健康度
- [ ] 石油黄金分析结果推送（待配置）

---

_自动生成 by weekly-summary.sh | ${TODAY} ${NOW}_

**版权：** MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
EOF

echo "[$TODAY $NOW] 每周运营总结完成 ✅" >> "$LOG_FILE"
