# 🦎 Git 仓库索引

_最后更新：2026-03-24 15:08_

---

## 📦 仓库配置

### 双仓库结构

```
工作区：/home/zhaog/.openclaw/workspace/
├── origin      → git@github.com:zhaog100/openclaw-skills.git
└── xiaomila    → git@github.com:zhaog100/xiaomila-skills.git
```

| 远程仓库 | 用途 | 推送内容 |
|----------|------|----------|
| **origin** | 公共技能库 | 公共技能、核心框架 |
| **xiaomila** | 个人技能库 | 个人技能、小米辣专属 |

---

## 🎯 推送规则

### 核心原则
```
辣推辣，公推公 ✅
```

### 判断标准

| 内容类型 | 推送目标 | 示例 |
|----------|----------|------|
| **公共技能** | origin | github-bounty-hunter, smart-model-switch |
| **个人技能** | xiaomila | 个人工具、测试技能 |
| **核心配置** | origin | AGENTS.md, MEMORY.md, SOUL.md |
| **个人笔记** | xiaomila | 个人学习记录 |

### 决策流程
```
1. 是否涉及核心框架？
   ├─ 是 → origin
   └─ 否 → 继续判断

2. 是否可复用/有通用价值？
   ├─ 是 → origin
   └─ 否 → xiaomila

3. 是否个人专属？
   ├─ 是 → xiaomila
   └─ 否 → origin
```

---

## 📊 当前状态

### Git 状态
```bash
$ git status
位于分支 master
与上游分支 'origin/master' 一致
```

### 未提交变更（需要处理）
| 文件 | 类型 | 建议推送 |
|------|------|----------|
| AGENTS.md | 核心规范 | origin |
| HEARTBEAT.md | 核心规范 | origin |
| IDENTITY.md | 核心身份 | origin |
| MEMORY.md | 长期记忆 | origin |
| TOOLS.md | 工作备忘 | origin |
| USER.md | 用户档案 | origin |
| Stellar-Guilds | 子模组 | 单独判断 |
| data/bounty-known-issues.txt | 数据 | origin |

---

## 🔧 常用命令

### 查看状态
```bash
git status
git remote -v
```

### 推送公共内容
```bash
git add <文件>
git commit -m "feat|fix|docs: 描述"
git push origin master
```

### 推送个人内容
```bash
git add <文件>
git commit -m "feat|fix|docs: 描述"
git push xiaomila master
```

### 检查默认分支
```bash
git symbolic-ref refs/remotes/origin/HEAD
```

---

## 📝 提交规范

### Commit Message 格式
```
feat|fix|security|docs|chore([范围]): 描述
```

### 示例
```bash
feat(github-bounty-hunter): 添加自动批量开发功能
fix(context-manager): 修复 context 占用计算错误
docs(MEMORY): 更新 Bounty 狩猎教训
chore(deps): 更新依赖版本
```

### 类型说明
| 类型 | 用途 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| security | 安全修复 |
| docs | 文档更新 |
| chore | 构建/工具/配置 |

---

## ⚠️ 注意事项

### Git Rebase 禁令
```
❌ 禁止使用：git rebase --strategy=ours
✅ 改用：git rebase --skip
```

### 敏感信息
```
❌ 禁止提交：API 密钥、数据库密码、私钥
✅ 正确做法：写入 ~/.openclaw/secrets/
```

### 版权信息
```
✅ 必须包含：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
```

---

## 🔗 关联文档

- **核心规范**: `AGENTS.md` - 行为规范
- **推送规则**: `IDENTITY.md` - 仓库推送规则
- **长期记忆**: `MEMORY.md` - Git 经验记录

---

**维护**: 小米辣 (PM + Dev) 🌶️  
**版本**: v1.0

---

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**
