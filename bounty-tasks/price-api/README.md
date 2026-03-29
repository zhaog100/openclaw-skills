# Food Delivery Price Intelligence API

外卖价格情报 API - 从 Uber Eats/DoorDash/Grubhub 提取餐厅菜单和价格数据

## 功能特性

- ✅ 餐厅搜索（按关键词 + 地址）
- ✅ 菜单提取（完整菜品 + 价格）
- ✅ 跨平台比价（Uber Eats vs DoorDash）
- ✅ 移动代理支持（Proxies.sx）
- ✅ 实时配送费/时间估算

## API 端点

```
GET /api/food/search?query=pizza&address=10001&platform=ubereats
GET /api/food/restaurant/:id?platform=ubereats
GET /api/food/menu/:restaurant_id?platform=ubereats
GET /api/food/compare?query=pizza&address=10001
```

## 快速开始

```bash
# 安装依赖
pip install fastapi uvicorn requests

# 启动服务
python main.py

# 测试
curl "http://localhost:8000/api/food/search?query=pizza&address=10001"
```

## 定价

- $0.01 USDC / 餐厅搜索
- $0.02 USDC / 完整菜单提取
- $0.03 USDC / 跨平台比价

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
