#!/bin/bash
# 启动带有 COS 自动上传功能的 MinerU API

echo "🚀 启动带有腾讯云 COS 自动上传功能的 MinerU API..."

# 设置环境变量启用 COS
export MINERU_ENABLE_COS=true
export MINERU_COS_CONFIG="config/cos_config.json"

# 检查配置文件
if [ ! -f "$MINERU_COS_CONFIG" ]; then
    echo "⚠️  配置文件不存在: $MINERU_COS_CONFIG"
    echo "请先创建配置文件并填入腾讯云凭证"
    exit 1
fi

echo "✅ COS 功能已启用"
echo "📁 配置文件: $MINERU_COS_CONFIG"

# 启动 MinerU API
echo "🔧 启动 MinerU API (端口 8000)..."
mineru-api --host 0.0.0.0 --port 8000