# Oil-Gold Correlation — 石油黄金相关性分析工具

_版本: 2.1.5 | MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)_

⚠️ **重要声明**: 本工具提供技术分析参考，不构成投资建议。市场有风险，投资需谨慎。所有分析结果仅供参考。

---

## 🌐 技能仓库

**官方仓库**: `https://github.com/your-username/openclaw-skills/tree/main/skills/oil-gold-correlation`
**主分支**: `main`
**版本**: `v2.1.5`

### 📥 下载方式

#### 1. 通过 Git 下载（推荐）
```bash
git clone https://github.com/your-username/openclaw-skills.git
cd openclaw-skills/skills/oil-gold-correlation
git checkout v2.1.4
```

#### 2. 通过 OpenClaw CLI 安装
```bash
openclaw skills install oil-gold-correlation@v2.1.4
```

#### 3. 手动下载
下载链接: `https://github.com/your-username/openclaw-skills/tree/main/skills/oil-gold-correlation`

---

## 功能

- **8 种相关性分析方法**：Pearson / Spearman / Kendall / Granger 因果 / Cointegration / DCC-GARCH 等
- **多数据源**：akshare（国内）/ yfinance（国际）/ FRED（宏观）/ Alpha Vantage（备用）
- **投资顾问**：8 品种 × 9 技术指标，自动生成操作建议
- **定时推送**：早盘(10:00) / 晚盘(21:00) / 美盘(22:00) + 夏令时自适应
- **可视化图表**：4 种图表类型（折线/散点/热力/回归）

## 安装（推荐 Miniconda）

### 1. 创建 Python 环境

**Miniconda（推荐，跨平台一致）**:
```bash
# 下载并安装 Miniconda: https://docs.conda.io/en/latest/miniconda.html
conda create -n oil-gold python=3.11 -y
conda activate oil-gold
```

**或直接使用系统 Python**:
```bash
python3 --version  # 需要 3.10+
```

### 2. 安装依赖

```bash
# 激活 conda 环境后（如果使用）
pip install -r requirements.txt
```

## 快速开始（使用跨平台启动脚本）

### 一键执行全流程

**Linux/macOS**:
```bash
chmod +x run.sh
./run.sh all 1y
```

**Windows**:
```batch
run.bat all 1y
```

### 分步执行

```bash
# 1. 获取数据
./run.sh fetch 1y

# 2. 分析相关性
./run.sh analyze all

# 3. 生成可视化
./run.sh visualize

# 4. 生成报告
./run.sh report

# 5. 获取投资建议（短期）
./run.sh advisor 3

# 6. 数据源健康检查
./run.sh health
```

## 配置

### 1. 推送渠道配置

编辑 `config/push-config.yaml`，支持多渠道推送（QQ/Telegram/Discord）。

### 2. 定时任务配置

**重要**: 技能安装后需要手动配置定时任务，否则报告不会自动推送。

**使用方法**:
1. 复制 `cron-jobs-template.json` 到 `~/.openclaw/cron/jobs.json`
2. 根据实际路径修改配置文件
3. 验证任务: `openclaw cron list`

**各平台路径**:
- **Windows**: `%USERPROFILE%\.openclaw\cron\jobs.json`
- **Linux/macOS**: `~/.openclaw/cron/jobs.json`

### 3. 手动测试定时任务

```bash
openclaw cron run oil-gold-morning
```

## 数据源策略

### 主数据源：akshare（国内期货）
- **优势**: 无IP限制，稳定可靠
- **品种**: 沪金AU0、原油期货SC0
- **优先级**: 第一优先，默认使用

### 备用数据源：yfinance（国际行情）
- **注意**: 腾讯云IP可能被限速
- **策略**: akshare失败时自动切换
- **缓存**: 30分钟内不重复请求

### 多源智能调度
- 自动检测可用数据源
- 失败重试 + 指数退避
- 数据源健康监控

## 依赖清单

### 核心依赖
- Python 3.10+
- pandas >= 2.0
- numpy >= 1.24
- scipy >= 1.10
- statsmodels >= 0.14

### 数据源依赖
- akshare >= 1.10（主数据源）
- yfinance >= 0.2.36（备用数据源）
- requests >= 2.28

### 可视化依赖
- plotly >= 5.0

## 作者

思捷娅科技 (SJYKJ)

## 完整安装检查清单

- [ ] 1. 下载技能文件到 `skills/oil-gold-correlation/`
- [ ] 2. 安装 Python 环境（推荐 Miniconda）
- [ ] 3. 创建 conda 环境: `conda create -n oil-gold python=3.11 -y`
- [ ] 4. 安装依赖: `pip install -r requirements.txt`
- [ ] 5. 验证数据源: `./run.sh fetch 7d`
- [ ] 6. 测试全流程: `./run.sh all`
- [ ] 7. 配置定时任务（复制模板到 cron/jobs.json）
- [ ] 8. 配置推送目标（编辑 push-config.yaml）
- [ ] 9. 手动测试推送: `openclaw cron run oil-gold-morning`