---
name: diagram-generator
description: Generate diagrams and flowcharts using Graphviz (Python). Supports flowcharts, architecture diagrams, state diagrams, and data flow diagrams.
---

# Diagram Generator

Graphviz-based diagram generation skill using Python.

## Features

- ✅ **Flowcharts** - Business processes, decision trees
- ✅ **Architecture Diagrams** - System architecture, module relationships
- ✅ **State Diagrams** - State machines, lifecycles
- ✅ **Data Flow Diagrams** - Data flow, system interactions

## Installation

✅ Already installed:
- **Graphviz**: System tool (`/usr/bin/dot`)
- **Python graphviz**: Library in `/tmp/chart-venv/`

## Usage

### Activate Environment

```bash
source /tmp/chart-venv/bin/activate
```

### Basic Flowchart

```python
from graphviz import Digraph

# Create flowchart
dot = Digraph()
dot.attr(rankdir='TB')

# Add nodes
dot.node('A', 'Start', shape='ellipse', style='filled', fillcolor='lightblue')
dot.node('B', 'Decision', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('C', 'Execute', shape='box', style='filled', fillcolor='lightgreen')
dot.node('D', 'End', shape='ellipse', style='filled', fillcolor='lightcoral')

# Add edges
dot.edge('A', 'B')
dot.edge('B', 'C', label='Yes')
dot.edge('B', 'D', label='No')
dot.edge('C', 'D')

# Save as PNG
dot.render('/tmp/flowchart', format='png', cleanup=True)

print("✅ Flowchart generated")
```

## Supported Formats

- **PNG**: Bitmap format (recommended)
- **SVG**: Vector format
- **PDF**: Print format

## Node Shapes

- `box` - Rectangle (normal steps)
- `diamond` - Diamond (decisions)
- `ellipse` - Ellipse (start/end)
- `circle` - Circle (initial state)
- `cylinder` - Cylinder (database)

## Documentation

See `GRAPHVIZ-USAGE.md` for detailed examples:
- Flowcharts
- Architecture diagrams
- State diagrams
- Data flow diagrams

## Quick Test

```bash
source /tmp/chart-venv/bin/activate

python3 << 'EOF'
from graphviz import Digraph

dot = Digraph()
dot.node('A', '测试节点')
dot.render('/tmp/test', format='png', cleanup=True)

print("✅ 测试图表已生成")
EOF

ls -lh /tmp/test.png
```

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
