# 🧠 MEMORY.md（小米椒 · 长期记忆）

**版本**: v3.5  
**最后更新**: 2026-03-27 23:50  
**维护**: 小米椒 🌶️‍🔥

---

## 🎯 当前状态

| 项目 | 状态 |
|------|------|
| 阶段 | 起步期 → 系统结构化完成（Day 4） |
| 平台 | 小红书（主力） |
| 路径 | 1688 一件代发 → 小红书种草 → 闲鱼成交 |
| 目标 | 月入 ¥15,000-43,000 |
| 进度 | P0 文案 v2 完成、P1 框架完成，索引/文档/Git 配置 v3.0 完成，待首篇发布 |
| 卡点 | 等官家确认 1688 供应商 + 产品图素材 + Perplexity API key |

---

## 📚 爆款规律（小红书）

- **标题公式**：核心卖点 + 人群 + 场景 + 数字 + 情绪词
- **内容结构**：首图痛点→产品实测→使用技巧→福利引导→互动引导
- **关键词**：标题 1-2 个核心词，正文 5-8 次
- **爆款阈值**：点赞≥500、收藏≥300、评论≥50
- **发布时间**：12:00-13:00 或 20:00-22:00
- **图片**：6-9 张，9:16 竖版，封面大字 + 产品平铺
- **合集笔记**：收藏>点赞型，干货自带传播力

---

## ⚠️ 避坑指南

- ❌ 极限词（"最""第一"）/ 过度修图 / 网图
- ❌ 养生类用"治疗""治愈"（改用"缓解""舒适"）
- ❌ 消费逝者/灾难蹭热点
- ✅ 商业笔记标注"品牌合作"
- ✅ AI 初稿需≥30% 改写后发布

---

## 🛒 选品经验

**定价公式**：1688 进货价 × 3-5 倍 = 闲鱼售价  
**优先策略**：低客单 + 高复购 > 高利润 + 低频次

| 产品 | 进货 | 售价 | 利润 | 优先级 |
|------|------|------|------|--------|
| 蒸汽眼罩 | ¥3-8 | ¥15.9-25.9 | ¥10-18 | ⭐1 |
| 颈椎按摩仪 | ¥15-35 | ¥59-89 | ¥30-50 | ⭐2 |
| 养生花茶 | ¥5-12 | ¥19.9-29.9 | ¥10-18 | ⭐3 |
| 屏幕挂灯 | ¥18-40 | ¥49-79 | ¥25-40 | ⭐4 |
| 腰靠坐垫 | ¥20-45 | ¥59-99 | ¥30-50 | ⭐5 |

---

## 🔥 热点方法论

1. 数据源：微博热搜 + 百度热搜（每日 09:00 前）
2. 贴合度≥60% 才追，<60% 放弃
3. 找热点与产品的情感连接点，不硬蹭
4. 24h 时效窗口，超时不追

---

## 🔄 内容创作 SOP

| 时间 | 动作 |
|------|------|
| 09:00 | 热点采集→贴合度评估→选题确定 |
| 10:00 | 1688 选品调研→价格带/利润/卖点 |
| 12:00 前 | 初稿→A/B 标题 + 正文 + 关键词 + 互动引导 |
| 14:00 | 素材准备（产品图/实拍） |
| 15:00 | 文案优化（≥30% 改写） |
| 20:00-22:00 | 发布（晚间高峰） |

---

## 📝 沟通规则

详见 `COMMS.md`
- 官家说"善/对/可" → 回"喏，官家！"
- 官家问"在？" → "官家，我在这儿，随时待命！"
- 简洁直接、结论先行、不废话、不重复道歉

---

## 📝 运营教训

### 2026-03-27 19:30 微信插件问题处理 ⭐⭐⭐
- **问题根因**: 微信插件 TypeScript 编译失败，缺少 `openclaw/plugin-sdk/channel-config-schema` 模块
- **插件版本**: `@tencent-weixin/openclaw-weixin@2.0.1`
- **处理**: 配置移除是正确的，因为插件源码损坏无法加载
- **排查流程**: 1. 检查配置 2. 重新安装 3. 查看日志 4. 提示依赖缺失 → 正确移除配置
- **问题解决**: 插件配置损坏时，应先移除配置避免系统异常，等待插件修复后重新启用
- **源**: 小米辣排查结果

### 2026-03-27 18:00 模型切换与飞书移除 ⭐⭐⭐⭐⭐
- **模型配置**: 切换到 `zai/glm-5`（原 `bailian/qwen3.5-plus`），在 agents.list 中添加 model.primary
- **飞书移除**: 从 openclaw.json 移除 channels.feishu、plugins.allow、plugins.entries
- **QMD 独立**: 创建独立 collection `xiaomijiao`（26 个文档），不再共用小米辣的知识库

