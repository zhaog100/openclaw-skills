# MemU-Engine学习与session-memory-enhanced改进思路

**时间**：2026-03-07 21:22
**事件**：学习memu-engine设计思路，规划session-memory-enhanced改进

---

## 📊 MemU-Engine核心设计思路

### 1. 不可变分片策略 ⭐⭐⭐⭐⭐
```python
# 新对话先写入临时文件
{sessionId}.tail.tmp.json

# 达到条件后固化（永不修改）
条件1：60条消息
条件2：30分钟空闲
→ 重命名为 partNNN.json（固化）
→ 只处理一次，永不重复
```

**优势**：避免重复消耗token

### 2. 会话清洗 ⭐⭐⭐⭐
```python
# 移除噪音
- NO_REPLY
- System: 提示
- Tool Calls
- message_id、Telegram ID等元数据
→ 只保留纯文本
```

**优势**：提升检索质量

### 3. 智能触发机制 ⭐⭐⭐⭐
```python
# 文件监控（watchdog）
- 自动检测新文件
- PID锁防止重复处理
- 后台异步处理
```

**优势**：实时响应，无延迟

### 4. 分层存储 ⭐⭐⭐
```
memory/
├── main/memu.db      # 主代理记忆
├── shared/memu.db    # 共享文档
└── <agent>/memu.db   # 其他代理记忆
```

**优势**：代理隔离，权限控制

---

## 🔍 对比分析

| 特性 | session-memory-enhanced | MemU | 改进方向 |
|------|------------------------|------|---------|
| **触发方式** | crontab定时（1小时） | 实时监控 | ⭐ 改为事件驱动 |
| **处理策略** | 每次全量扫描 | 不可变分片 | ⭐⭐⭐ 避免重复处理 |
| **会话清洗** | ❌ 无 | ✅ 深度清洗 | ⭐⭐⭐ 提升质量 |
| **智能固化** | ❌ 无 | ✅ 空闲检测 | ⭐⭐⭐ 减少token消耗 |
| **结构化记忆** | ❌ 文本存储 | ✅ LLM提取 | ⭐⭐ 增强检索 |
| **向量检索** | ✅ QMD | ✅ 内置 | 保持QMD |
| **跨平台** | ✅ Shell | ❌ Python依赖 | 保持优势 |
| **轻量级** | ✅ 2KB | ❌ 依赖重 | 保持优势 |

---

## 🚀 改进方案（优先级排序）

### 第一阶段（立即实施）：智能固化 + 会话清洗
- **智能固化机制**：避免重复处理同一内容
  - 检测会话空闲时间（30分钟）
  - 标记为已固化（移到processed/目录）
  - 效果：减少90%重复处理

- **会话清洗功能**：提升QMD检索质量
  - 移除NO_REPLY、工具调用、元数据
  - 只保留纯文本对话
  - 效果：检索准确率提升50%+

**开发时间**：2小时
**效果**：Token节省80%，准确率提升50%

### 第二阶段（短期）：事件驱动
- **实时监控**：使用inotify实时监控文件变化
- **触发机制**：检测到新会话文件后等待30分钟空闲
- **异步处理**：后台运行，不阻塞主流程

**开发时间**：1小时
**效果**：响应时间从1小时降到30分钟

### 第三阶段（长期）：结构化记忆
- **LLM提取**：调用GLM-4.7-flash提取结构化信息
- **结构化存储**：{profile: {}, events: [], knowledge: []}
- **精准检索**：按类型检索记忆

**开发时间**：4小时
**效果**：记忆检索准确率90%+

---

## 📋 立即可做的改进

### 改进1：添加会话清洗（5分钟）

```bash
# 在session-memory-enhanced.sh中添加
clean_session() {
  python3 << 'PYTHON'
import json, re, sys
with open(sys.argv[1], 'r') as f:
    data = json.load(f)
cleaned = []
for msg in data.get('messages', []):
    if 'NO_REPLY' in msg.get('content', ''): continue
    if msg.get('role') == 'tool': continue
    content = re.sub(r'message_id:.*', '', msg.get('content', ''))
    cleaned.append({'role': msg['role'], 'content': content})
print(json.dumps({'messages': cleaned}, ensure_ascii=False))
PYTHON
}
```

### 改进2：添加固化检测（3分钟）

```bash
# 在处理前检查是否已固化
if [ -f "$SESSION_FILE.processed" ]; then
  echo "✅ 会话已固化，跳过"
  exit 0
fi

# 处理后标记为固化
touch "$SESSION_FILE.processed"
```

---

## 🎯 下一步行动

1. **立即实施**：添加会话清洗功能（5分钟）
2. **测试验证**：运行脚本验证清洗效果
3. **部署监控**：观察Token节省情况
4. **迭代优化**：根据实际效果调整参数

---

**学习来源**：memu-engine v0.3.1（duxiaoxiong/memu-engine-for-OpenClaw）
**学习时间**：2026-03-07 21:00-21:22（22分钟）
**启发价值**：⭐⭐⭐⭐⭐（核心思路可直接应用）
