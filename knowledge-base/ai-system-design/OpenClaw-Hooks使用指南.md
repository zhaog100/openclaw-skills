# OpenClaw Hooks使用指南

_三个已启用的核心Hooks详解_

---

## 一、session-memory（会话记忆）

### 核心功能
**让AI越用越聪明！** 每次新对话都能保留历史上下文，实现真正的长期记忆。

### 工作原理
1. **自动保存**：每次对话结束时，自动保存上下文到 `memory/sessions/` 目录
2. **智能加载**：新对话开始时，自动加载相关历史会话
3. **语义检索**：根据对话内容智能检索最相关的历史记忆
4. **自动清理**：定期清理过期记忆（默认保留365天）

### 使用方式

**手动触发**（管理员）：
```bash
# 在对话中使用 /new 命令
/new 今天我们来聊聊项目管理
```

**自动触发**（AI自动）：
- AI会在需要时自动加载相关历史会话
- 用户无需手动操作

### 配置文件
位置：`~/.openclaw/openclaw.json`

```json
{
  "hooks": {
    "session-memory": {
      "enabled": true,
      "storage": {
        "type": "file",
        "path": "memory/sessions/",
        "format": "json"
      },
      "memory": {
        "maxSessions": 100,
        "retentionDays": 365,
        "compressOld": true
      },
      "context": {
        "maxMessages": 50,
        "includeTools": false,
        "includeFiles": true
      }
    }
  }
}
```

### 存储位置
- **会话文件**：`C:\Users\zhaog\.openclaw\workspace\memory\sessions\`
- **格式**：JSON文件（每个会话一个文件）
- **命名**：`session-{timestamp}-{id}.json`

### 最佳实践

1. **信任AI的记忆**
   - 不需要重复告诉AI你的偏好
   - AI会记住你的工作习惯
   - 跨会话保持一致性

2. **重要信息会保留**
   - 重要的决策
   - 你的偏好和习惯
   - 项目相关信息

3. **隐私保护**
   - 敏感信息不要在对话中提及
   - 如需清除记忆，可以手动删除会话文件

### 验证方法

**测试1：跨会话记忆**
```
会话1：官家，我喜欢简洁的回复风格
会话2（新会话）：还记得我的回复风格偏好吗？
AI应答：记得，你喜欢简洁的回复风格
```

**测试2：项目信息保留**
```
会话1：官家，我正在做PMP认证准备
会话2（几天后）：PMP准备得怎么样了？
AI应答：（自动关联到之前的PMP讨论）
```

---

## 二、command-logger（命令审计）

### 核心功能
**所有交互可追溯！** 记录所有用户命令和AI响应，便于审计和回溯。

### 工作原理
1. **实时记录**：每次用户输入都自动记录
2. **完整信息**：包含时间戳、用户ID、会话ID、命令内容、响应结果
3. **日志轮转**：每天一个日志文件，自动压缩旧日志
4. **JSON格式**：便于解析和分析

### 使用方式

**自动运行**：无需手动操作，所有交互自动记录

### 配置文件
位置：`~/.openclaw/openclaw.json`

```json
{
  "hooks": {
    "command-logger": {
      "enabled": true,
      "output": {
        "file": "logs/commands.log",
        "format": "json",
        "rotate": "daily"
      },
      "include": {
        "timestamp": true,
        "userId": true,
        "sessionId": true,
        "command": true,
        "result": true,
        "duration": true
      }
    }
  }
}
```

### 日志位置
- **日志文件**：`C:\Users\zhaog\.openclaw\logs\commands.log`
- **格式**：每行一个JSON对象
- **轮转**：每天一个文件（commands-2026-02-27.log）

### 日志格式示例
```json
{
  "timestamp": "2026-02-27T13:15:00Z",
  "userId": "user123",
  "sessionId": "session456",
  "command": "学习这篇文章",
  "result": "已学习并集成OpenClaw扩展能力",
  "duration": "5.2s",
  "metadata": {
    "channel": "qqbot",
    "model": "aihubmix/gpt-4.1-free"
  }
}
```

### 使用场景

1. **回溯历史**
   - 找回之前讨论的内容
   - 追踪问题根源

2. **性能分析**
   - 统计命令执行时间
   - 识别慢查询

3. **安全审计**
   - 记录所有操作
   - 追踪异常行为

### 查看日志

**方法1：直接查看文件**
```bash
# 查看今天的日志
cat ~/.openclaw/logs/commands.log

# 查看特定日期
cat ~/.openclaw/logs/commands-2026-02-27.log
```

**方法2：使用jq工具**
```bash
# 统计今天的命令数
cat ~/.openclaw/logs/commands.log | jq -s 'length'

# 查找包含"学习"的命令
cat ~/.openclaw/logs/commands.log | jq 'select(.command | contains("学习"))'
```

---

## 三、boot-md（启动脚本）

### 核心功能
**启动自动运行！** OpenClaw启动时自动执行BOOT.md中定义的任务。

### 工作原理
1. **自动检测**：OpenClaw启动时自动查找 `BOOT.md`
2. **执行任务**：读取BOOT.md内容并执行
3. **问候用户**：根据时间段显示不同的问候语
4. **系统检查**：自动检查系统状态

### 使用方式

**自动运行**：OpenClaw启动时自动执行，无需手动操作

### BOOT.md位置
文件：`C:\Users\zhaog\.openclaw\workspace\BOOT.md`

### 当前配置（已创建）

```markdown
# OpenClaw 启动脚本

_官家，我又醒了！今天能为您做些什么？_

---

## 系统状态检查

