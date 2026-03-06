#!/usr/bin/env python3

"""
图片内容提取技能 v1.0.0
智能提取图片内容，生成结构化Markdown
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import re
from datetime import datetime

class ImageContentExtractor:
    def __init__(self, config_path: Optional[str] = None):
        """初始化提取器"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.setup()

    def _get_default_config_path(self) -> str:
        """获取默认配置路径"""
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "extractor-config.json"
        )

    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "ocr": {
                "engine": "tesseract",
                "languages": ["chi_sim", "eng"],
                "fallback_to_ai": True
            },
            "preprocessing": {
                "block_height": 2000,
                "overlap_height": 100
            },
            "output": {
                "format": "markdown",
                "add_toc": True,
                "add_metadata": True
            }
        }

    def setup(self):
        """设置OCR引擎"""
        self.ocr_engine = self._setup_ocr_engine()

    def _setup_ocr_engine(self):
        """设置OCR引擎"""
        engine_type = self.config["ocr"]["engine"]

        if engine_type == "tesseract":
            try:
                import pytesseract
                return {"type": "tesseract", "engine": pytesseract}
            except ImportError:
                if self.config["ocr"].get("fallback_to_ai"):
                    return {"type": "ai_vision"}
                else:
                    raise RuntimeError("Tesseract未安装且未启用AI备用")

        return {"type": "ai_vision"}

    def extract_content(self, image_path: str) -> Dict:
        """提取内容主函数"""
        print(f"🚀 开始提取: {image_path}")

        # 1. 预处理图片
        processed_blocks = self._preprocess_image(image_path)

        # 2. OCR识别
        raw_texts = self._ocr_process(processed_blocks)

        # 3. 合并内容
        merged_text = self._merge_texts(raw_texts)

        # 4. 结构分析
        structured_content = self._analyze_structure(merged_text)

        # 5. 生成Markdown
        markdown = self._generate_markdown(structured_content, image_path)

        return {
            "success": True,
            "markdown": markdown,
            "metadata": {
                "source": image_path,
                "extracted_at": datetime.now().isoformat(),
                "blocks_processed": len(processed_blocks)
            }
        }

    def _preprocess_image(self, image_path: str) -> List[str]:
        """图片预处理 - 智能分块"""
        from PIL import Image
        import cv2
        import numpy as np

        img = Image.open(image_path)
        width, height = img.size

        print(f"📊 图片尺寸: {width}x{height}")

        block_height = self.config["preprocessing"]["block_height"]
        overlap = self.config["preprocessing"]["overlap_height"]

        if height <= block_height:
            return [image_path]

        # 分块处理
        blocks = []
        num_blocks = (height - overlap) // (block_height - overlap)

        output_dir = os.path.join(os.path.dirname(image_path), "temp_blocks")
        os.makedirs(output_dir, exist_ok=True)

        for i in range(num_blocks):
            top = i * (block_height - overlap)
            bottom = min(top + block_height, height)

            block = img.crop((0, top, width, bottom))

            # 检测内容边界
            content_bounds = self._detect_content_bounds(np.array(block))
            if content_bounds:
                block = block.crop(content_bounds)

            block_path = os.path.join(output_dir, f"block_{i:03d}.png")
            block.save(block_path)
            blocks.append(block_path)

        print(f"✂️  分块处理: {num_blocks} 块")
        return blocks

    def _detect_content_bounds(self, img_array):
        """检测内容边界"""
        import cv2

        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        coords = cv2.findNonZero(binary)

        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            return (x, y, x + w, y + h)

        return None

    def _ocr_process(self, image_paths: List[str]) -> List[str]:
        """OCR识别"""
        texts = []

        for i, img_path in enumerate(image_paths, 1):
            print(f"🔍 识别块 {i}/{len(image_paths)}")

            if self.ocr_engine["type"] == "tesseract":
                text = self._ocr_tesseract(img_path)
            else:
                text = self._ocr_ai_vision(img_path)

            texts.append(text)

        return texts

    def _ocr_tesseract(self, image_path: str) -> str:
        """Tesseract OCR"""
        try:
            from PIL import Image

            img = Image.open(image_path)
            langs = '+'.join(self.config["ocr"]["languages"])
            text = self.ocr_engine["engine"].image_to_string(img, lang=langs)
            return text.strip()
        except Exception as e:
            print(f"⚠️  Tesseract失败: {e}")
            return ""

    def _ocr_ai_vision(self, image_path: str) -> str:
        """AI视觉识别（备用）"""
        # 这里集成OpenClaw的image工具
        return "[AI视觉识别结果]"

    def _merge_texts(self, texts: List[str]) -> str:
        """智能合并文本"""
        if len(texts) == 1:
            return texts[0]

        overlap_lines = self.config["preprocessing"]["overlap_height"] // 20
        merged = texts[0]

        for i in range(1, len(texts)):
            lines1 = merged.split('\n')
            lines2 = texts[i].split('\n')

            # 查找最佳匹配
            best_match = 0
            for j in range(1, min(len(lines1), len(lines2), overlap_lines * 2) + 1):
                if lines1[-j:] == lines2[:j]:
                    best_match = j

            if best_match > 0:
                merged = '\n'.join(lines1 + lines2[best_match:])
            else:
                merged += '\n\n' + texts[i]

        return merged

    def _analyze_structure(self, text: str) -> Dict:
        """结构分析"""
        lines = text.split('\n')
        structure = {
            "title": "",
            "sections": [],
            "current_section": None
        }

        for line in lines:
            stripped = line.strip()

            # 检测标题
            if self._is_title(stripped):
                if structure["current_section"]:
                    structure["sections"].append(structure["current_section"])

                structure["current_section"] = {
                    "type": "section",
                    "title": stripped,
                    "content": []
                }

                if not structure["title"]:
                    structure["title"] = stripped

            # 检测列表
            elif self._is_list_item(stripped):
                if structure["current_section"]:
                    structure["current_section"]["content"].append({
                        "type": "list_item",
                        "text": stripped
                    })

            # 检测代码块
            elif self._is_code_block(stripped):
                if structure["current_section"]:
                    structure["current_section"]["content"].append({
                        "type": "code",
                        "text": stripped
                    })

            # 普通段落
            elif stripped:
                if structure["current_section"]:
                    structure["current_section"]["content"].append({
                        "type": "paragraph",
                        "text": stripped
                    })

        # 添加最后一个section
        if structure["current_section"]:
            structure["sections"].append(structure["current_section"])

        return structure

    def _is_title(self, line: str) -> bool:
        """判断是否为标题"""
        if not line or len(line) > 50:
            return False

        # 检测数字编号
        if re.match(r'^\d+\.?\s', line):
            return True

        # 检测中文标题特征
        if re.match(r'^[一二三四五六七八九十]+、', line):
            return True

        # 检测全大写
        if line.isupper() and len(line) < 30:
            return True

        return False

    def _is_list_item(self, line: str) -> bool:
        """判断是否为列表项"""
        return line.startswith(('•', '-', '*', '·', '○', '●'))

    def _is_code_block(self, line: str) -> bool:
        """判断是否为代码块"""
        # 简单判断：包含特殊字符
        return bool(re.search(r'[{}\[\]();]', line))

    def _generate_markdown(self, structure: Dict, source_path: str) -> str:
        """生成Markdown"""
        md_lines = []

        # 元数据
        if self.config["output"].get("add_metadata"):
            md_lines.append(f"# {structure['title']}")
            md_lines.append("")
            md_lines.append(f"> 来源: {os.path.basename(source_path)}")
            md_lines.append(f"> 提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            md_lines.append("")

        # 目录
        if self.config["output"].get("add_toc") and len(structure["sections"]) > 3:
            md_lines.append("## 目录")
            md_lines.append("")
            for i, section in enumerate(structure["sections"], 1):
                md_lines.append(f"{i}. [{section['title']}](#{self._slugify(section['title'])})")
            md_lines.append("")

        # 内容
        for section in structure["sections"]:
            md_lines.append(f"## {section['title']}")
            md_lines.append("")

            for item in section["content"]:
                if item["type"] == "paragraph":
                    md_lines.append(item["text"])
                    md_lines.append("")
                elif item["type"] == "list_item":
                    md_lines.append(f"- {item['text'].lstrip('•-*·○● ')}")
                elif item["type"] == "code":
                    md_lines.append(f"```")
                    md_lines.append(item["text"])
                    md_lines.append("```")
                    md_lines.append("")

            md_lines.append("")

        return '\n'.join(md_lines)

    def _slugify(self, text: str) -> str:
        """生成slug"""
        # 简单处理
        return re.sub(r'[^\w\u4e00-\u9fff-]', '-', text.lower()).strip('-')

    def save_to_knowledge_base(self, markdown: str, title: str, category: str = "uncategorized") -> str:
        """保存到知识库"""
        knowledge_dir = os.path.expanduser("~/.openclaw/workspace/knowledge")

        # 创建分类目录
        category_dir = os.path.join(knowledge_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # 生成文件名
        filename = f"{title}.md"
        filepath = os.path.join(category_dir, filename)

        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✅ 已保存到知识库: {filepath}")

        # 更新QMD索引
        self._update_qmd_index()

        return filepath

    def _update_qmd_index(self):
        """更新QMD索引"""
        import subprocess

        try:
            subprocess.run(
                ["qmd", "update"],
                cwd=os.path.expanduser("~/.openclaw/workspace"),
                timeout=60
            )
            print("✅ QMD索引已更新")
        except Exception as e:
            print(f"⚠️  QMD索引更新失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="图片内容提取技能 v1.0.0")
    parser.add_argument("image_path", help="图片路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-k", "--knowledge-base", action="store_true", help="保存到知识库")
    parser.add_argument("-c", "--category", default="uncategorized", help="知识库分类")
    parser.add_argument("-t", "--title", help="文档标题")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 提取内容
    extractor = ImageContentExtractor()
    result = extractor.extract_content(args.image_path)

    if not result["success"]:
        print("❌ 提取失败")
        return 1

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result["markdown"])
        print(f"✅ 已保存: {args.output}")

    elif args.knowledge_base:
        title = args.title or os.path.splitext(os.path.basename(args.image_path))[0]
        extractor.save_to_knowledge_base(result["markdown"], title, args.category)

    if args.verbose:
        print("\n" + "=" * 40)
        print(result["markdown"])

    return 0

if __name__ == "__main__":
    sys.exit(main())
