---
description: 原油黄金相关性分析工具。
name: oil-gold-correlation
石油黄金实时相关性分析。获取大宗商品价格数据，计算多种相关性指标（Pearson/Spearman/Kendall），支持 DCC-GARCH 动态相关、Granger 因果检验、协整分析，输出可视化图表和自然语言结论。
version: 2.1.4
author: 思捷娅科技 (SJYKJ)
recommendModel: zai/glm-5
altModels:
  - zai/glm-5
  - qwen3-max
  - qwen3.5-plus
  - kimi-k2.5
---

# 石油黄金相关性分析

实时分析黄金（XAU/USD）和原油（WTI/Brent）之间的相关性，支持多种统计方法和可视化。

## 触发词

- "石油黄金相关性" / "原油黄金分析" / "gold oil correlation"
- "大宗商品关联" / "油价金价关系"
- "石油黄金" / "oil gold"
- "该买黄金吗" / "黄金投资建议" / "原油怎么投"
- "黄金买卖" / "石油基金" / "大宗商品投资"
- "国际形势" / "地缘分析" / "石油黄金新闻"

## 使用方式

当用户问及石油和黄金的关系、大宗商品关联性时，按以下流程执行：

### 1. 数据获取

```bash
python3 scripts/fetch_data.py [--period 1y] [--interval 1d]
```

使用 yfinance 获取数据（免费、无需 Key）：
- 黄金期货：`GC=F`
- WTI 原油：`CL=F`
- 布伦特原油：`BZ=F`

数据缓存 5 分钟，避免频繁请求。

### 2. 相关性分析

```bash
python3 scripts/analysis.py [--method all] [--window 30]
```

分析方法（从简单到高级）：

| 方法 | 说明 | 适用场景 |
|------|------|---------|
| Pearson | 线性相关性 | 基础分析 |
| Spearman | 秩相关性 | 非线性单调关系 |
| Kendall | 秩一致性 | 小样本稳健 |
| Rolling Correlation | 滚动窗口相关 | 相关性变化趋势 |
| Granger Causality | 因果方向 | 谁领先谁 |
| Cointegration (ADF) | 长期均衡 | 是否存在稳定关系 |
| 白银-黄金相关 | 白银与黄金收益率相关 | 商品联动分析 |
| 白银-原油相关 | 白银与原油收益率相关 | 商品联动分析 |

### 3. 可视化

```bash
python3 scripts/visualize.py [--output media/oil-gold.html]
```

生成图表：
1. 价格走势叠加图（双 Y 轴）
2. 收益率散点图 + 回归线
3. 滚动相关系数时序图

### 4. 报告生成

```bash
python3 scripts/report.py [--period 1y]
```

输出自然语言分析结论，包含：
- 当前相关系数及解读
- 相关性趋势（增强/减弱）
- 因果关系方向（如有）
- 投资启示

## 时间窗口

| 命令 | 窗口 | 用途 |
|------|------|------|
| `7d` / `一周` | 7 天 | 短期波动 |
| `30d` / `一月` | 30 天 | 月度趋势 |
| `90d` / `一季度` | 90 天 | 中期走势 |
| `1y` / `一年` | 252 交易日 | 长期关系 |
| `滚动` | 30 日滚动窗口 | 相关性变化 |

### 5. 投资建议（短期 1天~1周）

```bash
python3 scripts/advisor.py [--days 3]
```

综合技术指标生成短期买卖建议，覆盖多品种：

| 品类 | 品种 | 代码 | 类型 |
|------|------|------|------|
| 黄金 | COMEX期货 | GC=F | 期货 |
| 黄金 | GLD ETF | GLD | 基金 |
| 黄金 | 现货 | XAUUSD=X | 现货 |
| 原油 | WTI期货 | CL=F | 期货 |
| 原油 | 布伦特期货 | BZ=F | 期货 |
| 原油 | USO ETF | USO | 基金 |
| 关联 | 美元指数 | DX-Y.NYB | 指数 |
| 关联 | 白银期货 | SI=F | 期货 |

技术指标：RSI(14) + MACD(12,26,9) + KDJ随机 + 布林带(20) + ATR(14) + OBV量价分析 + Fibonacci回撤 + 支撑/阻力位 + 黄金-原油比率 + 多时间框架分析
输出：评分、建议、操作策略、止盈止损价位、预测区间、量价背离、Fib区间

### v1.3.0 智能建议引擎
5大核心功能：
1. **动态权重系统** — 根据市场环境（趋势/震荡/高波动）自动调整指标权重
2. **信号冲突处理** — 多空分类 + 一致度计算 + 趋势指标优先
3. **置信度评分** — HIGH/MEDIUM/LOW 三级，基于一致度+信号强度+数量
4. **止损止盈建议** — ATR 1.5倍止损 + Fibonacci目标 + 风险回报比 ≥ 2:1
5. **仓位建议** — HIGH 2%/MEDIUM 1% 账户风险，LOW 不开仓

