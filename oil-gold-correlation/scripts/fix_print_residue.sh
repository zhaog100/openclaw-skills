#!/bin/bash
# 批量修复石油黄金技能print残留问题

cd /home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts

echo "=== 开始批量修复print残留 ==="

# 定义需要添加logging的文件列表
files=(
    "advisor.py"
    "analysis.py"
    "analyze_history.py"
    "fetch_data.py"
    "geopolitics.py"
    "fetch_fred.py"
    "fetch_alpha_vantage.py"
    "fetch_twelve_data.py"
    "multi_source.py"
    "multi_timeframe_analysis.py"
    "opportunity_scanner.py"
    "report.py"
    "report_text.py"
    "report_text_brief.py"
    "report_text_wrapper.py"
    "report_card.py"
    "visualize.py"
    "history_report.py"
    "send_qq_api.py"
    "send_qq_direct.py"
    "send_qq_gw.py"
    "send_qq_ws.py"
    "test_report.py"
)

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️ 文件不存在: $file"
        continue
    fi
    
    count=$(grep -c "print(" "$file" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
        echo "✅ $file 无print残留"
        continue
    fi
    
    echo "🔄 处理 $file ($count处print)"
    
    # 1. 添加logging导入（在现有import之后）
    if ! grep -q "^import logging" "$file"; then
        # 在第一个import语句后插入
        sed -i '1{/^import /a\import logging\nlogging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")\nlogger = logging.getLogger(__name__)}' "$file"
    fi
    
    # 2. 替换print(为logger.info(
    # 处理简单情况
    sed -i 's/^print(/logger.info(/g' "$file"
    
    echo "  ✅ 已修复"
done

echo ""
echo "=== 修复完成，检查结果 ==="
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        count=$(grep -c "print(" "$file" 2>/dev/null || echo 0)
        echo "$file: $count处print"
    fi
done
