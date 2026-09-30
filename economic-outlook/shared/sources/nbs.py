"""国家统计局数据适配器（新版 V3.1 API）— cid 需实际运行填充。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
import json
import requests
from .base import BaseAdapter, DataPoint

# 预设 cid 映射（需实际调用 queryIndexTreeAsync 后填充 UUID）
PRESET_CIDS = {
    "gdp":       {"cid": "", "indicator_ids": [], "freq": "Q"},
    "cpi":       {"cid": "", "indicator_ids": [], "freq": "M"},
    "ppi":       {"cid": "", "indicator_ids": [], "freq": "M"},
    "社零":      {"cid": "", "indicator_ids": [], "freq": "M"},
    "固投":      {"cid": "", "indicator_ids": [], "freq": "M"},
    "失业率":    {"cid": "", "indicator_ids": [], "freq": "M"},
}


class NBSAdapter(BaseAdapter):
    name = "nbs"
    BASE = "https://data.stats.gov.cn/dg/website/publicrelease/web/external"

    def __init__(self, config: dict):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_indicator(self, keyword: str, pid: str = "") -> list:
        url = f"{self.BASE}/new/queryIndexTreeAsync"
        r = self.session.get(url, params={"pid": pid, "code": keyword}, timeout=30)
        r.raise_for_status()
        nodes = r.json().get("data", {}).get("list", [])
        return [
            {"_id": n.get("_id"), "name": n.get("name"), "isLeaf": n.get("isLeaf", False)}
            for n in nodes
        ]

    def get_indicators(self, cid: str) -> list:
        url = f"{self.BASE}/new/queryIndicatorsByCid"
        r = self.session.get(url, params={"cid": cid}, timeout=30)
        r.raise_for_status()
        return r.json().get("data", {}).get("list", [])

    def query_data(self, cid: str, indicator_ids: list, start: str, end: str, freq: str = "M") -> list:
        url = f"{self.BASE}/stream/esData"
        suffix = {"M": "MM", "Q": "SS", "Y": "YY"}.get(freq, "MM")
        dts = f"{start}{suffix}-{end}{suffix}"
        payload = {"cid": cid, "indicatorIds": indicator_ids, "dts": dts, "das": [], "showType": "1"}
        r = self.session.post(
            url, json=payload,
            headers={**self.headers, "Content-Type": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("data", {}).get("list", [])

    def fetch(self, indicator: str, **kwargs) -> list:
        preset = PRESET_CIDS.get(indicator, {})
        if not preset.get("cid"):
            # 未配置 cid：尝试搜索（可能返回空）
            try:
                cands = self.search_indicator(indicator)
                if not cands:
                    return []
                leaf = next((c for c in cands if c["isLeaf"]), cands[0])
                cid = leaf["_id"]
                indicators = self.get_indicators(cid)
                indicator_ids = [i["_id"] for i in indicators[:1]]
                freq = "M"
            except Exception:
                return []
        else:
            cid = preset["cid"]
            indicator_ids = preset.get("indicator_ids", [])
            freq = preset.get("freq", "M")

        start = kwargs.get("start", "202001")
        end = kwargs.get("end", "202609")
        rows = self.query_data(cid, indicator_ids, start, end, freq)
        self._sleep()

        points = []
        for row in rows:
            for ind_id in indicator_ids:
                val = row.get(ind_id)
                if val in (None, ""):
                    continue
                try:
                    value = float(val)
                except (ValueError, TypeError):
                    continue
                points.append(DataPoint(
                    indicator=indicator,
                    period=str(row.get("dt", "")),
                    value=value,
                    source="国家统计局",
                ))
        return points
