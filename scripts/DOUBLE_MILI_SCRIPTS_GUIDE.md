# 双米粒协作脚本使用指南

**版本**：v2.0
**创建时间**：2026-03-11 23:35

---

## 📋 脚本说明

### **小米粒脚本**（xiaomi_dev_v2.sh）
**职责**：开发 + 集成 + 发布
**协作对象**：米粒儿（产品+测试+客户）

### **米粒儿脚本**（mili_product_v2.sh）
**职责**：产品 + 测试 + 客户
**协作对象**：小米粒（开发+集成+发布）

---

## 🚀 快速开始

### **1. 米粒儿创建产品构思**

```bash
# 进入工作目录
cd /root/.openclaw/workspace

# 创建产品构思
bash scripts/mili_product_v2.sh create test-product

# 这会创建：
# - products/test-product-concept.md（产品构思文档）
# - GitHub Issue（讨论产品）
```

### **2. 小米粒分析产品构思**

```bash
# 小米粒分析产品构思
bash scripts/xiaomi_dev_v2.sh analyze test-product

# 这会创建：
# - tech_analysis_test-product.md（技术分析）
# - 回复GitHub Issue（技术建议）
```

### **3. 双方讨论**

```bash
# 在GitHub Issues中讨论
# 米粒儿和小米粒通过回复Issue进行讨论
# 讨论内容包括：
# - 产品视角（米粒儿）
# - 技术视角（小米粒）
# - 最终方案（综合）
```

### **4. 小米粒技术实现**

```bash
# 小米粒实现功能
bash scripts/xiaomi_dev_v2.sh implement test-product

# 这会创建：
# - feature/test-product分支
# - skills/test-product/目录
# - SKILL.md、package.json、scripts/
# - 通知米粒儿验收
```

### **5. 米粒儿质量验收**

```bash
# 米粒儿进行5层质量验收
bash scripts/mili_product_v2.sh review test-product

# 验收5层：
# - Layer 1: 需求完整性
# - Layer 2: 设计合理性
# - Layer 3: 代码质量
# - Layer 4: 功能完整性
# - Layer 5: 用户体验
```

### **6. 米粒儿批准发布**

```bash
# 验收通过后，批准发布
bash scripts/mili_product_v2.sh approve test-product

# 这会：
# - 创建发布批准文件
# - 通知小米粒发布
```

### **7. 小米粒发布到ClawHub**

```bash
# 小米粒发布到ClawHub
bash scripts/xiaomi_dev_v2.sh publish test-product

# 这会：
# - 合并到master分支
# - 发布到ClawHub
# - 推送到GitHub
# - 关闭GitHub Issue
```

---

## 📊 完整流程示例

```bash
# ========== 米粒儿操作 ==========

# 1. 创建产品构思
bash scripts/mili_product_v2.sh create my-awesome-tool

# 2. 分析小米粒的技术方案
bash scripts/mili_product_v2.sh analyze my-awesome-tool

# 3. 在GitHub Issues中讨论
# ...

# ========== 小米粒操作 ==========

# 4. 分析产品构思
bash scripts/xiaomi_dev_v2.sh analyze my-awesome-tool

# 5. 技术实现
bash scripts/xiaomi_dev_v2.sh implement my-awesome-tool

# 6. 等待米粒儿验收
# ...

# ========== 米粒儿操作 ==========

# 7. 5层质量验收
bash scripts/mili_product_v2.sh review my-awesome-tool

# 8. 批准发布
bash scripts/mili_product_v2.sh approve my-awesome-tool

# ========== 小米粒操作 ==========

# 9. 发布到ClawHub
bash scripts/xiaomi_dev_v2.sh publish my-awesome-tool

# ✅ 完成！
```

---

## 🛠️ 脚本命令详解

### **小米粒脚本**（xiaomi_dev_v2.sh）

```bash
# 分析产品构思
bash scripts/xiaomi_dev_v2.sh analyze <产品名称>
# - 读取产品构思文档
# - 进行技术分析
# - 创建技术分析文档
# - 回复GitHub Issue

# 技术实现
bash scripts/xiaomi_dev_v2.sh implement <产品名称>
# - 创建feature分支
# - 创建技能目录
# - 编写代码
# - 提交到GitHub
# - 通知米粒儿验收

# 发布到ClawHub
bash scripts/xiaomi_dev_v2.sh publish <产品名称>
# - 检查发布批准
# - 合并到master
# - 发布到ClawHub
# - 推送到GitHub
# - 通知米粒儿发布完成

# 完整流程（分析+实现）
bash scripts/xiaomi_dev_v2.sh all <产品名称>
```

