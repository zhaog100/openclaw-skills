#!/usr/bin/env python3

"""
Image Content Extractor v2.0 - Unified Version
统一图片内容提取技能
支持模式：terminal（终端）、document（文档）、general（通用）
"""

import json
import os
import sys
import argparse
import tempfile
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# 技能根目录
SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
CONFIG_EXAMPLE = SKILL_DIR / "config.example.json"

# 添加core和modes到路径
sys.path.insert(0, str(SKILL_DIR))

from core import OCREngine, ImagePreprocessor, ContentMerger, StructureAnalyzer
from modes.terminal import TerminalMode
from modes.document import DocumentMode
from modes.general import GeneralMode


def _env(key: str, default: object = None) -> object:
    """读取环境变量，支持 JSON 值"""
    val = os.environ.get(f"ICE_{key}")  # ICE = Image Content Extractor
    if val is None:
        return default
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return val


class ImageContentExtractor:
    """统一图片内容提取器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ocr = OCREngine(self.config.get("ocr"))
        self.preprocessor = ImagePreprocessor(self.config.get("preprocessing"))
        self.merger = ContentMerger(self.config.get("preprocessing", {}).get("overlap_height", 100))
        self.analyzer = StructureAnalyzer(self.config.get("structure_detection"))
        self.terminal_mode = TerminalMode()
        self.document_mode = DocumentMode()
        self.general_mode = GeneralMode()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置：指定路径 > config.json > config.example.json > 默认"""
        if config_path is None:
            config_path = os.environ.get("ICE_CONFIG_PATH")

        # 按优先级尝试
        candidates = []
        if config_path:
            candidates.append(Path(config_path))
        candidates.extend([CONFIG_FILE, CONFIG_EXAMPLE])

        for p in candidates:
            if p and p.is_file():
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

        return self._get_default_config()

    def _get_default_config(self) -> Dict:
        return {
            "ocr": {
                "engine": _env("OCR_ENGINE", "tesseract"),
                "languages": _env("OCR_LANGUAGES", ["chi_sim", "eng"]),
                "fallback_to_ai": _env("OCR_FALLBACK_AI", True),
            },
            "preprocessing": {
                "block_height": _env("BLOCK_HEIGHT", 2000),
                "overlap_height": _env("OVERLAP_HEIGHT", 100),
            },
            "output": {
                "format": "markdown",
                "add_metadata": True,
                "add_toc": True,
            },
        }

    def extract(self, image_path: str, mode: str = "auto") -> Dict:
        print(f"🚀 开始提取: {image_path}")

        if not os.path.exists(image_path):
            return {"success": False, "error": f"文件不存在: {image_path}"}

        if mode == "auto":
            mode = self._detect_mode(image_path)
            print(f"🔍 检测模式: {mode}")

        # 1. 预处理
        print("📋 预处理图片...")
        processed_blocks = self.preprocessor.preprocess(image_path, mode)

        # 2. OCR识别
        print(f"🔍 OCR识别 ({len(processed_blocks)} 块)...")
        ocr_results = []
        for i, block_path in enumerate(processed_blocks, 1):
            print(f"   识别块 {i}/{len(processed_blocks)}")
            result = self.ocr.recognize(block_path, mode)
            ocr_results.append(result)

        # 3. 合并内容
        print("🔗 合并内容...")
        merged = self.merger.merge_with_confidence(ocr_results)
        if not merged["success"]:
            return merged

        # 4. 结构分析
        print("📊 分析结构...")
        structure = self.analyzer.analyze(merged["text"], mode)

        # 5. 生成Markdown
        print("📝 生成Markdown...")
        markdown = self.analyzer.to_markdown(
            structure,
            add_metadata=self.config["output"].get("add_metadata", True),
            add_toc=self.config["output"].get("add_toc", True),
        )

        # 6. 模式特定后处理
        if mode == "terminal":
            markdown = self.terminal_mode.post_process(markdown)
        elif mode == "document":
            markdown = self.document_mode.post_process(markdown)

        print("✅ 提取完成！")

        return {
            "success": True,
            "markdown": markdown,
            "structure": structure,
            "metadata": {
                "source": image_path,
                "mode": mode,
                "extracted_at": datetime.now().isoformat(),
                "blocks_processed": len(processed_blocks),
                "confidence": merged["confidence"],
            },
        }

    def _detect_mode(self, image_path: str) -> str:
        import cv2
        import numpy as np
        from PIL import Image

        img = Image.open(image_path)
        img_array = np.array(img)

        if self.terminal_mode.is_terminal(img_array):
            return "terminal"
        if self.document_mode.is_document(img_array):
            return "document"
        return "general"

    def save_to_knowledge_base(self, markdown: str, title: str, category: str = "uncategorized") -> str:
        # 知识库路径：环境变量 > 配置 > 相对于workspace
        kb_root = _env("KB_PATH") or os.environ.get("OPENCLAW_WORKSPACE",
                   str(SKILL_DIR.parent.parent))
        knowledge_dir = os.path.join(kb_root, "knowledge")

        category_dir = os.path.join(knowledge_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        filename = f"{title}.md"
        filepath = os.path.join(category_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✅ 已保存到知识库: {filepath}")
        self._update_qmd_index(kb_root)
        return filepath

    def _update_qmd_index(self, workspace: str):
        import subprocess
        try:
            subprocess.run(["qmd", "update"], cwd=workspace, timeout=60, capture_output=True)
            print("✅ QMD索引已更新")
        except Exception as e:
            print(f"⚠️  QMD索引更新失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Image Content Extractor v2.0 - 统一图片内容提取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 extract.py /path/to/image.png
  python3 extract.py /path/to/terminal.png --mode terminal
  python3 extract.py /path/to/image.png -k -c testing -t "测试用例设计"
  python3 extract.py /path/to/images/ --batch
        """,
    )

    parser.add_argument("image_path", help="图片路径或目录（批量模式）")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-m", "--mode", choices=["auto", "terminal", "document", "general"], default="auto", help="提取模式（默认：auto）")
    parser.add_argument("-k", "--knowledge-base", action="store_true", help="保存到知识库")
    parser.add_argument("-c", "--category", default="uncategorized", help="知识库分类")
    parser.add_argument("-t", "--title", help="文档标题")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--batch", action="store_true", help="批量处理模式")
    parser.add_argument("--config", help="自定义配置文件路径")

    args = parser.parse_args()
    extractor = ImageContentExtractor(config_path=args.config)

    if args.batch:
        if not os.path.isdir(args.image_path):
            print("❌ 批量模式需要指定目录")
            return 1

        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        image_files = sorted(f for f in os.listdir(args.image_path) if os.path.splitext(f)[1].lower() in extensions)
        print(f"📦 批量处理: {len(image_files)} 个文件")

        for i, img_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] {img_file}")
            img_path = os.path.join(args.image_path, img_file)
            result = extractor.extract(img_path, args.mode)

            if result["success"] and args.knowledge_base:
                title = args.title or os.path.splitext(img_file)[0]
                extractor.save_to_knowledge_base(result["markdown"], title, args.category)

        print(f"\n✅ 批量处理完成！共 {len(image_files)} 个文件")
        return 0

    # 单文件处理
    result = extractor.extract(args.image_path, args.mode)
    if not result["success"]:
        print(f"❌ 提取失败: {result.get('error', '未知错误')}")
        return 1

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result["markdown"])
        print(f"✅ 已保存: {args.output}")
    elif args.knowledge_base:
        title = args.title or os.path.splitext(os.path.basename(args.image_path))[0]
        extractor.save_to_knowledge_base(result["markdown"], title, args.category)

    if args.verbose:
        print("\n" + "=" * 50)
        print("📄 提取结果:")
        print("=" * 50)
        print(result["markdown"])
        print("\n" + "=" * 50)
        print(f"📊 统计:")
        print(f"   模式: {result['metadata']['mode']}")
        print(f"   块数: {result['metadata']['blocks_processed']}")
        print(f"   置信度: {result['metadata']['confidence']:.1%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
