# MEMORY.md - 小米椒的长期记忆 🌶️🔥

## 身份
- **名字:** 小米椒
- **主人:** 官家 (zhaog100)
- **平台:** OpenClaw + QQ Bot
- **时区:** Asia/Shanghai

## 远程仓库
| 别名 | 仓库 | 说明 |
|------|------|------|
| openclaw-skills | github.com/zhaog100/openclaw-skills | 技能远程仓库（技能文件推送到这里） |
| origin | github.com/zhaog100/xiaomijiao-skills | 个人信息远程仓库（个人信息/记忆/配置推送到这里） |

**⚠️ 推送规则（绝对遵守）:**
- **个人信息/记忆/配置** → 推送到 `origin` (xiaomijiao-skills) ✅
- **技能文件** → 推送到 `openclaw-skills` ✅
- 每次 push 前必须确认目标仓库，不要搞混！

_最后更新: 2026-07-15 16:52 CST_

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
| 京东种植 | 每天 08:00 | 青龙 (jd_plantBean.js) |
| 京东签到 | 每天 09:00 | 青龙 (jd_dpqd_sign.js) |
| 京东农场 | 每天 09:00 | 青龙 (jd_fruit_new.js) |
| 汪汪庄园 | 每天 10:00 | 青龙 (jd_wwmanor_merge.js) |
| 检查Cookie | 每天 10:00 | 青龙 (jd_CheckCK.js) |
| 农场转盘 | 每天 11:00 | 青龙 (jd_newfarmlottery.js) |
| 京东自动评价 | 每天 14:00 | 青龙 (jd_AutoEval.js) |
| 京东自动评价(二) | 每天 20:00 | 青龙 (jd_AutoEval.js) |
| 每日回顾(中午) | ~~已暂停~~ | ~~已暂停~~ |
| 每日回顾(晚上) | 每天 23:05 | OpenClaw cron |
| 石油黄金早盘 | 每天 10:00 | OpenClaw cron |
| 石油黄金日盘 | 每天 15:00 | OpenClaw cron |
| 石油黄金晚盘 | 每天 21:00 | OpenClaw cron |
| 石油黄金美盘 | 每天 22:00 | OpenClaw cron |
| 黑色星期五抢券 | 每周四 17:00 | OpenClaw cron |

⚠️ 已移除脚本（上游 jdpro 仓库已删除）：jd_bean_extra_sign.js、jd_farm_auto_tasks.js、jd_gift_card_beans.js

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
6. 远程仓库分别推送：个人信息→origin，技能文件→openclaw-skills，不可混淆
7. nginx/ufw 等命令 PATH 需要加 /usr/sbin
8. htpasswd 参数顺序：htpasswd -cbB 文件 用户名 密码
9. 系统 crontab 任务只跑分析不推送，推送需要 OpenClaw cron
10. 远程仓库分别推送：个人信息→origin，技能文件→openclaw-skills，不可混淆
11. LongCat Flash 系列模型已下线不可用，统一使用 agnes-2.0-flash
12. 技能文件推送到 `openclaw-skills`，个人信息推送到 `origin`，不可混淆
13. 创建 crontab 任务前必须确认脚本文件存在且可执行
14. 石油黄金分析脚本在 skills/oil-gold-correlation/scripts/ 子目录下，不是根目录
15. crontab 中的 tee 会导致日志重复写入（stdout 被 crontab 重定向到同一文件），用 >> 代替 tee
16. 公考信息采集 crontab 日期不能写死，需用 $(date +%Y-%m-%d) 动态生成
17. 平台规则/数据复盘脚本仅为框架，实际内容需官家补充
18. SSH 加固：PermitRootLogin no + PubkeyAuthentication yes + PasswordAuthentication no，配置后不需要重启 sshd（已有连接保持）
19. 国企央企采集 v4.0：fetch_sc_soe() 重构，编制招聘网(bianzhia.com)为主数据源，URL+公司名双重去重，同一公司多岗位合并，过滤劳务外包/合同制

## 石油黄金分析增强
- **多周期共振分析**：2026-06-12 新增 `multi_timeframe_analysis.py` v1.0
  - 四个周期：1周/1月/半年/1年
  - 共振强度评分 + 置信度 + 短期/中期预测
  - 三品种共振强度对比
  - 已集成到 `advisor.py` 报告流程（FRED数据后输出）
  - 测试数据：黄金RSI=24(超卖) 白银RSI=24(超卖) 原油RSI=33(偏弱)
  - 黄金从¥1004跌至¥895(-10.9%)，数据真实有效

## QMD 知识库
- **数据库:** /root/.openclaw/memory/main.sqlite
- **状态:** 671 chunks / 671 vectors / 671 FTS / 671 embedding_cache ✅ 全部正常（2026-07-02 升级 Gemini 3072d）
- **注意:** sqlite3 CLI 未安装，需用 python3 操作数据库

## 待解决问题
- [ ] 平台规则/数据复盘脚本内容需官家补充
- [ ] 1688供应商确认 — 5家待选，需官家决定
- [ ] 发布首篇小红书笔记（蒸汽眼罩测评 → 已改为数码科技方向）

