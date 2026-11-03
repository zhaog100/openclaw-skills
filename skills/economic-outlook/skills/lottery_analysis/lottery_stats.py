#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 大乐透/双色球 数理分析 - 数据拉取+统计(考拉数理同款方法)
# 用法: python3 lottery_stats.py dlt | ssq
# 纪律: 摇奖独立, 所有"预测"输出必须带免责声明, 只分析不预测

import sys, re, json, urllib.request, time
from collections import Counter
from datetime import datetime, timezone, timedelta

UA = {"User-Agent": "Mozilla/5.0 (Linux; Android 16; Pixel 10) AppleWebKit/537.36 Chrome/156"}
BJ = timezone(timedelta(hours=8))
CACHES = {"dlt": "/tmp/lottery_cache_dlt.json", "ssq": "/tmp/lottery_cache_ssq.json"}


def fetch_history(kind):
    """拉官方历史开奖. dlt=大乐透(17500 dlt_asc), ssq=双色球(17500 ssq_asc). 带缓存"""
    url = {"dlt": "https://data.17500.cn/dlt_asc.txt", "ssq": "https://data.17500.cn/ssq_asc.txt"}[kind]
    cache = CACHES[kind]
    raw = None
    try:
        req = urllib.request.Request(url, headers=UA)
        raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        with open(cache, "w", encoding="utf-8") as f:
            f.write(raw)
    except Exception as e:
        print(f"⚠️ 拉取失败({e}), 用缓存", end=" ")
        try:
            raw = open(cache, encoding="utf-8").read()
        except Exception:
            print(" 且无缓存 → 退出")
            return []
    rows = []
    for line in raw.strip().split("\n"):
        t = line.split()
        if len(t) < 10:
            continue
        try:
            period, date = t[0], t[1]
            if kind == "dlt":
                front = [int(t[i]) for i in range(2, 7)]   # 前区5个
                back = [int(t[i]) for i in range(7, 9)]     # 后区2个
            else:
                front = [int(t[i]) for i in range(2, 8)]    # 红球6个
                back = [int(t[8])]                           # 蓝球1个
            rows.append({"period": period, "date": date, "front": front, "back": back})
        except (ValueError, IndexError):
            continue
    rows.sort(key=lambda r: r["period"])
    return rows


def chi_square(rows, kind):
    """卡方独立性检验: 各号码出现频率是否均匀(考拉数理步骤六)"""
    if kind == "dlt":
        all_front = [n for r in rows for n in r["front"]]
        expect_pool = 35
        cnt = Counter(all_front)
        obs = [cnt.get(i, 0) for i in range(1, expect_pool + 1)]
        total = len(all_front)
        E = total / expect_pool
        chi2 = sum((o - E) ** 2 / E for o in obs)
        dof = expect_pool - 1
        hi = cnt.most_common(3); lo = cnt.most_common(-3) if False else sorted(cnt.items(), key=lambda x: x[1])[:3]
        print(f"\n=== 前区 35 码卡方独立性检验(前 {len(rows)} 期) ===")
        print(f"  总出现 {total} 次, 期望每期码 {E:.1f} 次")
        print(f"  最高频: {hi}")
        print(f"  最低频: {lo}")
    else:
        all_front = [n for r in rows for n in r["front"]]
        expect_pool = 33
        cnt = Counter(all_front)
        obs = [cnt.get(i, 0) for i in range(1, expect_pool + 1)]
        total = len(all_front)
        E = total / expect_pool
        chi2 = sum((o - E) ** 2 / E for o in obs)
        print(f"\n=== 红球 33 码卡方独立性检验(前 {len(rows)} 期) ===")
        print(f"  总出现 {total} 次, 期望每期码 {E:.1f} 次")
        print(f"  最高频: {cnt.most_common(3)}")
        print(f"  最低频: {sorted(cnt.items(), key=lambda x: x[1])[:3]}")
    # 卡方分位数近似(查表)
    try:
        from scipy.stats import chi2 as chi2_dist
        pval = chi2_dist.sf(chi2, dof if kind == "dlt" else expect_pool - 1)
        verdict = "拒绝均匀(有偏)" if pval < 0.05 else "不能拒绝均匀(≈随机)"
        print(f"  χ² = {chi2:.2f}, p = {pval:.4f} → {verdict}")
    except Exception:
        print(f"  χ² = {chi2:.2f} (无 scipy, 跳过 p 值)")


