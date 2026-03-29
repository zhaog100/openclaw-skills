# 软件安装配置指南

_2026-02-28 11:10_

---

## 📂 安装路径配置

### 默认安装路径
```
D:\Program Files (x86)\
```

---

## 🎯 配置规则

### 规则1: 所有软件默认路径
```
默认: D:\Program Files (x86)\[软件名称]
示例:
- VS Code: D:\Program Files (x86)\Microsoft VS Code
- Node.js: D:\Program Files (x86)\nodejs
- Git: D:\Program Files (x86)\Git
```

### 规则2: 64位软件
```
如果软件仅支持64位，使用：
D:\Program Files\[软件名称]
```

### 规则3: 便携软件
```
便携软件可安装在：
D:\Tools\[软件名称]
或
D:\Program Files (x86)\Portable\[软件名称]
```

---

## 📝 已安装软件记录

### 1. Visual Studio Code ✅
```
当前路径: C:\Users\zhaog\AppData\Local\Programs\Microsoft VS Code
状态: ✅ 已安装（用户目录）
备注: 下次可配置到 D:\Program Files (x86)\Microsoft VS Code
```

---

## 🔧 安装命令示例

### winget安装（带路径）
```powershell
# 查看软件信息
winget show [软件ID]

# 安装时指定路径（如果支持）
winget install --id [软件ID] --location "D:\Program Files (x86)"
```

### 手动安装
```
1. 下载安装包
2. 运行安装程序
3. 选择"自定义安装"
4. 修改路径为: D:\Program Files (x86)\[软件名称]
5. 继续安装
```

---

## 📊 路径对比

### 默认路径 vs 自定义路径

| 软件 | 默认路径 | 官家偏好路径 |
|------|---------|-------------|
| VS Code | C:\Users\...\AppData\Local | D:\Program Files (x86)\Microsoft VS Code |
| Node.js | C:\Program Files\nodejs | D:\Program Files (x86)\nodejs |
| Git | C:\Program Files\Git | D:\Program Files (x86)\Git |
| Python | C:\Users\...\AppData\Local | D:\Program Files (x86)\Python |

---

## 💡 注意事项

### 1. 权限问题
```
⚠️ 安装到D盘可能需要管理员权限
✅ 建议: 使用管理员权限运行安装程序
```

### 2. 环境变量
```
✅ 安装后自动添加到PATH
⚠️ 手动检查: 系统属性 → 高级 → 环境变量
```

### 3. 快捷方式
```
✅ 安装时勾选"创建桌面快捷方式"
✅ 安装时勾选"添加到右键菜单"
```

---

## 🎯 安装流程

### 步骤1: 确认软件名称和版本
```powershell
# 搜索软件
winget search [软件名称]
```

### 步骤2: 查看软件信息
```powershell
# 查看详细信息
winget show [软件ID]
```

### 步骤3: 下载安装包（如需手动安装）
```
访问官网下载
或使用winget下载
```

### 步骤4: 安装到指定路径
```powershell
# 自动安装（如果支持路径参数）
winget install --id [软件ID] --location "D:\Program Files (x86)"

# 或手动安装，选择自定义路径
```

### 步骤5: 验证安装
```powershell
# 检查版本
[软件名称] --version

# 检查路径
where [软件名称]
```

---

## 📋 软件清单模板

### 软件安装记录

```markdown
### [软件名称]
- 安装日期: YYYY-MM-DD
- 版本: x.x.x
- 安装路径: D:\Program Files (x86)\[软件名称]
- 安装方式: winget/手动
- 状态: ✅/❌
```

---

## 🔄 迁移指南

### 从C盘迁移到D盘

#### 步骤1: 备份配置
```
导出软件配置和设置
```

#### 步骤2: 卸载旧版本
```
控制面板 → 程序和功能 → 卸载
```

#### 步骤3: 清理残留
```
删除安装目录
删除注册表项（可选）
```

#### 步骤4: 重新安装
```
使用新路径重新安装
```

#### 步骤5: 恢复配置
```
导入之前备份的配置
```

---

## 🎨 最佳实践

### 1. 统一命名规范
```
✅ 使用官方名称
✅ 避免空格和特殊字符
✅ 保持路径简洁
```

### 2. 定期清理
```
✅ 每月检查D盘软件
✅ 卸载不用的软件
✅ 清理临时文件
```

### 3. 备份重要配置
```
✅ 导出软件配置
✅ 保存序列号和密钥
✅ 记录安装步骤
```

---

## 📊 磁盘空间管理

### D盘空间监控
```powershell
# 查看D盘空间
Get-PSDrive D | Select-Object Used,Free

# 查看文件夹大小
Get-ChildItem "D:\Program Files (x86)" | Measure-Object -Property Length -Sum
```

### 空间建议
```
✅ 保持至少20GB可用空间
✅ 定期清理临时文件
✅ 使用磁盘清理工具
```

---

## 🚀 快速安装命令

### 常用软件安装命令

```powershell
# Visual Studio Code
winget install --id Microsoft.VisualStudioCode --location "D:\Program Files (x86)"

# Git
winget install --id Git.Git --location "D:\Program Files (x86)"

# Node.js
winget install --id OpenJS.NodeJS --location "D:\Program Files (x86)"

# Python
winget install --id Python.Python.3.12 --location "D:\Program Files (x86)"

# 7-Zip
winget install --id 7zip.7zip --location "D:\Program Files (x86)"
```

---

## 📝 配置更新记录

### 2026-02-28 11:10
```
✅ 记录官家偏好路径
✅ 创建安装配置指南
✅ 提供安装命令示例
✅ 说明注意事项
```

---

**配置时间**: 2026-02-28 11:10
**状态**: ✅ 已记录
**默认路径**: D:\Program Files (x86)
**适用范围**: 所有未来软件安装
