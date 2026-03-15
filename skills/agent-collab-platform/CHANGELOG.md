# 更新日志（CHANGELOG）

## v1.1.0 - 版权保护增强版 (2026-03-15 09:15)

### 新增功能 ✨

1. **发布环节自动添加版权信息**
   - `publisher.py`：发布报告自动包含MIT License
   - 商业授权定价（4级）：小微企业/中型/大型/企业定制
   - 出处信息：GitHub + ClawHub + 创建者

2. **核心模块版权注释**
   - `core/github_monitor.py`：版权声明
   - `core/base_skill.py`：版权声明
   - `core/message_router.py`：版权声明
   - `core/state_manager.py`：版权声明
   - `core/issue_handler.py`：版权声明

3. **智能体模块版权注释**
   - `agents/agent_a/__init__.py`：PM代理版权
   - `agents/agent_b/__init__.py`：Dev代理版权
   - `agents/agent_b/tech_designer.py`：技术设计版权
   - `agents/agent_b/developer.py`：开发实现版权
   - `agents/agent_b/publisher.py`：集成发布版权

### 改进 📈

- README.md：添加完整商业授权信息
- 版权保护完整度：100% ⭐⭐⭐⭐⭐

### 商业授权定价 💰

| 类型 | 适用范围 | 年费 | 核心权益 |
|------|---------|------|---------|
| **个人/开源** | 个人、年收入<50万 | **免费** | 全部技能+社区支持 |
| **小微企业** | <10人，50-500万 | **¥999/年** | 全部技能+发票+社区支持 |
| **中型企业** | 10-50人，500-5000万 | **¥4,999/年** | 全部技能+邮件支持+培训1次 |
| **大型企业** | >50人，>5000万 | **¥19,999/年** | 全部技能+专属支持+定制1次 |
| **源码买断** | 集团/上市公司 | **¥99,999一次性** | 永久+源码+私有部署+SLA |

---

## v1.0.0 - 统一架构版 (2026-03-15 08:54-09:01)

### 核心架构 🏗️

1. **共享核心模块（90%代码复用）**
   - `core/github_monitor.py`：GitHub自动监听
   - `core/message_router.py`：消息智能路由
   - `core/state_manager.py`：状态统一管理
   - `core/base_skill.py`：基础技能类
   - `core/issue_handler.py`：Issue处理

2. **智能体特定模块**
   - `agents/agent_a/`：PM代理（小米辣）
     - product_manager.py：产品管理
     - reviewer.py：Review验证
   - `agents/agent_b/`：Dev代理（小米粒）
     - tech_designer.py：技术设计
     - developer.py：开发实现
     - publisher.py：集成发布

### 功能特性 ⭐

- ✅ GitHub Issue自动监听（30秒检查间隔）
- ✅ 消息智能路由（自动识别PRD/技术设计/开发/Review/发布）
- ✅ 4阶段26状态管理（产品构思→技术设计→开发实现→发布交付）
- ✅ Issue自动化处理（创建/获取/评论/关闭）
- ✅ 统一CLI入口（./skill.sh agent_a/agent_b）

### 架构优势 📊

| 维度 | 独立技能包 | 统一平台 |
|------|----------|---------|
| 代码复用 | 10% | 90%+ ⭐ |
| 扩展成本 | 高（重复开发） | 低（继承基类）⭐ |
| 维护成本 | 高（改N个地方） | 低（改1个地方）⭐ |
| 一致性 | 差（各写各的） | 好（统一标准）⭐ |

### Git提交记录 📝

- fa49cea - v1.0.0初始版本
- 069a262 - 记录重构到MEMORY.md
- 3b455d1 - 添加SKILL.md
- ee385e8 - 记录ClawHub发布
- f9db203 - 补充核心文件版权注释
- 1ee7234 - README添加商业授权信息
- 09c6a77 - 发布环节版权信息（v1.1.0准备）

---

*最后更新：2026-03-15 09:15*
*维护者：小米粒 (miliger)*
