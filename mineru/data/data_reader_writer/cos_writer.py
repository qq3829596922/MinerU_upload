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
from PIL import Image
import io

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
        
        logger.info(f"COSDataWriter.__init__ called with:")
        logger.info(f"  parent_dir: {parent_dir}")
        logger.info(f"  secret_id: {'***' if secret_id else 'None'}")
        logger.info(f"  secret_key: {'***' if secret_key else 'None'}")
        logger.info(f"  region: {region}")
        logger.info(f"  bucket: {bucket}")
        logger.info(f"  cos_prefix: {cos_prefix}")
        logger.info(f"  enable_upload: {enable_upload}")
        
        self.enable_upload = enable_upload
        self.cos_prefix = cos_prefix.rstrip('/') + '/'
        self.region = region  # 保存 region
        
        if self.enable_upload:
            # 从环境变量获取凭证（如果没有传入）
            self.secret_id = secret_id or os.environ.get('COS_SECRET_ID')
            self.secret_key = secret_key or os.environ.get('COS_SECRET_KEY')
            self.bucket = bucket or os.environ.get('COS_BUCKET')
            
            logger.info(f"  Final secret_id: {'***' if self.secret_id else 'None'}")
            logger.info(f"  Final secret_key: {'***' if self.secret_key else 'None'}")
            logger.info(f"  Final bucket: {self.bucket}")
            
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
                logger.info(f"COS client initialized successfully for bucket: {self.bucket}")
    
    def write(self, path: str, data: bytes) -> Optional[str]:
        """
        写入文件并上传到 COS
        本地保存原图和缩小图，COS只上传缩小图
        
        Args:
            path: 文件路径
            data: 文件数据
            
        Returns:
            COS URL 如果上传成功，否则返回 None
        """
        logger.info(f"COSDataWriter.write called with path: {path}, data size: {len(data)} bytes")
        
        # 先写入本地原图
        super().write(path, data)
        logger.info(f"File written to local path: {path}")
        
        # 检查是否为图片文件，如果是则在本地也保存缩小版本
        file_ext = os.path.splitext(path)[1].lower()
        resized_data = None  # 初始化变量
        new_width = None
        new_height = None
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            try:
                # 打开图片
                img = Image.open(io.BytesIO(data))
                
                # 计算缩小后的尺寸（1/2大小）
                new_width = img.width // 2
                new_height = img.height // 2
                
                # 缩放图片
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为字节数据
                output_buffer = io.BytesIO()
                save_format = 'JPEG' if file_ext in ['.jpg', '.jpeg'] else img.format
                
                if save_format == 'JPEG' and img.mode == 'RGBA':
                    # 如果是RGBA模式的JPEG，转换为RGB
                    img_rgb = Image.new('RGB', resized_img.size, (255, 255, 255))
                    img_rgb.paste(resized_img, mask=resized_img.split()[3] if len(resized_img.split()) == 4 else None)
                    img_rgb.save(output_buffer, format=save_format, quality=100, optimize=True)
                else:
                    resized_img.save(output_buffer, format=save_format, quality=100 if save_format == 'JPEG' else None)
                
                resized_data = output_buffer.getvalue()
                
                # 构建缩小图片的本地保存路径
                # parent_dir 已经是 images 目录，需要在同级创建 resize_images
                if self._parent_dir and 'images' in self._parent_dir:
                    # 将 parent_dir 中的 images 替换为 resize_images
                    resize_parent_dir = self._parent_dir.replace('images', 'resize_images')
                    # 确保目录存在
                    os.makedirs(resize_parent_dir, exist_ok=True)
                    # 构建完整路径
                    if os.path.isabs(path):
                        resize_path = os.path.join(resize_parent_dir, os.path.basename(path))
                    else:
                        resize_path = os.path.join(resize_parent_dir, path)
                else:
                    # 其他情况的处理
                    if 'images' in path:
                        resize_path = path.replace('images', 'resize_images')
                    else:
                        resize_path = os.path.join('resize_images', os.path.basename(path))
                
                # 直接保存缩小图片到本地（不使用super().write避免路径重复处理）
                with open(resize_path, 'wb') as f:
                    f.write(resized_data)
                logger.info(f"Resized image saved locally to: {resize_path}")
                logger.info(f"Image resized from {img.width}x{img.height} to {new_width}x{new_height}")
                
            except Exception as e:
                logger.debug(f"Failed to create resized version: {e}")
        
        # 如果启用了上传，则上传缩小的图片到 COS
        if self.enable_upload:
            logger.info("COS upload is enabled, starting upload...")
            try:
                # 准备上传数据
                upload_data = data
                
                # 如果是图片文件，使用已经生成的缩小版本
                if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                    # 如果之前成功生成了缩小版本，使用它
                    if resized_data is not None:
                        upload_data = resized_data
                        logger.info(f"Using resized image for COS upload: {new_width}x{new_height}")
                        logger.info(f"Data size changed from {len(data)} bytes to {len(upload_data)} bytes")
                    else:
                        # 如果之前没有成功生成缩小版本，现在生成
                        try:
                            img = Image.open(io.BytesIO(data))
                            new_width = img.width // 2
                            new_height = img.height // 2
                            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            
                            output_buffer = io.BytesIO()
                            save_format = 'JPEG' if file_ext in ['.jpg', '.jpeg'] else img.format
                            
                            if save_format == 'JPEG' and img.mode == 'RGBA':
                                img_rgb = Image.new('RGB', resized_img.size, (255, 255, 255))
                                img_rgb.paste(resized_img, mask=resized_img.split()[3] if len(resized_img.split()) == 4 else None)
                                img_rgb.save(output_buffer, format=save_format, quality=100, optimize=True)
                            else:
                                resized_img.save(output_buffer, format=save_format, quality=100 if save_format == 'JPEG' else None)
                            
                            upload_data = output_buffer.getvalue()
                            logger.info(f"Image resized for COS: {img.width}x{img.height} -> {new_width}x{new_height}")
                        except Exception as e:
                            logger.debug(f"Failed to resize for COS, using original: {e}")
                            upload_data = data
                
                # 构建 COS 对象键 - 保持原始路径不变
                # 如果是绝对路径，只取文件名
                if os.path.isabs(path):
                    cos_key = self.cos_prefix + os.path.basename(path)
                else:
                    cos_key = self.cos_prefix + path.replace('\\', '/')
                
                logger.info(f"COS key: {cos_key}")
                logger.info(f"Uploading to bucket: {self.bucket}")
                
                # 上传到 COS（使用处理后的数据）
                response = self.cos_client.put_object(
                    Bucket=self.bucket,
                    Body=upload_data,  # 使用可能已缩放的数据
                    Key=cos_key,
                    EnableMD5=True
                )
                
                logger.info(f"COS upload response: {response}")
                
                # 构建访问 URL
                cos_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"
                
                logger.info(f"Successfully uploaded to COS: {cos_url}")
                return cos_url
                
            except Exception as e:
                logger.error(f"Failed to upload to COS: {e}", exc_info=True)
                return None
        else:
            logger.info("COS upload is disabled")
        
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