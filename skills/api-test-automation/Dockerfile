# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.4

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建报告目录
RUN mkdir -p reports cases config artifacts

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 暴露端口（如果需要）
# EXPOSE 8080

# 默认命令
CMD ["python", "scripts/run_tests.py", "--help"]
