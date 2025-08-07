#!/bin/bash
# 直接运行 MinerU API with COS

# 检查配置
if [ ! -f "config/cos_config.json" ]; then
    echo "❌ 请先配置 config/cos_config.json"
    exit 1
fi

# 设置环境变量
export MINERU_ENABLE_COS=true
export MINERU_COS_CONFIG="$(pwd)/config/cos_config.json"

echo "✅ COS 功能已启用"
echo "📁 配置文件: $MINERU_COS_CONFIG"

# 启动 API
mineru-api --host 0.0.0.0 --port 8000