#!/usr/bin/env python3
"""
qmd 混合检索测试脚本
测试 BM25+ 向量 +LLM 重排的混合检索效果
"""

import subprocess
import sys
from datetime import datetime

WORKSPACE = '/home/zhaog/.openclaw/workspace'
MEMORY_DIR = f'{WORKSPACE}/memory'
LOGS_DIR = f'{WORKSPACE}/logs'

def run_qmd_command(args):
    """运行 qmd 命令"""
    cmd = [
        '/home/zhaog/.bun/bin/bun',
        f'{WORKSPACE}/../.bun/install/global/node_modules/@tobilu/qmd/src/qmd.ts'
    ] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_hybrid_search(query, collection='daily-logs'):
    """测试混合检索"""
    print("=" * 80)
    print(f"🔍 混合检索测试")
    print("=" * 80)
    print(f"查询：{query}")
    print(f"集合：{collection}")
    print()
    
    # 混合搜索（--hybrid）
    print("1️⃣  混合搜索（BM25 + 向量）...")
    returncode, stdout, stderr = run_qmd_command([
        'search', collection, query, '--hybrid', '-n', '5'
    ])
    
    if returncode == 0:
        print("✅ 混合搜索成功")
        print()
        print("结果：")
        print("-" * 80)
        print(stdout)
    else:
        print(f"❌ 混合搜索失败：{stderr}")
    print()
    
    # 纯语义搜索
    print("2️⃣  纯语义搜索...")
    returncode, stdout, stderr = run_qmd_command([
        'search', collection, query, '-n', '5'
    ])
    
    if returncode == 0:
        print("✅ 语义搜索成功")
        print()
        print("结果：")
        print("-" * 80)
        print(stdout)
    else:
        print(f"❌ 语义搜索失败：{stderr}")
    print()
    
    # 关键词搜索
    print("3️⃣  关键词搜索...")
    returncode, stdout, stderr = run_qmd_command([
        'search', collection, query, '--keyword', '-n', '5'
    ])
    
    if returncode == 0:
        print("✅ 关键词搜索成功")
        print()
        print("结果：")
        print("-" * 80)
        print(stdout)
    else:
        print(f"❌ 关键词搜索失败：{stderr}")
    print()
    
    print("=" * 80)
    print("💡 建议：")
    print("  - 混合检索：推荐默认使用，准确率约 93%")
    print("  - 语义搜索：适合记忆模糊、关键词不好描述的场景")
    print("  - 关键词搜索：传统全文检索，适合精确匹配")
    print("=" * 80)

def test_get_document(doc_id):
    """测试文档获取"""
    print("=" * 80)
    print(f"📄 获取文档：{doc_id}")
    print("=" * 80)
    
    returncode, stdout, stderr = run_qmd_command([
        'get', doc_id
    ])
    
    if returncode == 0:
        print("✅ 获取成功")
        print()
        print("内容：")
        print("-" * 80)
        print(stdout)
    else:
        print(f"❌ 获取失败：{stderr}")
    
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("用法：python3 tools/qmd-hybrid-search.py <查询> [集合名]")
        print()
        print("示例：")
        print("  python3 tools/qmd-hybrid-search.py \"写作风格\"")
        print("  python3 tools/qmd-hybrid-search.py \"之前讨论过什么\" daily-logs")
        print()
        print("或使用 --get 获取文档：")
        print("  python3 tools/qmd-hybrid-search.py --get <doc_id>")
        return
    
    if sys.argv[1] == '--get':
        if len(sys.argv) < 3:
            print("❌ 缺少文档 ID")
            return
        test_get_document(sys.argv[2])
    else:
        query = sys.argv[1]
        collection = sys.argv[2] if len(sys.argv) > 2 else 'daily-logs'
        test_hybrid_search(query, collection)

if __name__ == '__main__':
    main()
