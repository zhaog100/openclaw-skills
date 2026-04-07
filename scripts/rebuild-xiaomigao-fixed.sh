#!/bin/bash
# 小米糕容器重建脚本（修复版）
# 解决 Snap Docker 与 /tmp 目录冲突问题

LOG_FILE="/home/zhaog/.openclaw/workspace/logs/xiaomigao-rebuild.log"
BUILD_DIR="$HOME/docker-build-xiaomigao"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查容器是否存在
if docker ps -a --format "{{.Names}}" | grep -q "xiaomigao"; then
    log "✓ 小米糕容器已存在"
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep xiaomigao
    exit 0
fi

log "========== 开始重建小米糕容器 =========="

# 创建构建目录（避免使用 /tmp）
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM node:20-bookworm

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 OpenClaw 2026.4.5
RUN npm install -g openclaw@2026.4.5

# 配置 OpenClaw
RUN mkdir -p /root/.openclaw && \
    echo '{"gateway":{"port":18790,"host":"0.0.0.0"}}' > /root/.openclaw/config.json

# 暴露端口
EXPOSE 18790

# 启动命令
CMD ["openclaw", "gateway", "start"]
EOF

log "✓ Dockerfile 已创建"

# 构建镜像
log "构建镜像（这可能需要几分钟）..."
if docker build -t xiaomigao:2026.4.5 -t xiaomigao:latest . >> "$LOG_FILE" 2>&1; then
    log "✓ 镜像构建成功"
else
    log "✗ 镜像构建失败，查看日志: $LOG_FILE"
    exit 1
fi

# 启动容器
log "启动容器..."
if docker run -d \
    --name xiaomigao \
    --hostname xiaomigao \
    -p 18790:18790 \
    -v xiaomigao-data:/root/.openclaw \
    --restart unless-stopped \
    xiaomigao:latest >> "$LOG_FILE" 2>&1; then
    log "✓ 容器启动成功"
else
    log "✗ 容器启动失败"
    exit 1
fi

# 等待启动
sleep 10

# 健康检查
log "健康检查..."
if curl -s http://localhost:18790/health > /dev/null 2>&1; then
    log "✓ 健康检查通过"
    log "========== 重建完成 =========="

    # 显示容器信息
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep xiaomigao

    # 清理构建目录
    rm -rf "$BUILD_DIR"

    exit 0
else
    log "⚠ 健康检查失败，查看容器日志:"
    docker logs xiaomigao | tail -20 | tee -a "$LOG_FILE"
    exit 1
fi