### 1. QMD知识库状态
- 命令：qmd status
- 预期：22个文件已索引

### 2. AIHubMix连接验证
- 主力模型：aihubmix/gpt-4.1-free
- 备用模型：zai/glm-5

### 3. 记忆系统检查
- MEMORY.md：长期记忆
- daily log：今日日志
- session-memory：会话记忆

---

## 问候与提醒

### 早晨（6:00-12:00）
官家，早安！🌾

### 下午（12:00-18:00）
官家，下午好！🌾

### 晚上（18:00-24:00）
官家，晚上好！🌾

---

## 技能状态

**已启用技能（6个）**：
- qqbot-cron、qqbot-media、clawhub
- healthcheck、skill-creator、qmd

**已启用钩子（3个）**：
- session-memory、command-logger、boot-md
```

### 自定义BOOT.md

**可以添加的内容**：
1. **个性化问候**
   ```markdown
   ## 个性化问候
   官家，{当前时间}好！
   ```

2. **待办提醒**
   ```markdown
   ## 今日待办
   - 检查PMP学习进度
   - 更新知识库
   ```

3. **自定义任务**
   ```markdown
   ## 启动任务
   1. 检查QMD状态
   2. 验证模型连接
   3. 加载最新记忆
   ```

### 验证方法

**测试1：重启OpenClaw**
```bash
# 重启OpenClaw
openclaw gateway restart

# 观察启动日志
# 应该看到BOOT.md被执行
```

**测试2：查看启动消息**
- OpenClaw启动后，应该收到问候消息
- 系统状态检查结果

---

## 四、三个Hooks协同工作

### 协同场景

**场景1：新用户首次对话**
1. **boot-md**：启动时加载系统状态
2. **session-memory**：保存首次对话信息
3. **command-logger**：记录所有交互

**场景2：老用户日常使用**
1. **boot-md**：启动时问候
2. **session-memory**：加载历史记忆，记住用户偏好
3. **command-logger**：记录新交互

**场景3：问题回溯**
1. **command-logger**：查找历史日志
2. **session-memory**：加载相关会话上下文
3. **boot-md**：重启后恢复工作状态

### 数据流
```
用户输入 → command-logger记录 → AI处理
    ↓
session-memory保存 ← AI响应
    ↓
boot-md启动 ← 系统重启
```

---

## 五、故障排查

### session-memory不工作

**症状**：AI记不住之前的对话

**检查**：
```bash
# 1. 检查钩子状态
openclaw hooks list

# 2. 检查存储目录
ls ~/.openclaw/workspace/memory/sessions/

# 3. 检查配置文件
cat ~/.openclaw/openclaw.json | grep session-memory
```

**解决**：
- 确保hooks list显示ready
- 确保sessions目录存在且可写
- 检查配置文件格式正确

### command-logger不记录

**症状**：找不到日志文件

**检查**：
```bash
# 1. 检查日志目录
ls ~/.openclaw/logs/

# 2. 检查文件权限
ls -la ~/.openclaw/logs/

# 3. 检查配置
cat ~/.openclaw/openclaw.json | grep command-logger
```

**解决**：
- 创建logs目录：`mkdir -p ~/.openclaw/logs`
- 检查文件权限
- 重启OpenClaw

### boot-md不运行

**症状**：启动时没有问候

**检查**：
```bash
# 1. 检查BOOT.md是否存在
ls ~/.openclaw/workspace/BOOT.md

# 2. 检查文件内容
cat ~/.openclaw/workspace/BOOT.md

# 3. 检查钩子状态
openclaw hooks list
```

**解决**：
- 确保BOOT.md存在
- 确保文件内容有效
- 重启OpenClaw

---

## 六、最佳实践

### 1. 信任但验证
- 信任AI的记忆能力
- 定期检查会话文件
- 定期清理旧记忆

### 2. 日志管理
- 定期备份重要日志
- 定期清理旧日志
- 使用日志分析工具

### 3. 启动脚本维护
- 定期更新BOOT.md
- 添加个性化内容
- 保持简洁有效

### 4. 协同使用
- 充分利用三个Hooks的协同效应
- 建立完整的工作流
- 定期评估效果

---

## 七、高级用法

### session-memory高级配置

**自定义保留策略**：
```json
{
  "memory": {
    "maxSessions": 200,
    "retentionDays": 730,
    "compressOld": true,
    "compressAfterDays": 90
  }
}
```

**上下文窗口控制**：
```json
{
  "context": {
    "maxMessages": 100,
    "includeTools": true,
    "includeFiles": true,
    "prioritizeRecent": true
  }
}
```

### command-logger高级配置

**多级日志**：
```json
{
  "output": {
    "file": "logs/commands.log",
    "level": "info",
    "rotate": "daily",
    "compress": true
  }
}
```

**过滤敏感信息**：
```json
{
  "filter": {
    "excludePatterns": ["password", "token", "secret"],
    "maskFields": ["apiKey", "password"]
  }
}
```

### boot-md高级用法

**动态内容**：
```markdown
## 动态任务
- 当前时间：{now}
- 今日待办：{daily_tasks}
- 天气：{weather}
```

**条件执行**：
```markdown
## 条件任务
{{if time < "12:00"}}
- 早晨任务：检查邮件
{{endif}}

{{if weekday}}
- 工作日任务：检查日历
{{endif}}
```

---

**最后更新**：2026年2月27日 13:30
**适用对象**：OpenClaw用户、AI助手集成
**核心目标**：充分利用三个Hooks，打造智能化、自动化、可追溯的AI助手