---

### **米粒儿脚本**（mili_product_v2.sh）

```bash
# 创建产品构思
bash scripts/mili_product_v2.sh create <产品名称>
# - 创建产品构思文档
# - 创建GitHub Issue
# - 提交到GitHub

# 分析技术方案
bash scripts/mili_product_v2.sh analyze <产品名称>
# - 读取小米粒的技术分析
# - 从产品视角分析
# - 创建综合方案
# - 回复GitHub Issue

# 5层质量验收
bash scripts/mili_product_v2.sh review <产品名称>
# - Layer 1: 需求完整性
# - Layer 2: 设计合理性
# - Layer 3: 代码质量
# - Layer 4: 功能完整性
# - Layer 5: 用户体验
# - 创建验收文档
# - 提交到GitHub

# 批准发布
bash scripts/mili_product_v2.sh approve <产品名称>
# - 创建发布批准文件
# - 通知小米粒发布

# 完整流程（创建构思）
bash scripts/mili_product_v2.sh all <产品名称>
```

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── scripts/
│   ├── xiaomi_dev_v2.sh          # 小米粒脚本
│   └── mili_product_v2.sh        # 米粒儿脚本
│
├── products/                      # 米粒儿的产品构思
│   └── xxx-concept.md
│
├── skills/                        # 小米粒的实现
│   └── xxx/
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/
│
├── reviews/                       # 米粒儿的验收文档
│   └── xxx_review_YYYYMMDD_HHMMSS.md
│
├── issues/                        # GitHub Issue跟踪
│   ├── current_issue.txt
│   └── publish_approved.txt
│
└── docs/
    ├── DOUBLE_MILI_COLLABORATION_V2.md
    ├── DOUBLE_MILI_SCRIPTS_GUIDE.md（本文档）
    └── FORUM_RESEARCH_MULTI_AGENT.md
```

---

## 🎯 协作流程图

```
米粒儿                          小米粒
  │                              │
  ├─1. create产品构思            │
  │                              │
  ├─2. analyze技术方案 ←─────────┤
  │                              │
  ├─3. GitHub Issues讨论 ───────→│
  │                              │
  ├─4. 综合方案 ←────────────────┤
  │                              │
  │                              ├─5. implement技术实现
  │                              │
  ├─6. review验收 ←──────────────┤
  │                              │
  ├─7. approve批准发布           │
  │                              │
  │                              ├─8. publish发布
  │                              │
  └─✅ 完成                      └─✅ 完成
```

---

## 💡 使用技巧

### **1. 使用GitHub Issues讨论**
- 所有讨论都在GitHub Issues中进行
- 可追溯、可搜索、可关联
- 自动关闭Issue

### **2. 5层质量验收**
- 逐层验收，确保质量
- 每层都有检查清单
- 验收不通过则返回修改

### **3. 无状态协作**
- 每次都从GitHub同步最新状态
- 不需要维护复杂的状态
- 简单可靠

### **4. 自动通知**
- 关键步骤自动通知对方
- GitHub Issue自动回复
- 清晰的协作流程

---

## 🚨 注意事项

### **1. Git配置**
确保Git已配置：
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### **2. GitHub CLI**
建议安装GitHub CLI：
```bash
# Ubuntu/Debian
sudo apt install gh

# 登录
gh auth login
```

### **3. ClawHub CLI**
确保ClawHub CLI已安装：
```bash
clawhub --version
```

### **4. 分支管理**
- feature分支：开发中
- master分支：正式发布
- 每个产品一个feature分支

---

## 📊 协作统计

可以使用以下命令统计协作情况：

```bash
# 查看所有产品构思
ls products/

# 查看所有实现
ls skills/

# 查看所有验收文档
ls reviews/

# 查看GitHub Issues
gh issue list

# 查看发布状态
clawhub list
```

---

## 🎉 完成标志

当看到以下输出时，表示协作完成：

```
[米粒儿] ✅ 发布完成！
[小米粒] ✅ 已发布到ClawHub
[米粒儿] 感谢小米粒的专业实现！🎉
```

---

**官家，双米粒协作脚本使用指南完成！** 🌾✅

---

*最后更新：2026-03-11 23:35*
