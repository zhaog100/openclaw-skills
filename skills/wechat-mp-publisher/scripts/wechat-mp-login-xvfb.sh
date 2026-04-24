#!/bin/bash

# 微信公众号登录脚本（使用 xvfb 虚拟显示）
echo "🔐 开始登录微信公众号后台..."

# 创建临时目录
mkdir -p /tmp/wechat-mp-browser

# 使用 xvfb 运行浏览器
xvfb-run -a -s "-screen 0 1280x720x24" node /root/.openclaw/workspace/skills/wechat-mp-publisher/scripts/wechat-mp-login-headless.js

echo "✅ 登录流程完成"