输出格式：方向 + 置信度 + 信号汇总(看多/看空) + 具体入场/止损/止盈价位 + 风险回报比 + 仓位 + 风险提示

## 定时推送

### 配置方式

推送目标通过配置文件灵活管理，不写死 Bot/账号：

```yaml
# config/push-config.yaml（如不存在则自动创建默认配置）
push:
  enabled: true
  channels:
    - name: default          # 推送目标名称（自定义）
      type: qqbot            # qqbot | telegram | discord | webhook
      target: c2c            # c2c(私聊) | group:群号 | channel:频道号
      account: default       # OpenClaw 账号ID
    # 添加更多目标，按需配置：
    # - name: bot2
    #   type: qqbot
    #   target: c2c
    #   account: bot2
    # - name: telegram-alerts
    #   type: telegram
    #   target: chat:123456

schedule:
  - id: morning             # 早盘（大陆期货日盘）
    time: "10:00"            # CST 固定
    timezone: Asia/Shanghai
    timeout: 300
    data_baseline: T-1       # 上一交易日收盘价

  - id: evening             # 晚盘（大陆期货夜盘）
    time: "21:00"            # CST 固定
    timezone: Asia/Shanghai
    timeout: 300
    data_baseline: T-0       # 当日最新收盘价

  - id: us-market           # 美盘（美股开盘后）
    time: "22:00"            # Cron 固定触发时间
    timezone: Asia/Shanghai
    timeout: 600
    dst_aware: true          # 夏/冬令时自适应
    summer_shift: "22:00"    # 夏令时执行时间
    winter_shift: "23:00"    # 冬令时执行时间（自动 sleep 30min）
    data_baseline: US-open   # 美股开盘半小时后

cron:
  sessionTarget: isolated
  lightContext: true
  model: zai/glm-5
```

**使用方式**：
- 配置文件路径：`skills/oil-gold-correlation/config/push-config.yaml`
- 首次运行自动生成默认配置
- 用户可自由添加/删除推送目标
- 支持多渠道混合推送（QQ + Telegram + Discord 同时推送）

### 推送时间表

| 时段 | Cron触发时间 | 实际推送时间 | 数据基准 | 说明 |
|------|-------------|-------------|----------|------|
| 早盘 | 10:00 CST | 10:00 CST | T-1 收盘价 | 沪金AU0、SC原油SC0、FRED宏观 |
| 晚盘 | 21:00 CST | 21:00 CST | T-0 最新价 | 同上 |
| 美盘 | 22:00 CST | 22:00/23:00 自适应 | 美股开盘后 | 夏/冬令时自动切换 |

**美盘夏/冬令时自动切换**：
- 夏令时（3月第2周日~11月第1周日）：直接执行 → 22:00 CST
- 冬令时（11月第1周日~次年3月第2周日）：sleep 30 分钟后执行 → 23:00 CST

### 数据源与时效性

| 数据类型 | 数据源 | 实时性 | 说明 |
|----------|--------|--------|------|
| 黄金/原油行情 | akshare futures_main_sina | T-1 收盘 | 上一交易日收盘价 |
| 国际品种 | yfinance | ⚠️ 腾讯云IP被限速 | 备用 |
| 央视新闻 | akshare news_cctv | 昨+今 | 每日采集 |
| 东方财富 | stock_info_global_em | ✅ 实时 | 全球财经200条 |
| 上期所 | futures_news_shmet | ✅ 实时 | 期货专业新闻 |
| CNBC国际 | RSS | ✅ 实时 | 国际财经 |
| FRED宏观 | fred.stlouisfed.org | ⚠️ 延迟1天 | 无需API Key |
| 美股指数 | FRED (SP500等) | ⚠️ 延迟1天 | FRED非实时 |

**缓存策略**：行情数据 5 分钟 TTL，FRED 数据 1 小时 TTL

手动触发: `openclaw cron run <job-id>`

## 注意事项

1. **数据单位**：黄金 USD/盎司，原油 USD/桶 — 量级不同，分析时用收益率（pct_change）
2. **交易时间**：周末/节假日无数据，自动跳过空值
3. **缓存**：数据缓存 5 分钟，避免 yfinance 限速
4. **相关性 ≠ 因果性**：报告时注意措辞，Granger 因果仅表示时序领先性
5. **regime switching**：不同市场状态（牛市/熊市/震荡）下相关性可能完全不同
6. **行情数据为 T-1 收盘价**，非盘中实时
7. **美盘时间由 oil-gold-us-adapter.sh 自动切换**，无需手动调整
8. **yfinance 在腾讯云 IP 被限速**，akshare 是唯一可用数据源
9. **FRED 宏观数据本身有 1-3 天发布延迟**（非实时）
10. **周末/节假日无期货交易数据**

