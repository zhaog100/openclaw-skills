# Git 推送最佳实践策略

**文档版本**: v1.0  
**创建日期**: 2026-03-17  
**创建者**: 小米辣 (PM + Dev 双代理) 🌶️

---

## 🚨 问题背景

**常见问题**：Git 推送被拒绝
```
error: Updates were rejected because the remote contains work that you do not have locally.
```

**根本原因**：
1. 推送前没有拉取远程更新
2. 多个设备/会话推送到同一分支
3. Git 配置没有自动 rebase

---

## ✅ 解决方案

### 方案 1：配置 Git 自动 Rebase（推荐）

#### 1️⃣ 全局 Git 配置
```bash
git config --global pull.rebase true
git config --global push.autoSetupRemote true
git config --global rerere.enabled true
```

#### 2️⃣ 安全推送命令
添加到 `~/.bashrc`：
```bash
function git-push-safe() {
    git pull --rebase origin "$(git branch --show-current)" && git push origin "$(git branch --show-current)"
}
alias gps='git-push-safe'
```

#### 3️⃣ 使用方法
```bash
gps  # 一键安全推送
```

---

## 📋 推送前检查清单

1. ✅ `git status` - 检查工作区状态
2. ✅ `git pull --rebase` - 拉取远程更新
3. ✅ 解决冲突（如有）
4. ✅ `git push` - 推送

---

## 🔧 故障排除

### 推送被拒绝
```bash
git pull --rebase origin master
git push origin master
```

### SSH 连接失败
```bash
sudo /etc/init.d/ssh restart
```

---

## 📊 配置验证

```bash
git config --list | grep -E "pull|push|rerere"
ssh -T git@github.com
```

---

**最后更新**: 2026-03-17 14:22  
**更新者**: 小米辣 (PM + Dev 双代理) 🌶️
