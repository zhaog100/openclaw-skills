# MEMORY.md - 小米辣的长期记忆 🌶️

## 身份
- **名字:** 小米辣
- **主人:** 官家 (zhaog100)
- **平台:** OpenClaw + QQ Bot
- **时区:** Asia/Shanghai

## 远程仓库
| 别名 | 仓库 | 说明 |
|------|------|------|
| openclaw-skills | github.com/zhaog100/openclaw-skills | OpenClaw 技能仓库（子模块，不碰） |
| origin | github.com/zhaog100/xiaomijiao-skills | 小米辣技能仓库（个人仓库） |

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
- Cookie 需定期更新

### 石油黄金分析
- 技能位置: skills/oil-gold-correlation/scripts/
- OpenClaw cron: 早盘(10:00)、日盘(15:00)、晚盘(21:00)、美盘(22:00)
- 系统 cron: 每小时7d分析、每天9点日报、每周一10点90d分析
- 日志目录: /logs/
- ⚠️ Granger 因果检验数据不足（Insufficient observations），7d 数据量不够

### GitHub Bounty
- 账号: zhaog100
- 主要仓库: Scottcjn/Rustchain, ubiquity-os/*, midnightntwrk/*, illbnm/*

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
- **青龙认证**: nginx 反向代理 5701 端口 + Basic Auth
- **端口**: 22(SSH), 5700(青龙直连), 5701(青龙+认证)
- **待加固**: SSH 密钥登录、关闭 root 远程登录（官家暂未确认执行）

## 经验教训（核心规则，永久有效）
1. BusyBox grep 不支持 -P，用 sed 替代
2. crontab 脚本路径要写绝对路径
3. OpenClaw 升级后需重启 gateway
4. 创建 cron 前先确认脚本存在
5. 远程仓库 push 前必须确认目标
6. openclaw-skills 是子模块，绝对不要修改和推送
7. nginx/ufw 等命令 PATH 需要加 /usr/sbin
8. htpasswd 参数顺序：htpasswd -cbB 文件 用户名 密码
9. 系统 crontab 任务只跑分析不推送，推送需要 OpenClaw cron
10. 每日回顾任务中必须明确"不碰 openclaw-skills"规则
11. LongCat Flash 系列模型已下线不可用，统一使用 LongCat-2.0-Preview
12. openclaw-skills 子模块中的旧模型引用不能修改（规则6），但 workspace/ 下的脚本和技能配置需要同步更新
13. 创建 crontab 任务前必须确认脚本文件存在且可执行
14. 石油黄金分析脚本在 skills/oil-gold-correlation/scripts/ 子目录下，不是根目录
15. crontab 中的 tee 会导致日志重复写入（stdout 被 crontab 重定向到同一文件），用 >> 代替 tee
16. 公考信息采集 crontab 日期不能写死，需用 $(date +%Y-%m-%d) 动态生成
17. 平台规则/数据复盘脚本仅为框架，实际内容需官家补充

## 当前市场关注
- OPEC产量暴跌30%+（约970万桶/日）：伊拉克-66%、科威特-76%、沙特-33%、阿联酋-40%
- 中东局势升级：伊朗称袭击美国第五舰队总部，霍尔木兹海峡封锁持续
- 黄金从$5,000+高点回落至$4,463，跌幅超10%
- 布伦特原油连续第三日上涨，夏季需求高峰临近
- 多家民营银行下架3年期5年期定期存款 — 利率下行信号
- 2026-06-04 新热点：泽连斯基表态愿与普京直接谈判、华为人才离职创业估值1亿美元、宇树机器人登《美国达人秀》
- 高考季热点持续发酵：送考旗袍销量暴涨5倍、考场作弊提醒

## QMD 知识库
- **数据库:** /root/.openclaw/memory/main.sqlite
- **状态:** FTS 全文搜索可用；向量索引受限于内存（1.9G），Qwen3-Embedding-0.6B 加载时 OOM
- **注意:** sqlite3 CLI 未安装，需用 python3 操作数据库

## 待解决问题
- [ ] QMD 向量索引未配置（需要 OpenAI API Key，本地 embedding OOM）
- [ ] SSH 安全加固（密钥登录、关闭 root 远程）
- [ ] 平台规则/数据复盘脚本内容需官家补充
- [ ] 1688供应商确认 — 5家待选，需官家决定
- [ ] 发布首篇小红书笔记（蒸汽眼罩测评）

## 今日变更记录（2026-06-04）
- 石油黄金报告 v3.1 升级：新增波动率&风险对比、历史阶段定位、RSI仪表盘
- 京东主账号Cookie完整更新(2004字符)，签到修复成功
- 副账号Cookie字段不完整，签到仍失败，需官家补Cookie
- 推送方案文档 push-scheme-v2.md 同步更新至 v3.1
- 内存使用偏高(1.1G/1.9G)，需持续关注

---
_最后更新: 2026-06-04 22:50 CST_
