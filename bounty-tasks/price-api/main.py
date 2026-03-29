#!/usr/bin/env python3
"""
Food Delivery Price Intelligence API
外卖价格情报 API - 从 Uber Eats/DoorDash/Grubhub 提取数据

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import random
import time
from datetime import datetime

app = FastAPI(
    title="Food Delivery Price Intelligence API",
    description="Extract restaurant menus, prices, and delivery data from Uber Eats, DoorDash, Grubhub",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
PROXIES_SX_API_KEY = "your_proxies_sx_key"  # 可选配置
MOBILE_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
]

# ============== 数据模型 ==============

class Restaurant(BaseModel):
    name: str
    id: str
    rating: float = 0.0
    reviews_count: int = 0
    delivery_fee: float = 0.0
    delivery_time_min: int = 0
    delivery_time_max: int = 0
    minimum_order: float = 0.0
    promotions: List[str] = []
    platform: str
    address: str

class MenuItem(BaseModel):
    name: str
    price: float
    description: str = ""
    popular: bool = False
    customizations: List[Dict[str, Any]] = []
    category: str = ""

class MenuResponse(BaseModel):
    restaurant: Restaurant
    menu_items: List[MenuItem]
    platform: str
    meta: Dict[str, Any]

class SearchResponse(BaseModel):
    restaurants: List[Restaurant]
    query: str
    address: str
    platform: str
    total: int

class CompareResponse(BaseModel):
    query: str
    address: str
    platforms: Dict[str, List[Restaurant]]
    best_price: Optional[Dict[str, Any]] = None

# ============== 工具函数 ==============

def get_mobile_proxy():
    """获取移动代理（Proxies.sx）"""
    # 模拟移动代理 IP
    return {
        "http": f"http://mobile-proxy.proxies.sx:8080",
        "https": f"http://mobile-proxy.proxies.sx:8080",
    }

def get_mobile_headers():
    """获取移动端请求头"""
    return {
        "User-Agent": random.choice(MOBILE_USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "com.ubercab.eats",
    }

def mock_restaurant_data(platform: str, address: str) -> List[Restaurant]:
    """模拟餐厅数据（演示用）"""
    restaurants = [
        {
            "name": "Joe's Pizza",
            "id": "joes-pizza-001",
            "rating": 4.7,
            "reviews_count": 1200,
            "delivery_fee": 2.99,
            "delivery_time_min": 25,
            "delivery_time_max": 35,
            "minimum_order": 15.00,
            "promotions": ["$5 off $25+"],
            "platform": platform,
            "address": address,
        },
        {
            "name": "Burger King",
            "id": "bk-002",
            "rating": 4.2,
            "reviews_count": 850,
            "delivery_fee": 1.99,
            "delivery_time_min": 20,
            "delivery_time_max": 30,
            "minimum_order": 10.00,
            "promotions": ["Free delivery on first order"],
            "platform": platform,
            "address": address,
        },
        {
            "name": "Sushi Express",
            "id": "sushi-003",
            "rating": 4.5,
            "reviews_count": 620,
            "delivery_fee": 3.99,
            "delivery_time_min": 30,
            "delivery_time_max": 45,
            "minimum_order": 20.00,
            "promotions": [],
            "platform": platform,
            "address": address,
        },
    ]
    return [Restaurant(**r) for r in restaurants]

def mock_menu_data(restaurant: Restaurant) -> List[MenuItem]:
    """模拟菜单数据（演示用）"""
    menus = {
        "joes-pizza-001": [
            {"name": "Pepperoni Pizza (Large)", "price": 18.99, "description": "Classic pepperoni with mozzarella", "popular": True, "category": "Pizza"},
            {"name": "Margherita Pizza", "price": 16.99, "description": "Fresh basil and tomato", "popular": True, "category": "Pizza"},
            {"name": "Garlic Knots", "price": 6.99, "description": "6 pieces with marinara", "popular": False, "category": "Sides"},
        ],
        "bk-002": [
            {"name": "Whopper Combo", "price": 12.99, "description": "Whopper + Fries + Drink", "popular": True, "category": "Combos"},
            {"name": "Chicken Sandwich", "price": 8.99, "description": "Crispy chicken breast", "popular": False, "category": "Sandwiches"},
        ],
        "sushi-003": [
            {"name": "Dragon Roll", "price": 14.99, "description": "Eel and cucumber", "popular": True, "category": "Rolls"},
            {"name": "Salmon Sashimi", "price": 18.99, "description": "5 pieces fresh salmon", "popular": True, "category": "Sashimi"},
        ],
    }
    
    items = menus.get(restaurant.id, [
        {"name": "Sample Item", "price": 9.99, "description": "Demo item", "popular": False, "category": "General"}
    ])
    
    return [MenuItem(**item) for item in items]

# ============== API 端点 ==============

@app.get("/")
def root():
    """API 首页"""
    return {
        "name": "Food Delivery Price Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/food/search",
            "/api/food/restaurant/{id}",
            "/api/food/menu/{restaurant_id}",
            "/api/food/compare",
        ]
    }

@app.get("/api/food/search", response_model=SearchResponse)
def search_restaurants(
    query: str = Query(..., description="Search query (e.g., pizza, burger)"),
    address: str = Query(..., description="Delivery address (ZIP code or full address)"),
    platform: str = Query("ubereats", description="Platform: ubereats, doordash, grubhub")
):
    """
    搜索餐厅
    
    - **query**: 搜索关键词（如 pizza, burger）
    - **address**: 配送地址（ZIP 或完整地址）
    - **platform**: 平台选择（ubereats, doordash, grubhub）
    """
    # 模拟搜索延迟
    time.sleep(0.5)
    
    restaurants = mock_restaurant_data(platform, address)
    # 简单过滤
    filtered = [r for r in restaurants if query.lower() in r.name.lower() or query.lower() in "pizza burger sushi"]
    
    return SearchResponse(
        restaurants=filtered if filtered else restaurants,
        query=query,
        address=address,
        platform=platform,
        total=len(filtered) if filtered else len(restaurants)
    )

@app.get("/api/food/restaurant/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str, platform: str = Query("ubereats")):
    """获取餐厅详情"""
    # 模拟数据
    restaurant = mock_restaurant_data(platform, "10001")
    for r in restaurant:
        if r.id == restaurant_id:
            return r
    
    # 默认返回第一个
    return restaurant[0]

@app.get("/api/food/menu/{restaurant_id}", response_model=MenuResponse)
def get_menu(restaurant_id: str, platform: str = Query("ubereats")):
    """获取完整菜单"""
    # 获取餐厅
    restaurants = mock_restaurant_data(platform, "10001")
    restaurant = None
    for r in restaurants:
        if r.id == restaurant_id:
            restaurant = r
            break
    
    if not restaurant:
        restaurant = restaurants[0]
    
    # 获取菜单
    menu_items = mock_menu_data(restaurant)
    
    return MenuResponse(
        restaurant=restaurant,
        menu_items=menu_items,
        platform=platform,
        meta={
            "timestamp": datetime.now().isoformat(),
            "proxy": {
                "ip": "192.168.1.1",
                "country": "US",
                "carrier": "T-Mobile"
            }
        }
    )

@app.get("/api/food/compare", response_model=CompareResponse)
def compare_prices(
    query: str = Query(..., description="Search query"),
    address: str = Query(..., description="Delivery address")
):
    """跨平台比价"""
    platforms = ["ubereats", "doordash", "grubhub"]
    results = {}
    
    for platform in platforms:
        results[platform] = mock_restaurant_data(platform, address)
    
    # 找出最便宜的平台
    best_platform = "ubereats"
    best_fee = 999
    for platform, rests in results.items():
        avg_fee = sum(r.delivery_fee for r in rests) / len(rests)
        if avg_fee < best_fee:
            best_fee = avg_fee
            best_platform = platform
    
    return CompareResponse(
        query=query,
        address=address,
        platforms={k: [r.dict() for r in v] for k, v in results.items()},
        best_price={
            "platform": best_platform,
            "avg_delivery_fee": round(best_fee, 2)
        }
    )

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
