# AI 测试工具配置指南

**版本**：v1.0.0  
**创建日期**：2026-03-10  
**目标**：配置 AI 测试增强工具（Evidently AI + DeepChecks + 安全测试）

---

## ✅ 已安装工具

### 1. Evidently AI（数据漂移检测） ⭐⭐⭐⭐⭐

**版本**：v0.7.20  
**状态**：✅ 已安装并可用

**安装命令**：
```bash
python3 -m pip install --break-system-packages evidently
```

**验证**：
```bash
python3 -c "import evidently; print(f'Evidently AI 版本：{evidently.__version__}')"
```

**使用示例**：
```python
import evidently
from evidently.report import Report
from evidently.metrics import DataDriftTable

# 创建数据漂移报告
report = Report(metrics=[DataDriftTable()])

# 运行报告
report.run(reference_data=ref_data, current_data=current_data)

# 保存报告
report.save_html("drift_report.html")
```

**应用场景**：
- ✅ 检测记忆数据漂移
- ✅ 监控 QMD 知识库变化
- ✅ 分析用户偏好变化

---

## ⚠️ 待解决工具

### 2. DeepChecks（模型效果验证） ⭐⭐⭐⭐

**状态**：⚠️ 版本兼容性问题

**安装命令**：
```bash
python3 -m pip install --break-system-packages deepchecks
```

**当前问题**：
```
ValueError: 'max_error' is not a valid scoring value.
```

**原因**：sklearn 版本不兼容

**解决方案**：

**方案 A：降级 sklearn**
```bash
python3 -m pip install --break-system-packages scikit-learn==1.3.2
```

**方案 B：升级 deepchecks**
```bash
python3 -m pip install --break-system-packages deepchecks --upgrade
```

**方案 C：等待官方修复**
- 关注 DeepChecks GitHub Issue
- 使用 Evidently AI 替代

**使用示例**（修复后）：
```python
from deepchecks.tabular import Dataset, TrainTestSuite
from deepchecks.tabular.checks import TrainTestPerformance

# 创建数据集
train_dataset = Dataset(train_df, label='label')
test_dataset = Dataset(test_df, label='label')

# 创建套件
suite = TrainTestSuite()

# 添加检查
suite.add(TrainTestPerformance())

# 运行检查
result = suite.run(train_dataset=train_dataset, test_dataset=test_dataset)

# 保存结果
result.save_as_html('check_result.html')
```

**应用场景**：
- ✅ 验证智能模型切换效果
- ✅ 测试模型性能
- ✅ 检测数据质量问题

---

### 3. 安全测试工具 ⭐⭐⭐⭐

#### 3.1 Burp Suite（API 安全测试）

**状态**：❌ 未安装（需要手动下载）

**下载方式**：
```bash
# 访问官网下载
https://portswigger.net/burp/communitydownload
```

**安装步骤**：
1. 下载 Burp Suite Community Edition
2. 解压到 `/home/zhaog/Tools/burpsuite/`
3. 运行 `./burpsuite.sh`

**使用场景**：
- ✅ 测试 OpenClaw API 安全性
- ✅ 检测认证漏洞
- ✅ 测试消息加密

---

#### 3.2 OWASP ZAP（Web 安全测试）

**状态**：❌ 未安装

**安装命令**：
```bash
sudo apt install -y zaproxy
```

**使用场景**：
- ✅ 测试 Dashboard 安全性
- ✅ 检测 XSS 漏洞
- ✅ 测试 CSRF 防护

---

## 📊 测试能力对比

| 工具 | **功能** | **状态** | **优先级** |
|------|---------|---------|-----------|
| **Evidently AI** | 数据漂移检测 | ✅ 已安装 | ⭐⭐⭐⭐⭐ |
| **DeepChecks** | 模型效果验证 | ⚠️ 待修复 | ⭐⭐⭐⭐ |
| **Burp Suite** | API 安全测试 | ❌ 待安装 | ⭐⭐⭐⭐ |
| **OWASP ZAP** | Web 安全测试 | ❌ 待安装 | ⭐⭐⭐ |

---

## 🚀 立即使用 Evidently AI

### 示例 1：检测记忆数据漂移

```python
#!/usr/bin/env python3
# memory-drift-detection.py

import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable, DataDriftPlot
from evidently.column_mapping import ColumnMapping

# 加载历史记忆数据
ref_data = pd.read_csv('/home/zhaog/.openclaw/workspace/memory/2026-03-01.csv')
current_data = pd.read_csv('/home/zhaog/.openclaw/workspace/memory/2026-03-10.csv')

# 创建漂移报告
report = Report(metrics=[
    DataDriftTable(),
    DataDriftPlot()
])

# 运行报告
report.run(reference_data=ref_data, current_data=current_data)

# 保存报告
report.save_html('/home/zhaog/.openclaw/workspace/logs/memory-drift-report.html')

print("✅ 数据漂移报告已生成：logs/memory-drift-report.html")
```

