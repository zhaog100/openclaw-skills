#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 - lottery_analysis 微技能（单一职责, 官家11-03 18:14: 跟其他微技能同构）

核心代码与 skill.py 同目录, 直接 import, 不挂外部技能。
摇奖独立不预测, 输出带免责声明。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from skills.base import BaseSkill


class LotteryAnalysisSkill(BaseSkill):
    name = "lottery_analysis"
    description = "大乐透/双色球 综合出号(统计+曼德尔+纯随机)+报告落盘+门面推送, 摇奖独立不预测"
    version = "2.0.0"
    depends_on: list = []

    def _send_qq_gw(self) -> str:
        """定位 send_qq_gw.py 门面(与油金同构: 全候选扫描, 找不到明标不静默)。"""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base = .../economic-outlook/skills/lottery_analysis → 上溯到 workspace 各级找 oil-gold-correlation
        cands = []
        for n in range(1, 6):
            parent = base
            for _ in range(n - 1):
                parent = os.path.dirname(parent)
            for cand in (os.path.join(parent, "oil-gold-correlation", "scripts", "send_qq_gw.py"),
                         os.path.join(parent, "skills", "oil-gold-correlation", "scripts", "send_qq_gw.py"),
                         os.path.join(parent, "economic-outlook", "scripts", "send_qq_gw.py"),
                         os.path.join(parent, "skills", "economic-outlook", "scripts", "send_qq_gw.py")):
                cands.append(cand)
        for c in cands:
            if os.path.isfile(c):
                return c
        return ""

    def _report_to_text(self, kind: str) -> str:
        """跑 combined_ticket.print_report 落盘成报告文本(含 10 种投注形式 + 结论段)。"""
        import subprocess, os as _os, tempfile
        base = os.path.dirname(os.path.abspath(__file__))
        env = dict(_os.environ)
        env.setdefault("PYTHONPATH", _os.path.join(_os.environ.get("HOME", ""), ".local/lib/python3.12/site-packages"))
        out_path = os.path.join(base, "..", "..", "data", f"lottery_report_{kind}.txt")
        _os.makedirs(os.path.dirname(out_path), exist_ok=True)
        r = subprocess.run(["python3", os.path.join(base, "combined_ticket.py"), kind],
                            cwd=base, env=env, timeout=180, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(r.stdout)
            return out_path
        return ""

    def run(self, context: dict) -> dict:
        # 官家11-21: 彩票接入门面调度 — 跟油金 oil_gold 同构: 出号 + 报告落盘 + send_qq_gw 统一推送
        base = os.path.dirname(os.path.abspath(__file__))
        for p in (base, os.path.dirname(base)):
            if p not in sys.path:
                sys.path.insert(0, p)
        kind = context.get("kind", "ssq")
        out = {"kind": kind}
        # ① 出号(结构化)
        try:
            import importlib
            ct = importlib.import_module("combined_ticket")
            r = ct.generate(kind)
            out.update({
                "success": True, "kind": kind, "kind_cn": r["kind_cn"], "periods": r["N"],
                "top5": r["top5"], "sum_range": r["sum_range"], "bayes": r["bayes"],
                "mandel": r["mandel"], "comb_total": r["comb_total"], "cost": r["cost"],
                "notes": r["notes"], "random": r["random"], "disclaimer": r["disclaimer"],
                "blue_pool_used": r.get("blue_pool_used", []),
            })
        except Exception as e:
            out.update({"success": False, "kind": kind, "error": str(e)[:120], "degraded": True,
                       "disclaimer": "摇奖独立, 历史统计不预测未来, 不构成购彩建议"})
            return out
        # ② 报告文本落盘(含 10 种投注形式 + 结论段, 跟油金 report_text_latest 同构)
        out["report_generated"] = False
        out["report_text_path"] = ""
        rp = self._report_to_text(kind)
        if rp and os.path.exists(rp):
            out["report_generated"] = True
            out["report_text_path"] = rp
        # ③ 门面统一推送(走 send_qq_gw.py, open_id 回落链: context > 环境变量 > 不硬编码)
        target = context.get("qq_target_user_id") or os.environ.get("QQ_TARGET_USER_ID", "")
        out["push"] = {"channel": "qqbot", "method": "send_qq_gw.py (门面统一推送)", "unified": True}
        gw = self._send_qq_gw()
        if target and out["report_text_path"] and gw:
            try:
                import subprocess, os as _os
                env = dict(_os.environ)
                env["QQ_TARGET_USER_ID"] = target
                rr = subprocess.run(["python3", gw, out["report_text_path"]],
                                    env=env, timeout=120, capture_output=True, text=True)
                out["push"]["sent"] = rr.returncode == 0
                out["push"]["note"] = "门面统一推送成功" if rr.returncode == 0 else f"推送异常: {(rr.stderr or rr.stdout)[:60]}"
            except Exception as e:
                out["push"]["sent"] = False
                out["push"]["note"] = f"推送失败: {str(e)[:60]}"
        else:
            out["push"]["sent"] = False
            out["push"]["note"] = "无 open_id / 报告未生成 / send_qq_gw 未找到, 跳过推送(不硬编码)"
        return out


if __name__ == "__main__":
    import json
    print(json.dumps(LotteryAnalysisSkill().run({}), ensure_ascii=False, indent=2))
