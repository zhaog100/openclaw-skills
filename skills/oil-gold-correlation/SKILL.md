---
name: oil-gold-correlation
石油黄金白银实时相关性分析。多数据源交叉验证 + 隐藏机遇扫描 + 智能建议引擎。
version: 3.3.0
author: 小米辣 🌶️
lessons_updated: 2026-04-24
---

# 石油黄金白银相关性分析 v3.3

多数据源交叉验证，发现隐藏投资机遇。

## 触发词

- "石油黄金白银相关性" / "原油黄金白银分析" / "gold oil silver correlation"
- "大宗商品关联" / "油价金价银价关系"
- "石油黄金白银" / "oil gold silver"
- "该买黄金吗" / "黄金投资建议" / "原油怎么投"
- "黄金买卖" / "石油基金" / "大宗商品投资"
- "国际形势" / "地缘分析" / "石油黄金新闻"
- "隐藏机遇" / "内外盘背离" / "跨品种分析"

## 使用方式

### 1. 每日投资报告（主功能）

```bash
python3 scripts/advisor.py [--days 3]
```

v3.3 多数据源架构（永不因单一源失败而返回空）：

| 优先级 | 数据源 | 品种 | 货币 | 依赖 |
|--------|--------|------|------|------|
| 🟢 最高 | akshare | 沪金AU0、沪银AG0、沪油SC0 | CNY | 无 |
| 🟡 备用 | yfinance | GC=F, SI=F, CL=F, BZ=F, DX-Y.NYB | USD | 可能被限流 |
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

## 报告结构（v3.3）

```
一、今日操作摘要 — 买入/卖出/观望 + 数据来源标注（CNY/USD）
二、短期分析 — 技术指标详细分析
三、中长期趋势 — 均线系统 + 趋势强度
四、综合建议 — 品种综合评分
五、国际形势 — 自动新闻采集 + 分级评分（核心5分/边缘1分）
六、综合投资建议 — 智能引擎（动态权重+置信度+止损止盈）
七、🔍 隐藏机遇扫描（v3.3 核心）
  🥇 内外盘背离：沪金补涨机会
  🥈 跨品种异常：黄金-原油比率偏离
  🥉 量价背离：底部/顶部信号
```

## v3.3 新功能

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

## 📚 经验教训（v3.3 新增）

### 一、数据源策略

| 数据源 | 状态 | 说明 |
|--------|------|------|
| **akshare** | 🟢 主力 | 国内期货数据稳定，免费无需Key，但只有 **T-1 收盘价**，无盘中实时数据 |
| **yfinance** | 🔴 不可用 | 腾讯云 IP 被持续限速/封禁超2小时，**不可作为主力** |
| **Alpha Vantage** | 🟠 可选 | 25次/天，需API Key，无Key时自动跳过 |
| **Twelve Data** | 🟠 可选 | 需API Key，无Key时自动跳过 |
| **FRED** | 🔵 宏观 | 美元指数/CPI/利率/VIX等宏观指标，延迟1-3天 |

**关键教训**：
- yfinance 在腾讯云服务器上 **持续被限速**，不能依赖
- akshare 是唯一稳定的免费国内数据源，但数据滞后1天
- 报告必须标注数据来源和时效性（T-1）
- 多数据源降级策略：akshare → Alpha Vantage → Twelve Data → FRED，永不返回空报告

### 二、QQ Bot 推送经验

#### 1. 文件发送
- QQ Bot 发文件必须放在 `/root/.openclaw/media/qqbot/` 目录
- 使用 `<qqmedia>绝对路径</qqmedia>` 标签发送
- 其他路径报错 "Media path must be inside QQ Bot media storage"
- **PNG RGBA 格式不支持** → 转 JPEG 解决（`convert input.png -colorspace RGB output.jpg`）
- **结论**：图片方案调试成本高，**纯文本+emoji 更稳定高效**

