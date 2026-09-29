# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License

---
name: economic-outlook
description: "经济形势综合分析：多源宏观数据 + 政策引擎 + 多维评分 + 半年/1年/2年三情景预测。周报推送 QQ。"
version: 1.1.0
author: 小米椒 🌶️
lessons_updated: 2026-09-28
---

# 经济形势综合分析 v1.0

综合国内宏观 + 货币政策 + 房地产 + 网络经济 + 金银价格，输出未来 半年/1年/2年 经济形势三情景预测。

## 触发词

- "经济形势分析" / "经济展望" / "宏观经济"
- "房地产走势" / "网络经济" / "货币形势"
- "金银走势" / "CPI PPI 分析"
- "未来经济" / "经济预测"

## 数据源（全部 akshare 免费，本机实测 11/11 拉通）

| 类别 | 指标 | 接口 | 数据量 |
|------|------|------|--------|
| 物价 | CPI 同比/环比 | `macro_china_cpi` | 224 |
| 物价 | PPI | `macro_china_ppi` | 248 |
| 景气 | 制造业 PMI | `macro_china_pmi` | 224 |
| 货币 | M2 货币供应 | `macro_china_money_supply` | 224 |
| 货币 | 社融 | `macro_china_shrzgm` | 136 |
| 增长 | GDP 季度 | `macro_china_gdp` | 82 |
| 利率 | SHIBOR | `macro_china_shibor_all` | 2376 |
| 利率 | LPR（货币政策核心） | `macro_china_lpr` | 1576 |
| 房地产 | 商品房销售/房价 | `macro_china_real_estate` | 326 |
| 房价 | 70城新房/二手房指数 | `macro_china_new_house_price` | 376 |
| 就业 | 城镇调查失业率 | `macro_china_urban_unemployment` | 306 |
| 消费 | 社零 | `macro_china_consumer_goods_retail` | 209 |
| 社保 | 社保基金收支 | `macro_china_insurance_income` | 265 |
| 城镇消费 | CPI 城市分项（城镇消费价格指数） | `macro_china_cpi`（城市-同比列） | 224 |
| 金银 | 沪金 AU0 | `futures_zh_daily_sina` | 4561 |
| 金银 | 沪银 AG0 | `futures_zh_daily_sina` | 3502 |

**政策数据**：`data/policy_timeline.json`（建国以来核心政策节点人工整理，官家可补充）

## 架构

```
economic-outlook/
├── SKILL.md
├── data/
│   └── policy_timeline.json    # 政策时间线（核心节点版）
├── scripts/
│   ├── fetch_macro.py          # 数据层：akshare 拉 11 项指标（带 1h 缓存）
│   ├── policy_engine.py        # 政策层：事件情绪打分 + 时间衰减
│   ├── macro_model.py          # 分析层：6 维度加权评分（0-100）
│   ├── forecast.py            # 预测层：半年/1年/2年 三情景推演
│   ├── report_text.py         # 报告层：纯文本+emoji 生成
│   └── run_report.sh          # 一键入口
└── cache/                      # 数据缓存 + 报告输出
```

## 八维加权评分（v1.1）

| 维度 | 权重 | 逻辑 |
|------|------|------|
| 货币流动性 | 20% | M2 增速 + LPR 降息方向 |
| 景气 | 15% | PMI 水平 + 近 3 月趋势 |
| 房地产 | 15% | 70城房价指数 + 商品房销售 |
| 通胀 | 12% | CPI/PPI（温和通胀最优，通缩/过热扣分） |
| 金银信号 | 8% | 沪金/沪银 60 日趋势（避险/通胀预期） |
| 政策 | 15% | 政策事件情绪 + 时间衰减 |
| 就业 | 10% | 城镇调查失业率（≤5% 健康，>7% 承压） |
| 消费 | 5% | 社零累计同比 + 城镇消费价格指数 |

## 预测逻辑（半年/1年/2年）

- 每个 horizon 输出 **乐观 / 基准 / 悲观** 三情景
- 时间衰减系数：半年=1.0、1年=0.75、2年=0.5
- 政策事件冲击：近期重大事件（weight≥4）加减成
- 分领域方向判断：房地产 / 金融 / 新经济 / 消费 各自 上行/震荡/下行

## 使用方式

```bash
# 生成周报（纯文本）
bash scripts/run_report.sh

# 生成 + 输出推送文本（供 OpenClaw 读）
bash scripts/run_report.sh push

# 单独查预测
python3 scripts/forecast.py

# 单独查政策
python3 scripts/policy_engine.py
```

## 定时推送（周报）

每周 **周一 09:00 CST** 自动推送 QQ。
- cron prompt 用绝对路径，isolated session
- 读 `cache/report_text.txt` 推送

## 报告结构

```
📊 经济形势周报
【各维度评分】货币/景气/地产/通胀/金银/政策（0-100 进度条）
【最新指标】CPI/PMI/沪金/沪银
【近期政策信号】近 12 月重大事件
【半年/1年/2年预测】基准+乐观+悲观+分领域方向
⚠️ 免责声明
```

## 政策时间线维护

`data/policy_timeline.json` 是**人工整理项**，当前含 1949-2026 核心节点。
官家可随时补充：
- 新政策：在 `events` 数组加一条（date/title/impact/weight/sectors/note）
- impact 取值：`+` `++` `+++`（利好）/ `-` `--`（利空）/ `中性`
- weight：1-5（重大程度）

## 注意事项

1. akshare 数据 T-1 时效，无盘中实时
2. 政策时间线是简化版，深度分析需人工判断
3. 预测为三情景推演，**不构成投资建议**
4. 数据缓存 1 小时，避免限速
5. 完整报告生成约 6-10 秒（11 项并发拉取）

## 依赖

- akshare（国内数据主力）
- pandas / numpy

---

Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

## 按需接口（慢，不进自动周报）

**零售价格指数** `macro_china_retail_price_index`：需循环 137 个类目，耗时 2-3 分钟，
不纳入每周一自动周报（避免卡死 cron）。需要时用：

```bash
python3 scripts/retail_price_on_demand.py                # 全量
python3 scripts/retail_price_on_demand.py --category 食品类  # 指定类
```
结果缓存 24h（`cache/retail_price.pkl`）。

**⚠️ 2026-09-29 状态**：数据源 `quotes.sina.cn` 对本机 IP 持续限速/ReadTimeout，
该指标当前拿不到。脚本已加 15s 超时 + 部分降级 + 优雅失败，不会卡死周报。
新浪源恢复后重跑即可。