## 依赖

### Python 环境（推荐 Miniconda）
```bash
# 创建并激活环境
conda create -n oil-gold python=3.11 -y
conda activate oil-gold

# 安装依赖
pip install -r requirements.txt
```

### 依赖清单
- yfinance >= 0.2.36
- pandas >= 2.0
- numpy >= 1.24
- scipy >= 1.10
- plotly >= 5.0
- statsmodels >= 0.14
- requests >= 2.28
- akshare >= 1.10

### 跨平台启动脚本
为方便使用，提供统一启动脚本：
- **Linux/macOS**: `./run.sh {fetch|analyze|visualize|report|advisor|all}`
- **Windows**: `run.bat {fetch|analyze|visualize|report|advisor|all}`

---

Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

---

## 🌐 技能仓库

**官方仓库**: `https://github.com/zhaog100/openclaw-skills/tree/main/skills/oil-gold-correlation`
**主分支**: `main`
**版本**: `v2.1.4`

### 📥 下载方式

#### 1. 通过 Git 下载（推荐）
```bash
git clone https://github.com/zhaog100/openclaw-skills.git
cd openclaw-skills/skills/oil-gold-correlation
git checkout v2.1.4
```

#### 2. 通过 OpenClaw CLI 安装
```bash
openclaw skills install oil-gold-correlation@v2.1.4
```

#### 3. 手动下载
下载链接: `https://github.com/zhaog100/openclaw-skills/tree/main/skills/oil-gold-correlation`

## 🛠️ 部署指南

### 安装后必做：配置 Cron 任务

**重要**：技能安装后需要手动配置定时任务，否则报告不会自动推送。

#### 1. 添加 Cron 任务

编辑 `~/.openclaw/cron/jobs.json`，添加以下 3 个任务：

```json
{
  "id": "oil-gold-morning",
  "name": "oil-gold-morning",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 10 * * *" },
  "message": "生成并推送石油黄金早盘报告",
  "model": "minimax/MiniMax-M2.7",
  "timeoutSeconds": 300
},
{
  "id": "oil-gold-evening",
  "name": "oil-gold-evening",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 21 * * *" },
  "message": "生成并推送石油黄金晚盘报告",
  "model": "minimax/MiniMax-M2.7",
  "timeoutSeconds": 300
},
{
  "id": "oil-gold-us-market",
  "name": "oil-gold-us-market",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 22 * * *" },
  "message": "生成并推送石油黄金美盘报告",
  "model": "minimax/MiniMax-M2.7",
  "timeoutSeconds": 600
}
```

#### 2. 验证 Cron 任务

```bash
openclaw cron list
```

应看到以下 3 个任务：
- `oil-gold-morning` (10:00)
- `oil-gold-evening` (21:00)
- `oil-gold-us-market` (22:00)

#### 3. 手动测试

```bash
openclaw cron run oil-gold-morning
```

### 配置推送目标

编辑 `config/push-config.yaml` 自定义推送目标（见上方配置方式）。

---

### 三平台路径映射
为方便配置，以下是各平台的路径对应关系：

```
┌─────────────┬──────────────────────────────────────────┐
│  平台        │  Cron 配置路径                             │
├─────────────┼──────────────────────────────────────────┤
│ Windows     │  %USERPROFILE%\.openclaw\cron\        │
│             │    jobs.json                              │
│ Linux/macOS │  ~/.openclaw/cron/jobs.json               │
│ macOS       │  ~/.openclaw/cron/jobs.json               │
└─────────────┴──────────────────────────────────────────┘
```

### 模板文件
技能目录已提供 `cron-jobs-template.json` 文件，可直接复制到对应路径使用。

**注意**：如果未配置 Cron 任务，技能功能正常但不会自动推送报告。

---

Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

---

## 🌐 技能仓库

**官方仓库**: `https://github.com/zhaog100/openclaw-skills/tree/main/skills/oil-gold-correlation`
**主分支**: `main`
**版本**: `v2.1.4`

### 📥 下载方式

#### 1. 通过 Git 下载（推荐）
```bash
git clone https://github.com/zhaog100/openclaw-skills.git
cd openclaw-skills/skills/oil-gold-correlation
git checkout v2.1.4
```

#### 2. 通过 OpenClaw CLI 安装
```bash
openclaw skills install oil-gold-correlation@v2.1.4
```

#### 3. 手动下载
下载链接: `https://github.com/zhaog100/openclaw-skills/tree/main/skills/oil-gold-correlation`

