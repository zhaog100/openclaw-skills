#!/usr/bin/env python3
"""P2 内容助手测试脚本"""

import sys
import json
sys.path.insert(0, '.')
from assistant import ContentAssistant, print_result

def test_all():
    assistant = ContentAssistant(model="qwen2.5:0.5b")
    results = []
    
    # 测试1: 文案生成
    print("\n🧪 测试1: 文案生成")
    r1 = assistant.generate_copy(
        topic="小米椒咖啡屋新品上市",
        style="小红书",
        length="short"
    )
    print_result(r1)
    results.append(("generate", r1))
    
    # 测试2: 文案优化
    print("\n🧪 测试2: 文案优化")
    r2 = assistant.optimize_copy(
        original="这家店不错，值得推荐",
        platform="小红书"
    )
    print_result(r2)
    results.append(("optimize", r2))
    
    # 测试3: 概念解释
    print("\n🧪 测试3: 概念解释")
    r3 = assistant.explain_concept(
        concept="什么是小红书算法",
        audience="普通人"
    )
    print_result(r3)
    results.append(("explain", r3))
    
    # 汇总
    print("\n" + "=" * 50)
    print("📊 测试汇总")
    print("=" * 50)
    for name, r in results:
        status = "✅" if r.success else "❌"
        print(f"{status} {name}: {r.latency_ms}ms")
    
    success_count = sum(1 for _, r in results if r.success)
    print(f"\n成功率: {success_count}/{len(results)}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
