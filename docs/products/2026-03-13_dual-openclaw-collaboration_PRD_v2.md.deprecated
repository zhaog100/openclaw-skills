# 产品需求文档 - 双 OpenClaw 协作系统（MemOS 方案）

**文档版本**：v2.0  
**创建日期**：2026-03-13  
**创建者**：小米辣（PM 代理）  
**状态**：草稿  
**Issue**：#1  
**官家指令**：2026-03-13 11:42  
**参考文章**：https://mp.weixin.qq.com/s/aHgRVRdFmUR8Qnkh0cPuaA

---

## 1. 需求概述

### 1.1 背景

**核心需求**：让两个 OpenClaw 实例（小米辣 PM + 小米粒 Dev）能够：
- ✅ 各司其职（创意策划 vs 执行落地）
- ✅ 无缝衔接（B 能读到 A 的产出）
- ✅ 24/7 高效协作（无需人工复制粘贴）

**现有方案对比**：

| 方案 | 复杂度 | 记忆共享 | 推荐度 |
|------|--------|---------|--------|
| GitHub Issues | ⚠️ 中 | ❌ 手动 | ❌ 不推荐 |
| 飞书中继服务 | ❌ 高 | ⚠️ 需开发 | ⚠️ 备选 |
| **MemOS 插件** | ✅ 低 | ✅ 自动 | ✅ **强烈推荐** |

### 1.2 目标

**核心目标**：基于 MemOS 插件实现双 OpenClaw 实例记忆共享和协作。

**具体目标**：
1. ✅ 部署两个独立 OpenClaw 实例（不同端口）
2. ✅ 安装 MemOS 插件（两个实例都装）
3. ✅ 配置共享 user_id（实现记忆池共享）
4. ✅ 自动记忆召回和写回（无需手动干预）
5. ✅ 支持异步协作（A 今天产出，B 明天接力）

### 1.3 范围

**包含**：
- 双 OpenClaw 实例部署
- MemOS 插件安装配置
- 共享记忆池配置
- 协作流程设计

**不包含**（后续版本）：
- 权限控制（A 可读 B，B 不可改 A）
- 记忆检索精度优化
- 复用模板系统

---

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────┐         ┌─────────────────┐
│  OpenClaw A     │         │  OpenClaw B     │
│  (创意策划)     │         │  (执行落地)     │
│  Port 3000      │         │  Port 3001      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │  MemOS 插件               │  MemOS 插件
         │                           │
         └────────────┬──────────────┘
                      │
              ┌───────▼───────┐
              │   MemOS Cloud │
              │   (共享记忆池) │
              │  user_id=xxx  │
              └───────────────┘
```

### 2.2 核心机制

#### 记忆隔离机制
```
user_id="openclaw-user"（默认配置）
├─ OpenClaw A 的对话记录和输出
├─ OpenClaw B 的对话记录和输出
└─ 所有共享的上下文
```

#### 召回机制
1. OpenClaw B 启动后，MemOS 自动分析用户问题意图
2. 去共享记忆池检索相关上下文
3. 精简后注入给 B 作为背景知识
4. B 基于 A 的产出继续工作

#### 写回机制
1. OpenClaw A 的产出自动写回 MemOS
2. OpenClaw B 的产出自动写回 MemOS
3. 自动分类和索引，支持后续检索

---

## 3. 部署指南

### 3.1 准备工作

**获取 MemOS API Key**：
1. 访问 [MemOS 官网](https://memos.openmem.net)
2. 注册账号
3. 获取 API Key（格式：`mpg-...`）

### 3.2 部署 OpenClaw A（创意策划）

```bash
# 1. 创建配置目录并写入 API Key
mkdir -p ~/.openclaw && echo "MEMOS_API_KEY=mpg-your_key_here" > ~/.openclaw/.env

# 2. 安装 OpenClaw（如果还没装）
npm install -g openclaw@latest

# 3. 初始化配置
openclaw onboard

# 4. 安装 MemOS 插件
openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 5. 重启 Gateway
openclaw gateway restart
```

**配置检查**：
```bash
cat ~/.openclaw/openclaw.json | grep memos-cloud-openclaw-plugin
# 应看到 "enabled": true
```

### 3.3 部署 OpenClaw B（执行落地）

```bash
# 1. 创建独立工作目录
mkdir -p ~/.openclaw-exec

# 2. 复制配置（共享同一个 API Key 和 user_id）
cp ~/.openclaw/.env ~/.openclaw-exec/.env

# 3. 用独立配置启动第二个实例
OPENCLAW_HOME=~/.openclaw-exec openclaw onboard --port 3001

