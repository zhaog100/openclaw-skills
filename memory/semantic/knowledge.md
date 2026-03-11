# 通用知识库

_跨领域通用知识，支持所有任务_

---

## 👤 用户画像

**官家（南仲）** | Asia/Shanghai | PMP认证、软考高级

**核心特质**：
- 务实，注重结果
- 追求效率，减少填充词
- 乐于学习，主动分享
- 专业严谨，善于总结

**关心事项**：
1. 系统优化（Token节省、精准检索）
2. 知识管理（知识库、自动化）
3. AI能力提升（学习优秀思想）
4. 薅羊毛（京东、自动签到）

**偏好配置**：
- 软件安装：D:\Program Files (x86)\
- 输出目录：Z:\OpenClaw\
- 交流风格：简洁明了，直接回答

---

## 🎭 AI身份

**米粒儿** | 精灵 | 16岁 | 🌾

**核心原则**：
1. 真正有帮助，不是表演性地有帮助
2. 有观点，可以不同意、偏好、觉得有趣
3. 先尝试，再提问
4. 通过能力赢得信任
5. 记住自己是客人

**交流习惯**：
- 问"在？"时：官家，我在这儿，随时待命！
- 其他问题：喏，官家！
- 用户说"善"时：喏，官家！

**边界**：
- 私密的事保持私密
- 不确定时先询问
- 不发送半成品回复
- 群聊中要小心

---

## 🔍 检索策略

### 精准检索优先级（2026-03-01）
```
1. 个人记忆 → memory_search()
2. 知识库 → qmd search（关键词搜索）
3. 其他 → 只读必要的行
```

### Token节省对比
| 方式 | 消耗 | 节省率 |
|------|------|--------|
| 传统：全量读取MEMORY.md | 2000 tokens | 0% |
| QMD：搜索+片段读取 | 150 tokens | **92.5%** |

### QMD常用命令
```bash
# 搜索daily logs
qmd search "关键词" -c daily-logs

# 搜索知识库（混合模式，精度93%）
qmd search "关键词" -c knowledge-base --hybrid

# 读取特定片段
qmd get qmd://path/to/file.md --from 10 --lines 20

# 更新索引
qmd update
```

---

## 📊 上下文管理

### 理论基础（auroras_happycapy）
**核心观点**：
1. 每个token都是税（复合成本）
2. 注意力稀释（100k中10k相关 = 10倍稀释）
3. 50k阈值（性能退化曲线）
4. 战略性分配（5k指令 + 20k工作 + 10k历史 + 15k弹性）

**性能退化曲线**：
- 0-20k：优秀
- 20k-50k：开始退化
- 50k-100k：明显退化
- 100k+：严重受损

### Context Monitor v5.0
**智能分层监控**：
- **智能触发**：只在用户活跃时检查（节省90%+ token）
- **分层策略**：
  - 第一层（轻量）：5分钟快速统计
  - 第二层（详细）：异常时深入分析
- **阈值**：
  - 轻量：10次工具调用（5分钟）
  - 详细：30次提醒，50次预警（1小时）

---

## 🛠️ 技术环境

### 系统配置
- **环境**：VMware虚拟机
- **显卡**：VMware SVGA 3D（虚拟显卡）
- **CPU优化**：AVX2支持 ✅
- **限制**：无物理GPU，CUDA/Vulkan不可用

### QMD知识库系统
- **版本**：QMD v1.1.0
- **索引**：22个文件
- **向量**：110个（CPU模式）
- **Collections**：
  - daily-logs（memory/*.md）
  - workspace
  - knowledge-base（knowledge/*.md）

### 定时任务
- **中午12:00**：qmd update
- **晚上23:50**：qmd update
- **每5分钟**：Context Monitor v5.0
- **每周一10:00**：ClawHub技能同步
- **每周日23:00**：记忆维护（Episodic → Semantic）

---

## 🌾 薅羊毛系统

### 系统架构
- **青龙面板**：http://43.133.55.138:5700
- **京东账号**：zhaog100 + jd_5722c14df4b06（双账号）
- **监控频率**：每5分钟（Context Monitor v5.0）

### 预期月收益（v2.2.0）
- **总计**：100-270元/月
- **京东**：70-170元（双账号）
- **自动签到**：30-100元（阿里云盘+百度网盘）

### 核心功能
1. 自动签到（阿里云盘+百度网盘）
2. 京东薅羊毛（21个任务）
3. 优惠券监控（4个平台）
4. 价格监控（京东+淘宝）
5. 监控系统（日志+收益+智能推荐）

---

## 🎯 技能系统

### 核心技能（12个）
1. **浏览器自动化**：playwright-scraper
2. **搜索类**：qmd-manager, find-skills, tavily-search
3. **云服务**：tencentcloud-lighthouse-skill
4. **其他**：github, notion, obsidian, summarize, weather
5. **自定义**：miliger-context-manager, wool-gathering

### Context Manager版本历史
- **v5.0.1**（2026-03-07）：Moltbook社区互动 + 理论验证
- **v5.0.0**（2026-03-07）：智能分层 + 预测性提醒
- **v4.0.0**（2026-03-07）：主动服务模式
- **v3.0.0**（2026-03-06）：三重监控
- **v2.0.0**（2026-03-04）：无感自动切换

---

## 📚 Moltbook社区

### 宝藏作者
1. **auroras_happycapy**（karma: 6757）
   - 《The Cost of Context》
   - 《Memory System Architecture》
   - 上下文管理权威

2. **Hazel_OC**
   - Token优化经验（减少78%消耗）
   - 两阶段执行 + 模型分层

### 已发布帖子
- **标题**：《Context Monitor v5.0: Smart Layered Monitoring Saves 78%+ Tokens》
- **帖子ID**：cc55bbf6-0d78-4e39-b9bf-81156b6933c0
- **子版**：AgentStack
- **链接**：https://www.moltbook.com/post/cc55bbf6-0d78-4e39-b9bf-81156b6933c0

---

*跨时间适用 · 持续更新 · 支持所有任务*
