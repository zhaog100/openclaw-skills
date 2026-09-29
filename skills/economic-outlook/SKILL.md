# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License

---
name: economic-outlook
description: "经济形势综合分析：多源宏观数据 + 政策引擎 + 多维评分 + 半年/1年/2年三情景预测。周报推送 QQ。"
version: 3.3.0
author: 小米椒 🌶️
lessons_updated: 2026-09-28
---

# 经济形势综合分析 v3.3（PRD V2.0 + 官方源真实采集适配器层）

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
| 外需 | 出口同比 | `macro_china_exports_yoy` | 542 |
| 外需 | 进口同比 | `macro_china_imports_yoy` | 381 |
| 外部平衡 | 外汇储备 | `macro_china_fx_reserves_yearly` | 132 |
| 金融条件 | 10年期国债收益率 | `bond_china_yield` | 738 |

**v2.0 说明（按 PRD V1.0 扩展）**：数据源 15 → 21（含美国 PMI/CPI 外需领先指标），维度 8 → 10，预测 horizon 3（半年/1年/2年）→ **8 个季度**。

**政策数据**：`data/policy_timeline.json`（建国以来核心政策节点人工整理，官家可补充）

## 架构

```
economic-outlook/
├── SKILL.md
├── data/
│   └── policy_timeline.json    # 政策时间线（核心节点版）
├── scripts/
│   ├── fetch_macro.py          # 数据层：akshare 拉 19 项指标（1h 缓存）
│   ├── policy_engine.py        # 政策层：事件情绪打分 + 时间衰减
│   ├── macro_model.py          # 分析层：10 维度加权评分（0-100）
│   ├── forecast.py            # 预测层：8 个季度 三情景推演
│   ├── features.py           # FR-03：同比/环比/剪刀差/扩散指数
│   ├── drivers.py            # FR-06：前 5 大驱动因子解释
│   ├── alerts.py             # FR-08：P0 指标阈值告警
│   ├── backtest.py           # FR-10：GDP/CPI 滚动回测（PRD §11 验收）
│   ├── report_text.py         # 报告层：纯文本+emoji 生成
│   └── run_report.sh          # 一键入口
└── cache/                      # 数据缓存 + 报告输出
```

## 十维加权评分（v2.0）

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
| 外需 | 6% | 出口同比（海关） |
| 金融条件 | 2% | 10年期国债收益率 + 外汇储备变动 |

## 预测逻辑（v2.0：8 个季度，对齐 PRD）

- 输出未来 **8 个季度（Q1-Q8，2 年）** 三情景：乐观 / 基准 / 悲观
- 时间衰减系数：Q1=0.95 → Q8=0.60
- 政策事件冲击：近期重大事件（weight≥4）加减成
- 分领域方向判断：房地产 / 金融 / 新经济 / 消费 / 外需 各自 上行/震荡/下行

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

## PRD 对齐说明（v2.0）

本版按官家提供的《中国经济走势预测 Skill 需求文档 PRD V1.0》扩展：
- ✅ P0 指标接入：GDP、CPI/PPI、失业率、出口/进口、社零、M2/社融、LPR、10年期国债、外汇储备、70城房价、商品房
- ✅ 8 季度三情景预测（PRD §3.1/§3.2）
- ✅ 政策事件驱动（§5.3 政治局/中央经济工作会议/十五五规划）
- ⏳ V2 待补：分国别出口、专项债、集装箱运价、高频（用电/地铁/迁徙）、iCPI、消费者信心、16-24岁失业率（无免费公开源或需第三方付费库）

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


## PRD 功能覆盖（v2.1 补齐）

| FR 编号 | 功能 | 脚本 | 状态 |
|---------|------|------|------|
| FR-01 | 数据采集调度 | fetch_macro.py（19 源并发+缓存+超时） | ✅ |
| FR-02 | 数据质量监控 | 采集层 fail 标记 | ✅ |
| FR-03 | 指标计算（同比/环比/扩散/剪刀差） | features.py | ✅ |
| FR-04 | 预测引擎（三情景） | forecast.py（8 季度） | ✅ |
| FR-06 | 解释生成（前 5 驱动因子） | drivers.py | ✅ |
| FR-07 | 可视化（进度条+仪表盘） | report_text.py | ✅ |
| FR-08 | 告警（阈值突破） | alerts.py | ✅ |
| FR-09 | 报告导出（纯文本） | report_text.py | ✅ |
| FR-10 | 回测（误差跟踪） | backtest.py | ✅ |

**PRD §11 验收（回测基线已达标）**：
- GDP 方向准确率 83.6%（要求 >70%）✅
- CPI 平均绝对误差 0.412pct（要求 <0.5pct）✅

## 按需接口（慢，不进自动周报）


## v3.0 架构（对齐 PRD V2.0：单文件夹 + 1 核心 + N 映射）

```
用户输入 → entry.py（统一入口）→ router.py（意图路由）
          ├── core（宏观引擎）→ 宏观状态向量
          └── mappings（4 映射）→ 合规过滤 → 聚合输出
```

