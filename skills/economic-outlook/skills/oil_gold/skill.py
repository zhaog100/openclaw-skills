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
def _oil_gold_dir() -> str:
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ws = os.path.dirname(base)  # skills/ -> workspace
    p = os.path.join(ws, "oil-gold-correlation")
    return p if os.path.isdir(p) else ""


class OilGoldSkill(BaseSkill):
    name = "oil_gold"
    description = "石油黄金相关性分析：多周期 Pearson/Spearman/Granger/协整 + 多周期共振结论"
    version = "1.0.0"
    depends_on: list = []

    def run(self, context: dict) -> dict:
        import sys
        import importlib.util
        og = _oil_gold_dir()
        if not og:
            return {"success": False, "error": "oil-gold-correlation 目录不存在",
                    "degraded": True}
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

        # 2. 报告文本（若已生成则带上路径）
        if os.path.exists(out["report_text_path"]):
            out["report_text"] = "已生成"
        else:
            out["report_text"] = "未生成（需先跑 report_text.py）"

        # 3. 生成报告文本（复用石油黄金 report_text.py，失败隔离）
        try:
            spec2 = importlib.util.spec_from_file_location(
                "oil_report", os.path.join(scripts, "report_text.py"))
            rep_mod = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(rep_mod)
            rep_mod.main() if hasattr(rep_mod, "main") else None
        except Exception as e:
            out["report_text"] = f"生成失败: {str(e)[:60]}"
            out["correlation"]["status"] = out.get("correlation", {}).get("status", "degraded")

        # 4. QQ 推送（门面统一推送：走 send_qq_gw.py，open_id 从 context/env 读）
        target = context.get("qq_target_user_id") or os.environ.get("QQ_TARGET_USER_ID", "")
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
        return out
