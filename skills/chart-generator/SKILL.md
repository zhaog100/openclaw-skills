---
name: chart-generator
description: Generate charts and graphs using Python (matplotlib, plotly, seaborn). Supports line charts, bar charts, pie charts, scatter plots, heatmaps, boxplots, and interactive charts.
---

# Chart Generator

Python-based chart generation skill with multiple libraries support.

## Features

- ✅ **matplotlib** - Static charts (line, bar, pie, scatter)
- ✅ **plotly** - Interactive charts (HTML output)
- ✅ **seaborn** - Statistical charts (heatmap, boxplot)

## Chart Types

1. **Line Chart** - Trends, time series
2. **Bar Chart** - Comparisons, rankings
3. **Pie Chart** - Proportions, distributions
4. **Scatter Plot** - Correlations, distributions
5. **Heatmap** - Matrix data, correlations
6. **Boxplot** - Statistical distributions
7. **Interactive Charts** - Plotly-based HTML charts

## Usage

### Activate Environment

```bash
source /tmp/chart-venv/bin/activate
```

### Generate Chart

```python
import matplotlib.pyplot as plt

# Data
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Create chart
plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o')
plt.title('My Chart')
plt.savefig('/tmp/chart.png', dpi=300)
```

## Installation Location

- **Virtual Environment**: `/tmp/chart-venv/`
- **Usage Guide**: `skills/chart-generator/USAGE.md`

## Examples

See `USAGE.md` for detailed examples:
- Line charts
- Bar charts
- Pie charts
- Scatter plots
- Heatmaps
- Boxplots
- Interactive charts

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (miliger)

**商业使用授权**：
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 企业定制版：¥99,999 一次性（源码买断）
