# 2026-03-09 ClawHub CLI 安装记录

**时间：** 17:30-17:50（20分钟）
**状态：** ✅ 完成

---

## 📊 安装成果

```
✅ Bun 1.3.10（npm 安装）
✅ ClawHub CLI 0.0.1（clawnet）
✅ 可用命令：login, publish, install, search, info, star
```

---

## 🔧 安装步骤

### 1. 安装 ClawHub CLI
```bash
npm install -g @clawhub/cli
```

### 2. 安装 Bun 运行时
```bash
# 方式1：官方脚本（慢）
curl -fsSL https://bun.sh/install | bash

# 方式2：npm 安装（快）✅
npm install -g bun
```

### 3. 验证安装
```bash
bun --version     # 1.3.10
clawnet --version # 0.0.1
```

---

## ⚠️ 平台说明

### 两个不同的 ClawHub 平台

| 平台 | 地址 | CLI | 你的技能 |
|------|------|-----|---------|
| **ClawHub.ai** | clawhub.ai | 未知 | ✅ 12个已发布 |
| **ClawHub.network** | clawhub.network | clawnet | ❌ 无技能 |

**当前状态：**
- ✅ ClawHub CLI 已安装
- ✅ 连接到 clawhub.network
- ⏸️ 之前的12个技能在 clawhub.ai 上

**建议方案：**
1. **继续使用 clawhub.ai 在线发布**（推荐）
2. **使用 clawhub.network 新平台**
3. **等待 clawhub.ai CLI**

---

## 🚀 可用命令（clawhub.network）

```bash
# 登录
clawnet login

# 发布技能
clawnet publish /path/to/skill

# 搜索技能
clawnet search <keyword>

# 安装技能
clawnet install <slug>

# 查看详情
clawnet info <slug>

# 收藏技能
clawnet star <slug>
```

---

## 📝 配置文件

```
~/.config/clawhub/config.json
{
  "registry": "https://clawhub.ai"
}

ClawHub CLI 默认连接：
https://clawhub.network
```

---

## 💡 下一步

**选项1：继续使用 clawhub.ai**
- 访问 https://clawhub.ai
- 在线发布技能（熟悉的流程）

**选项2：使用 clawhub.network**
- 登录：`clawnet login`
- 发布：`clawnet publish /path/to/skill`

---

*安装完成时间：2026-03-09 17:50*
