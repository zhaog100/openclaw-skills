# 智能上下文管理策略

**版本**: v1.0.0
**创建时间**: 2026-03-04 19:03
**目标**: 自动管理长对话的上下文，避免达到模型限制

---

## 📊 当前状态分析

**模型信息**:
```
模型: zai/glm-5
上下文限制: 205k tokens
当前使用: 90k/205k (44%)
剩余: 115k tokens
触发阈值: 195k tokens (95%)
```

**会话信息**:
```
会话Key: agent:main:qqbot:direct:b1094aa...
类型: QQ私聊
状态: 活跃中
```

---

## 🎯 策略设计

### 方案A：自动记忆更新（推荐）

**触发条件**:
```
当上下文达到 95% (195k tokens) 时
```

**执行流程**:
```
1. 检测当前token使用率 >= 95%
2. 自动提取本次对话关键信息
3. 更新 memory/YYYY-MM-DD.md
4. 更新 MEMORY.md（长期记忆）
5. 更新知识库（如果有关键知识点）
6. 记录会话ID和关键决策
7. 发送提醒给用户（可选）
```

**提取内容**:
```
✅ 用户偏好和决策
✅ 重要任务和进展
✅ 配置变更
✅ 问题解决方案
✅ 待办事项
✅ 关键数据和信息
```

**记忆格式**:
```markdown
# 会话总结 [Session ID]

**时间**: YYYY-MM-DD HH:MM
**会话ID**: agent:main:qqbot:direct:xxx
**Token使用**: XXX/205k

## 关键决策
- 决策1
- 决策2

## 任务进展
- 已完成：XXX
- 进行中：XXX
- 待办：XXX

## 重要信息
- 信息1
- 信息2

## 配置变更
- 变更1
- 变更2
```

---

### 方案B：新会话传递（高级）

**触发条件**:
```
当上下文达到 95% (195k tokens) 时
```

**执行流程**:
```
1. 检测当前token使用率 >= 95%
2. 提取关键信息（同方案A）
3. 创建记忆文件
4. 发送系统消息提醒用户
5. 等待用户开始新会话
6. 新会话自动加载记忆文件
```

**系统提醒格式**:
```
💡 上下文即将达到上限（95%）
我已经整理了本次对话的关键信息
建议开始新会话继续对话
新会话会自动加载我们的记忆 💾
```

---

### 方案C：知识库更新（知识管理）

**触发条件**:
```
当上下文达到 95% 且有重要知识时
```

**执行流程**:
```
1. 检测当前token使用率 >= 95%
2. 分析对话内容，提取知识点
3. 判断是否需要更新知识库：
   - 新的技能或工具
   - 重要的配置信息
   - 解决问题的方法
   - 最佳实践
4. 创建/更新知识库文件
5. 运行 qmd update 更新索引
6. 记录更新日志
```

**知识库格式**:
```
knowledge-base/
├── project-management/
├── software-testing/
├── content-creation/
├── system-configuration/  ← 新增
│   ├── openclaw-config.md
│   ├── qqbot-config.md
│   └── miliger-config.md  ← 新增
└── troubleshooting/  ← 新增
    └── common-issues.md
```

---

## 🔧 实现方案

### 方法1：Hook钩子（推荐）

**创建钩子脚本**:
```bash
/root/.openclaw/hooks/session-memory/
├── context-monitor.sh  # 监控脚本
├── extract-memory.py   # 提取记忆
├── update-knowledge.py # 更新知识库
└── notify-user.sh      # 通知用户
```

**配置Hook**:
```json
{
  "hooks": {
    "session-memory": {
      "triggers": ["context:95%"],
      "actions": [
        "extract-memory",
        "update-knowledge",
        "notify-user"
      ]
    }
  }
}
```

**优点**:
- ✅ 自动执行
- ✅ 无需人工干预
- ✅ 可靠稳定

---

### 方法2：定时检查（简单）