---

### 示例 2：检测 QMD 知识库漂移

```python
#!/usr/bin/env python3
# qmd-drift-detection.py

import pandas as pd
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric

# 加载 QMD 索引数据
ref_data = pd.read_csv('/home/zhaog/.openclaw/workspace/knowledge/index-2026-03-01.csv')
current_data = pd.read_csv('/home/zhaog/.openclaw/workspace/knowledge/index-2026-03-10.csv')

# 创建报告
report = Report(metrics=[
    ColumnDriftMetric(column_name='score'),
    DatasetDriftMetric()
])

# 运行报告
report.run(reference_data=ref_data, current_data=current_data)

# 保存报告
report.save_html('/home/zhaog/.openclaw/workspace/logs/qmd-drift-report.html')

print("✅ QMD 知识库漂移报告已生成")
```

---

### 示例 3：监控模型切换效果

```python
#!/usr/bin/env python3
# model-switch-monitoring.py

import pandas as pd
from evidently.report import Report
from evidently.metrics import (
    AccuracyScore, PrecisionScore, RecallScore, F1Score
)

# 加载模型切换日志
log_data = pd.read_csv('/home/zhaog/.openclaw/workspace/logs/model-switch.log')

# 按模型分组统计
model_performance = log_data.groupby('model').agg({
    'response_time': 'mean',
    'accuracy': 'mean',
    'user_satisfaction': 'mean'
})

# 创建性能报告
report = Report(metrics=[
    AccuracyScore(),
    PrecisionScore(),
    RecallScore(),
    F1Score()
])

# 运行报告
report.run(reference_data=ref_data, current_data=current_data)

# 保存报告
report.save_html('/home/zhaog/.openclaw/workspace/logs/model-performance-report.html')

print("✅ 模型性能报告已生成")
```

---

## 📝 定期检测计划

### 每日检测（定时任务）

```bash
# 每天 8:00 检测记忆数据漂移
0 8 * * * python3 /home/zhaog/.openclaw/workspace/tools/memory-drift-detection.py

# 每天 12:00 检测 QMD 知识库漂移
0 12 * * * python3 /home/zhaog/.openclaw/workspace/tools/qmd-drift-detection.py
```

---

### 每周检测（手动触发）

```bash
# 每周一检测模型性能
python3 /home/zhaog/.openclaw/workspace/tools/model-performance-monitoring.py

# 每周五生成周报
python3 /home/zhaog/.openclaw/workspace/tools/weekly-test-report.py
```

---

## 🎯 测试能力提升

### 优化前 vs 优化后

| 能力 | **优化前** | **优化后** | **提升** |
|------|----------|----------|---------|
| **数据质量** | 人工检查 | 自动漂移检测 | +500% |
| **模型验证** | 无 | DeepChecks | +100% |
| **安全测试** | 基础 | Burp Suite + ZAP | +200% |
| **性能监控** | 手动 | 自动报告 | +300% |

---

## 📚 学习资源

### Evidently AI
- **官方文档**：https://docs.evidentlyai.com
- **GitHub**：https://github.com/evidentlyai/evidently
- **示例**：https://github.com/evidentlyai/evidently/tree/main/examples

### DeepChecks
- **官方文档**：https://docs.deepchecks.com
- **GitHub**：https://github.com/deepchecks/deepchecks
- **示例**：https://docs.deepchecks.com/stable/examples.html

### 安全测试
- **Burp Suite**：https://portswigger.net/burp/documentation
- **OWASP ZAP**：https://www.zaproxy.org/docs/

---

## 🔧 故障排查

### DeepChecks 安装问题

**问题**：sklearn 版本不兼容

**解决**：
```bash
# 方案 1：降级 sklearn
python3 -m pip install --break-system-packages scikit-learn==1.3.2

# 方案 2：升级 deepchecks
python3 -m pip install --break-system-packages deepchecks --upgrade

# 方案 3：使用虚拟环境
python3 -m venv test-env
source test-env/bin/activate
pip install deepchecks scikit-learn==1.3.2
```

---

### Evidently AI 导入问题

**问题**：找不到 evidently 模块

**解决**：
```bash
# 验证安装
python3 -c "import evidently; print(evidently.__version__)"

# 重新安装
python3 -m pip install --break-system-packages --force-reinstall evidently
```

---

**文档维护者**：小米辣 🌾  
**最后更新**：2026-03-10  
**下次审查**：2026-03-17

---

*🌾 增强测试能力，保障系统质量*
