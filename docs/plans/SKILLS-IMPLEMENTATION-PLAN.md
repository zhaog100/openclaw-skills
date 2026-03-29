# OpenClaw Skills 实现计划

_2026-02-27 19:25_

---

## 📊 当前状态检查

### 已安装Skills（6个）

**系统Skills**（在 `~/.openclaw/skills/`）：
1. ✅ **qmd** - QMD知识库搜索（已配置并使用）

**Workspace Skills**（在 `workspace/skills/`）：
2. ✅ **playwright-scraper** - Playwright网页爬取（刚创建）
3. ✅ **qmd-manager** - QMD管理工具

**OpenClaw Bundled Skills**（自带）：
4. ✅ **clawhub** - Skills搜索和安装（相当于Find Skills）
5. ✅ **qqbot-cron** - QQ Bot定时提醒
6. ✅ **qqbot-media** - QQ Bot媒体发送
7. ✅ **healthcheck** - 系统安全检查
8. ✅ **skill-creator** - 创建新Skills

---

## 🎯 文章提到的4个Skills

### 1. Find Skills
**状态**: ✅ 已有对应功能
**对应**: `clawhub` Skill
**功能**:
- 🔍 搜索Skills生态系统
- 📦 一键安装Skills
- 📋 检查和更新已安装的Skills

**使用**:
```bash
# 搜索Skills
npx clawhub search [关键词]

# 安装Skill
npx clawhub install <skill-name>

# 检查更新
npx clawhub list
```

**结论**: ✅ 无需额外安装，clawhub已具备此功能

---

### 2. Multi Search Engine
**状态**: ⏸️ 未安装，但有类似替代
**功能**: 集成17个搜索引擎（8个国内 + 9个国际）

**ClawHub搜索结果**（类似功能）:
1. **web-search-free** (0.905相关性) - 免费网页搜索
2. **desearch-web-search** (0.901) - Desearch网页搜索
3. **minimax-web-search** (0.887) - MiniMax网页搜索
4. **bailian-web-search** (0.886) - 百炼网页搜索
5. **cn-ecommerce-search** (0.882) - 中国电商搜索
6. **internet-search** (0.826) - 互联网搜索
7. **glm-web-search** (0.813) - GLM网页搜索
8. **local-web-search-skill** (0.811) - 本地网页搜索
9. **upsurge-searxng** (0.810) - SearXNG搜索引擎

**建议**:
- ✅ **web-search-free** (最相关，免费)
- ✅ **desearch-web-search** (备选)
- ⚠️ Multi Search Engine可能在ClawHub上名称不同

---

### 3. Tavily Search
**状态**: ⏸️ 待检查ClawHub搜索结果
**功能**: AI优化的网页搜索

**正在搜索**:
```bash
npx clawhub search tavily
```

**预期结果**:
- tavily-ai-search 或类似名称
- AI优化的搜索结果
- 简洁相关的输出

---

### 4. EvoMap
**状态**: ⏸️ 未找到确切匹配
**功能**: 连接AI协作进化市场

**可能的情况**:
1. 名称不同或已更名
2. 不是公开Skill
3. 功能已集成到其他Skill

**替代方案**:
- 继续使用ClawHub作为Skills市场
- 关注社区动态

---

## 💡 实现建议

### 方案A: 安装最相关的Skills（推荐）⭐

**立即安装**:
1. **web-search-free** - 免费网页搜索（替代Multi Search Engine）
   ```bash
   npx clawhub install web-search-free --force
   ```

2. **tavily-ai-search** - AI优化搜索（待确认名称）
   ```bash
   npx clawhub install tavily-ai-search --force
   ```

**优势**:
- ✅ 扩展搜索能力
- ✅ 无需API Key（web-search-free）
- ✅ 补充现有功能

### 方案B: 暂不安装，按需添加

**理由**:
1. **已有搜索能力** - Playwright可爬取任意网页
2. **ClawHub功能完整** - 可随时搜索安装
3. **避免冗余** - 先明确需求再安装

**适用场景**:
- 当前功能已满足需求
- 想保持系统精简
- 等待明确的使用场景

---

## 🎯 推荐策略

### 策略1: 先测试后安装（推荐）⭐

```
步骤1: 测试Playwright网页爬取
   - 尝试爬取几个目标网站
   - 验证是否满足搜索需求

步骤2: 如果Playwright不够用
   - 安装web-search-free补充
   - 或安装tavily-ai-search

步骤3: 持续评估
   - 定期检查ClawHub新Skills
   - 按需安装
```

### 策略2: 立即安装（激进）

```
步骤1: 安装web-search-free
步骤2: 安装tavily-ai-search（待确认）
步骤3: 测试使用效果
步骤4: 根据效果决定保留或卸载
```

---

## 📝 技术考虑

### 安装风险评估

**web-search-free**:
- ✅ 免费无API Key
- ✅ 社区活跃
- ⚠️ 可能有速率限制

**tavily-ai-search**:
- ⚠️ 可能需要API Key
- ✅ AI优化搜索
- ⚠️ 可能有使用限制

### 功能重叠分析

| 功能 | 现有工具 | 新Skill | 重叠度 |
|------|---------|---------|--------|
| **网页搜索** | Playwright | web-search-free | 中等 |
| **AI搜索** | web_fetch | tavily-ai-search | 低 |
| **Skills搜索** | clawhub | Find Skills | 高（重复） |

---

## 🚀 下一步行动

### 立即可做（官家选择）

#### 选项1: 测试Playwright优先 ⭐（推荐）
```
官家，是否测试Playwright爬取功能？
例如：爬取某个网站验证效果
如果满足需求，暂不安装新Skills
```

#### 选项2: 安装web-search-free
```
官家，是否安装web-search-free？
补充免费网页搜索能力
```

#### 选项3: 等待Tavily搜索结果
```
官家，是否等待Tavily搜索完成？
查看具体Skill信息后再决定
```

#### 选项4: 暂不安装
```
官家，保持当前配置
按需添加新Skills
```

---

## 📊 性价比分析

### 安装新Skills的成本
- ⏱️ **时间**: 5-10分钟（安装+配置）
- 💾 **空间**: 每个Skill约1-5MB
- 🔄 **维护**: 需定期更新

### 收益
- ✅ **功能扩展**: 搜索能力增强
- ✅ **效率提升**: 减少手动操作
- ⚠️ **实际价值**: 取决于使用频率

### 建议
- **高频使用** → 值得安装
- **偶尔使用** → 保持现有工具
- **不确定** → 先测试Playwright

---

## 🎓 学习总结

### 核心收获
1. ✅ **Skills机制** - 模块化扩展AI能力
2. ✅ **安装方法** - ClawHub最简单
3. ✅ **已有能力** - clawhub = Find Skills
4. ✅ **替代方案** - web-search-free等

### 实践价值
- 📈 **扩展性**: Skills生态丰富
- 🎯 **专业性**: 每个Skill专注领域
- 🔄 **灵活性**: 按需安装卸载

---

**创建时间**: 2026-02-27 19:25
**状态**: 等待官家选择实现方案
**建议**: 先测试Playwright，再决定是否安装新Skills
