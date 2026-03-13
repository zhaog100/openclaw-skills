# 技术设计文档 - demo-skill

**创建时间**：2026-03-12 11:32
**创建者**：小米辣
**版本**：v1.0.0
**Issue**：#2

---

## 📋 设计概述

**目标**：创建一个演示双米粒协作系统完整流程的技能

**技术栈**：
- Bash 4.0+
- Git（版本管理演示）
- 无外部依赖
- 纯本地执行

---

## 🏗️ 架构设计

### 文件结构

```
skills/demo-skill/
├── SKILL.md              # 技能说明（ClawHub必需）
├── README.md             # 详细文档
├── package.json          # 元信息
├── demo-skill.sh         # 主脚本（核心实现）
├── install.sh            # 安装脚本
└── test/
    └── test.sh           # 测试脚本（覆盖率>80%）
```

### 核心组件

1. **demo-skill.sh** - 主脚本
   - 命令解析
   - 功能路由
   - 错误处理

2. **install.sh** - 安装脚本
   - 权限设置
   - 路径配置
   - 依赖检查

3. **test.sh** - 测试脚本
   - 单元测试
   - 集成测试
   - 覆盖率报告

---

## 🔧 功能设计

### 1. demo-skill（默认命令）

**功能**：显示欢迎信息和可用命令

**实现**：
```bash
show_welcome() {
    cat << 'EOF'
🌾 demo-skill - 双米粒协作系统演示
========================================

欢迎体验双米粒协作系统！

【可用命令】
  demo-skill         显示此欢迎信息
  demo-skill status  显示系统状态
  demo-skill info    显示技能信息
  demo-skill help    显示帮助文档

【协作流程】
  1. 小米辣创建PRD → 2. 小米辣技术设计 → 3. 小米辣开发 →
  4. 双向Review → 5. 发布到ClawHub

【版本】v1.0.0
【创建者】小米辣
EOF
}
```

**验收标准**：
- ✅ 显示欢迎信息
- ✅ 显示4个可用命令
- ✅ 显示协作流程
- ✅ 响应时间 < 1秒

---

### 2. demo-skill status

**功能**：显示双米粒协作系统状态

**实现**：
```bash
show_status() {
    echo "📊 双米粒协作系统状态"
    echo "========================================"
    echo ""

    # 检查Git状态
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "✅ Git仓库：正常"
        echo "   分支：$(git branch --show-current)"
        echo "   提交：$(git log -1 --oneline)"
    else
        echo "❌ Git仓库：未找到"
    fi

    echo ""

    # 检查GitHub CLI
    if command -v gh &> /dev/null; then
        echo "✅ GitHub CLI：正常"
        echo "   版本：$(gh --version | head -1)"
    else
        echo "⚠️  GitHub CLI：未安装"
    fi

    echo ""

    # 检查ClawHub CLI
    if command -v clawhub &> /dev/null; then
        echo "✅ ClawHub CLI：正常"
    else
        echo "⚠️  ClawHub CLI：未安装"
    fi

    echo ""
    echo "【协作流程】"
    echo "  1. ✅ 小米辣完成PRD"
    echo "  2. ⏳ 小米辣技术设计（当前）"
    echo "  3. ⏳ 小米辣开发实现"
    echo "  4. ⏳ 双向Review"
    echo "  5. ⏳ 发布到ClawHub"
}
```

**验收标准**：
- ✅ 显示Git状态
- ✅ 显示GitHub CLI状态
- ✅ 显示ClawHub CLI状态
- ✅ 显示协作流程进度

---

### 3. demo-skill info

**功能**：显示技能元信息

**实现**：
```bash
show_info() {
    cat << 'EOF'
📦 demo-skill 技能信息
========================================

【基本信息】
  名称：demo-skill
  版本：v1.0.0
  创建者：小米辣
  创建时间：2026-03-12

【技术栈】
  语言：Bash 4.0+
  依赖：无（纯本地执行）
  网络：无需网络请求

【功能列表】
  1. demo-skill         显示欢迎信息
  2. demo-skill status  显示系统状态
  3. demo-skill info    显示技能信息
  4. demo-skill help    显示帮助文档

【发布信息】
  ClawHub ID：待发布
  GitHub Issue：#2

【许可证】
  MIT License
EOF
}
```

**验收标准**：
- ✅ 显示基本信息
- ✅ 显示技术栈
- ✅ 显示功能列表
- ✅ 显示发布信息

---

### 4. demo-skill help

**功能**：显示详细帮助和协作流程

