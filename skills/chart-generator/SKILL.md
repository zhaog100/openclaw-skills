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
