# Claude Code 代码变更记录

## [2025-08-14] 图片自动缩放与双重保存功能
- **提交ID**: 85958d44
- **修改文件**: 
  - `mineru/cli/common.py`
  - `mineru/data/data_reader_writer/cos_writer.py`
- **主要变更**: 
  - 本地同时保存原图和缩略图
  - COS只上传缩略图节省存储
  - 自动创建 resize_images 目录

### 核心代码示例
```python
# COSDataWriter 现在会：
# 1. 保存原图到 images/
# 2. 生成并保存缩略图到 resize_images/ (1/2尺寸)
# 3. COS只上传缩略图到原路径
if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
    # 生成缩略图
    new_width = img.width // 2
    new_height = img.height // 2
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
```

## [2025-08-07] 腾讯云 COS 自动上传功能
- **提交ID**: 722f38d3
- **修改文件**: 
  - `mineru/data/data_reader_writer/cos_writer.py` (新增)
  - `mineru/cli/common.py`
  - `mineru/data/data_reader_writer/__init__.py`
- **主要变更**: 
  - 集成腾讯云 COS，处理 PDF 时自动上传图片
  - 通过环境变量控制功能开关
  - 支持配置文件管理凭证
  - 添加 Docker 容器化支持

### 核心代码示例
```python
# 创建支持 COS 的图片写入器
def create_image_writer(local_image_dir, pdf_file_name=None):
    if COSDataWriter and os.environ.get('MINERU_ENABLE_COS', '').lower() == 'true':
        return COSDataWriter(
            parent_dir=local_image_dir,
            bucket=cos_config.get('bucket'),
            cos_prefix=cos_config.get('prefix', 'mineru/')
        )
    return FileBasedDataWriter(local_image_dir)
```

## [2025-08-06] PDF 提取工具开发
- **提交ID**: (未提交)
- **修改文件**: `pdf_extract_with_images.py`, `pdfplumber_extract.py`
- **主要变更**: 
  - 实现 PDF 图片提取，使用 Markdown 格式占位符
  - 表格内容嵌入文本中，不单独提取
  - 清理多余换行符，提升可读性

### 核心代码示例
```python
# 图片提取和占位符
for img_index, img in enumerate(image_list):
    # 保存图片为 JPG
    img_filename = f"page{page_num+1}_img{img_index+1}.jpg"
    img_path = images_dir / img_filename
    
    # 创建 Markdown 格式的占位符
    placeholder = f"![](images/{img_filename})"
    image_placeholders.append(placeholder)

# 文本清理
text_content = re.sub(r'\n{3,}', '\n\n', text_content)
```

## [2025-08-05] MinerU SGLang 服务器配置
- **提交ID**: (系统配置)
- **修改文件**: 环境变量配置
- **主要变更**: 
  - 解决 CUDA nvcc 编译器缺失问题
  - 安装 cuda-nvcc-12-9 包
  - 配置 PATH 和 LD_LIBRARY_PATH 环境变量

### 核心代码示例
```bash
# 环境变量配置
export PATH=/usr/local/cuda-12.9/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.9/lib64:$LD_LIBRARY_PATH

# 启动服务
mineru-sglang-server --host 0.0.0.0 --port 30000
```