# Diagram Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 使用Graphviz生成图表和流程图 - 支持流程图、架构图、状态图、数据流图

## 🎯 简介

Diagram Generator 是一个基于Graphviz的图表生成工具，使用Python实现，支持多种图表类型。

### 核心功能

- ✅ **流程图** - 业务流程、决策树
- ✅ **架构图** - 系统架构、模块关系
- ✅ **状态图** - 状态机、生命周期
- ✅ **数据流图** - 数据流、系统交互

## 🚀 快速开始

### 安装

✅ **已预安装**：
- **Graphviz**: 系统工具 (`/usr/bin/dot`)
- **Python graphviz**: 虚拟环境库 (`/tmp/chart-venv/`)

### 激活环境

```bash
source /tmp/chart-venv/bin/activate
```

### 基础用法

```python
from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='My Flowchart')
dot.node('A', 'Start')
dot.node('B', 'Process')
dot.node('C', 'End')

dot.edges(['AB', 'BC'])

# 保存
dot.render('my_flowchart', format='png', cleanup=True)
```

## 📊 支持的图表类型

### 1. 流程图（Flowchart）

```python
from graphviz import Digraph

dot = Digraph('flowchart', format='png')
dot.attr(rankdir='TB')  # 从上到下

dot.node('start', 'Start', shape='ellipse')
dot.node('decision', 'Decision?', shape='diamond')
dot.node('yes', 'Yes Action', shape='box')
dot.node('no', 'No Action', shape='box')
dot.node('end', 'End', shape='ellipse')

dot.edges([
  ('start', 'decision'),
  ('decision', 'yes', 'Yes'),
  ('node', 'no', 'No'),
  ('yes', 'end'),
  ('no', 'end')
])

dot.render('flowchart', view=True)
```

### 2. 架构图（Architecture Diagram）

```python
from graphviz import Graph

dot = Graph('architecture', format='png')
dot.attr(rankdir='LR')  # 从左到右

# 节点
dot.node('web', 'Web App')
dot.node('api', 'API Server')
dot.node('db', 'Database')
dot.node('cache', 'Redis')

# 连接
dot.edge('web', 'api')
dot.edge('api', 'db')
dot.edge('api', 'cache')

dot.render('architecture', view=True)
```

### ... (truncated) ...
