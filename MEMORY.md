# 🧠 MEMORY.md（小米椒 · 长期记忆）

**版本**: v3.74
**最后更新**: 2026-05-01 23:50
**维护**: 小米椒 🌶️‍🔥

---

## 🎯 当前状态

| 项目 | 状态 |
|------|------|
| 阶段 | 执行期（Day 38） |
| 平台 | 小红书（主力）+ 闲鱼（成交） |
| 路径 | 1688 一件代发 → 小红书种草 → 闲鱼成交 |
| 目标 | 月入 ¥15,000-43,000 |
| 进度 | 商贸运营中，Day38，系统优化完成，模型切换LongCat-Flash-Chat，磁盘清理释放2.8GB |
| 卡点 | 小红书0发布（Day 38持续）、产品线单一(仅蒸汽眼罩)、引流转化率低 |
| Git | main分支，推送正常 |
| Skills | 10个（+xiaohongshu-ops, oil-gold-correlation, multi-channel-memory, self-improving等） |
| Cron任务 | 13个（全部已改百炼模型） | 运行正常 |
| OpenClaw | v2026.4.23-beta.4 | Git推送正常 |
| 主力模型 | longcat/LongCat-Flash-Chat |
| 百炼 baseUrl | coding.dashscope.aliyuncs.com/v1（备用） |
| 备用模型 | 16个（百炼8 + 智谱4 + LongCat4） |
| Fallback | 百炼8个 → zai 4个 → longcat 4个 = 16个模型 |

---

## 🔥 热点方法论

1. 数据源：**百度热搜**（免费 + 无需API key）
2. 采集方式：`scripts/hotspot-collector.sh` 自动采集
3. 定时任务：每日 09:00 自动执行
4. 贴合度≥60% 才追，<60% 放弃
5. 找热点与产品的情感连接点，不硬蹭
6. 24h 时效窗口，超时不追

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
|------|------|------|--------|
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

### 2026-03 部署期总结（已归档详情到 intel/archive/memory-lessons-2026-03.md）
- **系统部署**（3/23-3/27）：OpenClaw安装、Gateway独立(18790)、模型切换zai/glm-5、QMD独立collection、Git双仓库
- **运营机制**（3/28-3/31）：双时间点回顾(12:00+23:50)、热点采集(百度热搜09:00)、闲鱼一件代发方案、敏感数据安全规则、exec免审批配置
- **关键教训**：2GB内存偏紧(swap优化后释放~500MB)、QMD占用高(改02:00执行)、GitHub push protection限制(个人数据推xiaomijiao)

### 2026-04-02 安全加固与自主进化 ⭐⭐⭐⭐⭐
- **ClawHavoc事件**：恶意插件窃取SSH Key和钱包助记词，allowInsecureAuth已关闭
- **Self-Improving**：v1.2.16三层记忆(HOT/WARM/COLD)，~/self-improving/目录
- **Proactivity**：v1.0.1主动跟随机制，~/proactivity/目录
- **exec免审批**：openclaw.json加`approvals.exec.enabled=false` + exec-approvals.json改`defaults.security=full`
- **AGENTS.md v3.3**：任务接受流程+权限分级+数据监控+爆款记录+安全检查
- **HEARTBEAT.md v1.3**：AI打卡上班模式(早班08:30/午间12:00/晚班20:30)

### 2026-04-03 热点策略与系统稳定性 ⭐⭐⭐⭐⭐
- **热点贴合度<60%**：连续两日百度热搜与蒸汽眼罩关联性低，坚持原创方向不盲目追热点
- **系统零故障**：exec免审批+Gateway独立+定时任务100%执行
- **OpenClaw v2026.4.5升级**：313秒完成，插件更新失败不影响核心功能

### 2026-04-07 京东任务+百炼API配置 ⭐⭐⭐⭐⭐
- **京东双账号**：zhaog100(Plus,762京豆) + jd_5722c14df4b06(银牌,5京豆)
- **百炼Coding Plan**：baseUrl=coding.dashscope.aliyuncs.com/v1，8个模型
- **教训**：百炼provider名="modelstudio"(不是"bailian")，手动编辑JSON的baseUrl会丢/v1路径

### 2026-04-08 Git推送暂停机制 ⭐⭐⭐⭐⭐
- **官家指令**：暂停每天同步信息到远程仓库，仅保留本地commit
- **实现**：xiaomijiao-cron.sh的do_git_push()移除git push命令
- **恢复**：用备份scripts/xiaomijiao-cron.sh.bak.20260408还原

