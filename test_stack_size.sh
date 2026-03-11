#!/bin/bash
# 测试增加Node.js栈大小

echo "=== 测试1: 使用默认栈大小 ==="
timeout 10 docker exec qinglong node /ql/scripts/jd_faker2/jd_dailybonus.js 2>&1 | tail -5

echo -e "\n=== 测试2: 增加栈大小到2MB ==="
timeout 10 docker exec qinglong node --stack-size=2048 /ql/scripts/jd_faker2/jd_dailybonus.js 2>&1 | tail -5

echo -e "\n=== 测试3: 增加栈大小到4MB ==="
timeout 10 docker exec qinglong node --stack-size=4096 /ql/scripts/jd_faker2/jd_dailybonus.js 2>&1 | tail -5
