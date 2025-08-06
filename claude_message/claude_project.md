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
│   └── utils/            # 工具函数
├── pdf_extract_with_images.py  # PyMuPDF 版提取脚本
├── pdfplumber_extract.py       # pdfplumber 版提取脚本
└── claude_code.md              # 对话记录（旧）
```

## 模块代码示例

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

### 服务启动脚本
```bash
#!/bin/bash
# start_services.sh

# 启动 SGLang 推理服务器
mineru-sglang-server --host 0.0.0.0 --port 30000 &

# 启动 REST API 服务器
mineru-api --host 0.0.0.0 --port 8000 &
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