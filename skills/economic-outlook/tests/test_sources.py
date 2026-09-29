#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 数据源适配器测试（3.6 验收: 11 适配器至少 8 个可用）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared'))


def main():
    passed = 0
    # 11 个适配器（官方 3 + 信号专用 8）
    adapters = [
        ("shared.sources.pmi", "PMIAdapter"),
        ("shared.sources.credit", "CreditAdapter"),
        ("shared.sources.china_us_spread", "ChinaUSSpreadAdapter"),
        ("shared.sources.global_pmi", "GlobalPMIAdapter"),
        ("shared.sources.recruitment", "RecruitmentAdapter"),
        ("shared.sources.etf_flow", "ETFFlowAdapter"),
        ("shared.sources.export_category", "ExportCategoryAdapter"),
        ("shared.sources.domestic_retail", "DomesticRetailAdapter"),
        ("shared.sources.nbs", "NBSAdapter"),
        ("shared.sources.customs", "CustomsAdapter"),
        ("shared.sources.pboc", "PBOCAdapter"),
    ]
    import importlib
    usable = 0
    for mod_path, cls_name in adapters:
        try:
            m = importlib.import_module(mod_path)
            cls = getattr(m, cls_name, None)
            if cls is not None:
                inst = cls({})  # 3.6: 可实例化才算可用
                usable += 1
                print(f"  ✓ {cls_name} 可实例化")
            else:
                print(f"  ✗ {cls_name} 类不存在")
        except Exception as e:
            print(f"  ✗ {cls_name} 失败: {str(e)[:40]}")

    # 3.6 验收: 至少 8 个可用
    assert usable >= 8, f"可用适配器 {usable} < 8，不达标"
    print(f"\n{usable}/11 适配器可用 ✓ (3.6 验收: ≥8 达标)")
    passed += 1

    print(f"\ntest_sources: PASS ({passed} checks, 适配器 {usable}/11)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
