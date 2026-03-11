# 结构图生成技能使用指南（Graphviz + Python）

## ✅ 安装状态

**安装时间**：2026-03-09 22:38
**工具名称**：Graphviz + Python graphviz 库
**版本**：
- Graphviz：系统工具
- Python graphviz：最新版

**安装位置**：
- Graphviz：`/usr/bin/dot`
- Python 库：`/tmp/chart-venv/`

---

## 🚀 使用方式

### **1. 激活虚拟环境**

```bash
source /tmp/chart-venv/bin/activate
```

### **2. 基础流程图**

```python
from graphviz import Digraph

# 创建流程图
dot = Digraph(comment='我的流程图')
dot.attr(rankdir='TD')  # 从上到下（TB/TD），从左到右（LR）

# 添加节点
dot.node('A', '开始', shape='ellipse', style='filled', fillcolor='lightblue')
dot.node('B', '判断', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('C', '执行', shape='box', style='filled', fillcolor='lightgreen')
dot.node('D', '结束', shape='ellipse', style='filled', fillcolor='lightcoral')

# 添加边
dot.edge('A', 'B')
dot.edge('B', 'C', label='Yes')
dot.edge('B', 'D', label='No')
dot.edge('C', 'D')

# 保存为 PNG
dot.render('/tmp/my-flowchart', format='png', cleanup=True)

print("✅ 流程图已生成")
```

---

## 📊 支持的图表类型

### **1. 流程图（Flowchart）**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='TB')

# 节点
dot.node('A', '开始')
dot.node('B', '判断', shape='diamond')
dot.node('C', '执行')
dot.node('D', '结束')

# 边
dot.edge('A', 'B')
dot.edge('B', 'C', label='Yes')
dot.edge('B', 'D', label='No')
dot.edge('C', 'D')

dot.render('flowchart', format='png', cleanup=True)
```

---

### **2. 架构图（Architecture Diagram）**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='TB')

# 子图 - 前端
with dot.subgraph(name='cluster_frontend') as c:
    c.attr(label='前端')
    c.node('web', 'Web App')
    c.node('mobile', 'Mobile App')

# 子图 - 后端
with dot.subgraph(name='cluster_backend') as c:
    c.attr(label='后端')
    c.node('api', 'API Gateway')
    c.node('auth', 'Auth Service')
    c.node('logic', 'Business Logic')

# 子图 - 数据层
with dot.subgraph(name='cluster_data') as c:
    c.attr(label='数据层')
    c.node('db', 'PostgreSQL')
    c.node('cache', 'Redis')

# 连接
dot.edge('web', 'api')
dot.edge('mobile', 'api')
dot.edge('api', 'auth')
dot.edge('api', 'logic')
dot.edge('auth', 'db')
dot.edge('logic', 'db')
dot.edge('logic', 'cache')

dot.render('architecture', format='png', cleanup=True)
```

---

### **3. 状态图（State Diagram）**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='LR')

# 状态
dot.node('start', '开始', shape='circle', style='filled', fillcolor='green')
dot.node('pending', '待处理', shape='box')
dot.node('processing', '处理中', shape='box')
dot.node('success', '成功', shape='box', style='filled', fillcolor='lightgreen')
dot.node('failed', '失败', shape='box', style='filled', fillcolor='lightcoral')
dot.node('end', '结束', shape='doublecircle', style='filled', fillcolor='red')

# 转换
dot.edge('start', 'pending')
dot.edge('pending', 'processing', label='开始处理')
dot.edge('processing', 'success', label='处理成功')
dot.edge('processing', 'failed', label='处理失败')
dot.edge('success', 'end')
dot.edge('failed', 'end')

dot.render('state-diagram', format='png', cleanup=True)
```

---

### **4. 数据流程图（Data Flow Diagram）**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='LR')

# 参与者
dot.node('user', '用户', shape='box', style='rounded')
dot.node('frontend', '前端', shape='box')
dot.node('api', 'API', shape='box')
dot.node('database', '数据库', shape='cylinder')

# 数据流
dot.edge('user', 'frontend', label='提交表单')
dot.edge('frontend', 'api', label='HTTP POST')
dot.edge('api', 'database', label='INSERT')
dot.edge('database', 'api', label='返回结果')
dot.edge('api', 'frontend', label='JSON Response')
dot.edge('frontend', 'user', label='显示结果')

dot.render('data-flow', format='png', cleanup=True)
```

---

## 🎯 实际用例

### **用例1：系统架构图**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='TB', size='10,8')

# 前端层
with dot.subgraph(name='cluster_0') as c:
    c.attr(label='前端层', style='filled', color='lightgrey')
    c.node('web', 'Web App')
    c.node('mobile', 'Mobile App')

# 网关层
with dot.subgraph(name='cluster_1') as c:
    c.attr(label='网关层', style='filled', color='lightblue')
    c.node('gateway', 'API Gateway')
    c.node('auth', 'Auth Service')

# 服务层
with dot.subgraph(name='cluster_2') as c:
    c.attr(label='服务层', style='filled', color='lightgreen')
    c.node('user_service', 'User Service')
    c.node('order_service', 'Order Service')
    c.node('product_service', 'Product Service')

# 数据层
with dot.subgraph(name='cluster_3') as c:
    c.attr(label='数据层', style='filled', color='lightyellow')
    c.node('mysql', 'MySQL', shape='cylinder')
    c.node('redis', 'Redis', shape='cylinder')
    c.node('mongodb', 'MongoDB', shape='cylinder')

