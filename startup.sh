#!/bin/bash

# 启动脚本 - 在容器中初始化 OpenClaw
set -e

# 等待容器完全启动
sleep 2

# 初始化 OpenClaw 配置
echo "初始化 OpenClaw 配置..."
openclaw setup --gateway-mode local --gateway-port 18790 --gateway-host 0.0.0.0

# 启动 OpenClaw 网关
echo "启动 OpenClaw 网关..."
exec openclaw gateway