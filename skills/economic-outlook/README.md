# 中国经济预测与决策参考 Skill（V3.0 信号驱动多出口决策系统）

从"宏观预测工具"升级为"信号驱动的多出口决策系统"：8 信号 → 8×6 加权组合 → 6 决策出口 → 历史类比 → 行动触发器。

## 架构分层

```
数据层 → 信号层(8) → 组合层(8×6加权+冲突+置信度) → 出口层(6) → 历史类比 → 行动触发器
akshare/官方源/政策   signals/     aggregator        outcomes/     history_analogy  triggers
```

## 安装
```bash
pip install -r requirements.txt
```

## 运行

### 统一入口（V3.0 信号驱动）
```bash
python entry.py "未来一年经济和股市怎么看"          # 综合决策报告
python entry.py "股票基金创业就业怎么配置" --verbose  # + 决策矩阵
```

### 各层单独跑
```bash
python scripts/history_analogy.py   # 历史类比：当前画像 → 最像哪一年 → 结构启示
python scripts/triggers.py          # 行动触发器：锚点切换 + 创业/投资/出口/政策 4 场景动作
python scripts/report_text.py       # 传统宏观周报（10 维度评分 + 8 季度预测）
python scripts/run_decision_report.sh  # 完整决策周报（信号+决策+历史类比+触发器 四层）
```

## 目录结构

```
economic-outlook/
├── SKILL.md / README.md / requirements.txt
├── entry.py                  # 统一入口 run(query, verbose)
├── router.py                 # 意图路由
│
├── core/                     # 核心引擎（宏观状态向量 + 预测）
│   ├── data_loader.py        # 数据加载（官方源优先 → akshare 降级）
│   ├── indicators.py / nowcast.py / forecast.py / scenarios.py / state_vector.py
│
├── signals/                  # ★信号层（V3.0 核心）
│   ├── pmi_orders.py         # PMI 新订单
│   ├── credit_impulse.py     # 信用脉冲（Biggs 公式）
│   ├── etf_flow.py           # ETF 资金流（反转逻辑）
│   ├── export_category.py    # 出口品类（量价拆分）
│   ├── domestic_category.py  # 国内品类（社零分项）
│   ├── china_us_spread.py    # 中美利差（分位数法）
│   ├── recruitment.py        # 招聘指数
│   ├── global_pmi.py         # 全球 PMI（美国 ISM 替代）
│   ├── aggregator.py         # 8×6 加权矩阵 + 冲突检测 + 置信度
│   ├── comprehensive_output.py / matrix_view.py
│   └── backtest_*.py ×6      # 回测框架
│
├── outcomes/                 # ★决策出口层（V3.0 §5）
│   ├── stock.py / fund.py / startup.py / employment.py / commodity.py / overseas.py
│   └── report.py             # 6 出口统一报告
│
├── mappings/                 # 旧版映射（stock/fund/startup/employment）
│
├── shared/
│   ├── cache.py / compliance.py / formatters.py
│   └── sources/              # ★11 数据源适配器
│       ├── nbs.py / customs.py / pboc.py      # 官方源（降级兜底）
│       ├── pmi.py / credit.py / china_us_spread.py / global_pmi.py
│       ├── recruitment.py / etf_flow.py / export_category.py
│       ├── domestic_retail.py / sector_returns.py
│
├── config/                   # 配置全外置（迁移只改这里）
│   ├── signals.yaml          # 信号权重/阈值/回测参数/数据边界
│   ├── sources.yaml / thresholds.yaml / compliance.yaml / model_params.yaml
│
├── scripts/
│   ├── fetch_macro.py        # 21 个 akshare 数据源
│   ├── macro_model.py        # 10 维度评分
│   ├── policy_engine.py      # 政策时间线引擎
│   ├── report_text.py / drivers.py / alerts.py
│   ├── history_analogy.py    # ★历史类比（5 锚点）
│   ├── triggers.py           # ★行动触发器（4 锚点切换 + 4 场景动作）
│   └── run_decision_report.sh
│
├── tests/                    # 7 个测试全 PASS
│   └── test_core / test_mappings / test_router / test_sources / test_signals / test_aggregator / test_outcomes
│
└── data/
    └── policy_timeline.json  # 33 条政策事件（静态）
```

## 6 决策出口

| 出口 | 核心问题 | 输出 |
|------|---------|------|
| 股票 | 超配什么行业？仓位多少？ | 超配/低配 + 周期位置 + 风格 |
| 基金 | 股债怎么配？ | 股债倾向 + ETF 轮动 |
| 创业 | 哪个方向机会大？ | 行业/时机评分 |
| 就业 | 哪些行业/城市/技能？ | 热度排名 |
| 大宗 | 需求在起来吗？ | 品种方向 |
| 海外 | 人民币还是美元资产？ | 币种/区域配置 |

## 历史类比 + 行动触发器

- **历史类比**（`scripts/history_analogy.py`）：当前经济画像（CPI/信用/利差/PMI/外需/政策 6 维）自动匹配 5 个历史锚点（2018/2014-15/2020Q2/2021/2022），输出"最像哪一年 + 当时怎么走 + 结构启示"。
- **行动触发器**（`scripts/triggers.py`）：
  - 4 个锚点切换触发器（信用脉冲转正 / 出口跌破0 / CPI破2% / 政策转强）→ 越线自动提示切锚点
  - 4 场景行动清单（创业 / 投资理财 / 出口贸易 / 政策导向）→ 信号直接翻译成动作

## 合规边界

- 不推个股 / 不荐具体基金 / 不给买卖点
- 不承诺薪资或录用 / 不承诺创业成功或收益
- 输出经 `shared/compliance.py` 过滤，最终文本统一追加免责声明
- 仅供参考，不构成投资建议/商业决策依据

## 迁移

复制整个文件夹 → 改 `config/`（数据源/权重/阈值全在 yaml）→ `pip install -r requirements.txt` → `python -m tests.test_core` → 上线。

**实测边界（诚实标注）**：
- 核心 4 信号真跑通：PMI 新订单、信用脉冲、中美利差、全球 PMI（美国 ISM 替代）
- 出口品类/国内品类/招聘 → 占位兜底（海关 412 / 统计局分项无免费源 / 招聘 API 需商业合作）
- ETF 资金流 → 东财行情接口云主机受限（换网络/加代理即通，代码不用改）
- 官方 NBS/海关/央行 → 本机网络受限，自动降级 akshare

---

**版权**: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
