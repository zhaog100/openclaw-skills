#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按需拉取零售价格指数（macro_china_retail_price_index）
官方说明：该接口需循环 137 个类目，耗时 >60s，不纳入自动周报，仅手动触发。

用法: python3 retail_price_on_demand.py [--category 食品类|衣着类|]

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os, time, pickle, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_TTL = 3600 * 24  # 24h 缓存


def fetch(cache_hours=24):
    p = os.path.join(CACHE_DIR, 'retail_price.pkl')
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < cache_hours * 3600:
        with open(p, 'rb') as f:
            df = pickle.load(f)
        logger.info(f"命中缓存（{cache_hours}h 内）: {len(df)} 行")
        return df

    logger.info("开始拉取 retail_price_index（137 类目，约 2-3 分钟）...")
    import akshare as ak, requests
    t0 = time.time()
    # 全局设 requests 超时，防止卡死在某页请求
    _orig_get = requests.get
    def _timeout_get(*args, **kwargs):
        kwargs.setdefault('timeout', 15)
        return _orig_get(*args, **kwargs)
    requests.get = _timeout_get
    try:
        try:
            df = ak.macro_china_retail_price_index()
        except Exception as e:
            # 完整拉取失败 → 降级拉第一页
            logger.warning(f"完整拉取失败({str(e)[:40]})，降级第一页...")
            import json as _json, re as _re, pandas as pd
            url = "https://quotes.sina.cn/mac/api/jsonp_v3.php/SINAREMOTECALLCALLBACK1601651495761/MacPage_Service.get_pagedata"
            params = {"cate": "price", "event": "12", "from": "0", "num": "31", "condition": ""}
            r = requests.get(url, params=params, timeout=20)
            data_text = r.text
            m = _re.search(r'\((\{.*\})\)', data_text, _re.DOTALL)
            if not m:
                logger.warning("降级失败：无法解析 JSONP")
                df = None
            else:
                data_json = _json.loads(m.group(1))
                df = pd.DataFrame(data_json["data"])
                df.columns = [item[1] for item in data_json["config"]["all"]]
                df["零售商品价格指数"] = pd.to_numeric(df["零售商品价格指数"], errors="coerce")
                df = df.sort_values(by=["统计月份"], ignore_index=True)
                logger.warning(f"降级成功：仅第一页 {len(df)} 行")
    finally:
        requests.get = _orig_get

    # 若返回 None（降级失败）
    if df is None:
        return None
    with open(p, 'wb') as f:
        pickle.dump(df, f)
    logger.info(f"拉取完成 {len(df)} 行，耗时 {time.time()-t0:.1f}s")
    return df
    with open(p, 'wb') as f:
        pickle.dump(df, f)
    logger.info(f"拉取完成 {len(df)} 行，耗时 {time.time()-t0:.1f}s")
    return df


def summarize(df, category=None):
    """输出汇总"""
    if category:
        subset = df[df['item'] == category] if 'item' in df.columns else df
    else:
        subset = df

    # 找最新日期
    date_col = 'date' if 'date' in subset.columns else subset.columns[0]
    latest_date = subset[date_col].max()
    latest = subset[subset[date_col] == latest_date]

    print(f"\n=== 零售价格指数 最新（{latest_date}） ===")
    if 'category' in latest.columns and 'item' in latest.columns:
        print("【分类】")
        for _, row in latest.iterrows():
            print(f"  {row.get('category','?')} / {row.get('item','?')}")
    print("\n全表列名:", list(df.columns))
    return latest


if __name__ == '__main__':
    df = fetch()
    if df is None:
        print("⚠️ 拉取失败（接口超时），本次无数据。可稍后重试。")
        raise SystemExit(0)
    cat = None
    for i, a in enumerate(sys.argv[1:]):
        if a == '--category':
            cat = sys.argv[i+2]
    summarize(df, cat)
