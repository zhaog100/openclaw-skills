# multi-platform-notifier - 多平台通知集成

> 统一的企业级消息通知工具，支持企业微信、钉钉、飞书

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 功能特性

- ✅ **统一接口** - 一套命令发送所有平台
- ✅ **配置管理** - 简单的 Webhook 配置
- ✅ **消息模板** - 内置常用通知模板
- ✅ **发送历史** - 完整的日志记录
- ✅ **纯本地执行** - 需要 curl 和 jq

---

## 🚀 快速开始

### 安装

```bash
cd skills/multi-platform-notifier
chmod +x skill.sh test.sh
```

### 配置平台

```bash
# 添加企业微信
./skill.sh config --add wecom "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

# 添加钉钉
./skill.sh config --add dingtalk "https://oapi.dingtalk.com/robot/send?access_token=xxx"

# 添加飞书
./skill.sh config --add feishu "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

# 测试连接
./skill.sh config --test wecom
```

### 发送消息

```bash
# 发送文本消息
./skill.sh send -p wecom -c "Hello World"

# 发送到所有平台
./skill.sh send -p all -c "重要通知"

# 使用告警模板
./skill.sh send -p wecom -T alert --level 紧急 --message 服务器宕机
```

---

## 📊 命令参考

### send - 发送通知

```bash
./skill.sh send --platform <平台> --content <内容> [选项]

选项:
  -p, --platform     目标平台 (wecom|dingtalk|feishu|all)
  -c, --content      消息内容
  -t, --type         消息类型 (text|markdown|card)
  -T, --template     使用模板 (alert|success|reminder)
  --level           告警级别 (template 用)
  --message         告警内容 (template 用)
```

### config - 配置管理

```bash
./skill.sh config --list                  # 列出配置
./skill.sh config --add <平台> <webhook>  # 添加配置
./skill.sh config --remove <平台>         # 删除配置
./skill.sh config --test <平台>           # 测试连接
```

### history - 查看历史

```bash
./skill.sh history --limit 10             # 最近 10 条
./skill.sh history --status failed        # 失败记录
./skill.sh history --platform wecom       # 指定平台
```

---

## 📁 项目结构

```
multi-platform-notifier/
├── skill.sh              # 主入口
├── test.sh               # 测试脚本
├── platforms/            # 平台适配器
│   ├── wecom.sh         # 企业微信
│   ├── dingtalk.sh      # 钉钉
│   └── feishu.sh        # 飞书
├── templates/            # 消息模板
│   ├── alert.json       # 告警
│   ├── success.json     # 成功
│   └── reminder.json    # 提醒
├── config/
│   └── platforms.conf   # 配置文件
├── logs/
│   └── send.log         # 发送日志
├── SKILL.md             # 技能说明
└── README.md            # 本文档
```

---

## 🔧 开发计划

### Phase 1（已完成）✅
- [x] 统一发送接口
- [x] 配置管理
- [x] 消息模板
- [x] 发送历史

### Phase 2（计划中）⏳
- [ ] 失败重试机制
- [ ] 并发发送优化
- [ ] 卡片消息支持
- [ ] Webhook 签名验证

---

## 📝 许可证

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

---

*版本：v1.0*  
*最后更新：2026-03-16*  
*创建者：小米辣 (PM + Dev)*
