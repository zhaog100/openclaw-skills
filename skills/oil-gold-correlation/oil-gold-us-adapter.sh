# oil-gold-us-adapter.sh
# 自动判断美股夏/冬令时，动态调整推送时间
# 夏令时(3月第2周日~11月第1周日): 美股21:30开盘 → cron 23:00直接推送
# 冬令时(11月第1周日~3月第2周日): 美股22:30开盘 → 需延迟到00:00推送
#
# 用法: 由 cron 在 23:00 触发，脚本判断是否需要等待

month=$(date +%m)
day=$(date +%d)

is_dst=0
if [ "$month" -ge 3 ] && [ "$month" -le 10 ]; then
    is_dst=1
elif [ "$month" -eq 11 ] && [ "$day" -le 7 ]; then
    is_dst=1
elif [ "$month" -eq 3 ] && [ "$day" -ge 8 ]; then
    is_dst=1
fi

if [ "$is_dst" -eq 0 ]; then
    # 冬令时，美股22:30才开盘，等待60分钟后执行（23:00→00:00）
    echo "[oil-gold-us] 冬令时，等待60分钟后执行..."
    sleep 3600
fi

python3 /root/.openclaw/workspace/skills/oil-gold-correlation/scripts/report_text.py

