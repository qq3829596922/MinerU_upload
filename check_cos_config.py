#!/usr/bin/env python3
"""
检查腾讯云 COS 配置
"""
import json
import os
from pathlib import Path

def check_config():
    config_path = "config/cos_config.json"
    
    if not Path(config_path).exists():
        print("❌ 配置文件不存在：config/cos_config.json")
        print("\n请创建配置文件，参考 config/cos_config.example.json")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    cos_config = config.get('cos', {})
    
    print("🔍 检查 COS 配置...")
    print("-" * 50)
    
    # 检查必要字段
    required_fields = ['secret_id', 'secret_key', 'bucket', 'region']
    missing = []
    
    for field in required_fields:
        value = cos_config.get(field, '')
        if not value or value.startswith('your-'):
            missing.append(field)
        else:
            if field in ['secret_id', 'secret_key']:
                # 隐藏敏感信息
                display_value = value[:6] + '***' + value[-4:] if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"✓ {field}: {display_value}")
    
    if missing:
        print(f"\n❌ 缺少配置：{', '.join(missing)}")
        print("\n请编辑 config/cos_config.json 填入正确的值")
        return False
    
    # 检查 bucket 格式
    bucket = cos_config['bucket']
    if '-' not in bucket or not bucket.split('-')[-1].isdigit():
        print(f"\n⚠️  Bucket 名称格式可能不正确：{bucket}")
        print("   正确格式：bucketname-appid")
        print("   例如：myimages-1234567890")
    
    # 检查是否启用
    if not cos_config.get('enable_upload', False):
        print("\n⚠️  COS 上传功能未启用")
        print("   请设置 'enable_upload': true")
    
    print("\n📋 当前配置：")
    print(f"   Region: {cos_config['region']}")
    print(f"   Prefix: {cos_config.get('prefix', 'mineru/')}")
    print(f"   Enable: {cos_config.get('enable_upload', False)}")
    
    return True


if __name__ == "__main__":
    print("腾讯云 COS 配置检查工具")
    print("=" * 50)
    
    if check_config():
        print("\n✅ 配置检查通过！")
        
        # 测试连接
        try:
            from qcloud_cos import CosConfig, CosS3Client
            
            with open("config/cos_config.json", 'r') as f:
                config = json.load(f)
            cos_config = config['cos']
            
            print("\n🔗 测试 COS 连接...")
            client_config = CosConfig(
                Region=cos_config['region'],
                SecretId=cos_config['secret_id'],
                SecretKey=cos_config['secret_key']
            )
            client = CosS3Client(client_config)
            
            # 尝试获取 bucket 信息
            try:
                response = client.head_bucket(Bucket=cos_config['bucket'])
                print("✅ 成功连接到 COS Bucket！")
            except Exception as e:
                error_msg = str(e)
                if "NoSuchBucket" in error_msg:
                    print(f"❌ Bucket 不存在：{cos_config['bucket']}")
                    print("\n可能的原因：")
                    print("1. Bucket 名称错误（需要包含 APPID）")
                    print("2. Bucket 不在指定的 Region")
                    print("3. Bucket 未创建")
                elif "AccessDenied" in error_msg:
                    print("❌ 访问被拒绝，请检查 SecretId 和 SecretKey")
                else:
                    print(f"❌ 连接失败：{e}")
                    
        except ImportError:
            print("\n⚠️  未安装 COS SDK，请运行：pip install cos-python-sdk-v5")