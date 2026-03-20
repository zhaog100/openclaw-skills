# 第 1 周 AI 测试技能学习指南

**版本**：v1.0.0  
**创建日期**：2026-03-10  
**目标**：掌握 Evidently AI、DeepChecks、OWASP ZAP 的核心用法

---

## 📅 学习日程

### 周一：Evidently AI 基础 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 理解数据漂移概念
- ✅ 安装并配置 Evidently AI
- ✅ 创建第一个漂移报告

**学习内容**：

#### 1. 数据漂移概念

**什么是数据漂移**：
```
数据漂移 = 生产数据分布 vs 训练数据分布 的差异

原因：
- 用户行为变化
- 季节性因素
- 系统变更
- 外部环境变化

影响：
- 模型性能下降
- 预测准确性降低
- 业务决策失误
```

**漂移类型**：
```
1. 特征漂移（Feature Drift）
   - 输入数据分布变化
   
2. 标签漂移（Label Drift）
   - 目标变量分布变化
   
3. 概念漂移（Concept Drift）
   - 特征与标签关系变化
```

---

#### 2. 安装配置

**已安装**：
```bash
✅ Evidently AI v0.7.20
✅ 依赖：pandas, scikit-learn, plotly
```

**验证安装**：
```bash
python3 -c "import evidently; print(f'Evidently AI 版本：{evidently.__version__}')"
# 输出：Evidently AI 版本：0.7.20
```

---

#### 3. 第一个漂移报告

**实战脚本**：`tools/memory-drift-detection.py`

```python
#!/usr/bin/env python3
"""
记忆数据漂移检测
检测今日记忆 vs 历史记忆的数据漂移
"""

import pandas as pd
from evidently.report import Report
from evidently.metrics import (
    DataDriftTable,
    DataDriftPlot,
    ColumnDriftMetric
)
import os
from datetime import datetime, timedelta

def load_memory_data(date_str):
    """加载指定日期的记忆数据"""
    file_path = f'/home/zhaog/.openclaw/workspace/memory/{date_str}.md'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在：{file_path}")
        return None
    
    # 读取 Markdown 文件，提取关键信息
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简化处理：统计字数、段落数等
    data = {
        'word_count': len(content),
        'paragraph_count': content.count('\n\n'),
        'header_count': content.count('#'),
        'code_block_count': content.count('```'),
        'timestamp': date_str
    }
    
    return pd.DataFrame([data])

def detect_memory_drift(ref_date, current_date):
    """检测记忆数据漂移"""
    print(f"=== 记忆数据漂移检测 ===")
    print(f"参考日期：{ref_date}")
    print(f"当前日期：{current_date}")
    print()
    
    # 加载数据
    ref_data = load_memory_data(ref_date)
    current_data = load_memory_data(current_date)
    
    if ref_data is None or current_data is None:
        print("❌ 数据加载失败")
        return
    
    print(f"参考数据：{len(ref_data)} 条记录")
    print(f"当前数据：{len(current_data)} 条记录")
    print()
    
    # 创建漂移报告
    report = Report(metrics=[
        DataDriftTable(),
        DataDriftPlot(),
        ColumnDriftMetric(column_name='word_count'),
        ColumnDriftMetric(column_name='paragraph_count')
    ])
    
    # 运行报告
    print("🔍 正在分析数据漂移...")
    report.run(reference_data=ref_data, current_data=current_data)
    
    # 保存报告
    report_path = f'/home/zhaog/.openclaw/workspace/logs/memory-drift-{current_date}.html'
    report.save_html(report_path)
    
    print(f"✅ 报告已保存：{report_path}")
    print()
    
    # 输出摘要
    print("📊 漂移摘要：")
    print("-" * 50)
    # 这里可以添加更多分析逻辑
    
    return report

if __name__ == '__main__':
    # 示例：检测今天 vs 7 天前的漂移
    current_date = datetime.now().strftime('%Y-%m-%d')
    ref_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    detect_memory_drift(ref_date, current_date)