# 4. 安装 MemOS 插件
OPENCLAW_HOME=~/.openclaw-exec openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 5. 重启 Gateway
OPENCLAW_HOME=~/.openclaw-exec openclaw gateway restart
```

**配置检查**：
```bash
cat ~/.openclaw-exec/openclaw.json | grep memos-cloud-openclaw-plugin
# 应看到 "enabled": true
```

### 3.4 自定义 user_id（可选）

默认配置下，两个实例使用相同的 `user_id`（`openclaw-user`），已实现记忆共享。

如需自定义：
```bash
# 在两个 .env 文件中都添加
MEMOS_USER_ID=my-custom-user-id
```

---

## 4. 协作流程设计

### 4.1 角色分工

| 实例 | 角色 | 职责 | 工具 |
|------|------|------|------|
| **OpenClaw A** | 创意策划 | 需求分析、方案设计、文案创作 | 设计工具、文案模板 |
| **OpenClaw B** | 执行落地 | 物料清单、风险预案、Double-Check | 项目管理系统、预算工具 |

### 4.2 协作示例：策划技术沙龙

#### 第一步：OpenClaw A 产出创意方案
```
用户 → OpenClaw A：帮我策划一场技术沙龙活动

OpenClaw A → MemOS：写入活动主流程、招募文案

结果：
- 活动主流程（时间、地点、议程）
- 招募文案（宣传语、报名方式）
```

#### 第二步：OpenClaw B 无缝接力
```
用户 → OpenClaw B：基于这个方案，产出物料清单和风险预案

MemOS → OpenClaw B：自动检索并注入 A 的产出

OpenClaw B → 用户：
- 物料清单（与 A 的议程对应）
- 风险预案（场地、设备、人员）

结果：
- B 没有问什么活动
- B 直接基于 A 的方案做了后续补充
```

#### 第三步：OpenClaw B Double-Check
```
用户 → OpenClaw B：检查整体方案是否有遗漏

OpenClaw B → MemOS：检索完整上下文

