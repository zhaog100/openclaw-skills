# smart-model v2.0 - 技术设计文档

**创建时间**：2026-03-12 14:58
**创建者**：小米粒
**Issue**：#5
**PRD来源**：Issue #4

---

## 📋 设计概述

本文档是 smart-model v2.0 的技术设计文档，基于 PRD（Issue #4）进行技术实现设计。

---

## 🎯 设计目标

**核心目标**：实现 AI 根据任务复杂度、文件类型、上下文使用量等因素，自动选择最优模型。

**技术目标**：
1. ✅ 文件类型检测准确率 > 95%
2. ✅ 复杂度分析准确率 > 90%
3. ✅ 上下文监控准确率 100%
4. ✅ 模型切换响应时间 < 50ms

---

## 🏗️ 技术架构设计

### 1️⃣ 文件类型检测模块

**模块名称**：`file_type_detector.sh`

**核心算法**：
```bash
# 文件扩展名映射
declare -A FILE_TYPE_MAP=(
    ["py"]="code"
    ["js"]="code"
    ["sh"]="code"
    ["ts"]="code"
    ["java"]="code"
    ["go"]="code"
    ["rs"]="code"
    ["md"]="document"
    ["txt"]="document"
    ["pdf"]="document"
    ["docx"]="document"
    ["xlsx"]="document"
    ["jpg"]="image"
    ["png"]="image"
    ["gif"]="image"
    ["webp"]="image"
)

# 检测逻辑
detect_file_type() {
    local file_path="$1"
    local ext="${file_path##*.}"
    echo "${FILE_TYPE_MAP[$ext]:-none}"
}
```

**输出**：
- code → Coding 模型
- document → 大上下文模型
- image → Vision 模型
- none → 根据复杂度判断

---

### 2️⃣ 多维度复杂度分析模块

**模块名称**：`complexity_analyzer.sh`

**评分维度**（4维度加权）：

| 维度 | 权重 | 评分规则 |
|------|------|---------|
| **长度** | 30% | <50字(1分) <200字(2分) <500字(3分) |
| **关键词** | 40% | 简单(0分) 中等(2分) 复杂(3分) |
| **代码** | 20% | 无代码(0分) 少量(2分) 大量(3分) |
| **视觉** | 10% | 无视觉(0分) 有视觉(3分) |

**核心算法**：
```bash
calculate_complexity() {
    local message="$1"
    
    # 长度评分（30%）
    local length_score=0
    local len=${#message}
    if [ $len -lt 50 ]; then
        length_score=1
    elif [ $len -lt 200 ]; then
        length_score=2
    else
        length_score=3
    fi
    
    # 关键词评分（40%）
    local keyword_score=0
    # ... 关键词检测逻辑
    
    # 代码检测（20%）
    local code_score=0
    # ... 代码检测逻辑
    
    # 视觉检测（10%）
    local visual_score=0
    # ... 视觉检测逻辑
    
    # 加权总分
    local total=$(( (length_score * 30 + keyword_score * 40 + code_score * 20 + visual_score * 10) / 100 ))
    echo $total
}
```

**模型映射**：
```bash
map_to_model() {
    local score="$1"
    if [ $score -le 3 ]; then
        echo "flash"
    elif [ $score -le 6 ]; then
        echo "main"
    elif [ $score -le 8 ]; then
        echo "complex"
    else
        echo "complex-deep"
    fi
}
```

---

### 3️⃣ 上下文监控模块

**模块名称**：`context_monitor.sh`

**监控策略**（双策略系统）：

| 上下文占用率 | 策略 | 动作 |
|------------|------|------|
| <60% | 绿色 | 当前模型继续 ✅ |
| 60-85% | 黄色 | 准备切换，提醒用户 ⚠️ |
| >85% | 红色 | 强制切换 + 大上下文模型 🚨 |

**防频繁切换机制**：
```bash
# 冷却期：10分钟
COOLDOWN_PERIOD=600

# 连续性要求：2次
CONTINUITY_THRESHOLD=2

# 通知间隔：5分钟
NOTIFICATION_INTERVAL=300

# 检查冷却期
check_cooldown() {
    local last_switch="$1"
    local current_time=$(date +%s)
    
    if [ $((current_time - last_switch)) -lt $COOLDOWN_PERIOD ]; then
        return 1  # 在冷却期内
    fi
    return 0
}
```

---

### 4️⃣ AI主动检测模块

**模块名称**：`ai_detector.sh`

**触发时机**：AI回复前的钩子（hook）

