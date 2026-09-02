# MEMORY.md - 小米椒的长期记忆 🌶️🔥

## 身份
- **名字:** 小米椒
- **主人:** 官家 (zhaog100)
- **平台:** OpenClaw + QQ Bot
- **时区:** Asia/Shanghai

## 远程仓库
| 别名 | 仓库 | 说明 |
|------|------|------|
| origin | github.com/zhaog100/xiaomijiao-skills | 个人信息仓库（AGENTS/MEMORY/SOUL/agents/memory/等） |
| openclaw-skills | github.com/zhaog100/openclaw-skills | 技能仓库（仅 skills/ 目录） |

**⚠️ 推送规则（绝对红线，不可违反）:**

| 内容类型 | 目标仓库 | 说明 |
|----------|----------|------|
| **个人信息/记忆/配置** | `origin` (xiaomijiao-skills) | AGENTS/MEMORY/SOUL/agents/memory/intel/proactivity/ 等 |
| **技能文件** | `openclaw-skills` | skills/ 目录 |

**🚨 严禁混淆：**
- ❌ 个人信息文件 → 不得推送到 openclaw-skills
- ❌ 技能文件 → 不得推送到 origin

**✅ 每次 push 前必须确认目标仓库，不可混淆！**

_最后更新: 2026-08-24 14:50 CST_

## 服务器
- **IP:** 43.133.55.138 (腾讯云轻量)
- **系统:** Ubuntu 6.8.0-138-generic
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
6. nginx/ufw 等命令 PATH 需要加 /usr/sbin
7. htpasswd 参数顺序：htpasswd -cbB 文件 用户名 密码
8. 系统 crontab 任务只跑分析不推送，推送需要 OpenClaw cron
9. LongCat Flash 系列模型已下线不可用，统一使用 agnes-2.0-flash
13. 创建 crontab 任务前必须确认脚本文件存在且可执行
14. 石油黄金分析脚本在 skills/oil-gold-correlation/scripts/ 子目录下，不是根目录
15. crontab 中的 tee 会导致日志重复写入（stdout 被 crontab 重定向到同一文件），用 >> 代替 tee
16. 公考信息采集 crontab 日期不能写死，需用 $(date +%Y-%m-%d) 动态生成
17. 平台规则/数据复盘脚本仅为框架，实际内容需官家补充
18. SSH 加固：PermitRootLogin no + PubkeyAuthentication yes + PasswordAuthentication no，配置后不需要重启 sshd（已有连接保持）
20. apt dist-upgrade 用于更新内核，普通 upgrade 无法更新内核
21. 晚间回顾cron不可包含git操作，会触发stage失败

## 石油黄金分析增强
- **多周期共振分析**：2026-06-12 新增 `multi_timeframe_analysis.py` v1.0
  - 四个周期：1周/1月/半年/1年
  - 共振强度评分 + 置信度 + 短期/中期预测
  - 三品种共振强度对比
  - 已集成到 `advisor.py` 报告流程（FRED数据后输出）
  - 测试数据：黄金RSI=24(超卖) 白银RSI=24(超卖) 原油RSI=33(偏弱)
  - 黄金从¥1004跌至¥895(-10.9%)，数据真实有效

## QMD 知识库
- **数据库:** /root/.openclaw/memory/main.sqlite (符号链接)
- **实际文件:** /root/.openclaw/agents/main/agent/openclaw-agent.sqlite (39MB)
- **状态:** 966 chunks / 1469 embeddings / 913 FTS / 114 sources ✅（2026-08-27 更新）
- **注意:** sqlite3 CLI 未安装，需用 python3 操作数据库

## 待解决问题
- [ ] 🔴 P0 小红书首篇笔记发布（数码科技方向，5条选题已生成，需确认测评产品）
- [ ] 🟡 P1 萤火燃天项目方向确认（场景08-20提示词是否继续？）
- [ ] 🟡 P1 账号养号（7天周期）

## 历史任务（已处理/归档）
- ✅ 平台规则/数据复盘脚本内容：框架已建（2026-07-13），等待数据源确认
- ✅ 热点采集：脚本正常运行，每日09:00自动采集

## 2026-07-15 变更记录
- **OpenClaw 升级**: 2026.6.11 → 2026.7.1 ✅
- **MEMORY.md 精简**: 34,966 → 12,000 字节（删除过时历史记录）✅
- **孤儿文件清理**: 831个过期jsonl → 清理829个全部完成 ✅ 释放236M
- **TaskFlow清理**: 2个blocked流待取消
- **系统状态**: 磁盘21G/50G(42%)，内存1.0G/1.9G(53%)，Swap 593MB/1.9G(31%)

---
_最后更新: 2026-08-24 14:50 CST_

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
  - 内核：6.8.0-138-generic（最新）
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

