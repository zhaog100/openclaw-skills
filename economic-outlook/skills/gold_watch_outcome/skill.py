#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析平台 V3.1 — gold_watch_outcome 微技能（出口层，单一职责）

读 gold_watch_signal 结果, 判到价→生成"申购/赎回国泰 A/C 哪只基金、多少钱"操作文本,
统一走门面 send_qq_gw.py 推送(open_id 走 QQ_TARGET_USER_ID, 不硬编码)。

跟 fund_outcome 同构: 出口层不拉数据(数据来自 depends_on 的 signal), 只判断+生成+推送。
频率/静默由调用方(cron/scheduler)控制, 本技能每次跑都"判到价才推、未破档返回静默标记"。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, json, datetime, tempfile, subprocess
from skills.base import BaseSkill

FX = 7.10
G_PER_OZ = 31.1035


class GoldWatchOutcomeSkill(BaseSkill):
    name = "gold_watch_outcome"
    description = "黄金盯价出口: 读 signal 判到价→生成申购/赎回国泰 A/C 操作文本, 走 send_qq_gw 推送"
    version = "1.0.0"
    depends_on = ["gold_watch_signal"]
    inputs_schema = {"gold_watch_signal": {}}

    def _cfg(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        p = os.path.join(os.path.dirname(base), "oil-gold-correlation", "data", "gold_watch.json")
        return json.load(open(p)).get("watch_shgold_spot", {}) if os.path.exists(p) else {}

    def _gw_path(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        p = os.path.join(os.path.dirname(base), "oil-gold-correlation", "scripts", "send_qq_gw.py")
        return p

    def run(self, context: dict) -> dict:
        cfg = self._cfg()
        cost = cfg.get("cost_basis", 903)
        spread = cfg.get("spread", 16.6)
        breakeven = cfg.get("breakeven", 919.6)
        fund = cfg.get("fund", {"A": "000218", "C": "004253"})

        # 读 signal 结果
        sig = context.get("gold_watch_signal") or {}
        if not sig.get("success"):
            return {"triggered": False, "reason": "signal 拉价失败, 跳过(不用过期价)",
                    "xauusd": sig.get("xauusd")}
        xau = sig.get("xauusd")
        if not xau:
            return {"triggered": False, "reason": "无实时金价, 静默", "xauusd": None}
        # 基准价对齐 signal 层: 有实盘价(中行客户买入价)就用它, 否则退回 sh_equiv(XAUUSD 折算)
        # 官家10-28: 破档判定锚"上金所Au9999现货"(东财118.AU9999), 不用国际金折算价(虚高~15元)
        sh = sig.get("boc_buy") or sig.get("au0_realtime") or sig.get("sh_equiv", round(xau * FX / G_PER_OZ, 2))
        price_basis = sig.get("price_basis", "sge_au9999_spot" if sig.get("au0_realtime") else ("boc_spot" if sig.get("boc_buy") else "xau_conv"))

        # 动态买卖点(读 signal 透传的 target 结构 + 当前行情高低点)
        # 简化: 用当前 sh 附近的固定档位(903 成本/919.6 回本线对应), 精确动态值由 signal 算
        # 动态均线档: 优先用 signal 层算出的动态档(dyn_buy1/2/dyn_sell1/2, 滚 20/60 日高低点)
        #            signal 拉不到 au0 才退回 config 固定档兜底
        buy1 = sig.get("dyn_buy1") or cfg.get("buy1", 882)
        buy2 = sig.get("dyn_buy2") or cfg.get("buy2", 877)
        sell1 = sig.get("dyn_sell1") or cfg.get("sell1", 951)
        sell2 = sig.get("dyn_sell2") or cfg.get("sell2", 1007)
        tier_mode = "dynamic" if sig.get("dyn_buy1") else "fixed"
        if sig.get("au0_realtime"):
            sh = sig["au0_realtime"]
        elif sig.get("sh_equiv"):
            sh = sig["sh_equiv"]
        else:
            sh = sig.get("boc_buy") or sig.get("au0_last") or (xau * FX / G_PER_OZ if xau else None)
            tier_mode = "fixed"
        if sh is None:
            return {"triggered": False, "reason": "无可用金价(signal 未出基准价), 静默", "xauusd": xau}

        msgs, triggered = [], False
        trend_state = sig.get("trend_state", "横盘")
        # 趋势过滤器(官家 10-24): 跌势中破档=防半山腰, 文案升级需官家确认
        def _buy_tag(buy_ref, amt_desc):
            if trend_state in ("跌势", "downtrend"):
                return f"⚠️ 沪金≈¥{sh:.0f}/克, 破{buy_ref}买点(跌势中,MA20斜率下行/RSI弱势,防半山腰) → 申购 {fund.get('A','国泰A')} {amt_desc} 需官家确认"
            return f"⚡️ 沪金≈¥{sh:.0f}/克, 破{buy_ref}买点 → 申购 {fund.get('A','国泰A')} {amt_desc}"
        if sh <= buy2:
            msgs.append(_buy_tag("第3笔", "第3笔(低位重仓30%)")); triggered = True
        elif sh <= buy1:
            msgs.append(_buy_tag("第2笔", "第2笔(40%)")); triggered = True
        elif sh >= sell2:
            msgs.append(f"⚡️ 沪金≈¥{sh:.0f}/克, 到卖点{sell2} → 赎回 {fund.get('C','国泰C')} 波段仓(清掉)"); triggered = True
        elif sh >= sell1:
            msgs.append(f"⚡️ 沪金≈¥{sh:.0f}/克, 到卖点{sell1} → 赎回 {fund.get('C','国泰C')} 减1/3"); triggered = True

        out = {"triggered": triggered, "sh_equiv": sh, "cost_basis": cost,
               "breakeven": breakeven, "spread": spread, "tier_mode": tier_mode,
               "dyn": {"buy1": buy1, "buy2": buy2, "sell1": sell1, "sell2": sell2},
               "trend_state": trend_state,
               "source": sig.get("source"), "price_basis": sig.get("price_basis")}
        if not triggered:
            trend_note = "(跌势中,防半山腰)" if trend_state in ("跌势", "downtrend") else ""
            out["reason"] = (f"沪金 {sh:.0f} 未破买点二档 {buy2} 也未到卖点一档 {sell1}"
                             f"{trend_note} (成本{cost}/回本线{breakeven}), 静默")
            return out

        # 推门面 send_qq_gw.py (open_id 走 env)
        target = os.environ.get("QQ_TARGET_USER_ID", "")
        out["push"] = {"sent": False}
        if target:
            gw = self._gw_path()
            if os.path.exists(gw):
                tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                tmp.write("\n".join(msgs) + f"\n({now} 上金所Au9999现货≈¥{sh:.2f}/克, 实盘按上金所现货价)\n⚠️ 仅供参考, 不构成投资建议")
                tmp.close()
                try:
                    r = subprocess.run(["python3", gw, tmp.name],
                                       env=dict(os.environ), timeout=120, capture_output=True)
                    out["push"]["sent"] = (r.returncode == 0)
                    out["push"]["note"] = "门面推送成功" if r.returncode == 0 else f"异常:{r.stderr[:60]}"
                except Exception as e:
                    out["push"]["note"] = f"推送异常:{str(e)[:60]}"
                finally:
                    os.unlink(tmp.name)
        else:
            out["push"]["note"] = "无 open_id 目标, 跳过推送(不硬编码)"
        out["alerts"] = msgs
        return out


if __name__ == "__main__":
    import sys
    # 独立跑: 先跑 signal 再喂 outcome
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from skills.gold_watch_signal.skill import GoldWatchSignalSkill
    sig = GoldWatchSignalSkill().execute({})
    res = GoldWatchOutcomeSkill().execute({"gold_watch_signal": sig.data})
    print(json.dumps(res.data if res.success else {"error": res.error}, ensure_ascii=False))
