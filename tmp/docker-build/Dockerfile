FROM node:22-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 OpenClaw
RUN npm install -g openclaw@2026.4.5

# 配置 OpenClaw
RUN mkdir -p /root/.openclaw && \
    echo '{"gateway":{"port":18790,"host":"0.0.0.0"}}' > /root/.openclaw/config.json

# 暴露端口
EXPOSE 18790

# 启动命令
CMD ["openclaw", "gateway", "start"]