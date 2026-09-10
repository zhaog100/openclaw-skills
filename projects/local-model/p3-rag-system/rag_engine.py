#!/usr/bin/env python3
"""
RAG 检索增强生成引擎 - 小米椒运营知识库
作者：小米椒 🌶️🔥
版本：v1.0
"""

import os
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 配置
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
DEFAULT_MODEL = "qwen2.5:0.5b"
OLLAMA_API = "http://localhost:11434"


@dataclass
class Document:
    """文档数据结构"""
    doc_id: str
    title: str
    content: str
    source: str
    chunks: List[str] = None
    chunk_size: int = 500
    overlap: int = 100


@dataclass
class SearchResult:
    """检索结果"""
    doc_id: str
    title: str
    content: str
    relevance_score: float
    source: str


class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self, knowledge_dir: str = KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self.documents: Dict[str, Document] = {}
        self._load_documents()
    
    def _load_documents(self):
        """加载所有 Markdown 文档"""
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)
            return
        
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.knowledge_dir, filename)
                doc_id = hashlib.md5(filepath.encode()).hexdigest()[:8]
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = self._extract_title(content)
                doc = Document(
                    doc_id=doc_id,
                    title=title,
                    content=content,
                    source=filename,
                    chunks=self._chunk_content(content)
                )
                self.documents[doc_id] = doc
    
    def _extract_title(self, content: str) -> str:
        """从 Markdown 提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return os.path.splitext(os.path.basename(content.split('\n')[0]))[0]
    
    def _chunk_content(self, content: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """将内容分块"""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return self.documents.get(doc_id)
    
    def list_documents(self) -> List[Dict]:
        """列出所有文档"""
        return [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "source": doc.source,
                "chunks": len(doc.chunks) if doc.chunks else 0
            }
            for doc in self.documents.values()
        ]


class SearchEngine:
    """简单关键词检索引擎"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self._build_index()
    
    def _build_index(self):
        """构建关键词索引"""
        self.keyword_index: Dict[str, List[str]] = {}
        for doc_id, doc in self.kb.documents.items():
            for chunk in doc.chunks or []:
                keywords = self._extract_keywords(chunk)
                for kw in keywords:
                    if kw not in self.keyword_index:
                        self.keyword_index[kw] = []
                    self.keyword_index[kw].append(doc_id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词 - 正确分词"""
        # 中文：按单字或词组提取（至少2个连续汉字）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        # 英文单词
        english_words = re.findall(r'[a-zA-Z]{3,}', text)
        # 数字+单位组合
        number_words = re.findall(r'[\d]+[\u4e00-\u9fa5]+', text)
        # 额外拆分：确保长字符串被切分成小片段
        extra_chunks = []
        for i in range(0, len(text)-1, 2):
            chunk = text[i:i+4]
            if len(chunk) >= 2 and all('\u4e00' <= c <= '\u9fa5' for c in chunk):
                extra_chunks.append(chunk)
        return list(set(chinese_words + english_words + number_words + extra_chunks))
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """搜索相关知识 - 改进版：拆分查询关键词"""
        # 拆分查询为更细粒度的关键词
        query_keywords = self._extract_keywords(query)
        # 额外拆分长词（如"小红书爆款标题怎么写" → 小红书, 爆款, 标题）
        query_keywords.extend(re.findall(r'[\u4e00-\u9fa5]{2,4}', query))
        query_keywords = list(set(query_keywords))
        
        score_map: Dict[str, float] = {}
        
        for kw in query_keywords:
            if kw in self.keyword_index:
                for doc_id in self.keyword_index[kw]:
                    score_map[doc_id] = score_map.get(doc_id, 0) + 1
        
        # 计算相关性分数
        results = []
        for doc_id, score in score_map.items():
            doc = self.kb.get_document(doc_id)
            if doc:
                best_chunk = self._find_best_chunk(doc, query)
                results.append(SearchResult(
                    doc_id=doc_id,
                    title=doc.title,
                    content=best_chunk,
                    relevance_score=score,
                    source=doc.source
                ))
        
        # 按分数排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    def _find_best_chunk(self, doc: Document, query: str) -> str:
        """找到与查询最相关的 chunk"""
        best_score = 0
        best_chunk = ""
        query_keywords = set(self._extract_keywords(query))
        
        for chunk in doc.chunks or []:
            chunk_keywords = set(self._extract_keywords(chunk))
            score = len(query_keywords & chunk_keywords)
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        return best_chunk if best_chunk else (doc.chunks[0] if doc.chunks else doc.content[:500])


class RAGEngine:
    """RAG 检索增强生成引擎"""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.kb = KnowledgeBase()
        self.search = SearchEngine(self.kb)
    
    def query(self, question: str, max_context: int = 1500) -> Tuple[str, List[str]]:
        """
        查询问题并返回回答 + 使用的知识来源
        """
        # 1. 检索相关知识
        results = self.search.search(question, top_k=3)
        
        if not results:
            return self._fallback_answer(question), []
        
        # 2. 构建上下文
        context_parts = []
        sources = []
        
        for r in results:
            if len(context_parts) + len(r.content) > max_context:
                break
            context_parts.append(f"【{r.title}】\n{r.content}")
            sources.append(f"{r.title} ({r.source})")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # 3. 构建 Prompt
        prompt = f"""基于以下知识库内容，回答用户问题。

【知识库内容】
{context}

【用户问题】
{question}

【回答要求】
1. 基于知识库内容回答
2. 如果知识库没有相关信息，说明"暂无线索"
3. 给出具体、可操作的建议
4. 用小米椒的口吻回答（活泼、专业）
"""
        
        # 4. 调用 Ollama
        answer = self._call_ollama(prompt)
        
        return answer, sources
    
    def _call_ollama(self, prompt: str) -> str:
        """调用 Ollama API"""
        import requests
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024
            }
        }
        
        try:
            resp = requests.post(
                f"{OLLAMA_API}/api/generate",
                json=payload,
                timeout=120
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
            else:
                return f"API错误: HTTP {resp.status_code}"
        except Exception as e:
            return f"调用失败: {str(e)}"
    
    def _fallback_answer(self, question: str) -> str:
        """降级回答"""
        return f"""关于「{question}」的问题，暂时没有找到相关知识。

建议：
1. 检查知识库是否包含相关内容
2. 尝试用更具体的关键词提问
3. 联系管理员添加相关知识

当前知识库包含：
{len(self.kb.documents)} 个文档
{sum(len(doc.chunks or []) for doc in self.kb.documents.values())} 个知识块"""


def print_usage():
    """打印使用说明"""
    print("""
╔════════════════════════════════════════════════════════╗
║  🌶️ 小米椒 RAG 检索增强系统 v1.0                       ║
║  基于本地知识库的智能问答引擎                          ║
╚════════════════════════════════════════════════════════╝

使用方式:
  python rag_engine.py query "你的问题"
  python rag_engine.py list      列出知识库
  python rag_engine.py add <file> 添加新文档
  python rag_engine.py demo      运行演示

示例问题:
  - 小红书爆款标题怎么写？
  - 数码测评内容怎么规划？
  - 封面设计有什么技巧？
""")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1]
    engine = RAGEngine()
    
    if command == "query":
        if len(sys.argv) < 3:
            print("❌ 请提供问题")
            sys.exit(1)
        question = " ".join(sys.argv[2:])
        print(f"\n🔍 正在检索: {question}\n")
        
        answer, sources = engine.query(question)
        
        print("✅ 回答:\n")
        print(answer)
        print(f"\n📚 参考来源:")
        for src in sources:
            print(f"  • {src}")
    
    elif command == "list":
        docs = engine.kb.list_documents()
        print(f"\n📚 知识库 ({len(docs)} 个文档)\n")
        for doc in docs:
            print(f"  • {doc['title']} ({doc['chunks']} 个知识块)")
        print()
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ 请提供文件路径")
            sys.exit(1)
        filepath = sys.argv[2]
        if os.path.exists(filepath):
            print(f"✅ 已添加: {filepath}")
            print("⚠️ 请重启系统以加载新文档")
        else:
            print(f"❌ 文件不存在: {filepath}")
    
    elif command == "demo":
        print("\n🌶️ 小米椒 RAG 演示系统\n")
        
        questions = [
            "小红书爆款标题怎么写？",
            "数码测评内容怎么规划？",
            "封面设计有什么技巧？",
            "SEO优化要注意什么？"
        ]
        
        for q in questions:
            print(f"\n{'='*50}")
            print(f"Q: {q}")
            print("-"*50)
            answer, sources = engine.query(q)
            print(f"A: {answer[:300]}...")
            print(f"📚 来源: {sources[0] if sources else '无'}")
    
    else:
        print(f"❌ 未知命令: {command}")
        print_usage()


if __name__ == "__main__":
    main()
