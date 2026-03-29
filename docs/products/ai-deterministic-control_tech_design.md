# AI 确定性控制工具（ai-deterministic-control）技术设计文档 v1.0

| 项目 | 信息 |
|------|------|
| 产品名 | ai-deterministic-control |
| 版本 | v1.0 |
| 作者 | 思捷娅科技 (SJYKJ) |
| 日期 | 2026-03-16 |
| 技术栈 | Python 3.8+ / Bash |
| 技能目录 | `/root/.openclaw/workspace/skills/ai-deterministic-control/` |

---

## 目录

1. [架构设计](#1-架构设计)
2. [模块详细设计](#2-模块详细设计)
3. [接口设计](#3-接口设计)
4. [数据结构](#4-数据结构)
5. [一致性算法](#5-一致性算法)
6. [场景预设配置](#6-场景预设配置)
7. [与 smart-model-switch 联动方案](#7-与-smart-model-switch-联动方案)
8. [错误处理](#8-错误处理)
9. [测试方案](#9-测试方案)
10. [版权声明](#10-版权声明)

---

## 1. 架构设计

### 1.1 模块划分

```
┌─────────────────────────────────────────────────┐
│                    CLI 层                        │
│  detcontrol set / check / report / preset / monitor │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│              ConfigManager                       │
│  temperature / topP / seed / presets 管理        │
└──────┬───────────┬──────────────┬───────────────┘
       │           │              │
┌──────▼──────┐ ┌──▼──────────┐ ┌▼──────────────┐
│SeedManager  │ │MonitorEngine│ │ModelBridge    │
│种子管理      │ │监控+趋势     │ │openclaw.json  │
│生成/存储/复现│ │异常检测/报告  │ │参数注入       │
└─────────────┘ └──────┬──────┘ └──────────────┘
                      │
             ┌────────▼──────────┐
             │ConsistencyChecker │
             │ 编辑距离+语义相似  │
             │ 多次采样+阈值告警  │
             └───────────────────┘
```

### 1.2 数据流图

```
用户输入 ──► CLI ──► ConfigManager ──► ModelBridge ──► openclaw.json
                │
                ├──► SeedManager ──► seed 存储文件
                │
                ├──► ConsistencyChecker
                │      │
                │      ├── 多次采样（n 次）
                │      ├── 编辑距离计算
                │      ├── TF-IDF 语义相似度
                │      └── 综合评分 + 阈值告警
                │
                └──► MonitorEngine
                       ├── 历史数据读取
                       ├── 趋势分析（滑动窗口）
                       ├── 异常检测（Z-score）
                       └── 报告生成（Markdown/JSON）
```

### 1.3 文件结构

```
skills/ai-deterministic-control/
├── SKILL.md                    # 技能描述
├── detcontrol                  # CLI 入口（Bash）
├── src/
│   ├── __init__.py
│   ├── config_manager.py       # ConfigManager
│   ├── consistency_checker.py  # ConsistencyChecker
│   ├── seed_manager.py         # SeedManager
│   ├── monitor_engine.py       # MonitorEngine
│   ├── model_bridge.py         # ModelBridge
│   └── algorithms.py           # 一致性算法（编辑距离、TF-IDF）
├── presets/
│   └── default.json            # 场景预设配置
├── data/
│   ├── seeds.json              # 种子存储
│   └── monitor_history.json    # 监控历史数据
└── tests/
    ├── test_config_manager.py
    ├── test_consistency_checker.py
    ├── test_seed_manager.py
    ├── test_monitor_engine.py
    └── test_algorithms.py
```

---

## 2. 模块详细设计

### 2.1 ConfigManager — 参数管理

**职责**：管理 temperature、topP、seed 参数及场景预设。

**核心逻辑**：

```python
class ConfigManager:
    """确定性控制参数管理器"""
    
    PRESETS_FILE = "presets/default.json"
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or self._default_dir()
        self.config_path = os.path.join(self.config_dir, "detcontrol_config.json")
        self.presets = self._load_presets()
        self.config = self._load_config()
    
    def set_temperature(self, value: float) -> Dict:
        """设置温度参数，范围 [0.0, 2.0]"""
        
    def set_top_p(self, value: float) -> Dict:
        """设置 top_p 参数，范围 [0.0, 1.0]"""
    
    def set_seed(self, value: int) -> Dict:
        """设置随机种子"""
    
    def apply_preset(self, name: str) -> Dict:
        """应用场景预设"""
    
    def get_config(self) -> DeterministicConfig:
        """获取当前配置"""
    
    def _load_presets(self) -> Dict: ...
    def _load_config(self) -> Dict: ...
    def _save_config(self) -> None: ...
```

**配置文件格式**（`detcontrol_config.json`）：

```json
{
  "temperature": 0.3,
  "top_p": 0.9,
  "seed": 42,
  "active_preset": "code_generation",
  "last_modified": "2026-03-16T18:00:00+08:00"
}
```

### 2.2 ConsistencyChecker — 一致性检查

**职责**：多次采样输出，计算一致性评分，触发阈值告警。

**核心逻辑**：

```python
class ConsistencyChecker:
    """输出一致性检查器"""
    
    DEFAULT_SAMPLES = 5
    CHAR_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6
    
    def __init__(self, config: DeterministicConfig = None):
        self.config = config or DeterministicConfig()
        self.char_weight = self.DEFAULT_SAMPLES
        self.semantic_weight = self.DEFAULT_SAMPLES
    
    def check(self, prompt: str, sampler_fn: Callable[[str, Dict], str],
              n_samples: int = 5) -> ConsistencyReport:
        """
        一致性检查主流程：
        1. 用相同 prompt + 参数采样 n 次
        2. 两两计算字符相似度和语义相似度
        3. 加权平均得综合评分
        4. 与阈值对比，生成告警
        """
        samples = [sampler_fn(prompt, self.config.to_dict()) for _ in range(n_samples)]
        
        char_scores, sem_scores = [], []
        for i in range(len(samples)):
            for j in range(i + 1, len(samples)):
                cs = self._char_similarity(samples[i], samples[j])
                ss = self._semantic_similarity(samples[i], samples[j])
                char_scores.append(cs)
                sem_scores.append(ss)
        
        avg_char = sum(char_scores) / len(char_scores) if char_scores else 0
        avg_sem = sum(sem_scores) / len(sem_scores) if sem_scores else 0
        composite = self.CHAR_WEIGHT * avg_char + self.SEMANTIC_WEIGHT * avg_sem
        
        alert = self._check_threshold(composite)
        return ConsistencyReport(
            samples=samples, char_similarity=avg_char,
            semantic_similarity=avg_sem, composite_score=composite,
            alert=alert
        )
    
    def _char_similarity(self, a: str, b: str) -> float:
        """Levenshtein 编辑距离转相似度 [0, 1]"""
        from .algorithms import levenshtein_similarity
        return levenshtein_similarity(a, b)
    
    def _semantic_similarity(self, a: str, b: str) -> float:
        """TF-IDF 余弦相似度 [0, 1]"""
        from .algorithms import tfidf_cosine_similarity
        return tfidf_cosine_similarity(a, b)
    
    def _check_threshold(self, score: float) -> Optional[Alert]:
        """阈值告警：score < 0.8 → WARN, < 0.6 → CRITICAL"""
    
    @staticmethod
    def default_sampler(prompt: str, config: Dict) -> str:
        """
        默认采样函数：基于 openclaw API 进行实际 AI 调用。
        通过 openclaw message 命令或直接 HTTP 调用 API。
        
        降级策略：
        1. 优先使用 openclaw CLI（如果可用）
        2. 降级为 HTTP API 调用
        3. 最后降级为本地 mock（仅返回 prompt hash，用于测试）
        """
        import subprocess
        try:
            result = subprocess.run(
                ["openclaw", "message", "--model", config.get("model", "glm-5-turbo"),
                 "--temperature", str(config.get("temperature", 0.3)),
                 "--no-stream", prompt],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        # 降级：返回确定性 mock
        return f"[mock] {hash(prompt) % 10000}"
```

### 2.3 SeedManager — 种子管理

**职责**：生成、存储、复现随机种子，确保可复现性。

**核心逻辑**：

```python
class SeedManager:
    """随机种子管理器"""
    
    SEEDS_FILE = "data/seeds.json"
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or self._default_dir()
        self.seeds_path = os.path.join(self.data_dir, self.SEEDS_FILE)
        self.seeds = self._load_seeds()
    
    def generate(self, label: str = None) -> SeedRecord:
        """生成新种子，可选关联标签"""
        seed = random.randint(0, 2**32 - 1)
        record = SeedRecord(
            seed=seed, label=label or f"auto_{len(self.seeds) + 1}",
            created_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            prompt_hash=None
        )
        self.seeds[record.id] = record.to_dict()
        self._save_seeds()
        return record
    
    def get(self, seed_id: str) -> Optional[SeedRecord]:
        """按 ID 获取种子记录"""
    
    def lookup_by_label(self, label: str) -> Optional[SeedRecord]:
        """按标签查找"""
    
    def list_seeds(self, limit: int = 20) -> List[SeedRecord]:
        """列出最近种子"""
    
    def associate_prompt(self, seed_id: str, prompt: str) -> None:
        """关联 prompt（存储 hash）"""
    
    def reproduce(self, seed_id: str) -> Optional[int]:
        """获取种子值用于复现"""
```

### 2.4 MonitorEngine — 监控引擎

**职责**：趋势分析、异常检测、报告生成。

**核心逻辑**：

```python
class MonitorEngine:
    """随机性监控引擎"""
    
    HISTORY_FILE = "data/monitor_history.json"
    WINDOW_SIZE = 30          # 滑动窗口大小
    ZSCORE_THRESHOLD = 2.0    # 异常 Z-score 阈值
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or self._default_dir()
        self.history_path = os.path.join(self.data_dir, self.HISTORY_FILE)
        self.history = self._load_history()
    
    def record_check(self, report: ConsistencyReport, config: DeterministicConfig) -> None:
        """记录一次一致性检查结果"""
        entry = MonitorEntry(
            timestamp=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            temperature=config.temperature,
            top_p=config.top_p,
            seed=config.seed,
            composite_score=report.composite_score,
            char_similarity=report.char_similarity,
            semantic_similarity=report.semantic_similarity,
            num_samples=len(report.samples),
            alert_level=report.alert.level if report.alert else "ok"
        )
        self.history.append(entry.to_dict())
        self._save_history()
    
    def analyze_trend(self, days: int = 7) -> TrendAnalysis:
        """分析趋势：均值、标准差、方向"""
        recent = self._filter_recent(days)
        scores = [e["composite_score"] for e in recent]
        if not scores:
            return TrendAnalysis(status="no_data")
        
        mean = statistics.mean(scores)
        stdev = statistics.stdev(scores) if len(scores) > 1 else 0
        
        # 线性趋势方向
        direction = self._calc_direction(scores)
        return TrendAnalysis(
            status="stable" if stdev < 0.1 else "volatile",
            mean_score=mean, stdev=stdev, trend_direction=direction,
            data_points=len(scores)
        )
    
    def detect_anomalies(self) -> List[Anomaly]:
        """Z-score 异常检测"""
        scores = [e["composite_score"] for e in self.history]
        if len(scores) < 3:
            return []
        
        mean = statistics.mean(scores)
        stdev = statistics.stdev(scores)
        if stdev == 0:
            return []
        
        anomalies = []
        for i, entry in enumerate(self.history):
            z = abs((entry["composite_score"] - mean) / stdev)
            if z > self.ZSCORE_THRESHOLD:
                anomalies.append(Anomaly(
                    index=i, timestamp=entry["timestamp"],
                    score=entry["composite_score"], z_score=z,
                    severity="critical" if z > 3 else "warning"
                ))
        return anomalies
    
    def generate_report(self, format: str = "markdown", days: int = 7) -> str:
        """生成监控报告"""
        trend = self.analyze_trend(days)
        anomalies = self.detect_anomalies()
        # ... 格式化输出
```

### 2.5 ModelBridge — 模型桥接

**职责**：读取 `openclaw.json`，注入确定性参数。

**核心逻辑**：

```python
class ModelBridge:
    """OpenClaw 模型参数桥接"""
    
    OPENCLAW_CONFIG = "~/.openclaw/openclaw.json"
    
    def __init__(self):
        self.config_path = Path(self.OPENCLAW_CONFIG).expanduser()
    
    def inject_params(self, config: DeterministicConfig) -> Dict:
        """
        将确定性参数注入 openclaw.json 的模型配置。
        在模型配置的 parameters 字段中添加 temperature/top_p/seed。
        
        安全措施：
        1. 修改前自动备份 openclaw.json
        2. 验证 JSON 格式后再写入
        3. 写入失败时自动恢复备份
        """
        # 自动备份
        self._backup_config()
        data = self._read_config()
        try:
            for model_name in data.get("models", {}):
                model_cfg = data["models"][model_name]
                if "parameters" not in model_cfg:
                    model_cfg["parameters"] = {}
                model_cfg["parameters"]["temperature"] = config.temperature
                model_cfg["parameters"]["top_p"] = config.top_p
                if config.seed is not None:
                    model_cfg["parameters"]["seed"] = config.seed
            # 写入前验证 JSON 格式
            json.dumps(data, ensure_ascii=False)
            self._write_config(data)
        except (json.JSONDecodeError, Exception) as e:
            self._restore_config()
            raise RuntimeError(f"写入失败，已恢复备份: {e}")
        return data
    
    def inject_model_params(self, model_name: str, config: DeterministicConfig) -> Dict:
        """只注入指定模型的参数"""
        data = self._read_config()
        if model_name in data.get("models", {}):
            model_cfg = data["models"][model_name]
            if "parameters" not in model_cfg:
                model_cfg["parameters"] = {}
            model_cfg["parameters"]["temperature"] = config.temperature
            model_cfg["parameters"]["top_p"] = config.top_p
            if config.seed is not None:
                model_cfg["parameters"]["seed"] = config.seed
        self._write_config(data)
        return data
    
    def read_current(self) -> Dict:
        """读取当前模型配置"""
        return self._read_config()
    
    def reset_params(self, targets: List[str] = None) -> Dict:
        """
        恢复默认配置。
        targets: ["temperature", "seed"] 或 None（全部恢复）
        默认值：temperature=0.3, top_p=0.9, seed=None
        """
        defaults = {"temperature": 0.3, "top_p": 0.9, "seed": None}
        if targets is None:
            targets = list(defaults.keys())
        self._backup_config()
        data = self._read_config()
        try:
            for model_name in data.get("models", {}):
                if "parameters" in data["models"][model_name]:
                    for key in targets:
                        data["models"][model_name]["parameters"][key] = defaults[key]
            json.dumps(data, ensure_ascii=False)
            self._write_config(data)
        except Exception as e:
            self._restore_config()
            raise RuntimeError(f"重置失败，已恢复备份: {e}")
        return data
    
    def _backup_config(self) -> None: ...
    def _restore_config(self) -> None: ...
    
    def _read_config(self) -> Dict: ...
    def _write_config(self, data: Dict) -> None: ...
```

### 2.6 CLI — 命令行接口

**入口脚本**：`detcontrol`（Bash wrapper）

```bash
#!/usr/bin/env bash
# detcontrol - AI 确定性控制工具 CLI
source /root/.openclaw/workspace/skills/utils/error-handler.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

case "${1:-help}" in
  set)
    # detcontrol set --temperature 0.1 [--top-p 0.9] [--seed 42]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" set "${@:2}"
    ;;
  check)
    # detcontrol check --prompt "..." [--samples 5] [--threshold 0.8]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" check "${@:2}"
    ;;
  report)
    # detcontrol report [--format markdown|json] [--days 7]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" report "${@:2}"
    ;;
  preset)
    # detcontrol preset [list|apply|create] [name]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" preset "${@:2}"
    ;;
  monitor)
    # detcontrol monitor [status|trend|anomalies]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" monitor "${@:2}"
    ;;
  inject)
    # detcontrol inject [--model model_name]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" inject "${@:2}"
    ;;
  reset)
    # detcontrol reset [--all | --temperature | --seed]
    $PYTHON "$SCRIPT_DIR/src/__main__.py" reset "${@:2}"
    ;;
  help|--help|-h)
    # 显示帮助
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac
```

**命令汇总**：

| 命令 | 说明 | 性能目标 |
|------|------|----------|
| `detcontrol set --temp 0.1` | 设置温度 | < 100ms |
| `detcontrol set --top-p 0.9` | 设置 top_p | < 100ms |
| `detcontrol set --seed 42` | 设置种子 | < 100ms |
| `detcontrol preset apply code_generation` | 应用预设 | < 100ms |
| `detcontrol preset list` | 列出预设 | < 100ms |
| `detcontrol check --prompt "..." --samples 5` | 一致性检查 | < 1s |
| `detcontrol report --days 7` | 监控报告 | < 5s |
| `detcontrol monitor trend` | 趋势分析 | < 2s |
| `detcontrol inject --model glm-5` | 参数注入 | < 200ms |
| `detcontrol reset [--all | --temperature | --seed]` | 恢复默认配置 | < 100ms |

---

## 3. 接口设计

### 3.1 ConfigManager 接口

```
输入                          输出
──────────────────────────────────────────────
set_temperature(0.1)      →   {"status": "ok", "temperature": 0.1}
set_top_p(0.9)            →   {"status": "ok", "top_p": 0.9}
set_seed(42)              →   {"status": "ok", "seed": 42}
apply_preset("code_gen")  →   {"status": "ok", "preset": "code_generation", "config": {...}}
get_config()              →   DeterministicConfig dataclass
```

### 3.2 ConsistencyChecker 接口

```
输入                                            输出
──────────────────────────────────────────────────────────
check(prompt, sampler_fn, n=5)     →   ConsistencyReport
                                       ├── samples: List[str]
                                       ├── char_similarity: float
                                       ├── semantic_similarity: float
                                       ├── composite_score: float
                                       └── alert: Optional[Alert]
```

### 3.3 SeedManager 接口

```
输入                          输出
──────────────────────────────────────────────
generate("test_run")       →   SeedRecord {id, seed, label, created_at}
get("seed_001")            →   SeedRecord | None
lookup_by_label("test")    →   SeedRecord | None
list_seeds(20)             →   List[SeedRecord]
associate_prompt(id, prompt) → None
reproduce("seed_001")      →   int (seed value) | None
```

### 3.4 MonitorEngine 接口

```
输入                          输出
──────────────────────────────────────────────
record_check(report, config) →   None
analyze_trend(7)            →   TrendAnalysis {status, mean, stdev, direction}
detect_anomalies()          →   List[Anomaly]
generate_report("md", 7)    →   str (Markdown 报告)
```

### 3.5 ModelBridge 接口

```
输入                          输出
──────────────────────────────────────────────
inject_params(config)       →   Dict (更新后的 openclaw.json)
inject_model_params("glm-5", config) → Dict
read_current()              →   Dict (当前 openclaw.json)
reset_params(["temperature","seed"]) → Dict (恢复默认)
```

---

## 4. 数据结构

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

class AlertLevel(Enum):
    OK = "ok"
    WARN = "warning"
    CRITICAL = "critical"

class TrendDirection(Enum):
    STABLE = "stable"
    IMPROVING = "improving"
    DECLINING = "declining"
    VOLATILE = "volatile"

@dataclass
class DeterministicConfig:
    """确定性控制核心配置"""
    temperature: float = 0.3
    top_p: float = 0.9
    seed: Optional[int] = None
    active_preset: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = {"temperature": self.temperature, "top_p": self.top_p}
        if self.seed is not None:
            d["seed"] = self.seed
        return d

@dataclass
class Alert:
    """告警信息"""
    level: AlertLevel
    message: str
    threshold: float
    actual: float

@dataclass
class ConsistencyReport:
    """一致性检查报告"""
    samples: List[str]
    char_similarity: float
    semantic_similarity: float
    composite_score: float
    alert: Optional[Alert] = None

@dataclass
class SeedRecord:
    """种子记录"""
    id: str
    seed: int
    label: str
    created_at: str
    prompt_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = {"id": self.id, "seed": self.seed, "label": self.label, "created_at": self.created_at}
        if self.prompt_hash:
            d["prompt_hash"] = self.prompt_hash
        return d

@dataclass
class MonitorEntry:
    """监控数据条目"""
    timestamp: str
    temperature: float
    top_p: float
    seed: Optional[int]
    composite_score: float
    char_similarity: float
    semantic_similarity: float
    num_samples: int
    alert_level: str

@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    status: str           # "stable" | "volatile" | "no_data"
    mean_score: float = 0.0
    stdev: float = 0.0
    trend_direction: str = "stable"
    data_points: int = 0

@dataclass
class Anomaly:
    """异常记录"""
    index: int
    timestamp: str
    score: float
    z_score: float
    severity: str         # "warning" | "critical"
```

---

## 5. 一致性算法

### 5.1 字符级编辑距离（Levenshtein）

纯 Python 实现，无外部依赖：

```python
def levenshtein_distance(s1: str, s2: str) -> int:
    """计算两个字符串的 Levenshtein 编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]

def levenshtein_similarity(s1: str, s2: str) -> float:
    """将编辑距离转为相似度分数 [0.0, 1.0]"""
    if not s1 and not s2:
        return 1.0
    max_len = max(len(s1), len(s2))
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)
```

### 5.2 语义相似度（TF-IDF 余弦相似度）

纯本地实现，使用 Python 标准库 `math` + `collections`：

```python
import math
import re
from collections import Counter

def tokenize(text: str) -> List[str]:
    """分词：转小写 + 按非字母数字拆分"""
    return [w.lower() for w in re.findall(r'\b\w+\b', text)]

def tfidf_cosine_similarity(text_a: str, text_b: str) -> float:
    """
    TF-IDF 余弦相似度，纯本地实现。
    对两段文本分别计算 TF，合并语料计算 IDF，最后求余弦相似度。
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)
    
    if not tokens_a or not tokens_b:
        return 0.0
    
    corpus = [tokens_a, tokens_b]
    N = len(corpus)
    vocab = set(tokens_a) | set(tokens_b)
    
    # 计算 IDF
    idf = {}
    for term in vocab:
        df = sum(1 for doc in corpus if term in doc)
        idf[term] = math.log(N / df) + 1  # smoothed IDF
    
    # 计算 TF-IDF 向量
    def tfidf_vector(tokens):
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        vec = {}
        for term in set(tokens):
            vec[term] = (tf[term] / max_tf) * idf[term]
        return vec
    
    vec_a = tfidf_vector(tokens_a)
    vec_b = tfidf_vector(tokens_b)
    
    # 余弦相似度
    dot = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vocab)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot / (norm_a * norm_b)
```

### 5.3 综合评分公式

```
composite_score = 0.4 × char_similarity + 0.6 × semantic_similarity
```

| 场景 | composite_score | 告警级别 |
|------|----------------|----------|
| score ≥ 0.8 | 高一致性 | OK |
| 0.6 ≤ score < 0.8 | 中等一致性 | WARNING |
| score < 0.6 | 低一致性 | CRITICAL |

---

## 6. 场景预设配置

`presets/default.json`：

```json
{
  "version": "1.0",
  "presets": {
    "code_generation": {
      "name": "代码生成",
      "description": "最高确定性，适用于代码、SQL、正则等生成任务",
      "temperature": 0.1,
      "top_p": 0.85,
      "seed": null,
      "tags": ["code", "sql", "regex", "api"]
    },
    "config_generation": {
      "name": "配置生成",
      "description": "高确定性，适用于 JSON、YAML、配置文件生成",
      "temperature": 0.2,
      "top_p": 0.88,
      "seed": null,
      "tags": ["json", "yaml", "config", "dockerfile"]
    },
    "conversation": {
      "name": "常规对话",
      "description": "平衡模式，适用于日常对话和问答",
      "temperature": 0.5,
      "top_p": 0.9,
      "seed": null,
      "tags": ["chat", "qa", "dialogue"]
    },
    "creative_writing": {
      "name": "创意写作",
      "description": "高随机性，适用于创意写作、头脑风暴",
      "temperature": 0.8,
      "top_p": 0.95,
      "seed": null,
      "tags": ["creative", "writing", "brainstorm", "story"]
    },
    "data_analysis": {
      "name": "数据分析",
      "description": "高确定性，适用于数据分析、统计报告",
      "temperature": 0.15,
      "top_p": 0.87,
      "seed": null,
      "tags": ["analysis", "statistics", "data"]
    },
    "translation": {
      "name": "翻译任务",
      "description": "高确定性，确保翻译一致性",
      "temperature": 0.1,
      "top_p": 0.85,
      "seed": null,
      "tags": ["translation", "i18n", "localization"]
    }
  }
}
```

---

## 7. 与 smart-model-switch 联动方案

### 7.1 联动机制

通过 **文件信号** 与 `smart-model-switch` 技能协作，避免强耦合：

```
检测到高确定性任务
    │
    ▼
detcontrol 生成信号文件：
~/.openclaw/workspace/.detcontrol_signal.json
{
  "mode": "deterministic",
  "recommended_temperature": 0.1,
  "reason": "code_generation_preset",
  "timestamp": "2026-03-16T18:00:00+08:00"
}
    │
    ▼
smart-model-switch 读取信号文件
    │
    ▼
切换到高确定性模型配置（低温度 + 精确模型）
```

### 7.2 信号文件格式

```json
{
  "mode": "deterministic" | "normal" | "creative",
  "recommended_temperature": 0.1,
  "recommended_model": null,
  "reason": "string",
  "preset_name": "string | null",
  "timestamp": "ISO8601"
}
```

### 7.3 联动流程

1. **自动触发**：用户执行 `detcontrol preset apply code_generation` 时，自动生成信号文件
2. **手动触发**：`detcontrol set --temperature 0.1 --signal` 时附带 `--signal` 标志
3. **信号消费**：`smart-model-switch` 在每次模型选择前检查信号文件，存在则优先采纳
4. **信号清除**：用户执行 `detcontrol preset apply conversation` 或手动清除时删除信号
5. **信号过期**：超过 30 分钟的信号自动失效

---

## 8. 错误处理

### 8.1 集成 error-handler 库

所有模块在初始化时加载统一错误处理：

```bash
source /root/.openclaw/workspace/skills/utils/error-handler.sh
```

### 8.2 Python 端错误处理模式

```python
import sys
import json
import traceback

def safe_execute(func, context=""):
    """统一错误处理包装器"""
    try:
        return func()
    except FileNotFoundError as e:
        error_exit(f"[FILE_NOT_FOUND] {context}: {e}", "error")
    except json.JSONDecodeError as e:
        error_exit(f"[JSON_PARSE_ERROR] {context}: {e}", "error")
    except PermissionError as e:
        error_exit(f"[PERMISSION_DENIED] {context}: {e}", "error")
    except ValueError as e:
        error_exit(f"[INVALID_VALUE] {context}: {e}", "warning")
    except Exception as e:
        error_exit(f"[UNEXPECTED] {context}: {e}\n{traceback.format_exc()}", "error")

def error_exit(message, level="error"):
    """格式化错误输出，兼容 error-handler"""
    output = {"level": level, "message": message, "source": "ai-deterministic-control"}
    print(json.dumps(output, ensure_ascii=False), file=sys.stderr)
    sys.exit(1 if level == "error" else 0)
```

### 8.3 错误分类

| 错误类型 | 级别 | 处理 |
|----------|------|------|
| 参数越界（temperature > 2.0） | warning | 自动 clamp 到合法范围，提示用户 |
| 配置文件不存在 | info | 自动创建默认配置 |
| 配置文件 JSON 格式错误 | error | 报错并拒绝操作 |
| 采样函数超时 | warning | 跳过本次采样，降低 n_samples |
| 种子 ID 不存在 | warning | 提示可用的种子列表 |
| openclaw.json 不存在 | warning | 提示需要初始化 OpenClaw |

---

## 9. 测试方案

### 9.1 单元测试

```
tests/
├── test_config_manager.py      # ConfigManager 单元测试
├── test_consistency_checker.py # ConsistencyChecker 单元测试
├── test_seed_manager.py        # SeedManager 单元测试
├── test_monitor_engine.py      # MonitorEngine 单元测试
└── test_algorithms.py          # 算法单元测试
```

#### test_algorithms.py 关键用例

```python
# Levenshtein
assert levenshtein_distance("hello", "hello") == 0
assert levenshtein_distance("kitten", "sitting") == 3
assert levenshtein_similarity("abc", "abc") == 1.0
assert levenshtein_similarity("abc", "xyz") < 0.5

# TF-IDF 相似度
assert tfidf_cosine_similarity("same text", "same text") == 1.0
assert tfidf_cosine_similarity("python code", "java code") > 0.3
assert tfidf_cosine_similarity("", "hello") == 0.0

# 综合评分
assert composite_score(same_text, same_text) == 1.0
```

#### test_config_manager.py 关键用例

```python
# 参数范围验证
cm.set_temperature(3.0)  # 应 clamp 到 2.0，warning
cm.set_temperature(-0.1)  # 应 clamp 到 0.0
cm.set_top_p(1.5)  # 应 clamp 到 1.0

# 预设应用
cm.apply_preset("code_generation")
assert cm.get_config().temperature == 0.1
```

### 9.2 集成测试

```python
# 端到端：设置 → 注入 → 检查 → 监控
def test_full_workflow():
    cm = ConfigManager(tmp_dir)
    cm.apply_preset("code_generation")
    
    bridge = ModelBridge(tmp_config)
    bridge.inject_params(cm.get_config())
    assert bridge.read_current()["models"]["glm-5"]["parameters"]["temperature"] == 0.1
    
    checker = ConsistencyChecker(cm.get_config())
    report = checker.check("写一个排序函数", mock_sampler, n=3)
    assert report.composite_score > 0.5
    
    monitor = MonitorEngine(tmp_dir)
    monitor.record_check(report, cm.get_config())
    trend = monitor.analyze_trend()
    assert trend.status in ["stable", "volatile", "no_data"]
```

### 9.3 性能测试

```python
import time

def test_set_performance():
    cm = ConfigManager()
    start = time.time()
    for _ in range(100):
        cm.set_temperature(0.1)
    elapsed = time.time() - start
    assert elapsed < 10  # 100 次 < 10s → 平均 < 100ms

def test_check_performance():
    checker = ConsistencyChecker()
    start = time.time()
    checker.check("test prompt", fast_mock_sampler, n=5)
    elapsed = time.time() - start
    assert elapsed < 1.0  # < 1s
```

### 9.4 运行测试

```bash
cd skills/ai-deterministic-control
python -m pytest tests/ -v --tb=short
```

---

## 10. 版权声明

---

**AI 确定性控制工具（ai-deterministic-control）技术设计文档 v1.0**

Copyright © 2026 思捷娅科技 (SJYKJ). All rights reserved.

本技术设计文档及相关代码由思捷娅科技 (SJYKJ) 设计并开发。  
本作品采用 [MIT License](https://opensource.org/licenses/MIT) 许可协议。

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

*文档版本：v1.0*  
*创建日期：2026-03-16*  
*作者：思捷娅科技 (SJYKJ)*  
*许可协议：MIT License*
