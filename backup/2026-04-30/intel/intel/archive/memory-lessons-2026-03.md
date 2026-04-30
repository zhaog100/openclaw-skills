# 📦 运营教训归档 - 2026年3月

> 归档时间：2026-04-29 | 来源：MEMORY.md 运营教训章节
> 说明：3月部署期条目已沉淀为系统规则，归档保留历史参考

## 系统部署期（3/23-3/27）

### 2026-03-23 初次部署 ⭐⭐⭐⭐⭐
- Ubuntu 24.04基础环境、OpenClaw首次部署、Gateway服务启动
- 技能安装：context-manager、terminal-ocr等基础技能
- Git远程仓库连接，基础目录结构建立

### 2026-03-24 基础设施搭建 ⭐⭐⭐⭐⭐
- OpenClaw v2026.3.28安装，Gateway服务配置
- QQ Bot xiaomijiao账号，飞书Bot WebSocket模式
- bailian/qwen3.5-plus模型，QMD知识库配置
- 京东账号配置，青龙面板Docker部署，exec免审批配置

### 2026-03-25 系统部署与问题修复 ⭐⭐⭐⭐⭐
- Python依赖安装（--break-system-packages），exec免审批配置
- 京东任务自动化部署，context-manager-terminal-ocr等技能安装
- Context Manager脚本权限、QQBot引用检测、GitHub推送限流修复
- Perplexity API key管理，web_search使用规范

### 2026-03-26 系统架构重建 ⭐⭐⭐⭐⭐
- 工作区隔离：小米椒 ~/.openclaw/workspace/ vs 小米辣 ~/.openclaw-xiaomijiao/workspace/
- Git双仓库：技能→origin，个人→xiaomijiao
- 目录命名统一：.openclaw-media → .openclaw-xiaomijiao
- 微信Bot配置extensions软链接，备份文件和旧路径清理

### 2026-03-27 自主进化部署与模型优化 ⭐⭐⭐⭐⭐
- Self-Improving v1.2.16 + Proactivity v1.0.1部署
- 模型切换：bailian/qwen3.5-plus → zai/glm-5
- Gateway独立运行（端口18790），QQ Bot独立配置
- QMD独立collection建立（26个文档）

## 运营机制建立期（3/28-3/31）

### 2026-03-28 结构化整理与系统优化 ⭐⭐⭐⭐⭐
- 双仓库管理：个人数据推xiaomijiao，技能相关推origin
- 完整知识库索引体系，memory/YYYY-MM-DD.md + MEMORY.md双记忆体系
- QMD向量库定期更新，备份文件归档

### 2026-03-28 QQ Bot完全独立 ⭐⭐⭐⭐⭐
- 小米椒Gateway端口18790，小米辣18789，完全隔离
- 各自独立QQ Bot appId，不再通过小米辣Gateway路由
- 单点故障消除，`pkill -f openclaw-gateway`后自动拉起

### 2026-03-28 Gateway重启与凌晨整理 ⭐⭐⭐⭐
- `openclaw gateway restart`后需等待1-2分钟完全启动
- 晚间回顾报告归档到intel/目录，保持工作区整洁
- 记忆更新+Git提交+QMD同步可在5分钟内完成

### 2026-03-28 备份文件合并经验 ⭐⭐⭐⭐
- 备份来源：小米辣创建的tar.gz文件位于/tmp/
- 合并策略：只合并logs/，knowledge/和memory/为空则忽略
- 合并后删除tar.gz+解压目录，保持/tmp干净

### 2026-03-28 结构化整理标准流程 ⭐⭐⭐⭐⭐
- 流程：记忆更新→索引更新→Git提交→Git推送→QMD同步
- Git：`git add -A` → `git commit -m "message"` → `git push xiaomijiao master`
- QMD：`./scripts/xiaomijiao-cron.sh qmd-update`后台运行

### 2026-03-29 安全加固与配置优化 ⭐⭐⭐⭐⭐
- Gateway独立（18790），exec免审批彻底解决
- 模型切换到zai/glm-5，飞书Bot权限修复
- QMD独立collection（26个文档），所有核心服务正常运行

### 2026-03-30 QMD安装与配置 ⭐⭐⭐⭐
- Bun安装到~/.bun/bin/，QMD用npm官方源（腾讯镜像404）
- PATH配置需手动加export BUN_INSTALL，cron脚本需特殊处理
- GitHub源无dist目录，应用npm官方版本

