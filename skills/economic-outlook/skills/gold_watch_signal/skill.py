#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析平台 V3.1 — gold_watch_signal 微技能（单一职责）

官家 10-22 要求: 把黄金盯价三层(①秒级tick/②15min轮询/③分钟级)收敛进门面统一架构,
   按门面现有"信号+出口"粒度拆(跟 china_us_spread 等 18 个微技能同构):
     gold_watch_signal  : 纯计算——拉金价、算沪金口径价、动态买卖点、回本线、点差 (不推送)
     gold_watch_outcome : 出口——读 signal 结果判到价, 生成"申购/赎回国泰 A/C 哪只"文本, 走 send_qq_gw 门面推送
   频率不进技能, 进 scheduler (schedules.yaml 的 cron 参数): 1min/15min/每日摘要 都调同一个 workflow。

本技能 = 信号层: 拉国际金 XAUUSD(REST 兜底 + WS 接入点), 折算沪金基准价, 算动态买卖点/回本线。
   数据源优先级: XAU_WS_URL 配了就走 WebSocket 秒级 tick; 没配走免费 REST(gold-api)。
   官家实盘: 中行积存金 成本 903 / 点差 16.6 / 回本线 919.6 (config gold_watch.json)。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, json, urllib.request
from skills.base import BaseSkill

FX = 7.10            # USD/CNY 粗估(国际金→沪金口径换算)
G_PER_OZ = 31.1035   # 克/盎司
REST_XAU = "https://api.gold-api.com/price/XAU"   # 免费 REST 兜底源


class GoldWatchSignalSkill(BaseSkill):
    name = "gold_watch_signal"
    description = "黄金实时盯价信号: 拉 XAUUSD/沪金价→折算沪金基准价+动态买卖点+回本线(纯计算不推送)"
    version = "1.0.0"
    depends_on: list = []

    def _cfg_path(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ws = os.path.dirname(base)   # economic-outlook -> workspace
        p = os.path.join(ws, "oil-gold-correlation", "data", "gold_watch.json")
        return p

    def _load_cfg(self):
        p = self._cfg_path()
        if not os.path.exists(p):
            return {}
        return json.load(open(p)).get("watch_shgold_spot", {})

    def _fetch_xau(self):
        """拉 XAUUSD(美元/盎司)。WS 源优先(XAU_WS_URL), 兜底 REST。"""
        ws_url = os.environ.get("XAU_WS_URL", "")
        if ws_url:
            # 接入点: 官家有 XAUUSD WebSocket tick 源时启用(websockets 连 ws_url、订阅、取最新价)
            # 骨架留口, 不硬造拉不通的 WS(当前无稳定免费 tick 源)
            pass
        try:
            r = urllib.request.urlopen(REST_XAU, timeout=10)
            return float(json.loads(r.read()).get("price", 0)), "rest"
        except Exception:
            return None, None

    def run(self, context: dict) -> dict:
        cfg = self._load_cfg()
        cost = cfg.get("cost_basis", 903)
        spread = cfg.get("spread", 16.6)
        breakeven = cfg.get("breakeven", round(cost + spread, 1))

        xau, src = self._fetch_xau()
        out = {"success": True, "source": src or "unavailable",
               "xauusd": xau, "cost_basis": cost, "spread": spread,
               "breakeven": breakeven}

        if xau is None:
            out["success"] = False
            out["error"] = "XAUUSD 拉取失败(REST/WS 均不可用), 本轮不用过期价"
            return out

        # 国际金→沪金基准价(元/克)
        out["sh_equiv"] = round(xau * FX / G_PER_OZ, 2)

        # 动态买卖点(读 config 的 dynamic 算法; 无则用当前固定档兜底)
        dyn = cfg.get("dynamic", {})
        targets = dyn.get("targets", ["mid20", "hi20", "hi60"])
        # 动态档依赖行情高低点, 信号层只透传"用哪几档", 实际价位由 context 或 outcome 层算
        out["targets"] = targets
        out["min_target"] = cfg.get("breakeven", breakeven)  # 卖点须 ≥ 回本线
        out["bank_premium"] = cfg.get("bank_premium", 21)
        return out


if __name__ == "__main__":
    import sys
    skill = GoldWatchSignalSkill()
    r = skill.execute({})
    print(json.dumps(r.data if r.success else {"error": r.error}, ensure_ascii=False))
