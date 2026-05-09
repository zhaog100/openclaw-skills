# OpenCLI Bridge - 快速参考

## 安装

```bash
# 1. 安装 OpenCLI
npm install -g @jackwener/opencli

# 2. 安装 Extension
# 下载: https://github.com/jackwener/opencli/releases
# 加载到 chrome://extensions

# 3. 验证
opencli doctor
```

## 常用命令

### 内容平台

```bash
opencli bilibili hot --limit 10
opencli zhihu hot --limit 10
opencli xiaohongshu search --query "AI"
opencli twitter trending
opencli hackernews top --limit 10
```

### 浏览器自动化

```bash
opencli operate open <url>
opencli operate state
opencli operate click <index>
opencli operate type <index> "text"
opencli operate network
```

## 安全提示

- ✅ 使用环境变量存储敏感信息
- ✅ 日志自动脱敏
- ✅ 遵守网站使用条款
- ❌ 不要在命令中暴露密码

## 输出格式

```bash
--format json    # JSON
--format yaml    # YAML
--format csv     # CSV
--format md      # Markdown
```

## 许可证

- **OpenCLI**: Apache-2.0 (jackwener)
- **Bridge**: MIT (小米粒)
