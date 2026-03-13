# 交互式卡片内容获取技能分析

**需求时间：** 2026-03-05 12:35
**需求人：** 官家
**核心需求：** 获取飞书/QQ/企业微信交互式卡片里面的内容

---

## 🎯 需求分析

**用户真实需求：**
- ✅ 通过技能自动获取交互式卡片的具体内容
- ✅ 支持多平台：飞书、QQ、企业微信
- ✅ 看到卡片的JSON结构和数据

**当前问题：**
- ❌ `sessions_history` 只返回 `[Interactive Card]` 占位符
- ❌ `quote-reader` 技能无法获取卡片内容（设计目标不同）
- ❌ OpenClaw没有提供获取消息详情的API

---

## 🔍 技术方案

### 1. 飞书卡片内容获取

**API端点：**
```
GET /open-apis/im/v1/messages/:message_id
```

**需要的权限：**
- ✅ `im:message:readonly`（已授权）
- ✅ `im:message.p2p_msg:readonly`（已授权）

**返回格式：**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "message_id": "om_x100b55a43f16d4a0c2bff2ed4e68060",
        "content": "{\"zh-CN\":{\"title\":\"卡片标题\",\"elements\":[...]}}"
      }
    ]
  }
}
```

**实现方式：**
1. 调用飞书API（需要tenant_access_token）
2. 解析content字段（JSON字符串）
3. 提取卡片结构和数据

### 2. QQ卡片内容获取

**需要：**
- QQ Bot API
- 获取消息详情权限
- API调用方式（待研究）

### 3. 企业微信卡片内容获取

**需要：**
- 企业微信API
- 获取消息详情权限
- API调用方式（待研究）

---

## 💡 解决方案

### 方案1：新技能 - interactive-card-reader ⭐⭐⭐⭐⭐

**技能名称：** `interactive-card-reader`

**核心功能：**
1. 检测交互式卡片（通过消息ID）
2. 调用各平台API获取消息详情
3. 解析卡片JSON结构
4. 返回卡片内容供AI使用

**技术实现：**

#### 飞书实现（已完成权限准备）
```bash
# 脚本：get-feishu-card.sh
MESSAGE_ID="$1"

# 调用飞书API（需要tenant_access_token）
curl -X GET \
  "https://open.feishu.cn/open-apis/im/v1/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $TENANT_ACCESS_TOKEN"

# 解析返回的content字段
# 输出卡片内容
```

#### QQ实现（需要研究）
```bash
# 脚本：get-qq-card.sh
# 待研究QQ Bot API
```

#### 企业微信实现（需要研究）
```bash
# 脚本：get-wechat-card.sh
# 待研究企业微信API
```

### 方案2：增强 quote-reader 技能

**问题：**
- quote-reader设计目标是"引用前文读取"
- 不是"获取交互式卡片内容"
- 功能定位不同

**建议：**
- ❌ 不建议增强quote-reader
- ✅ 建议新建interactive-card-reader技能

### 方案3：OpenClaw核心增强

**需要OpenClaw提供：**
1. 飞书/QQ/企业微信消息详情API
2. 交互式卡片内容解析
3. 统一的消息内容格式

**优点：**
- ✅ 核心功能，所有技能可用
- ✅ 统一API，简化开发

**缺点：**
- ⚠️ 需要等待OpenClaw官方支持
- ⚠️ 优先级可能不高

---

## 🚀 推荐方案

**推荐：方案1 - 新建 interactive-card-reader 技能**

**理由：**
1. ✅ 功能定位清晰（专门处理交互式卡片）
2. ✅ 独立性强（不依赖其他技能）
3. ✅ 可扩展（支持多平台）
4. ✅ 实施快（飞书权限已就绪）

**实施步骤：**

### Phase 1：飞书卡片获取（1-2小时）
1. 获取飞书tenant_access_token
2. 实现get-feishu-card.sh脚本
3. 解析卡片JSON
4. 测试验证

### Phase 2：AI集成（1小时）
1. 设计AI调用流程
2. 实现integrate-card.sh
3. 更新SKILL.md

### Phase 3：多平台支持（待定）
1. 研究QQ Bot API
2. 研究企业微信API
3. 实现对应脚本

---

## 🔑 关键问题

### 问题1：如何获取飞书tenant_access_token？

**方案：**
```bash
# 调用飞书API获取tenant_access_token
curl -X POST \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a92cdc08bff8dcd3",
    "app_secret": "APP_SECRET"
  }'
```

**需要：**
- ✅ App ID: `cli_a92cdc08bff8dcd3`
- ⚠️ App Secret（需要从配置中获取）

### 问题2：App Secret从哪里获取？

**可能的位置：**
1. OpenClaw Gateway配置
2. 环境变量
3. 需要官家提供

---

## 📊 可行性评估

| 平台 | 权限 | API | 难度 | 优先级 |
|------|------|-----|------|--------|
| 飞书 | ✅ 已有 | ✅ 有文档 | 🟢 低 | 🔴 高 |
| QQ | ⚠️ 待确认 | ⚠️ 待研究 | 🟡 中 | 🟡 中 |
| 企业微信 | ⚠️ 待确认 | ⚠️ 待研究 | 🟡 中 | 🟢 低 |

**总体可行性：** ✅ 可行（飞书优先）

---

## 🎯 下一步行动

### 立即可做（官家提供App Secret）
1. ✅ 获取App Secret
2. ✅ 实现get-feishu-card.sh
3. ✅ 测试验证
4. ✅ 发布技能

### 需要等待（OpenClaw支持）
1. ⏳ OpenClaw提供消息详情API
2. ⏳ 或者提供tenant_access_token获取方法

---

## 💡 临时解决方案

**在技能实现前，官家可以：**
1. **截图** - 截取卡片内容发给我
2. **复制文字** - 长按卡片复制内容
3. **描述问题** - 直接告诉我想了解什么

**这些是临时方案，技能实现后可以自动化。**

---

## 📝 技能规格

**技能名称：** `interactive-card-reader`

**版本：** v1.0.0

**描述：** 获取飞书/QQ/企业微信交互式卡片内容，自动调用平台API解析卡片结构

**触发词：** "卡片内容"、"交互式卡片"、"获取卡片"、"card content"

**核心能力：**
- 多平台支持（飞书优先）
- 自动调用API
- JSON结构解析
- AI友好集成

**文件结构：**
```
interactive-card-reader/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── config/
│   ├── platform-config.json
│   └── feishu-config.json
├── scripts/
│   ├── get-feishu-card.sh
│   ├── get-qq-card.sh
│   ├── get-wechat-card.sh
│   └── integrate-card.sh
└── data/
    └── token-cache.json
```

---

*分析时间：2026-03-05 12:35*
*分析人：小米辣*
*状态：✅ 可行，等待App Secret*
