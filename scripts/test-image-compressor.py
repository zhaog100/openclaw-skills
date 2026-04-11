#!/usr/bin/env python3
"""
Image Compressor API 测试脚本
智能压缩、转换、优化图片
"""

import os
import requests
import base64
from pathlib import Path

# API配置（需要从官家获取）
API_URL = "https://api.yourdomain.com/image-compressor/v1/compress.php"
API_KEY = os.environ.get("IMAGE_COMPRESSOR_API_KEY", "")
RETURN_FORMAT = "json"  # json, file, base64

# 测试配置
INPUT_DIR = "products/raw"
OUTPUT_DIR = "products/compressed"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("=" * 60)
print("Image Compressor API 测试 - 智能压缩转换")
print("=" * 60)
print()

if not API_KEY:
    print("⚠️  API Key未配置")
    print("   请设置环境变量: IMAGE_COMPRESSOR_API_KEY")
    print("   或修改脚本直接填入API Key")
    exit(1)

# ========== 测试场景1：小红书图片压缩 ==========
print("场景1：小红书图片压缩（9:16竖版）")
print("-" * 60)

test_image = "xiaohongshu_test.jpg"

if os.path.exists(test_image):
    print(f"📤 测试图片: {test_image}")
    print(f"🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")

    # 基础压缩（WebP格式，quality=80）
    print("⏳ 测试1：基础压缩（WebP, quality=80）")
    files = {
        'image': open(test_image, 'rb'),
        'format': 'webp',
        'quality': '80'
    }

    response = requests.post(f"{API_URL}?format=webp&quality=80", files=files, timeout=30)
    response.raise_for_status()

    result = response.json()
    
    if result['ok']:
        output_path = os.path.join(OUTPUT_DIR, "compressed_basic.webp")
        
        # 保存base64图片
        image_data = base64.b64decode(result['file_base64'])
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        original_size = result['meta']['input']['size_bytes']
        compressed_size = result['meta']['output']['size_bytes']
        compression = result['meta']['output']['compression_percent']
        
        print(f"✅ 成功！")
        print(f"📁 输出文件: {output_path}")
        print(f"📊 原始大小: {original_size / 1024:.1f} KB")
        print(f"📊 压缩后: {compressed_size / 1024:.1f} KB")
        print(f"📉 压缩率: {compression:.1f}%")
    else:
        print(f"❌ 错误: {result.get('error', 'Unknown error')}")
        print(f"   响应: {result}")
else:
    print(f"⚠️  测试图片不存在: {test_image}")
    print("   请准备一张测试图片")
    print("   或使用现有图片: products/raw/xiaohongshu_test.jpg")

print()

# ========== 测试场景2：固定宽度压缩 ==========
print()
print("场景2：固定宽度压缩（width=1080，保持比例）")
print("-" * 60)

if os.path.exists(test_image):
    print(f"📤 测试图片: {test_image}")
    print("⏳ 测试2：固定宽度（1080px）")
    
    # 固定宽度1080，保持比例，WebP格式
    files = {
        'image': open(test_image, 'rb'),
        'max_width': '1080',
        'format': 'webp'
    }
    
    response = requests.post(f"{API_URL}?max_width=1080&format=webp", files=files, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    
    if result['ok']:
        output_path = os.path.join(OUTPUT_DIR, "compressed_fixed_1080.webp")
        image_data = base64.b64decode(result['file_base64'])
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        original_size = result['meta']['input']['size_bytes']
        compressed_size = result['meta']['output']['size_bytes']
        compression = result['meta']['output']['compression_percent']
        
        print(f"✅ 成功！")
        print(f"📁 输出文件: {output_path}")
        print(f"📊 原始大小: {original_size / 1024:.1f} KB")
        print(f"📊 压缩后: {compressed_size / 1024:.1f} KB")
        print(f"📉 压缩率: {compression:.1f}%")
    else:
        print(f"❌ 错误: {result.get('error', 'Unknown error')}")

print()
print("=" * 60)
print("测试完成！")
print(f"📁 输出目录: {OUTPUT_DIR}")
print("=" * 60)
print()

# ========== 使用说明 ==========
print()
print("🔑 API Key获取：")
print("   1. 访问: https://rapidapi.com/vintarok-vintarok-default/api/smart-adaptive-ultra-fast-image-compressor-converter")
print("   2. 注册账户")
print("   3. 查找API密钥（在API Keys或Dashboard）")
print("   4. 复制API Key（以sk_开头）")
print("   5. 设置环境变量: export IMAGE_COMPRESSOR_API_KEY='sk_...'（仅本次会话有效）")
print()
print("📋 参数参考：")
print("   quality: 0-100（默认82，值越小文件越小）")
print("   max_width: 最大输出宽度（像素），留空保持原宽")
print("   max_height: 最大输出高度（像素），留空保持原高")
print("   format: auto/jpeg/png/webp（auto推荐WebP）")
print("   mode: fit（等比缩放）/fill（填）/stretch（拉伸）")
print("=" * 60)
