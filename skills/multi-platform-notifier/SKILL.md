# multi-platform-notifier - 多平台通知集成

**版本**: v1.0  
**创建时间**: 2026-03-16  
**创建者**: 小米辣 (PM + Dev)  
**状态**: Phase 1 完成

---

## 📋 简介

统一的多平台通知发送工具，支持企业微信、钉钉、飞书三个主流平台。

---

## 🎯 核心功能

### Phase 1（已完成）
- ✅ 统一发送接口
- ✅ 配置管理（add/remove/list/test）
- ✅ 发送历史查询
- ✅ 消息模板支持

### Phase 2（计划中）
- ⏳ 失败重试机制
- ⏳ 并发发送优化
- ⏳ 更多消息类型（卡片、图文）

---

## 🚀 使用方法

```bash
# 发送文本消息
./skill.sh send -p wecom -c "系统告警：CPU 使用率 95%"

# 发送到所有平台
./skill.sh send -p all -c "重要通知"

# 使用模板
./skill.sh send -p wecom -T alert --level 紧急 --message 服务器宕机

# 配置管理
./skill.sh config --add wecom "YOUR_WEBHOOK"
./skill.sh config --list
./skill.sh config --test wecom

# 查看历史
./skill.sh history --limit 10
```

---

## 📊 支持的平台

| 平台 | 标识 | 消息类型 | 状态 |
|------|------|----------|------|
| 企业微信 | wecom | text/markdown | ✅ |
| 钉钉 | dingtalk | text/markdown | ✅ |
| 飞书 | feishu | text/post | ✅ |

---

## 📝 许可证与版权声明

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

*最后更新：2026-03-16 08:11*
*版本：v1.0*
