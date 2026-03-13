# 最终方案确认书 - 双 OpenClaw 协作系统

**版本**：v1.0（最终确认版）  
**日期**：2026-03-13  
**确认方**：小米辣（PM）+ 小米粒（Dev）  
**官家确认**：待确认

---

## 一、方案概述

### 方案名称
**双 OpenClaw 协作系统 - 飞书长连接方案**

### 核心目标
实现两个 OpenClaw 实例（小米辣 PM + 小米粒 Dev）通过飞书 Bot 进行消息共享和协作。

### 核心特性
1. **消息接收**：WebSocket 长连接（无需公网 IP）
2. **消息路由**：只在被@时响应，否则放行
3. **消息存储**：SQLite 共享数据库
4. **不影响**：官家正常对话

---

## 二、飞书配置（两个 Bot）

### 小米辣 Bot
| 配置项 | 值 | 确认 |
|--------|-----|------|
| App ID | cli_a92cdc08bff8dcd3 | ☐ |
| App Secret | Z0L5SAC9DgpOiHm534d7AeChZBpqpMHP | ☐ |
| Open ID | ou_84aad35d084aa403a838cf73ee18467 | ☐ |
| 订阅方式 | 长连接（WebSocket） | ☐ |
| 事件订阅 | im.message.receive_v1 | ☐ |
| 应用版本 | 已发布 | ☐ |

### 小米粒 Bot
| 配置项 | 值 | 确认 |
|--------|-----|------|
| App ID | cli_a939da914df99cbd | ☐ |
| App Secret | mlBcbjAeogdie5cC7liAngSOQEvlYSFK | ☐ |
| Open ID | ou_84aad35d084aa403a838cf73ee18467 | ☐ |
| 订阅方式 | 长连接（WebSocket） | ☐ |
| 事件订阅 | im.message.receive_v1 | ☐ |
| 应用版本 | 已发布 | ☐ |

---

## 三、技术架构

```
飞书群/私聊
    ↓
飞书 Bot（两个独立应用）
    ↓
WebSocket 长连接
    ↓
中继服务（Flask + WebSocket 客户端）
    ↓
┌─────────────────────────┐
│  消息路由判断           │
│  - 有@Bot → 处理并回复   │
│  - 无@Bot → 直接放行    │
└─────────────────────────┘
    ↓
SQLite 数据库（消息存储）
    ↓
┌─────────────────────────┐
│  OpenClaw A（小米辣）   │
│  OpenClaw B（小米粒）   │
└─────────────────────────┘
```

**确认**：☐ 理解并同意此架构

---

## 四、核心功能

### 4.1 WebSocket 连接
```python
import websocket

class FeishuWebSocketClient:
    def __init__(self, app_id, app_secret):
        self.ws_url = "wss://ws.feishu.cn/ws/..."
    
    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.ws.run_forever()
```

**确认**：☐ 已实现 ☐ 已测试

---

### 4.2 @提及提取
```python
import re

def extract_mentions(text):
    pattern = r'<at user_id="(.*?)">.*?</at>'
    mentions = re.findall(pattern, text)
    return mentions
```

**确认**：☐ 已实现 ☐ 已测试

---

### 4.3 消息路由逻辑
```python
def on_message(self, ws, message):
    event = json.loads(message)
    mentions = extract_mentions(event['message']['content'])
    
    # 判断是否@Bot
    if bot_open_id in mentions:
        # Bot 处理并回复
        response = process_bot_message(event)
        send_feishu_message(response)
    # 否则不处理（放行）
```

**确认**：☐ 已实现 ☐ 已测试

---

### 4.4 数据库设计
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,
    chat_id TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    sender_type TEXT NOT NULL,
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    mentions TEXT,
    bot_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_id ON messages(chat_id);
CREATE INDEX idx_sender_id ON messages(sender_id);
CREATE INDEX idx_timestamp ON messages(timestamp);
```

**确认**：☐ 已创建 ☐ 已测试

---

## 五、开发进度

### 已完成
- [ ] 飞书配置（两个 Bot）
- [ ] 技术设计文档
- [ ] WebSocket 客户端
- [ ] @提及提取

### 进行中
- [ ] 消息路由逻辑
- [ ] 飞书消息发送
- [ ] 数据库集成

### 待开始
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 错误处理

---

## 六、测试计划

### 6.1 WebSocket 连接测试
- [ ] 连接建立成功
- [ ] 消息接收正常
- [ ] 连接稳定无断开

### 6.2 @提及提取测试
- [ ] 单个@提及正确提取
- [ ] 多个@提及正确处理
- [ ] 无@提取得空列表

### 6.3 消息路由测试
- [ ] @Bot 时正确响应
- [ ] 无@时正常放行
- [ ] 不影响官家对话

### 6.4 端到端测试
- [ ] 飞书群@Bot 测试
- [ ] 飞书私聊@Bot 测试
- [ ] 消息存储测试
- [ ] OpenClaw 访问测试

---

## 七、时间计划

| 时间 | 事件 | 状态 |
|------|------|------|
| **17:29** | 最终方案确认 | ⏳ 待确认 |
| **17:35** | 飞书配置完成 | ⏳ 待完成 |
| **17:45** | 技术开发完成 | ⏳ 待完成 |
| **18:00** | 完整测试通过 | ⏳ 待完成 |

---

## 八、最终确认

### 小米辣（PM）确认
- [ ] 方案理解
- [ ] 架构理解
- [ ] 功能理解
- [ ] 同意实施

**签名**：________________  **日期**：2026-03-13

---

### 小米粒（Dev）确认
- [ ] 方案理解
- [ ] 架构理解
- [ ] 功能理解
- [ ] 同意实施
- [ ] 飞书配置完成
- [ ] 技术开发完成
- [ ] 测试通过

**签名**：________________  **日期**：2026-03-13

---

### 官家确认
- [ ] 方案审批
- [ ] 同意实施

**签名**：________________  **日期**：2026-03-13

---

**文档位置**：`docs/products/final-scheme-confirmation.md`  
**创建时间**：2026-03-13 17:29  
**版本**：v1.0（最终确认版）
