"""海关总署数据适配器 — 模拟表单提交，需 Cookie，页面结构可能变动。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
import re
import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from .base import BaseAdapter, DataPoint

PARTNER_CODES = {
    "美国": "502", "欧盟": "300", "东盟": "400",
    "日本": "116", "韩国": "133", "中国香港": "101", "中国台湾": "143",
}


class CustomsAdapter(BaseAdapter):
    name = "customs"
    INDEX = "http://stats.customs.gov.cn/"
    QUERY_API = "http://stats.customs.gov.cn/queryData/queryDataByWhere"

    def __init__(self, config: dict):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._init_cookie()

    def _init_cookie(self):
        try:
            self.session.get(self.INDEX, timeout=30)
        except Exception:
            pass

    def query_trade(self, partner="美国", trade_type="出口", start_year="2024", end_year="2026"):
        partner_code = PARTNER_CODES.get(partner, partner)
        payload = {
            "pageSize": 100, "pageNum": 1, "queryType": "1", "statType": "1",
            "partnerCode": partner_code,
            "tradeType": "1" if trade_type == "出口" else "2",
            "startYear": start_year, "endYear": end_year, "currency": "1",
        }
        try:
            r = self.session.post(
                self.QUERY_API, data=payload,
                headers={**self.headers, "Content-Type": "application/x-www-form-urlencoded",
                         "Referer": self.INDEX},
                timeout=30,
            )
            r.raise_for_status()
        except Exception as e:
            print(f"[海关] 请求失败: {e}")
            return []
        try:
            rows = r.json().get("data", {}).get("list", [])
        except Exception:
            if BeautifulSoup:
                rows = self._parse_html_table(BeautifulSoup(r.text, "html.parser"))
            else:
                rows = []
        self._sleep()
        return rows

    def _parse_html_table(self, soup) -> list:
        table = soup.find("table")
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows

    def fetch(self, indicator: str, **kwargs) -> list:
        partner = kwargs.get("partner")
        if not partner and "_" in indicator:
            partner = indicator.split("_", 1)[1]
        partner = partner or "美国"

        rows = self.query_trade(partner=partner)
        points = []
        for row in rows:
            period = row.get("年份") or row.get("时间") or row.get("date", "")
            value_str = row.get("出口额") or row.get("金额") or row.get("value", "")
            if not period or not value_str:
                continue
            try:
                value = float(re.sub(r"[^\d.\-]", "", str(value_str)))
            except (ValueError, TypeError):
                continue
            points.append(DataPoint(
                indicator=indicator, period=str(period), value=value,
                unit="亿元", source="海关总署",
            ))
        return points
