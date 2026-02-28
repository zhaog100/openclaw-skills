# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🖥️ 系统环境

### 虚拟机配置
- **环境**：VMware虚拟机
- **显卡**：VMware SVGA 3D（虚拟显卡）
- **CPU优化**：AVX2支持 ✅
- **限制**：无物理GPU，CUDA/Vulkan不可用

---

## 🔍 QMD知识库系统

### 当前状态（2026-02-27 10:30）
- **版本**：QMD v1.1.0
- **索引**：22个文件
- **向量**：生成中（CPU模式）
- **Collections**：3个
  - daily-logs: 5个文件（memory/*.md）
  - workspace: 0个文件
  - knowledge-base: 17个文件（knowledge/*.md）

### 常用命令
```powershell
# 查看状态
qmd status

# 搜索
qmd search "关键词" -c knowledge-base -n 3
qmd search "PMP" -c knowledge-base

# 读取文件
qmd get qmd://knowledge-base/path/to/file.md

# 更新索引
qmd update

# 生成向量（必须设置环境变量！）
$env:QMD_FORCE_CPU="1"; qmd embed

# 混合搜索（向量完成后）
qmd query "如何平衡项目质量和进度" -c knowledge-base
```

### ⚠️ 重要：CPU强制模式
**VMware虚拟机必须设置环境变量**，否则会误判CUDA：

```powershell
# 临时使用（单次会话）
$env:QMD_FORCE_CPU="1"; qmd embed

# 永久启用（推荐）
Add-Content $PROFILE 'Set-Item -Path Env:QMD_FORCE_CPU -Value "1"'
# 重启PowerShell后生效
```

**原因**：VMware虚拟GPU会被 `node-llama-cpp` 误判为CUDA，导致尝试编译CUDA binaries失败。

### 知识库路径
```
knowledge-base/
├── project-management/（6个文件）
│   ├── pmp-certification/
│   ├── agile-methodology/
│   └── project-planning/
├── software-testing/（4个文件）
│   ├── test-automation/
│   ├── test-management/
│   └── test-tools/
├── content-creation/（3个文件）
│   ├── content-strategy/
│   ├── video-creation/
│   └── wechat-public/
└── 其他（4个文件）
```

### MCP配置
- **配置文件**：`C:\Users\zhaog\.openclaw\workspace\config\mcporter.json`
- **服务**：已配置，待启用

---

## ⏰ 定时任务

### 已配置任务
- **中午12:00**：`qmd update`
- **晚上23:50**：`qmd update`
- **配置文件**：CRON-CONFIG.md

### 手动触发
```bash
# 检查cron状态
openclaw cron status

# 手动运行更新
qmd update
```

---

## 🚀 QMD GPU加速方案（未来优化）

### 当前状态
- ✅ CPU模式：完全可用
- ⏱️ 性能：22文件首次生成10-15分钟，增量更新10-30秒
- 🎯 CPU优化：AVX2已启用

### 方案一：CUDA Toolkit（推荐，如果有NVIDIA显卡）
**前提条件**：
- 宿主机有NVIDIA显卡
- 配置VMware GPU直通

**安装步骤**：
1. 宿主机安装NVIDIA驱动
2. 配置VMware GPU直通
3. 虚拟机中安装CUDA Toolkit
4. 重新编译QMD：`qmd embed --gpu cuda`

**预期提升**：
- 首次生成：1-2分钟（提升50-60%）
- 增量更新：5-10秒（提升50%）

### 方案二：Vulkan支持（通用方案）
**前提条件**：
- 虚拟显卡支持Vulkan
- 或配置GPU直通

**安装步骤**：
1. 检查Vulkan支持：`vulkaninfo`
2. 安装Vulkan Runtime
3. 重新编译QMD：`qmd embed --gpu vulkan`

**预期提升**：
- 首次生成：2-3分钟（提升30-40%）
- 增量更新：8-15秒（提升30%）

### 建议
- **短期**：使用CPU模式（功能完全，收益够用）
- **长期**：如需性能优化，优先考虑CUDA（性能更好）

---

## 📊 Token节省策略

### 工作流优先级
1. **QMD搜索**（~50 tokens）
2. **Memory搜索**（~50 tokens）
3. **文件读取**（仅必要时，限制行数）

### 节省效果
- 传统方式：全量读取 ~2000 tokens
- QMD方式：搜索+片段 ~150 tokens
- **节省：92.5%**

### 搜索模式
| 模式 | 精度 | 速度 | 命令 |
|------|------|------|------|
| 关键词 | 中等 | 最快 | `qmd search` |
| 向量 | 59% | 快 | `qmd vsearch` |
| 混合 | 93% | 快 | `qmd query` |

---

## ⚠️ 注意事项

### 网络限制
- OpenAI API需要代理
- GitHub访问受限
- 使用国内镜像或本地工具

### 性能优化
- CPU模式可用但较慢
- 向量生成首次较慢，增量快
- 建议闲时生成向量

### 文件管理
- 知识库文件放 `knowledge/` 目录
- Daily logs放 `memory/` 目录
- 自动更新会索引新文件

---

**最后更新**：2026年2月27日 10:30
