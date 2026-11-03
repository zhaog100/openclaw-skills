#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# -*- coding: utf-8 -*-
"""
经济分析平台 V3.1 - lottery_analysis 微技能 (大乐透/双色球数理分析适配器)

核心代码(统计/曼德尔/公式/综合出号)与本适配器同目录(A方案, 官家11-03 18:02), 包成门面平台的一个微技能,
registry 自动发现后与 oil_gold 等微技能并列。单一职责: 只做彩票 5 项数理统计
(卡方独立性/奇偶比/大小比/和值分布/连号), 摇奖独立不预测, 输出带免责声明。

照 oil_gold 适配器写法: 子进程跑 combined_ticket.py dlt|ssq(统计+曼德尔+纯随机综合出号), 失败隔离, 门面统一推送。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from skills.base import BaseSkill


def _lottery_dir() -> str:
    """核心代码与 skill.py 同目录(A方案, 官家11-03 18:02: 核心代码直接挪进门面微技能目录)"""
    p = os.path.dirname(os.path.abspath(__file__))
    return p if os.path.isfile(os.path.join(p, "lottery_stats.py")) else ""


class LotteryAnalysisSkill(BaseSkill):
    name = "lottery_analysis"
    description = "大乐透/双色球 5 项数理统计(卡方独立性/奇偶比/大小比/和值分布/连号), 摇奖独立不预测"
    version = "1.0.0"
    depends_on: list = []

    def run(self, context: dict) -> dict:
        kind = context.get("kind", "dlt")
        out = {"success": False, "kind": kind,
               "kind_cn": "大乐透" if kind == "dlt" else "双色球"}
        og = _lottery_dir()
        if not og:
            out["error"] = "lottery-analysis 目录不存在"
            out["degraded"] = True
            return out
        # A方案: 综合出号入口(统计+曼德尔+纯随机), 回退到纯统计
        script = os.path.join(og, "combined_ticket.py")
        if not os.path.exists(script):
            script = os.path.join(og, "lottery_stats.py")
        if not os.path.exists(script):
            out["error"] = "combined_ticket.py/lottery_stats.py 不存在"
            out["degraded"] = True
            return out

        # 1. 子进程跑统计(独立, 等价老 cron 链路, 最稳)
        import subprocess
        env = dict(os.environ)
        env.setdefault("PYTHONPATH",
                       os.path.join(os.environ.get("HOME", ""), ".local/lib/python3.12/site-packages"))
        try:
            proc = subprocess.run(["python3", script, kind],
                                  cwd=og, env=env, timeout=120,
                                  capture_output=True, text=True)
            out["stdout"] = proc.stdout.strip()
            out["success"] = proc.returncode == 0
            if proc.returncode != 0:
                out["error"] = (proc.stderr or "").strip()[-120:]
        except Exception as e:
            out["success"] = False
            out["error"] = str(e)[:80]

        # 2. 关键指标结构化抽取(卡方/期数), 便于门面下游消费
        if out["success"]:
            import re
            txt = out["stdout"]
            m = re.search(r"χ²\s*=\s*([\d.]+)", txt)
            out["chi2"] = float(m.group(1)) if m else None
            m = re.search(r"p\s*=\s*([\d.]+)\s*→\s*(\S+)", txt)
            out["p_val"] = float(m.group(1)) if m else None
            out["chi_verdict"] = m.group(2) if m else None
            m = re.search(r"共\s*(\d+)\s*期", txt)
            out["periods"] = int(m.group(1)) if m else None
            out["disclaimer"] = "摇奖独立, 历史分布不预测未来, 不构成购彩建议, 彩票本质是随机游戏"
        return out