**执行流程**：
```bash
ai_active_detection() {
    # 1. 检查上下文使用率
    local context_usage=$(get_context_usage)
    
    # 2. 分析消息复杂度
    local complexity=$(calculate_complexity "$USER_MESSAGE")
    
    # 3. 判断是否需要切换模型
    local need_switch=false
    if [ $context_usage -gt 85 ] || [ $complexity -gt 8 ]; then
        need_switch=true
    fi
    
    # 4. 输出决策（静默或提醒）
    if [ "$need_switch" = true ]; then
        echo "建议切换模型：当前上下文${context_usage}%，复杂度${complexity}分"
    fi
}
```

**静默模式**：
- 无问题时不输出
- 有问题时输出建议

---

### 5️⃣ 自动切换执行模块

**模块名称**：`model_switcher.sh`

**执行模式**：

| 模式 | 说明 | 优先级 |
|------|------|--------|
| **本地模式** | 修改 agents.json | 高 |
| **远程模式** | 发送系统事件到 Gateway | 中 |
| **混合模式** | 优先本地，失败时远程 | 默认 |

**切换逻辑**：
```bash
switch_model() {
    local target_model="$1"
    local mode="${2:-hybrid}"
    
    case $mode in
        local)
            update_agents_json "$target_model"
            ;;
        remote)
            send_gateway_event "$target_model"
            ;;
        hybrid)
            if update_agents_json "$target_model"; then
                log_success "本地切换成功"
            else
                send_gateway_event "$target_model"
            fi
            ;;
    esac
}
```

---

## 📁 文件结构

```
skills/smart-model/
├── SKILL.md
├── README.md
├── package.json
├── smart-model.sh              # 主脚本
├── install.sh
├── test/
│   └── test.sh
├── modules/
│   ├── file_type_detector.sh   # 文件类型检测
│   ├── complexity_analyzer.sh  # 复杂度分析
│   ├── context_monitor.sh      # 上下文监控
│   ├── ai_detector.sh          # AI主动检测
│   └── model_switcher.sh       # 模型切换
└── config/
    ├── agents.json             # 模型配置
    └── keywords.txt            # 关键词库
```

---

## 🧪 测试计划

### 单元测试
- [ ] 文件类型检测测试（20+种文件）
- [ ] 复杂度分析测试（各种场景）
- [ ] 上下文监控测试（3种策略）
- [ ] 模型切换测试（3种模式）

### 集成测试
- [ ] 端到端流程测试
- [ ] 性能测试（<50ms）
- [ ] 准确率测试（>90%）

### 压力测试
- [ ] 高频切换测试
- [ ] 并发测试
- [ ] 长时间运行测试

---

## 📊 性能指标

| 指标 | 目标 | 验收标准 |
|------|------|---------|
| **文件检测时间** | <10ms | ✅ 必须 |
| **复杂度分析时间** | <50ms | ✅ 必须 |
| **模型切换时间** | <1s | ✅ 必须 |
| **准确率** | >90% | ✅ 必须 |
| **可用性** | >99% | ✅ 必须 |

---

## 🔧 依赖清单

**核心依赖**：
- session-memory-enhanced v4.0.0
- context-manager v2.2.2
- smart-memory-sync v1.0.0
- smart-model-switch v1.3.0（参考实现）

**工具依赖**：
- jq（JSON处理）
- curl（HTTP请求）
- bc（数学计算）

---

## 📅 开发计划

### Phase 1 (MVP) - 2026-03-15
- [ ] 文件类型检测模块
- [ ] 复杂度分析模块
- [ ] 上下文监控模块
- [ ] AI主动检测模块

### Phase 2 - 2026-03-17
- [ ] 模型切换模块
- [ ] 成本优化建议
- [ ] 性能统计报表
- [ ] 完整测试

### Phase 3 - 2026-03-18
- [ ] 文档完善
- [ ] ClawHub 发布
- [ ] 用户反馈收集

---

## ✅ 验收标准

### 功能验收
- [ ] 所有5个核心模块按设计实现
- [ ] 2个辅助功能按设计实现
- [ ] 测试覆盖率 > 85%
- [ ] 所有测试通过

### 性能验收
- [ ] 分析时间 < 50ms
- [ ] 切换时间 < 1s
- [ ] 准确率 > 90%
- [ ] 可用性 > 99%

---

## 🎯 下一步

**等待米粒儿Review**：
1. ⏳ 技术架构确认
2. ⏳ 模块设计确认
3. ⏳ 性能指标确认
4. ⏳ 开发计划确认

**米粒儿确认后**：
- ⏳ 开始开发实现
- ⏳ 创建模块脚本
- ⏳ 编写测试用例

---

*创建时间：2026-03-12 14:58*
*创建者：小米粒*
*状态：待Review*
