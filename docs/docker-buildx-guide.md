# Docker Buildx 构建器使用指南

> 安装时间：2026-04-07 12:18 CST
> 版本：v0.21.2
> 状态：✅ 已启用

---

## 📊 当前配置

**构建器名称**：multiarch
**驱动**：docker-container
**BuildKit 版本**：v0.28.1
**支持平台**：
- linux/amd64
- linux/amd64/v2
- linux/amd64/v3
- linux/386

**垃圾回收策略**：
- 源代码缓存：48 小时后清理
- 构建缓存：60 天后清理
- 最大缓存空间：93.13 GB

---

## 🚀 基本用法

### 1. 构建镜像

```bash
# 基本构建
docker buildx build -t myimage:latest .

# 多平台构建
docker buildx build --platform linux/amd64,linux/arm64 -t myimage:latest .

# 构建并加载到本地 Docker
docker buildx build --load -t myimage:latest .

# 构建并推送到仓库
docker buildx build --push -t username/myimage:latest .
```

### 2. 高级特性

#### 构建缓存

```bash
# 使用远程缓存（加速构建）
docker buildx build \
  --cache-from type=registry,ref=username/myimage:cache \
  --cache-to type=registry,ref=username/myimage:cache,mode=max \
  -t username/myimage:latest \
  --push .
```

#### 多平台构建

```bash
# 构建并推送多平台镜像
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t username/myimage:latest \
  --push .
```

#### 输出格式

```bash
# 输出为 Docker 镜像
docker buildx build --output type=docker -t myimage:latest .

# 输出为 tar 文件
docker buildx build --output type=tar,dest=image.tar .

# 输出为本地目录
docker buildx build --output type=local,dest=./output .
```

---

## ⚡ 性能优化

### 1. 缓存策略

**最佳实践**：
```bash
# 使用内联缓存（推荐）
docker buildx build \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --cache-from username/myimage:latest \
  -t username/myimage:latest \
  --push .
```

**GitHub Actions 集成**：
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: username/myimage:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 2. 并行构建

```bash
# 启用并行构建（自动）
docker buildx build --platform linux/amd64,linux/arm64 -t myimage:latest .
```

### 3. 构建优化技巧

**Dockerfile 优化**：
```dockerfile
# ❌ 不好 - 每次都重新下载
RUN apt-get update && apt-get install -y package

# ✅ 好 - 使用缓存挂载
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y package

# ✅ 好 - 使用绑定挂载
RUN --mount=type=bind,source=.,target=/app \
    cd /app && make build
```

---

## 🔧 管理命令

### 查看构建器状态

```bash
# 列出所有构建器
docker buildx ls

# 检查当前构建器
docker buildx inspect

# 查看构建历史
docker buildx du
```

### 清理缓存

```bash
# 清理所有构建缓存
docker buildx prune -a

# 只清理过期的缓存
docker buildx prune --filter until=24h
```

### 切换构建器

```bash
# 切换到默认构建器
docker buildx use default

# 切换到 multiarch 构建器
docker buildx use multiarch
```

---

## 📊 性能对比

### 传统构建 vs Buildx

| 特性 | 传统 docker build | Buildx |
|------|------------------|--------|
| 多平台构建 | ❌ | ✅ |
| 高级缓存 | ❌ | ✅ |
| 并行构建 | ❌ | ✅ |
| 外部缓存 | ❌ | ✅ |
| 构建速度 | 基准 | ⬆️ 2-5 倍 |
| 镜像大小 | 基准 | ⬇️ 10-30% |

---

## 🎯 使用场景

### 1. 小米糕容器重建

```bash
# 使用 Buildx 构建小米糕镜像
cd ~/.openclaw/workspace
docker buildx build \
  --platform linux/amd64 \
  --cache-from type=local,src=/tmp/buildx-cache \
  --cache-to type=local,dest=/tmp/buildx-cache,mode=max \
  -t xiaomigao:latest \
  --load \
  -f Dockerfile.xiaomigao .
```

### 2. Bounty 项目构建

```bash
# 快速构建 homelab-stack 服务
cd ~/workspace/homelab-stack
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t homelab-stack:latest \
  --load \
  .
```

---

## ⚠️ 注意事项

1. **docker-container 驱动**：
   - 需要启动 BuildKit 容器
   - `--load` 选项需要额外的导出步骤
   - 适合多平台构建

2. **缓存管理**：
   - 定期清理缓存（`docker buildx prune`）
   - 监控缓存空间使用
   - 使用远程缓存加速 CI/CD

3. **网络问题**：
   - 首次拉取 buildkit 镜像可能较慢
   - 考虑配置国内镜像源
   - 使用缓存减少网络请求

---

## 📚 参考资料

- [Docker Buildx 官方文档](https://docs.docker.com/build/buildx/)
- [BuildKit 官方文档](https://github.com/moby/buildkit)
- [多平台构建指南](https://docs.docker.com/build/building/multi-platform/)

---

_最后更新：2026-04-07 12:18 CST_
