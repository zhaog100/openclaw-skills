#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票推送脚本 (官家11-06 点头 P3)
开奖日 T-1 晚 19:00 推双色球/大乐透出号建议, 必带免责声明。
主路 QQ 开放平台直发, 兜底 Gateway /tools/invoke; 双路全失败写漏推标记+25min补推。
cron: 双色球 0 19 * * 1,3,6 (开奖周二/四/日→推周一/三/六)
      大乐透 0 19 * * 0,2,5 (开奖周一/三/六→推周日/二/五)
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, datetime, subprocess, pathlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

DISCLAIMER = "⚠️ 仅供参考，理性购彩。摇奖独立，历史统计不改变中奖概率，不构成购彩建议。"
TODO_FILE = os.path.expanduser("~/.openclaw/workspace/intel/待办_彩票漏推.md")
CLOG = os.path.expanduser("~/.openclaw/workspace/logs/lottery-push-cron.log")


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CLOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def generate(kind):
    """调 lottery_analysis 出号。"""
    from skills.lottery_analysis.skill import LotteryAnalysisSkill
    r = LotteryAnalysisSkill().run({"kind": kind})
    if not r.get("success"):
        log(f"{kind} 出号失败: {r.get('error')}")
        return None
    return r


def build_text(kind, r):
    """组装推送文案。"""
    lines = []
    title = {"ssq": "🔴 双色球", "dlt": "🔵 大乐透"}.get(kind, kind)
    lines.append(f"【彩票分析】{title} · {datetime.date.today().strftime('%m-%d')} 出号建议")
    if r.get("top5"):
        # top5 是最高频号码列表(非组合), random 才有完整 6+1/6+2 组合
        lines.append(f"🎯 最高频号码 Top5: {' '.join(str(x) for x in r['top5'])}")
    m = r.get("mandel")
    if m:
        if isinstance(m, dict):
            parts = []
            if m.get("bank_danger"): parts.append(f"高频候选 {' '.join(str(x) for x in m['bank_danger'])}")
            if m.get("kelly_pct") is not None:
                note = m.get("kelly_note", "")
                parts.append(f"凯利仓位 {m['kelly_pct']}%" + (f"（{note}）" if note else ""))
            lines.append("📐 曼德尔: " + " | ".join(parts))
        else:
            lines.append(f"📐 曼德尔: {m}")
    if r.get("random"):
        rd = r["random"]
        # 双色球: red(6)+blue(1) | 大乐透: red(5)+blue(2) 之类
        if isinstance(rd, dict):
            parts = []
            # 双色球: red/blue | 大乐透: front/back
            front = rd.get("red") or rd.get("front")
            back = rd.get("blue") or rd.get("back")
            if front: parts.append(f"前区 {' '.join(front)}")
            if back:
                parts.append(f"后区 {' '.join(back) if isinstance(back, (list,tuple)) else str(back)}")
            lines.append("🎲 纯随机: " + " | ".join(parts))
        else:
            lines.append(f"🎲 纯随机: {rd}")
    if r.get("sum_range"):
        lines.append(f"和值区间: {r['sum_range']}")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def push(text, kind):
    """双路推送, 全失败写标记+排程补推。返回是否成功。"""
    # 写最新文案落盘(补推用)
    latest = os.path.join(BASE, "reports", "lottery_latest.txt")
    pathlib.Path(os.path.dirname(latest)).mkdir(parents=True, exist_ok=True)
    with open(latest, "w", encoding="utf-8") as f:
        f.write(text)

    from scripts.send_qq_gw import send_via_qqbot, send_via_gateway
    sent = False
    try:
        if send_via_qqbot(text):
            sent = True
            log(f"{kind} 主路(QQ开放平台)推送成功")
        elif send_via_gateway(text):
            sent = True
            log(f"{kind} 兜底路(Gateway)推送成功")
    except Exception as e:
        log(f"{kind} 推送异常: {e}")

    if sent:
        # 清历史漏推标记
        p = pathlib.Path(TODO_FILE)
        if p.exists():
            p.unlink()
            log(f"{kind} 漏推标记已清")
        return True

    # 双路全失败: 写标记 + 25min 补推
    log(f"{kind} 双路推送全失败, 写漏推标记")
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.write(f"# 彩票漏推待办 (双路推送全失败)\n\n"
                    f"- 时间: {now}\n- 彩种: {kind}\n"
                    f"- 处理: 已排程 25min 后自动补推一次(读 {latest}); 人工可立即推 send_qq_gw.py\n")
        subprocess.Popen(
            ["nohup", "sh", "-c",
             f"sleep 1500; python3 {BASE}/scripts/send_qq_gw.py {latest} >> {CLOG} 2>&1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"{kind} 25min 补推已排程")
    except Exception as e:
        log(f"{kind} 漏推标记/补推写入异常: {e}")
    return False


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "ssq"
    log(f"===== 彩票推送启动 kind={kind} =====")
    r = generate(kind)
    if r is None:
        log(f"{kind} 出号失败, 跳过推送")
        sys.exit(1)
    text = build_text(kind, r)
    log(f"{kind} 文案已生成:\n{text}")
    push(text, kind)
    log(f"===== 彩票推送结束 kind={kind} =====")


if __name__ == "__main__":
    main()
