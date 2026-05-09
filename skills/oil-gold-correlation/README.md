# Oil-Gold Correlation — 石油黄金相关性分析工具

_版本: 2.0.0 | MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)_

---

## 功能

- **8 种相关性分析方法**：Pearson / Spearman / Kendall / Granger 因果 / Cointegration / DCC-GARCH 等
- **多数据源**：akshare（国内）/ yfinance（国际）/ FRED（宏观）/ Alpha Vantage（备用）
- **投资顾问**：8 品种 × 9 技术指标，自动生成操作建议
- **定时推送**：早盘(10:00) / 晚盘(21:00) / 美盘(22:00) + 夏令时自适应
- **可视化图表**：4 种图表类型（折线/散点/热力/回归）

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 获取数据
python3 scripts/fetch_data.py --period 1y

# 分析相关性
python3 scripts/analysis.py --method all

# 生成报告
python3 scripts/report.py --period 1y

# 文本报告（定时推送用）
python3 scripts/report_text.py
```

## 配置

1. **推送渠道**：编辑 `config/push-config.yaml`
2. **定时任务**：编辑 `~/.openclaw/cron/jobs.json`，添加 3 个 cron job（10:00/21:00/22:00）

## 数据源

| 类型 | 源 | 说明 |
|------|-----|------|
| 国内行情 | akshare | 沪金AU0、沪油SC0、沪银AG0 |
| 国际行情 | yfinance | XAUUSD、CL=F、BZ=F |
| 宏观数据 | FRED | 美元指数、VIX、TED利差 |
| 地缘政治 | CCTV/东方财富 | 新闻分析 |

## 依赖

- Python 3.10+
- pandas, numpy, scipy, statsmodels
- akshare, yfinance, requests
- plotly（可视化）

## 作者

思捷娅科技 (SJYKJ)/zhaog100