```

**运行脚本**：
```bash
cd /home/zhaog/.openclaw/workspace
python3 tools/memory-drift-detection.py
```

**查看报告**：
```bash
# 在浏览器中打开
firefox logs/memory-drift-2026-03-10.html
```

---

#### 4. 实战练习

**练习 1**：检测 QMD 知识库漂移
```python
# 参考上面的脚本，修改为检测 QMD 知识库
# 提示：读取 knowledge/ 目录下的 Markdown 文件
```

**练习 2**：自定义漂移指标
```python
from evidently.metrics import Metric
# 创建一个自定义指标，检测记忆内容的情感变化
```

**练习 3**：时间序列漂移检测
```python
# 检测最近 7 天的数据漂移趋势
# 提示：使用循环加载每天的数据
```

---

**今日产出**：
- 📋 `tools/memory-drift-detection.py`
- 📋 `logs/memory-drift-2026-03-10.html`
- 📋 学习笔记（记录关键概念）

---

### 周二：Evidently AI 高级 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 自定义漂移指标
- ✅ 多列联合分析
- ✅ 时间序列漂移检测

**学习内容**：

#### 1. 自定义漂移指标

```python
from evidently.metrics import Metric
from evidently.core import IncludeTags, Tag

class WordCountDrift(Metric):
    """自定义指标：字数漂移"""
    
    def __init__(self):
        super().__init__()
    
    def calculate_value(self, current_data, reference_data):
        ref_mean = reference_data['word_count'].mean()
        curr_mean = current_data['word_count'].mean()
        
        drift = abs(curr_mean - ref_mean) / ref_mean
        
        return {
            'reference_mean': ref_mean,
            'current_mean': curr_mean,
            'drift_ratio': drift,
            'is_drift': drift > 0.2  # 阈值 20%
        }
```

---

#### 2. 多列联合分析

```python
from evidently.column_mapping import ColumnMapping
from evidently.metrics import ColumnDriftMetric

# 定义列映射
column_mapping = ColumnMapping()
column_mapping.target = 'user_satisfaction'
column_mapping.prediction = 'model_choice'
column_mapping.numerical_features = ['word_count', 'response_time']
column_mapping.categorical_features = ['model_type', 'topic']

# 创建报告
report = Report(metrics=[
    ColumnDriftMetric(column_name='word_count'),
    ColumnDriftMetric(column_name='response_time'),
    # ... 更多指标
])

report.run(
    reference_data=ref_data,
    current_data=current_data,
    column_mapping=column_mapping
)
```

---

#### 3. 时间序列漂移检测

```python
# 检测最近 7 天的漂移趋势
dates = pd.date_range(end=datetime.now(), periods=7)
drift_scores = []

for date in dates:
    date_str = date.strftime('%Y-%m-%d')
    data = load_memory_data(date_str)
    
    # 计算漂移分数
    drift_score = calculate_drift_score(data, baseline_data)
    drift_scores.append({
        'date': date_str,
        'drift_score': drift_score
    })

# 绘制趋势图
import matplotlib.pyplot as plt
plt.plot([d['date'] for d in drift_scores], 
         [d['drift_score'] for d in drift_scores])
plt.savefig('logs/drift-trend.png')
```

---

**今日产出**：
- 📋 `tools/custom-drift-metrics.py`
- 📋 `tools/time-series-drift.py`
- 📋 `logs/drift-trend.png`

---

### 周三：DeepChecks 基础 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 理解模型验证概念
- ✅ 安装并配置 DeepChecks
- ✅ 创建第一个模型验证报告

**学习内容**：

#### 1. 模型验证概念

**什么是模型验证**：
```
模型验证 = 评估模型性能 + 检测模型问题

验证内容：
- 准确性（Accuracy）
- 精确率（Precision）
- 召回率（Recall）
- F1 分数
- 推理时间
- 数据漂移
- 标签漂移
```

---

#### 2. 第一个模型验证报告

**实战脚本**：`tools/model-performance-check.py`

```python
#!/usr/bin/env python3
"""
模型性能验证
验证智能模型切换的效果
"""

import pandas as pd
from deepchecks.tabular import Dataset, TrainTestSuite
from deepchecks.tabular.checks import (
    TrainTestPerformance,
    TrainTestLabelDrift,
    ModelInferenceTime,
    BoostingOverfit
)

def load_model_switch_log():
    """加载模型切换日志"""
    log_file = '/home/zhaog/.openclaw/workspace/logs/model-switch.log'
    
    # 读取日志（假设是 CSV 格式）
    df = pd.read_csv(log_file)
    
    return df

