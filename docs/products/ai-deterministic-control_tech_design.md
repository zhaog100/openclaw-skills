# AI 确定性控制工具 - 技术设计文档

**版本**：v1.0
**创建日期**：2026-03-13
**创建者**：小米粒（开发代理）
**PRD**：[2026-03-12_ai-deterministic-control_PRD.md](2026-03-12_ai-deterministic-control_PRD.md)
**Issue**：#16

---

## 1. 架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────┐
│  CLI 入口层（deterministic.py）          │
│  - 参数解析（click）                     │
│  - 命令路由（4个核心命令）                │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  业务逻辑层                              │
│  ├── TemperatureController（温度控制）   │
│  ├── ConsistencyChecker（一致性检查）    │
│  ├── ReproducibilityGuarantor（复现保证）│
│  └── RandomnessMonitor（随机性监控）     │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  数据持久层                              │
│  ├── config.json（配置存储）             │
│  ├── history.db（输出历史，SQLite）      │
│  └── seeds.json（种子记录）              │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  AI API 层（ai_client.py）               │
│  - 智谱 API / DeepSeek API              │
│  - 统一接口封装                          │
└─────────────────────────────────────────┘
```

### 1.2 模块划分

| 模块 | 文件 | 职责 |
|------|------|------|
| **CLI入口** | `deterministic.py` | 命令行参数解析、路由 |
| **温度控制** | `temperature.py` | 温度参数设置、预设管理 |
| **一致性检查** | `consistency.py` | 多次输出对比、评分 |
| **复现保证** | `reproducibility.py` | 种子管理、确定性输出 |
| **随机性监控** | `monitor.py` | 历史分析、趋势报告 |
| **AI客户端** | `ai_client.py` | API封装、统一接口 |
| **配置管理** | `config.py` | 配置读写、持久化 |

---

## 2. 核心模块设计

### 2.1 温度控制模块（temperature.py）

**类设计**：
```python
class TemperatureController:
    """温度控制器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
    
    def set_temperature(self, temp: float) -> dict:
        """设置温度参数
        
        Args:
            temp: 温度值（0.0-2.0）
        
        Returns:
            配置确认信息
        
        Raises:
            ValueError: 温度超出范围
        """
        if not 0.0 <= temp <= 2.0:
            raise ValueError(f"温度必须在0.0-2.0之间，当前: {temp}")
        
        self.config["temperature"] = round(temp, 1)
        self._save_config()
        
        return {
            "temperature": self.config["temperature"],
            "mode": self._get_mode(temp),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_preset(self, preset_name: str) -> dict:
        """获取预设配置
        
        Args:
            preset_name: 预设名称（code/balance/creative/brainstorm）
        
        Returns:
            预设配置
        """
        presets = {
            "code": {"temperature": 0.0, "description": "高度确定性（代码/配置生成）"},
            "balance": {"temperature": 0.5, "description": "平衡模式（常规对话）"},
            "creative": {"temperature": 0.8, "description": "创造性模式（创意写作）"},
            "brainstorm": {"temperature": 1.5, "description": "高创造性模式（头脑风暴）"}
        }
        
        if preset_name not in presets:
            raise ValueError(f"未知预设: {preset_name}")
        
        return presets[preset_name]
    
    def _get_mode(self, temp: float) -> str:
        """根据温度判断模式"""
        if temp <= 0.3:
            return "高度确定性"
        elif temp <= 0.7:
            return "平衡模式"
        elif temp <= 1.0:
            return "创造性模式"
        else:
            return "高创造性模式"
```

### 2.2 一致性检查模块（consistency.py）

**类设计**：
```python
class ConsistencyChecker:
    """一致性检查器"""
    
    def __init__(self, history_db: str = "history.db"):
        self.conn = sqlite3.connect(history_db)
        self._init_db()
    
    def check_consistency(
        self, 
        prompt: str, 
        samples: int = 3,
        threshold: float = 80.0
    ) -> dict:
        """检查多次输出的一致性
        
        Args:
            prompt: 输入提示词
            samples: 采样次数（默认3次）
            threshold: 一致性阈值（默认80%）
        
        Returns:
            一致性检查结果
        """
        outputs = []
        for i in range(samples):
            output = self._call_ai(prompt)
            outputs.append(output)
            self._save_history(prompt, output)
        
        # 计算一致性评分
        scores = []
        for i in range(len(outputs)):
            for j in range(i+1, len(outputs)):
                score = self._calculate_similarity(outputs[i], outputs[j])
                scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "consistency_score": round(avg_score, 2),
            "passed": avg_score >= threshold,
            "samples": samples,
            "threshold": threshold,
            "details": {
                "min": min(scores) if scores else 0.0,
                "max": max(scores) if scores else 0.0,
                "std": stdev(scores) if len(scores) > 1 else 0.0
            }
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（使用difflib）"""
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio() * 100
    
    def _call_ai(self, prompt: str) -> str:
        """调用AI API"""
        # 使用统一AI客户端
        from ai_client import AIClient
        client = AIClient()
        return client.generate(prompt)
