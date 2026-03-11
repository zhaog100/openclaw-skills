# 飞书Bot配置流程

## 完整配置步骤

### 第一步：创建飞书应用

1. 访问：https://open.feishu.cn/app
2. 点击"创建企业自建应用"
3. 输入应用名称（如：米粒儿）
4. 上传应用图标
5. 获取App ID和App Secret

---

### 第二步：配置应用权限

**权限配置JSON**
```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "application:application.app_message_stats.overview:readonly",
      "application:application:self_manage",
      "application:bot.menu:write",
      "cardkit:card:write",
      "contact:user.employee_id:readonly",
      "corehr:file:download",
      "docs:document.content:read",
      "event:ip_list",
      "im:chat",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.group_msg",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource",
      "sheets:spreadsheet",
      "wiki:wiki:readonly"
    ],
    "user": [
      "aily:file:read",
      "aily:file:write",
      "im:chat.access_event.bot_p2p_chat:read"
    ]
  }
}
```

**配置方法**
1. 左侧菜单 → 权限管理
2. 点击"批量导入"
3. 粘贴上述JSON
4. 确认导入

---

### 第三步：启用机器人能力

1. 左侧菜单 → 应用能力
2. 点击"机器人"
3. 开启开关
4. 配置机器人名称（如：米粒儿）
5. 上传机器人头像

---

### 第四步：配置事件订阅

1. 左侧菜单 → 事件订阅
2. 选择"使用长连接接收事件"（WebSocket模式）
3. 添加事件：
   - `im.message.receive_v1`（接收消息）
4. 保存配置

---

### 第五步：发布应用

1. 左侧菜单 → 版本管理与发布
2. 点击"创建版本"
3. 输入版本号（如：1.0.0）
4. 填写版本说明
5. 点击"保存并发布"
6. 等待审核（通常自动通过）

---

### 第六步：配置OpenClaw

**配置文件**（~/.openclaw/openclaw.json）
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "main": {
          "appId": "cli_xxxxxxxxxxxxxxxx",
          "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
          "botName": "米粒儿"
        },
        "default": {
          "dmPolicy": "pairing"
        }
      }
    }
  }
}
```

**重启Gateway**
```bash
openclaw gateway restart
```

---

### 第七步：配对

1. 在飞书中搜索Bot（米粒儿）
2. 发送消息
3. OpenClaw收到配对请求
4. 执行配对命令：
   ```bash
   openclaw pairing approve feishu <PAIRING_CODE>
   ```
5. 配对成功

---

## 常见问题

### Q1: 配置文件报错"Invalid config"
**原因**：配置格式错误
**解决**：使用jq验证JSON格式
```bash
cat ~/.openclaw/openclaw.json | jq .
```

### Q2: Gateway无法连接飞书
**原因**：App ID或App Secret错误
**解决**：检查配置文件中的凭证

### Q3: Bot无响应
**原因**：事件订阅未配置或未启用
**解决**：确认事件订阅已配置并启用

### Q4: 权限不足
**原因**：缺少必要权限
**解决**：重新导入权限JSON，确保22个权限全部配置

---

## 功能支持

### 已支持功能
- ✅ 私聊消息
- ✅ 群聊@消息
- ✅ 卡片消息
- ✅ 文档操作（docx）
- ✅ 多维表格（bitable）
- ✅ 知识库（wiki）
- ✅ 云盘（drive）
- ✅ 文件上传

### OpenClaw技能
- `/feishu_doc` - 文档操作
- `/feishu_drive` - 云盘操作
- `/feishu_perm` - 权限管理
- `/feishu_wiki` - 知识库操作
- `/feishu_chat` - 聊天操作
- `/feishu_bitable` - 多维表格

---

## 配置示例

### 完整配置文件示例
```json
{
  "channels": {
    "qqbot": {
      "enabled": true,
      "allowFrom": ["*"],
      "appId": "102845238",
      "clientSecret": "xxx"
    },
    "feishu": {
      "enabled": true,
      "accounts": {
        "main": {
          "appId": "cli_a92cdc08bff8dcd3",
          "appSecret": "xxx",
          "botName": "米粒儿"
        },
        "default": {
          "dmPolicy": "pairing"
        }
      }
    }
  }
}
```

**双渠道Bot配置完成**（QQ + 飞书）✅

---

## 参考文档

- OpenClaw中文文档：`/docs/zh-CN/channels/feishu.md`
- OpenClaw英文文档：`/docs/channels/feishu.md`
- 飞书开放平台：https://open.feishu.cn/
- 飞书API文档：https://open.feishu.cn/document/

---

*最后更新：2026-03-03*
