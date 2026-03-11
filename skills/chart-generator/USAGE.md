# 图表生成技能使用指南

## ✅ 安装状态

**安装时间**：2026-03-09 22:27
**Python 图表库**：
- ✅ matplotlib（静态图表）
- ✅ plotly（交互式图表）
- ✅ seaborn（统计图表）

**安装位置**：`/tmp/chart-venv/`

---

## 🚀 使用方式

### **1. 激活虚拟环境**

```bash
source /tmp/chart-venv/bin/activate
```

### **2. 基础图表生成**

#### **折线图**

```python
import matplotlib.pyplot as plt

# 数据
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o', linestyle='-', color='b')

# 添加标签
plt.title('折线图示例')
plt.xlabel('X 轴')
plt.ylabel('Y 轴')

# 保存图表
plt.savefig('/tmp/line-chart.png', dpi=300, bbox_inches='tight')
print("✅ 折线图已保存: /tmp/line-chart.png")
```

#### **柱状图**

```python
import matplotlib.pyplot as plt

# 数据
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]

# 创建图表
plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='skyblue')

# 添加标签
plt.title('柱状图示例')
plt.xlabel('类别')
plt.ylabel('数值')

# 保存图表
plt.savefig('/tmp/bar-chart.png', dpi=300, bbox_inches='tight')
print("✅ 柱状图已保存: /tmp/bar-chart.png")
```

#### **饼图**

```python
import matplotlib.pyplot as plt

# 数据
labels = ['A', 'B', 'C', 'D']
sizes = [30, 20, 25, 25]
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

# 创建图表
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)

# 添加标题
plt.title('饼图示例')

# 保存图表
plt.savefig('/tmp/pie-chart.png', dpi=300, bbox_inches='tight')
print("✅ 饼图已保存: /tmp/pie-chart.png")
```

#### **散点图**

```python
import matplotlib.pyplot as plt
import numpy as np

# 数据
x = np.random.randn(50)
y = np.random.randn(50)

# 创建图表
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.6, c='blue')

# 添加标签
plt.title('散点图示例')
plt.xlabel('X 轴')
plt.ylabel('Y 轴')

# 保存图表
plt.savefig('/tmp/scatter-chart.png', dpi=300, bbox_inches='tight')
print("✅ 散点图已保存: /tmp/scatter-chart.png")
```

---

### **3. 高级图表（Seaborn）**

#### **热力图**

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 数据
data = np.random.rand(10, 10)

# 创建图表
plt.figure(figsize=(12, 8))
sns.heatmap(data, annot=True, cmap='coolwarm', fmt='.2f')

# 添加标题
plt.title('热力图示例')

# 保存图表
plt.savefig('/tmp/heatmap.png', dpi=300, bbox_inches='tight')
print("✅ 热力图已保存: /tmp/heatmap.png")
```

#### **箱线图**

```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 数据
data = np.random.randn(100, 5)

# 创建图表
plt.figure(figsize=(10, 6))
sns.boxplot(data=data)

# 添加标签
plt.title('箱线图示例')
plt.xlabel('类别')
plt.ylabel('数值')

# 保存图表
plt.savefig('/tmp/boxplot.png', dpi=300, bbox_inches='tight')
print("✅ 箱线图已保存: /tmp/boxplot.png")
```

---

### **4. 交互式图表（Plotly）**

#### **交互式折线图**

```python
import plotly.graph_objects as go

# 数据
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# 创建图表
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='数据'))

# 更新布局
fig.update_layout(
    title='交互式折线图',
    xaxis_title='X 轴',
    yaxis_title='Y 轴'
)

# 保存为 HTML
fig.write_html('/tmp/interactive-line-chart.html')
print("✅ 交互式折线图已保存: /tmp/interactive-line-chart.html")
```

#### **交互式柱状图**

```python
import plotly.graph_objects as go

# 数据
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]

# 创建图表
fig = go.Figure(data=[go.Bar(x=categories, y=values)])

# 更新布局
fig.update_layout(
    title='交互式柱状图',
    xaxis_title='类别',
    yaxis_title='数值'
)

# 保存为 HTML
fig.write_html('/tmp/interactive-bar-chart.html')
print("✅ 交互式柱状图已保存: /tmp/interactive-bar-chart.html")
```

---

## 🎯 实际用例

### **用例1：项目进度图表**

```python
import matplotlib.pyplot as plt
import numpy as np

