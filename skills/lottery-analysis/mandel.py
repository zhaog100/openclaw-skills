#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 曼德尔公式: 组合冷凝+资金管理(官家11-02 23:01 截图)
# 定位: 不是预测号码, 是缩小选号范围/控制成本。
# 纪律: 所有输出必须带"摇奖独立, 不构成购彩建议"免责声明。

import sys, json
from itertools import combinations
from lottery_stats import fetch_history


def _topn_freq(rows, kind, n=5):
    """取前区/红球最高频 n 个码作"定胆候选"(统计层输出, 非预测)"""
    from collections import Counter
    cnt = Counter(num for r in rows for num in r["front"])
    return [c for c, _ in cnt.most_common(n)]


def _zone_heat(rows, kind):
    """区间热度: 把前区/红球均分 3 区, 各码落在哪个区更热"""
    pool = 35 if kind == "dlt" else 33
    zone = [0, 0, 0]
    for r in rows:
        for num in r["front"]:
            zone[min(num * 3 // pool, 2)] += 1
    return zone


def _kelly(b, odds):
    """凯利公式 f* = (b*odds - 1) / (b - 1); b=净赔率, odds=胜率"""
    if b <= 1:
        return 0.0
    f = (b * odds - 1) / (b - 1)
    return max(0.0, min(f, 1.0))


def mandel(kind="ssq", bankroll=100.0, per_note=2.0, b_net=0.0):
    """曼德尔公式主流程: 定胆→分区过滤→胆拖组合→凯利仓位。
    全部含免责声明, 不预测号码, 只做组合冷凝+资金控制。"""
    rows = fetch_history(kind)
    if not rows:
        return {"success": False, "error": "无历史数据",
                "disclaimer": "摇奖独立, 不构成购彩建议"}
    pool = 33 if kind == "ssq" else 35
    # ① 定胆: 最高频 5 码
    bank = _topn_freq(rows, kind, n=5)
    # ② 分区过滤: 3 区热度
    zone = _zone_heat(rows, kind)
    zmax = zone.index(max(zone))
    zone_hint = {0: "前 1/3", 1: "中 1/3", 2: "后 1/3"}[zmax]
    # ③ 组合设计: 胆拖(5 胆 + 拖码)
    drag = [n for n in range(1, pool + 1) if n not in bank]
    drag_pick = drag[:6]
    notes = 1
    if kind == "ssq":
        need = 6; have = min(5, len(bank))
        du = need - have
        if 0 < du <= len(drag_pick):
            notes = sum(1 for _ in combinations(drag_pick, du))
    else:
        notes = 5
    # ④ 资金管理: 凯利(彩票净赔率极低 → 仓位极保守)
    f_kelly = _kelly(b_net, 0.05)
    bank_pct = round(f_kelly * 100, 1)
    return {
        "success": True, "kind": kind,
        "kind_cn": "双色球" if kind == "ssq" else "大乐透",
        "bank_danger": bank, "bank_note": "最高频候选(统计层, 非预测, 摇奖独立)",
        "zone_hint": f"{zone_hint} 区间近期热度最高",
        "drag_example": drag_pick, "notes": notes,
        "cost": notes * per_note, "cost_note": f"{notes} 注 x {per_note} 元",
        "kelly_pct": bank_pct,
        "kelly_note": "凯利仓位(彩票净赔率极低, 仓位应极保守, 0% = 数学上不建议下注)",
        "bankroll_used": round(bankroll * f_kelly, 2),
        "disclaimer": "曼德尔公式只做组合冷凝+资金管理, 不预测号码; 摇奖独立, 历史频率不影响下期, 以上不构成购彩建议, 彩票本质是随机游戏",
    }


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    print(json.dumps(mandel(kind), ensure_ascii=False, indent=2))
