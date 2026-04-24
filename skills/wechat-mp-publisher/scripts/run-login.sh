#!/bin/bash

# 微信公众号自动化登录脚本（使用 xvfb）
echo "🔐 开始自动化登录微信公众号..."

# 创建临时目录
mkdir -p /tmp/wechat-mp-session

# 使用 xvfb 运行浏览器
xvfb-run -a -s "-screen 0 1280x720x24" node /root/.openclaw/workspace/skills/wechat-mp-publisher/scripts/wechat-mp-login-automated.js

echo "✅ 登录流程完成"