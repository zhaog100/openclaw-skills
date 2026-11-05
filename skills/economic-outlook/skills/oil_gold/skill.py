#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析平台 V3.1 — oil_gold 微技能（石油黄金相关性分析适配器）

把 oil-gold-correlation skill 的 analysis.py 包成门面平台的一个微技能，
registry 自动发现后与 18 个微技能并列。单一职责：只做石油黄金相关性分析。

输出 = analysis.run_all() 的结构化 dict + 报告文本路径。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os
from skills.base import BaseSkill

# 石油黄金 skill 实际路径（workspace 下，用相对定位避免硬编码绝对路径）
def _oil_gold_dir() -> tuple:
    """油金报告源真实位置。返回 (dir, unavailable_reason):
    · dir: 找到的油金目录(可能为 ""), reason: 找不到时布局不符的明标原因(官家11-05修: 不再静默降级)
    全候选扫描, 兼容多种布局(平级顶层 / workspace/skills 下 / economic-outlook 内嵌套)。"""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # base = .../economic-outlook; 往上推各级候选 workspace 根
    cands = []
    for i in range(1, 5):
        cands.append(os.path.join(base + os.sep + os.path.join("..",), "oil-gold-correlation"))
    # 用 os.path 规整地推: base 的各级父目录 + 各级父目录下的 skills/
    seen = set()
    for n in range(1, 6):
        parent = base
        for _ in range(n - 1):
            parent = os.path.dirname(parent)
        for cand in (os.path.join(parent, "oil-gold-correlation"),
                     os.path.join(parent, "skills", "oil-gold-correlation")):
            if cand not in seen:
                seen.add(cand)
                cands.append(cand)
    for cand in cands:
        if os.path.isdir(cand):
            return cand, ""
    # 全找不到 → 明标布局不符(不静默, 官家红线: 拉取失败必须显式标记)
    tried = "; ".join(cands[:6])
    reason = (f"oil-gold-correlation 目录不存在(解包布局不符: 需摆成 workspace/skills/economic-outlook "
              f"+ workspace/oil-gold-correlation 或 workspace 顶层并排; 已试 {tried[:200]})")
    return "", reason


