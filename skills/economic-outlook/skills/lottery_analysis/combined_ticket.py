#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 综合出号: 统计层(高频/和值/贝叶斯) + 曼德尔公式(定胆+拖/凯利) + 纯随机对照
# 用法: python3 combined_ticket.py ssq|dlt
# 纪律: 摇奖独立, 任何选号法不提升中奖概率, 输出带免责声明

import sys, json, random
from collections import Counter
from lottery_stats import fetch_history, random_note
from formulas import combinations, cost_expected, sum_distribution, mandel, bayes_update


def generate(kind="ssq", n_mandel=2):
    """综合出号: 统计层 + 曼德尔定胆+拖 + 纯随机对照, 全揉一份报告"""
    rows = fetch_history(kind)
    mand = mandel(kind)
    bess = bayes_update(rows, kind)
    comb = combinations(kind)
    cost = cost_expected(kind)
    srange = sum_distribution(rows, kind)
    cnt = Counter(n for r in rows for n in r["front"])
    top5 = [c for c, _ in cnt.most_common(5)]

    bank = mand["bank_danger"][:5]
    if kind == "ssq":
        blue = Counter(r["back"][0] for r in rows).most_common(1)[0][0]
        drag = [n for n in range(1, 34) if n not in bank][:max(n_mandel, 1)]
        notes = [{"front": sorted(bank + [d])[:6], "back": [blue]} for d in drag]
    else:
        backcnt = Counter()
        for r in rows:
            for n in r["back"]:
                backcnt[n] += 1
        back_top = sorted([c for c, _ in backcnt.most_common(2)])
        bank5 = sorted(bank[:5])
        drag = [n for n in range(1, 36) if n not in bank5][:max(n_mandel, 1)]
        notes = [{"front": bank5, "back": back_top}]
        for d in drag[1:]:
            notes.append({"front": sorted(bank5[:-1] + [d]), "back": back_top})

    return {
        "kind_cn": mand["kind_cn"], "N": bess["N"],
        "top5": top5,
        "sum_range": srange["common_range"], "sum_mean": srange["mean"],
        "bayes": {"theta": bess["theta"], "ci": bess["ci95"], "all_in": bess["all_in_ci"]},
        "mandel": mand,
        "comb_total": comb["total"],
        "cost": cost,
        "notes": notes,
        "random": random_note(kind),
        "disclaimer": "摇奖独立, 历史统计不改变中奖概率, 任意合法组合头奖概率相同, 不构成购彩建议",
    }


def print_report(kind="ssq"):
    r = generate(kind)
    print("=" * 46)
    print(f"📊 {r['kind_cn']} 综合出号 (基于 {r['N']} 期历史)")
    print("=" * 46)
    print(f"【统计】 高频前区码Top5: {r['top5']}")
    print(f"          和值常见区间: {r['sum_range']}, 均值 {r['sum_mean']}")
    print(f"          贝叶斯: θ={r['bayes']['theta']}, 全落CI内={r['bayes']['all_in']}")
    print(f"【曼德尔】定胆: {r['mandel']['bank_danger']}  拖码: {r['mandel']['drag_example']}")
    print(f"          凯利仓位: {r['mandel']['kelly_pct']}% ({r['mandel']['kelly_note']})")
    print(f"【概率】 头奖 1/{r['comb_total']:,}, 每注期望 {r['cost']['buy1_expected']}元")
    print(f"\n【曼德尔出号(统计选号)】")
    for i, n in enumerate(r["notes"], 1):
        fs = " ".join(f"{x:02d}" for x in n["front"])
        bs = " ".join(f"{x:02d}" for x in n["back"])
        print(f"  {i}. 前区 {fs}  后区 {bs}")
    rnd = r["random"]
    print(f"\n【纯随机对照(无放回,中奖概率与上面完全相同)】")
    if "front" in rnd:
        print(f"  前区 {' '.join(rnd['front'])}  后区 {' '.join(rnd['back'])}")
    else:
        print(f"  红球 {' '.join(rnd['red'])}  蓝 {rnd['blue']}")
    print(f"\n⚠️ {r['disclaimer']}")


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    print_report(kind)
