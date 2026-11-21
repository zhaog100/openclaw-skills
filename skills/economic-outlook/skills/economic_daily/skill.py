#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
economic_daily 微技能（单一职责）
经济分析报告(全维度) → 报告落盘 + 走 send_qq_gw.py 门面统一推送

接入门面: 经济报告是门面之后开发的, 之前没接进来, 现在补上
跟 oil_gold / lottery_analysis 同构: 出报告 + 落盘 + send_qq_gw 门面推送

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from skills.base import BaseSkill


class EconomicDailySkill(BaseSkill):
    name = "economic_daily"
    description = "经济形势日报: 全维度报告生成+落盘+send_qq_gw门面统一推送"
    version = "1.0.0"
    depends_on: list = []

    def _find_send_qq_gw(self) -> str:
        """定位 send_qq_gw.py 门面(全候选扫描, 找不到明标不静默)。"""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    def run(self, context: dict) -> dict:
        # 调 report_text.py 的 generate_report 出全维度经济报告
        # skill.py 在 skills/economic_daily/ 下, 往上 3 层到 economic-outlook/
        # (1) economic_daily (2) skills (3) economic-outlook
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scripts = os.path.join(base, "scripts")
        for p in (base, scripts):
            if p not in sys.path:
                sys.path.insert(0, p)
        out = {"success": False}
        try:
            # report_text 及其依赖(fetch_macro/policy_engine/macro_model/forecast)都在 scripts/ 下
            if scripts not in sys.path:
                sys.path.insert(0, scripts)
            import importlib
            report_text = importlib.import_module("report_text")
            text = report_text.generate_report()
            out["success"] = True
            out["report_len"] = len(text) if text else 0
            # 报告落盘(跟油金 report_text_latest 同构)
            data_dir = os.path.join(base, "data")
            os.makedirs(data_dir, exist_ok=True)
            rp = os.path.join(data_dir, "economic_daily_report.txt")
            with open(rp, "w", encoding="utf-8") as f:
                f.write(text)
            out["report_path"] = rp
        except Exception as e:
            out["error"] = str(e)[:120]
            out["report_path"] = ""
            out["push"] = {"sent": False, "note": f"报告生成失败: {str(e)[:60]}"}
            return out
        # 门面统一推送(send_qq_gw.py, open_id 回落链: context > 环境变量 > 不硬编码)
        target = context.get("qq_target_user_id") or os.environ.get("QQ_TARGET_USER_ID", "")
        out["push"] = {"channel": "qqbot", "method": "send_qq_gw.py (门面统一推送)", "unified": True}
        gw = self._find_send_qq_gw()
        if target and out.get("report_path") and gw:
            import subprocess
            env = dict(os.environ)
            env["QQ_TARGET_USER_ID"] = target
            try:
                rr = subprocess.run(["python3", gw, out["report_path"]], env=env,
                                     timeout=120, capture_output=True, text=True)
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
    s = EconomicDailySkill()
    ctx = {"qq_target_user_id": os.environ.get("QQ_TARGET_USER_ID", "")}
    r = s.run(ctx)
    print(json.dumps(r, ensure_ascii=False))