### 目录
- `core/state_vector.py` — 宏观状态向量（PRD §5.5 schema）
- `mappings/{stock,fund,startup,employment}.py` — 4 个决策映射（只读状态向量，不重预测宏观）
- `shared/compliance.py` — 合规过滤（个股/买卖点/基金推荐/收益承诺）
- `shared/formatters.py` — 输出格式化
- `config/thresholds.json` + `config/model_params.json` — 配置外置（迁移只改这里）
- `requirements.txt` — 依赖声明

### 调用方式（单入口，flag 强制触发映射模块）
```bash
python3 entry.py "未来经济走势"                # 纯宏观
python3 entry.py "股市和行业怎么看" --stock     # 强制股票映射
python3 entry.py "适合创业吗" --startup          # 强制创业映射
python3 entry.py "什么行业好就业" --employment  # 强制就业映射
# flag 可与 query 关键词叠加，合规过滤始终生效
```

**意图路由说明**：`--flag` 通过 `force` 参数直接指定映射模块，与 query 关键词（宏观/股票/基金/创业/就业）合并命中；
"行业"等词已收窄为"行业景气/行业配置"避免误判。

### 合规边界（PRD §10）
- 股票：不推个股、不给买卖点
- 基金：不推具体基金、不承诺收益（需持牌机构）
- 创业：不承诺成功/收益
- 就业：不承诺薪资/录用

### 迁移性（PRD §16 清单）
✅ 入口明确（entry.py/SKILL.md）✅ 依赖声明（requirements.txt）✅ 配置外置（config/）
✅ 缓存可重建 ✅ 核心 schema 固定 ✅ 映射不硬编码核心 ✅ 合规集中 ✅ 无绝对路径 ✅ 版本号明确

### PRD V2.0 阶段对照
- **MVP（P0）**：核心引擎 + 股票(行业景气) + 就业(热度排名) + 入口路由 + 合规 + 回测 → ✅ 已交付
- **P1**：基金映射、创业映射、情景模拟、告警系统 → ✅ 代码已备好（stock/employment 为 P0，fund/startup 为 P1，均已实现）
- **P2**：区域/城市/技能细分、NL 问答、另类数据 → ⏳ 未做


## v3.2 对齐 PRD V2.0 完整目录结构（§一）

```
economic-outlook/
├── SKILL.md / entry.py / router.py        # 统一入口 + 意图路由
├── core/                                  # 1 核心引擎（只做宏观预测）
│   ├── data_loader.py   indicators.py   nowcast.py
│   ├── forecast.py      scenarios.py     state_vector.py
├── mappings/                              # N 映射模块（只读状态向量）
│   ├── stock.py  fund.py  startup.py  employment.py
├── shared/                                # 共享层
│   ├── sources.py   cache.py   compliance.py   formatters.py
├── config/                                # 配置外置（迁移只改这里）
│   ├── sources.yaml  thresholds.yaml  compliance.yaml  model_params.yaml
├── tests/                                 # test_core / test_mappings / test_router
├── scripts/                               # 数据+分析+回测+报告（akshare 21 源）
├── requirements.txt
└── README.md
```

**API 对齐 PRD §三/§四**：
- `from entry import run; r = run("..."); print(r["summary"])` ✅
- `route(query, force)` 返回含 `summary/disclaimer/intents` ✅
- 映射模块 `map(state)` 只读核心状态向量 ✅
- 合规 `filter_output` 递归过滤（yaml 规则驱动）✅
- 缓存 `cache_get/cache_set`（官方数据发布后更新一次）✅
- 3 个测试全 PASS ✅


## v3.3 官方源真实采集（接国家统计局/海关/央行）

新增 `shared/sources/` 适配器包（适配器模式，官方源不可用时优雅降级 akshare）：

```
shared/sources/
├── __init__.py    # 统一出口 SourceRouter（指标→适配器路由，失败返回空）
├── base.py        # BaseAdapter + DataPoint（统一数据点格式）
├── nbs.py         # 国家统计局（新版 V2.0 API，UUID cid 待填充）
├── customs.py     # 海关总署（模拟表单，Cookie，412 容错）
└── pboc.py        # 央行（社融三级跳 xls；M2 走 akshare 代理）
```

**设计要点**（按官家采集文档）：
- 每个官方源独立适配器，统一输出 `list[DataPoint]`，`core/data_loader` 不感知底层差异
- `config/sources.yaml` 配置指标走哪个适配器 + 采集参数（retry/timeout/sleep）
- 礼貌采集：`_sleep(0.5)` + 3 次重试
- **降级策略**：官方源（cid 未填/412/结构变动）失败 → 返回空，主流程仍走 akshare 21 源

**现状（如实）**：
- NBS：`PRESET_CIDS` 的 cid/indicatorId 是 UUID 占位，需实际调 `queryIndexTreeAsync` 后填入 `config`（时间分片指标要多个 cid 拼接）
- 海关：`stats.customs.gov.cn` 实测返回 412（反爬），需真实 Cookie/代理才能拿到数
- 央行：社融三级跳代码已实现，M2 走 akshare 代理稳定

`tests/test_sources.py` 验证适配器不崩（PASS）。
