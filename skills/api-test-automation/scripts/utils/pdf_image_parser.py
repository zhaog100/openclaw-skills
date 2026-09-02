# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

"""PDF/Image 文档解析器

支持：
- PDF 文本提取（PyMuPDF / pdfplumber）
- 图片 OCR（tesseract / 阿里云 OCR API）
- 降级策略：优先本地，无依赖则返回空并告警
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("api_test.pdf_image_parser")


class PdfImageParser:
    """PDF 和图片文档解析器"""

    def __init__(self, ocr_api_key: str = "", ocr_api_secret: str = ""):
        self.ocr_api_key = ocr_api_key
        self.ocr_api_secret = ocr_api_secret
        self._pdf_backend = self._detect_pdf_backend()
        self._ocr_backend = self._detect_ocr_backend()

    def _detect_pdf_backend(self) -> Optional[str]:
        """检测可用的 PDF 解析后端"""
        try:
            import fitz  # PyMuPDF
            return "pymupdf"
        except ImportError:
            pass
        try:
            import pdfplumber
            return "pdfplumber"
        except ImportError:
            pass
        logger.warning("未安装 PyMuPDF 或 pdfplumber，PDF 解析不可用")
        return None

    def _detect_ocr_backend(self) -> Optional[str]:
        """检测可用的 OCR 后端"""
        if self.ocr_api_key and self.ocr_api_secret:
            return "aliyun"
        try:
            import pytesseract
            return "tesseract"
        except ImportError:
            pass
        try:
            from PIL import Image
            return "pillow"
        except ImportError:
            pass
        logger.warning("未配置 OCR API 密钥，图片 OCR 不可用")
        return None

    def parse_pdf(self, filepath: str) -> str:
        """
        从 PDF 文件提取文本

        Args:
            filepath: PDF 文件路径

        Returns:
            提取的纯文本
        """
        if not self._pdf_backend:
            raise RuntimeError("PDF 解析后端不可用，请安装 pymupdf 或 pdfplumber")

        content = Path(filepath).read_bytes()

        if self._pdf_backend == "pymupdf":
            return self._parse_pymupdf(content)
        elif self._pdf_backend == "pdfplumber":
            return self._parse_pdfplumber(content)

    def _parse_pymupdf(self, content: bytes) -> str:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        texts = []
        for page in doc:
            texts.append(page.get_text())
        doc.close()
        return "\n".join(texts)

    def _parse_pdfplumber(self, content: bytes) -> str:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            texts = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(texts)

    def parse_image(self, filepath: str) -> str:
        """
        从图片文件提取文本（OCR）

        Args:
            filepath: 图片文件路径（PNG/JPG/BMP 等）

        Returns:
            提取的纯文本
        """
        if not self._ocr_backend:
            raise RuntimeError("OCR 后端不可用，请安装 pytesseract 或配置 OCR API")

        if self._ocr_backend == "tesseract":
            return self._ocr_tesseract(filepath)
        elif self._ocr_backend == "aliyun":
            return self._ocr_aliyun(filepath)
        elif self._ocr_backend == "pillow":
            return self._ocr_pillow(filepath)

    def _ocr_tesseract(self, filepath: str) -> str:
        import pytesseract
        return pytesseract.image_to_string(Path(filepath), lang="chi_sim+eng")

    def _ocr_aliyun(self, filepath: str) -> str:
        """阿里云 OCR API 调用"""
        import httpx
        with open(filepath, "rb") as f:
            image_data = f.read()

        resp = httpx.post(
            "https://ocr-api.aliyuncs.com/recognize",
            headers={
                "Authorization": f"APPCODE {self.ocr_api_key}",
                "X-Ca-Secret-Token": self.ocr_api_secret,
            },
            data={"image": image_data.hex(), "type": "general"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("text", "")

    def _ocr_pillow(self, filepath: str) -> str:
        """Pillow 基础 OCR（无文字识别，仅返回元数据）"""
        from PIL import Image
        img = Image.open(filepath)
        return f"[图片: {img.size[0]}x{img.size[1]}, mode={img.mode}]"
