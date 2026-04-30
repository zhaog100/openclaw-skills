# Plotly 数据可视化 API 调研报告 - 数据图表生成

**调研时间**: 2026-04-11 15:50
**库名称**: Plotly
**官网**: https://plotly.com/
**GitHub**: https://github.com/plotly/plotly.py
**文档**: https://plotly.com/python/
**PyPI**: https://pypi.org/project/plotly/
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 交互式数据可视化 |
| 开发方 | Plotly Technologies |
| 许可证 | MIT License（完全开源） |
| 图表类型 | 40+（柱状图、折线图、饼图、散点图等） |
| 语言支持 | Python, R, JavaScript |
| 费用 | 完全免费（开源版） |
| 在线版本 | Plotly Cloud（付费） |

---

## 🎯 核心功能

### 1. 交互式图表
- **Plotly Express**: 简化API，一行代码生成图表
- **Plotly Graph Objects**: 灵活API，完全自定义
- **在线导出**: HTML, PNG, JPG, PDF格式
- **响应式**: 适配桌面和移动设备

### 2. 丰富的图表类型
- **基础图表**: 柱状图、折线图、饼图、散点图
- **统计图表**: 箱线图、小提琴图、热力图
- **3D图表**: 3D散点图、3D曲面图
- **地图**: 地理地图、Choropleth地图
- **时间序列**: 时间序列图表、K线图

### 3. 数据分析集成
- **Pandas集成**: 直接使用DataFrame
- **NumPy集成**: 支持NumPy数组
- **JSON数据**: 支持JSON格式数据
- **实时更新**: 支持实时数据流

---

## 💰 定价方案

| 计划 | 费用 |
|------|--------|
| Free | 完全免费（MIT开源版） |
| Online（可选）| 付费（Plotly Cloud） |

---

## 🧧 使用方法

### 1. 安装
```bash
pip install plotly
```

### 2. Python基础使用（Plotly Express）
```python
import plotly.express as px
import pandas as pd

# 示例数据
data = {
    '日期': ['周一', '周二', '周三', '周四', '周五'],
    '点赞': [120, 150, 180, 90, 200],
    '收藏': [80, 100, 120, 70, 150]
}
df = pd.DataFrame(data)

# 创建柱状图
fig = px.bar(df, x='日期', y='点赞', title='小红书点赞数据')

# 显示图表
fig.show()

# 保存为HTML
fig.write_html('xiaohongshu_data.html')
```

### 3. 创建折线图（趋势分析）
```python
import plotly.express as px
import pandas as pd

# 示例数据（曝光趋势）
data = {
    '日期': pd.date_range(start='2026-04-01', periods=7, freq='D'),
    '曝光': [5000, 8000, 12000, 15000, 10000, 18000, 20000]
}
df = pd.DataFrame(data)

# 创建折线图
fig = px.line(df, x='日期', y='曝光', title='一周曝光趋势')

# 添加标记
fig.update_layout(
    xaxis_title='日期',
    yaxis_title='曝光量',
    hovermode='x unified'
)

# 显示图表
fig.show()
```

### 4. 创建饼图（用户分布）
```python
import plotly.express as px

# 示例数据（用户性别分布）
data = {
    '性别': ['女性', '男性', '未知'],
    '比例': [65, 30, 5]
}

# 创建饼图
fig = px.pie(data, values='比例', names='性别', title='用户性别分布')

# 显示百分比
fig.update_traces(textposition='inside', textinfo='percent+label')

# 显示图表
fig.show()
```

---

## 🚀 集成建议

### 场景1：小红书数据复盘
- **输入**: 曝光/点赞/收藏/评论数据
- **处理**: 调用Plotly生成可视化图表
- **输出**: 交互式图表（HTML格式）
- **应用**:
  - 数据复盘时展示趋势
  - 对比不同笔记数据
  - 生成周报/月报

### 场景2：竞品数据对比
- **输入**: 竞品数据（粉丝数/互动率等）
- **处理**: 调用Plotly生成对比图
- **输出**: 对比图表
- **应用**:
  - 竞品分析可视化
  - 识别优势和劣势

### 场景3：热词云图
- **输入**: 关键词列表（RAKE提取）
- **处理**: 调用Plotly生成词云
- **输出**: 词云图
- **应用**:
  - 展示热门关键词
  - 优化内容选题

---

## ⚠️ 注意事项

### 在线版本限制
- **开源版**: 完全免费，本地运行
- **在线版**: 付费（Plotly Cloud）
- **限制**: 免费版有水印（导出时）

### 性能
- **大数据集**: Plotly Express优化了大数据集处理
- **3D图表**: 需要GPU加速
- **导出**: HTML导出最快，PNG/JPG较慢

---

## 📋 集成清单

### 第1步：安装Plotly
- [ ] 安装plotly库
- [ ] 测试基础功能

### 第2步：编写可视化脚本
- [ ] 编写数据复盘图表函数
- [ ] 编写竞品对比图表函数
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到数据复盘流程
- [ ] 集成到周报生成流程
- [ ] 测试准确性

---

## ✅ 已完成

- [x] 库文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 安装plotly库
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **官网**: https://plotly.com/
- **GitHub**: https://github.com/plotly/plotly.py
- **文档**: https://plotly.com/python/
- **PyPI**: https://pypi.org/project/plotly/
- **示例**: https://plotly.com/python/

---

*小米椒 🌶️‍🔥 | 2026-04-11*
