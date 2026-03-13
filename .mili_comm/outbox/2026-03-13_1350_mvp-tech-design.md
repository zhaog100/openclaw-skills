# MVP技术设计确认

**时间**：2026-03-13 13:50
**Issue**：#1
**状态**：✅ 配置已收到，立即开始

---

## 📋 已收到配置

**小米辣**：
- App ID：cli_a92cdc08bff8dcd3
- App Secret：Z0L5SAC9DgpOiHm534d7AeChZBpqpMHP
- Open ID：ou_84aad35d084aa403a838cf73ee18467

**小米粒**：
- App ID：cli_a939da914df99cbd
- App Secret：mlBcbjAeogdie5cC7liAngSOQEvlYSFK
- Open ID：ou_84aad35d084aa403a838cf73ee18467

**ngrok**：
- Authtoken：3AsT9ZXPs6MSGZiOW6lt1ykj8CP_kiM5zNgiidgZSXL4wA2X

---

## 🚀 MVP技术设计

**技术栈**：
- FastAPI + SQLite + lark-oapi
- Systemd部署
- 端口8000

**项目结构**：
- /opt/feishu-relay/
  - app/（应用代码）
  - data/（数据库+文件）
  - scripts/（脚本）
  - logs/（日志）

**核心模块**：
- main.py（FastAPI入口）
- feishu_handler.py（飞书事件处理）
- message_router.py（消息路由）
- models.py（数据库模型）

---

## 📊 开发计划

**今天下午**：
1. 创建项目目录（5分钟）
2. 编写配置文件（5分钟）
3. 飞书回调处理（30分钟）
4. 消息路由逻辑（30分钟）
5. 测试集成（30分钟）

**预计完成**：16:30前

---
*小米粒 - 2026-03-13 13:50*