def validate_model_performance():
    """验证模型性能"""
    print("=== 模型性能验证 ===")
    print()
    
    # 加载数据
    data = load_model_switch_log()
    
    # 创建数据集
    dataset = Dataset(
        data,
        label='user_satisfaction',
        cat_features=['model_type'],
        numerical_features=['response_time', 'accuracy']
    )
    
    # 创建套件
    suite = TrainTestSuite()
    
    # 添加检查
    suite.add(TrainTestPerformance())
    suite.add(TrainTestLabelDrift())
    suite.add(ModelInferenceTime())
    
    # 运行检查
    print("🔍 正在验证模型性能...")
    result = suite.run(dataset)
    
    # 保存结果
    result.save_as_html('logs/model-performance-report.html')
    
    print("✅ 报告已保存：logs/model-performance-report.html")
    print()
    
    return result

if __name__ == '__main__':
    validate_model_performance()
```

---

**今日产出**：
- 📋 `tools/model-performance-check.py`
- 📋 `logs/model-performance-report.html`

---

### 周四：DeepChecks 高级 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 模型性能监控
- ✅ 模型退化检测
- ✅ 集成到智能切换

**学习内容**：

#### 1. 模型性能监控

```python
from deepchecks.tabular.suite import ModelEvaluationSuite

# 创建监控套件
monitor_suite = ModelEvaluationSuite()

# 添加监控指标
monitor_suite.add(checks=[
    'performance_report',
    'model_error_analysis',
    'feature_label_correlation',
    'simple_model_comparison'
])

# 运行监控
result = monitor_suite.run(dataset)
```

---

#### 2. 集成到智能切换

```python
# skills/smart-model-switch/scripts/model-validator.py

def validate_before_switch(model_name):
    """切换前验证模型"""
    # 获取模型指标
    metrics = get_model_metrics(model_name)
    
    # 阈值检查
    if metrics['accuracy'] < 0.8:
        log_warning(f"{model_name} 准确率低于阈值")
        return False
    
    if metrics['response_time'] > 5.0:
        log_warning(f"{model_name} 响应时间过长")
        return False
    
    return True
```

---

**今日产出**：
- 📋 `tools/model-monitoring.py`
- 📋 `skills/smart-model-switch/scripts/model-validator.py`

---

### 周五：OWASP ZAP 实战 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 理解 Web 安全测试概念
- ✅ 使用 OWASP ZAP 进行被动扫描
- ✅ 使用 OWASP ZAP 进行主动扫描

**学习内容**：

#### 1. Web 安全测试概念

**OWASP Top 10**：
```
1. 注入（Injection）
2. 认证失效（Broken Authentication）
3. 敏感信息泄露（Sensitive Data Exposure）
4. XML 外部实体（XXE）
5. 访问控制失效（Broken Access Control）
6. 安全配置错误（Security Misconfiguration）
7. 跨站脚本（XSS）
8. 不安全的反序列化（Insecure Deserialization）
9. 使用含已知漏洞的组件
10. 日志记录和监控不足
```

---

#### 2. 被动扫描

**已运行**：
```bash
✅ ZAP 后台模式（端口 8090）
✅ 被动扫描规则（80+ 条）
```

**查看结果**：
```bash
# 在 ZAP GUI 中查看
# Sites 树 → Alerts 标签页
```

---

#### 3. 主动扫描脚本

**实战脚本**：`tools/security-scan.sh`

```bash
#!/bin/bash
# OWASP ZAP 安全扫描脚本

API_KEY="your_zap_api_key"
BASE_URL="http://127.0.0.1:8090"
TARGET="http://127.0.0.1:18789"

echo "=== OWASP ZAP 安全扫描 ==="
echo "目标：$TARGET"
echo ""

# 启动爬取
echo "🕷️ 启动爬取..."
curl "$BASE_URL/JSON/spider/action/scan/?url=$TARGET&apikey=$API_KEY"
sleep 60

# 启动主动扫描
echo "🔍 启动主动扫描..."
curl "$BASE_URL/JSON/ascan/action/scan/?url=$TARGET&apikey=$API_KEY"
sleep 120

