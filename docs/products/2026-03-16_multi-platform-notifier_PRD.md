# PRD - 多平台通知集成 (multi-platform-notifier)

**版本**: v1.0  
**创建者**: 小米辣 (PM + Dev)  
**创建时间**: 2026-03-16 07:51  
**优先级**: P0  
**预计时间**: 2-3 天

---

## 📋 产品概述

### 背景
当前 OpenClaw 系统需要向多个平台发送通知（企业微信、钉钉、飞书等），但缺乏统一的通知接口。每个平台都有独立的 API 和消息格式，导致：
- 代码重复
- 维护成本高
- 新增平台困难

### 目标
开发一个统一的多平台通知技能，支持：
- ✅ 企业微信机器人
- ✅ 钉钉机器人
- ✅ 飞书机器人
- ✅ 统一 API 接口
- ✅ 配置化管理

---

## 🎯 核心功能

### 功能 1: 统一发送接口

```bash
# 发送文本消息
./skill.sh send --platform wecom --content "系统告警：CPU 使用率 95%"

# 发送到多个平台
./skill.sh send --platform all --content "重要通知"

# 发送卡片消息
./skill.sh send --platform dingtalk --type card --template alert
```

### 功能 2: 平台配置管理

```bash
# 查看配置
./skill.sh config --list

# 添加平台
./skill.sh config --add wecom --webhook "https://qyapi.weixin.qq.com/..."

# 测试连接
./skill.sh test --platform wecom
```

### 功能 3: 消息模板

内置常用模板：
- 🚨 告警模板
- ✅ 成功通知
- ⏰ 定时提醒
- 📊 日报/周报

### 功能 4: 发送记录

```bash
# 查看发送历史
./skill.sh history --limit 10

# 查看失败记录
./skill.sh history --status failed
```

---

## 🏗️ 技术架构

### 核心模块

```
multi-platform-notifier/
├── notifier.sh          # 主入口脚本
├── platforms/           # 平台适配器
│   ├── wecom.sh        # 企业微信
│   ├── dingtalk.sh     # 钉钉
│   └── feishu.sh       # 飞书
├── templates/           # 消息模板
│   ├── alert.json
│   ├── success.json
│   └── reminder.json
├── config/              # 配置文件
│   └── platforms.conf
├── logs/                # 日志目录
├── SKILL.md            # 技能说明
├── README.md           # 使用文档
└── test.sh             # 测试脚本
```

### 消息流转

```
用户命令 → notifier.sh → 平台适配器 → API 请求 → 返回结果
                                    ↓
                              记录日志 + 更新历史
```

---

## 📐 API 设计

### 企业微信机器人

```bash
curl "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=KEY" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"消息内容"}}'
```

### 钉钉机器人

```bash
curl "https://oapi.dingtalk.com/robot/send?access_token=TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"消息内容"}}'
```

### 飞书机器人

```bash
curl "https://open.feishu.cn/open-apis/bot/v2/hook/TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"消息内容"}}'
```

---

## ✅ 验收标准

### 功能验收
- [ ] 支持 3 个平台（企业微信、钉钉、飞书）
- [ ] 统一发送接口工作正常
- [ ] 配置管理功能完整
- [ ] 消息模板可用
- [ ] 发送记录可查询

### 性能验收
- [ ] 单次发送响应 < 3 秒
- [ ] 并发支持（可选）
- [ ] 失败重试机制

### 文档验收
- [ ] README.md 完整
- [ ] SKILL.md 规范
- [ ] 配置示例齐全
- [ ] 版权声明完整

---

## 📅 开发计划

### Phase 1: 核心功能 (Day 1)
- [ ] 创建技能目录结构
- [ ] 实现 notifier.sh 主入口
- [ ] 实现 wecom.sh 适配器
- [ ] 配置文件格式设计

### Phase 2: 平台扩展 (Day 2)
- [ ] 实现 dingtalk.sh 适配器
- [ ] 实现 feishu.sh 适配器
- [ ] 实现配置管理命令
- [ ] 实现发送记录功能

### Phase 3: 完善发布 (Day 3)
- [ ] 添加消息模板
- [ ] 编写文档 (README + SKILL)
- [ ] 测试验证
- [ ] 添加版权声明
- [ ] 发布到 ClawHub

---

## 🔗 相关资源

- 企业微信文档：https://developer.work.weixin.qq.com/document/path/91770
- 钉钉文档：https://open.dingtalk.com/document/robots/custom-robot-access
- 飞书文档：https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-skills
- ClawHub: https://clawhub.com
- 创建者：思捷娅科技 (SJYKJ)

**商业使用授权**：
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 企业定制版：¥99,999 一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)

---

*PRD 版本：v1.0*  
*最后更新：2026-03-16 07:51*  
*创建者：小米辣 (PM + Dev)*
