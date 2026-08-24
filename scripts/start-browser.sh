#!/bin/bash
# 小红书运营 - 浏览器启动脚本
# 用法：./start-browser.sh

set -e

# 清理旧进程
pkill -9 Xvfb 2>/dev/null || true
pkill -9 chromium 2>/dev/null || true
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true

# 启动虚拟显示
echo "Starting Xvfb on :99..."
Xvfb :99 -screen 0 1024x768x24 &
sleep 3

# 启动 Chromium
echo "Starting Chromium with CDP on port 18800..."
export DISPLAY=:99
nohup /snap/bin/chromium \
  --remote-debugging-port=18800 \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --user-data-dir=/tmp/chromium-manual \
  > /tmp/chromium-manual.log 2>&1 &

# 等待浏览器就绪
echo "Waiting for browser to be ready..."
sleep 15

# 验证
if curl -s http://127.0.0.1:18800/json/version > /dev/null; then
  echo "✅ Browser started successfully!"
  curl -s http://127.0.0.1:18800/json/version | head -3
else
  echo "❌ Browser failed to start"
  exit 1
fi