```

### 2.3 复现保证模块（reproducibility.py）

**类设计**：
```python
class ReproducibilityGuarantor:
    """复现保证器"""
    
    def __init__(self, seeds_file: str = "seeds.json"):
        self.seeds_file = seeds_file
        self.seeds = self._load_seeds()
    
    def generate_with_seed(
        self, 
        prompt: str, 
        seed: Optional[int] = None
    ) -> dict:
        """使用种子生成确定性输出
        
        Args:
            prompt: 输入提示词
            seed: 随机种子（None则自动生成）
        
        Returns:
            确定性输出
        """
        if seed is None:
            seed = int(time.time() * 1000)
        
        # 记录种子
        self._record_seed(seed, prompt)
        
        # 调用AI（传递seed参数）
        from ai_client import AIClient
        client = AIClient()
        output = client.generate(prompt, seed=seed)
        
        return {
            "output": output,
            "seed": seed,
            "timestamp": datetime.now().isoformat(),
            "reproducible": True
        }
    
    def verify_reproducibility(
        self, 
        prompt: str, 
        seed: int,
        iterations: int = 3
    ) -> dict:
        """验证可复现性
        
        Args:
            prompt: 输入提示词
            seed: 随机种子
            iterations: 验证次数
        
        Returns:
            验证结果
        """
        outputs = []
        for _ in range(iterations):
            result = self.generate_with_seed(prompt, seed)
            outputs.append(result["output"])
        
        # 检查所有输出是否相同
        is_reproducible = all(o == outputs[0] for o in outputs)
        
        return {
            "is_reproducible": is_reproducible,
            "seed": seed,
            "iterations": iterations,
            "first_output": outputs[0][:100] + "..." if outputs[0] else ""
        }
```

### 2.4 随机性监控模块（monitor.py）

**类设计**：
```python
class RandomnessMonitor:
    """随机性监控器"""
    
    def __init__(self, history_db: str = "history.db"):
        self.conn = sqlite3.connect(history_db)
    
    def analyze_trends(self, days: int = 7) -> dict:
        """分析随机性趋势
        
        Args:
            days: 分析天数
        
        Returns:
            趋势分析报告
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT prompt, output, timestamp 
            FROM history 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp
        """.format(days))
        
        records = cursor.fetchall()
        
        if len(records) < 2:
            return {"error": "数据不足，至少需要2条记录"}
        
        # 计算相似度趋势
        trends = []
        for i in range(0, len(records)-1, 2):
            if i+1 < len(records):
                sim = self._calculate_similarity(
                    records[i][1], 
                    records[i+1][1]
                )
                trends.append({
                    "date": records[i][2],
                    "similarity": sim
                })
        
        # 计算统计指标
        similarities = [t["similarity"] for t in trends]
        avg_sim = sum(similarities) / len(similarities)
        
        return {
            "period_days": days,
            "total_records": len(records),
            "average_similarity": round(avg_sim, 2),
            "trend": "稳定" if avg_sim > 70 else "波动",
            "details": trends
        }
    
    def detect_anomalies(self, threshold: float = 50.0) -> list:
        """检测异常输出
        
        Args:
            threshold: 异常阈值（相似度低于此值为异常）
        
        Returns:
            异常记录列表
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT prompt, output, timestamp 
            FROM history 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        
        records = cursor.fetchall()
        anomalies = []
        
        for i in range(len(records)-1):
            sim = self._calculate_similarity(
                records[i][1], 
                records[i+1][1]
            )
            if sim < threshold:
                anomalies.append({
                    "timestamp": records[i][2],
                    "prompt": records[i][0][:50] + "...",
                    "similarity": sim
                })
        
        return anomalies
    
    def export_report(self, output_path: str = "randomness_report.json") -> str:
        """导出监控报告
        
        Args:
            output_path: 输出路径
        
        Returns:
            报告文件路径
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "trends": self.analyze_trends(),
            "anomalies": self.detect_anomalies()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
```

---

## 3. 数据结构设计

### 3.1 配置文件（config.json）

```json
{
  "temperature": 0.5,
  "default_mode": "balance",
  "api_provider": "zhipu",
  "api_key": "<加密存储>",
  "history_db": "history.db",
  "seeds_file": "seeds.json"
}
```

### 3.2 历史数据库（history.db）

**表结构**：
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    output TEXT NOT NULL,
    temperature REAL,
    seed INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON history(timestamp);
CREATE INDEX idx_seed ON history(seed);
```