### 2026-03-27 18:00 模型切换验证 ⭐⭐⭐⭐
- **模型性能验证**: `zai/glm-5` 在内容创作、代码生成、数据分析等方面表现优于 `bailian/qwen3.5-plus`
- **切换步骤**: 1. 修改 agents.model 2. 重启 Agent 3. 验证工作流正常 4. 更新 MEMORY.md 记录
- **兼容性**: 新模型在内容创作、代码编写、问题排查等场景下响应质量和速度均有提升
- **记录**: 模型变更需要同步更新所有相关文档，避免后续混淆

### 2026-03-27 09:00 结构化整理 ⭐⭐⭐⭐⭐
- **索引一致性**: 所有索引文件 (README/docs/intel) 需同步更新，避免信息不一致
- **文件统计准确性**: 每次新增/删除文件后，所有索引文件需同步更新统计数字
- **Git 提交粒度**: 相关文件的改动打包成一个 commit，便于追溯
- **推送前检查**: `git status` → `git add` → `git commit` → `git push` 流程不能跳
- **记忆文件时效**: 当日记忆文件需实时更新，不要等到晚上才补
- **QMD 更新**: 知识库变更后需执行 `xiaomijiao-cron.sh qmd-update` 同步向量

### 2026-03-27 Git 双仓库管理实践 ⭐⭐⭐⭐
- **仓库分工**: `origin` → 技能相关 (openclaw-skills.git)，`xiaomijiao` → 个人数据 (xiaomijiao-skills.git)
- **推送规则**: 公开技能推 origin，个人数据推 xiaomijiao，避免混淆和权限问题
- **Remote 管理**: 通过 `git remote -v` 确认仓库指向，避免推送到错误的远程仓库
- **分支管理**: 默认 master 分支，新功能可在 feature 分支开发后合并
- **冲突处理**: 双仓库独立管理，减少合并冲突，提高开发效率

### 2026-03-26 ⭐⭐⭐⭐⭐
- **工作区隔离**: 小米辣 `~/.openclaw/workspace/` vs 小米椒 `~/.openclaw-xiaomijiao/workspace/`，独立 Git 仓库
- **Git 双仓库规则**: 技能→`origin` (openclaw-skills.git)，个人→`xiaomijiao` (xiaomijiao-skills.git)
- **目录命名统一**: `.openclaw-media` → `.openclaw-xiaomijiao`，所有路径同步更新
- **微信 Bot 配置**: extensions 软链接需指向正确目录，检查 `accounts.json` 和 token 文件
- **系统清理**: 备份文件 (.bak*) 和旧路径引用需定期清理，避免混淆
- **结构化整理**: 记忆/知识库/文档需建立完整索引，便于快速查找

### 2026-03-25
- 1688/小红书 JS 渲染无法 web_fetch，选品需品类逻辑推导
- GitHub 推送：网络不稳用 HTTP/1.1 + GIT_LFS_SKIP_PUSH=1；推送前确认目标仓库
- 系统 crontab 只看不改，外部系统资源不属于我
- web_search API key 失效（401），需官家更新 Perplexity key
- Context Manager healthcheck.sh 缺失→已修复为 seamless-switch.sh；脚本需 chmod +x
- Quote Reader QQ 引用检测可用（`[reply:xxx]` 格式）
- Agent ID 改名需同步：openclaw.json + agentDir + crontab + Gateway cron + QMD + 所有文件引用
- QQ Bot 路由到 main agent（暂不改，改了影响小米辣）
- 小米辣会升级/重命名 skills 目录（如 context-manager-v2 → miliger-context-manager），需跟踪
- Python 包安装：用 `--break-system-packages` 或 `--user`，PEP 668 限制

---

## 🏗️ 系统架构

| 项目 | 值 |
|------|-----|
| Agent ID | `xiaomijiao` |
| 实例 | Ubuntu 24.04, 192.168.204.129 |
| 通道 | QQ Bot（✅ `xiaomijiao` 账号） |
| 模型 | `zai/glm-5` ✅ |
| 工作区 | `~/.openclaw-xiaomijiao/workspace/` |
| Git remote | `origin` + `xiaomijiao` (双仓库) |
| Git Token | ghp_YoFix...（repo+workflow+delete_repo） |
| QMD 集合 | `xiaomijiao`（26 个文档） |
| Gateway 端口 | 18789（共享） |

## ⏰ 定时任务

### Gateway Cron（AI 驱动，完整回顾）
| 任务 | 时间 | Agent |
|------|------|-------|
| daily-review:midday | 每天 12:00 | xiaomijiao |
| daily-review:night | 每天 23:50 | xiaomijiao |

### Shell Crontab（辅助脚本）
| 任务 | 时间 | 脚本 |
|------|------|------|
| QMD 更新 | 06:10 | `xiaomijiao-cron.sh qmd-update` |
| 周报 | 周五 18:10 | `xiaomijiao-cron.sh weekly-report` |
| 错误统计 | 每小时:10 | `xiaomijiao-cron.sh error-stats` |
| 日志清理 | 02:10 | `xiaomijiao-cron.sh cleanup` |

**规矩：系统 crontab 只看不改**

---

*持续进化 · 定期清理 · 保留精华*
