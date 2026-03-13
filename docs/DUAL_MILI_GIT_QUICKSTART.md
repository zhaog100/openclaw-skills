# 双米粒协作系统 - Git通信快速开始

**版本**：v4.0 - Git通信集成版
**发布日期**：2026-03-12
**适用于**：两个独立的OpenClaw会话

---

## 🎯 前置条件

### 会话1（小米辣）
- OpenClaw已安装
- Git已配置
- GitHub CLI已安装（`gh`）
- 已认证GitHub账号

### 会话2（小米辣）
- OpenClaw已安装
- Git已配置
- GitHub CLI已安装（`gh`）
- 已认证GitHub账号

### GitHub仓库
- 仓库：`github.com/zhaog100/openclaw-skills`
- 已配置远程推送

---

## 🚀 快速开始（5步）

### 步骤1：初始化（两个会话都执行）

```bash
# 会话1（小米辣）或 会话2（小米辣）
cd /root/.openclaw/workspace

# 初始化通信目录（首次使用）
bash scripts/mili_comm.sh init
```

**创建目录**：
```
.mili_comm/
├── inbox/              # 收件箱
├── outbox/             # 发件箱
├── archive/            # 归档
├── issues.txt          # Issue记录
└── status.json         # 状态管理
```

---

### 步骤2：小米辣创建产品构思（会话1）

```bash
# 会话1（小米辣）
cd /root/.openclaw/workspace

# 创建产品构思（自动创建Issue + Git推送）
bash scripts/mili_product_v3.sh demo-skill concept
```

**自动执行**：
1. ✅ 创建产品构思文档
2. ✅ 创建GitHub Issue（标签：小米辣、concept）
3. ✅ 记录Issue编号到 `.mili_comm/issues.txt`
4. ✅ Git提交并推送
5. ✅ 更新状态到 `.mili_comm/status.json`

**输出**：
```
Issue创建成功：#42
URL：https://github.com/zhaog100/openclaw-skills/issues/42
Git推送完成
状态已更新
```

---

### 步骤3：小米辣读取并开发（会话2）

```bash
# 会话2（小米辣）
cd /root/.openclaw/workspace

# 拉取最新代码
bash scripts/mili_comm.sh pull

# 查询Issue
bash scripts/mili_comm.sh query demo-skill open

# 查看Issue详情
bash scripts/mili_comm.sh view 42

# 开发+自检（自动评论Issue + Git推送）
bash scripts/xiaomi_dev_v3.sh demo-skill dev
bash scripts/xiaomi_dev_v3.sh demo-skill check
```

**自动执行**：
1. ✅ Git拉取最新代码
2. ✅ 查询并读取Issue #42
3. ✅ 创建Git分支 `feature/2026-03-12_demo-skill`
4. ✅ 开发功能代码
5. ✅ 创建自检文档
6. ✅ 评论Issue（"开发完成，请求Review"）
7. ✅ Git提交并推送

---

### 步骤4：小米辣Review（会话1）

```bash
# 会话1（小米辣）
cd /root/.openclaw/workspace

# 拉取最新代码
bash scripts/mili_comm.sh pull

# Review（自动评论Issue + Git推送）
bash scripts/mili_product_v3.sh demo-skill review
```

**自动执行**：
1. ✅ Git拉取最新代码
2. ✅ 读取小米辣的自检文档
3. ✅ 12维度Review（含反对意见）
4. ✅ 创建Review文档
5. ✅ 评论Issue（"Review完成，✅ 批准"）
6. ✅ Git提交并推送

---

### 步骤5：小米辣发布（会话2）

```bash
# 会话2（小米辣）
cd /root/.openclaw/workspace

# 拉取最新代码
bash scripts/mili_comm.sh pull

# 发布（自动关闭Issue + Git推送）
bash scripts/xiaomi_dev_v3.sh demo-skill publish

# 关闭Issue
bash scripts/mili_comm.sh close 42 "✅ 发布成功"
```

**自动执行**：
1. ✅ Git拉取最新代码
2. ✅ 合并feature分支到master
3. ✅ 发布到ClawHub
4. ✅ 关闭GitHub Issue #42
5. ✅ Git推送
6. ✅ 更新状态为"publish"

---

## 📊 通信数据

### .mili_comm/issues.txt

```
# 双米粒Issue记录
# 格式：issue_[功能名]=[issue-number]
# 创建时间：2026-03-12 09:51:00

issue_demo-skill=42
```