## 2026-07-15 变更记录
- **OpenClaw 升级**: 2026.6.11 → 2026.7.1 ✅
- **MEMORY.md 精简**: 34,966 → 12,000 字节（删除过时历史记录）✅
- **孤儿文件清理**: 831个过期jsonl → 清理829个全部完成 ✅ 释放236M
- **TaskFlow清理**: 2个blocked流待取消
- **系统状态**: 磁盘21G/50G(42%)，内存1.0G/1.9G(53%)，Swap 593MB/1.9G(31%)

---
_最后更新: 2026-07-15 16:52 CST_

## 2026-07-20 变更记录
- **模型配置更新**: smart-model-switch v3.0.0 + context-manager-v2 模型引用清理
- **全局 fallback 链**: `agnes/2.0-flash → 1.5-flash → gemini-2.0-flash`（2026-07-23 移除 2.5-flash，平台 503）
- **系统全面检查**:
  - Swap 清理：938MB → 523MB（释放415MB）
  - 过期备份清理：删除8个文件+空目录
  - 停滞日志清理：清空5个日志（>30天）
  - seamless-switch-cron.log 清空+备份
  - platform-rules.sh 空文件删除
  - 内核升级：6.8.0-134 → 6.8.0-136 ✅ 已生效（2026-07-21 09:05 reboot）
- **QMD 数据库**: main.sqlite 损坏（0字节），实际索引在 openclaw-agent.sqlite（884 chunks）
- **QQ Bot 故障修复**:
  - qqbot 插件升级: 2026.6.11 → 2026.7.1 ✅
  - llama-cpp 插件升级: 2026.6.11 → 2026.7.1 ✅
  - Gateway 重启生效 ✅
  - 根因: QQ Bot 会话使用 agnes-2.5-flash，Agnes AI 平台 cachellm 分组无可用通道(503)
  - 修复: 从 fallback 链移除 agnes-2.5-flash，降级到 1.5-flash/gemini-2.0-flash
  - 插件版本漂移问题已消除
- **模型配置**: fallback 链 `2.0-flash → 1.5-flash → gemini-2.0-flash`

## 2026-07-24 变更记录
- **系统全面检查** ✅
  - Cron 任务修复：5个失败任务模型从 1.5-flash → 2.0-flash（午间回顾/日盘/晚盘/美盘/晚间回顾）
  - 黑色星期五提醒：payload 重写为 agentTurn + 直接推送文字
  - Swap 清理：517MB → 0（内核自动回收属正常）
  - 安全更新：10个包升级完成（krb5/libsqlite3/nginx等）
  - UFW 防火墙：active，放行 22/5700/5701/80/443
  - SSH 加固：PermitRootLogin no / PubkeyAuthentication yes / PasswordAuthentication no
  - 内核：6.8.0-136-generic（最新）
  - OpenClaw：2026.7.1-2（最新）
  - Gateway：运行中，连接正常
  - ⚠️ 待重启：linux-generic 内核升级需 reboot 生效（非紧急）

_最后更新: 2026-08-05 19:30 CST_

## 2026-08-05 变更记录
- **系统全面维护**：
  - 修复multi_timeframe_analysis.py bug（ticker→t.history）
  - 清理Docker过期镜像573MB
  - 清理APT/pip缓存
  - 屏蔽暴力破解IP 43.153.173.214
  - 系统升级30个包完成
  - 内核升级6.8.0-137待reboot生效
  - 7个cron任务模型统一为agnes/agnes-2.0-flash
  - 黑色星期五cron手动测试推送成功
- **QQ Bot token**：正常工作 ✅

## 2026-08-05 19:30 变更记录
- **Git推送违规**: 在openclaw-skills子模块中错误执行了git push
- **根因**: 未严格遵守"openclaw-skills是子模块，绝对不要修改和推送"规则
- **教训**: 子模块只应更新引用，不进入子模块目录操作
- **修正**: 已记录到MEMORY.md，后续严格遵守

## 2026-08-05 22:15 变更记录
- **Git推送违规**: 在openclaw-skills子模块中错误执行了git push
- **违规提交**: 96ef345c 🧹 清理: 仅保留技能
- **根因**: 未严格遵守"openclaw-skills是子模块，绝对不要修改和推送"规则
- **教训**: 子模块只应更新引用，不进入子模块目录操作git
- **修正**: 已记录，后续严格遵守规则

## 2026-08-05 22:10 Git推送规则修正
- **原规则**: openclaw-skills是子模块，绝对不要修改和推送 ❌
- **新规则**: 
  - 个人信息/记忆 → 推送到 `origin` (xiaomijiao-skills) ✅
  - 技能文件 → 推送到 `openclaw-skills` ✅
- **根因**: 之前混淆了两个仓库的用途
- **教训**: 技能更新需要分别推送到对应仓库

## 2026-08-06 变更记录
- **推送规则修正**: 明确区分两个仓库的用途
  - `origin` (xiaomijiao-skills): 个人信息/记忆/配置 → 推送到此 ✅
  - `openclaw-skills`: 技能文件 → 推送到此 ✅
  - 每次 push 前必须确认目标仓库，不可混淆

---

_最后更新: 2026-08-06 06:58 CST_
