# 使用 Python 3.11 官方镜像
FROM python:3.11-slim-bullseye

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装 PyTorch (CPU版本，体积更小)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装 MinerU 依赖和 API 服务依赖
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir \
    uvicorn \
    fastapi \
    python-multipart \
    cos-python-sdk-v5

# 创建必要的目录
RUN mkdir -p /app/config /app/output /app/uploads /app/logs

# 设置环境变量
ENV MINERU_ENABLE_COS=true
ENV MINERU_COS_CONFIG=/app/config/cos_config.json
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "mineru.cli.fast_api", "--host", "0.0.0.0", "--port", "8000"]