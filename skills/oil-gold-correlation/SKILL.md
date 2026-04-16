---
name: oil-gold-correlation
石油黄金实时相关性分析。多数据源交叉验证 + 隐藏机遇扫描 + 智能建议引擎。
version: 1.4.0
author: 小米粒 🌾
---

# 石油黄金相关性分析 v1.4.0

多数据源交叉验证，发现隐藏投资机遇。

## 触发词

- "石油黄金相关性" / "原油黄金分析" / "gold oil correlation"
- "大宗商品关联" / "油价金价关系"
- "石油黄金" / "oil gold"
- "该买黄金吗" / "黄金投资建议" / "原油怎么投"
- "黄金买卖" / "石油基金" / "大宗商品投资"
- "国际形势" / "地缘分析" / "石油黄金新闻"
- "隐藏机遇" / "内外盘背离" / "跨品种分析"

## 使用方式

### 1. 每日投资报告（主功能）

```bash
python3 scripts/advisor.py [--days 3]
```

v1.4.0 多数据源架构（永不因单一源失败而返回空）：

| 优先级 | 数据源 | 品种 | 货币 | 依赖 |
|--------|--------|------|------|------|
| 🟢 最高 | akshare | 沪金AU0、沪油SC0 | CNY | 无 |
| 🟡 备用 | yfinance | GC=F, CL=F, BZ=F, DX-Y.NYB | USD | 可能被限流 |
| 🟠 额外 | Alpha Vantage | GLD, USO | USD | API Key |
| 🟠 额外 | Twelve Data | XAU/USD, CL | USD | API Key |
| 🔵 宏观 | FRED | 美元指数/CPI/利率/VIX | USD | 免费 |

**降级策略**：yfinance 不可用时自动跳过国际品种，akshare 至少1个品种成功即输出报告。

### 2. 相关性分析

```bash
python3 scripts/analysis.py [--method all] [--window 30]
```

分析方法：Pearson / Spearman / Kendall / Rolling / Granger / 协整 / DCC-GARCH

### 3. 可视化

```bash
python3 scripts/visualize.py [--output media/oil-gold.html]
```

### 4. 多数据源管理器（API）

```python
from scripts.multi_source import create_default_manager
mgr = create_default_manager()
data = mgr.fetch("gold_futures", "90d")  # 返回 {source: DataFrame}
consensus = mgr.consensus(data)           # 多源加权共识价
validation = mgr.cross_validate(data)     # 交叉验证
```

### 5. 隐藏机遇扫描

```python
from scripts.opportunity_scanner import OpportunityScanner
scanner = OpportunityScanner()
scanner.scan_divergence(domestic_data, international_data)  # 内外盘背离
scanner.scan_cross_commodity(gold_data, oil_data)            # 跨品种异常
scanner.scan_volume_price(data)                               # 量价背离
report = scanner.generate_opportunity_report()                # 生成报告
```

## 报告结构（v1.4.0）

```
一、今日操作摘要 — 买入/卖出/观望 + 数据来源标注（CNY/USD）
二、短期分析 — 技术指标详细分析
三、中长期趋势 — 均线系统 + 趋势强度
四、综合建议 — 品种综合评分
五、国际形势 — 自动新闻采集 + 分级评分（核心5分/边缘1分）
六、综合投资建议 — 智能引擎（动态权重+置信度+止损止盈）
七、🔍 隐藏机遇扫描（v1.4.0 核心）
  🥇 内外盘背离：沪金补涨机会
  🥈 跨品种异常：黄金-原油比率偏离
  🥉 量价背离：底部/顶部信号
```

## v1.4.0 新功能

### 🔍 隐藏机遇扫描器
- **内外盘背离** — 国际涨国内不涨 → 补涨机会
- **跨品种异常** — 黄金-原油比率偏离历史均值 >1σ
- **量价背离** — 价涨量缩 → 顶部信号；价跌量缩 → 底部信号
- **多时间框架共振** — 短线+长线同向 → 高确信信号

### 🌐 多数据源集成
- 5个数据源自动降级，永不返回空报告
- 环境检测：自动判断 yfinance 可用性
- 报告头部标注数据来源（CNY/USD）
- Alpha Vantage / Twelve Data 可选（需 API Key）

### 🛡️ 地缘评分优化
- 核心关键词（战争/OPEC减产/美联储降息）5分
- 边缘关键词（中国经济/供需）1分
- 二次过滤：必须包含商品关联词才计分
- 避免"中国经济"类泛泛新闻拉高到30分

## 定时推送

每天早上 **9:00 CST** 自动推送到 QQ。
手动触发: `openclaw cron run <job-id>`

## API Key 配置（可选）

```bash
# Alpha Vantage (https://www.alphavantage.co/support/#api-key)
export ALPHA_VANTAGE_API_KEY=your_key

# Twelve Data (https://twelvedata.com/apikey)
export TWELVE_DATA_API_KEY=your_key
```

无 Key 时自动跳过，不影响其他数据源。

## 注意事项

1. 数据缓存 5 分钟，避免限速
2. 相关性 ≠ 因果性，Granger 仅表示时序领先性
3. 期货有杠杆风险，新手从 ETF 开始
4. 单品种仓位 ≤ 10%，总仓位 ≤ 30%

## 依赖

- yfinance >= 0.2
- pandas >= 2.0
- numpy
- scipy >= 1.10
- plotly >= 5.0
- statsmodels >= 0.14（可选）
- akshare（国内数据源）
- requests（Alpha Vantage / Twelve Data）

---

Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