**Cron任务**:
```bash
# 每小时检查一次上下文
0 * * * * /root/.openclaw/scripts/check_context.sh
```

**检查脚本**:
```python
#!/usr/bin/env python3
import requests
import json

# 获取当前会话状态
response = requests.get('http://localhost:3000/api/sessions')
sessions = response.json()

for session in sessions:
    if session['tokens_used'] / session['tokens_limit'] >= 0.95:
        # 触发记忆更新
        update_memory(session['id'])
        notify_user(session['id'])
```

**优点**:
- ✅ 实现简单
- ✅ 资源消耗少
- ⚠️ 可能有延迟

---

### 方法3：手动触发（最简单）

**用户命令**:
```
官家发送："保存会话记忆"
或："更新记忆"
```

**执行流程**:
```
1. 接收用户命令
2. 提取本次对话关键信息
3. 更新记忆文件
4. 确认完成
```

**优点**:
- ✅ 完全可控
- ✅ 实现最简单
- ⚠️ 需要人工触发

---

## 💾 记忆文件结构

### 短期记忆（Daily Log）
```
memory/2026-03-04.md
```

**内容**:
```markdown
# 2026-03-04 会话记录

## 会话1 (19:03-20:30)
**Token使用**: 90k/205k (44%)
**会话ID**: agent:main:qqbot:direct:b1094aa...

### 关键决策
1. 优惠券推送格式改为Markdown链接
2. 暂缓B站/小红书签到配置
3. 维持米粒管家现状

### 任务进展
✅ 京东双账号配置完成
✅ 优惠券推送格式统一
⏸️ 抖音/快手Cookie抓取（技术限制）

### 重要信息
- 抖音极速版需要手机端Cookie（网页版不兼容）
- Server酱推送在微信中无法直接跳转
- 新的Markdown链接格式：[领取优惠券](链接)
```

### 长期记忆（MEMORY.md）
```
MEMORY.md
```

**更新内容**:
```markdown
## 🎯 重要里程碑

**2026-03-04 优惠券推送优化**:
- ✅ 测试多种链接格式
- ✅ 确认Markdown链接格式最实用
- ✅ 统一所有推送脚本为Markdown格式
- ✅ 立即发送4种推送验证新格式
- 📊 格式：[领取优惠券](链接)
```

### 知识库（Knowledge Base）
```
knowledge-base/system-configuration/miliger-config.md
```

**内容**:
```markdown
# 米粒管家配置指南

## 优惠券推送配置

### Server酱推送格式
**格式**: Markdown链接
**代码**: `message += f"- 🔗 [领取优惠券]({url})\n\n"`
**显示**: 领取优惠券（可点击/长按）

### 推送时间
- 京东优惠券：每天9:30
- 满减券：每天9:30
- 咖啡券：每天9:30
- 运动品牌券：每天9:30
```

---

## 🎯 推荐方案

**短期（立即可用）**:
```
✅ 方案3：手动触发
- 官家发送"更新记忆"
- 我立即提取关键信息
- 更新memory/和MEMORY.md
```

**中期（1-2周内）**:
```
✅ 方案2：定时检查
- 每小时检查一次上下文
- 达到95%自动更新记忆
- 发送提醒给用户
```

**长期（1个月内）**:
```
✅ 方案1：Hook钩子
- 实时监控上下文
- 自动触发记忆更新
- 无需人工干预
```

---

## 📋 执行步骤

**立即实施（手动方案）**:
```
1. 官家发送"更新记忆"
2. 我提取本次对话关键信息
3. 更新memory/2026-03-04.md
4. 更新MEMORY.md
5. 可选：更新知识库
6. 确认完成
```

**下次会话**:
```
1. 我自动加载memory/2026-03-04.md
2. 读取MEMORY.md长期记忆
3. 可选：查询知识库
4. 继续对话，无缝衔接
```

---

**状态**: ✅ 策略设计完成
**下一步**: 等待官家选择方案
