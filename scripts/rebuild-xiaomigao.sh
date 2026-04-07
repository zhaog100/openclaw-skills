#!/bin/bash
# 小米糕容器自动重建脚本
# 当网络恢复时自动执行

LOG_FILE="/home/zhaog/.openclaw/workspace/logs/xiaomigao-rebuild.log"
WORKSPACE="/home/zhaog/.openclaw/workspace"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查网络
check_network() {
    # Test multiple endpoints for better reliability
    if curl -s --max-time 5 https://www.google.com > /dev/null 2>&1 || \
       curl -s --max-time 5 https://github.com > /dev/null 2>&1 || \
       curl -s --max-time 5 https://www.baidu.com > /dev/null 2>&1; then
        echo "DEBUG: Network check passed" >&2
        return 0
    else
        echo "DEBUG: Network check failed" >&2
        return 1
    fi
}

# 检查容器是否存在
check_container() {
    if docker ps -a --format "{{.Names}}" | grep -q "xiaomigao"; then
        return 0
    else
        return 1
    fi
}

# 主逻辑
main() {
    log "========== 开始检查 =========="
    
    # 如果容器已存在，退出
    if check_container; then
        log "✓ 小米糕容器已存在，无需重建"
        exit 0
    fi
    
    # 检查网络
    if ! check_network; then
        log "✗ 网络不可用，等待下次重试"
        exit 1
    fi
    
    log "✓ 网络已恢复，开始重建容器..."
    
    # 创建 Dockerfile
    cat > "$WORKSPACE/Dockerfile.xiaomigao" << 'EOF'
FROM node:22-alpine

# 安装系统依赖
RUN apk add --no-cache curl git

# 安装 OpenClaw
RUN npm install -g openclaw@2026.4.5

# 配置 OpenClaw
RUN mkdir -p /root/.openclaw && \
    echo '{"gateway":{"port":18790,"host":"0.0.0.0","mode":"local"}}' > /root/.openclaw/config.json

# 暴露端口
EXPOSE 18790

# 启动命令
CMD ["openclaw", "gateway", "--allow-unconfigured"]
EOF
    
    # 构建镜像
    log "构建镜像..."
    cd "$WORKSPACE"
    if docker build -t xiaomigao:latest -f Dockerfile.xiaomigao . >> "$LOG_FILE" 2>&1; then
        log "✓ 镜像构建成功"
    else
        log "✗ 镜像构建失败"
        exit 1
    fi
    
    # 启动容器
    log "启动容器..."
    if docker run -d \
        --name xiaomigao \
        -p 18790:18790 \
        -v /root/.openclaw:/root/.openclaw \
        --restart unless-stopped \
        xiaomigao:latest >> "$LOG_FILE" 2>&1; then
        log "✓ 容器启动成功"
    else
        log "✗ 容器启动失败"
        exit 1
    fi
    
    # 健康检查 - 检查进程是否运行而不是HTTP端点
    sleep 10
    if docker ps --filter "name=xiaomigao" --filter "status=running" --format "{{.Names}}" | grep -q "xiaomigao"; then
        log "✓ 容器运行正常"
        
        # 检查OpenClaw进程是否在容器内运行
        if docker exec xiaomigao ps aux | grep -q "openclaw-gateway"; then
            log "✓ OpenClaw网关进程运行正常"
            log "========== 重建完成 =========="
            
            # 通知用户（通过 QQ Bot）
            # 注意：由于容器刚刚重建，QQ Bot可能还没完全启动，这里跳过通知
            log "容器重建完成，网关进程正在启动中..."
            
            exit 0
        else
            log "✗ OpenClaw网关进程未找到"
            exit 1
        fi
    else
        log "✗ 容器未运行"
        exit 1
    fi
}

main
