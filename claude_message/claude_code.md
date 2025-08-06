# Claude Code 代码变更记录

## [2025-08-06] PDF 提取工具开发
- **提交ID**: (待提交)
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