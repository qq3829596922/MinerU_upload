# Claude Project 项目结构

## 目录结构
```
MinerU/
├── claude_message/         # Claude 开发文档
│   ├── claude_code.md     # 代码变更记录
│   ├── claude_work.md     # 工作内容记录
│   └── claude_project.md  # 项目结构说明
├── demo/                  # 示例文件
│   ├── demo.py           # 主程序示例
│   └── pdfs/             # PDF 测试文件
├── mineru/               # 核心库
│   ├── cli/              # 命令行工具
│   │   ├── fast_api.py   # REST API 实现
│   │   └── common.py     # 公共功能
│   ├── data/
│   │   └── data_reader_writer/
│   │       ├── __init__.py
│   │       ├── filebase.py     # 基础文件写入器
│   │       └── cos_writer.py   # COS 自动上传写入器
│   └── utils/            # 工具函数
├── config/                # 配置文件
│   └── cos_config.json   # COS 配置
├── Docker 相关文件
│   ├── Dockerfile         # 基础 API 镜像
│   ├── Dockerfile.final   # 完整功能镜像
│   ├── Dockerfile.working # 开发测试镜像
│   ├── docker-compose.yml # 默认部署配置
│   ├── docker-compose-mount.yml  # 挂载本地目录
│   └── docker-compose-official.yml # 官方镜像配置
├── run_api_with_cos.sh    # COS API 启动脚本
├── pdf_extract_with_images.py  # PyMuPDF 版提取脚本
└── pdfplumber_extract.py       # pdfplumber 版提取脚本
```

## 模块代码示例

### COS 自动上传集成
```python
# mineru/data/data_reader_writer/cos_writer.py
class COSDataWriter(FileBasedDataWriter):
    """扩展的 DataWriter，支持自动上传到腾讯云 COS"""
    
    def __init__(self, parent_dir: str = '', bucket: str = '', cos_prefix: str = 'mineru/'):
        super().__init__(parent_dir)
        # 初始化 COS 客户端
        self.client = CosS3Client(config)
        
    def write(self, rel_path: str, data: bytes) -> str:
        # 先保存到本地
        local_path = super().write(rel_path, data)
        
        # 上传到 COS
        cos_key = f"{self.cos_prefix}{rel_path}"
        self.client.put_object(
            Bucket=self.bucket,
            Body=data,
            Key=cos_key
        )
        return f"https://{self.bucket}.cos.{region}.myqcloud.com/{cos_key}"
```

### PDF 提取工具
```python
# pdf_extract_with_images.py
#!/usr/bin/env python3
"""
PDF 图片提取工具 - 保留表格在文本中
- 文本版本：清理多余换行，保持可读性
- HTML版本：保留表格格式
- 图片占位符：使用 Markdown 格式 ![](images/xxx.jpg)
"""
import fitz  # PyMuPDF
import re
from pathlib import Path

def extract_pdf_with_images(pdf_path, output_dir="output"):
    doc = fitz.open(pdf_path)
    # 提取逻辑...
```

### MinerU API
```python
# mineru/cli/fast_api.py
@app.post(path="/file_parse")
async def parse_pdf(
    files: List[UploadFile] = File(...),
    backend: str = Form("pipeline"),
    server_url: Optional[str] = Form(None),
):
    # API 处理逻辑
    if file_path.suffix.lower() in pdf_suffixes + image_suffixes:
        pdf_bytes = read_fn(temp_path)
```

### Docker 部署配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  mineru-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./uploads:/app/uploads
      - ./output:/app/output
    environment:
      - MINERU_ENABLE_COS=true
      - MINERU_COS_CONFIG=/app/config/cos_config.json
    command: python -m mineru.api --host 0.0.0.0 --port 8000
    restart: unless-stopped
```

### 服务启动脚本
```bash
#!/bin/bash
# run_api_with_cos.sh

# 设置 COS 环境变量
export MINERU_ENABLE_COS=true
export MINERU_COS_CONFIG="config/cos_config.json"

# 启动 API 服务
python -m mineru.api --host 0.0.0.0 --port 8000
```

## 配置示例

### CUDA 环境配置
```bash
# ~/.bashrc 或 ~/.zshrc
export PATH=/usr/local/cuda-12.9/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.9/lib64:$LD_LIBRARY_PATH
```

### API 调用示例
```bash
# 使用 VLM 后端处理 PDF
curl -X POST "http://localhost:8000/file_parse" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@demo.pdf" \
  -F "backend=vlm-sglang-client" \
  -F "server_url=http://localhost:30000" \
  -F "return_md=true"
```