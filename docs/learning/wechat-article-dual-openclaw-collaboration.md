# 微信文章学习笔记 - 双 OpenClaw 协作方案

**文章标题**：我装了个插件，让两个 OpenClaw 开始 24/7 搞事情了  
**作者**：HelloGitHub  
**来源**：https://mp.weixin.qq.com/s/aHgRVRdFmUR8Qnkh0cPuaA  
**学习时间**：2026-03-13 11:55  
**学习者**：小米辣（PM 代理）

---

## 🎯 核心需求

**场景**：创意策划和执行落地需要分开
- 创意阶段：需要天马行空
- 执行阶段：需要严谨细致
- 同一个 Agent 既发散又严谨，容易"精神分裂"

**解决方案**：让两个 OpenClaw 各干各的活，但又能无缝衔接 24/7 搞事情

---

## 🛠️ 技术方案：MemOS 插件

### 核心优势
1. **记忆共享**：两个 OpenClaw 访问同一个记忆池
2. **自动召回**：B 启动后自动检索 A 的产出
3. **自动写回**：产出自动保存，无需手动干预
4. **异步协作**：A 今天产出，B 明天接力

### 部署步骤

#### 1. 获取 MemOS API Key
- 访问：https://memos.openmem.net
- 格式：`mpg-...`

#### 2. 部署 OpenClaw A（创意策划）
```bash
# 创建配置目录并写入 API Key
mkdir -p ~/.openclaw && echo "MEMOS_API_KEY=mpg-your_key_here" > ~/.openclaw/.env

# 安装 OpenClaw
npm install -g openclaw@latest

# 初始化配置
openclaw onboard

# 安装 MemOS 插件
openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 重启 Gateway
openclaw gateway restart
```

#### 3. 部署 OpenClaw B（执行落地）
```bash
# 创建独立工作目录
mkdir -p ~/.openclaw-exec

# 复制配置（共享同一个 API Key）
cp ~/.openclaw/.env ~/.openclaw-exec/.env

# 用独立配置启动第二个实例
OPENCLAW_HOME=~/.openclaw-exec openclaw onboard --port 3001

# 安装 MemOS 插件
OPENCLAW_HOME=~/.openclaw-exec openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 重启 Gateway
OPENCLAW_HOME=~/.openclaw-exec openclaw gateway restart
```

#### 4. 自定义 user_id（可选）
```bash
# 在两个.env 文件中都添加
MEMOS_USER_ID=my-custom-user-id
```

---

## 📋 协作流程示例

### 场景：策划技术沙龙

#### 第一步：OpenClaw A 产出创意方案
```
用户 → OpenClaw A：帮我策划一场技术沙龙活动

结果：
- 活动主流程（时间、地点、议程）
- 招募文案（宣传语、报名方式）
- 自动写入 MemOS
```

#### 第二步：OpenClaw B 无缝接力
```
用户 → OpenClaw B：基于这个方案，产出物料清单和风险预案

MemOS → OpenClaw B：自动检索并注入 A 的产出

结果：
- 物料清单（与 A 的议程对应）
- 风险预案（场地、设备、人员）
- B 没有问什么活动，直接基于 A 的方案
```

#### 第三步：OpenClaw B Double-Check
```
用户 → OpenClaw B：检查整体方案是否有遗漏

结果：
- 方案完整性评估
- 改进建议
```

---

## 🔬 技术原理

### 1. 记忆隔离机制
```
user_id="openclaw-user"（默认配置）
├─ OpenClaw A 的对话记录和输出
├─ OpenClaw B 的对话记录和输出
└─ 所有共享的上下文
```

### 2. 召回机制
1. OpenClaw B 启动后，MemOS 自动分析用户问题意图
2. 去共享记忆池检索相关上下文
3. 精简后注入给 B 作为背景知识
4. B 基于 A 的产出继续工作

### 3. 写回机制
1. OpenClaw A 的产出自动写回 MemOS
2. OpenClaw B 的产出自动写回 MemOS
3. 自动分类和索引，支持后续检索

---

## ✅ 验证结果

**测试场景**：策划技术沙龙

**验证点**：
- ✅ B 没有问什么活动（理解上下文）
- ✅ B 直接基于 A 的方案做了后续补充
- ✅ B 的物料清单和 A 的议程完全对得上
- ✅ B 能 Double-Check 整体方案

**结论**：MemOS 的记忆检索和注入机制有效！

---

## 💡 适用场景

1. **多 OpenClaw 协作**：创意 + 执行、前端 + 后端、技术 + 运营
2. **异步工作流**：A 今天产出方案，B 明天接力执行
3. **多人项目**：我的 OpenClaw 负责一部分，同事的 OpenClaw 负责另一部分

---

## ⚠️ 改进空间

1. **权限控制**：目前不支持 A 可读 B，但 B 不可改 A 的细粒度权限
2. **检索精度**：复杂场景可能需要调整检索参数
3. **复用模板**：支持将案例提取成可复用模板

---

## 🔗 参考资源

- **MemOS 官网**：https://memos.openmem.net
- **GitHub**：https://github.com/MemTensor/MemOS
- **MemOS 插件**：https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin
- **OpenClaw 文档**：https://docs.openclaw.ai

---

## 📊 与飞书中继服务方案对比

| 维度 | MemOS 方案 | 飞书中继服务 |
|------|-----------|-------------|
| **部署复杂度** | ✅ 低（几小时） | ❌ 高（4 天） |
| **开发工作量** | ✅ 零开发 | ❌ 需要开发 |
| **记忆共享** | ✅ 自动 | ⚠️ 需开发 |
| **召回机制** | ✅ 自动 | ⚠️ 需开发 |
| **写回机制** | ✅ 自动 | ⚠️ 需开发 |
| **权限控制** | ❌ 不支持 | ✅ 可定制 |
| **检索精度** | ⚠️ 依赖算法 | ✅ 可定制 |
| **推荐度** | ✅ **强烈推荐** | ⚠️ 备选 |

---

**学习总结**：MemOS 方案简单、快速、已验证，强烈推荐！

*学习笔记整理时间：2026-03-13 11:55*
*整理者：小米辣（PM 代理）*
