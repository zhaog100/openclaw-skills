# ClawHub v7.0.0 更新指南

> miliger-context-manager 版本升级指南

---

## ⚠️ API限流问题

**当前状态：**
```
❌ ClawHub API 限流中
❌ 无法自动下载
✅ 需要手动操作
```

---

## 📋 手动更新步骤

### 步骤1：下载远程版本

**方法A：浏览器下载** ✅ **推荐**

```
1. 访问: https://clawhub.ai/zhaog100/miliger-context-manager
2. 点击页面上的 "Download" 按钮
3. 保存文件到: /tmp/miliger-context-manager-v7.0.0.tar.gz
```

**方法B：等待API限流解除**

```
等待时间: 约1-2分钟
然后运行: ~/.openclaw/workspace/tools/update-context-manager.sh
```

---

### 步骤2：运行更新脚本

```bash
# 下载完成后执行
~/.openclaw/workspace/tools/update-context-manager.sh
```

**脚本功能：**
1. ✅ 备份当前版本（v2.2.2）
2. ✅ 验证下载文件
3. ✅ 删除旧版本
4. ✅ 安装新版本（v7.0.0）
5. ✅ 更新符号链接
6. ✅ 运行安装脚本

---

### 步骤3：验证更新

```bash
# 检查版本
cd ~/.openclaw/workspace/skills/miliger-context-manager-7.0.0
cat package.json | grep version

# 查看文档
cat SKILL.md | head -50

# 查看变更日志（如果有）
cat CHANGELOG.md 2>/dev/null || cat README.md | head -50
```

---

## 🔧 手动安装（如果脚本失败）

### 1. 备份当前版本

```bash
# 创建备份目录
mkdir -p ~/.openclaw/workspace/skills/_archived

# 备份当前版本
cp -r ~/.openclaw/workspace/skills/context-manager-v2 \
      ~/.openclaw/workspace/skills/_archived/context-manager-v2.2.2-backup-$(date +%Y%m%d)
```

### 2. 解压新版本

```bash
# 创建新目录
mkdir -p ~/.openclaw/workspace/skills/miliger-context-manager-7.0.0

# 解压
cd ~/.openclaw/workspace/skills/miliger-context-manager-7.0.0
tar -xzf /tmp/miliger-context-manager-v7.0.0.tar.gz
```

### 3. 验证安装

```bash
# 检查文件
ls -la

# 检查版本
cat package.json | grep version
```

### 4. 运行安装脚本

```bash
# 如果有install.sh
if [ -f install.sh ]; then
    chmod +x install.sh
    ./install.sh
fi
```

---

## 📊 版本变更预期

### v2.2.2 → v7.0.0

**可能的新功能：**
- 性能优化
- 新的监控特性
- 更好的错误处理
- 改进的用户界面

**需要检查：**
- 配置文件格式变化
- 新的环境变量
- 依赖项变化
- API接口变化

---

## 🚨 回滚方案

如果新版本有问题：

### 方案1：从备份恢复

```bash
# 删除新版本
rm -rf ~/.openclaw/workspace/skills/miliger-context-manager-7.0.0

# 恢复备份
cp -r ~/.openclaw/workspace/skills/_archived/context-manager-v2.2.2-backup-* \
      ~/.openclaw/workspace/skills/context-manager-v2
```

### 方案2：重新安装v2.2.2

```bash
# 使用已打包的v2.2.2
cd ~/.openclaw/workspace/skills
tar -xzf context-manager-v2.2.1.tar.gz
```

---

## 📝 更新后检查清单

- [ ] 版本号确认（v7.0.0）
- [ ] 核心文件存在（SKILL.md, package.json）
- [ ] 安装脚本执行成功
- [ ] 功能测试通过
- [ ] 配置文件更新（如有）
- [ ] 文档阅读完成

---

## 🔍 版本差异查看

**在线查看：**
```
https://clawhub.ai/zhaog100/miliger-context-manager
```

**本地对比：**
```bash
# 解压到临时目录
mkdir -p /tmp/context-manager-compare
cd /tmp/context-manager-compare
tar -xzf /tmp/miliger-context-manager-v7.0.0.tar.gz

# 对比核心文件
diff -u ~/.openclaw/workspace/skills/context-manager-v2/SKILL.md \
        /tmp/context-manager-compare/SKILL.md

diff -u ~/.openclaw/workspace/skills/context-manager-v2/package.json \
        /tmp/context-manager-compare/package.json
```

---

## ⏰ 预计时间

- 手动下载: 2-3分钟
- 运行脚本: 1分钟
- 验证测试: 2-3分钟
- **总计: 5-7分钟**

---

## 🆘 常见问题

### Q: 下载按钮在哪里？
A: 访问技能页面后，通常在右上角或版本列表中

### Q: 文件验证失败？
A: 确保下载完整，检查文件大小和格式

### Q: 安装脚本失败？
A: 检查错误日志，可能需要手动安装依赖

### Q: 如何确认是新版本？
A: 查看package.json中的version字段

---

## 📞 需要帮助？

**选项1：等待API限流解除**
- 约1-2分钟后重试

**选项2：手动下载后继续**
- 完成下载后运行脚本

**选项3：查看在线文档**
- 访问ClawHub网站查看详情

---

*更新指南 - miliger-context-manager v7.0.0*
*创建时间: 2026-03-09 18:05*