### 2026-04-09 系统升级+商贸规划 ⭐⭐⭐⭐⭐
- **OpenClaw 2026.4.9**：SSRF防护+.env注入防护
- **LongCat配置**：5个模型，Lite独享50M tokens/天，80%自动切换
- **严重错误反思**：擅自建议数码/科技方向，违反官家明确指示继续商贸 → 教训：①不擅自决定重要方向 ②不过度推测意图 ③认真检查历史记忆

### 2026-04-10 多通道记忆整合 ⭐⭐⭐⭐⭐
- **问题**：QQ Bot聊天记录未进入每日回顾
- **解决**：multi-channel-memory v1.0.0技能，UTC→北京时间+8h
- **Bug修复**：line 228 grep -c含换行导致integer expression expected → tr -d '\n'
- **百炼Key更新**：需重启Gateway生效

### 2026-04-11 Public-APIs全集成 ⭐⭐⭐⭐⭐
- **19个工具调研完成**：素材优化(3)+热点扩展(2)+内容增强(2)+数据分析(2)+基础工具(3)+多媒体(4)+运营(3)
- **云端API Key**：Image Compressor/RapidAPI、APITube News、Meteoblue、Poof
- **本地工具**：14个Python库+vader+pandas+plotly+FFmpeg v6.1.1
- **模型策略**：长Cat优先→智谱GLM-5→百炼Qwen3.5-Plus（当前主力：长Cat）

### 2026-04-12 oil-gold技能+akshare替代 ⭐⭐⭐⭐⭐
- **yfinance限速**：腾讯云IP被持续封禁 → akshare国内免费替代
- **磁盘清理**：pip缓存2.7G+npm缓存1.1G+journal 463M → 释放4G(49%→40%)
- **QQ Bot双账号**：appId 102845238 + 1903724446，不同Bot看到同一用户openid不同
- **matplotlib字体**：ttc需fonttools提取为ttf才能识别

### 2026-04-13 QQ Bot多账号openid不同 ⭐⭐⭐⭐⭐
- **问题**：bot2的cron推送显示delivered但官家没收到
- **根因**：不同QQ Bot appId看到同一用户的openid不同
  - default(102845238): C099848DC9A60BF60A7BE31626822790
  - bot2(1903724446): E7331F9772A02575890BBE94E788248A
- **解决**：所有bot2的cron统一用E7331F9772A02575890BBE94E788248A

### 2026-04-14 oil-gold纯文本推送+双Bot全覆盖 ⭐⭐⭐⭐⭐
- **图片方案废弃**：matplotlib间距/字体/兼容性问题 → 纯文本+emoji进度条
- **推送时间**：10:00(日盘开盘)/15:30(日盘收盘)/23:00(美股开盘后)，冬令时自动延迟
- **13个cron任务**：oil-gold 6个 + xhs 4个 + 回顾京东 3个
- **QQ Bot发图片**：PNG RGBA格式不支持，必须转JPEG

### 2026-04-17 百炼模型终极修复 ⭐⭐⭐⭐⭐
- **现象**：配置正确但Gateway始终404，反复fallback到智谱
- **四层根因**：
  1. Provider名"bailian"非内置名→Gateway不认识→404
  2. 手动编辑JSON的baseUrl被Gateway用.origin丢掉/v1路径→404
  3. Session override锁死fallback模型
  4. Auth profile cooldown阻止重试
- **最终修复**：`openclaw models auth add` → custom → modelstudio → default → 粘贴key
- **教训**：改模型必须用`openclaw models auth add`，不要手动编辑JSON！

### 2026-04-20 晚间回顾流程完善+数据复盘自动化 ⭐⭐⭐⭐⭐
- **Day 26数据**：小红书4篇笔记4360曝光/188赞/158收藏/56评论/引流40人
- **闲鱼数据**：265浏览/46咨询/11成交/¥269.5/客单价¥24.5
- **转化漏斗**：小红书→闲鱼6.08%→咨询17.4%→成交23.9%，整体0.25%
- **脚本警告**：cron.sh line 234 integer expression（换行符导致）

### 2026-04-24 石油黄金白银投资经验全面总结 ⭐⭐⭐⭐⭐
- **技能v1.6.0**：新增白银集成+经验教训章节
- **数据源**：akshare主力(T-1)+yfinance不可用+Alpha Vantage/Twelve Data可选+FRED宏观
- **三资产**：黄金+白银+原油，独立仪表盘+技术分析+操作建议
- **已知限制**：akshare只有T-1数据，完整报告~133秒，部分cron偶发超时

