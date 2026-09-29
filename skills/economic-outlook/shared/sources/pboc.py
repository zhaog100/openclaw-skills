"""中国人民银行数据适配器 — 社融三级跳（索引→年份→专题→xls），M2 建议走 akshare。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
import io
import re
import requests
import pandas as pd
from .base import BaseAdapter, DataPoint


class PBOCAdapter(BaseAdapter):
    name = "pboc"
    BASE = "https://www.pbc.gov.cn"
    SOCIAL_FINANCING_INDEX = f"{BASE}/diaochatongjisi/116219/116319/index.html"
    MONEY_SUPPLY_INDEX = f"{BASE}/diaochatongjisi/116219/116319/index.html"

    def __init__(self, config: dict):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get_text(self, url: str, timeout: int = 30) -> str:
        r = self.session.get(url, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text

    def _abs_url(self, href: str) -> str:
        return href if href.startswith("http") else self.BASE + href

    def fetch_social_financing(self, year=None) -> list:
        """社融采集：索引页 → 年份页 → 专题页 → xls。链路长，fail-fast。"""
        index_html = self._get_text(self.SOCIAL_FINANCING_INDEX)
        years = re.findall(r'href=["\']([^"\']+)["\'][^>]*>\s*(\d{4})年统计数据\s*</a>', index_html)
        if not years:
            raise RuntimeError("央行索引页未找到「XXXX年统计数据」链接")
        year_map = {int(y): href for href, y in years}
        target = max(year_map) if year is None else year
        if target not in year_map:
            raise ValueError(f"央行无 {target} 年数据")

        year_html = self._get_text(self._abs_url(year_map[target]))
        topics = re.findall(r'href=["\']([^"\']+)["\'][^>]*>\s*(社会融资规模)\s*</a>', year_html)
        if not topics:
            raise RuntimeError(f"{target} 年页未找到「社会融资规模」专题")

        topic_html = self._get_text(self._abs_url(topics[0][0]))
        books = re.findall(r'href=["\']([^"\']+\.xlsx?)["\']', topic_html)
        if not books:
            raise RuntimeError(f"{target} 年社融专题页未找到 xls 附件")

        content = self.session.get(self._abs_url(books[0]), headers=self.headers, timeout=60).content
        raw = pd.read_excel(io.BytesIO(content), header=None)

        start = None
        for i in range(len(raw)):
            if str(raw.iloc[i, 0]).strip() == "月份":
                start = i
                break
        if start is None:
            raise RuntimeError(f"{target} 年社融表没有独立的「月份」表头单元格")

        points = []
        for i in range(start + 1, len(raw)):
            row = raw.iloc[i]
            month_str = str(row.iloc[0]).strip()
            if not month_str or month_str == "nan":
                continue
            m = re.search(r"(\d+)", month_str)
            if not m:
                continue
            month = int(m.group(1))
            if month < 1 or month > 12:
                continue
            try:
                value = float(row.iloc[1])
            except (ValueError, TypeError, IndexError):
                continue
            points.append(DataPoint(
                indicator="社融", period=f"{target}{month:02d}",
                value=value, unit="亿元", source="中国人民银行",
            ))
        return points

    def fetch_money_supply(self) -> list:
        """M2/M1/M0：央行页面复杂，建议优先用 akshare macro_china_money_supply。"""
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) , "scripts"))
            import fetch_macro
            m2 = fetch_macro.fetch_m2()
            if m2 is not None and len(m2):
                points = []
                for _, row in m2.iterrows():
                    for col, ind in [
                        ("货币和准货币(M2)-同比增长", "m2"),
                        ("货币(M1)-同比增长", "m1"),
                    ]:
                        if col in m2.columns and pd.notna(row.get(col)):
                            points.append(DataPoint(
                                indicator=ind,
                                period=str(row.get("月份", "")),
                                value=float(row[col]),
                                source="akshare(央行)",
                            ))
                return points
        except Exception:
            pass
        return []

    def fetch(self, indicator: str, **kwargs) -> list:
        if indicator == "社融":
            try:
                return self.fetch_social_financing(year=kwargs.get("year"))
            except Exception as e:
                print(f"[央行] 社融采集失败: {e}")
                return []
        if indicator in ("m1", "m2", "m0"):
            return self.fetch_money_supply()
        return []
