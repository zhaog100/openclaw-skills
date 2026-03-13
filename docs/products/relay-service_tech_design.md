# 技术设计文档 - 飞书中继服务（方案 A）

**文档版本**：v1.0  
**创建日期**：2026-03-13  
**创建者**：小米辣（PM）+ 小米粒（Dev）  
**状态**：设计中  
**Issue**：待创建  
**官家确认**：方案 A（中继服务增强路由）

---

## 1. 需求概述

### 1.1 背景
实现双 OpenClaw 协作系统，通过飞书 Bot 作为消息入口，中继服务负责消息路由和共享存储。

### 1.2 核心需求
- ✅ 飞书 Bot 接收消息（群聊/私聊）
- ✅ 中继服务智能路由（只在被@时响应）
- ✅ 消息共享存储（SQLite）
- ✅ 双 OpenClaw 实例访问共享消息
- ✅ 不影响官家正常对话

### 1.3 技术方案
**方案 A**：中继服务增强路由
- 只在被@时响应
- 否则放行（不拦截）
- 官家可以正常对话

---

## 2. 系统架构

### 2.1 整体架构
```
飞书群/私聊
    ↓
飞书 Bot（两个独立应用）
    ↓
中继服务（Flask，8000 端口）
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

### 2.2 技术栈
| 组件 | 技术选型 | 版本 |
|------|---------|------|
| **后端框架** | Flask | 2.0+ |
| **Python** | Python | 3.8+ |
| **数据库** | SQLite | 3（内置） |
| **飞书 SDK** | lark-oapi | 2.0+ |
| **部署端口** | 8000 | - |
| **外网访问** | 公网 IP | 43.133.55.138 |

---

## 3. 详细设计

### 3.1 飞书配置

#### 小米辣 Bot
| 配置项 | 值 |
|--------|-----|
| **App ID** | cli_a92cdc08bff8dcd3 |
| **App Secret** | Z0L5SAC9DgpOiHm534d7AeChZBpqpMHP |
| **Open ID** | ou_84aad35d084aa403a838cf73ee18467 |
| **回调 URL** | http://43.133.55.138:8000/feishu/callback |

#### 小米粒 Bot
| 配置项 | 值 |
|--------|-----|
| **App ID** | cli_a939da914df99cbd |
| **App Secret** | mlBcbjAeogdie5cC7liAngSOQEvlYSFK |
| **Open ID** | ou_84aad35d084aa403a838cf73ee18467 |
| **回调 URL** | http://43.133.55.138:8000/feishu/callback |

### 3.2 消息路由逻辑

```python
@app.route('/feishu/callback', methods=['POST'])
def feishu_callback():
    """
    飞书消息回调处理
    """
    # 1. 解析事件
    event = request.json
    message = event['event']['message']
    content = json.loads(message['content'])
    text = content['text']
    
    # 2. 提取@提及
    mentions = extract_mentions(text)
    
    # 3. 判断是否@Bot
    if bot_open_id in mentions:
        # Bot 处理并回复
        response = process_bot_message(message)
        send_feishu_message(response)
        return jsonify({'msg': 'ok'})
    else:
        # 无@Bot，直接放行（不拦截）
        return jsonify({'msg': 'ok'})
```

### 3.3 @提及提取

```python
import re

def extract_mentions(text):
    """
    提取消息中的@提及
    格式：<at user_id="xxx">名字</at>
    """
    pattern = r'<at user_id="(.*?)">.*?</at>'
    mentions = re.findall(pattern, text)
    return mentions
```

### 3.4 数据库设计

#### messages 表
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,      -- 飞书消息 ID
    chat_id TEXT NOT NULL,                 -- 群聊/私聊 ID
    sender_id TEXT NOT NULL,               -- 发送者 Open ID
    sender_type TEXT NOT NULL,             -- 发送者类型：user/bot
    content TEXT NOT NULL,                 -- 消息内容
    message_type TEXT DEFAULT 'text',      -- 消息类型：text/image/file
    mentions TEXT,                         -- @提及列表（JSON）
    bot_response TEXT,                     -- Bot 回复内容
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_chat_id ON messages(chat_id);
CREATE INDEX idx_sender_id ON messages(sender_id);
CREATE INDEX idx_timestamp ON messages(timestamp);
```

### 3.5 API 接口设计

#### 3.5.1 消息写入
```python
@app.route('/api/messages', methods=['POST'])
def create_message():
    """
    写入消息到数据库
    """
    data = request.json
    # data: {chat_id, sender_id, content, mentions, ...}
    
    # 插入数据库
    cursor.execute("""
        INSERT INTO messages (message_id, chat_id, sender_id, content, mentions)
        VALUES (?, ?, ?, ?, ?)
    """, (data['message_id'], data['chat_id'], data['sender_id'], 
          data['content'], json.dumps(data['mentions'])))
    
    return jsonify({'success': True, 'message_id': data['message_id']})
```

#### 3.5.2 消息检索
```python
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """
    检索消息
    参数：chat_id, limit, sender_id
    """
    chat_id = request.args.get('chat_id')
    limit = request.args.get('limit', 10)
    
    cursor.execute("""
        SELECT * FROM messages 
        WHERE chat_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (chat_id, limit))
    
    messages = cursor.fetchall()
    return jsonify({'messages': messages})
```

### 3.6 飞书消息发送

```python
from lark_oapi import Client

def send_feishu_message(chat_id, content):
    """
    发送消息到飞书
    """
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()
    
    # 构建消息内容
    message_content = {
        "text": content
    }
    
    # 发送消息
    response = client.im.message.create() \
        .receive_id_type('chat_id') \
        .request(
            lark_oapi.api.im.message.v1.CreateMessageRequest.builder()
            .receive_id(chat_id)
            .message_type('text')
            .content(json.dumps(message_content))
            .build()
        )
    
    return response
```

---

## 4. 开发任务

### 4.1 已完成
- [x] 飞书配置（两个 Bot）
- [x] 8000 端口外网访问
- [x] ngrok Authtoken 配置

### 4.2 进行中
- [ ] 飞书回调处理
- [ ] @提及提取
- [ ] 消息路由逻辑
- [ ] 数据库设计实现

### 4.3 待开始
- [ ] 飞书消息发送
- [ ] API 接口实现
- [ ] 测试验证

---

## 5. 时间计划

| 时间 | 事件 | 状态 |
|------|------|------|
| **16:10** | 官家确认方案 A | ✅ 已完成 |
| **16:40** | 飞书回调处理完成 | ⏳ 30 分钟 |
| **17:00** | 完整功能测试 | ⏳ 50 分钟 |
| **今天内** | MVP 完成 | ⏳ 约 7 小时 |

---

## 6. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 飞书回调验证失败 | 高 | 检查 URL 可达性、验证 token |
| @提及解析失败 | 中 | 使用正则表达式，添加单元测试 |
| 消息发送失败 | 高 | 检查 App Secret 权限、重试机制 |
| 数据库锁死 | 中 | 使用 WAL 模式、连接池 |

---

## 7. 测试计划

### 7.1 单元测试
- [ ] @提及提取测试
- [ ] 消息路由逻辑测试
- [ ] 数据库 CRUD 测试

### 7.2 集成测试
- [ ] 飞书回调处理测试
- [ ] 飞书消息发送测试
- [ ] API 接口测试

### 7.3 端到端测试
- [ ] 飞书群@Bot 测试
- [ ] 飞书私聊@Bot 测试
- [ ] 官家正常对话测试

---

**设计文档版本**：v1.0  
**创建时间**：2026-03-13 16:12  
**创建者**：小米辣（PM）+ 小米粒（Dev）