#### 2. 消息截断
- QQ 有消息长度限制，长报告会被截断
- 解决：拆分为两条消息推送（PART 1 + PART 2）
- PART 1：行情+仪表盘+技术详解（~500字符）
- PART 2：宏观信号灯+操作建议（~230字符）

#### 3. Cron 定时任务
- `sessionTarget` 必须用 `isolated`，不能用 `session:agent:main:main`（否则 announce 不走 QQ channel）
- cron prompt 不要用 `cd &&` 复合命令，用绝对路径
- isolated session **不继承 agent 模型配置**，需指定可用模型
- 不同 QQ Bot（不同 appId）看到同一用户的 **openid 不同**！
  - default bot: `C099848DC9A60BF60A7BE31626822790`
  - bot2: `E7331F9772A02575890BBE94E788248A`
  - 每个 bot 的 cron 必须用对应的 openid

### 三、地缘风险评分优化

- **问题**：早期版本关键词评分过高（战争+95），导致泛泛新闻拉高到30分
- **修复**：
  - 核心关键词（战争/OPEC减产/美联储降息）→ +50
  - 边缘关键词（中国经济/供需）→ +1
  - 二次过滤：必须包含商品关联词才计分
- **数据源**：百度热搜有 cookie 限制 → 改用央视新闻（`news_cctv`）

### 四、技术分析要点

- **收益率 vs 绝对价格**：分析相关性时用收益率（`pct_change()`）而非绝对价格，避免量级差异
- **黄金-原油相关性**：历史数据显示强负相关（r ≈ -0.61 ~ -0.93）
- **关键指标**：RSI（超买>70/超卖<30）、MACD、KDJ、OBV 量价背离、均线系统（MA5/MA10/MA20/MA60）
- **支撑阻力**：基于近期高低点计算，动态更新
- **投资决策仪表盘**：综合技术面+宏观面+地缘风险，输出 0-100 分和买入/观望/回避建议

### 五、版本迭代历史

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| v3.3.0 | 04-12 | 初始安装，yfinance 限速问题发现 |
| v3.3 | 04-14 | fetch_data.py SyntaxError 修复（docstring重复） |
| v3.3 | 04-14 | bug 修复验证通过 |
| v3.3 | 04-13~16 | 多数据源架构 + 隐藏机遇扫描器 + 地缘评分优化 |
| v3.3 | 04-24 | 经验教训文档化 + 纯文本报告 v2.1 |
| v3.3 | 04-24 | **白银集成** - 支持沪银AG0期货，三资产分析

### 六、定时推送时间（按市场开收盘）

| 时段 | 时间 | 说明 |
|------|------|------|
| 早盘 | 10:00 | 日盘开盘1h后，隔夜数据回顾 |
| 日盘收盘 | 15:30 | 中国日盘收盘后，当日数据完整 |
| 美盘开盘 | 23:00 | 美股开盘30min后，全球定价确认 |

- 冬令时自动延迟至 00:00（`oil-gold-us-adapter.sh`）
- 中国期货日盘: 09:00-15:00，夜盘: 21:00-次日02:30
- 美股夏令时: 21:30-04:00，冬令时: 22:30-05:00

### 七、已知限制

1. akshare 只有 T-1 收盘价，无盘中实时数据
2. 地缘风险采集 13 个 channel，耗时约 8-10 秒
3. 完整报告生成约 133 秒（含数据采集+分析+地缘）
4. 布油/美元暂未接入（可扩展）
5. 部分 cron 任务偶发超时（180s timeout）

### 八、部署经验

- **GitHub 更新**：从 `feat/github-marketing` 分支拉取，更新前备份旧版
- **依赖安装**：`pip3 install -r requirements.txt`（yfinance/pandas/numpy/scipy/plotly/statsmodels/akshare/requests）
- **缓存目录**：`cache/` 存放 pickle 数据，5分钟过期
- **报告输出**：`cache/report_text.txt` 纯文本报告，供 cron 读取推送
- **Copyright**：所有文件末尾需加 `MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)`

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
