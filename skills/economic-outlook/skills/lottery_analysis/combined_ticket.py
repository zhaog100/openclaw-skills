#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 综合出号: 统计层(高频/和值/贝叶斯) + 曼德尔公式(定胆+拖/凯利) + 纯随机对照
# 用法: python3 combined_ticket.py ssq|dlt
# 纪律: 摇奖独立, 任何选号法不提升中奖概率, 输出带免责声明

import sys, json, random
from collections import Counter
from lottery_stats import fetch_history, random_note, chi_square, odd_even, sum_range, consecutive
from formulas import combinations, cost_expected, sum_distribution, mandel, bayes_update


def _history_analysis(rows, kind):
    """历史号分析(官家11-10): 每次出号附历史维度, 看清"最近开出啥/什么结构居多", 纯描述不预测。
    输出: 最新3期实际开奖 / 高频前3 / 低频前3 / 奇偶比 / 和值分布 / 连号占比 / 大小比。"""
    from collections import Counter
    if not rows:
        return {"ok": False}
    pool, pick = (33, 6) if kind == "ssq" else (35, 5)
    cnt = Counter(n for r in rows for n in r["front"])
    last3 = [{"period": r["period"], "date": r["date"],
              "front": [f"{n:02d}" for n in r["front"]],
              "back": [f"{n:02d}" for n in r["back"]]} for r in rows[-3:]]
    high = [(f"{n:02d}", c) for n, c in cnt.most_common(3)]
    low = [(f"{n:02d}", c) for n, c in sorted(cnt.items(), key=lambda x: x[1])[:3]]
    total = len(rows) * pick
    odd = sum(1 for r in rows for n in r["front"] if n % 2 == 1)
    big = sum(1 for r in rows for n in r["front"] if n > pool / 2)
    sums = sorted(sum(r["front"]) for r in rows)
    q1, q3 = sums[len(sums)//4], sums[3*len(sums)//4]
    cons = sum(1 for r in rows if any(b-a==1 for a, b in zip(sorted(r["front"]), sorted(r["front"])[1:])))
    return {
        "ok": True,
        "last3": last3,
        "high": high, "low": low,
        "odd_pct": round(odd/total*100, 1), "even_pct": round((total-odd)/total*100, 1),
        "big_pct": round(big/total*100, 1),
        "sum_mean": round(sum(sums)/len(sums), 1), "sum_range": [q1, q3],
        "consec_pct": round(cons/len(rows)*100, 1),
        "note": "历史描述, 摇奖独立, 不预测未来, 仅供结构参照",
    }


def _retro_analysis(rows, kind):
    """反推复盘(官家11-10): 最新一期新号出来后, 反推"为什么开出这几个号"——
    对照历史分布标出该期在 和值/奇偶/大小/连号/冷号 各维度的偏离, 产出偏差信号反哺下期出号。
    纪律: 摇奖独立, 反推是结构复盘(该期相对历史的偏离), 不预测下期; 偏差信号只做权重微调, 不改随机性。"""
    from collections import Counter
    if len(rows) < 10:
        return {"ok": False}
    pool, pick = (33, 6) if kind == "ssq" else (35, 5)
    hist = rows[:-1]                      # 历史(不含最新一期)
    last = rows[-1]                       # 最新一期(该反推它)
    last_front = sorted(last["front"])
    # 历史基线
    hist_sums = sorted(sum(r["front"]) for r in hist)
    hs_mean = sum(hist_sums)/len(hist_sums)
    hs_q1, hs_q3 = hist_sums[len(hist_sums)//4], hist_sums[3*len(hist_sums)//4]
    last_sum = sum(last_front)
    # 奇偶/大小基线
    hist_odd = sum(1 for r in hist for n in r["front"] if n%2==1)/(len(hist)*pick*100)
    hist_big = sum(1 for r in hist for n in r["front"] if n>pool/2)/(len(hist)*pick*100)
    last_odd = sum(1 for n in last_front if n%2==1)/pick
    last_big = sum(1 for n in last_front if n>pool/2)/pick
    # 连号
    has_consec = any(b-a==1 for a,b in zip(last_front, last_front[1:]))
    # 冷号回补: 该期前区里遗漏值(距上次出现期数)大的
    last_seen = {}
    for i, r in enumerate(hist):
        for n in r["front"]:
            last_seen[n] = i
    gaps = []
    for n in last_front:
        gap = (len(hist)-1) - last_seen.get(n, -1)   # 距上次出现的期数
        gaps.append((n, gap))
    cold_picks = [n for n,g in sorted(gaps, key=lambda x:x[1], reverse=True) if g >= len(hist)*0.3][:3]
    # 偏差信号(反哺下期): 该期和值偏高→下期往均值拉
    if last_sum > hs_q3:
        sum_signal = "上期和值偏高(%.0f>上分位%.0f), 下期和值约束往均值%.0f靠" % (last_sum, hs_q3, hs_mean)
        sum_shift = -1
    elif last_sum < hs_q1:
        sum_signal = "上期和值偏低(%.0f<下分位%.0f), 下期和值约束往均值%.0f靠" % (last_sum, hs_q1, hs_mean)
        sum_shift = 1
    else:
        sum_signal = "上期和值在常见区间[%.0f~%.0f]内, 下期按常态区间" % (hs_q1, hs_q3)
        sum_shift = 0
    # 奇偶偏差
    odd_signal = "上期奇偶%.0f%%(历史基线%.0f%%), 偏%s" % (last_odd*100, hist_odd*100, "奇" if last_odd>hist_odd else "偶")
    reasons = [
        "和值 %.0f (历史均值%.0f, 常见%.0f~%.0f)" % (last_sum, hs_mean, hs_q1, hs_q3),
        "奇偶 %.0f%% 奇 (基线%.0f%%)" % (last_odd*100, hist_odd*100),
        "大小 %.0f%% 大 (基线%.0f%%)" % (last_big*100, hist_big*100),
        "连号" if has_consec else "无连号",
        ("冷号回补: " + "、".join(f"{n:02d}(遗漏{g}期)" for n,g in sorted(gaps,key=lambda x:x[1],reverse=True)[:3])) if cold_picks else "无显著冷号",
    ]
    return {
        "ok": True, "period": last["period"], "date": last["date"],
        "last_front": [f"{n:02d}" for n in last_front],
        "last_back": [f"{n:02d}" for n in last.get("back",[])],
        "reasons": reasons,
        "sum_signal": sum_signal, "sum_shift": sum_shift,
        "odd_signal": odd_signal,
        "cold_picks": cold_picks,
        "note": "反推是该期相对历史的结构复盘, 摇奖独立, 不预测下期; 偏差信号只做权重微调",
    }


def _sum_constrained_front(bank, kind, target_range, pool=None, pick=None):
    """[A 11-10优化] 和值约束出号: 拖码不再机械取最小号, 改从"和值落在常见区间"的组合里选。
    bank=已定胆码, 补齐到 pick 个时和值必须落在 target_range(和值常见区间 q1~q3),
    同时尽量拉开大小/奇偶结构。返回多组合规前区(结构更均衡)。"""
    import random
    pool = pool if pool else (33 if kind == "ssq" else 35)
    pick = pick if pick else (6 if kind == "ssq" else 5)
    lo, hi = target_range if target_range else (0, 999)
    need = pick - len(bank)
    cands = [n for n in range(1, pool + 1) if n not in bank]
    if need <= 0:
        return [sorted(bank)]
    # 生成组合: 从 cands 无放回抽 need 个, 筛和值落 [lo,hi], 去重保结构多样性
    bank_sum = sum(bank)
    seen, out = set(), []
    attempts = 0
    while len(out) < pick and attempts < 4000:
        attempts += 1
        combo = random.sample(cands, need)
        tot = bank_sum + sum(combo)
        if not (lo <= tot <= hi):
            continue
        front = sorted(bank + combo)
        key = tuple(front)
        if key in seen:
            continue
        seen.add(key)
        out.append(front)
    if not out:   # 和值区间太窄抽不到 → 放宽到全和值再抽
        out = [sorted(bank + random.sample(cands, need))]
    return out


def generate(kind="ssq", n_mandel=2):
    """综合出号: 统计层 + 曼德尔双因子胆码 + 和值约束拖码 + 蓝球多值覆盖 + 纯随机对照
    [D 11-10优化] A出号结构(和值约束+结构均衡) B蓝球多值 C胆码双因子, 全揉一份报告。
    纪律: 摇奖独立, 优化只改组合结构/覆盖度/成本效率, 不改变中奖概率。"""
    rows = fetch_history(kind)
    mand = mandel(kind)
    bess = bayes_update(rows, kind)
    comb = combinations(kind)
    cost = cost_expected(kind)
    srange = sum_distribution(rows, kind)
    cnt = Counter(n for r in rows for n in r["front"])
    top5 = [c for c, _ in cnt.most_common(5)]

    bank = mand["bank_danger"][:5]
    target = srange["common_range"]
    # 反推复盘(官家11-10): 最新一期反推 + 偏差信号反哺下期
    retro = _retro_analysis(rows, kind)
    if retro.get("ok") and retro["sum_shift"] != 0:
        lo, hi = target
        mean_s = srange["mean"]
        shift = (mean_s - lo) * 0.3 if retro["sum_shift"] == -1 else (hi - mean_s) * 0.3
        target = [int(lo + (shift if retro["sum_shift"]==1 else -shift)), int(hi - (shift if retro["sum_shift"]==-1 else shift))]
    if kind == "ssq":
        # [B] 蓝球多值: 官家11-21改"高频并列全保留" — TOP3差≤5视为并列, 全进推荐不单押
        blue_cnt = Counter(r["back"][0] for r in rows)
        top3 = blue_cnt.most_common(3)
        blue_hot = [c for c, _ in top3]
        top_vals = [v for _, v in top3]
        tie_band = sorted([c for c, v in top3 if top_vals[0] - v <= 5], key=lambda c: (-blue_cnt.get(c, 0), c))
        all_blues = set(range(1, 17))
        cold = [b for b in all_blues if b not in blue_cnt]
        blue_pool = tie_band + ([cold[0] % 16 + 1] if cold else [])
        blue_pool = sorted(set(blue_pool))[:4] or [blue_hot[0]]
        # [A] 和值约束出号: 多组拖码, 每组和值落常见区间
        fronts = _sum_constrained_front(bank, kind, target, pool=33, pick=6)
        notes = [{"front": f, "back": [blue_pool[i % len(blue_pool)]]} for i, f in enumerate(fronts[:max(n_mandel, 2)])]
        blue_pool_used = blue_pool
        # 双色球 10 种投注形式(官家11-10模板): 单式/7+1/8+1/6+2蓝/全蓝/全复式7+2/8+2/4胆4拖/3胆7拖/4胆4拖2蓝
        import itertools as _it
        from math import comb as _comb
        base_red = sorted(fronts[0]) if fronts else sorted(bank[:5] + [n for f in fronts[:2] for n in f if n not in bank[:5]][:1])[:6]
        base_blue = blue_pool[0] if blue_pool else 1
        def _money(n):
            return f"{n}注, {n*2}元"
        def _note_of(reds, blues, label):
            n = _comb(len(reds), 6) * len(blues) if len(reds) > 6 else (len(blues) * (1 if len(reds)==6 else 0))
            if len(reds) <= 6 and len(blues) == 1:
                return f"1注, 2元"
            return _money(n)
        # 红球池: 从双因子胆码+和值约束出号里取7个/8个
        red7 = sorted(set(bank[:5]) | set(n for f in fronts[:4] for n in f))[:7]
        red8 = sorted(set(bank[:5]) | set(n for f in fronts[:4] for n in f))[:8]
        # 蓝球: 2蓝 = 高频前2
        blue2 = sorted(blue_cnt.most_common(2))[:2] if False else [c for c, _ in blue_cnt.most_common(2)]
        b16 = list(range(1, 17))
        # 10 种形式数据
        forms = []
        # 1 单式
        forms.append({"name": "单式投注", "desc": f"红球：{'、'.join(f'{x:02d}' for x in base_red)}\n蓝球：{base_blue:02d}",
                      "note": "1注, 2元", "expand": []})
        # 2 红球复式 7+1
        n71 = _comb(7, 6)
        forms.append({"name": "红球复式：7+1", "desc": f"红球：{'、'.join(f'{x:02d}' for x in red7)}\n蓝球：{base_blue:02d}",
                      "note": f"C(7,6)={n71}注, {n71*2}元",
                      "expand": [sorted(c) for c in _it.combinations(red7, 6)], "blue": base_blue})
        # 3 红球复式 8+1
        n81 = _comb(8, 6)
        forms.append({"name": "红球复式：8+1", "desc": f"红球：{'、'.join(f'{x:02d}' for x in red8)}\n蓝球：{base_blue:02d}",
                      "note": f"C(8,6)={n81}注, {n81*2}元",
                      "expand": [sorted(c) for c in _it.combinations(red8, 6)], "blue": base_blue})
        # 4 蓝球复式 6+2
        n62 = 2
        forms.append({"name": "蓝球复式：6+2", "desc": f"红球：{'、'.join(f'{x:02d}' for x in base_red)}\n蓝球：{'、'.join(f'{x:02d}' for x in blue2)}",
                      "note": f"{n62}注, {n62*2}元",
                      "expand": [dict(red=base_red, blue=b) for b in blue2]})
        # 5 蓝球复式 6+16全蓝
        n616 = 16
        forms.append({"name": "蓝球复式：6+16全蓝", "desc": f"红球：{'、'.join(f'{x:02d}' for x in base_red)}\n蓝球：全包16个",
                      "note": f"{n616}注, {n616*2}元",
                      "expand": [dict(red=base_red, blue=b) for b in b16][:4]})
        # 6 全复式 7+2
        n72 = _comb(7, 6) * 2
        forms.append({"name": "全复式：7+2", "desc": f"红球：{'、'.join(f'{x:02d}' for x in red7)}\n蓝球：{'、'.join(f'{x:02d}' for x in blue2)}",
                      "note": f"C(7,6)×2={n72}注, {n72*2}元"})
        # 7 全复式 8+2
        n82 = _comb(8, 6) * 2
        forms.append({"name": "全复式：8+2", "desc": f"红球：{'、'.join(f'{x:02d}' for x in red8)}\n蓝球：{'、'.join(f'{x:02d}' for x in blue2)}",
                      "note": f"C(8,6)×2={n82}注, {n82*2}元"})
        # 8 胆拖 4胆4拖+1蓝
        bank4 = sorted(bank[:4])
        drag4 = sorted(n for n in red8 if n not in bank4)[:4]
        n44 = _comb(4, 2)
        forms.append({"name": "胆拖投注：4胆4拖+1蓝", "desc": f"红球胆码：{'、'.join(f'{x:02d}' for x in bank4)}\n红球拖码：{'、'.join(f'{x:02d}' for x in drag4)}\n蓝球：{base_blue:02d}",
                      "note": f"C(4,2)={n44}注, {n44*2}元",
                      "expand": [sorted(bank4 + list(c)) for c in _it.combinations(drag4, 2)], "blue": base_blue})
        # 9 胆拖 3胆7拖+1蓝
        bank3 = sorted(bank[:3])
        drag7 = sorted(n for n in red8 for n in set(range(1,34)) if n not in bank3 and n not in drag4)[:7]
        drag7 = sorted(set(n for n in range(1,34) if n not in bank3) | set(drag7))[:7]
        n37 = _comb(7, 3)
        forms.append({"name": "胆拖投注：3胆7拖+1蓝", "desc": f"红球胆码：{'、'.join(f'{x:02d}' for x in bank3)}\n红球拖码：{'、'.join(f'{x:02d}' for x in drag7)}\n蓝球：{base_blue:02d}",
                      "note": f"C(7,3)={n37}注, {n37*2}元",
                      "expand": [sorted(bank3 + list(c)) for c in _it.combinations(drag7, 3)][:1], "blue": base_blue})
        # 10 胆拖复式 4胆4拖+2蓝
        n442 = _comb(4, 2) * 2
        forms.append({"name": "胆拖复式：4胆4拖+2蓝", "desc": f"红球胆码：{'、'.join(f'{x:02d}' for x in bank4)}\n红球拖码：{'、'.join(f'{x:02d}' for x in drag4)}\n蓝球：{'、'.join(f'{x:02d}' for x in blue2)}",
                      "note": f"C(4,2)×2={n442}注, {n442*2}元",
                      "expand": [dict(red=sorted(bank4 + list(c)), blue=b) for c in _it.combinations(drag4, 2) for b in blue2][:4]})

        single = {"front": base_red, "back": [base_blue]}
        full_multi = {"red": red8, "blue": blue2, "combos": []}
        danchi = {"bank": bank4, "drag": drag4}
        # 存 10 种形式供展示
        forms_data = forms
    else:
        backcnt = Counter()
        for r in rows:
            for n in r["back"]:
                backcnt[n] += 1
        back_top = sorted([c for c, _ in backcnt.most_common(2)])
        if retro.get("ok") and retro["sum_shift"] != 0:
            lo, hi = target
            mean_s = srange["mean"]
            shift = (mean_s - lo) * 0.3 if retro["sum_shift"] == -1 else (hi - mean_s) * 0.3
            target = [int(lo + (shift if retro["sum_shift"]==1 else -shift)), int(hi - (shift if retro["sum_shift"]==-1 else shift))]
        fronts = _sum_constrained_front(sorted(bank[:5]), kind, target, pool=35, pick=5)
        notes = [{"front": f, "back": back_top} for f in fronts[:max(n_mandel, 2)]]
        blue_pool_used = back_top
        # 三式: 单式/复式/胆拖(前区复式=胆码5+拖码, 后区复式=back_top)
        # 基本投注: 前区5个+后区2个, 每注2元
        single = {"front": sorted(fronts[0]) if fronts else [], "back": back_top}
        # 追加投注: 同基本投注, 每注3元, 中一/二等奖额外+80%
        extra = {"front": single["front"], "back": back_top}
        # 前区复式: 前区6个+, 后区固定2个 → 注数=C(前区n,5)*1
        # 后区复式: 前区5个, 后区3个+ → 注数=1*C(后区n,2)
        # 双区复式: 前区6个+, 后区3个+ → 注数=C(前区n,5)*C(后区n,2)
        # 前区复式需≥6个: 双因子胆5 + 从历史高频码补到7个(保证和值约束出号池覆盖)
        _front_extra = [c for c, _ in Counter(n for r in rows for n in r["front"]).most_common(8)]
        front_pool = sorted(set(bank[:5]) | set(_front_extra))[:7]
        back_pool  = sorted(back_top + [b for b in range(1,13) if b not in back_top][:1])[:3]
        import itertools as _it
        from math import comb as _comb
        _fn, _bn = len(front_pool), len(back_pool)
        front_only  = {"front": front_pool, "back": back_top,
                       "note": f"前区复式: 前区{_fn}个+后区2个, 注数C({_fn},5)×1={_comb(_fn,5) if _fn>=5 else 0}"}
        back_only   = {"front": sorted(fronts[0]) if fronts else [], "back": back_pool,
                       "note": f"后区复式: 前区5个+后区{_bn}个, 注数1×C({_bn},2)={_comb(_bn,2) if _bn>=2 else 0}"}
        dual_multi  = {"front": front_pool, "back": back_pool,
                       "note": f"双区复式: 前区{_fn}个+后区{_bn}个, 注数C({_fn},5)×C({_bn},2)={_comb(_fn,5)*_comb(_bn,2) if _fn>=5 and _bn>=2 else 0}"}
        # 胆拖三型
        front_bank  = sorted(bank[:3])  # 前区1-4个胆码
        front_drag  = sorted(set(n for f in fronts for n in f if n not in front_bank))[:5]  # 拖码
        back_bank   = sorted(back_top[:1])  # 后区1个胆码
        _back_cnt = Counter(n for r in rows for n in r["back"])
        back_drag   = [b for b, _ in _back_cnt.most_common(6) if b not in back_bank][:3] or sorted(b for b in range(1,13) if b not in back_bank)[:3]  # 后区拖码(高频优先, 限1-12)
        danchi = {
            "front": {"bank": front_bank, "drag": front_drag, "back": back_top,
                      "note": f"前区胆拖: 前区胆{len(front_bank)}+拖{len(front_drag)}个, 后区{back_top}"},
            "back":  {"front": sorted(fronts[0]) if fronts else [], "bank": back_bank, "drag": back_drag,
                      "note": f"后区胆拖: 前区5个, 后区胆{back_bank}+拖{back_drag}"},
            "dual":  {"front_bank": front_bank, "front_drag": front_drag,
                     "back_bank": back_bank, "back_drag": back_drag,
                      "note": f"双区胆拖: 前区胆{len(front_bank)}+拖{len(front_drag)}, 后区胆{back_bank}+拖{back_drag}"},
        }
        full_multi = {"red": front_pool, "blue": back_pool}  # 兼容旧字段
        red_multi = front_pool

    return {
        "kind": kind,
        "kind_cn": mand["kind_cn"], "N": bess["N"],
        "top5": top5,
        "sum_range": srange["common_range"], "sum_mean": srange["mean"],
        "bayes": {"theta": bess["theta"], "ci": bess["ci95"], "all_in": bess["all_in_ci"]},
        "mandel": mand,
        "comb_total": comb["total"],
        "cost": cost,
        "notes": notes,
        "single": single,
        "extra": locals().get("extra"),
        "front_only": locals().get("front_only"),
        "back_only": locals().get("back_only"),
        "dual_multi": locals().get("dual_multi"),
        "full_multi": full_multi,
        "danchi": danchi,
        "forms": locals().get("forms_data"),
        "blue_pool_used": locals().get("blue_pool_used", []),
        "history": _history_analysis(rows, kind),
        "retro": retro if retro.get("ok") else None,
        "random": random_note(kind),
        "disclaimer": "摇奖独立, 历史统计不改变中奖概率, 任意合法组合头奖概率相同, 不构成购彩建议",
    }


def print_report(kind="ssq"):
    r = generate(kind)
    print("=" * 46)
    print(f"📊 {r['kind_cn']} 推荐报告 (基于 {r['N']} 期历史)")
    print("=" * 46)
    # 上期反推复盘(该期为什么开出这几个号 + 偏差信号)
    rt = r.get("retro")
    if rt:
        print(f"【上期反推】{rt['period']}({rt['date'][5:]}) 开出: {' '.join(rt['last_front'])} {' '.join(rt['last_back'])}")
        for reason in rt["reasons"]:
            print(f"  · {reason}")
        print(f"  → {rt['sum_signal']}")
        print(f"  ⚠️ {rt['note']}")
    print(f"\n【推荐号码】")
    for i, n in enumerate(r["notes"], 1):
        fs = " ".join(f"{x:02d}" for x in n["front"])
        bs = " ".join(f"{x:02d}" for x in n["back"])
        print(f"  {i}. 前区 {fs}  后区 {bs}")
    # 三式投注: 按彩种分叉(双色球=红蓝, 大乐透=前后区 基本/追加/复式三型/胆拖三型)
    if r["kind"] == "ssq" and r.get("forms"):
        idx = 1
        for f in r["forms"]:
            print(f"\n{idx}. {f['name']}")
            print(f"例子：")
            for line in f["desc"].split("\n"):
                print(f"  {line}")
            print(f"注数/金额： {f['note']}")
            exp = f.get("expand", [])
            if exp:
                if len(exp) <= 8:
                    print(f"展开后的{len(exp)}注红球为：")
                    for i2, e in enumerate(exp, 1):
                        if isinstance(e, dict):
                            print(f"  {i2}. 红球 {'、'.join(f'{x:02d}' for x in e['red'])}，蓝球 {e['blue']:02d}")
                        else:
                            print(f"  {i2}. {'、'.join(f'{x:02d}' for x in e)}")
                    if f.get("blue"):
                        print(f"蓝球均为：{f['blue']:02d}")
                else:
                    print(f"其中一注示例：")
                    e = exp[0]
                    if isinstance(e, dict):
                        print(f"  红球：{'、'.join(f'{x:02d}' for x in e['red'])}")
                        print(f"  蓝球：{e['blue']:02d}")
                    else:
                        print(f"  红球：{'、'.join(f'{x:02d}' for x in e)}")
                        print(f"  蓝球：{f.get('blue', '?'):02d}")
            idx += 1
    else:
        # 大乐透: 单式基本 + 复式三型 + 胆拖三型(官家11-10模板, 分隔用顿号"、")
        def _fmt(nums, width=2):
            return "、".join(f"{x:0{width}d}" for x in nums)
        if r.get("single"):
            sg = r["single"]
            print(f"\n单式基本投注")
            print(f"前区：{_fmt(sg['front'])}")
            print(f"后区：{_fmt(sg['back'])}")
        if r.get("front_only"):
            f1 = r["front_only"]
            print(f"\n前区复式投注：前区选 {len(f1['front'])}个，后区固定选2个")
            print(f"前区：{_fmt(f1['front'])}")
            print(f"后区：{_fmt(f1['back'])}")
        if r.get("back_only"):
            b1 = r["back_only"]
            print(f"\n后区复式投注：前区固定选5个，后区选 {len(b1['back'])}个")
            print(f"前区：{_fmt(b1['front'])}")
            print(f"后区：{_fmt(b1['back'])}")
        if r.get("dual_multi"):
            d1 = r["dual_multi"]
            print(f"\n双区复式：前区选{len(d1['front'])}个，后区选{len(d1['back'])}个")
            print(f"前区：{_fmt(d1['front'])}")
            print(f"后区：{_fmt(d1['back'])}")
        if r.get("danchi"):
            dc = r["danchi"]
            print(f"\n胆拖投注")
            if dc.get("front"):
                f = dc["front"]
                print(f"前区胆拖：前区选{len(f['bank'])}个胆码 + {len(f['drag'])}个拖码（合计{len(f['bank'])+len(f['drag'])}个），后区选2个")
                print(f"前区胆码：{_fmt(f['bank'])}（{len(f['bank'])}个胆码，每注都必须包含）")
                print(f"前区拖码：{_fmt(f['drag'])}（{len(f['drag'])}个拖码）")
                print(f"后区固定：{_fmt(f['back'])}")
            if dc.get("back"):
                b = dc["back"]
                print(f"后区胆拖：前区选5个，后区选{len(b['bank'])}个胆码 + {len(b['drag'])}个拖码")
                print(f"前区固定：{_fmt(b['front'])}")
                print(f"后区胆码：{_fmt(b['bank'])}（{len(b['bank'])}个胆码，每注都必须包含）")
                print(f"后区拖码：{_fmt(b['drag'])}（{len(b['drag'])}个拖码）")
            if dc.get("dual"):
                d = dc["dual"]
                print(f"双区胆拖：前区和后区同时采用胆拖方式")
                print(f"前区胆码：{_fmt(d['front_bank'])}")
                print(f"前区拖码：{_fmt(d['front_drag'])}")
                print(f"后区胆码：{_fmt(d['back_bank'])}")
                print(f"后区拖码：{_fmt(d['back_drag'])}")
    rnd = r["random"]
    # 官家11-21: 结论段(该买几注/预算/覆盖策略) — 不再只有号码, 明确告诉官家怎么买
    # 蓝球多值从 r["blue_pool_used"] 取(generate 已暴露并列全保留的蓝球池)
    _blue_all = r.get("blue_pool_used", []) or []
    print(f"\n【结论 / 购买建议】")
    if kind == "ssq":
        _bstr = '、'.join(f'{b:02d}' for b in _blue_all[:4]) if _blue_all else '见上'
        print(f"  · 本期蓝球多值: {_bstr} (高频并列全保留, 不单押1个)")
        print(f"  · 性价比之选: 单式(2元/注) 2-4 注 或 蓝球6+2复式(4元/2注) 覆盖多蓝球")
        print(f"  · 想提高命中面: 红球7+1复式(14元/7注) 或 胆拖4胆4拖(12元/6注)")
        print(f"  · 预算建议: 2-4 注(4-8元) 理性购彩, 蓝球别只押1个, 用多蓝覆盖")
    else:
        print(f"  · 性价比之选: 基本投注(2元/注) 或 追加投注(3元/注) 2-4 注")
        print(f"  · 想提高命中面: 前区复式(7前+2后) 或 前区胆拖")
        print(f"  · 预算建议: 2-4 注(4-12元) 理性购彩")
    print(f"  · 提醒: 摇奖独立, 以上结构优化只提覆盖度/成本效率, 不改变中奖概率, 量力而行")
    print(f"\n【纯随机对照(无放回,中奖概率与上面完全相同)】")
    if "front" in rnd:
        print(f"  前区 {' '.join(rnd['front'])}  后区 {' '.join(rnd['back'])}")
    else:
        print(f"  红球 {' '.join(rnd['red'])}  蓝 {rnd['blue']}")
    # 历史分析静默参与出号(高频/和值/蓝球多值已用历史算), 报告只出最终推荐, 不展示历史段
    print(f"\n⚠️ {r['disclaimer']}")


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    print_report(kind)
