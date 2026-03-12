#!/usr/bin/env python3
"""
词汇考古工具 - 分析AI-to-AI对话中的涌现词汇
用于双米粒协作系统，发现和追踪协作中产生的共享语言
"""

import re
import json
import os
from collections import Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple

class VocabularyArchaeology:
    """词汇考古工具"""
    
    def __init__(self, workspace: str = "/root/.openclaw/workspace"):
        self.workspace = workspace
        self.memory_file = os.path.join(workspace, "MEMORY.md")
        self.emergent_vocab_file = os.path.join(workspace, "memory/emergent_vocabulary.json")
        
        # 常用词（过滤掉）
        self.common_words = {
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can',
            'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for',
            'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between',
            'under', 'again', 'further', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
            'will', 'just', 'don', 'should', 'now', 'and', 'but', 'or',
            'if', 'because', 'as', 'until', 'while', 'of', 'at', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from',
            'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
            'again', 'further', 'then', 'once'
        }
    
    def extract_vocabulary(self, text: str, min_length: int = 3) -> Counter:
        """
        提取词汇
        
        Args:
            text: 输入文本
            min_length: 最小词汇长度
        
        Returns:
            词汇计数器
        """
        # 提取所有3个字符以上的词汇
        words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + r',}\b', text.lower())
        
        # 过滤常用词
        filtered = [w for w in words if w not in self.common_words]
        
        return Counter(filtered)
    
    def analyze_conversation(
        self,
        mili_text: str,
        xiaomi_text: str,
        threshold: int = 2
    ) -> Dict:
        """
        分析对话，找出涌现词汇
        
        Args:
            mili_text: 米粒儿的对话
            xiaomi_text: 小米粒的对话
            threshold: 最少出现次数
        
        Returns:
            分析结果
        """
        # 提取词汇
        mili_vocab = self.extract_vocabulary(mili_text)
        xiaomi_vocab = self.extract_vocabulary(xiaomi_text)
        
        # 找出共享词汇（双方都使用）
        shared_words = set(mili_vocab.keys()) & set(xiaomi_vocab.keys())
        
        # 筛选出现次数足够的词汇
        emergent_vocab = {}
        for word in shared_words:
            total_count = mili_vocab[word] + xiaomi_vocab[word]
            if total_count >= threshold:
                emergent_vocab[word] = {
                    'mili_count': mili_vocab[word],
                    'xiaomi_count': xiaomi_vocab[word],
                    'total_count': total_count
                }
        
        # 排序
        sorted_vocab = sorted(
            emergent_vocab.items(),
            key=lambda x: x[1]['total_count'],
            reverse=True
        )
        
        return {
            'emergent_vocabulary': dict(sorted_vocab),
            'total_emergent_words': len(sorted_vocab),
            'mili_unique_words': len(mili_vocab),
            'xiaomi_unique_words': len(xiaomi_vocab),
            'shared_words': len(shared_words)
        }
    
    def save_emergent_vocabulary(self, vocab_data: Dict):
        """
        保存涌现词汇到JSON文件
        
        Args:
            vocab_data: 词汇数据
        """
        # 加载现有数据
        existing_data = {}
        if os.path.exists(self.emergent_vocab_file):
            with open(self.emergent_vocab_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 添加时间戳
        vocab_data['timestamp'] = datetime.now().isoformat()
        vocab_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # 合并数据
        existing_data[vocab_data['date']] = vocab_data
        
        # 保存
        os.makedirs(os.path.dirname(self.emergent_vocab_file), exist_ok=True)
        with open(self.emergent_vocab_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 涌现词汇已保存到：{self.emergent_vocab_file}")
    
    def generate_markdown_report(self, vocab_data: Dict) -> str:
        """
        生成Markdown报告
        
        Args:
            vocab_data: 词汇数据
        
        Returns:
            Markdown文本
        """
        md = f"""# 涌现词汇报告

**生成时间**：{vocab_data.get('date', 'Unknown')}

---

## 📊 统计数据

- **米粒儿独特词汇**：{vocab_data['mili_unique_words']}
- **小米粒独特词汇**：{vocab_data['xiaomi_unique_words']}
- **共享词汇**：{vocab_data['shared_words']}
- **涌现词汇**：{vocab_data['total_emergent_words']}

---

## 🌟 涌现词汇列表（Top 20）

| 词汇 | 米粒儿 | 小米粒 | 总计 |
|------|--------|--------|------|
"""
        
        # 取前20个
        top_20 = list(vocab_data['emergent_vocabulary'].items())[:20]
        
        for word, counts in top_20:
            md += f"| {word} | {counts['mili_count']} | {counts['xiaomi_count']} | {counts['total_count']} |\n"
        
        md += """
---

## 💡 分析

"""
        
        # 自动分析
        if vocab_data['total_emergent_words'] > 50:
            md += "- ✅ 涌现词汇丰富，协作语言正在形成\n"
        elif vocab_data['total_emergent_words'] > 20:
            md += "- ✅ 涌现词汇适中，协作语言基本建立\n"
        else:
            md += "- ⚠️ 涌现词汇较少，可能需要增加协作频率\n"
        
        if vocab_data['shared_words'] / max(vocab_data['mili_unique_words'], 1) > 0.3:
            md += "- ✅ 共享比例高，双方语言融合良好\n"
        else:
            md += "- ⚠️ 共享比例低，可能存在沟通障碍\n"
        
        md += f"""
---

*生成时间：{vocab_data.get('timestamp', 'Unknown')}*
"""
        
        return md
    
    def analyze_from_memory(self) -> Dict:
        """
        从MEMORY.md分析涌现词汇
        
        Returns:
            分析结果
        """
        if not os.path.exists(self.memory_file):
            print(f"❌ MEMORY.md不存在：{self.memory_file}")
            return {}
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分离米粒儿和小米粒的内容（简化版）
        # 实际应该从对话记录中提取
        mili_sections = re.findall(r'## 米粒儿.*?(?=## |$)', content, re.DOTALL)
        xiaomi_sections = re.findall(r'## 小米粒.*?(?=## |$)', content, re.DOTALL)
        
        mili_text = ' '.join(mili_sections)
        xiaomi_text = ' '.join(xiaomi_sections)
        
        return self.analyze_conversation(mili_text, xiaomi_text)


def main():
    """主函数 - 演示用法"""
    print("================================")
    print("词汇考古工具 - 双米粒协作系统")
    print("================================")
    print()
    
    # 创建工具
    archaeology = VocabularyArchaeology()
    
    # 示例对话（模拟数据）
    mili_example = """
    官家，Review完成！
    
    我发现小米粒的代码有几个反对意见：
    1. 性能优化不够
    2. 错误处理不完善
    
    系统约束检查：Git状态正常，网络稳定。
    """
    
    xiaomi_example = """
    喏，官家！开发完成。
    
    我做了性能优化和错误处理。
    系统约束都检查过了，没问题。
    
    Review的反对意见我都看了，准备改进。
    """
    
    # 分析对话
    print("📊 分析对话中...")
    result = archaeology.analyze_conversation(mili_example, xiaomi_example, threshold=1)
    
    print()
    print(f"✅ 分析完成！")
    print(f"   - 米粒儿独特词汇：{result['mili_unique_words']}")
    print(f"   - 小米粒独特词汇：{result['xiaomi_unique_words']}")
    print(f"   - 共享词汇：{result['shared_words']}")
    print(f"   - 涌现词汇：{result['total_emergent_words']}")
    print()
    
    # 显示前10个涌现词汇
    print("🌟 涌现词汇（前10）：")
    top_10 = list(result['emergent_vocabulary'].items())[:10]
    for word, counts in top_10:
        print(f"   - {word}: {counts['total_count']}次")
    print()
    
    # 生成Markdown报告
    report = archaeology.generate_markdown_report(result)
    
    # 保存报告
    report_file = "/root/.openclaw/workspace/memory/emergent_vocabulary_report.md"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存到：{report_file}")
    print()
    
    # 保存JSON数据
    archaeology.save_emergent_vocabulary(result)
    
    print("✅ 词汇考古完成！")


if __name__ == "__main__":
    main()
