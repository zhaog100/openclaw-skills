#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品素材管理脚本
商贸模式：按产品分类管理素材，AI生成封面图
"""

import os
import sys
from pathlib import Path

# 技能目录
SKILL_DIR = Path(__file__).parent.parent
ASSETS_DIR = SKILL_DIR / "assets"

def create_asset_structure(product_name):
    """创建产品素材目录结构"""
    product_dir = ASSETS_DIR / f"product-01-{product_name}"
    
    # 创建子目录
    subdirs = {
        'cover-images': '封面图',
        'detail-images': '详情图',
        'real-shot': '实拍图',
        'user-reviews': '买家秀'
    }
    
    created_dirs = []
    for dir_name, desc in subdirs.items():
        dir_path = product_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(dir_path)
    
    return product_dir, created_dirs

def pack_assets(product_name):
    """打包素材"""
    product_dir = ASSETS_DIR / f"product-01-{product_name}"
    
    if not product_dir.exists():
        logger.warning(f"产品目录不存在: {product_dir}")
        return None
    
    # 查找所有图片文件
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(product_dir.rglob(ext))
    
    if not image_files:
        logger.warning(f"未找到图片文件: {product_dir}")
        return None
    
    # 输出素材清单
    logger.info(f"产品素材清单（{product_name}）")
    
    # 分类统计
    cover_count = len(list((product_dir / 'cover-images').glob('*')))
    detail_count = len(list((product_dir / 'detail-images').glob('*')))
    real_count = len(list((product_dir / 'real-shot').glob('*')))
    review_count = len(list((product_dir / 'user-reviews').glob('*')))
    
    logger.info(f"封面图: {cover_count}个")
    logger.info(f"详情图: {detail_count}个")
    logger.info(f"实拍图: {real_count}个")
    logger.info(f"买家秀: {review_count}个")
    logger.info(f"总计: {len(image_files)}个")
    
    # 推荐使用
    if cover_count > 0 and detail_count > 0:
        logger.info(f"\n推荐使用: 最新封面图 + 1-2张详情图")
    
    return len(image_files)

def list_assets(product_name):
    """列出素材"""
    product_dir = ASSETS_DIR / f"product-01-{product_name}"
    
    if not product_dir.exists():
        logger.warning(f"产品目录不存在: {product_dir}")
        return None
    
    logger.info(f"=== 产品素材（{product_name}）===")
    
    # 分类列出
    subdirs = ['cover-images', 'detail-images', 'real-shot', 'user-reviews']
    
    for subdir in subdirs:
        dir_path = product_dir / subdir
        if dir_path.exists():
            files = list(dir_path.glob('*'))
            logger.info(f"\n{subdir}/")
            for f in files[:5]:  # 只显示前5个
                logger.info(f"  {f.name}")
            if len(files) > 5:
                logger.info(f"  ...（共{len(files)}个文件）")
    
    return True

def main():
    """主函数"""
    logger.info("=== 产品素材管理脚本 ===")
    
    if len(sys.argv) < 2:
        logger.info("用法: python3 scripts/asset-manager.py --action <action> --product <product>")
        logger.info("action: create|pack|list")
        logger.info("product: steam-eye-mask|neck-massager|herbal-tea")
        return 1
    
    action = sys.argv[1]
    if action != '--action':
        logger.error("❌ 错误参数")
        return 1
    
    action_value = sys.argv[2]
    if sys.argv[3] != '--product':
        logger.error("❌ 错误参数")
        return 1
    
    product_name = sys.argv[4]
    
    if action_value == 'create':
        logger.info(f"创建素材目录结构: {product_name}")
        product_dir, created_dirs = create_asset_structure(product_name)
        logger.info(f"✅ 已创建: {product_dir}")
        logger.info(f"子目录: {len(created_dirs)}个")
    
    elif action_value == 'pack':
        logger.info(f"打包素材: {product_name}")
        count = pack_assets(product_name)
        if count:
            logger.info(f"✅ 共{count}个文件")
    
    elif action_value == 'list':
        logger.info(f"列出素材: {product_name}")
        list_assets(product_name)
    
    else:
        logger.error(f"❌ 未知操作: {action_value}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