class OilGoldSkill(BaseSkill):
    name = "oil_gold"
    description = "石油黄金相关性分析：多周期 Pearson/Spearman/Granger/协整 + 多周期共振结论"
    version = "1.0.0"
    depends_on: list = []

    def run(self, context: dict) -> dict:
        import sys
        import importlib.util
        og, _missing_reason = _oil_gold_dir()
        if not og:
            # 官家11-05: 找不到油金目录 = 布局不符, 明标 unavailable_reason(不静默降级, 守红线)
            return {"success": False, "error": "oil-gold-correlation 目录不存在(布局不符)",
                    "degraded": True, "__unavailable__": True,
                    "unavailable_reason": _missing_reason}
        scripts = os.path.join(og, "scripts")
        # 把 oil-gold 的 scripts 挂进 sys.path（临时，失败隔离）
        for p in [scripts, os.path.join(og, "reports")]:
            if p not in sys.path:
                sys.path.insert(0, p)

        out = {"success": True, "period": "7d", "method": "all",
               "report_text_path": os.path.join(og, "reports", "report_text_latest.txt")}

        # 1. 相关性分析（结构化 dict）
        try:
            spec = importlib.util.spec_from_file_location(
                "oil_analysis", os.path.join(scripts, "analysis.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result = mod.run_all(context.get("df"), window=context.get("window", 30)) \
                if context.get("df") is not None else None
            if result is None:
                # 无预置 df 时走脚本自拉数据（降级：抓不到就标占位不崩）
                out["correlation"] = {"status": "pending",
                                       "note": "需 analysis.py --period 自拉数据，门面无预置 df"}
            else:
                out["correlation"] = result
        except Exception as e:
            out["correlation"] = {"status": "degraded", "error": str(e)[:80]}
            out["success"] = True  # 失败隔离：单项降级不判整体失败

        # 2. 报告文本生成路径（默认走子进程跑 report_text.py 落盘，最稳）
        out["report_text"] = "未生成"
        out["report_generated"] = False

        # 3. 生成报告文本：用子进程独立跑 report_text.py（它内部自拉数据+写盘），失败隔离
        #    比 import 调 main() 更稳——主模块依赖 sys.argv/相对路径，子进程等价于老 cron 链路
        try:
            import subprocess, os as _os
            env = dict(_os.environ)
            env.setdefault("PYTHONPATH",
                           _os.path.join(_os.environ.get("HOME", ""), ".local/lib/python3.12/site-packages"))
            rep_proc = subprocess.run(
                ["python3", os.path.join(scripts, "report_text.py")],
                cwd=scripts, env=env, timeout=600,
                capture_output=True, text=True)
            if rep_proc.returncode == 0 and os.path.exists(out["report_text_path"]):
                out["report_text"] = "已生成"
                out["report_generated"] = True
            else:
                out["report_text"] = f"生成失败(rc={rep_proc.returncode}): {rep_proc.stderr[:80]}"
        except Exception as e:
            out["report_text"] = f"生成异常: {str(e)[:80]}"
        # 降级：若本次没生成但旧报告文件在，仍可推旧报告（标注陈旧）
        if not out["report_generated"] and os.path.exists(out["report_text_path"]):
            out["report_stale"] = True
            out["report_text"] = out.get("report_text", "") + "（推送旧报告，陈旧）"

        # 4. QQ 推送（门面统一推送：走 send_qq_gw.py，open_id 从 context/env 读）
        # 回落链：context > 环境变量 > config/oil_gold.json（不硬编码 open_id 进代码）
        target = context.get("qq_target_user_id") or os.environ.get("QQ_TARGET_USER_ID", "")
        if not target:
            try:
                _cf = os.path.expanduser("~/.openclaw/workspace/config/oil_gold.json")
                import json as _json
                _cd = _json.load(open(_cf, encoding="utf-8"))
                target = _cd.get("qq_target_user_id", "")
            except Exception:
                pass
        out["push"] = {"channel": "qqbot", "method": "send_qq_gw.py (Gateway REST)",
                       "unified": True}
        if target and os.path.exists(out["report_text_path"]):
            try:
                import subprocess, os as _os
                env = dict(_os.environ)
                env["QQ_TARGET_USER_ID"] = target
                r = subprocess.run(["python3", os.path.join(scripts, "send_qq_gw.py"), out["report_text_path"]],
                                   env=env, timeout=120, capture_output=True, text=True)
                out["push"]["sent"] = r.returncode == 0
                out["push"]["note"] = "门面统一推送成功" if r.returncode == 0 else f"推送异常: {r.stderr[:60]}"
            except Exception as e:
                out["push"]["sent"] = False
                out["push"]["note"] = f"推送失败: {str(e)[:60]}"
        else:
            out["push"]["sent"] = False
            out["push"]["note"] = "无 open_id 目标或报告未生成，跳过推送（不硬编码）"

        # 5. [退役 官家10-22] 旧 _gold_price_alert(读 support/resistance 固定档) 由
        #    gold_watch_signal + gold_watch_outcome 两个 BaseSkill 取代(动态买卖点/回本线/点差, 走门面)
        #    保留本调用作降级兜底: 仅当显式传旧 gold_watch 且无新技能时才走
        watch = context.get("gold_watch")
        if watch and target and not self._new_gold_watch_available():
            out["price_alert"] = _gold_price_alert(watch, out)
        return out


def _gold_price_alert(watch: dict, out: dict) -> dict:
    """区间盯价：沪金触到 watch 里设的支撑/止损/阻力才生成提醒（不触发不推）。

    watch 结构: {support, stop_loss, resistance, last_alert_key}
    返回 {triggered, reason, price, msg}
    """
    # 当前沪金价：从报告文本或 out 里取
    price = None
    import re
    rpt = out.get("report_text_path") or ""
    if rpt and os.path.exists(rpt):
        with open(rpt, encoding="utf-8", errors="ignore") as f:
            m = re.search(r"黄金 ¥([0-9,.]+)", f.read())
            if m:
                price = float(m.group(1).replace(",", ""))
    if price is None:
        return {"triggered": False, "reason": "无实时金价，跳过提醒"}

    alerts = []
    if watch.get("support") and price <= float(watch["support"]):
        alerts.append(f"沪金 {price:.0f} 跌到支撑 {watch['support']}，可分批买入区间下沿")
    if watch.get("stop_loss") and price <= float(watch["stop_loss"]):
        alerts.append(f"🔴 沪金 {price:.0f} 破止损 {watch['stop_loss']}，按纪律全撤")
    if watch.get("resistance") and price >= float(watch["resistance"]):
        alerts.append(f"沪金 {price:.0f} 到阻力 {watch['resistance']}，可分批卖出")

    # 去重：同一次触发的 key 不重复推（last_alert_key 由调用方存）
    key = "|".join(sorted([a[:6] for a in alerts])) or "none"
    if alerts and key == watch.get("last_alert_key"):
        return {"triggered": False, "reason": "同类提醒已发过，去重跳过", "price": price}
    if alerts:
        return {"triggered": True, "price": price, "alert_key": key,
                "msg": "🥇 黄金盯价提醒\n" + "\n".join(alerts) +
                       "\n（区间参考，非投资建议）"}
    return {"triggered": False, "reason": "未触支撑/止损/阻力", "price": price, "alert_key": key}
