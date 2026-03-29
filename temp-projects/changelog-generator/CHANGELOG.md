# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Initial] - 2026-03-29

### Added
- Add auto-maintenance system milestone (4-layer auto-update, 6 cron tasks)
- Add qmd-manager skill for QMD knowledge base operations

### Changed
- refactor: 全局修正名称 小米辣→小米粒 + 结构化整理
- feat: AI代码生成改用OpenClaw Gateway OpenAI兼容API
- refactor(bounty-v3): 清理敏感信息和无关内容
- refactor: 优化15个SKILL.md (4728→915行,省80.6%), 删除venv+daily-review-helper重复
- refactor(smart-memory-sync): 统一配置管理，环境变量优先，相对路径
- refactor(lighthouse): add config.json, env var priority, remove hardcoded paths
- refactor(image-content-extractor): add config support, env vars, fix hardcoded paths
- refactor(clawhub-publisher): 配置外部化，环境变量优先，相对路径
- refactor(session-memory-enhanced): extract config to config.json with shared config lib
- refactor(daily-review-helper): 配置外部化 + 共享config loader
- refactor: 抽取统一配置系统，支持环境变量覆盖
- refactor: unify config, remove hardcoded repo paths
- refactor: smart-model-switch 统一配置化
- refactor(daily-review): extract hardcoded config to config.json with env var override
- refactor: 抽取配置到config.json，修复enhanced脚本重复问题
- refactor: 抽取配置到config.json，敏感信息与代码分离
- refactor: MEMORY.md精简 91KB→4KB，保留核心教训和关键数据
- refactor: 统一版权信息为'思捷娅科技'
- Update workspace - 2026-03-12
- Update: MEMORY.md + 知识库索引（2026-03-02）
- Update configuration files - Model strategy adjustment (2026-03-01)