# 连接
dot.edge('web', 'gateway')
dot.edge('mobile', 'gateway')
dot.edge('gateway', 'auth')
dot.edge('gateway', 'user_service')
dot.edge('gateway', 'order_service')
dot.edge('gateway', 'product_service')
dot.edge('user_service', 'mysql')
dot.edge('order_service', 'mysql')
dot.edge('order_service', 'redis')
dot.edge('product_service', 'mongodb')

dot.render('/tmp/system-architecture', format='png', cleanup=True)
print("✅ 系统架构图已生成")
```

---

### **用例2：用户流程图**

```python
from graphviz import Digraph

dot = Digraph()
dot.attr(rankdir='TB')

# 节点
dot.node('start', '用户访问', shape='ellipse', style='filled', fillcolor='lightblue')
dot.node('check_login', '已登录?', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('login', '登录', shape='box')
dot.node('register', '注册', shape='box')
dot.node('home', '首页', shape='box', style='filled', fillcolor='lightgreen')
dot.node('search', '搜索', shape='box')
dot.node('detail', '查看详情', shape='box')
dot.node('purchase', '购买', shape='box')
dot.node('end', '离开', shape='ellipse', style='filled', fillcolor='lightcoral')

# 边
dot.edge('start', 'check_login')
dot.edge('check_login', 'login', label='No')
dot.edge('check_login', 'home', label='Yes')
dot.edge('login', 'register', label='新用户')
dot.edge('login', 'home', label='成功')
dot.edge('register', 'login')
dot.edge('home', 'search')
dot.edge('search', 'detail')
dot.edge('detail', 'purchase')
dot.edge('detail', 'search', label='继续搜索')
dot.edge('purchase', 'home', label='成功')
dot.edge('home', 'end')

dot.render('/tmp/user-flow', format='png', cleanup=True)
print("✅ 用户流程图已生成")
```

---

## 🎨 节点形状和样式

### **常用形状**

| 形状 | 参数 | 适用场景 |
|------|------|---------|
| **矩形** | `shape='box'` | 普通步骤 |
| **圆角矩形** | `shape='box', style='rounded'` | 开始/结束 |
| **菱形** | `shape='diamond'` | 判断/分支 |
| **椭圆** | `shape='ellipse'` | 开始/结束 |
| **圆形** | `shape='circle'` | 初始状态 |
| **双圆** | `shape='doublecircle'` | 终止状态 |
| **圆柱** | `shape='cylinder'` | 数据库 |

### **常用样式**

```python
# 填充颜色
dot.node('A', '节点', style='filled', fillcolor='lightblue')

# 边框样式
dot.node('B', '节点', style='dashed')
dot.node('C', '节点', style='bold')

# 组合样式
dot.node('D', '节点', style='filled,rounded', fillcolor='lightgreen')
```

### **常用颜色**

- `lightblue` - 浅蓝色
- `lightgreen` - 浅绿色
- `lightyellow` - 浅黄色
- `lightcoral` - 浅珊瑚色
- `lightgrey` - 浅灰色

---

## 📋 常用参数

### **图级别参数**

```python
# 方向：TB（从上到下）、LR（从左到右）、BT、RL
dot.attr(rankdir='TB')

# 大小（英寸）
dot.attr(size='10,8')

# 背景
dot.attr(bgcolor='white')

# 字体
dot.attr(fontname='Arial')
```

### **节点参数**

```python
dot.node('id', 'label',
    shape='box',        # 形状
    style='filled',     # 样式
    fillcolor='lightblue',  # 填充颜色
    color='blue',       # 边框颜色
    fontcolor='black',  # 字体颜色
    fontsize='14',      # 字体大小
    width='2',          # 宽度（英寸）
    height='1'          # 高度（英寸）
)
```

### **边参数**

```python
dot.edge('A', 'B',
    label='标签',       # 边标签
    color='blue',       # 颜色
    style='dashed',     # 样式
    penwidth='2',       # 线宽
    fontsize='12'       # 字体大小
)
```

---

## ⚠️ 注意事项

1. **文件格式**：
   - PNG：位图格式（推荐）
   - SVG：矢量格式
   - PDF：打印格式

2. **中文字体**：
   ```python
   # 设置中文字体
   dot.attr(fontname='SimHei')
   ```

3. **虚拟环境**：
   - 每次使用前需要激活：`source /tmp/chart-venv/bin/activate`

4. **cleanup 参数**：
   - `cleanup=True` - 自动删除中间文件
   - `cleanup=False` - 保留 DOT 文件

---

## 🔧 常用命令

```bash
# 激活虚拟环境
source /tmp/chart-venv/bin/activate

# 测试生成
python3 << 'EOF'
from graphviz import Digraph
dot = Digraph()
dot.node('A', '测试')
dot.render('test', format='png', cleanup=True)
EOF

# 查看文件
ls -lh test.png
```

---

## 📊 图表类型对比

| 图表类型 | 复杂度 | 推荐场景 |
|---------|--------|---------|
| **流程图** | ⭐⭐ | 业务流程、决策树 |
| **架构图** | ⭐⭐⭐ | 系统架构、模块关系 |
| **状态图** | ⭐⭐⭐ | 状态机、生命周期 |
| **数据流图** | ⭐⭐ | 数据流向、系统交互 |

---

**官家，结构图生成技能已安装完成！** 🌾

**支持工具**：Graphviz + Python graphviz 库
**支持图表**：流程图、架构图、状态图、数据流图
