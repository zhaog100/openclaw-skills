#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 官家11-20借鉴 IOI-LottoLab: 走期回测框架(walk-forward, 杜绝未来数据泄露)
# 用法: python3 walk_forward.py [ssq|dlt] [期数]
# 纪律: 摇奖独立, 回测只验证"策略 vs 随机"差异, 大概率趋同, 不预测未来
import os, sys, random
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lottery_stats import fetch_history


def _mandel_bank(rows, kind, n_bank=5):
    """官家11-20: 直接用传入的 rows 切片算双因子胆码(不走 fetch_history, 避免每期重拉)。
    双因子: 全期频率(0.5) + 近50期活跃(0.3) + 遗漏适中(0.2) + 玄学加权(0.15, 与 mandel 一致)"""
    pool = 35 if kind == "dlt" else 33
    cnt_all = Counter(num for r in rows for num in r["front"])
    recent = rows[-50:]
    cnt_recent = Counter(num for r in recent for num in r["front"])
    max_all = max(cnt_all.values()) or 1
    max_recent = max(cnt_recent.values()) or 1
    last_seen = {}
    for idx, r in enumerate(rows):
        for num in r["front"]:
            last_seen[num] = idx
    gap_max = len(rows)
    score = {}
    for num in range(1, pool + 1):
        f = cnt_all.get(num, 0) / max_all
        a = cnt_recent.get(num, 0) / max_recent
        gap = gap_max - last_seen.get(num, 0)
        g = 1.0 - min(gap / gap_max, 1.0)
        base = 0.5 * f + 0.3 * a + 0.2 * g
        # 玄学加权(与 formulas.mandel 同口径): 梅花易数方位 + 紫微五行 + 周易时间数, 官方权重 0.15
        if os.environ.get("LOTTERY_XUANXUE", "1") == "1":
            import datetime as _dt, hashlib as _hl
            now = _dt.datetime.now()
            seed = _hl.md5(f"{now.year}{now.month:02d}{now.day:02d}{kind}".encode()).digest()
            day_el = ["金", "木", "水", "火", "土"][(now.day + now.month) % 5]
            num_el = ["金", "木", "水", "火", "土"][(num - 1) % 5]
            s = 0.0
            if num_el == day_el:
                s += 0.15
            order = ["金", "水", "木", "火", "土"]
            if order[(order.index(num_el) + 1) % 5] == day_el or order[(order.index(day_el) + 1) % 5] == num_el:
                s += 0.3
            s += (seed[num % 16] / 255.0) * 0.45
            score[num] = 0.85 * base + 0.15 * min(1.0, s)
        else:
            score[num] = base
    return sorted(score, key=score.get, reverse=True)[:n_bank]


def walk_forward_backtest(kind="ssq", warmup=50, last_n=50):
    """官家11-20借鉴 IOI-LottoLab: 走期回测
    一次拉全量历史, 对第 t 期只用 rows[:t] 算胆码 → 命中 rows[t] 前区。
    杜绝未来数据泄露; 对照纯随机同种子(可复现)。"""
    rows = fetch_history(kind)
    if len(rows) < warmup + 10:
        return {"success": False, "error": f"历史数据不足({len(rows)}期)"}
    pool = 35 if kind == "dlt" else 33
    nfront = 5 if kind == "dlt" else 6
    start = max(warmup, len(rows) - last_n)

    strategy_hits, random_hits = [], []
    total_s = total_r = 0
    ge3_s = ge3_r = 0
    periods = 0
    for t in range(start, len(rows)):
        bank = _mandel_bank(rows[:t], kind, n_bank=nfront)
        actual_front = set(rows[t]["front"])
        s_hits = len(set(bank) & actual_front)
        rng = random.Random(t)
        r_front = set(rng.sample(range(1, pool + 1), nfront))
        r_hits = len(r_front & actual_front)
        strategy_hits.append(s_hits)
        random_hits.append(r_hits)
        total_s += s_hits
        total_r += r_hits
        if s_hits >= 3: ge3_s += 1
        if r_hits >= 3: ge3_r += 1
        periods += 1

    if periods == 0:
        return {"success": False, "error": "无有效回测期"}

    avg_s, avg_r = total_s / periods, total_r / periods
    edge = avg_s - avg_r
    verdict = ("策略优于随机" if edge > 0.15 else "策略劣于随机" if edge < -0.15 else "策略≈随机(无超额, 符合摇奖独立)")

    return {"success": True, "kind": kind, "periods": periods, "warmup": warmup,
            "strategy_avg": round(avg_s, 3), "random_avg": round(avg_r, 3),
            "edge": round(edge, 3), "strategy_ge3": ge3_s, "random_ge3": ge3_r,
            "verdict": verdict,
            "note": "走期回测: 每期只用其之前的数据, 杜绝未来泄露",
            "disclaimer": "摇奖独立, 历史统计不改变中奖概率, 不构成购彩建议"}


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    res = walk_forward_backtest(kind, last_n=n)
    print(f"[{kind}] 走期回测 {n} 期, warmup={res.get('warmup', 50)}")
    for k in ["strategy_avg", "random_avg", "edge", "strategy_ge3", "random_ge3", "verdict", "disclaimer"]:
        if k in res:
            print(f"  {k}: {res[k]}")
