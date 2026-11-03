#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 彩票概率/成本公式包(鲁班科普3505期 + 官家大乐透算法图, 11-02 23:14 扩)
# 覆盖双色球+大乐透, 公式全部可算, 输出带免责声明
# 纪律: 摇奖独立, 官方概率是确定的数, 民间"公式"多为娱乐不提升中奖率

from math import comb
import statistics


def combinations(kind="ssq"):
    """组合数(官方规则): 双色球 C(33,6)x16蓝球 / 大乐透 C(35,5)x C(12,2)"""
    if kind == "ssq":
        red, blue = comb(33, 6), comb(16, 1)
        return {"kind": "双色球", "play": "红球6+蓝球1", "red_C": red, "blue_C": blue,
                "total": red * blue, "note": "从 %d 种组合里中一等奖" % (red * blue)}
    front, back = comb(35, 5), comb(12, 2)
    return {"kind": "大乐透", "play": "前区35选5+后区12选2", "front_C": front, "back_C": back,
            "total": front * back, "note": "从 %d 种组合里中一等奖" % (front * back)}


def jackpot_odds(kind="ssq"):
    """头奖概率 1/总组合数 + 期望买多少注中1次"""
    total = combinations(kind)["total"]
    return {"kind": kind, "jackpot_odds": round(1 / total, 15), "expected_notes": total,
            "note": "买 %d 注才期望中1次头奖(数学上必亏)" % total}


def prize_structure(kind="ssq"):
    """奖级结构(图: 大乐透)。双色球按官方固定奖级"""
    if kind == "dlt":
        return {
            "一等奖_5_2": "浮动, 奖池<1亿约78% / 1-8亿约58%+20% / >8亿约28%+50%, 单注封顶500万",
            "二等奖_5_1": "约22%, 封顶50万",
            "三等奖_5_0": "约?", "四至八等": "3000/300/200/100/15/5 元",
            "追加": "每注+1元, 提升奖级奖金, 不增加中奖概率",
            "note": "奖级金额是机制, 非预测; 概率仍由组合数决定",
        }
    return {"note": "双色球奖级: 一等奖浮动/二等奖约5%... 以当期官方为准"}


