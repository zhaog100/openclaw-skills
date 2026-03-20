#!/bin/bash
# Price Intelligence API 测试脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

BASE_URL="http://localhost:8000"

echo "=== Price Intelligence API 测试 ==="
echo ""

# 1. 健康检查
echo "1. 健康检查..."
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. 搜索餐厅
echo "2. 搜索餐厅 (pizza, 10001)..."
curl -s "$BASE_URL/api/food/search?query=pizza&address=10001&platform=ubereats" | jq '.restaurants | length'
echo ""

# 3. 获取餐厅详情
echo "3. 获取餐厅详情..."
curl -s "$BASE_URL/api/food/restaurant/joes-pizza-001?platform=ubereats" | jq '.name, .rating'
echo ""

# 4. 获取菜单
echo "4. 获取完整菜单..."
curl -s "$BASE_URL/api/food/menu/joes-pizza-001?platform=ubereats" | jq '.menu_items | length'
echo ""

# 5. 跨平台比价
echo "5. 跨平台比价..."
curl -s "$BASE_URL/api/food/compare?query=pizza&address=10001" | jq '.best_price'
echo ""

echo "=== 测试完成 ==="
