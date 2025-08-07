# Claude Work 工作内容记录

## [2025-08-07] Docker 容器化与 API 部署
- **功能1**：创建多种 Docker 镜像支持不同部署场景
- **功能2**：配置 docker-compose 支持一键部署
- **功能3**：集成 COS 自动上传到容器环境

### 核心代码示例

#### Dockerfile 配置
```dockerfile
# Dockerfile - 基础 API 服务镜像
FROM python:3.11-slim-bullseye

# 安装 PyTorch CPU 版本
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装 MinerU 和 API 依赖
RUN pip install -e . && pip install uvicorn fastapi cos-python-sdk-v5

# 配置 COS 环境变量
ENV MINERU_ENABLE_COS=true
ENV MINERU_COS_CONFIG=/app/config/cos_config.json
```

#### docker-compose 配置
```yaml
# docker-compose.yml
services:
  mineru-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./uploads:/app/uploads
    environment:
      - MINERU_ENABLE_COS=true
    command: python -m mineru.api --host 0.0.0.0 --port 8000
```

#### API 启动脚本
```bash
# run_api_with_cos.sh
#!/bin/bash
export MINERU_ENABLE_COS=true
export MINERU_COS_CONFIG="config/cos_config.json"
python -m mineru.api --host 0.0.0.0 --port 8000
```

---

## [2025-08-06] MinerU 集成腾讯云 COS 自动上传
- **功能1**：修改 MinerU 源码支持自动上传
- **功能2**：通过环境变量控制是否启用 COS
- **功能3**：保持向后兼容，不影响原有功能

### 核心代码修改

#### 1. 添加 COS Writer 支持
```python
# mineru/data/data_reader_writer/__init__.py
try:
    from .cos_writer import COSDataWriter
    _cos_available = True
except ImportError:
    COSDataWriter = None
    _cos_available = False
```

#### 2. 创建 Writer 工厂函数
```python
# mineru/cli/common.py
def create_image_writer(local_image_dir, pdf_file_name=None):
    """创建图片写入器，如果配置了 COS 则使用 COSDataWriter"""
    if COSDataWriter and os.environ.get('MINERU_ENABLE_COS', '').lower() == 'true':
        # 使用 COSDataWriter
        return COSDataWriter(...)
    # 默认使用 FileBasedDataWriter
    return FileBasedDataWriter(local_image_dir)
```

#### 3. 使用方法
```bash
# 启用 COS 自动上传
export MINERU_ENABLE_COS=true
export MINERU_COS_CONFIG="config/cos_config.json"

# 启动 API
mineru-api --host 0.0.0.0 --port 8000
```

---

## [2025-08-06] PDF 提取功能开发
- **功能1**：开发 PDF 图片和表格提取脚本
- **功能2**：使用 pdfplumber 实现更好的表格识别
- **功能3**：优化文本输出格式，清理多余换行

### 核心代码示例

#### PyMuPDF 版本
```python
# pdf_extract_with_images.py
def extract_pdf_with_images(pdf_path, output_dir="output"):
    """提取 PDF 文本和图片，图片保存并用占位符替换"""
    doc = fitz.open(pdf_path)
    
    # 获取页面文本和 HTML
    text_content = page.get_text()
    html_content = page.get_text("html")
    
    # 清理文本内容
    text_content = re.sub(r'\n{3,}', '\n\n', text_content)
```

#### pdfplumber 版本
```python
# pdfplumber_extract.py
def extract_pdf_with_pdfplumber(pdf_path, output_dir="output"):
    """使用 pdfplumber 提取 PDF 内容"""
    pdf = pdfplumber.open(pdf_path)
    
    # 提取文本（包含表格）
    text_content = page.extract_text() or ""
    
    # 图片占位符
    placeholder = f"![](images/{img_filename})"
```

## [2025-08-05] MinerU 环境配置与优化
- **功能1**：解决 CUDA 编译器缺失问题
- **功能2**：优化 SGLang 服务器内存使用
- **功能3**：理解 prefill 和批处理概念

### 核心代码示例

#### 服务启动配置
```bash
# 限制内存使用
mineru-sglang-server --host 0.0.0.0 --port 30000 --mem-fraction-static 0.5

# 默认配置性能最佳
mineru-sglang-server --host 0.0.0.0 --port 30000
```

#### API 调用示例
```bash
# MinerU API 服务
mineru-api --host 0.0.0.0 --port 8000

# API 调用
curl -X POST "http://localhost:8000/file_parse" \
  -F "files=@demo.pdf" \
  -F "backend=vlm-sglang-client" \
  -F "server_url=http://localhost:30000"
```