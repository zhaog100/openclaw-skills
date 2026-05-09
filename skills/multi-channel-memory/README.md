# 🌐 多通道记忆整合技能

**版本**: 1.0.0  
**作者**: 小米粒 (AI Agent) 🌾  
**许可**: MIT License

---

## 🎯 功能特性

| 功能 | 状态 | 说明 |
|------|------|------|
| 多通道对话提取 | ✅ | 终端、QQ、微信、飞书等 |
| UTC→北京时间转换 | ✅ | Asia/Shanghai +8h |
| 元数据自动过滤 | ✅ | message_id, sender metadata 等 |
| 通道来源标注 | ✅ | 每条消息标注通道 |
| 按时间排序 | ✅ |  chronological order |
| Git 自动提交 | ✅ | 可选 |

---

## 🚀 快速开始

### 安装

```bash
# 技能已位于
~/.openclaw/workspace/skills/multi-channel-memory/
```

### 手动提取

```bash
# 提取今天对话
bash scripts/extract-chats.sh

# 提取指定日期
bash scripts/extract-chats.sh 2026-04-10

# 提取并 Git 提交
bash scripts/extract-chats.sh --commit

# 提取指定日期并 Git 提交
bash scripts/extract-chats.sh 2026-04-10 --commit
```

### Python 直接调用

```bash
# 今天
python src/chat_extractor.py

# 指定日期
python src/chat_extractor.py --date 2026-04-10

# 指定输出目录
python src/chat_extractor.py --output-dir /path/to/output
```

---

## 📁 目录结构

```
multi-channel-memory/
├── _meta.json              # 技能元数据
├── README.md               # 本文档
├── scripts/
│   └── extract-chats.sh    # Bash 提取脚本
└── src/
    └── chat_extractor.py   # Python 核心逻辑
```

---

## 📊 输出格式

**文件路径**: `memory/chat-YYYY-MM-DD.md`

**格式示例**:

```markdown
# 多通道对话记录 - 2026-04-10

**生成时间**: 2026-04-10 09:25:00 CST
**通道数量**: 3
**消息总数**: 42
---

## 09:00 - 09:59

### 09:25:10 [飞书] 用户
今天的工作安排是什么？
---

### 09:25:15 [飞书] AI
今天的计划是完成技能更新和论坛冲浪。
---

### 09:30:22 [QQ] 用户
扫描高质量任务在继续吗？
---

### 09:30:25 [QQ] AI
是的！继续全自动扫描和执行！🚀
---

## 10:00 - 10:59

### 10:15:30 [终端] 用户
gh pr merge 33
---

### 10:15:35 [终端] AI
PR #33 已成功合并！
---
```

---

## 🔧 配置

### 1. 启用 sessionMemory（原生支持）

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "experimental": {
    "sessionMemory": true
  }
}
```

**效果**: `memory_search` 可搜索任何通道的上下文

### 2. 配置 identityLinks（通道映射）

```json
{
  "session": {
    "identityLinks": {
      "qqbot:<YOUR_USER_ID>": "canonical:user-zhao",
      "feishu:<YOUR_OPEN_ID>": "canonical:user-zhao"
    }
  }
}
```

**注意**: 将 `<YOUR_USER_ID>` 和 `<YOUR_OPEN_ID>` 替换为你的实际 ID

**效果**: 同一人在不同通道映射到同一身份

### 3. 设置 dmScope = main（共享会话）

```json
{
  "session": {
    "dmScope": "main"
  }
}
```

**效果**: 所有 DM 共享主会话，跨通道连续性

---

## 📅 Cron 集成

已集成到每日回顾流程：

```bash
# 午间回顾 (12:10 CST)
10 12 * * * bash ~/.openclaw/workspace/scripts/daily_review.sh morning

# 晚间回顾 (23:30 CST)
30 23 * * * bash ~/.openclaw/workspace/scripts/daily_review.sh evening
```

**自动执行**:
1. 提取当天多通道对话
2. 保存到 `memory/chat-YYYY-MM-DD.md`
3. Git 提交（如果配置）

---

## 🧪 测试

```bash
# 测试 Python 脚本
python src/chat_extractor.py --date 2026-04-09

# 测试 Bash 脚本
bash scripts/extract-chats.sh 2026-04-09

# 验证输出
cat memory/chat-2026-04-09.md
```

---

## 🎯 使用场景

### 场景 1: 每日回顾

```bash
# 晚间回顾时自动提取
bash scripts/extract-chats.sh --commit
```

### 场景 2: 补录历史对话

```bash
# 提取昨天的对话
bash scripts/extract-chats.sh 2026-04-09
```

### 场景 3: 审计特定日期

```bash
# 提取并查看
bash scripts/extract-chats.sh 2026-04-01
cat memory/chat-2026-04-01.md
```

---

## 📈 统计信息

脚本执行后会输出：

```
[INFO] 开始提取多通道对话...
[INFO] 日期：2026-04-10
[INFO] 输出目录：/Users/zhaog/.openclaw/workspace/memory
✅ 找到 5 个会话
✅ 提取到 42 条消息
📝 格式化聊天日志...
✅ 已保存到：memory/chat-2026-04-10.md

=== 统计信息 ===
总行数：350
消息数：42
小时段数：8
```

---

## 🔐 隐私与安全

### 元数据过滤

自动移除以下内容：
- ❌ message_id
- ❌ sender_id
- ❌ Conversation info JSON
- ❌ Sender metadata JSON
- ❌ [QQBot] 标记
- ❌ 工具调用标记

### 保留内容

- ✅ 用户消息内容
- ✅ AI 回复内容
- ✅ 时间戳（转换为北京时间）
- ✅ 通道来源标注

---

## 🛠️ 故障排除

### 问题 1: 找不到会话文件

**错误**: `Sessions file not found`

**解决**:
```bash
# 检查 sessions 目录
ls -la ~/.openclaw/workspace/sessions/

# 确保 sessions.json 存在
cat ~/.openclaw/workspace/sessions/sessions.json
```

### 问题 2: 时间戳不正确

**原因**: UTC 未转换为北京时间

**解决**: 已自动处理，脚本中 `TIMEZONE_OFFSET = timedelta(hours=8)`

### 问题 3: Git 提交失败

**错误**: `not a git repository`

**解决**:
```bash
# 初始化 Git
cd ~/.openclaw/workspace
git init
git remote add origin <your-repo>
```

---

## 📝 更新日志

### v1.0.0 (2026-04-10)

- ✅ 初始版本
- ✅ 多通道对话提取
- ✅ UTC→北京时间转换
- ✅ 元数据自动过滤
- ✅ 通道来源标注
- ✅ 集成到每日回顾流程

---

## 🙏 致谢

感谢 OpenClaw 社区的 sessionMemory 实验性功能启发！

---

**Built with ❤️ by 小米粒 (AI Agent)** 🌾  
**版权**: 思捷娅科技 (SJYKJ) - MIT License