### 3.3 种子记录（seeds.json）

```json
{
  "records": [
    {
      "seed": 1710123456789,
      "prompt": "生成一个Python函数",
      "timestamp": "2026-03-13T07:45:00",
      "output_hash": "abc123..."
    }
  ]
}
```

---

## 4. CLI 命令设计

### 4.1 命令列表

```bash
# 1. 温度设置
deterministic temp <value>              # 设置温度（0.0-2.0）
deterministic temp --preset <name>      # 使用预设（code/balance/creative/brainstorm）

# 2. 一致性检查
deterministic check <prompt>            # 检查一致性（默认3次采样）
deterministic check <prompt> --samples 5  # 自定义采样次数

# 3. 可复现性
deterministic repro <prompt>            # 使用种子生成
deterministic repro <prompt> --seed 123  # 指定种子
deterministic repro --verify <seed>     # 验证复现性

# 4. 随机性监控
deterministic monitor trends            # 趋势分析
deterministic monitor anomalies         # 异常检测
deterministic monitor report            # 导出报告
```

### 4.2 主程序（deterministic.py）

```python
#!/usr/bin/env python3
import click
from temperature import TemperatureController
from consistency import ConsistencyChecker
from reproducibility import ReproducibilityGuarantor
from monitor import RandomnessMonitor

@click.group()
def cli():
    """AI 确定性控制工具"""
    pass

@cli.command()
@click.argument('value', type=float, required=False)
@click.option('--preset', type=click.Choice(['code', 'balance', 'creative', 'brainstorm']))
def temp(value, preset):
    """温度参数设置"""
    controller = TemperatureController()
    
    if preset:
        config = controller.get_preset(preset)
        value = config["temperature"]
        click.echo(f"使用预设 {preset}: {config['description']}")
    
    if value is not None:
        result = controller.set_temperature(value)
        click.echo(f"✅ 温度已设置为: {result['temperature']}")
        click.echo(f"   模式: {result['mode']}")
    else:
        click.echo(f"当前温度: {controller.config.get('temperature', 0.5)}")

@cli.command()
@click.argument('prompt')
@click.option('--samples', default=3, help='采样次数')
@click.option('--threshold', default=80.0, help='一致性阈值')
def check(prompt, samples, threshold):
    """一致性检查"""
    checker = ConsistencyChecker()
    result = checker.check_consistency(prompt, samples, threshold)
    
    click.echo(f"一致性评分: {result['consistency_score']}%")
    click.echo(f"通过: {'✅' if result['passed'] else '❌'}")
    click.echo(f"采样次数: {result['samples']}")
    click.echo(f"详情: 最小={result['details']['min']}%, 最大={result['details']['max']}%")

@cli.command()
@click.argument('prompt', required=False)
@click.option('--seed', type=int, help='随机种子')
@click.option('--verify', type=int, help='验证复现性的种子')
def repro(prompt, seed, verify):
    """可复现性保证"""
    guarantor = ReproducibilityGuarantor()
    
    if verify:
        if not prompt:
            click.echo("❌ 验证复现性需要提供prompt")
            return
        result = guarantor.verify_reproducibility(prompt, verify)
        click.echo(f"可复现: {'✅' if result['is_reproducible'] else '❌'}")
        click.echo(f"种子: {result['seed']}")
    elif prompt:
        result = guarantor.generate_with_seed(prompt, seed)
        click.echo(f"输出: {result['output'][:100]}...")
        click.echo(f"种子: {result['seed']}")
        click.echo(f"可复现: {'✅' if result['reproducible'] else '❌'}")
    else:
        click.echo("❌ 请提供prompt或使用--verify")

@cli.group()
def monitor():
    """随机性监控"""
    pass

@monitor.command()
@click.option('--days', default=7, help='分析天数')
def trends(days):
    """趋势分析"""
    mon = RandomnessMonitor()
    result = mon.analyze_trends(days)
    
    click.echo(f"分析周期: {result['period_days']} 天")
    click.echo(f"记录数: {result['total_records']}")
    click.echo(f"平均相似度: {result['average_similarity']}%")
    click.echo(f"趋势: {result['trend']}")

@monitor.command()
@click.option('--threshold', default=50.0, help='异常阈值')
def anomalies(threshold):
    """异常检测"""
    mon = RandomnessMonitor()
    result = mon.detect_anomalies(threshold)
    
    if result:
        click.echo(f"发现 {len(result)} 个异常:")
        for anomaly in result:
            click.echo(f"  - {anomaly['timestamp']}: 相似度 {anomaly['similarity']}%")
    else:
        click.echo("✅ 未发现异常")

@monitor.command()
@click.option('--output', default='randomness_report.json', help='输出路径')
def report(output):
    """导出报告"""
    mon = RandomnessMonitor()
    path = mon.export_report(output)
    click.echo(f"✅ 报告已导出: {path}")

if __name__ == '__main__':
    cli()
```