def sum_distribution(rows, kind="ssq"):
    """和值分布: 前区码和值近似正态(视频1.11), 均值/常见区间/极值"""
    sums = [sum(r["front"]) for r in rows]
    s = sorted(sums)
    n = len(s)
    q1, q3 = s[n // 4], s[3 * n // 4]
    return {"mean": round(statistics.mean(sums), 1), "median": round(statistics.median(sums), 1),
            "min": min(s), "max": max(s), "common_range": [q1, q3],
            "note": "和值只是表象, 组合才是本质, 不代表中奖概率"}


def golden_section_anchor(kind="dlt"):
    """民间黄金分割(35×0.618≈22, 35-22≈13)当区间锚点(图: 01-13/14-22/23-35)。
    仅作结构参照, 明确标注'娱乐, 不提升概率'。"""
    if kind == "dlt":
        anchor = 35 * 0.618
        return {"anchor": round(anchor, 1), "anchor2": round(35 - anchor, 1),
                "zones": ["01-13", "14-22", "23-35"],
                "note": "黄金分割锚点=民间娱乐结构法, 不提升中奖概率(摇奖独立)"}
    return {}


def bayes_update(rows, kind="ssq"):
    """贝叶斯更新(考拉数理3.2, 官家11-03定稿): 摇奖独立下, 单码真实概率θ=1/pool是物理常数,
    历史数据D不更新它。用'实测频率k/N的95%置信区间是否包含θ'来证'历史与随机一致'。
    不更新θ本身(因为摇奖机物理独立, 似然对θ无信息量), 只检验频率波动范围。
    输出: 每码的实测频率+95%CI, 以及'是否全部落在CI内'(=历史数据无异常偏置)。"""
    from collections import Counter
    if not rows:
        return {"ok": False, "error": "无历史数据"}
    pool, pick = (33, 6) if kind == "ssq" else (35, 5)
    N = len(rows)
    theta = pick / pool   # 摇奖独立下单码出现概率=每期选中pick个/pool个(物理常数, 不随数据更新)
    cnt = Counter(num for r in rows for num in r["front"])
    # 每码: 实测频率 + 95% CI (二项分布正态近似: k/N ± 1.96*sqrt(θ(1-θ)/N))
    import math
    se = math.sqrt(theta * (1 - theta) / N)   # θ(1-θ)/N 标准误
    lo, hi = theta - 1.96 * se, theta + 1.96 * se
    freqs = {}
    all_in_ci = True
    for num in range(1, pool + 1):
        k = cnt.get(num, 0)
        obs = k / N
        in_ci = lo <= obs <= hi
        if not in_ci:
            all_in_ci = False
        freqs[num] = {"obs": round(obs, 5), "in_95ci": in_ci}
    out_of_ci = {n: v for n, v in freqs.items() if not v["in_95ci"]}
    return {
        "theta": round(theta, 6),
        "N": N,
        "ci95": [round(lo, 5), round(hi, 5)],
        "all_in_ci": all_in_ci,
        "out_of_ci": out_of_ci,
        "note": "摇奖独立: θ=%d/%d=%.4f是物理常数(每期pick个/pool个), 历史数据不更新θ。%d期实测中%d码落在95%%CI外=%s, "
                "%s" % (
                    pick, pool, theta, N, len(out_of_ci),
                    "有" if out_of_ci else "无",
                    "全部落在CI内→历史与随机一致, 看再多数据也改不了下一期概率"
                    if all_in_ci else
                    "有限样本噪声(期望%d码出界, 实际%d, 不构成规律)" % (
                        pool * 0.05, len(out_of_ci))
                ),
    }


def cost_expected(kind="ssq", per_note=2.0, payout_rate=0.51):
    """成本/期望公式(鲁班科普1.9实数据): 每注2元, 返奖率约51%→收回约1.02元, 期望必为负。
    期望收益 = 成本 x (返奖率 - 1) < 0"""
    back = per_note * payout_rate
    buy1 = back - per_note
    odds = 1 / combinations(kind)["total"]
    full = odds * 1_000_000 - per_note
    return {"per_note_cost": per_note, "payout_rate": payout_rate, "back_per_note": round(back, 2),
            "buy1_expected": round(buy1, 4), "full_jackpot_expected": round(full, 4),
            "note": "每注%.2f元只有%.2f元(约%d%%)回到奖金池, 期望%.4f元必为负, 长期必亏"
            % (per_note, back, payout_rate * 100, buy1)}


def mandel(kind="ssq", bankroll=100.0, per_note=2.0, b_net=0.0):
    """曼德尔公式(图: 定胆+拖/分区/组合/凯利)。只做组合冷凝+资金控制, 不预测号码。"""
    from collections import Counter
    from lottery_stats import fetch_history
    rows = fetch_history(kind)
    if not rows:
        return {"success": False, "error": "无历史数据"}
    pool = 33 if kind == "ssq" else 35
    cnt = Counter(num for r in rows for num in r["front"])
    bank = [c for c, _ in cnt.most_common(5)]
    drag = [n for n in range(1, pool + 1) if n not in bank][:6]
    # 凯利(彩票净赔率极低→仓位极保守)
    f_kelly = max(0.0, min(((b_net * 0.05 - 1) / (b_net - 1)) if b_net > 1 else 0.0, 1.0))
    return {"success": True, "kind_cn": "双色球" if kind == "ssq" else "大乐透",
            "bank_danger": bank, "bank_note": "最高频候选(统计层, 非预测)",
            "drag_example": drag, "kelly_pct": round(f_kelly * 100, 1),
            "kelly_note": "凯利仓位(彩票净赔率极低, 0%=数学上不建议下注)",
            "disclaimer": "曼德尔公式只做组合冷凝+资金管理, 不预测号码; 摇奖独立, 不构成购彩建议"}


if __name__ == "__main__":
    import json, sys
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    from lottery_stats import fetch_history
    rows = fetch_history(kind)
    out = {"combinations": combinations(kind), "jackpot": jackpot_odds(kind),
           "prize": prize_structure(kind), "sum_distribution": sum_distribution(rows, kind),
           "golden_section": golden_section_anchor(kind), "bayes": bayes_update(rows, kind),
           "cost": cost_expected(kind), "mandel": mandel(kind)}
    out["disclaimer"] = "摇奖独立, 官方概率确定, 民间公式多为娱乐不提升中奖率, 统计/公式均不预测未来, 不构成购彩建议, 彩票本质是随机游戏"
    print(json.dumps(out, ensure_ascii=False, indent=2))
