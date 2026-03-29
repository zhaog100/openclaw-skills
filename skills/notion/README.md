# Notion API Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Notion API for creating and managing pages, databases, and blocks. 📝

## 🎯 简介

Notion API 技能提供完整的 Notion 集成能力，支持：
- ✅ **页面管理** - 创建、读取、更新页面
- ✅ **数据库操作** - 管理 Notion 数据库
- ✅ **块操作** - 创建和管理各种类型的块

## 🚀 快速开始

### 1. 设置 API Key

1. 创建集成：https://notion.so/my-integrations
2. 复制 API key（格式：`ntn_` 或 `secret_` 开头）
3. 保存到配置文件：
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```
4. 分享目标页面/数据库给你的集成（点击"..." → "Connect to" → 你的集成名称）

### 2. API 基础

所有请求需要：
```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

## 📚 核心功能

### 1. 页面操作

#### 创建页面
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": { "database_id": "your-database-id" },
    "properties": {
      "Name": { "title": [{ "text": { "content": "New Page" } }] }
    }
  }'
```

#### 读取页面
```bash
curl -X GET "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 2. 数据库操作

#### 查询数据库
```bash
curl -X POST "https://api.notion.com/v1/databases/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "select": { "equals": "Done" }
    }
  }'
```

### 3. 块操作

#### 添加块到页面
```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{block_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{ "text": { "content": "New paragraph" } }]
        }
      }
    ]
  }'
```

## 💡 最佳实践

### 1. 错误处理
```bash
response=$(curl -s -w "\n%{http_code}" ...)
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -ne 200 ]; then
  echo "请求失败: $body"
  exit 1
fi
```

### 2. 分页处理
```bash
has_more=true
next_cursor=""

while [ "$has_more" = true ]; do
  response=$(curl -X POST "..." -d "{\"start_cursor\": \"$next_cursor\"}")
  # 处理结果
  
  has_more=$(echo "$response" | jq -r '.has_more')
  next_cursor=$(echo "$response" | jq -r '.next_cursor')
done
```

### 3. 速率限制
Notion API 有速率限制（3 requests/second），建议添加延迟：
```bash
sleep 0.34  # 约3 requests/second
```

## 📊 常见用途

### 1. 自动创建日报
```bash
# 获取今天的日期
today=$(date +%Y-%m-%d)

# 创建日报页面
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d "{
    \"parent\": { \"database_id\": \"$DAILY_DB_ID\" },
    \"properties\": {
      \"Date\": { \"date\": { \"start\": \"$today\" } },
      \"Title\": { \"title\": [{ \"text\": { \"content\": \"日报 - $today\" } }] }
    }
  }"
```

### 2. 同步任务状态
```bash
# 更新任务状态
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "properties": {
      "Status": { "select": { "name": "Done" } }
    }
  }'
```

## ⚠️ 注意事项

1. **API Key 安全** - 不要提交到 Git
2. **版本管理** - 注意 Notion API 版本（当前：2025-09-03）
3. **权限配置** - 确保集成有访问目标页面的权限
4. **速率限制** - 3 requests/second

## 📖 详细文档

- **SKILL.md** - 完整使用指南
- **Notion API 文档**：https://developers.notion.com

## 📞 技术支持

- **Notion API 文档**：https://developers.notion.com
- **GitHub**：https://github.com/zhaog100/openclaw-skills

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
