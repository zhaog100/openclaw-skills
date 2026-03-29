# ClawHub 配置指南

_更新时间：2026-03-09 17:30_

---

## 📊 当前状态

```json
{
  "registry": "https://clawhub.ai",
  "api_key": "未配置",
  "cli": "未安装"
}
```

---

## 🔧 配置选项

### 方式1：在线发布（推荐新手）

**适合场景：** 偶尔发布，不需要命令行

**步骤：**
1. 访问 https://clawhub.com
2. 注册/登录账号
3. 点击 "Publish Skill"
4. 上传技能包（.tar.gz）
5. 填写技能信息

**优点：**
- ✅ 简单直观
- ✅ 无需安装工具
- ✅ 图形界面操作

**缺点：**
- ❌ 每次需要上传文件
- ❌ 无法批量发布

---

### 方式2：ClawHub CLI（推荐开发者）

**适合场景：** 频繁发布，需要自动化

#### 安装 CLI

```bash
# 检查 Node.js
node --version  # 需要 v18+

# 安装 ClawHub CLI
npm install -g @clawhub/cli

# 验证安装
clawhub --version
```

#### 配置认证

```bash
# 方式1：交互式登录
clawhub login

# 方式2：手动配置
mkdir -p ~/.config/clawhub
cat > ~/.config/clawhub/config.json << EOF
{
  "registry": "https://clawhub.ai",
  "api_key": "YOUR_API_KEY_HERE",
  "email": "your@email.com"
}
EOF
```

#### 获取 API Key

1. 登录 https://clawhub.com
2. 进入 Settings → API Keys
3. 点击 "Generate New Key"
4. 复制 Key 到配置文件

---

## 🚀 常用命令

### 查看配置
```bash
clawhub config list
clawhub whoami
```

### 发布技能
```bash
# 检查技能
clawhub inspect <slug>

# 发布新技能
clawhub publish /path/to/skill --version 1.0.0

# 更新技能
clawhub publish /path/to/skill --version 1.1.0
```

### 安装技能
```bash
clawhub install <slug>
clawhub install <slug>@1.0.0
```

### 管理技能
```bash
clawhub list              # 列出已安装技能
clawhub search <keyword>  # 搜索技能
clawhub info <slug>       # 查看详情
clawhub update <slug>     # 更新技能
clawhub remove <slug>     # 删除技能
```

---

## 📋 你已发布的技能

从记忆库中找到以下技能：

| 技能名称 | 版本 | 发布ID | 发布日期 |
|---------|------|--------|---------|
| **miliger-context-manager** | v2.2.2 | k9720rgtq7nytyjgyzx6sbgg0n82cxf9 | 2026-03-06 |
| **smart-model-switch** | v1.3.0 | k97383tnwydej4c1ntcbfkdhws82amgg | 2026-03-05 |
| **quote-reader** | v1.1.0 | k9789dbamh0bv6yb0hecgwd2kn82bqzt | 2026-03-05 |
| **image-content-extractor** | v2.0.0 | k97dazj7a3ywc4syne4kn3r83d82cz35 | 2026-03-06 |
| **smart-memory-sync** | v1.0.0 | k9791azgxkhtf9r8sfy08g5bkd82dzws | 2026-03-06 |

**总计：12个技能已发布** ⭐⭐⭐⭐⭐

---

## 🔑 快速配置（你的情况）

**根据你的使用记录，你已经有ClawHub账号并发布过技能。**

### 选项1：找回API Key

```bash
# 访问 ClawHub 网站
https://clawhub.com/settings/api-keys

# 复制 API Key
```

### 选项2：重新登录

```bash
# 如果安装了 CLI
clawhub login

# 按提示输入邮箱和密码
```

### 选项3：继续使用在线发布

```bash
# 打包技能
cd ~/.openclaw/workspace/skills/<skill-name>
tar -czf ../<skill-name>.tar.gz .

# 访问 https://clawhub.com/publish
# 上传 .tar.gz 文件
```

---

## 💡 推荐配置路径

**对于你（已有发布记录）：**

```bash
# 1. 安装 CLI（如果需要自动化）
npm install -g @clawhub/cli

# 2. 登录账号
clawhub login

# 3. 验证配置
clawhub whoami

# 4. 查看已发布技能
clawhub list --mine
```

---

## 📝 配置文件位置

```
~/.config/clawhub/
├── config.json        # 主配置
├── credentials.json   # 认证信息
└── cache/             # 缓存目录
```

---

## ⚠️ 常见问题

### Q: 忘记API Key怎么办？
A: 访问 https://clawhub.com/settings/api-keys 重新生成

### Q: 技能发布失败？
A: 检查：
- 文件大小（<20MB）
- package.json 格式
- 必需文件（SKILL.md, package.json）

### Q: 如何更新已发布的技能？
A: `clawhub publish /path/to/skill --version 1.1.0`

### Q: 如何删除技能？
A: `clawhub unpublish <slug>` 或网站操作

---

## 🎯 下一步

1. **选择配置方式**（在线 vs CLI）
2. **配置认证信息**
3. **验证配置**（发布测试技能）
4. **开始使用**

---

*ClawHub配置指南*
*版本：v1.0*
*适用于：已有账号的用户*