### 2026-05-01 模型切换+系统清理+配置核查 ⭐⭐⭐⭐⭐
- **模型切换**：primary→longcat/LongCat-Flash-Chat，10个cron任务全部更新
- **LongCat配额**：LongCat-2.0-Preview有16M日配额限制，改用Flash-Chat
- **超时修复**：oil-gold-daily (300s→600s)，xhs-topic-ideation (180s→300s)
- **系统清理**：npm缓存(2.3GB→248MB)、journal日志(806MB→92MB)、git gc(303MB→296MB)，释放~2.8GB
- **配置核查**：openclaw.json、auth-profiles、MEMORY.md、smart-model-switch全部正常
- **磁盘状态**：50GB总容量，26GB已用(54%)，22GB可用
- **远程仓库**：git@github.com:zhaog100/xiaomijiao-skills.git (xiaomijiao remote)

### 2026-04-13 oil-gold技能多次迭代 ⭐⭐⭐⭐
- **yfinance限速**：akshare是稳定备用
- **央视新闻**：news_economic_baidu失效→改用news_cctv
- **关键词分级**：geopolitics风险评分从+95降到+50（更合理）
- **新增**：FRED宏观数据(12项指标)+投资决策仪表盘+最终购买建议

### 2026-04-13 淘宝桌面客户端API ⭐⭐⭐
- **taobao-native**：v1.0.43，只支持Windows/macOS
- **Linux服务器**：不支持，需官家本地电脑安装
- **优先级**：低，继续聚焦现有商贸模式


## 🏗️ 系统架构

| 项目 | 值 |
|------|-----|
| Agent ID | `xiaomijiao` |
| 实例 | Ubuntu 24.04, 192.168.204.129 |
| 通道 | QQ Bot（✅ `xiaomijiao` 账号） |
| 模型 | `zai/glm-4.7-flashx` ✅ |
| 工作区 | `~/.openclaw/workspace/` |
| Git remote | `origin` + `xiaomijiao` (双仓库) |
| Git Token | 已配置（repo+workflow+delete_repo） |
| QMD 集合 | `xiaomijiao`（830 个文档） |
| Gateway 端口 | 18789（独立） |
| 飞书 Bot | ✅ `cli_a92cdc08bff8dcd3`（WebSocket 模式，权限已修复） |
| 青龙面板 | Docker qinglong:5700（京东任务自动化） |
| 京东账号 | zhaog100 + jd_5722c14df4b06 (双账号) |

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

### 2026-04-05 周报机制优化 ⭐⭐⭐⭐⭐
- **问题发现**: 周五18:10 weekly-report cron启动但未完成，超时48小时
- **手动干预**: 16:41手动补做第12周报告，Git推送1527d2d
- **根本原因**: 定时任务脚本异常或环境变量问题
- **解决方案**: 检查cron任务配置，设置更详细的错误日志
- **教训**: 重要定时任务需有备份机制和错误监控
- **改进**: 增加任务失败通知机制，避免任务静默失败

### 2026-04-04 系统稳定性验证 ⭐⭐⭐⭐⭐
- **运行状态**: Day 12全天零故障，exec免审批配置稳定生效
- **定时任务**: Shell+Gateway双重定时任务100%执行成功
- **Git管理**: 双仓库策略有效，个人数据推xiaomijiao remote
- **QMD状态**: 801个文档向量库同步正常
- **京东任务**: 7个任务全部启用，运行状态正常
- **结论**: OpenClaw v2026.4.1架构稳定，支持全天候运营

### 2026-04-03 热点运营策略完善 ⭐⭐⭐⭐
- **贴合度分析**: 连续两日百度热搜<60%，与蒸汽眼罩关联性低
- **决策原则**: 坚持"打工人午睡神器"原创方向，不盲目追热点
- **优势**: 百度热搜免费+稳定+实时性好，适合SOHO低成本运营
- **系统化**: 脚本自动化执行+贴合度评估+决策记录，形成完整闭环

### 2026-04-02 自主进化体系部署 ⭐⭐⭐⭐⭐
- **Self-Improving**: v1.2.16已安装，三层记忆体系（HOT/WARM/COLD）
- **Proactivity**: v1.0.1已安装，主动发现遗漏和恢复上下文

- **MEMORY.md**: v3.57 → v3.58，同步 Day 26 状态
- **知识库新增**: 4 文件（午间回顾/数据复盘/选题灵感/今日记忆）
- **教训**: Git Push 需配置 SSH 免密认证；脚本变量需 tr -d '\n' 清理换行符

*持续进化 · 定期清理 · 保留精华 | v3.63 | 2026-04-24*
