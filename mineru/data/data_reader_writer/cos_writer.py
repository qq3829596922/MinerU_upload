"""
腾讯云 COS 集成的 DataWriter
在保存图片到本地的同时，自动上传到腾讯云 COS
"""
import os
from typing import Optional
from .filebase import FileBasedDataWriter
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import logging

logger = logging.getLogger(__name__)


class COSDataWriter(FileBasedDataWriter):
    """扩展的 DataWriter，支持自动上传到腾讯云 COS"""
    
    def __init__(
        self, 
        parent_dir: str = '',
        secret_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = 'ap-guangzhou',
        bucket: str = '',
        cos_prefix: str = 'mineru/',
        enable_upload: bool = True
    ):
        """
        初始化 COS DataWriter
        
        Args:
            parent_dir: 本地父目录
            secret_id: 腾讯云 SecretId (可从环境变量读取)
            secret_key: 腾讯云 SecretKey (可从环境变量读取)
            region: COS 区域
            bucket: COS 存储桶名称
            cos_prefix: COS 路径前缀
            enable_upload: 是否启用上传
        """
        super().__init__(parent_dir)
        
        self.enable_upload = enable_upload
        self.cos_prefix = cos_prefix.rstrip('/') + '/'
        self.region = region  # 保存 region
        
        if self.enable_upload:
            # 从环境变量获取凭证（如果没有传入）
            self.secret_id = secret_id or os.environ.get('COS_SECRET_ID')
            self.secret_key = secret_key or os.environ.get('COS_SECRET_KEY')
            self.bucket = bucket or os.environ.get('COS_BUCKET')
            
            if not all([self.secret_id, self.secret_key, self.bucket]):
                logger.warning("COS credentials not complete, upload disabled")
                self.enable_upload = False
            else:
                # 初始化 COS 客户端
                config = CosConfig(
                    Region=self.region,
                    SecretId=self.secret_id,
                    SecretKey=self.secret_key
                )
                self.cos_client = CosS3Client(config)
                logger.info(f"COS client initialized for bucket: {self.bucket}")
    
    def write(self, path: str, data: bytes) -> Optional[str]:
        """
        写入文件并上传到 COS
        
        Args:
            path: 文件路径
            data: 文件数据
            
        Returns:
            COS URL 如果上传成功，否则返回 None
        """
        # 先写入本地
        super().write(path, data)
        
        # 如果启用了上传，则上传到 COS
        if self.enable_upload:
            try:
                # 构建 COS 对象键
                # 如果是绝对路径，只取文件名
                if os.path.isabs(path):
                    cos_key = self.cos_prefix + os.path.basename(path)
                else:
                    cos_key = self.cos_prefix + path.replace('\\', '/')
                
                # 上传到 COS
                response = self.cos_client.put_object(
                    Bucket=self.bucket,
                    Body=data,
                    Key=cos_key,
                    EnableMD5=True
                )
                
                # 构建访问 URL
                cos_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"
                
                logger.info(f"Uploaded to COS: {cos_url}")
                return cos_url
                
            except Exception as e:
                logger.error(f"Failed to upload to COS: {e}")
                return None
        
        return None
    
    def write_with_metadata(self, path: str, data: bytes, metadata: dict = None) -> Optional[str]:
        """
        写入文件并上传到 COS，同时设置元数据
        
        Args:
            path: 文件路径
            data: 文件数据
            metadata: 元数据字典
            
        Returns:
            COS URL 如果上传成功
        """
        # 先写入本地
        super().write(path, data)
        
        if self.enable_upload and metadata:
            try:
                cos_key = self.cos_prefix + os.path.basename(path)
                
                # 准备元数据
                cos_metadata = {f'x-cos-meta-{k}': str(v) for k, v in metadata.items()}
                
                # 上传到 COS
                response = self.cos_client.put_object(
                    Bucket=self.bucket,
                    Body=data,
                    Key=cos_key,
                    Metadata=cos_metadata,
                    EnableMD5=True
                )
                
                cos_url = f"https://{self.bucket}.cos.{self.cos_client._conf._region}.myqcloud.com/{cos_key}"
                logger.info(f"Uploaded to COS with metadata: {cos_url}")
                return cos_url
                
            except Exception as e:
                logger.error(f"Failed to upload to COS: {e}")
                return None
        
        return None