def odd_even(rows, kind):
    """奇偶比 + 大小比(前区/红球)"""
    pool = 35 if kind == "dlt" else 33
    odd_cnt = sum(1 for r in rows for n in r["front"] if n % 2 == 1)
    total = len(rows) * (5 if kind == "dlt" else 6)
    print(f"\n=== 奇偶/大小比 ===")
    print(f"  前区总码 {total}, 奇数 {odd_cnt} ({odd_cnt/total*100:.1f}%), 偶数 {total-odd_cnt}")
    big = sum(1 for r in rows for n in r["front"] if n > pool / 2)
    print(f"  大号(>{pool/2:.0f}) {big} ({big/total*100:.1f}%)")


def sum_range(rows, kind):
    """前区/红球和值区间分布"""
    sums = [sum(r["front"]) for r in rows]
    import statistics
    print(f"\n=== 和值分布 ===")
    print(f"  均值 {statistics.mean(sums):.0f}, 中位 {statistics.median(sums):.0f}, "
          f"最小 {min(sums)}, 最大 {max(sums)}")
    # 25%~75% 分位(常见区间)
    s = sorted(sums)
    q1, q3 = s[len(s) // 4], s[3 * len(s) // 4]
    print(f"  常见区间(25%~75%分位): [{q1}, {q3}]")


def consecutive(rows, kind):
    """连号检测(前区/红球中相邻两码差=1)"""
    cnt = 0
    for r in rows:
        f = sorted(r["front"])
        if any(b - a == 1 for a, b in zip(f, f[1:])):
            cnt += 1
    print(f"\n=== 连号 ===")
    print(f"  含连号期数: {cnt}/{len(rows)} ({cnt/len(rows)*100:.1f}%)")


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "dlt"
    name = "大乐透" if kind == "dlt" else "双色球"
    rows = fetch_history(kind)
    if not rows:
        print("无数据, 退出")
        return
    print(f"📊 {name} 统计 | 共 {len(rows)} 期 | {rows[0]['date']} ~ {rows[-1]['date']}")
    chi_square(rows, kind)
    odd_even(rows, kind)
    sum_range(rows, kind)
    consecutive(rows, kind)
    print("\n⚠️ 免责声明: 以上为统计描述, 摇奖独立, 历史分布不预测未来, 不构成购彩建议, 彩票本质是随机游戏")




def random_note(kind="ssq"):
    """纯随机生成一注(官家11-03: 严格按游戏规则无放回抽样, random.sample 均匀无偏)。
    红球=1-33无放回抽6, 蓝球=1-16抽1(双色球); 大乐透=前区35无放回抽5+后区12抽2。
    核心: random.sample 保证每个组合等概率, 不重复。
    纪律: 均匀随机=公平, 但绝不改变开奖本身的随机性, 任何算法都无法预测。"""
    import random
    if kind == "ssq":
        red = sorted(random.sample(range(1, 34), 6))
        blue = random.randint(1, 16)
        return {"kind": "双色球", "red": [f"{n:02d}" for n in red], "blue": f"{blue:02d}",
                "note": "无放回随机(每组合等概率), 不影响开奖随机性, 不构成购彩建议"}
    front = sorted(random.sample(range(1, 36), 5))
    back = sorted(random.sample(range(1, 13), 2))
    return {"kind": "大乐透", "front": [f"{n:02d}" for n in front], "back": [f"{n:02d}" for n in back],
            "note": "无放回随机(每组合等概率), 不影响开奖随机性, 不构成购彩建议"}


if __name__ == "__main__":
    main()
