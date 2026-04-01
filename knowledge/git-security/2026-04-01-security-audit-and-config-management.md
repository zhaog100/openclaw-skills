# Git 安全审计与配置管理

**日期**: 2026-04-01  
**分类**: Git / 安全 / 配置管理

---

## 📋 概述

本文档记录了 Git 仓库安全审计、API Key 轮换、分支管理和配置同步的完整流程。

---

## 🔒 安全审计

### 配置文件权限

**问题**: openclaw.json 权限过松（664）  
**修复**: `chmod 600 ~/.openclaw/openclaw.json`  
**验证**: `ls -la ~/.openclaw/openclaw.json`

### 敏感信息处理

**脱敏规则：**
- 密码: `****bwyn` (只显示后4位)
- API Key: `sk-proj-lsd***5cA` (前缀 + *** + 后4位)
- Token: `ghp_dS3***oDrdn` (前缀 + *** + 后4位)
- 邮箱: `z***@gmail.com` (首字母 + *** + 域名)

**存储规则：**
- 所有敏感信息存储在 `.env` 文件
- `.env` 已加入 `.gitignore`
- Git 历史已用 `git filter-repo` 清理

---

## 🔑 API Key 轮换

### 轮换流程

1. **评估必要性**
   - Git 历史泄露
   - 定期安全更新
   - Token 失效

2. **创建新 Key**
   - GitHub: https://github.com/settings/tokens/new
   - 智谱: https://open.bigmodel.cn/api-keys
   - 百炼: https://dashscope.console.aliyun.com/apiKey

3. **更新配置文件**
   - `~/.git-credentials`
   - `~/.openclaw/secrets/*.env`
   - `~/.openclaw/agents/main/agent/models.json`

4. **同步到 Docker**
   ```bash
   docker cp <file> <container>:<path>
   docker restart <container>
   ```

5. **验证**
   - GitHub: `gh auth status`
   - API: 发送测试请求
   - QQ Bot: 检查连接状态

### 权限要求

**GitHub Token:**
- `repo` (完整仓库访问)
- `workflow` (GitHub Actions)
- `read:org` (读取组织信息)
- `write:packages` (写入包)

---

## 📦 Git 分支管理

### 分支合并

**无共同历史合并：**
```bash
git merge <branch> --allow-unrelated-histories
```

**冲突解决策略：**
1. 优先保留本地权威版本
2. 删除远程归档目录
3. 统一文件组织结构

**分支删除：**
```bash
# 删除远程分支
git push <remote> --delete <branch>

# 删除本地分支
git branch -d <branch>

# 强制删除未合并分支
git branch -D <branch>
```

### 大文件推送

**问题**: HTTP 408 timeout  
**解决**:
```bash
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 5M
```

**替代方案**:
- 使用 SSH 协议（需要配置公钥）
- 分批推送
- 压缩历史: `git gc --aggressive`

---

## 🐳 Docker 配置同步

### 同步流程

**1. 复制配置文件**
```bash
docker cp <local-file> <container>:<remote-path>
```

**2. 更新敏感信息**
```bash
docker exec <container> sed -i 's/old/new/g' <file>
```

**3. 重启容器**
```bash
docker restart <container>
```

**4. 验证**
```bash
docker logs <container> --tail 20
docker exec <container> cat <file>
```

### QQ Bot 配置更新

**小米辣：**
- AppID: `102911630`
- Token: `RyV3cBlMxZCpT8nTArZI1lWH3pcQE3tj`
- 文件: `~/.openclaw/openclaw.json`

**小米糕：**
- AppID: `1903665913`
- Token: `br8PhzIbvFawIf2QoDc2StLnGjDhChDj`
- 文件: `/root/.openclaw/openclaw.json`

**重启验证：**
- Gateway 运行状态
- WebSocket 连接状态
- Session resumed

---

## 🎮 Vulkan GPU 支持

### 安装

```bash
sudo apt install -y libvulkan-dev vulkan-tools glslc
```

### 验证

```bash
vulkaninfo --summary
```

### QMD 加速

**效果**:
- 搜索速度: 0.3-0.5 秒（CPU 模式）
- GPU 加速: 需要真 GPU（VM 不支持）

---

## 📚 经验教训

### 1. Git 安全
- 配置文件权限必须 600
- 敏感信息必须脱敏
- 定期轮换 API Key
- Git 历史需要清理

### 2. 分支管理
- 无共同历史需要特殊参数
- 冲突解决要有策略
- 大文件推送需要优化

### 3. 配置同步
- Docker 需要手动同步配置
- Token 更新需要重启
- 验证是必不可少的步骤

### 4. 网络问题
- SSH 连接可能失败
- HTTPS 超时可以调整
- 重试是必要的

---

## 🔗 相关资源

- [GitHub Token 管理](https://github.com/settings/tokens)
- [OpenClaw 配置文档](https://docs.openclaw.ai)
- [Git 分支管理](https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%AE%A1%E7%90%86)
- [Docker 配置同步](https://docs.docker.com/engine/reference/commandline/cp/)

---

**更新**: 2026-04-01  
**维护**: 小米辣 (PM + Dev) 🌶️
