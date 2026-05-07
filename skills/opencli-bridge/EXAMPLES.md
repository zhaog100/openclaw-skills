# OpenCLI Bridge - 使用示例

## 示例 1: 研究 Bounty 任务趋势

```bash
# 收集 Hacker News 热门
opencli hackernews top --limit 20 --format json > hn-trending.json

# 搜索 GitHub Bounty
opencli operate open https://github.com/issues?q=label:bounty
opencli operate state
opencli operate network  # 发现 API
```

## 示例 2: 内容发布自动化

```bash
# 小红书（需先在 Chrome 登录）
opencli xiaohongshu publish \
  --title "AI 办公提效技巧" \
  --content "10个实用技巧..." \
  --images "./images/*.jpg"

# Bilibili 动态
opencli bilibili dynamic --content "今日分享..."
```

## 示例 3: 竞品分析

```bash
# 收集竞品数据
opencli bilibili search --query "AI工具" --limit 50 --format csv > competitors.csv

# 知乎讨论
opencli zhihu search --query "人工智能" --limit 30 --format json > zhihu-ai.json
```

## 示例 4: 自动化表单填写

```bash
# 打开页面
opencli operate open https://example.com/submit

# 查看元素
opencli operate state

# 填写表单
opencli operate type 3 "项目标题" && \
opencli operate type 4 "项目描述" && \
opencli operate type 5 "user@example.com"

# 提交
opencli operate click 10
```

## 示例 5: API 发现

```bash
# 打开网站
opencli operate open https://api.example.com

# 捕获 API 请求
opencli operate network

# 查看详情
opencli operate network --detail 0

# 使用 API
opencli operate eval "fetch('/api/data').then(r => r.json())"
```

## 示例 6: 定时数据收集

```bash
#!/bin/bash
# daily-collection.sh

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="./data/$DATE"

mkdir -p "$OUTPUT_DIR"

# Bilibili 热门
opencli bilibili hot --limit 50 --format json > "$OUTPUT_DIR/bilibili-hot.json"

# Hacker News
opencli hackernews top --limit 30 --format json > "$OUTPUT_DIR/hn-top.json"

# Twitter 趋势
opencli twitter trending --format json > "$OUTPUT_DIR/twitter-trending.json"

echo "✅ 数据已收集到 $OUTPUT_DIR"
```

## 示例 7: 敏感信息处理

```bash
# ❌ 错误（暴露邮箱）
# opencli operate type 3 "user@example.com"

# ✅ 正确（使用环境变量）
export EMAIL="user@example.com"
opencli operate type 3 "$EMAIL"

# ✅ 正确（从文件读取）
EMAIL=$(cat ~/.config/email.txt)
opencli operate type 3 "$EMAIL"

# ✅ 正确（日志自动脱敏）
# 输出: "user@***.com"
```

## 示例 8: 错误处理

```bash
#!/bin/bash

# 尝试获取数据
if opencli bilibili hot --limit 10 --format json > data.json 2>/dev/null; then
    echo "✅ 成功"
    # 处理数据
    cat data.json | jq '.[] | .title'
else
    EXIT_CODE=$?
    case $EXIT_CODE in
        69)
            echo "❌ Browser Bridge 未连接"
            echo "   检查 Extension 是否安装"
            ;;
        77)
            echo "❌ 需要登录"
            echo "   在 Chrome 中登录 bilibili.com"
            ;;
        75)
            echo "❌ 请求超时"
            echo "   稍后重试"
            ;;
        *)
            echo "❌ 未知错误 (exit: $EXIT_CODE)"
            ;;
    esac
fi
```

## 示例 9: 批量操作

```bash
#!/bin/bash
# batch-urls.txt
# https://example.com/page1
# https://example.com/page2
# https://example.com/page3

while IFS= read -r url; do
    echo "处理: $url"
    
    opencli operate open "$url" && \
    opencli operate state && \
    opencli operate eval "document.title"
    
    # 速率限制
    sleep 3
done < batch-urls.txt
```

## 示例 10: 创建自定义适配器

```bash
# 1. 探索网站
opencli operate open https://example.com
opencli operate state
opencli operate network

# 2. 生成适配器
opencli operate init example/hot

# 3. 编辑适配器
vim ~/.opencli/clis/example/hot.ts

# 4. 测试
opencli operate verify example/hot

# 5. 使用
opencli example hot --limit 10
```

## 安全提示

1. **敏感信息**: 使用环境变量或配置文件
2. **频率限制**: 遵守网站 robots.txt
3. **版权**: 尊重内容版权，仅用于学习
4. **日志**: 自动脱敏，但仍需注意

## 许可证

- **OpenCLI**: Apache-2.0 (jackwener)
- **示例代码**: MIT (小米粒)
