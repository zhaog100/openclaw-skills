# Chart Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Generate charts and graphs using Python (matplotlib, plotly, seaborn)

## 📊 简介

Chart Generator 是一个基于 Python 的图表生成技能，支持多种图表类型和可视化库。

### 核心功能

- ✅ **matplotlib** - 静态图表（折线图、柱状图、饼图、散点图）
- ✅ **plotly** - 交互式图表（HTML 输出）
- ✅ **seaborn** - 统计图表（热力图、箱线图）

### 支持的图表类型

1. **折线图** - 趋势分析、时间序列
2. **柱状图** - 比较、排名
3. **饼图** - 比例、分布
4. **散点图** - 相关性、分布
5. **热力图** - 矩阵数据、相关性
6. **箱线图** - 统计分布
7. **交互式图表** - 基于 Plotly 的 HTML 图表

## 🚀 快速开始

### 激活环境

```bash
source /tmp/chart-venv/bin/activate
```

### 生成图表示例

```python
import matplotlib.pyplot as plt

# 数据
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o')
plt.title('My Chart')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.grid(True)
plt.savefig('/tmp/chart.png', dpi=300)
```

## 📖 使用方法

详细使用方法请查看：
- **使用指南**：[USAGE.md](./USAGE.md)
- **技能文档**：[SKILL.md](./SKILL.md)

## 📦 安装

### 系统要求

- Python 3.7+
- matplotlib
- plotly
- seaborn

### 安装依赖

```bash
# 创建虚拟环境
python3 -m venv /tmp/chart-venv
source /tmp/chart-venv/bin/activate

# 安装依赖
pip install matplotlib plotly seaborn
```

## 💡 使用场景

- 数据可视化
- 报告生成
- 统计分析
- 趋势分析
- 数据探索

## 📂 文件结构

```
chart-generator/
├── SKILL.md          # 技能文档
├── USAGE.md          # 使用指南
├── README.md         # 本文件
└── package.json      # 包信息
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

Copyright (c) 2026 米粒儿 (miliger)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