### .mili_comm/status.json

```json
{
  "demo-skill": {
    "status": "publish",
    "last_update": "2026-03-12 09:55:00",
    "updater": "小米辣"
  }
}
```

---

## 💡 使用技巧

### 1. 每次操作前先拉取

```bash
# 无论是小米辣还是小米辣，每次操作前都先执行
bash scripts/mili_comm.sh pull
```

### 2. 操作后立即推送

```bash
# 所有脚本都会自动Git推送，但也可以手动推送
bash scripts/mili_comm.sh push "feat: 手动提交"
```

### 3. 查看当前状态

```bash
# 查看所有功能状态
bash scripts/mili_comm.sh status

# 查看特定功能状态
bash scripts/mili_comm.sh status demo-skill
```

### 4. 查询Issue

```bash
# 查询开放的Issue
bash scripts/mili_comm.sh query demo-skill open

# 查询所有Issue（包括已关闭）
bash scripts/mili_comm.sh query demo-skill all
```

---

## 🎯 完整示例：开发demo-skill

### 时间线

```
09:50  小米辣（会话1）创建产品构思
       ↓ 创建Issue #42
       ↓ Git推送
       
09:51  小米辣（会话2）拉取代码
       ↓ 读取Issue #42
       ↓ 开始开发
       
09:55  小米辣（会话2）开发完成
       ↓ 评论Issue #42
       ↓ Git推送
       
09:56  小米辣（会话1）拉取代码
       ↓ Review
       ↓ 评论Issue #42
       ↓ Git推送
       
09:57  小米辣（会话2）发布
       ↓ 关闭Issue #42
       ↓ Git推送
```

---

## 📋 核心命令列表

### 小米辣（会话1）

```bash
# 产品构思
bash scripts/mili_product_v3.sh feature concept

# Review
bash scripts/mili_product_v3.sh feature review

# 5层验收
bash scripts/mili_product_v3.sh feature accept

# Git操作
bash scripts/mili_comm.sh pull
bash scripts/mili_comm.sh push

# Issue操作
bash scripts/mili_comm.sh query feature open
bash scripts/mili_comm.sh view 42
bash scripts/mili_comm.sh comment 42 "消息"
```

### 小米辣（会话2）

```bash
# 并行分析
bash scripts/xiaomi_dev_v3.sh feature analyze

# 开发
bash scripts/xiaomi_dev_v3.sh feature dev

# 自检
bash scripts/xiaomi_dev_v3.sh feature check

# Review后思考
bash scripts/xiaomi_dev_v3.sh feature think

# 发布
bash scripts/xiaomi_dev_v3.sh feature publish

# Git操作
bash scripts/mili_comm.sh pull
bash scripts/mili_comm.sh push

# Issue操作
bash scripts/mili_comm.sh query feature open
bash scripts/mili_comm.sh view 42
bash scripts/mili_comm.sh comment 42 "消息"
bash scripts/mili_comm.sh close 42 "完成"
```

---

## ⚠️ 注意事项

### 1. GitHub CLI配置

```bash
# 首次使用需要认证
gh auth login

# 验证配置
gh auth status
```

### 2. Git配置

```bash
# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 配置远程仓库
git remote add origin https://github.com/zhaog100/openclaw-skills.git
```

### 3. 冲突处理

如果Git推送失败，可能是因为远程有新的提交：

```bash
# 拉取并合并
git pull --rebase origin master

# 推送
git push origin master
```

---

## 🎊 总结

### 核心优势

1. ✅ **异步通信**：不需要同时在线
2. ✅ **可追溯**：所有通信都有GitHub记录
3. ✅ **可搜索**：通过GitHub搜索历史Issue
4. ✅ **跨平台**：只要能访问GitHub就能协作
5. ✅ **版本控制**：Git管理所有文档和代码
6. ✅ **自动化**：所有脚本自动Git同步

### 最佳实践

1. **每次操作前先拉取**：避免冲突
2. **操作后立即推送**：让另一个会话看到最新状态
3. **使用Issue跟踪**：所有重要阶段都创建或评论Issue
4. **定期检查状态**：`bash scripts/mili_comm.sh status`

---

*发布时间：2026-03-12*
*版本：v4.0 - Git通信集成版*
*作者：小米辣（官家的智能助理）*