# 获取警报
echo "📊 获取警报..."
high_alerts=$(curl "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | jq '[.alerts[] | select(.riskcode=="2")] | length')
medium_alerts=$(curl "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | jq '[.alerts[] | select(.riskcode=="1")] | length')

echo ""
echo "📋 扫描结果："
echo "  高风险漏洞：$high_alerts"
echo "  中风险漏洞：$medium_alerts"

# 阈值检查
if [ "$high_alerts" -gt 0 ]; then
    echo "❌ 发现高风险漏洞，需要立即修复"
    exit 1
fi

if [ "$medium_alerts" -gt 5 ]; then
    echo "⚠️ 发现多个中风险漏洞，建议修复"
    exit 2
fi

echo "✅ 安全检查通过"
exit 0
```

---

**今日产出**：
- 📋 `tools/security-scan.sh`
- 📋 `logs/security-report.html`

---

### 周末：整合测试 ⭐⭐⭐⭐⭐

**学习目标**：
- ✅ 整合所有测试工具
- ✅ 创建完整测试报告
- ✅ 配置定时任务

**实战项目**：

创建完整测试报告脚本：
```python
# tools/full-test-report.py

from memory_drift_detection import detect_memory_drift
from model_performance_check import validate_model_performance
import subprocess

def generate_full_report():
    """生成完整测试报告"""
    print("=== 生成完整测试报告 ===")
    print()
    
    # 1. 数据漂移检测
    print("1️⃣ 数据漂移检测...")
    detect_memory_drift('2026-03-03', '2026-03-10')
    print()
    
    # 2. 模型性能验证
    print("2️⃣ 模型性能验证...")
    validate_model_performance()
    print()
    
    # 3. 安全扫描
    print("3️⃣ 安全扫描...")
    subprocess.run(['bash', 'tools/security-scan.sh'])
    print()
    
    # 4. 生成汇总报告
    print("4️⃣ 生成汇总报告...")
    # TODO: 整合所有报告
    
    print("✅ 完整测试报告已生成")

if __name__ == '__main__':
    generate_full_report()
```

**配置定时任务**：
```bash
# 添加到 crontab
# 每天早上 8:00 数据漂移检测
0 8 * * * python3 /home/zhaog/.openclaw/workspace/tools/memory-drift-detection.py

# 每天 12:00 模型性能验证
0 12 * * * python3 /home/zhaog/.openclaw/workspace/tools/model-performance-check.py

# 每周日 2:00 安全扫描
0 2 * * 0 bash /home/zhaog/.openclaw/workspace/tools/security-scan.sh
```

---

**周末产出**：
- 📋 `tools/full-test-report.py`
- 📋 定时任务配置
- 📋 完整测试报告模板

---

## 📊 学习检查清单

### 周一检查
- [ ] 理解数据漂移概念
- [ ] 运行第一个漂移报告
- [ ] 查看并理解报告内容

### 周二检查
- [ ] 创建自定义漂移指标
- [ ] 完成时间序列漂移检测

### 周三检查
- [ ] 理解模型验证概念
- [ ] 运行第一个模型验证报告

### 周四检查
- [ ] 创建模型监控脚本
- [ ] 集成到智能切换系统

### 周五检查
- [ ] 理解 OWASP Top 10
- [ ] 运行安全扫描脚本

### 周末检查
- [ ] 整合所有测试工具
- [ ] 配置定时任务
- [ ] 生成完整测试报告

---

## 📚 参考资源

### Evidently AI
- **官方文档**：https://docs.evidentlyai.com
- **示例库**：https://github.com/evidentlyai/evidently/tree/main/examples
- **指标参考**：https://docs.evidentlyai.com/reference/all-metrics

### DeepChecks
- **官方文档**：https://docs.deepchecks.com
- **示例库**：https://docs.deepchecks.com/stable/examples.html
- **检查参考**：https://docs.deepchecks.com/stable/checks.html

### OWASP ZAP
- **官方文档**：https://www.zaproxy.org/docs/
- **API 参考**：https://www.zaproxy.org/docs/api/
- **OWASP Top 10**：https://owasp.org/www-project-top-ten/

---

**文档维护者**：小米辣 🌾  
**最后更新**：2026-03-10  
**下周审查**：2026-03-17

---

*🌾 循序渐进，掌握 AI 测试核心技能*
