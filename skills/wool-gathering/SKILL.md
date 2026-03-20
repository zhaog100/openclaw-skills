---
name: wool-gathering
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。"
version: 1.2.2
---

# 薅羊毛综合技能 v2.3

自动化省钱赚钱工具集。

## 🎯 核心功能

### 京东系统（✅ 已上线）
- 22个定时任务，双账号支持
- 核心收益：领京豆、农场浇水、嘉年华城、PLUS盲盒/专属礼等
- 预期月收益：110-258元（双账号）

### 自动签到（已部署）
- 平台：阿里云盘、百度网盘、B站、爱奇艺等12个
- 预期收益：每月省100-200元会员费

### 价格监控（待开发）
### 优惠券推送（待开发）

## 🚀 使用方式

```bash
# 青龙面板管理
docker ps | grep qinglong
docker exec qinglong dailycheckin          # 手动签到
docker logs qinglong --tail 100            # 查看日志

# 面板地址：http://43.133.55.138:5700
# 签到定时：0 8 * * * dailycheckin
```

## 📁 结构

```
wool-gathering/
├── scripts/          # 可执行脚本（price_monitor, push_notification, coupon_fetcher）
├── references/       # 参考文档（qinglong-setup, platform-apis）
├── assets/           # 配置文件（config_template.json, docker-compose.yml）
├── JD_PLUS_GUIDE.md
└── JD_EARNINGS_REPORT.md
```

## ⚠️ 注意

- ✅ 自动签到、价格监控、联盟API优惠券合规
- ❌ 恶意抢券、爬虫滥用、刷单刷评违规
- Cookie定期更新，使用小号测试

> 详细平台列表、Cookie获取教程、价格监控开发指南见 `references/skill-details.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