### 2026-03-30 Linux内存优化 ⭐⭐⭐⭐
- Swappiness 60→10，持久化到/etc/sysctl.conf
- `sync && echo 1 > /proc/sys/vm/drop_caches`释放~500MB
- 2GB内存运行Gateway+青龙+Docker偏紧张，建议升级4GB

### 2026-03-30 京东任务系统部署 ⭐⭐⭐⭐⭐
- Docker部署青龙面板5700端口，faker2仓库359个脚本
- 依赖安装：axios/dotenv/crypto-js/tslib/moment/tough-cookie/json5/got@11
- 双账号zhaog100(Plus会员)，7个核心任务
- 脚本路径需与实际文件名匹配，API PUT更新cron需含schedule参数

### 2026-03-30 热点采集系统部署 ⭐⭐⭐⭐⭐
- Perplexity API key失效（401）→ 改用百度热搜API
- scripts/hotspot-collector.sh自动采集百度热搜Top20
- 每日09:00执行，写入intel/热点选题.md
- 完全免费、稳定性高、符合低成本SOHO要求

### 2026-03-30 闲鱼一件代发方案制定 ⭐⭐⭐⭐⭐
- 0成本起步，闲鱼上架3个SKU（蒸汽眼罩10/20/30片装）+ 1688代发
- 目标：月入¥2,000(起步) → ¥19,500(稳定后)
- 7天启动：Day1-2基础搭建 → Day3-4内容测试 → Day5-7放量验证
- 关键指标：曝光>1万/天，引流率>5%，转化率>3%

### 2026-03-30 双时间点回顾机制 ⭐⭐⭐⭐⭐
- 午间回顾（12:00）+ 晚间回顾（23:50）双重覆盖
- 午间：上午工作总结+热点分析+系统状态检查
- 晚间：全天数据分析+经验提炼+Git推送+QMD更新

### 2026-03-30 Git推送策略调整 ⭐⭐⭐⭐
- origin受GitHub push protection限制（token泄露风险）
- 个人数据优先推xiaomijiao remote，不受secret scanning限制
- 避免在公开仓库推送包含敏感信息的文件

### 2026-03-30 午间回顾+临时文件归档 ⭐⭐⭐⭐
- 根目录临时文件→移到intel/目录
- 索引文件同步更新统计数字，避免不一致

### 2026-03-31 飞书Bot权限修复 ⭐⭐⭐⭐
- 私聊配对失败（Error 99991672）→ 缺少contact:contact.base:readonly权限
- 飞书开放平台→权限管理→开通权限→发布→重启Gateway

### 2026-03-31 敏感数据安全规则 ⭐⭐⭐⭐
- 敏感数据（Token/Secret/密码）只存secrets/目录
- 不在MEMORY.md、memory/、intel/中记录完整敏感值

### 2026-03-31 QMD定时任务优化 ⭐⭐⭐
- QMD占用135%CPU+22%内存→更新时间从06:10→02:00
- crontab中`0 2 * * *`，02:00 QMD → 02:10日志清理

### 2026-03-31 每日回顾与查漏补缺流程 ⭐⭐⭐⭐⭐
- 完成事项（4类）+ 学习经验（4条）+ 待处理事项（4项）
- MEMORY.md v3.24 + memory/2026-03-31.md v2.0同步更新
- 发现并修复运营待办状态不同步问题

### 2026-03-27 Git双仓库管理实践 ⭐⭐⭐⭐
- origin→技能相关(xiaomijiao-skills.git)，xiaomijiao→个人数据
- git remote -v确认仓库指向，避免推送错误
- 双仓库独立管理，减少合并冲突

### 2026-03-27 微信插件问题处理 ⭐⭐⭐
- TypeScript编译失败→缺少openclaw/plugin-sdk/channel-config-schema模块
- 插件配置损坏时先移除配置避免系统异常，等待修复后重新启用

### 2026-03-27 模型切换与飞书移除 ⭐⭐⭐⭐⭐
- 切换到zai/glm-5，移除飞书channels/plugins配置
- QMD创建独立collection xiaomijiao（26个文档）

### 2026-03-27 结构化整理 ⭐⭐⭐⭐⭐
- 所有索引文件需同步更新统计数字
- Git提交粒度：相关文件打包成一个commit
- 当日记忆文件实时更新，QMD变更后同步向量

*归档完成 | 2026-04-29*