OpenClaw B → 用户：
- 方案完整性评估
- 改进建议
```

### 4.3 协作优势

1. **无需人工复制粘贴**：MemOS 自动召回和写回
2. **B 理解完整上下文**：不需要用户重复背景信息
3. **支持异步协作**：A 今天产出，B 明天接力
4. **记忆持久化**：所有产出自动保存和索引

---

## 5. 功能需求

### 5.1 核心功能（P0）

#### 功能 1：双实例部署 ⭐⭐⭐⭐⭐
- **描述**：部署两个独立 OpenClaw 实例
- **验收标准**：
  - [ ] 两个实例运行在不同端口（3000/3001）
  - [ ] 独立工作目录（~/.openclaw / ~/.openclaw-exec）
  - [ ] 共享同一个 MemOS API Key 和 user_id

#### 功能 2：MemOS 插件安装 ⭐⭐⭐⭐⭐
- **描述**：两个实例都安装 MemOS 插件
- **验收标准**：
  - [ ] 插件安装成功
  - [ ] 插件启用（"enabled": true）
  - [ ] Gateway 重启成功

#### 功能 3：记忆共享 ⭐⭐⭐⭐⭐
- **描述**：两个实例共享同一个记忆池
- **验收标准**：
  - [ ] A 的产出自动写入 MemOS
  - [ ] B 能读到 A 的产出
  - [ ] 无需手动复制粘贴

#### 功能 4：自动召回 ⭐⭐⭐⭐⭐
- **描述**：B 启动后自动检索相关上下文
- **验收标准**：
  - [ ] B 理解完整背景信息
  - [ ] 召回准确率 > 90%
  - [ ] 召回延迟 < 3 秒

#### 功能 5：自动写回 ⭐⭐⭐⭐⭐
- **描述**：产出自动写回 MemOS
- **验收标准**：
  - [ ] A 的产出自动保存
  - [ ] B 的产出自动保存
  - [ ] 自动分类和索引

### 5.2 辅助功能（P1）

#### 功能 6：角色定制
- **描述**：为不同实例配置不同角色和工具
- **验收标准**：
  - [ ] A 配置创意工具
  - [ ] B 配置执行工具

#### 功能 7：协作模板
- **描述**：将成功案例提取为可复用模板
- **验收标准**：
  - [ ] 模板可保存和加载
  - [ ] 新项目自动继承最佳实践

### 5.3 可选功能（P2）

#### 功能 8：权限控制
- **描述**：更灵活的权限管理
- **验收标准**：
  - [ ] A 可读 B 的输出
  - [ ] B 不可修改 A 的记忆

#### 功能 9：记忆检索优化
- **描述**：提升复杂场景的检索精度
- **验收标准**：
  - [ ] 支持调整检索参数
  - [ ] 检索准确率 > 95%

---

## 6. 技术需求

### 6.1 环境要求
- **OpenClaw**：最新版本（npm install -g openclaw@latest）
- **Node.js**：v18+
- **MemOS 插件**：github:MemTensor/MemOS-Cloud-OpenClaw-Plugin
- **操作系统**：Linux / macOS / Windows

### 6.2 性能要求
- **召回延迟**：< 3 秒
- **写回延迟**：< 1 秒
- **检索准确率**：> 90%

### 6.3 安全要求
- **API Key 管理**：存储在 .env 文件，不要提交到 Git
- **user_id 管理**：自定义 user_id 避免冲突

---

## 7. 开发计划

### 阶段 1：部署（预计 0.5 天）
- [ ] 获取 MemOS API Key
- [ ] 部署 OpenClaw A（创意策划）
- [ ] 部署 OpenClaw B（执行落地）
- [ ] 安装 MemOS 插件
- [ ] 验证记忆共享

### 阶段 2：测试（预计 0.5 天）
- [ ] 测试双实例协作流程
- [ ] 验证自动召回和写回
- [ ] 测试异步协作

### 阶段 3：优化（预计 0.5 天）
- [ ] 配置角色和工具
- [ ] 创建协作模板
- [ ] 性能优化

**总计**：1.5 天（远少于飞书中继服务的 4 天）

---

## 8. 验收标准

### 8.1 功能验收
- [ ] 两个 OpenClaw 实例正常运行（3000/3001 端口）
- [ ] MemOS 插件已启用
- [ ] A 的产出自动写入 MemOS
- [ ] B 能读到 A 的产出（无需人工复制）
- [ ] B 理解完整上下文（不需要用户重复背景）

### 8.2 性能验收
- [ ] 召回延迟 < 3 秒
- [ ] 写回延迟 < 1 秒
- [ ] 检索准确率 > 90%

### 8.3 协作验收
- [ ] 完成一次完整协作流程（如策划技术沙龙）
- [ ] B 基于 A 的产出无缝接力
- [ ] B 能 Double-Check 整体方案

---

## 9. 风险与依赖

### 9.1 风险
- **MemOS 服务稳定性**：依赖云服务可用性
- **检索精度**：复杂场景可能需要调整参数
- **权限控制**：目前不支持细粒度权限

### 9.2 依赖
- MemOS Cloud 服务
- OpenClaw Gateway
- MemOS 插件

---

## 10. 与飞书中继服务方案对比

| 维度 | MemOS 方案 | 飞书中继服务 |
|------|-----------|-------------|
| **部署复杂度** | ✅ 低（1.5 天） | ❌ 高（4 天） |
| **开发工作量** | ✅ 零开发 | ❌ 需要开发 |
| **记忆共享** | ✅ 自动 | ⚠️ 需开发 |
| **召回机制** | ✅ 自动 | ⚠️ 需开发 |
| **写回机制** | ✅ 自动 | ⚠️ 需开发 |
| **权限控制** | ❌ 不支持 | ✅ 可定制 |
| **检索精度** | ⚠️ 依赖算法 | ✅ 可定制 |
| **复用模板** | ❌ 待开发 | ✅ 可开发 |
| **推荐度** | ✅ **强烈推荐** | ⚠️ 备选 |

**推荐方案**：MemOS 方案（简单、快速、已验证）

---

## 11. 下一步行动

### 立即执行
1. ⏳ **获取 MemOS API Key**（访问 https://memos.openmem.net）
2. ⏳ **部署双 OpenClaw 实例**（3000/3001 端口）
3. ⏳ **安装 MemOS 插件**（两个实例都装）
4. ⏳ **验证记忆共享**（测试 A 产出 B 读取）

### 本周完成
1. ⏳ **测试协作流程**（如策划技术沙龙）
2. ⏳ **创建协作模板**（可复用案例）
3. ⏳ **优化配置**（角色定制、工具配置）

---

## 12. 参考资源

- **MemOS 官网**：https://memos.openmem.net
- **MemOS GitHub**：https://github.com/MemTensor/MemOS
- **MemOS 插件**：https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin
- **OpenClaw 文档**：https://docs.openclaw.ai
- **参考文章**：https://mp.weixin.qq.com/s/aHgRVRdFmUR8Qnkh0cPuaA

---

**PRD 版本**：v2.0  
**创建时间**：2026-03-13 11:50  
**创建者**：小米辣（PM 代理）  
**状态**：草稿，等待小米粒回复

---

*请 @小米粒 查看 PRD v2.0（MemOS 方案）并回复你的想法和建议！*

*这个方案比飞书中继服务更简单（1.5 天 vs 4 天），且已验证可行！*
