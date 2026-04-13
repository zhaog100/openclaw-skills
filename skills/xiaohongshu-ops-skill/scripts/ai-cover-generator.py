#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI封面图生成脚本
商贸模式：小红书封面自动生成
依赖：image_generate 工具
"""

import os
import sys
import json
from pathlib import Path

# 技能目录
SKILL_DIR = Path(__file__).parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
TEMPLATE_FILE = SKILL_DIR / "examples" / "comerce" / "product-promo-template.md"

def load_template():
    """读取商贸内容模板"""
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ 模板文件不存在: {TEMPLATE_FILE}")
        return None

def generate_cover_prompt(product_name, main_title, sub_title, price_tag):
    """生成封面图提示词"""
    prompt = f"""
小红书封面图生成，用于商贸产品推广

产品: {product_name}
主标题（大字）: {main_title}
副标题（中字）: {sub_title}
标签（小字）: {price_tag}

设计要求:
- 尺寸: 9:16 竖版（1080×1920）
- 布局: 产品图占60%，文字占40%
- 配色: 暖色调（米白/浅粉）
- 主标题: 黑色大字，白色描边，字号最大
- 副标题: 黑色中字，白色描边
- 标签: 小字，底部居中
- 风格: 小红书爆款封面风格
- 质量: 高清，适合移动端展示

不要添加过多装饰元素，保持简洁大气。
"""
    return prompt

def get_product_info(template_content):
    """从模板提取产品信息"""
    product_name = "蒸汽眼罩"
    main_title = "20分钟告别眼疲劳"
    sub_title = "打工人午休神器"
    price_tag = "¥15.9起 | 包邮"
    
    return product_name, main_title, sub_title, price_tag

def create_assets_dir(product_name):
    """创建产品素材目录"""
    product_dir = ASSETS_DIR / f"product-01-{product_name}"
    cover_dir = product_dir / "cover-images"
    
    cover_dir.mkdir(parents=True, exist_ok=True)
    
    return cover_dir

def main():
    """主函数"""
    print("=== AI封面图生成脚本 ===")
    print(f"技能目录: {SKILL_DIR}")
    print(f"模板文件: {TEMPLATE_FILE}")
    
    # 1. 读取模板
    template = load_template()
    if not template:
        sys.exit(1)
    
    # 2. 提取产品信息
    product_name, main_title, sub_title, price_tag = get_product_info(template)
    
    print(f"产品: {product_name}")
    print(f"主标题: {main_title}")
    print(f"副标题: {sub_title}")
    print(f"标签: {price_tag}")
    
    # 3. 创建素材目录
    cover_dir = create_assets_dir(product_name)
    print(f"输出目录: {cover_dir}")
    
    # 4. 生成提示词
    prompt = generate_cover_prompt(product_name, main_title, sub_title, price_tag)
    
    # 5. 输出提示词到文件（供外部调用）
    prompt_file = SKILL_DIR / "cover-prompt.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"提示词已生成: {prompt_file}")
    print("⚠️ 封面图生成需要通过 OpenClaw image_generate 工具调用")
    print("请使用: image_generate --prompt @cover-prompt.txt --size 1080x1920")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
