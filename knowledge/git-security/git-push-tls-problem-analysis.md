# Git 推送 TLS 问题详细分析

> 创建时间：2026-04-01 17:58
> 更新时间：2026-04-01

---

## 🔍 问题诊断

### 错误信息
```
fatal: 无法访问 'https://github.com/zhaog100/xiaomila-skills.git/'：
gnutls_handshake() failed: The TLS connection was non-properly terminated.

curl 35 GnuTLS recv error (-110): The TLS connection was non-properly terminated.
```

---

## 📊 问题原因分析

### 1. **TLS 握手失败**
- **症状**: `gnutls_handshake() failed`
- **含义**: Git 在与 GitHub 建立 HTTPS 连接时失败
- **阶段**: TLS/SSL 握手阶段（连接建立前）

### 2. **可能的原因**

#### A. **网络层面**
1. **防火墙/代理阻止**
   - 某些网络环境会阻止 HTTPS 连接
   - 企业网络可能有严格的 TLS 检查

2. **网络不稳定**
   - TLS 握手需要多次往返通信
   - 网络延迟或丢包可能导致失败

3. **MTU 问题**
   - 大数据包在传输中被分片
   - TLS 握手包过大导致失败

#### B. **TLS 层面**
1. **TLS 版本不兼容**
   - GitHub 要求 TLS 1.2 或更高
   - GnuTLS 可能配置不当

2. **证书问题**
   - CA 证书库过期或损坏
   - 证书链验证失败

3. **加密套件不匹配**
   - 客户端和服务器没有共同支持的加密算法

#### C. **Git 配置**
1. **GnuTLS 库问题**
   - Git 使用 GnuTLS 而非 OpenSSL
   - GnuTLS 某些版本有兼容性问题

2. **缓冲区设置**
   - 大文件推送时缓冲区不足
   - 已修复：`http.postBuffer 524288000`

---

## 🧪 测试和验证

### 测试 1: 基本网络连接
```bash
ping github.com
# 结果: ✅ 正常（0% 丢包）
# 结论: 网络连通性正常
```

### 测试 2: HTTPS 连接
```bash
curl -v https://github.com
# 结果: ❌ 失败（exit code 35）
# 错误: GnuTLS recv error (-110)
# 结论: HTTPS/TLS 问题
```

### 测试 3: SSH 连接
```bash
ssh -T git@github.com
# 结果: ❌ 失败
# 错误: Connection closed by port 22
# 结论: SSH 端口被阻止或配置问题
```

### 测试 4: Git 推送
```bash
git push xiaomila main
# 结果: ❌ 失败
# 错误: gnutls_handshake() failed
# 结论: Git HTTPS 推送不可用
```

---

## 🔧 解决方案

### 方案 1: **切换到 SSH**（推荐）
**优点**: 绕过 HTTPS/TLS 问题
**前提**: SSH 连接必须正常
**步骤**:
1. 解决 SSH 连接问题
2. 修改远程 URL: `git remote set-url origin git@github.com:...`
3. 推送: `git push origin main`

**当前状态**: ❌ SSH 也失败（Connection closed by port 22）

---

### 方案 2: **配置 Git 使用 OpenSSL**
**优点**: OpenSSL 更稳定
**步骤**:
```bash
# 重新编译 Git 使用 OpenSSL
# 或者使用系统包管理器安装 Git with OpenSSL
sudo apt install git
```

**当前状态**: ⏳ 需要重新编译或重新安装

---

### 方案 3: **配置 HTTP 代理**
**优点**: 绕过网络限制
**前提**: 有可用的代理服务器
**步骤**:
```bash
git config --global http.proxy http://proxy:port
git config --global https.proxy https://proxy:port
```

**当前状态**: ⏳ 需要代理服务器

---

### 方案 4: **使用 Git Bundle**（已实施）✅
**优点**: 完全离线，不依赖网络
**步骤**:
1. 创建 bundle: `git bundle create backup.bundle --all` ✅
2. 传输 bundle 文件（U盘、网盘等）
3. 在其他地方导入: `git clone backup.bundle`

**当前状态**: ✅ 已创建 backup-2026-04-01.bundle（291MB）

---

### 方案 5: **等待网络恢复**
**优点**: 无需额外配置
**前提**: 问题是临时的
**步骤**:
1. 定期重试（已配置 cron）✅
2. 记录推送日志 ✅
3. 等待网络环境改善

**当前状态**: ✅ 已配置定期重试

---

## 📋 推荐行动计划

### 🔴 立即执行（已完成）
1. ✅ 创建 Bundle 备份（防止数据丢失）
2. ✅ 配置定期重试（每天 2 次）
3. ✅ 修复 .env 权限（安全问题）

### 🟠 一周内执行
1. **调查 SSH 问题**
   - 检查 SSH 配置: `~/.ssh/config`
   - 检查防火墙规则
   - 尝试其他 SSH 端口（443）

2. **尝试代理推送**
   - 寻找可用的代理服务器
   - 配置 Git 代理

3. **重新编译 Git**
   - 使用 OpenSSL 替代 GnuTLS
   - 或使用 Docker 容器中的 Git

### 🟢 可选方案
1. **迁移到其他平台**
   - GitLab、Gitee 等
   - 可能网络环境更友好

2. **使用 GitHub API**
   - 通过 API 创建提交
   - 绕过 Git 推送

---

## 🎯 问题本质

**核心问题**: GnuTLS 库与 GitHub HTTPS 不兼容

**影响范围**:
- ❌ 无法推送（origin/main、xiaomila/main）
- ❌ SSH 也失败（多一层问题）
- ✅ 本地工作正常
- ✅ 数据已备份（Bundle）

**关键点**:
1. **不是 Git 问题** - 是 TLS 库问题
2. **不是 GitHub 问题** - 是网络/客户端问题
3. **不是致命问题** - 有备选方案（Bundle）

---

## 💡 总结

### 问题定性
- **类型**: 网络/传输层问题
- **严重性**: 中等（数据安全，但影响同步）
- **紧急性**: 低（有备份，定期重试）

### 推荐方案
1. **短期**: 使用 Bundle 文件传输（已实施）✅
2. **中期**: 解决 SSH 连接问题
3. **长期**: 重新编译 Git 或使用代理

### 预计解决时间
- **如果网络恢复**: 1-3 天
- **如果需要配置**: 1 周
- **如果使用 Bundle**: 立即可用 ✅

---

_更新时间: 2026-04-01 17:58_
