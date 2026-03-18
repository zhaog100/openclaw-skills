# agent-collab-platform

**版本**：v1.15.1 ⭐⭐⭐⭐⭐  
**类型**：智能体协作平台  
**作者**：思捷娅科技  

---

## 📋 简介

agent-collab-platform是统一的智能体协作平台，采用**共享核心+特定模块**的架构设计，支持无限扩展智能体A、B、C、D...

---

## 🎯 核心特性

### 共享核心（90%代码复用）
- ✅ GitHub Issue自动监听
- ✅ 消息智能路由
- ✅ 状态统一管理
- ✅ Issue处理自动化

### 智能体模块
- **agent_a**（PM代理）：产品管理 + Review验证
- **agent_b**（Dev代理）：技术设计 + 开发实现 + 集成发布
- **agent_c/d/e**（未来）：继承基类即可

### Bounty Hunter模块
- **bounty_scanner**: 自动扫描GitHub/Algora bounty
- **bounty_batch_dev**: 批量并行开发，子代理调度
- **pr_monitor**: PR状态+付款监控

---

## 🚀 快速开始

### 安装
```bash
clawhub install agent-collab-platform
```

### 使用

#### 启动PM代理（小米辣）
```bash
cd skills/agent-collab-platform
./skill.sh agent_a
```

#### 启动Dev代理（小米粒）
```bash
cd skills/agent-collab-platform
./skill.sh agent_b
```

---

## 📊 架构优势

| 维度 | 独立技能包 | 统一平台 |
|------|----------|---------|
| 代码复用 | 10% | 90%+ ⭐ |
| 扩展成本 | 高 | 低 ⭐ |
| 维护成本 | 高 | 低 ⭐ |

---

## ⛔ 开发规范（子代理必读）

**重要**：spawn 子代理开发技能时，必须在 task prompt 中引用以下文件：

```
请先阅读 docs/DEVELOPMENT_LESSONS.md（经验教训库），严格遵守其中的所有要求。
```

核心要求摘要：
1. **不产生幻觉** — 每个步骤实际执行，不能假设结果
2. **严格测试** — pytest + 逐接口功能验证 + 边界测试
3. **先测后发** — 全绿 → 验证 → 发布 → 汇报（附数据）
4. **做完再汇报** — 不让官家追问，有问题自己发现修复
5. **不确认当没说** — 不确定时先问，明确的需求直接做

详细教训和验证标准见 `docs/DEVELOPMENT_LESSONS.md`

---

## 📄 许可证

MIT License - 免费使用、修改和重新分发

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)