**实现**：
```bash
show_help() {
    cat << 'EOF'
📚 demo-skill 帮助文档
========================================

【命令详解】

1. demo-skill
   功能：显示欢迎信息和可用命令
   示例：demo-skill
   输出：欢迎信息 + 4个可用命令

2. demo-skill status
   功能：显示双米粒协作系统状态
   示例：demo-skill status
   输出：
     - Git仓库状态
     - GitHub CLI状态
     - ClawHub CLI状态
     - 协作流程进度

3. demo-skill info
   功能：显示技能元信息
   示例：demo-skill info
   输出：
     - 基本信息（名称、版本、创建者）
     - 技术栈（语言、依赖、网络）
     - 功能列表
     - 发布信息

4. demo-skill help
   功能：显示此帮助文档
   示例：demo-skill help
   输出：详细帮助 + 协作流程

---

【双米粒协作流程】

步骤1️⃣  小米辣创建PRD
  - 编写产品需求文档
  - 创建GitHub Issue
  - Git提交并推送

步骤2️⃣  小米辣技术设计
  - 查询Issue
  - 创建技术设计文档
  - 评论Issue（技术设计完成）

步骤3️⃣  小米辣开发实现
  - 编写代码
  - 编写测试
  - 自检（质疑清单）

步骤4️⃣  双向Review
  - 小米辣12维度Review
  - 小米辣回应质疑
  - 小米辣5层验收

步骤5️⃣  发布到ClawHub
  - 小米辣发布
  - 生成Package ID
  - 关闭Issue

---

【技术架构】

┌─────────────────┐
│   demo-skill    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───┴───┐ ┌───┴───┐
│ Bash  │ │  Git  │
└───────┘ └───────┘

【无外部依赖】
- ❌ API Key
- ❌ 网络请求
- ❌ 数据库
- ❌ 第三方库

---

【常见问题】

Q1: 这个技能有什么用？
A1: 演示双米粒协作系统的完整工作流程

Q2: 需要配置什么？
A2: 无需配置，开箱即用

Q3: 支持哪些平台？
A3: Linux/macOS（Bash 4.0+）

Q4: 如何安装？
A4: clawhub install demo-skill

---

【联系方式】

GitHub Issue：https://github.com/zhaog100/openclaw-skills/issues/2
创建者：小米辣
创建时间：2026-03-12
EOF
}
```

**验收标准**：
- ✅ 显示命令详解
- ✅ 显示协作流程（5步）
- ✅ 显示技术架构
- ✅ 显示常见问题

---

## 🧪 测试设计

### 测试策略

1. **单元测试**（60%覆盖率）
   - 测试每个函数
   - 测试命令解析
   - 测试错误处理

2. **集成测试**（20%覆盖率）
   - 测试完整命令流程
   - 测试Git集成
   - 测试输出格式

3. **端到端测试**（20%覆盖率）
   - 测试实际使用场景
   - 测试性能指标
   - 测试用户体验

### 测试用例

```bash
# 测试1：默认命令
test_welcome() {
    output=$(./demo-skill.sh)
    assert_contains "$output" "欢迎体验双米粒协作系统"
    assert_contains "$output" "demo-skill status"
}

# 测试2：status命令
test_status() {
    output=$(./demo-skill.sh status)
    assert_contains "$output" "Git仓库"
    assert_contains "$output" "GitHub CLI"
}

# 测试3：info命令
test_info() {
    output=$(./demo-skill.sh info)
    assert_contains "$output" "v1.0.0"
    assert_contains "$output" "小米辣"
}

# 测试4：help命令
test_help() {
    output=$(./demo-skill.sh help)
    assert_contains "$output" "双米粒协作流程"
    assert_contains "$output" "步骤1"
}

# 测试5：性能测试
test_performance() {
    start=$(date +%s%N)
    ./demo-skill.sh > /dev/null
    end=$(date +%s%N)
    duration=$(( (end - start) / 1000000 ))
    assert_less_than $duration 1000  # < 1秒
}
```

---

## 📊 性能指标

| 指标 | 目标 | 度量方法 |
|------|------|---------|
| **响应时间** | < 1秒 | date +%s%N |
| **内存占用** | < 10MB | ps aux |
| **CPU占用** | < 5% | top |
| **测试覆盖率** | > 80% | 自定义脚本 |

---

## 🔒 安全考虑

1. **输入验证**
   - 验证命令参数
   - 防止注入攻击
   - 限制输出长度

2. **权限控制**
   - 只读操作
   - 无文件修改
   - 无网络请求

3. **错误处理**
   - 友好错误信息
   - 日志记录
   - 异常捕获

---

## 📦 发布计划

### Phase 1: 技术设计（当前）
- [x] 创建技术设计文档
- [ ] 评论Issue #2
- [ ] Git提交

### Phase 2: 开发实现
- [ ] 编写主脚本
- [ ] 编写安装脚本
- [ ] 编写测试脚本
- [ ] 自检（质疑清单）

### Phase 3: Review验收
- [ ] 小米辣Review
- [ ] 回应质疑
- [ ] 小米辣验收

### Phase 4: 发布上线
- [ ] 发布到ClawHub
- [ ] 生成Package ID
- [ ] 关闭Issue #2

---

## ✅ 验收标准清单

### 功能验收
- [ ] 所有4个命令正常工作
- [ ] 输出格式正确
- [ ] 错误处理完善

### 性能验收
- [ ] 响应时间 < 1秒
- [ ] 内存占用 < 10MB
- [ ] CPU占用 < 5%

### 质量验收
- [ ] 测试覆盖率 > 80%
- [ ] SKILL.md完整
- [ ] README.md清晰
- [ ] 通过ClawHub安全扫描

### 文档验收
- [ ] 代码注释完整
- [ ] 使用说明清晰
- [ ] 示例代码正确

---

*设计时间：2026-03-12 11:32*
*设计者：小米辣*
*版本：v1.0.0*
*Issue：#2*