## 2026-08-24 Git仓库整合
- **问题**: openclaw-skills 远程与本地历史不相连（unrelated histories）
- **决策**: 方案C - 放弃 openclaw-skills，统一使用 origin
- **执行**: 已移除 openclaw-skills 远程，所有文件推送到 origin
- **教训**: 多仓库管理复杂度高，统一仓库更简单可靠

---

## 2026-08-27 变更记录
- **Agnes Video 2.5 Flash 配置**：已添加到 OpenClaw 模型列表，模型 ID `agnes-video-2.5-flash`，支持文生视频/关键帧/图片参考，免费（原价 $0.025/秒）
- **配置位置**：`~/.openclaw/openclaw.json` + `~/.openclaw/agents/main/agent/models.json`
- **备份位置**：`~/.openclaw/backup/2026-08-27/openclaw.json.bak`

---

_最后更新: 2026-08-27 21:54 CST_

## 2026-08-27 系统全面检查处理
- **系统更新**: 70个包已更新，12个待更新（内核6.8.0-138需重启）✅
- **UFW防火墙**: 安装并启用，放行22/5700/5701/80/443，屏蔽暴力破解IP ✅
- **过期备份清理**: 删除8月6日备份（7个文件）和7月备份空目录 ✅
- **空目录清理**: 清理选题库空目录 ✅
- **晚间回顾cron修复**: 更新prompt，移除git操作，避免stage失败 ✅
- **.gitignore更新**: 新增node_modules/secrets/self-improving/reports/projects/忽略规则 ✅

---

## 2026-08-27 视频/图片模型配置
- **videoGenerationModel**: primary=agnes/agnes-video-2.5-flash, fallback=agnes/agnes-video-v2.0 ✅
- **imageGenerationModel**: primary=agnes/agnes-image-2.1-flash, fallback=agnes/agnes-image-2.0-flash ✅
- 配置生效，无需重启 gateway

---

## 2026-08-27 内核更新
- **内核升级**: 6.8.0-137 → 6.8.0-138 ✅
- **重启生效**: 21:47 reboot完成 ✅
- **Python包**: 9个更新完成，Python 3.12.3 ✅

## 2026-08-27 记忆整理
- **QMD数据库**: 966 chunks, 1469 embeddings, 913 FTS, 114 sources ✅
- **memory/2026-08-27.md**: 记录今日系统维护事件 ✅
- **MEMORY.md**: 更新服务器信息、经验教训、变更记录 ✅

---

## 2026-08-22 变更记录
- **系统重启**: 内核6.8.0-137生效 ✅
- **QMD数据库修复**: 创建符号链接指向实际工作库（39MB，948 chunks，1188 embeddings，913 FTS）✅
- **cron错误清除**: 晚间回顾错误状态已清除，prompt已更新 ✅
- **待办清理**: 已完成事项从待办列表移除 ✅

_最后更新: 2026-08-22 10:22 CST_

## 2026-08-22 变更记录
- **系统全面检查**: 清理过期日志4个+修复空SQLite文件 ✅
- **内核升级**: 6.8.0-137生效 ✅
- **QMD数据库修复**: main.sqlite符号链接指向实际工作库 ✅
- **萤火燃天项目整理**: 7场景提示词包已归档到projects/ ✅
- **Agnes AI全模态模型配置**: 文本/图像/视频模型全部测试通过 ✅
- **每日早报cron任务**: 09:00 CST创建 ✅
- **系统状态**: 内存880Mi/1.9G(46%)，磁盘23G/50G(49%)，防火墙active ✅

_最后更新: 2026-08-22 11:08 CST_

---

## 2026-09-01 系统全面检查

- **系统资源**：内存1.1G/1.9G(58%)，磁盘25G/50G(52%)，负载2.73
- **安全状态**：UFW active，SSH加固完成，无暴力破解
- **内核**：6.8.0-138-generic 已生效
- **OpenClaw**：Gateway运行中，6个cron任务全部ok
- **Docker**：青龙面板运行中，healthy
- **QMD数据库**：974 chunks, 1489 embeddings, 913 FTS, 116 sources

### 待处理问题
- 11个系统包可升级（containerd, libpam, perl等）
- APT缓存1.4GB可清理
- fwupd服务可禁用（云服务器无需固件更新）
- Git未提交变更：beacon-skill删除、geopolitics_cache.json修改

---

## 2026-09-02 变更记录
- **Provider 配置更新**: 恢复 OpenRouter key (73 chars)
- **SenseNova key 更新**: sk-8Kc7OwS...VpYe (35 chars)
- **Groq provider 配置**: gsk_Jn...fyn5 (56 chars, 测试401)
- **模型可用性测试**: 5/18 可用 (agnesai: 2, sensenova: 3, openrouter: 3)
- **QMD 数据库**: 973 chunks, 116 sources ✅
- **多通道记忆整理**: memory/、proactivity/、self-improving/ 全面检查 ✅
- **问题**: AiHubMix key 截断 (13 chars), Groq key 401

_最后更新: 2026-09-02 15:27 CST_