# 数据
tasks = ['需求分析', '设计', '开发', '测试', '部署']
progress = [100, 90, 70, 40, 20]

# 创建图表
plt.figure(figsize=(12, 6))
bars = plt.barh(tasks, progress, color='skyblue')

# 添加百分比标签
for bar, prog in zip(bars, progress):
    plt.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
             f'{prog}%', va='center', fontsize=12)

# 添加标签
plt.title('项目进度图', fontsize=16, fontweight='bold')
plt.xlabel('完成度 (%)', fontsize=12)
plt.xlim(0, 110)

# 保存图表
plt.tight_layout()
plt.savefig('/tmp/project-progress.png', dpi=300)
print("✅ 项目进度图已保存")
```

### **用例2：Token 使用趋势**

```python
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 数据
days = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(7, 0, -1)]
tokens = [15000, 18000, 22000, 19000, 25000, 21000, 23000]

# 创建图表
plt.figure(figsize=(12, 6))
plt.plot(days, tokens, marker='o', linestyle='-', color='#2E86DE', linewidth=2, markersize=8)

# 添加数据标签
for i, (day, token) in enumerate(zip(days, tokens)):
    plt.text(i, token + 500, f'{token:,}', ha='center', fontsize=10)

# 添加标签
plt.title('Token 使用趋势（最近7天）', fontsize=16, fontweight='bold')
plt.xlabel('日期', fontsize=12)
plt.ylabel('Token 数量', fontsize=12)
plt.grid(axis='y', alpha=0.3)

# 保存图表
plt.tight_layout()
plt.savefig('/tmp/token-trend.png', dpi=300)
print("✅ Token 使用趋势图已保存")
```

### **用例3：技能就绪率饼图**

```python
import matplotlib.pyplot as plt

# 数据
labels = ['完全就绪', '部分就绪']
sizes = [9, 4]
colors = ['#27ae60', '#f39c12']
explode = (0.1, 0)

# 创建图表
plt.figure(figsize=(10, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90,
        textprops={'fontsize': 14})

# 添加标题
plt.title('技能就绪率分布', fontsize=16, fontweight='bold')

# 保存图表
plt.tight_layout()
plt.savefig('/tmp/skill-readiness.png', dpi=300)
print("✅ 技能就绪率饼图已保存")
```

---

## 📊 图表类型对比

| 图表类型 | 适用场景 | 库 | 交互性 |
|---------|---------|---|--------|
| **折线图** | 趋势、时间序列 | matplotlib | ❌ |
| **柱状图** | 对比、排名 | matplotlib | ❌ |
| **饼图** | 占比、分布 | matplotlib | ❌ |
| **散点图** | 相关性、分布 | matplotlib | ❌ |
| **热力图** | 矩阵数据、相关性 | seaborn | ❌ |
| **箱线图** | 统计分布 | seaborn | ❌ |
| **交互折线图** | 趋势、时间序列 | plotly | ✅ |
| **交互柱状图** | 对比、排名 | plotly | ✅ |

---

## ⚠️ 注意事项

1. **中文字体**：
   ```python
   plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
   plt.rcParams['axes.unicode_minus'] = False  # 负号显示
   ```

2. **保存路径**：
   - PNG 格式：适合静态展示
   - HTML 格式：适合交互式展示（Plotly）

3. **虚拟环境**：
   - 每次使用前需要激活：`source /tmp/chart-venv/bin/activate`

---

## 🔧 常用配置

### **设置中文字体**

```python
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
```

### **设置图表样式**

```python
# Seaborn 样式
import seaborn as sns
sns.set_style("whitegrid")  # whitegrid, darkgrid, white, dark, ticks

# Matplotlib 样式
plt.style.use('seaborn')  # seaborn, ggplot, bmh, etc.
```

---

## 🚀 快速测试

```bash
# 激活虚拟环境
source /tmp/chart-venv/bin/activate

# 测试图表生成
python3 << 'EOF'
import matplotlib.pyplot as plt

# 简单折线图
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o')
plt.title('测试图表')
plt.savefig('/tmp/test-chart.png', dpi=300)

print("✅ 测试图表已保存: /tmp/test-chart.png")
EOF

# 查看文件
ls -lh /tmp/test-chart.png
```

---

**官家，图表生成技能已安装完成！** 🌾

**安装的库**：matplotlib + plotly + seaborn
