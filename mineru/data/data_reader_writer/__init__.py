from .base import DataReader, DataWriter
from .dummy import DummyDataWriter
from .filebase import FileBasedDataReader, FileBasedDataWriter
from .multi_bucket_s3 import MultiBucketS3DataReader, MultiBucketS3DataWriter
from .s3 import S3DataReader, S3DataWriter

# 尝试导入 COS Writer
try:
    from .cos_writer import COSDataWriter
    _cos_available = True
except ImportError:
    COSDataWriter = None
    _cos_available = False

__all__ = [
    "DataReader",
    "DataWriter",
    "FileBasedDataReader",
    "FileBasedDataWriter",
    "S3DataReader",
    "S3DataWriter",
    "MultiBucketS3DataReader",
    "MultiBucketS3DataWriter",
    "DummyDataWriter",
]

if _cos_available:
    __all__.append("COSDataWriter")
