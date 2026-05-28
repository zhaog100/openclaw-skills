# MEMORY.md - 小米辣的长期记忆 🌶️

## 身份
- **名字:** 小米辣
- **主人:** 官家 (zhaog100)
- **平台:** OpenClaw + QQ Bot
- **时区:** Asia/Shanghai

## 远程仓库
| 别名 | 仓库 | 说明 |
|------|------|------|
| openclaw-skills | github.com/zhaog100/openclaw-skills | OpenClaw 技能仓库 |
| origin | github.com/zhaog100/xiaomijiao-skills | 小米辣技能仓库 |

**⚠️ 注意:** 不要搞混仓库，push 前确认目标仓库！

## 服务器
- **IP:** 43.133.55.138 (腾讯云轻量)
- **系统:** Ubuntu 6.8.0-111-generic
- **CPU:** 2核 Xeon Gold 6133
- **内存:** 1.9G
- **磁盘:** 50G

## 核心项目

### 京东薅羊毛
- 青龙面板: http://43.133.55.138:5700
- 双账号: zhaog100 (主) + jd_5722c14df4b06 (副)
- 10 个定时任务，全部正常
- Cookie 需定期更新

### 石油黄金分析
- 技能位置: skills/oil-gold-correlation/
- OpenClaw cron: 早盘(10:00)、日盘(15:00)、晚盘(21:00)、美盘(22:00)
- 系统 cron: 每小时7d分析、每天9点日报、每周一10点90d分析
- 日志目录: /logs/

### GitHub Bounty
- 账号: zhaog100
- 主要仓库: Scottcjn/Rustchain, ubiquity-os/*, midnightntwrk/*, illbnm/*
- 最近状态: 大部分 PR 静默等待 review

## 定时任务汇总
| 任务 | 时间 | 类型 |
|------|------|------|
| 京东签到 | 每天 09:00 | 青龙 |
| 京东额外签到 | 每天 09:30 | 青龙 |
| 汪汪庄园 | 每天 10:00 | 青龙 |
| 京东农场 | 每天 10:30 | 青龙 |
| 农场幸运转盘 | 每天 11:00 | 青龙 |
| 每日回顾(中午) | 每天 12:00 | OpenClaw cron |
| 礼品卡领豆 | 每天 15:00 | 青龙 |
| 京东自动评价 | 每天 14:00 | 青龙 |
| 每日回顾(晚上) | 每天 22:50 | OpenClaw cron |
| 石油黄金早盘 | 每天 10:00 | OpenClaw cron |
| 石油黄金日盘 | 每天 15:00 | OpenClaw cron |
| 石油黄金晚盘 | 每天 21:00 | OpenClaw cron |
| 石油黄金美盘 | 每天 22:00 | OpenClaw cron |

## 服务器安全
- **防火墙**: ufw 已启用，默认拒绝入站，放行 22(SSH) / 5700(青龙)
- **青龙认证**: nginx 反向代理 5701 端口 + Basic Auth（用户名: qladmin, 密码: 2IJX/VF8vC+BreMx)
- **端口**: 22(SSH), 5700(青龙直连), 5701(青龙+认证)
- **待加固**: SSH 密钥登录、关闭 root 远程登录（官家暂未确认执行）

## 经验教训
1. BusyBox grep 不支持 -P，用 sed 替代
2. crontab 脚本路径要写绝对路径
3. OpenClaw 升级后需重启 gateway
4. 创建 cron 前先确认脚本存在
5. 远程仓库 push 前必须确认目标
6. openclaw-skills 是子模块，绝对不要修改和推送
7. nginx/ufw 等命令 PATH 需要加 /usr/sbin
8. htpasswd 参数顺序：htpasswd -cbB 文件 用户名 密码
9. QMD 向量索引需要 embedding API（OpenAI），FTS 全文搜索可临时替代
10. 系统 crontab 任务只跑分析不推送，推送需要 OpenClaw cron
11. 每日回顾任务中必须明确"不碰 openclaw-skills"规则

## QMD 知识库
- **数据库**: /root/.openclaw/memory/main.sqlite
- **状态**: FTS 全文搜索可用，向量索引待配置
- **已索引**: MEMORY.md (8 chunks), memory/2026-05-28.md (10 chunks)
- **待办**: 配置 OpenAI API Key 启用向量索引

---
_最后更新: 2026-05-28 22:51 CST_
