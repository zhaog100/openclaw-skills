# QMD部署所需配置指南

## 🚨 当前错误分析

### 已识别的问题
1. **sqlite-vec-win32-x64 404错误**
   - 包不存在或版本不兼容
2. **@node-llama-cpp/win-x64-cuda-ext 依赖问题**
   - GPU加速组件下载失败
3. **better-sqlite3 安装缓慢**
   - 编译时间长（31.9s + 1m2.1s）
4. **类型检查失败**
   - TypeScript 类型定义加载失败

## 🔧 解决方案

### 方案1：纯CPU模式（推荐）
```bash
# 清理当前安装
npm uninstall -g qmd

# 重新安装CPU版本
npm install -g qmd --cpu

# 或者指定具体版本
npm install -g qmd@latest --cpu
```

### 方案2：依赖修复
```bash
# 安装缺失的依赖
npm install -g sqlite3
npm install -g @types/sqlite3

# 重新安装QMD
npm install -g qmd --ignore-scripts
```

### 方案3：Docker部署
```bash
# 使用CPU版本的Docker
docker pull tobi/qmd:cpu-latest

# 运行容器
docker run -v ~/.qmd:/app/.qmd tobi/qmd:cpu-latest
```

## 📋 完整配置清单

### 1. 系统依赖检查
```bash
# 检查Node.js版本
node --version
npm --version
bun --version

# 检查系统环境
python --version  # needed for some dependencies
gcc --version     # needed for native modules
```

### 2. QMD核心安装
```bash
# 推荐安装顺序
npm install -g bun          # 如果尚未安装
bun install -g qmd --cpu   # CPU模式，避免GPU依赖问题

# 验证安装
qmd --version
qmd help
```

### 3. 模型下载（首次运行）
```bash
# 首次运行会自动下载模型
qmd serve

# 或手动下载模型
qmd download-model jina-embeddings-v3
qmd download-model jina-reranker-v2-base-multilingual
```

### 4. 知识库创建和配置
```bash
# 进入工作目录
cd /c/Users/zhaog/.openclaw/workspace

# 创建记忆库
qmd collection add memory/*.md --name daily-logs
qmd collection add *.md --name workspace

# 生成embeddings
qmd embed daily-logs memory/*.md
qmd embed workspace *.md

# 验证collections
qmd list
```

### 5. MCP服务器配置
**配置文件已存在**：`config/mcporter.json`

```json
{
  "mcpServers": {
    "qmd": {
      "command": "qmd",
      "args": ["mcp"]
    }
  }
}
```

### 6. OpenClaw集成配置
需要在OpenClaw配置中启用MCP集成：

```json
{
  "mcp": {
    "enabled": true,
    "servers": {
      "qmd": {
        "command": "qmd",
        "args": ["mcp"]
      }
    }
  }
}
```

## 🎯 必需的配置步骤

### 步骤1：解决依赖问题
```bash
# 清理npm缓存
npm cache clean --force

# 重新安装QMD CPU版本
npm uninstall -g qmd
npm install -g qmd@latest --cpu --ignore-scripts
```

### 步骤2：验证基础功能
```bash
# 测试基础命令
qmd --version
qmd help

# 测试创建collection
qmd collection add README.md --name test

# 测试搜索
qmd search test "README" --hybrid
```

### 步骤3：创建知识库
```bash
# 创建日常记忆库
qmd collection add memory/*.md --name daily-logs
qmd embed daily-logs memory/*.md

# 创建工作空间库
qmd collection add *.md --name workspace  
qmd embed workspace *.md
```

### 步骤4：测试MCP集成
```bash
# 测试MCP服务器
qmd mcp

# 或通过OpenClaw测试
# 在对话中使用qmd搜索功能
```

## 📁 配置文件清单

### 必需文件
- ✅ `config/mcporter.json` - MCP服务器配置
- ✅ `memory/` - 日常记忆文档
- ✅ `knowledge/` - 知识库文档
- ✅ `QMD配置指南.md` - 详细配置文档

### 可选但推荐
- ❌ `heartbeat.md` - 自动维护任务（待创建）
- ❌ `qmd-maintenance.sh` - 维护脚本（待创建）

## ⚠️ 常见问题和解决方案

### 问题1：Node.js版本不兼容
**解决方案**：
```bash
# 使用nvm管理Node版本
nvm install 18.18.0  # 推荐LTS版本
nvm use 18.18.0
```

### 问题2：模型下载失败
**解决方案**：
```bash
# 手动下载模型
wget https://github.com/elastic/eland/raw/main/examples/llm/q2_K/m/7B/0.2.1/ggml-model-q4_0.gguf
# 将模型放到qmd模型目录
mkdir -p ~/.qmd/models
cp *.gguf ~/.qmd/models/
```

### 问题3：搜索结果不理想
**解决方案**：
```bash
# 重新生成embeddings
qmd embed daily-logs memory/*.md

# 调整搜索参数
qmd search daily-logs "关键词" --hybrid --limit 5
```

## 🚀 完成部署检查清单

### 环境配置
- [ ] Node.js 18+ LTS版本
- [ ] npm 或 bun 包管理器
- [ ] qmd 二进制文件可用
- [ ] 系统磁盘空间 > 2GB（模型文件）

### 核心功能
- [ ] qmd --version 成功
- [ ] qmd help 命令可用
- [ ] 能创建和列出collections
- [ ] 能执行搜索命令

### 知识库
- [ ] daily-logs collection 创建成功
- [ ] workspace collection 创建成功
- [ ] embeddings 生成完成
- [ ] 搜索功能正常工作

### MCP集成
- [ ] mcporter.json 配置正确
- [ ] MCP服务器启动成功
- [ ] OpenClaw 能调用qmd工具

## 🎉 部署完成后

### 验证命令
```bash
# 1. 基础功能测试
qmd --version
qmd list

# 2. 搜索功能测试
qmd search daily-logs "项目管理" --hybrid

# 3. MCP功能测试
# 在OpenClaw中询问：请搜索记忆中的项目管理相关内容

# 4. 性能测试
# 对比使用qmd前后的Token消耗
```

### 自动化维护
建议添加到heartbeat任务：
```markdown
# 在 heartbeat.md 中添加
- [ ] qmd embed daily-logs memory/*.md
- [ ] qmd embed workspace *.md  
- [ ] qmd list --status
```

---

*配置指南创建时间：2026年2月25日*
*预计完成时间：15-30分钟*