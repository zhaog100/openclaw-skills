# 石油黄金报告技能 · 跨平台版 (官家11-02 22:21 合并定稿)

## 快速开始 (任何机器, 跨平台)
    pip install -r requirements.txt      # numpy/pandas/scipy/akshare
    python3 scripts/report_text.py        # 门面入口
    # 或 bash scripts/run_report.sh

## 跨平台配置 (缺省=自动探测, 不设也能跑)
    OIL_GOLD_CACHE_DIR      缓存目录 (Windows 无 /tmp 时设, 默认系统临时目录/oil_gold_cache)
    OIL_GOLD_SKILLS_ROOT    盯价 skill 根 (跨机部署时设; 同 workspace 布局自动探测)

## 黄金取价五级降级链 (本机最全, 海外 IP 也能跑)
1. 东财 118.AU9999 实时现货 (https, f43 量级自适应)
2. 金投网 JO_71 q5 现货
3. 上金所官网挂牌 akshare spot_quotations_sge
4. 上金所官网直连 /graph/quotations (与 3 互校取更新)
5. 全挂 → 盯价实时主链 (OIL_GOLD_SKILLS_ROOT 探测) → 仍无则退日线, 黄金标「期货口径, 现货不可用偏高~22元」

## 验证 (11-02 实拉)
    gold:   836  现货(Au9999·akshare)
    silver: 11885  日线·2026-11-02收盘

## 版权
MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