### Fixed
- fix: 紧急恢复丢失的crontab任务
- fix: 京东青龙面板Cookie环境变量修复
- fix: Quote Reader QQ平台适配修复
- fix: unify bounty-hunter version to 5.0.0
- feat: AI生成前读取issue提到的源文件，大幅提升代码准确度
- perf: 优化AI生成速度，减少Gateway负载
- fix: AI多模型fallback，Gateway不稳定时自动切换
- fix: 文件锁防并发+AI超时60s
- fix: 代码质量检查，拒绝提交垃圾代码和空模板
- fix: 防止重复认领同一issue和创建重复PR
- fix: 自动检测默认分支，修复PR 422错误
- fix: 添加fork步骤，修复push到上游仓库403问题
- fix: 添加仓库黑名单过滤，防止认领无价值bounty
- fix: AI代码生成改用OpenClaw CLI + 环境变量API双方案
- fix(projectmind): v1.3.1 审计修复-package.json格式+SKILL.md env声明+setup.sh+安全说明
- fix(autoflow): v1.0.2 安全审计修复 - 统一env变量名+补充声明+setup.sh
- fix(autoflow): 修复import错误+路由函数引用（3处bug）
- fix: 批量修复技能安全问题并升级版本
- fix: auto-document-generator package.json版本引号修正
- fix: 统一package.json版本与SKILL.md一致（18个技能）
- fix: daily-review容错处理，记忆编辑失败不阻断投递
- fix: 优化脚本路径引用 + 清理残留 pid 文件
- fix(bounty-quick-scan): 优化 GitHub API 搜索语法
- fix(projectmind): Phase 2 Review修复
- fix: 移除嵌套git仓库，projectmind作为普通目录提交
- fix(projectmind): 站会is_blocker自动检测 + 11项测试全部通过
- fix: 修复 monitor.py 空值检查 Bug + 同步远程更新
- fix: 从 git 追踪中移除 config.json 和 price_history.db
- fix: 修复 RateLimitError 异常处理
- fix: 解决合并冲突，保留本地工作记录
- fix(github-bounty-hunter): 添加完整版权信息 - LICENSE文件 + README版权声明 + 主脚本版权头
- fix(monitor-guardian): 移除硬编码 Token，改用环境变量 🔒
- fix: 统一身份为小米粒🌾，修正SOUL.md和HEARTBEAT.md
- fix: meeting-minutes-generator NLP质量修复 - 对话格式识别+行动项精准过滤
- fix(meeting-minutes-generator): v1.0.1 - 对话格式NLP质量大幅改善
- fix: 修复 sqlite_store.py 导入路径
- fix(meeting-minutes): 行动项提取+决策识别+空文本+STT接口
- fix(project-progress-tracker): ascii_chart容错非数字值
- fix: 修正身份描述 - 我是小米辣不是小米粒 ⭐⭐⭐⭐⭐
- fix: 统一仓库名称 xiaomili→xiaomila ⭐⭐⭐⭐⭐
- fix(ai-deterministic-control): vote_with_timeout超时bug
- fix(agent-collab-platform): SKILL.md引用经验教训库
- fix(daily-review-assistant): 修复参数解析 bug + 补充 2026-03-16 晚间记录 🌾
- fix: auto-pipeline v1.0 PM工具范围调整
- fix: 修复 load-balancer.sh bug
- fix: 解决 Git 冲突（删除 smart-model PRD）
- fix: 修复 smart-model-switch v1.6.0 bug
- fix: 最终Review修复
- fix: 最终Review修复 - 两个技能全部修复
- fix: 修复两个P0技能Review阻塞项
- fix(auto-document-generator): 修复所有测试问题，达到100%通过率 🎉
- fix(auto-document-generator): 技术设计文档修复 - 4个问题已解决 🌾
- fix: 修正身份 - 我是小米粒（PM + Dev 双身份）🌾
- fix: 实现完全自动化定时任务管理
- fix: 修复 install.sh 路径错误
- fix: 修复 memory-updater.sh EOF 语法错误
- fix: 解决 package.json 合并冲突
- fix(utils): 修复 PM Review 问题 + 重新创建丢失文件
- fix(README): 版本号v1.12.0→v1.14.0 ⭐⭐⭐⭐⭐
- fix(agent-collab-platform): 版本号统一到v1.14.0（所有文件） ⭐⭐⭐⭐⭐
- fix(agent-collab-platform): 版本号更新到v1.14.0 ⭐⭐⭐⭐⭐
- fix(core): 修复GitHub监听器立即退出问题 - 主线程阻塞保持运行
- fix(版权): 批量统一所有技能版权信息为思捷娅科技(SJYKJ) ⭐⭐⭐⭐⭐
- fix(smart-model-switch): v1.4.1 - 修复版本冲突
- fix(版权): 统一4个技能版权信息为思捷娅科技(SJYKJ) ⭐⭐⭐⭐⭐
- fix(MEMORY): 修正仓库配置 - 明确xiaomili为主要推送目标（小米粒仓库）
- fix(scripts): 修复jd_task_checker.sh空变量错误
- fix: 修正身份配置 - 我是小米粒（Dev代理），不是小米辣 🌾
- fix: 解决smart-model-switch package.json冲突
- fix: 所有测试通过！覆盖率提升至56%
- fix: 修复冷却机制测试 + 添加AlertManager类
- fix(test): 修复测试问题 + 更新真实覆盖率
- fix: 规范化文件命名 - 修复4个不符合规范的文件
- fix: 修复2个漏洞 - 更新待开发清单 + 记录demo-skill开发完成
- fix: 修复 miliger-qmd-manager 安全问题
- fix: 京豆任务crontab配置修复（方案A）
- fix: 修复RELEASE-NOTES.md中的QQ号示例（不影响功能）
- fix: 修复记忆更新功能的关键问题
- fix: Context Manager v3.0.0修复
- fix: 添加京东邀请好友和种豆好友任务

### Removed

