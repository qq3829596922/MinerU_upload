#!/bin/bash
# 安装腾讯云 COS Python SDK

echo "安装腾讯云 COS SDK..."
pip install cos-python-sdk-v5

echo "安装完成！"
echo ""
echo "使用前请设置环境变量："
echo "export COS_SECRET_ID='your-secret-id'"
echo "export COS_SECRET_KEY='your-secret-key'"
echo "export COS_BUCKET='your-bucket-name'"