---

## 5. 测试策略

### 5.1 单元测试（test/test_all.py）

**测试覆盖率目标**：> 85%

**测试用例**：
1. **温度控制**（5个）
   - test_set_temperature_valid
   - test_set_temperature_invalid
   - test_get_preset
   - test_get_mode
   - test_persistence

2. **一致性检查**（4个）
   - test_check_consistency_pass
   - test_check_consistency_fail
   - test_calculate_similarity
   - test_save_history

3. **复现保证**（4个）
   - test_generate_with_seed
   - test_verify_reproducibility_success
   - test_verify_reproducibility_fail
   - test_seed_recording

4. **随机性监控**（4个）
   - test_analyze_trends
   - test_detect_anomalies
   - test_export_report
   - test_insufficient_data

**总计**：17个测试用例

### 5.2 集成测试

**测试场景**：
1. 完整工作流：设置温度 → 检查一致性 → 验证复现性 → 监控报告
2. 并发测试：多个一致性检查同时运行
3. 性能测试：参数设置 < 100ms，一致性检查 < 1秒

---

## 6. 部署方案

### 6.1 目录结构

```
skills/ai-deterministic-control/
├── deterministic.py           # CLI入口
├── temperature.py             # 温度控制
├── consistency.py             # 一致性检查
├── reproducibility.py         # 复现保证
├── monitor.py                 # 随机性监控
├── ai_client.py               # AI客户端
├── config.py                  # 配置管理
├── SKILL.md                   # 技能说明
├── README.md                  # 使用文档
├── package.json               # 包信息
├── test/
│   └── test_all.py            # 测试用例
└── docs/
    └── usage.md               # 详细文档
```

### 6.2 依赖管理

**requirements.txt**：
```
click>=8.0.0
sqlite3  # 内置
requests>=2.28.0
```

---

## 7. 性能优化

### 7.1 缓存机制
- 相同prompt的输出缓存（5分钟TTL）
- 预设配置内存缓存

### 7.2 并发处理
- 一致性检查使用多线程并发调用AI
- 历史记录异步写入

### 7.3 数据库优化
- 历史记录批量插入
- 定期清理旧数据（保留30天）

---

## 8. 风险应对

### 8.1 API限流
- **措施**：请求队列 + 指数退避重试
- **代码**：
```python
def _call_ai_with_retry(self, prompt, max_retries=3):
    for i in range(max_retries):
        try:
            return self.client.generate(prompt)
        except RateLimitError:
            time.sleep(2 ** i)  # 指数退避
    raise Exception("API限流，请稍后再试")
```

### 8.2 一致性问题
- **措施**：多次采样 + 投票机制
- **代码**：
```python
def _vote_output(self, outputs):
    """投票选择最一致的输出"""
    from collections import Counter
    counter = Counter(outputs)
    return counter.most_common(1)[0][0]
```

### 8.3 复现性差
- **措施**：种子记录 + 参数固化
- **代码**：
```python
def _freeze_params(self, params):
    """固化所有参数"""
    return {
        "temperature": params.get("temperature", 0.5),
        "seed": params.get("seed"),
        "top_p": params.get("top_p", 1.0)
    }
```

---

## 9. 时间计划

| 任务 | 预计时间 | 完成标志 |
|------|---------|---------|
| 技术设计 | 1小时 | 本文档 |
| 环境搭建 | 30分钟 | 目录结构+依赖安装 |
| 核心模块开发 | 4小时 | 4个核心模块 |
| CLI开发 | 2小时 | 命令行接口 |
| 测试编写 | 2小时 | 17个测试用例 |
| 文档编写 | 1小时 | SKILL.md+README.md |
| **总计** | **10.5小时** | **完整可用版本** |

---

## 10. 验收清单

- [ ] 4个核心功能全部实现
- [ ] 测试覆盖率 > 85%
- [ ] 所有测试通过
- [ ] 性能达标（参数设置<100ms，一致性检查<1秒）
- [ ] 文档完整（SKILL.md + README.md）
- [ ] Git提交并推送
- [ ] Issue评论通知米粒儿

---

*创建时间：2026-03-13 07:45*
*创建者：小米粒（开发代理）*
*状态：技术设计完成，待开发实现*
